from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal
from difflib import SequenceMatcher

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import BeverageType, CheckResult, CheckState, Evidence
from labelverify.domain.comparison import _result
from labelverify.domain.normalize import (
    punctuation_folded,
    reference_volume_ml,
    warning_text,
    warning_words,
)
from labelverify.domain.types import WarningObservation

_RECOGNIZED_MALT_CLASS = re.compile(
    r"\b(?:malt\s+beverage|beer|ale|lager|stout|porter|pilsner|india\s+pale\s+ale|ipa)\b",
    re.I,
)
_BELOW_THRESHOLD_CUE = re.compile(
    r"non-?\s*alcoholic|alcohol\s*-?\s*free|near\s+beer|cereal\s+beverage|less\s+than\s+0?\.5",
    re.I,
)


def _presentation(
    check_id: str,
    label: str,
    value: bool | None,
    evidence: Evidence | None,
    *,
    pass_reason: str,
    fail_reason: str,
    failure_requires_review: bool = False,
) -> CheckResult:
    if value is True:
        state: CheckState = "Match"
        code, text = "presentation_supported", pass_reason
    elif value is False:
        if failure_requires_review:
            state, code, text = "Review", "presentation_requires_review", fail_reason
        else:
            state, code, text = "Mismatch", "presentation_failure", fail_reason
    else:
        state, code, text = (
            "Review",
            "presentation_requires_review",
            "The image provides heuristic evidence but reviewer judgment is required",
        )
    return _result(
        check_id,
        label,
        state,
        code,
        text,
        candidate=None,
        observed=None,
        capability="visual_heuristic",
    ).model_copy(update={"evidence_ref": evidence.evidence_id if evidence else None})


def warning_checks_across(
    abv: Decimal | None,
    observed: WarningObservation,
    alternates: list[WarningObservation],
    net_contents_value: Decimal = Decimal("750"),
    net_contents_unit: str = "mL",
    *,
    beverage_type: BeverageType | None = None,
    class_type: str | None = None,
) -> list[CheckResult]:
    """Evaluate the statement on every panel that carries it and keep the best-read one.

    Up to three photographs of one product may each show part of the statement: a curved
    bottle or glare hides a line in one photograph and shows it in the next. The same
    printed statement cannot differ between photographs, so a complete clean read on one
    panel outranks a partial or noisy read on another, and a statutory word read in place
    on any panel is confirmed for the product as long as no panel contradicts it. Two
    complete reads that disagree on a word are a review item: one product cannot carry two
    statements, so either the images show two products or one read is wrong. Punctuation
    stays with the reviewer: the machine never clears it from a photograph.
    """

    observations = [observed, *alternates]
    # A fragment (an edge-cut heading) can complete the wording but cannot lead while any
    # panel carries the heading: the heading checks need a heading that was actually read.
    leaders = [item for item in observations if item.heading] or [observed]
    evaluated = [
        (
            observation,
            warning_checks(
                abv,
                observation,
                net_contents_value,
                net_contents_unit,
                beverage_type=beverage_type,
                class_type=class_type,
            ),
        )
        for observation in leaders
    ]
    # max keeps the first of equal ranks, so the primary panel wins ties.
    best_observation, best = max(evaluated, key=lambda item: _wording_rank(_row(item[1])))
    wording = _row(best)
    expected_words = warning_words(str(contracts().rules["warning"]["bodyExact"])).split()
    best_alignment = _alignment(best_observation, expected_words) if best_observation.body else None
    if not best_observation.heading and (
        wording.reason_code == "warning_ocr_difference_uncertain"
        or (
            wording.state == "Mismatch"
            and (best_alignment is None or len(best_alignment.covered) < 20)
        )
    ):
        # Only a fragment of the statement was in view and the read is not clean, or it
        # shows too little of the statute to establish a difference: what is missing is
        # more likely outside the photograph than absent from the label. A clear
        # substitution inside a substantial fragment stays a difference; the cut cannot
        # invent words.
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Review",
            "warning_fragment_review",
            "Only part of the statement was in view; add a photograph that shows all of it, "
            "or confirm the wording by eye",
            observed=best_observation.body,
        ).model_copy(update={"evidence_ref": wording.evidence_ref})
        best = [wording if item.check_id == "warning_wording" else item for item in best]
    if len(observations) > 1:
        # A complete read on another image that has a different word where the statute
        # has another disagrees with the best read, and a clean complete read on another
        # image disagrees with a best read that has one: OCR drops and garbles words but
        # does not compose different ones, so the images do not show one statement, and
        # the outcome cannot depend on which photograph carried the heading.
        others = [
            (observation, _alignment(observation, expected_words))
            for observation in observations
            if observation is not best_observation
            and observation.body
            and len(_reader_words(observation)) >= len(expected_words) - 3
        ]
        disagreeing = None
        if wording.state != "Mismatch":
            shared = set(best_alignment.disagreements) if best_alignment is not None else set()
            disagreeing = next(
                (
                    (observation, unshared[0], best_alignment)
                    for observation, alignment in others
                    if (
                        unshared := [item for item in alignment.disagreements if item not in shared]
                    )
                ),
                None,
            )
        elif best_alignment is not None and best_alignment.disagreements:
            clean = next(
                (
                    alignment
                    for _observation, alignment in others
                    if not alignment.replaced and len(alignment.covered) >= len(expected_words) - 3
                ),
                None,
            )
            if clean is not None:
                disagreeing = (best_observation, best_alignment.disagreements[0], clean)
        if disagreeing is not None:
            observation, (position, expected_word, actual_word), other_alignment = disagreeing
            other_read_it = other_alignment is not None and position in other_alignment.covered
            wording = _result(
                "warning_wording",
                "Warning wording",
                "Review",
                "warning_images_disagree",
                f'The statement reads differently on two images: one reads "{actual_word}" '
                + (
                    f'where the statute and the other image have "{expected_word}"; '
                    if other_read_it
                    else f'where the statute has "{expected_word}"; '
                )
                + "confirm that the images show one product and read the statement on the label",
                observed=observation.body,
            ).model_copy(
                update={
                    "evidence_ref": (
                        observation.body_evidence.evidence_id
                        if observation.body_evidence
                        else wording.evidence_ref
                    )
                }
            )
            return [wording if item.check_id == "warning_wording" else item for item in best]
    if len(observations) < 2 or wording.state == "Match":
        return best
    if wording.reason_code == "warning_punctuation_uncertain":
        return best
    readers = [observation for observation in observations if observation.body]
    if len(readers) < 2:
        return best
    alignments = [_alignment(observation, expected_words) for observation in readers]
    # A word read differently on any image is a contradiction the other images cannot
    # confirm away; the images must agree wherever they overlap.
    if any(alignment.replaced for alignment in alignments):
        return best
    covered: set[int] = set()
    for alignment in alignments:
        covered.update(alignment.covered)
    if len(covered) < len(expected_words):
        return best
    confirmed = _result(
        "warning_wording",
        "Warning wording",
        "Review",
        "warning_words_confirmed_across_images",
        (
            f"Every statutory word was read in its place across {len(readers)} images; no "
            "single image shows the whole statement cleanly, so confirm the punctuation on "
            "the label"
        ),
        observed=best_observation.body,
    ).model_copy(update={"evidence_ref": wording.evidence_ref})
    return [confirmed if item.check_id == "warning_wording" else item for item in best]


