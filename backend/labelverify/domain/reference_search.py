"""Reference-guided matching of application values against every OCR line.

The primary label-first flow chooses one candidate per field before any application record
exists. When a reviewer supplies the application values (brand, class, alcohol content, net
contents, producer, country), the question changes from "what does the label say?" to "does
the label carry this value anywhere?". A field whose chosen candidate differs from the
application is therefore re-examined against all readable lines before it is reported as a
difference, so an OCR mis-selection cannot masquerade as a label defect. Extraction itself
never sees the reference; this search runs on the observed lines afterwards.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal

from labelverify.contracts.models import (
    Candidate,
    CheckResult,
    ConfidenceProvenance,
    Evidence,
    OcrLine,
    Point,
    ReferenceRecord,
)
from labelverify.domain.comparison import _result
from labelverify.domain.normalize import (
    casefolded,
    looks_like_business_line,
    parse_abv,
    parse_proof,
    parse_volume_ml,
    punctuation_folded,
    reference_volume_ml,
    whitespace,
)
from labelverify.domain.types import ObservedCandidates

_SEARCHED_TEXT_FIELDS = {
    "brand": ("brand_name", True),
    "class_type": ("class_type", False),
    "producer": ("producer_name_address", False),
    "country": ("country_of_origin", False),
    "wine_appellation": ("wine_appellation", False),
}
# Conflicting label statements for these fields need a reviewer even when one of them
# matches the application; the search must not hide the conflict.
_CONFLICT_SENSITIVE = {"country", "abv", "proof", "net_contents"}
# Only a check that failed because extraction chose the wrong text, or found none, is
# re-examined against the lines. A rule-format or placement failure (an unauthorized
# abbreviation, an alcohol range that crosses a class boundary, a split field of vision)
# describes the label statement itself and stands whatever the application says.
_SEARCHABLE_REASONS = {
    "observed_not_found",
    "definite_difference",
    "numeric_difference",
    "ambiguous_candidates",
    "ambiguous_numeric_parse",
    "case_variation",
    "punctuation_variation",
    "ocr_near_match",
    "producer_formatting_variation",
}
# A percentage is an alcohol statement only in alcohol context; "CONTAINS 5% REAL FRUIT
# JUICE" is not a five percent alcohol content.
_ALCOHOL_CONTEXT = re.compile(r"\b(?:alc|alcohol|vol|volume|abv|proof)\b", re.I)


@dataclass(frozen=True)
class LineMatch:
    lines: list[OcrLine]
    quality: str  # exact, case, punctuation, contained


def apply_reference_search(
    checks: list[CheckResult], reference: ReferenceRecord, observed: ObservedCandidates
) -> list[CheckResult]:
    """Upgrade non-matching field checks when the application value is on the label."""

    if reference.reference_provenance == "label_ocr" or not observed.lines:
        return checks
    updated: list[CheckResult] = []
    for check in checks:
        replacement = None
        conflicting = (
            check.reason_code == "ambiguous_candidates" and check.check_id in _CONFLICT_SENSITIVE
        )
        searchable = check.reason_code in _SEARCHABLE_REASONS
        if check.applicable and check.state != "Match" and searchable and not conflicting:
            if check.check_id in _SEARCHED_TEXT_FIELDS:
                attribute, brand_case_matters = _SEARCHED_TEXT_FIELDS[check.check_id]
                value = getattr(reference, attribute)
                if isinstance(value, str) and value.strip():
                    replacement = _text_search(check, value, observed, brand_case_matters)
            elif check.check_id == "abv" and reference.abv_percent is not None:
                replacement = _number_search(
                    check,
                    reference.abv_percent,
                    observed,
                    parse_abv,
                    f"{reference.abv_percent}%",
                    context=_ALCOHOL_CONTEXT,
                )
            elif check.check_id == "proof" and reference.proof is not None:
                replacement = _number_search(
                    check, reference.proof, observed, parse_proof, f"{reference.proof} proof"
                )
            elif check.check_id == "net_contents":
                expected = reference_volume_ml(
                    reference.net_contents_value, reference.net_contents_unit
                )
                replacement = _number_search(
                    check,
                    expected,
                    observed,
                    parse_volume_ml,
                    f"{reference.net_contents_value} {reference.net_contents_unit}",
                    tolerance=Decimal("1"),
                )
        updated.append(replacement or check)
    return updated


def _text_search(
    check: CheckResult, value: str, observed: ObservedCandidates, brand_case_matters: bool
) -> CheckResult | None:
    match = find_text(value, observed.lines)
    if match is None:
        return None
    candidate = _candidate(check.check_id, match.lines, observed)
    observed_text = whitespace(" ".join(line.text for line in match.lines))
    if match.quality == "exact" or (match.quality == "case" and not brand_case_matters):
        return _result(
            check.check_id,
            check.label,
            "Match",
            "reference_found_on_label",
            "The application value was found on the label",
            reference=value,
            observed=observed_text,
            candidate=candidate,
        )
    if match.quality == "case":
        return _result(
            check.check_id,
            check.label,
            "Review",
            "case_variation",
            "The application value appears on the label with different capitalization; "
            "reviewer judgment is required",
            reference=value,
            observed=observed_text,
            candidate=candidate,
        )
    if match.quality == "punctuation":
        return _result(
            check.check_id,
            check.label,
            "Review",
            "punctuation_variation",
            "The application value appears on the label with different punctuation; "
            "reviewer judgment is required",
            reference=value,
            observed=observed_text,
            candidate=candidate,
        )
    if brand_case_matters and all(looks_like_business_line(line.text) for line in match.lines):
        # The application brand found only inside the company name or address ("OLD TOM
        # DISTILLERY" within "OLD TOM DISTILLERY LLC, FRANKFORT, KY") is the responsible
        # business, not the brand the label sells under; the difference stands.
        return None
    if brand_case_matters:
        # A brand that only appears inside a longer line ("OLD TOM" within "OLD TOM
        # DISTILLERY") may be a different brand name; the reviewer decides.
        return _result(
            check.check_id,
            check.label,
            "Review",
            "reference_within_longer_text",
            "The application value appears inside a longer label statement; confirm it is "
            "the brand name as labeled",
            reference=value,
            observed=observed_text,
            candidate=candidate,
        )
    return _result(
        check.check_id,
        check.label,
        "Match",
        "reference_found_within_label_text",
        "The application value was found within a longer label statement",
        reference=value,
        observed=observed_text,
        candidate=candidate,
    )


def find_text(value: str, lines: list[OcrLine]) -> LineMatch | None:
    """Locate a reference value in single lines, then in stacked pairs and triples."""

    wanted_exact = whitespace(value)
    wanted_case = casefolded(value)
    wanted_words = punctuation_folded(value)
    if not wanted_words:
        return None
    best: LineMatch | None = None
    ranking = {"exact": 0, "case": 1, "punctuation": 2, "contained": 3}

    def consider(candidate_lines: list[OcrLine]) -> None:
        nonlocal best
        text = whitespace(" ".join(line.text for line in candidate_lines))
        if text == wanted_exact:
            quality = "exact"
        elif casefolded(text) == wanted_case:
            quality = "case"
        elif punctuation_folded(text) == wanted_words:
            quality = "punctuation"
        elif _contains_words(punctuation_folded(text), wanted_words):
            quality = "contained"
        else:
            return
        if best is None or ranking[quality] < ranking[best.quality]:
            best = LineMatch(list(candidate_lines), quality)

    for line in lines:
        consider([line])
    if best is not None and best.quality in {"exact", "case"}:
        return best
    ordered = sorted(lines, key=lambda item: (item.panel_id, min(p.y for p in item.polygon)))
    for index, line in enumerate(ordered):
        group = [line]
        for follower in ordered[index + 1 : index + 3]:
            if follower.panel_id != line.panel_id or not _stacked(group[-1], follower):
                break
            group.append(follower)
            consider(list(group))
    return best


def _contains_words(haystack: str, needle: str) -> bool:
    return re.search(rf"(?<!\w){re.escape(needle)}(?!\w)", haystack) is not None


def _stacked(upper: OcrLine, lower: OcrLine) -> bool:
    upper_bottom = max(point.y for point in upper.polygon)
    lower_top = min(point.y for point in lower.polygon)
    height = max(
        1, max(point.y for point in upper.polygon) - min(point.y for point in upper.polygon)
    )
    upper_left = min(point.x for point in upper.polygon)
    upper_right = max(point.x for point in upper.polygon)
    lower_left = min(point.x for point in lower.polygon)
    lower_right = max(point.x for point in lower.polygon)
    overlap = min(upper_right, lower_right) - max(upper_left, lower_left)
    return -height * 0.2 <= lower_top - upper_bottom <= height * 1.5 and overlap > 0


def _number_search(
    check: CheckResult,
    expected: Decimal,
    observed: ObservedCandidates,
    parser: Callable[[str], Decimal | None],
    reference_display: str,
    *,
    tolerance: Decimal = Decimal("0"),
    context: re.Pattern[str] | None = None,
) -> CheckResult | None:
    found_values: list[tuple[OcrLine, Decimal]] = []
    for line in observed.lines:
        if context is not None and context.search(line.text) is None:
            continue
        value = parser(line.text)
        if value is not None:
            found_values.append((line, value))
    for line, value in found_values:
        if abs(value - expected) <= tolerance:
            candidate = _candidate(check.check_id, [line], observed)
            return _result(
                check.check_id,
                check.label,
                "Match",
                "reference_found_on_label",
                "The application value was found on the label",
                reference=reference_display,
                observed=whitespace(line.text),
                candidate=candidate,
            )
    return None


def _candidate(field: str, lines: list[OcrLine], observed: ObservedCandidates) -> Candidate:
    """Register evidence for a reference match so the UI can highlight it."""

    xs = [point.x for line in lines for point in line.polygon]
    ys = [point.y for line in lines for point in line.polygon]
    # A degenerate box (an OCR line with no height or width) still needs a positive area
    # to be drawn and to pass the result integrity check.
    left, right = min(xs), max(max(xs), min(xs) + 1)
    top, bottom = min(ys), max(max(ys), min(ys) + 1)
    sequence = sum(1 for item in observed.evidence if item.evidence_id.startswith("ev_ref_"))
    first = lines[0]
    evidence = Evidence(
        evidenceId=f"ev_ref_{field}_{first.panel_id}_{sequence + 1:02d}",
        panelId=first.panel_id,
        polygonOriginalPixels=[
            Point(x=left, y=top),
            Point(x=right, y=top),
            Point(x=right, y=bottom),
            Point(x=left, y=bottom),
        ],
        sourceView="derived"
        if any(line.source_view == "derived" for line in lines)
        else "original",
        transformId=first.transform_id,
        textSnippet=whitespace(" ".join(line.text for line in lines)),
        confidenceProvenance=ConfidenceProvenance(
            source="rapidocr",
            signal=min(
                (line.confidence for line in lines if line.confidence is not None), default=None
            ),
            calibratedProbability=False,
        ),
    )
    observed.evidence.append(evidence)
    return Candidate(value=evidence.text_snippet or "", evidence=evidence)
