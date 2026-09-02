from __future__ import annotations

from decimal import Decimal
from difflib import SequenceMatcher

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import CheckResult, CheckState, Evidence
from labelverify.domain.comparison import _result
from labelverify.domain.normalize import punctuation_folded, reference_volume_ml, warning_text
from labelverify.domain.types import WarningObservation


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


def warning_checks(
    abv: Decimal | None,
    observed: WarningObservation,
    net_contents_value: Decimal = Decimal("750"),
    net_contents_unit: str = "mL",
) -> list[CheckResult]:
    warning = contracts().rules["warning"]
    threshold = Decimal(str(warning["applicabilityAbvPercentGte"]))
    required = abv is not None and abv >= threshold
    actual_heading = warning_text(observed.heading or "")
    actual_body = warning_text(observed.body or "")
    actual_full = warning_text(observed.full_text or "")
    if abv is None:
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

    if not actual_body:
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Not verified",
            "warning_not_found",
            "The required warning text was not found or was unreadable",
        )
    elif comparable_body == comparable_expected_body and observed.punctuation_normalized:
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Review",
            "ocr_wrap_punctuation_uncertain",
            (
                "OCR detected possible punctuation at a visual line wrap; "
                "exact wording requires review"
            ),
        ).model_copy(update={"evidence_ref": body_evidence.evidence_id if body_evidence else None})
    elif comparable_body == comparable_expected_body:
        wording = _result(
            "warning_wording",
            "Warning wording",
            "Match",
            "warning_wording_exact",
            "The warning body wording and punctuation exactly match the prescribed statement",
        ).model_copy(update={"evidence_ref": body_evidence.evidence_id if body_evidence else None})
    elif punctuation_folded(actual_body) == punctuation_folded(expected_body):
        if _clear_terminal_punctuation_difference(actual_body, expected_body, body_evidence):
            wording = _result(
                "warning_wording",
                "Warning wording",
                "Mismatch",
                "warning_wording_difference",
                "Readable terminal punctuation differs from the prescribed statement",
                observed=actual_body,
            ).model_copy(
                update={"evidence_ref": body_evidence.evidence_id if body_evidence else None}
            )
        else:
            wording = _result(
                "warning_wording",
                "Warning wording",
                "Review",
                "warning_punctuation_uncertain",
                "The words match, but exact punctuation requires review",
                observed=actual_body,
            ).model_copy(
                update={"evidence_ref": body_evidence.evidence_id if body_evidence else None}
            )
    elif _material_wording_difference(actual_body, expected_body, body_evidence):
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

    if not actual_heading:
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
        _presentation(
            "warning_heading_emphasis",
            "Warning heading emphasis",
            observed.heading_bold,
            heading_evidence,
            pass_reason="The heading appears bold",
            fail_reason="The heading does not appear bold",
            failure_requires_review=True,
        ),
        _presentation(
            "warning_body_not_bold",
            "Warning body not bold",
            None if observed.body_bold is None else not observed.body_bold,
            body_evidence,
            pass_reason="The warning body does not appear bold",
            fail_reason="The warning body appears bold",
            failure_requires_review=True,
        ),
        _presentation(
            "warning_separation",
            "Warning separation",
            observed.separated,
            body_evidence,
            pass_reason="The warning appears separate from surrounding text",
            fail_reason="The warning does not appear separate from surrounding text",
        ),
        _presentation(
            "warning_continuity",
            "Warning continuity",
            observed.continuous,
            body_evidence,
            pass_reason="The warning appears continuous",
            fail_reason="The warning is interrupted by unrelated text",
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


def _required_type_size_mm(net_contents_value: Decimal, net_contents_unit: str) -> Decimal:
    milliliters = reference_volume_ml(net_contents_value, net_contents_unit)
    if milliliters > Decimal("3000"):
        return Decimal("3")
    if milliliters > Decimal("237"):
        return Decimal("2")
    return Decimal("1")


def _material_wording_difference(actual: str, expected: str, evidence: Evidence | None) -> bool:
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
    first_clause_is_clear = (
        missing_second_clause
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
    return (
        _has_clear_word_substitution(actual_words, expected_words)
        or first_clause_is_clear
        or (similarity < 0.75 and expected_token_overlap < 0.6)
    )


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


def _has_clear_word_substitution(actual: str, expected: str) -> bool:
    actual_tokens = actual.split()
    expected_tokens = expected.split()
    differences = SequenceMatcher(
        None, expected_tokens, actual_tokens, autojunk=False
    ).get_opcodes()
    for tag, expected_start, expected_end, actual_start, actual_end in differences:
        if tag != "replace":
            continue
        expected_replacements = expected_tokens[expected_start:expected_end]
        actual_replacements = actual_tokens[actual_start:actual_end]
        if len(expected_replacements) != len(actual_replacements):
            continue
        if any(
            SequenceMatcher(None, expected_word, actual_word, autojunk=False).ratio() < 0.5
            for expected_word, actual_word in zip(
                expected_replacements, actual_replacements, strict=True
            )
        ):
            return True
    return False


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
        return _result(
            "warning_physical_size",
            "Warning physical size",
            "Not verified",
            "reliable_scale_unavailable",
            "Physical type size and character density cannot be verified from an unscaled image",
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