def _row(checks: list[CheckResult]) -> CheckResult:
    return next(item for item in checks if item.check_id == "warning_wording")


def _reader_words(observation: WarningObservation) -> list[str]:
    return warning_words(warning_text(observation.body or "")).split()


def _alignment(observation: WarningObservation, expected_words: list[str]) -> _Alignment:
    actual_words = _reader_words(observation)
    starts, ends = _line_edges(
        observation.body_lines,
        lambda line: warning_words(warning_text(line)).split(),
        len(actual_words),
    )
    return _align(actual_words, expected_words, starts, ends)


def _wording_rank(check: CheckResult) -> int:
    """Higher is better evidence: a complete clean read, then a complete read with a
    difference, then partial or noisy reads, then nothing found."""

    if check.state == "Match":
        return 6 if check.reason_code == "warning_wording_exact" else 5
    if check.state == "Review" and check.reason_code == "warning_punctuation_uncertain":
        return 4
    if check.state == "Mismatch":
        return 3
    if check.state == "Review":
        return 2
    if check.reason_code in {"warning_not_found", "observed_unreadable"}:
        return 0
    return 1


def warning_checks(
    abv: Decimal | None,
    observed: WarningObservation,
    net_contents_value: Decimal = Decimal("750"),
    net_contents_unit: str = "mL",
    *,
    beverage_type: BeverageType | None = None,
    class_type: str | None = None,
) -> list[CheckResult]:
    warning = contracts().rules["warning"]
    threshold = Decimal(str(warning["applicabilityAbvPercentGte"]))
    required = abv is not None and abv >= threshold
    actual_heading = warning_text(observed.heading or "")
    actual_body = warning_text(observed.body or "")
    actual_full = warning_text(observed.full_text or "")
    class_reason = _required_by_class(beverage_type, class_type) if abv is None else None
    if abv is None and class_reason is not None:
        required = True
        applicability = _result(
            "warning_applicability",
            "Warning applicability",
            "Match",
            "warning_required_by_class",
            class_reason,
            reference=f"Required at {threshold}% ABV or more",
            observed=f"{beverage_type} designation",
        )
    elif abv is None:
        applicability = _result(
            "warning_applicability",
            "Warning applicability",
            "Review",
            "warning_applicability_unknown",
            "A trusted alcohol value is needed to decide whether the federal warning is required",
            reference=f"Required at {threshold}% ABV or more",
            observed="Alcohol value not established",
            capability="human_confirmation",
        )
    else:
        applicability = _result(
            "warning_applicability",
            "Warning applicability",
            "Match",
            "warning_required" if required else "warning_not_required",
            "The alcohol value establishes the federal warning applicability rule",
            reference=(f"ABV at least {threshold}%" if required else f"ABV below {threshold}%"),
            observed=f"{abv}% ABV",
        )
    if abv is not None and not required:
        return [applicability] + [
            _result(
                check_id,
                label,
                "Not verified",
                "not_applicable_warning_not_required",
                "This warning check is not applicable below the threshold",
                applicable=False,
            )
            for check_id, label in _warning_labels()
        ]

    if observed.source_unreadable and not actual_full:
        return [applicability] + [
            _result(
                check_id,
                label,
                "Not verified",
                "observed_unreadable",
                "The submitted image is not readable enough to verify this warning check",
                capability="human_confirmation"
                if check_id == "warning_physical_size"
                else "visual_heuristic",
            )
            for check_id, label in _warning_labels()
        ]

    heading_evidence = observed.heading_evidence
    body_evidence = observed.body_evidence
    expected_heading = str(warning["headingExact"])
    expected_body = str(warning["bodyExact"])
    comparable_body = actual_body.casefold()
    comparable_expected_body = expected_body.casefold()

    body_ref = body_evidence.evidence_id if body_evidence else None
    fragment = bool(actual_body) and not actual_heading
    if not actual_body:
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Not verified",
            "warning_not_found",
            "The required warning text was not found or was unreadable",
        )
    elif comparable_body == comparable_expected_body:
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Match",
            "warning_wording_exact",
            "The warning body wording and punctuation exactly match the prescribed statement",
        ).model_copy(update={"evidence_ref": body_ref})
    elif warning_words(actual_body) == warning_words(expected_body):
        # Every statutory word is present in order. Punctuation is compared separately
        # because OCR confuses commas, periods, and marker brackets and invents marks at
        # line wraps. A mark OCR cannot confuse, such as a clearly read exclamation point,
        # is a wording difference; any other punctuation difference is left to the reviewer
        # and never cleared by the machine, because the photograph cannot settle it.
        if _clear_terminal_punctuation_difference(actual_body, expected_body, body_evidence):
            wording = _result(
                "warning_wording",
                "Warning wording",
                "Mismatch",
                "warning_wording_difference",
                "Readable terminal punctuation differs from the prescribed statement",
                observed=actual_body,
            ).model_copy(update={"evidence_ref": body_ref})
        elif _same_ignoring_case_and_spacing(actual_body, expected_body):
            wording = _result(
                "warning_wording",
                "Warning wording",
                "Match",
                "warning_wording_exact",
                "The warning body wording and punctuation match the prescribed statement",
                observed=actual_body,
            ).model_copy(update={"evidence_ref": body_ref})
        else:
            wording = _result(
                "warning_wording",
                "Warning wording",
                "Review",
                "warning_punctuation_uncertain",
                (
                    "Every word matches the prescribed statement in order, but the "
                    "punctuation read differs ("
                    + _punctuation_difference(actual_body, expected_body)
                    + "); confirm commas, periods, and clause markers on the label"
                ),
                observed=actual_body,
            ).model_copy(update={"evidence_ref": body_ref})
    elif _material_wording_difference(
        actual_body, expected_body, body_evidence, observed.body_lines
    ):
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Mismatch",
            "warning_wording_difference",
            "Readable warning wording or punctuation differs from the prescribed statement",
            observed=actual_body,
        ).model_copy(update={"evidence_ref": body_evidence.evidence_id if body_evidence else None})
    else:
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Review",
            "warning_ocr_difference_uncertain",
            (
                "OCR differs from the prescribed statement, but the pixels require review "
                "before a label defect is asserted"
            ),
            observed=actual_body,
        ).model_copy(update={"evidence_ref": body_evidence.evidence_id if body_evidence else None})

    if fragment:
        heading_case = _not_in_view("warning_heading_uppercase", "Warning heading uppercase")
    elif not actual_heading:
        heading_case = _result(
            "warning_heading_uppercase",
            "Warning heading uppercase",
            "Not verified",
            "warning_heading_not_found",
            "The warning heading was not found or was unreadable",
        )
    elif actual_heading == expected_heading:
        heading_case = _result(
            "warning_heading_uppercase",
            "Warning heading uppercase",
            "Match",
            "warning_heading_exact",
            "The warning heading is exact and uppercase",
            observed=actual_heading,
        ).model_copy(
            update={"evidence_ref": heading_evidence.evidence_id if heading_evidence else None}
        )
    elif actual_heading.upper() == actual_heading and punctuation_folded(
        actual_heading
    ) == punctuation_folded(expected_heading):
        heading_case = _result(
            "warning_heading_uppercase",
            "Warning heading uppercase",
            "Review",
            "warning_heading_punctuation_uncertain",
            "The heading is uppercase, but exact punctuation requires review",
            observed=actual_heading,
        ).model_copy(
            update={"evidence_ref": heading_evidence.evidence_id if heading_evidence else None}
        )
    elif actual_heading.upper() == actual_heading and _edge_cut_heading(
        actual_heading, expected_heading
    ):
        # The photograph lost the end of the line ("GOVERNMENT WARNIN"); what was read is
        # uppercase and the statute's opening, so the reviewer confirms the rest by eye.
        heading_case = _result(
            "warning_heading_uppercase",
            "Warning heading uppercase",
            "Review",
            "warning_heading_edge_uncertain",
            "The heading is uppercase but cut off at the edge of the image; confirm "
            "GOVERNMENT WARNING: by eye",
            observed=actual_heading,
        ).model_copy(
            update={"evidence_ref": heading_evidence.evidence_id if heading_evidence else None}
        )
    else:
        heading_case = _result(
            "warning_heading_uppercase",
            "Warning heading uppercase",
            "Mismatch",
            "warning_heading_case_or_punctuation",
            "The warning heading capitalization or punctuation is not exact",
            observed=actual_heading,
        ).model_copy(
            update={"evidence_ref": heading_evidence.evidence_id if heading_evidence else None}
        )

    required_type_size_mm = _required_type_size_mm(net_contents_value, net_contents_unit)
    physical = _physical_size(observed, required_type_size_mm)
    if not actual_full:
        presentation = [
            _result(
                check_id,
                label,
                "Not verified",
                "warning_not_found",
                "The required warning evidence was not found in the submitted panels",
                capability="visual_heuristic",
            )
            for check_id, label in _warning_labels()[2:-1]
        ]
        return [applicability, wording, heading_case, *presentation, physical]
    return [
        applicability,
        wording,
        heading_case,
        _not_in_view("warning_heading_emphasis", "Warning heading emphasis")
        if fragment
        else _presentation(
            "warning_heading_emphasis",
            "Warning heading emphasis",
            observed.heading_bold,
            heading_evidence,
            pass_reason="The heading appears bold, heavier than the body",
            fail_reason=(
                "The heading appears no heavier than the body: either the heading is not "
                "bold or the body is; confirm on the label"
            ),
            # Type weight read from a photograph is never on its own a rejection.
            failure_requires_review=True,
        ),
        _presentation(
            "warning_body_not_bold",
            "Warning body not bold",
            None if observed.body_bold is None else not observed.body_bold,
            body_evidence,
            pass_reason="The warning body appears in regular weight, lighter than its heading",
            fail_reason=(
                "The warning body appears as heavy as its heading; confirm it is not bold"
            ),
            failure_requires_review=True,
        ),
        _not_in_view("warning_separation", "Warning separation")
        if fragment
        else _presentation(
            "warning_separation",
            "Warning separation",
            observed.separated,
            body_evidence,
            pass_reason="The warning appears separate from surrounding text",
            fail_reason=("Other text sits close to the warning; confirm it is separate and apart"),
            # OCR boxes are padded, so a small box gap is not proof that ink adjoins the
            # statement. Layout separation is a reviewer's call, never a machine rejection.
            failure_requires_review=True,
        ),
        _presentation(
            "warning_continuity",
            "Warning continuity",
            observed.continuous,
            body_evidence,
            pass_reason="The warning appears continuous",
            fail_reason="The warning is interrupted by unrelated text",
            # An interruption is a rejection only inside a cleanly read statement; a read
            # that skipped or garbled lines (a curved surface) cannot show what was printed
            # between the clauses.
            failure_requires_review=wording.state != "Match",
        ),
        _presentation(
            "warning_contrast",
            "Warning contrast",
            observed.contrast_sufficient,
            body_evidence,
            pass_reason="The warning contrast is visibly sufficient",
            fail_reason="The warning contrast is visibly insufficient",
        ),
        _presentation(
            "warning_legibility",
            "Warning legibility",
            observed.legible,
            body_evidence,
            pass_reason="The warning is visibly legible",
            fail_reason="The warning is not visibly legible",
        ),
        physical,
    ]


