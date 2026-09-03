"""Display-only presentation fields for the review UI (handoff REQ-3, 4, 5, 9, 10, 11, 12).

The UI never recomputes rules, grouping, or result states. Every value produced here is a
plain-language rendering of a governed check id, reason code, or quality signal so the
frontend can display it verbatim. Nothing in this module changes a check state, a summary,
or an evidence coordinate.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Literal

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import (
    BeverageInference,
    BeverageType,
    CheckResult,
    PanelResult,
    QualitySummary,
    WarningEvidence,
    WordingToken,
)
from labelverify.domain.types import ObservedCandidates

CheckGroup = Literal["identity", "content", "profile", "warning", "image"]

REASON_SHORT_MAX = 40

# Group, short label, and rule expectation per selected check. Rule expectations may vary by
# beverage type; the value keyed "default" applies when no type-specific text exists.
_CHECKS: dict[str, tuple[CheckGroup, str, dict[str, str]]] = {
    "beverage_type": (
        "identity",
        "Type",
        {"default": "Malt beverage, wine, or distilled spirits: selects the rule profile"},
    ),
    "brand": ("identity", "Brand", {"default": "Brand name present on the brand label"}),
    "class_type": (
        "identity",
        "Class",
        {"default": "Recognized class or type designation"},
    ),
    "abv": (
        "content",
        "Alcohol",
        {
            "default": "Authorized alcohol content statement",
            "wine": "Numeric percent alcohol by volume (7 to 14 percent may say table wine)",
            "distilled_spirits": "Authorized percent Alc./Vol. statement",
            "malt_beverage": "Alcohol content statement when stated or required",
        },
    ),
    "proof": ("content", "Proof", {"default": "Twice the ABV when printed"}),
    "net_contents": (
        "content",
        "Contents",
        {
            "default": "Net contents statement",
            "malt_beverage": "U.S. customary volume (metric may be additional)",
            "wine": "Metric statement",
            "distilled_spirits": "Metric statement for spirits",
        },
    ),
    "producer": (
        "content",
        "Bottler",
        {"default": "Role phrase, name, city and state"},
    ),
    "country": (
        "content",
        "Origin",
        {"default": "Visible origin statement when imported"},
    ),
    "wine_appellation": (
        "profile",
        "Appellation",
        {"default": "Appellation with a varietal or vintage designation (wine only)"},
    ),
    "wine_sulfites": (
        "profile",
        "Sulfites",
        {"default": "Contains sulfites when total SO2 is 10 ppm or more (wine only)"},
    ),
    "spirits_field_of_vision": (
        "profile",
        "Field of vision",
        {"default": "Brand, class and alcohol content on one container side (spirits only)"},
    ),
    "malt_class_designation": (
        "profile",
        "Malt class",
        {"default": "Recognized class such as beer, ale, lager, porter, stout (beer only)"},
    ),
    "warning_applicability": (
        "warning",
        "Required",
        {"default": "Any beverage at or above 0.5 percent alcohol"},
    ),
    "warning_wording": (
        "warning",
        "Wording",
        {"default": "Word-for-word statutory text including numbering"},
    ),
    "warning_heading_uppercase": (
        "warning",
        "Caps",
        {"default": "GOVERNMENT WARNING: in capitals"},
    ),
    "warning_heading_emphasis": ("warning", "Bold", {"default": "Heading in bold type"}),
    "warning_body_not_bold": (
        "warning",
        "Body weight",
        {"default": "Statement body in regular weight"},
    ),
    "warning_separation": (
        "warning",
        "Separate",
        {"default": "Not adjoining other label text"},
    ),
    "warning_continuity": ("warning", "Continuous", {"default": "One uninterrupted statement"}),
    "warning_contrast": ("warning", "Contrast", {"default": "Contrasting background"}),
    "warning_legibility": ("warning", "Legible", {"default": "Readily legible, not compressed"}),
    "warning_physical_size": (
        "warning",
        "Size",
        {"default": "Minimum type size for the container volume"},
    ),
    "panel_coverage": (
        "image",
        "Coverage",
        {"default": "Submitted surfaces cover the declared panels"},
    ),
    "image_quality": (
        "image",
        "Quality",
        {"default": "Sharp, exposed, no glare or skew"},
    ),
}

# Reason code to a short (40 character maximum) table cell phrase.
_REASON_SHORT: dict[str, str] = {
    "label_value_readable": "Found, not compared (label-derived)",
    "exact_match": "Exact match",
    "safe_representation_match": "Equivalent form",
    "safe_whitespace_match": "Equivalent spacing",
    "case_variation": "Case differs",
    "punctuation_variation": "Punctuation differs",
    "ocr_near_match": "Near match, confirm by eye",
    "definite_difference": "Differs from reference",
    "observed_not_found": "Not read on the label",
    "observed_unreadable": "Image too poor to read",
    "ambiguous_candidates": "Several candidates read",
    "ambiguous_numeric_parse": "Number could not be parsed",
    "numeric_match": "Value matches",
    "numeric_difference": "Value differs",
    "equivalent_volume_match": "Equivalent volume",
    "not_applicable": "Not applicable",
    "not_applicable_domestic": "Not imported",
    "not_applicable_beverage_type": "Other beverage type",
    "not_applicable_malt_optional": "Optional for malt beverages",
    "not_applicable_warning_not_required": "Warning not required",
    "beverage_type_supported": "Inferred from class, high confidence",
    "beverage_type_uncertain": "Type unclear, confirm",
    "beverage_type_conflict": "Conflicting type signals",
    "beverage_type_required_for_rule": "Needs the beverage type first",
    "abv_abbreviation_not_authorized": "ABV abbreviation not authorized",
    "alcohol_range_not_authorized": "Range not authorized here",
    "wine_alcohol_range_supported": "Authorized wine range",
    "wine_alcohol_range_invalid": "Range outside the allowed spread",
    "wine_alcohol_range_requires_actual_value": "Range needs an actual value",
    "wine_table_light_exception": "Table wine exception",
    "malt_alcohol_precision_invalid": "Malt precision not authorized",
    "malt_abv_trigger_unknown": "Malt alcohol trigger unknown",
    "malt_customary_net_contents_missing": "U.S. customary volume missing",
    "reference_abv_unavailable": "No trusted alcohol value",
    "reference_abv_proof_inconsistent": "Proof and ABV disagree",
    "proof_abv_relationship_match": "Proof = 2 x ABV",
    "proof_abv_relationship_and_placement_match": "Proof = 2 x ABV, same field",
    "proof_requires_actual_abv": "Proof needs an actual ABV",
    "proof_distinction_requires_review": "Proof vs ABV unclear",
    "proof_field_of_vision_split": "Proof not beside ABV",
    "producer_formatting_variation": "Formatting varies",
    "incomplete_plausible_designation": "Designation incomplete",
    "recognized_malt_class": "Recognized class",
    "ipa_alone_not_recognized": "IPA alone is not a class",
    "malt_specialty_designation_review": "Specialty designation, review",
    "wine_brand_label_placement_review": "Confirm brand-label placement",
    "wine_appellation_not_found": "No appellation read",
    "wine_appellation_found": "Appellation read",
    "wine_appellation_placement_review": "Appellation on another panel",
    "warning_words_confirmed_across_images": "Words confirmed across images; confirm punctuation",
    "warning_heading_edge_uncertain": "Heading cut off at the image edge; confirm",
    "warning_fragment_review": "Only part of the statement in view; add a photo",
    "reference_found_on_label": "Application value found on label",
    "reference_found_within_label_text": "Found inside a longer statement",
    "reference_within_longer_text": "Inside a longer line; confirm",
    "warning_required_by_class": "Required for this beverage class",
    "malt_abv_optional_unless_added_alcohol": "Optional unless added alcohol",
    "proof_adjacent_to_abv": "Proof = 2 x ABV, beside it",
    "wine_appellation_trigger_not_found": "No varietal or vintage trigger",
    "sulfite_declaration_found": "Declaration present",
    "sulfite_declaration_not_found": "No declaration read",
    "sulfite_threshold_not_triggered": "Threshold not triggered",
    "sulfite_chemistry_unknown": "Chemistry unknown",
    "field_of_vision_supported": "All three on one face",
    "field_of_vision_split": "Split across faces",
    "field_of_vision_evidence_incomplete": "Evidence incomplete",
    "import_status_unknown": "Import status unknown",
    "warning_required": "Required at this ABV",
    "warning_not_required": "Below 0.5 percent",
    "warning_applicability_unknown": "Alcohol value not established",
    "warning_wording_exact": "Word for word",
    "warning_wording_difference": "Wording differs",
    "warning_punctuation_uncertain": "Punctuation needs review",
    "warning_ocr_difference_uncertain": "OCR differs, confirm by eye",
    "ocr_wrap_punctuation_uncertain": "Line-wrap punctuation unclear",
    "warning_not_found": "Warning not read",
    "warning_heading_exact": "All capitals",
    "warning_heading_not_found": "Heading not read",
    "warning_heading_punctuation_uncertain": "Colon needs review",
    "warning_heading_case_or_punctuation": "Not all capitals",
    "presentation_supported": "Supported by the image",
    "presentation_failure": "Visible defect",
    "presentation_requires_review": "Confirm by eye",
    "quality_degraded_observation": "Image quality limits this",
    "reliable_scale_unavailable": "Needs a ruler, not a photo",
    "scale_supported": "Scale supported",
    "scale_supported_partial": "Scale partly supported",
    "physical_size_below_required": "Below the required size",
    "physical_size_and_density_supported": "Size and density supported",
    "character_density_unverified": "Character density unverified",
    "character_density_above_allowed": "Too many characters per inch",
    "panel_coverage_sufficient": "Panels cover the label",
    "panel_coverage_uncertain": "Coverage uncertain",
    "panel_coverage_absent": "A panel appears missing",
    "image_quality_sufficient": "Good",
    "image_quality_uncertain": "Quality needs review",
    "image_unreadable": "Image unreadable",
}

_HIGH_CONFIDENCE = 0.85
_MEDIUM_CONFIDENCE = 0.75


def check_group(check_id: str) -> CheckGroup:
    return _CHECKS[check_id][0]


def short_label(check_id: str) -> str:
    return _CHECKS[check_id][1]


def rule_expectation(check_id: str, beverage_type: BeverageType | None) -> str:
    variants = _CHECKS[check_id][2]
    if beverage_type is not None and beverage_type in variants:
        return variants[beverage_type]
    return variants["default"]


def reason_short(check: CheckResult) -> str:
    phrase = _REASON_SHORT.get(check.reason_code)
    if phrase is None:
        phrase = check.reason_text
    return _clip(phrase)


def _clip(value: str) -> str:
    text = " ".join(value.split())
    if len(text) <= REASON_SHORT_MAX:
        return text
    return text[: REASON_SHORT_MAX - 1].rstrip() + "…"


_APPLICATION_COMPARED_CHECKS = {
    "brand",
    "class_type",
    "abv",
    "proof",
    "net_contents",
    "producer",
    "country",
}


def present_checks(
    checks: list[CheckResult],
    beverage_type: BeverageType | None,
    reference_provenance: str = "label_ocr",
) -> list[CheckResult]:
    """Attach display fields; an application comparison shows the application value."""

    compared = reference_provenance != "label_ocr"
    return [
        check.model_copy(
            update={
                "group": check_group(check.check_id),
                "short_label": short_label(check.check_id),
                "rule_expectation": (
                    f"Application: {check.reference_display}"
                    if compared
                    and check.check_id in _APPLICATION_COMPARED_CHECKS
                    and check.reference_display
                    else rule_expectation(check.check_id, beverage_type)
                ),
                "reason_short": reason_short(check),
            }
        )
        for check in checks
    ]


def quality_summary(panel: PanelResult) -> QualitySummary:
    signals = panel.quality_signals
    issues: list[str] = []
    laplacian = _number(signals.get("laplacianVariance"))
    dark = _number(signals.get("darkFraction"))
    light = _number(signals.get("lightFraction"))
    clipped = _number(signals.get("clippedHighlightFraction"))
    skew = _number(signals.get("estimatedSkewDegrees"))
    if laplacian is not None and laplacian < 55.0:
        issues.append("blur")
    if dark is not None and dark > 0.55:
        issues.append("underexposed")
    if light is not None and light > 0.80:
        issues.append("overexposed")
    if clipped is not None and clipped > 0.20:
        issues.append("glare")
    if skew is not None and abs(skew) >= 1.5:
        issues.append("skew")
    if panel.coverage_state == "Unreadable":
        grade: Literal["good", "poor", "unreadable"] = "unreadable"
    elif panel.coverage_state == "Review" or issues:
        grade = "poor"
    else:
        grade = "good"
    return QualitySummary(grade=grade, issues=issues)


def bad_image(panels: list[PanelResult]) -> bool:
    """True when every submitted panel is unreadable (handoff REQ-18)."""

    return bool(panels) and all(panel.coverage_state == "Unreadable" for panel in panels)


def present_panels(panels: list[PanelResult]) -> list[PanelResult]:
    return [
        panel.model_copy(update={"quality_summary": quality_summary(panel)}) for panel in panels
    ]


def beverage_inference(
    beverage_type: BeverageType | None,
    confidence: float | None,
    reason: str,
    *,
    conflicting: bool,
) -> BeverageInference:
    if beverage_type is None or confidence is None:
        level: Literal["high", "medium", "low"] = "low"
    elif confidence >= _HIGH_CONFIDENCE:
        level = "high"
    elif confidence >= _MEDIUM_CONFIDENCE:
        level = "medium"
    else:
        level = "low"
    return BeverageInference(
        type=beverage_type, confidence=level, reason=reason, conflicting=conflicting
    )


def warning_evidence(observed: ObservedCandidates) -> WarningEvidence:
    warning = observed.warning
    return WarningEvidence(
        headingRef=warning.heading_evidence.evidence_id if warning.heading_evidence else None,
        bodyRef=warning.body_evidence.evidence_id if warning.body_evidence else None,
    )


def statutory_tokens() -> list[str]:
    warning = contracts().rules["warning"]
    return f"{warning['headingExact']} {warning['bodyExact']}".split()


def wording_diff(
    observed_heading: str | None, observed_body: str | None
) -> tuple[list[WordingToken], int, int]:
    """Align the read warning to the statutory tokens (REQ-11).

    Heading tokens compare exactly because the heading must be uppercase. Body tokens
    compare case-insensitively, matching the governed wording rule, so an all-capitals body
    still matches word for word.
    """

    warning = contracts().rules["warning"]
    expected_heading = str(warning["headingExact"]).split()
    expected_body = str(warning["bodyExact"]).split()
    expected = expected_heading + expected_body
    total = len(expected)
    heading_count = len(expected_heading)
    read = " ".join((observed_heading or "").split() + (observed_body or "").split())
    observed = read.split()
    if not observed:
        return (
            [WordingToken(expected=token, observed=None, status="missing") for token in expected],
            0,
            total,
        )

    def key(index: int, token: str) -> str:
        return token if index < heading_count else token.casefold()

    expected_keys = [key(index, token) for index, token in enumerate(expected)]
    # Observed tokens are compared with the same rule as the expected slot they align to;
    # casefold everything first, then re-check the heading slots exactly.
    matcher = SequenceMatcher(
        a=[token.casefold() for token in expected_keys],
        b=[token.casefold() for token in observed],
        autojunk=False,
    )
    tokens: list[WordingToken] = []
    matched = 0
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(a1 - a0):
                index = a0 + offset
                seen = observed[b0 + offset]
                exact = seen == expected[index] if index < heading_count else True
                status: Literal["match", "different"] = "match" if exact else "different"
                if exact:
                    matched += 1
                tokens.append(WordingToken(expected=expected[index], observed=seen, status=status))
        elif tag == "replace":
            span = max(a1 - a0, b1 - b0)
            for offset in range(span):
                index = a0 + offset
                replaced = observed[b0 + offset] if b0 + offset < b1 else None
                if index < a1:
                    tokens.append(
                        WordingToken(
                            expected=expected[index],
                            observed=replaced,
                            status="different" if replaced is not None else "missing",
                        )
                    )
                elif replaced is not None:
                    tokens.append(WordingToken(expected=None, observed=replaced, status="extra"))
        elif tag == "delete":
            for index in range(a0, a1):
                tokens.append(
                    WordingToken(expected=expected[index], observed=None, status="missing")
                )
        elif tag == "insert":
            for offset in range(b0, b1):
                tokens.append(
                    WordingToken(expected=None, observed=observed[offset], status="extra")
                )
    return tokens, matched, total


def present_wording(checks: list[CheckResult], observed: ObservedCandidates) -> list[CheckResult]:
    warning = observed.warning
    if warning.body is None and warning.heading is None and warning.full_text is None:
        return checks
    tokens, matched, total = wording_diff(warning.heading, warning.body)
    return [
        check.model_copy(
            update={"wording_diff": tokens, "matched_words": matched, "total_words": total}
        )
        if check.check_id == "warning_wording" and check.applicable
        else check
        for check in checks
    ]


def _number(value: float | bool | str | None) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None