def _not_in_view(check_id: str, label: str) -> CheckResult:
    """A fragment shows body text without its heading: the heading's weight and the block's
    separation from the text around it are outside the photograph."""

    return _result(
        check_id,
        label,
        "Not verified",
        "warning_heading_not_in_view",
        "The heading is outside the image, so this cannot be judged from it; add a "
        "photograph that shows the whole statement",
        capability="visual_heuristic",
    )


def _required_type_size_mm(net_contents_value: Decimal, net_contents_unit: str) -> Decimal:
    milliliters = reference_volume_ml(net_contents_value, net_contents_unit)
    if milliliters > Decimal("3000"):
        return Decimal("3")
    if milliliters > Decimal("237"):
        return Decimal("2")
    return Decimal("1")


def _material_wording_difference(
    actual: str,
    expected: str,
    evidence: Evidence | None,
    body_lines: tuple[str, ...] = (),
) -> bool:
    confidence = (
        evidence.confidence_provenance.signal
        if evidence is not None and evidence.confidence_provenance.signal is not None
        else 0.0
    )
    if confidence < 0.8:
        return False
    actual_words = punctuation_folded(actual)
    expected_words = punctuation_folded(expected)
    if not actual_words:
        return False
    similarity = SequenceMatcher(None, actual_words, expected_words, autojunk=False).ratio()
    missing_second_clause = "(2)" not in warning_text(actual)
    expected_first_clause = punctuation_folded(expected.split("(2)", maxsplit=1)[0])
    # A first clause read in full with nothing after it is a label missing its second
    # clause; a read that stops inside the first clause is a photograph that cut it short.
    first_clause_is_clear = (
        missing_second_clause
        and len(actual_words.split()) >= len(expected_first_clause.split()) * 0.9
        and SequenceMatcher(
            None,
            actual_words,
            expected_first_clause,
            autojunk=False,
        ).ratio()
        >= 0.9
    )
    actual_tokens = set(actual_words.split())
    expected_tokens = set(expected_words.split())
    expected_token_overlap = (
        len(actual_tokens & expected_tokens) / len(actual_tokens) if actual_tokens else 0.0
    )
    if _truncated_read(actual_words, expected_words) and not first_clause_is_clear:
        return False
    # A read of fewer than three words ("2105900750" under a heading, a lone line) is not
    # wording that can be judged; the statement was not read.
    if sum(1 for token in actual_words.split() if any(c.isalpha() for c in token)) < 3:
        return False
    if _garbled_read(actual_words.split(), expected_words.split(), body_lines):
        return False
    starts, ends = _line_edges(
        body_lines,
        lambda line: punctuation_folded(warning_text(line)).split(),
        len(actual_words.split()),
    )
    return (
        _has_clear_word_substitution(actual_words, expected_words, starts, ends)
        or first_clause_is_clear
        or (similarity < 0.75 and expected_token_overlap < 0.6)
    )


def _garbled_read(
    actual_tokens: list[str], expected_tokens: list[str], body_lines: tuple[str, ...]
) -> bool:
    """A read whose damage is made of the statutory words themselves.

    A curved surface, glare, or a cut leaves statutory words glued together
    ("consumptionof", "1according"), broken so that only the end of a word remains
    ("coholic", "mpairs"), or scattered over one- and two-word lines. Such a read is not
    readable wording: the words of the statute are there, in pieces, and only a reviewer
    can tell what is printed. Text that says something else is made of whole words, and an
    inflected or shortened real word ("drinking", "alcohol") is a whole word, so it is
    judged as a difference.
    """

    vocabulary = frozenset(token for token in expected_tokens if len(token) >= 2)
    long_words = [token for token in expected_tokens if len(token) >= 4]
    damaged = 0
    for token in actual_tokens:
        if token in expected_tokens or len(token) < 3:
            continue
        if _glued_statutory_words(token, vocabulary) or _end_of_statutory_word(token, long_words):
            damaged += 1
    return damaged >= 3 or bool(actual_tokens and damaged / len(actual_tokens) >= 0.2)


def _glued_statutory_words(token: str, vocabulary: frozenset[str]) -> bool:
    """Two or more statutory words fused into one token, a clause marker fused to its
    word, or a stray leading character fused to a statutory word."""

    letters = token.lstrip("0123456789")
    marker = len(letters) < len(token)
    if not letters or len(letters) > 40:
        # Nothing on a label fuses more than a few words; a very long token is noise.
        return False
    words = _statutory_segments(letters, vocabulary)
    if words >= 2 or (marker and words >= 1):
        return True
    # A stray character read onto the front of a word ("hproblems"); a trailing letter is
    # an inflection ("drinks") and is left alone.
    return len(letters) >= 5 and letters[1:] in vocabulary


def _statutory_segments(text: str, vocabulary: frozenset[str]) -> int:
    """The number of statutory words that tile the text, allowing one leftover character at
    either end; -1 when no tiling exists."""

    def tile(remaining: str, leftover_allowed: bool) -> int:
        if not remaining:
            return 0
        if len(remaining) == 1 and leftover_allowed:
            return 0
        best = -1
        for end in range(2, len(remaining) + 1):
            if remaining[:end] in vocabulary:
                rest = tile(remaining[end:], leftover_allowed)
                if rest >= 0:
                    best = max(best, rest + 1)
        return best

    direct = tile(text, True)
    if direct >= 0:
        return direct
    # One stray character at the start.
    return tile(text[1:], False) if len(text) > 1 else -1


def _end_of_statutory_word(token: str, long_words: list[str]) -> bool:
    """The tail of a statutory word without its start ("ccording", "eral"): the start of a
    word can be cut by an edge or a glare, and such a tail is not a word of its own."""

    return any(
        word != token and word.endswith(token) and not word.startswith(token) for word in long_words
    )


def _line_edges(
    lines: tuple[str, ...], tokenize: Callable[[str], list[str]], total: int
) -> tuple[frozenset[int], frozenset[int]]:
    """Indexes of the words that start and end a read line.

    Only these can be cut by the edge of the photograph. Without the line structure, or when
    the lines do not account for every word, only the ends of the whole read qualify.
    """

    counts = [len(tokenize(line)) for line in lines]
    if not lines or sum(counts) != total:
        return frozenset({0}), frozenset({max(0, total - 1)})
    starts: set[int] = set()
    ends: set[int] = set()
    position = 0
    for count in counts:
        if count:
            starts.add(position)
            ends.add(position + count - 1)
            position += count
    return frozenset(starts), frozenset(ends)


def _edge_cut_heading(actual: str, expected: str) -> bool:
    """An uppercase heading that is the start of the statutory heading with its end missing."""

    folded_actual = punctuation_folded(actual)
    folded_expected = punctuation_folded(expected)
    return (
        len(folded_actual) >= len("government warnin")
        and folded_actual != folded_expected
        and folded_expected.startswith(folded_actual)
    )


def _same_ignoring_case_and_spacing(actual: str, expected: str) -> bool:
    """Equal text once letter case and spacing are set aside.

    27 CFR 16.22 fixes the case of the heading only, and OCR drops or invents spaces around
    the clause markers, so neither is a wording difference.
    """

    repaired = _GLUED_DIGIT.sub(r"(\1) ", actual)
    return re.sub(r"\s+", "", repaired).casefold() == re.sub(r"\s+", "", expected).casefold()


# A clause number glued to the next word ("1According") is how OCR renders a marker whose
# brackets it could not resolve; no label prints a digit fused to a word.
_GLUED_DIGIT = re.compile(r"(?<![\w.(])([12])(?=[A-Za-z])")


_PUNCTUATION_NAMES = {
    ",": "commas",
    ".": "periods",
    "(": "opening parentheses",
    ")": "closing parentheses",
    ";": "semicolons",
    ":": "colons",
    "'": "apostrophes",
    "-": "hyphens",
    "!": "exclamation points",
    "?": "question marks",
}


def _punctuation_difference(actual: str, expected: str) -> str:
    """Name the punctuation marks whose counts differ between the read and the statute."""

    marks = sorted(
        {character for character in actual + expected if not character.isalnum()}
        - {" ", "\t", "\n"}
    )
    parts = []
    for mark in marks:
        read, wanted = actual.count(mark), expected.count(mark)
        if read != wanted:
            name = _PUNCTUATION_NAMES.get(mark, f"'{mark}' marks")
            parts.append(f"{name} {read} read, {wanted} expected")
    return "; ".join(parts) if parts else "marks differ in position"


def _clear_terminal_punctuation_difference(
    actual: str, expected: str, evidence: Evidence | None
) -> bool:
    confidence = (
        evidence.confidence_provenance.signal
        if evidence is not None and evidence.confidence_provenance.signal is not None
        else 0.0
    )
    actual_terminal = actual.rstrip()[-1:] if actual.rstrip() else ""
    expected_terminal = expected.rstrip()[-1:] if expected.rstrip() else ""
    return (
        confidence >= 0.9
        and actual_terminal in {"!", "?"}
        and expected_terminal in {".", "!", "?"}
        and actual_terminal != expected_terminal
    )


# Six or more statutory words missing from one read mark a fragment of the statement.
_FRAGMENT_DELETIONS = 6


@dataclass(frozen=True)
class _Alignment:
    """How a read lines up with the statute, word by word."""

    clear: int
    noisy: int
    deleted: int
    replaced: int
    # Replacements by a different word, beyond what damaged characters explain: the
    # statute position, the statutory word, and the word read.
    disagreements: tuple[tuple[int, str, str], ...]
    covered: frozenset[int]


def _has_clear_word_substitution(
    actual: str,
    expected: str,
    line_starts: frozenset[int] = frozenset({0}),
    line_ends: frozenset[int] | None = None,
) -> bool:
    """A word replaced, dropped, or added in an otherwise cleanly read statement.

    One clearly different word is decisive only when the rest of the read is clean. A read
    peppered with one-letter OCR slips ("stoud", "becanse", "ney") is noise, and heavily
    damaged words inside it ("epers" for "impairs" on faint gray type) are more noise, not
    evidence of different wording. Clear differences therefore have to outnumber the noisy
    ones before the statement is called different; otherwise a reviewer reads it. A
    statutory word missing from the middle of a cleanly read statement ("women should
    drink") is a clear difference; a run of words missing at either end is a truncated
    read and stays with the reviewer.
    """

    actual_tokens = actual.split()
    expected_tokens = expected.split()
    if line_ends is None:
        line_ends = frozenset({max(0, len(actual_tokens) - 1)})
    alignment = _align(actual_tokens, expected_tokens, line_starts, line_ends)
    # A read missing this many statutory words is a fragment (a label cut by the edge of
    # the photograph loses the start or end of every line), not a label with words left out.
    if alignment.deleted >= _FRAGMENT_DELETIONS:
        return False
    return alignment.clear >= 1 and alignment.clear > alignment.noisy


def _align(
    actual_tokens: list[str],
    expected_tokens: list[str],
    line_starts: frozenset[int],
    line_ends: frozenset[int],
) -> _Alignment:
    """Count the clear and noisy differences between a read and the statute.

    A word at the start or end of a read line can be cut by the edge of the photograph, so
    a fragment of the statutory word there, or a word missing beside a line edge, is noise;
    the same difference inside a line is a substitution or an omission.
    """

    differences = SequenceMatcher(
        None, expected_tokens, actual_tokens, autojunk=False
    ).get_opcodes()
    clear = 0
    noisy = 0
    deleted = 0
    replaced = 0
    disagreements: list[tuple[int, str, str]] = []
    covered: set[int] = set()
    equal_positions = [index for index, opcode in enumerate(differences) if opcode[0] == "equal"]
    first_equal = equal_positions[0] if equal_positions else len(differences)
    last_equal = equal_positions[-1] if equal_positions else -1

    def at_edge(index: int) -> bool:
        return index in line_starts or index in line_ends

    for position, (tag, expected_start, expected_end, actual_start, actual_end) in enumerate(
        differences
    ):
        if tag == "equal":
            covered.update(range(expected_start, expected_end))
            continue
        expected_run = expected_tokens[expected_start:expected_end]
        actual_run = actual_tokens[actual_start:actual_end]
        if tag == "replace" and len(expected_run) == len(actual_run):
            for offset, (expected_word, actual_word) in enumerate(
                zip(expected_run, actual_run, strict=True)
            ):
                if _clearly_different_word(
                    expected_word, actual_word, at_edge=at_edge(actual_start + offset)
                ):
                    clear += 1
                    replaced += 1
                    if _different_word(expected_word, actual_word):
                        disagreements.append((expected_start + offset, expected_word, actual_word))
                else:
                    noisy += 1
            continue
        if tag == "replace":
            # A run read as a different number of words is a glue or a split when the
            # letters agree ("Surgeon General" as "SurgeonGeneral"). Counts that differ by
            # more than one mean the read merged or skipped words, which is noise.
            if abs(len(expected_run) - len(actual_run)) > 1:
                noisy += max(len(expected_run), len(actual_run))
            elif _clearly_different_word(
                "".join(expected_run),
                "".join(actual_run),
                at_edge=any(at_edge(index) for index in range(actual_start, actual_end)),
            ):
                clear += 1
                replaced += 1
                if _different_word("".join(expected_run), " ".join(actual_run)):
                    disagreements.append(
                        (expected_start, " ".join(expected_run), " ".join(actual_run))
                    )
            else:
                noisy += 1
            continue
        # A single statutory word missing from the middle of the read is an omission; a run
        # of three or more missing words is a line the read skipped, which is noise, and so
        # is a word missing where a read line begins or ends.
        interior = first_equal < position < last_equal
        run = expected_run if tag == "delete" else actual_run
        if tag == "delete":
            deleted += len(run)
            beside_edge = actual_start in line_starts or (actual_start - 1) in line_ends
        else:
            beside_edge = any(at_edge(index) for index in range(actual_start, actual_end))
        for word in run:
            if interior and len(word) >= 3 and len(run) < 3 and not beside_edge:
                clear += 1
            else:
                noisy += 1
    return _Alignment(clear, noisy, deleted, replaced, tuple(disagreements), frozenset(covered))


def _different_word(expected: str, actual: str) -> bool:
    """A word that is another word, not a damaged reading of the expected one.

    OCR garbles characters but does not compose words: "rjsx" for "risk" is damage, "may"
    for "should not" is a different statement. More than half the letters changed is the
    line between them.
    """

    words = actual.split()
    if not words or any(
        word not in _statute_vocabulary() and word not in _FUNCTION_WORDS for word in words
    ):
        # "tlie", "riot", "rnay": damaged characters, not another word.
        return False
    if len(expected) < 3 or any(len(word) < 3 for word in words):
        # Two-letter words are one slip away from each other ("to", "the", "of").
        return False
    return _edit_distance(expected, "".join(words)) > len(expected) / 2


_FUNCTION_WORDS = frozenset(
    [
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "the",
        "not",
        "no",
        "may",
        "in",
        "on",
        "at",
        "by",
        "for",
        "with",
        "from",
        "is",
        "are",
        "be",
        "will",
        "shall",
        "can",
        "must",
        "should",
        "could",
        "would",
        "do",
        "does",
        "never",
        "always",
        "any",
        "all",
    ]
)


def _statute_vocabulary() -> frozenset[str]:
    return frozenset(warning_words(str(contracts().rules["warning"]["bodyExact"])).split())


def _truncated_read(actual: str, expected: str) -> bool:
    """A read that follows the statute from the start and stops early.

    A crop or a curved surface can cut the statement short; when what was read is an
    orderly prefix of the statute, the remainder is missing from the read, not from the
    label, and the statement goes to the reviewer.
    """

    actual_tokens = actual.split()
    expected_tokens = expected.split()
    if not actual_tokens or len(actual_tokens) >= len(expected_tokens) * 0.8:
        return False
    prefix = " ".join(expected_tokens[: len(actual_tokens)])
    return SequenceMatcher(None, actual, prefix, autojunk=False).ratio() >= 0.8


def _clearly_different_word(expected: str, actual: str, *, at_edge: bool = False) -> bool:
    """A word substitution that OCR character noise cannot explain.

    One damaged character in a short word ("may" read as "ney") or two in a long one
    ("consumption" read as "consungtion") is ordinary OCR noise and stays a review item;
    a different word ("or" printed as "and") needs more edits than a third of its length.
    """

    # A word cut by the edge of the photograph arrives as a fragment of the statutory word
    # ("ccording", "eral", "ould"); only a word at the start or end of a read line can be
    # cut, so the same fragment inside a line ("alcohol" for "alcoholic beverages") is a
    # change of wording.
    if (
        at_edge
        and len(actual) >= 3
        and len(actual) < len(expected)
        and (expected.startswith(actual) or expected.endswith(actual))
    ):
        return False
    distance = _edit_distance(expected, actual)
    return distance > max(1, round(len(expected) * 0.34))


def _edit_distance(first: str, second: str) -> int:
    previous = list(range(len(second) + 1))
    for row, left in enumerate(first, start=1):
        current = [row]
        for column, right in enumerate(second, start=1):
            current.append(
                min(
                    previous[column] + 1,
                    current[column - 1] + 1,
                    previous[column - 1] + (left != right),
                )
            )
        previous = current
    return previous[-1]


def _physical_size(observed: WarningObservation, required_type_size_mm: Decimal) -> CheckResult:
    maximum_characters_per_inch = {
        Decimal("1"): Decimal("40"),
        Decimal("2"): Decimal("25"),
        Decimal("3"): Decimal("12"),
    }[required_type_size_mm]
    reference = (
        f"At least {required_type_size_mm} mm and no more than "
        f"{maximum_characters_per_inch} characters per inch for the stated container capacity"
    )
    if (
        not observed.reliable_scale
        or observed.physical_size_mm is None
        or observed.scale_evidence is None
    ):
        # An ordinary photograph carries no physical scale, so the millimeter rule is
        # reported for the reviewer to check against the artwork specification. It is not
        # applicable to the machine summary, which otherwise could never be clean.
        return _result(
            "warning_physical_size",
            "Warning physical size",
            "Not verified",
            "reliable_scale_unavailable",
            (
                "Physical type size and character density cannot be measured from an "
                "unscaled image; confirm against the artwork dimensions"
            ),
            applicable=False,
            reference=reference,
            capability="human_confirmation",
        )
    if Decimal(str(observed.physical_size_mm)) < required_type_size_mm:
        result = _result(
            "warning_physical_size",
            "Warning physical size",
            "Mismatch",
            "physical_size_below_required",
            "Reliable scale evidence indicates type below the required size",
            reference=reference,
            observed=f"{observed.physical_size_mm:.2f} mm",
            capability="scale_supported",
        )
        return result.model_copy(update={"evidence_ref": observed.scale_evidence.evidence_id})
    if observed.characters_per_inch is None:
        result = _result(
            "warning_physical_size",
            "Warning physical size",
            "Review",
            "character_density_unverified",
            "The minimum type size is supported, but character density requires review",
            reference=reference,
            observed=f"{observed.physical_size_mm:.2f} mm",
            capability="scale_supported_partial",
        )
        return result.model_copy(update={"evidence_ref": observed.scale_evidence.evidence_id})
    if Decimal(str(observed.characters_per_inch)) <= maximum_characters_per_inch:
        result = _result(
            "warning_physical_size",
            "Warning physical size",
            "Match",
            "physical_size_and_density_supported",
            (
                "Reliable scale evidence supports the required physical type size "
                "and character density"
            ),
            reference=reference,
            observed=(
                f"{observed.physical_size_mm:.2f} mm; "
                f"{observed.characters_per_inch:.1f} characters per inch"
            ),
            capability="scale_supported",
        )
        return result.model_copy(update={"evidence_ref": observed.scale_evidence.evidence_id})
    result = _result(
        "warning_physical_size",
        "Warning physical size",
        "Mismatch",
        "character_density_above_allowed",
        "Reliable scale evidence indicates too many characters per inch",
        reference=reference,
        observed=(
            f"{observed.physical_size_mm:.2f} mm; "
            f"{observed.characters_per_inch:.1f} characters per inch"
        ),
        capability="scale_supported",
    )
    return result.model_copy(update={"evidence_ref": observed.scale_evidence.evidence_id})


def _required_by_class(beverage_type: BeverageType | None, class_type: str | None) -> str | None:
    """Why the warning applies when no alcohol value was read.

    Wine under 27 CFR part 4 and distilled spirits under part 5 are, by definition, above
    the 0.5 percent applicability threshold in 27 CFR 16.10. A malt beverage carrying a
    recognized class designation is as well unless the label says it is non-alcoholic.
    """

    if beverage_type in {"wine", "distilled_spirits"}:
        family = "Wine" if beverage_type == "wine" else "Distilled spirits"
        return (
            f"{family} regulated under the FAA Act contains at least 0.5 percent alcohol "
            "by volume, so the federal warning applies"
        )
    if (
        beverage_type == "malt_beverage"
        and class_type
        and _RECOGNIZED_MALT_CLASS.search(class_type)
        and not _BELOW_THRESHOLD_CUE.search(class_type)
    ):
        return (
            "A malt beverage with a recognized class designation and no non-alcoholic "
            "statement contains at least 0.5 percent alcohol by volume"
        )
    return None


def _warning_labels() -> tuple[tuple[str, str], ...]:
    return (
        ("warning_wording", "Warning wording"),
        ("warning_heading_uppercase", "Warning heading uppercase"),
        ("warning_heading_emphasis", "Warning heading emphasis"),
        ("warning_body_not_bold", "Warning body not bold"),
        ("warning_separation", "Warning separation"),
        ("warning_continuity", "Warning continuity"),
        ("warning_contrast", "Warning contrast"),
        ("warning_legibility", "Warning legibility"),
        ("warning_physical_size", "Warning physical size"),
    )
