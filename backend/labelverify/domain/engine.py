from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

from labelverify.contracts.models import CheckResult, ReferenceRecord, SummaryState
from labelverify.domain.aggregation import aggregate, validate_check_set
from labelverify.domain.beverage import beverage_type_hits
from labelverify.domain.comparison import (
    _result,
    compare_abv,
    compare_class,
    compare_country,
    compare_net_contents,
    compare_producer,
    compare_proof,
    compare_text,
)
from labelverify.domain.types import ObservedCandidates
from labelverify.domain.warnings import warning_checks


@dataclass(frozen=True)
class ComparisonInputs:
    reference: ReferenceRecord
    observed: ObservedCandidates


def compare_all(inputs: ComparisonInputs) -> tuple[list[CheckResult], SummaryState]:
    reference = inputs.reference
    observed = inputs.observed
    checks = [
        _beverage_type(reference, observed),
        compare_text("brand", "Brand name", reference.brand_name, observed.field("brand")),
        _class_type(reference, observed),
        _alcohol_content(reference, observed),
        _proof(reference, observed),
        _net_contents(reference, observed),
        compare_producer(reference.producer_name_address, observed.field("producer")),
        compare_country(
            _import_status(reference, observed),
            reference.country_of_origin,
            observed.field("country"),
        ),
        _wine_appellation(reference, observed),
        _wine_sulfites(reference, observed),
        _spirits_field_of_vision(reference, observed),
        _malt_class_designation(reference),
        *warning_checks(
            _warning_abv(reference),
            observed.warning,
            reference.net_contents_value,
            reference.net_contents_unit,
        ),
        _panel_coverage(observed),
        _image_quality(observed),
    ]
    checks = _label_derived_reference_guard(checks, reference)
    checks = _guard_degraded_evidence(checks, observed)
    validate_check_set(checks)
    return checks, aggregate(checks)


def mark_unresolved_beverage(checks: list[CheckResult]) -> tuple[list[CheckResult], SummaryState]:
    """Preserve the 24-row result while preventing profile-specific conclusions."""

    type_dependent = {
        "abv",
        "proof",
        "net_contents",
        "wine_appellation",
        "wine_sulfites",
        "spirits_field_of_vision",
        "malt_class_designation",
    }
    guarded: list[CheckResult] = []
    for check in checks:
        if check.check_id == "beverage_type":
            guarded.append(
                check.model_copy(
                    update={
                        "state": "Review",
                        "reason_code": "beverage_type_uncertain",
                        "reason_text": (
                            "The label does not provide one unambiguous beverage-type signal"
                        ),
                        "reference_display": None,
                        "observed_display": None,
                    }
                )
            )
        elif check.check_id in type_dependent:
            guarded.append(
                check.model_copy(
                    update={
                        "applicable": True,
                        "state": "Review",
                        "reason_code": "beverage_type_required_for_rule",
                        "reason_text": (
                            "Resolve the beverage type before applying this profile-specific rule"
                        ),
                    }
                )
            )
        else:
            guarded.append(check)
    validate_check_set(guarded)
    return guarded, aggregate(guarded)


def _label_derived_reference_guard(
    checks: list[CheckResult], reference: ReferenceRecord
) -> list[CheckResult]:
    if reference.reference_provenance != "label_ocr":
        return checks
    comparison_ids = {"brand", "class_type", "abv", "proof", "net_contents", "producer", "country"}
    return [
        check.model_copy(
            update={
                "reason_code": "label_value_readable",
                "reason_text": (
                    "OCR confirms readable label evidence; this is not an independent "
                    "COLA application comparison"
                ),
            }
        )
        if check.check_id in comparison_ids and check.state == "Match"
        else check
        for check in checks
    ]


_DOMESTIC_LOCATION = re.compile(
    r"\b(?:u\.?s\.?a\.?|united\s+states|alabama|alaska|arizona|arkansas|california|"
    r"colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|"
    r"iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|"
    r"mississippi|missouri|montana|nebraska|nevada|new\s+hampshire|new\s+jersey|"
    r"new\s+mexico|new\s+york|north\s+carolina|north\s+dakota|ohio|oklahoma|oregon|"
    r"pennsylvania|rhode\s+island|south\s+carolina|south\s+dakota|tennessee|texas|"
    r"utah|vermont|virginia|washington|west\s+virginia|wisconsin|wyoming)\b|"
    r"(?:,|\.)\s*(?:AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|"
    r"MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|"
    r"VT|VA|WA|WV|WI|WY)\b",
    re.I,
)
def _import_status(reference: ReferenceRecord, observed: ObservedCandidates) -> bool | None:
    if reference.reference_provenance != "label_ocr":
        return reference.is_imported
    if observed.field("country").status in {"Found", "Ambiguous"}:
        return True
    producer_text = " ".join(
        candidate.value for candidate in observed.field("producer").candidates
    )
    if re.search(r"\bimported\s+by\b", producer_text, re.I):
        return True
    if _DOMESTIC_LOCATION.search(producer_text):
        return False
    return None


def _beverage_type(reference: ReferenceRecord, observed: ObservedCandidates) -> CheckResult:
    hits = beverage_type_hits(observed)
    if reference.beverage_type in hits and len(hits) == 1:
        return _result(
            "beverage_type",
            "Beverage type",
            "Match",
            "beverage_type_supported",
            "The readable class or type supports the selected beverage profile",
            reference=reference.beverage_type,
            observed=reference.beverage_type,
        )
    if hits and reference.beverage_type not in hits:
        return _result(
            "beverage_type",
            "Beverage type",
            "Mismatch",
            "beverage_type_conflict",
            "The readable class or type conflicts with the selected beverage profile",
            reference=reference.beverage_type,
            observed=", ".join(sorted(hits)),
        )
    return _result(
        "beverage_type",
        "Beverage type",
        "Review",
        "beverage_type_uncertain",
        "The label does not provide one unambiguous beverage-type signal",
        reference=reference.beverage_type,
    )
def _class_type(reference: ReferenceRecord, observed: ObservedCandidates) -> CheckResult:
    result = compare_class(reference.class_type, observed.field("class_type"))
    if reference.beverage_type != "wine" or result.state != "Match":
        return result
    brand = observed.field("brand")
    class_type = observed.field("class_type")
    if brand.status != "Found" or class_type.status != "Found":
        return result
    if brand.candidates[0].evidence.panel_id != class_type.candidates[0].evidence.panel_id:
        result.state = "Review"
        result.reason_code = "wine_brand_label_placement_review"
        result.reason_text = (
            "Wine brand and class or type were found on different submitted panels; "
            "confirm the brand-label placement"
        )
    return result


def _alcohol_content(reference: ReferenceRecord, observed: ObservedCandidates) -> CheckResult:
    candidates = observed.field("abv")
    if reference.abv_percent is not None:
        result = compare_abv(reference.abv_percent, candidates)
        snippets = [
            item.evidence.text_snippet or item.value for item in candidates.candidates
        ]
        statement = " ".join(snippets)
        if re.search(r"\bABV\b", statement, re.I) and re.search(r"\d", statement):
            result.state = "Mismatch"
            result.reason_code = "abv_abbreviation_not_authorized"
            result.reason_text = (
                "The alcohol statement uses the unauthorized abbreviation ABV"
            )
            return result
        range_values = _alcohol_range(statement)
        if range_values is not None:
            low, high = range_values
            if reference.beverage_type != "wine":
                result.state = "Mismatch"
                result.reason_code = "alcohol_range_not_authorized"
                result.reason_text = "This beverage profile does not authorize an alcohol range"
                return result
            if reference.reference_provenance == "label_ocr":
                allowed_span = Decimal("3") if high <= Decimal("14") else Decimal("2")
                if high - low > allowed_span or low <= Decimal("14") < high:
                    result.state = "Mismatch"
                    result.reason_code = "wine_alcohol_range_invalid"
                    result.reason_text = (
                        "The visible wine alcohol range exceeds the permitted span or crosses "
                        "the 14 percent class boundary"
                    )
                else:
                    result.state = "Review"
                    result.reason_code = "wine_alcohol_range_requires_actual_value"
                    result.reason_text = (
                        "The range format is readable, but a trusted actual alcohol value is "
                        "required to confirm that the product falls within it"
                    )
                return result
            allowed_span = Decimal("3") if reference.abv_percent <= Decimal("14") else Decimal("2")
            if (
                low > reference.abv_percent
                or high < reference.abv_percent
                or high - low > allowed_span
                or low <= Decimal("14") < high
            ):
                result.state = "Mismatch"
                result.reason_code = "wine_alcohol_range_invalid"
                result.reason_text = (
                    "The wine alcohol range does not contain the reference value within the "
                    "allowed span and 14 percent class boundary"
                )
            else:
                result.state = "Match"
                result.reason_code = "wine_alcohol_range_supported"
                result.reason_text = (
                    "The wine alcohol range contains the reference value and stays within the "
                    "selected span and class boundary"
                )
            return result
        if reference.beverage_type == "malt_beverage" and candidates.status == "Found":
            match = re.search(r"(\d{1,3})(?:\.(\d+))?\s*%", candidates.candidates[0].value)
            if match:
                decimal_places = len(match.group(2) or "")
                allowed_places = 2 if reference.abv_percent < Decimal("0.5") else 1
                if decimal_places > allowed_places:
                    result.state = "Mismatch"
                    result.reason_code = "malt_alcohol_precision_invalid"
                    result.reason_text = (
                        "Malt-beverage alcohol content uses more decimal places than allowed"
                    )
        return result
    if reference.beverage_type == "malt_beverage":
        if reference.malt_alcohol_source == "none" and candidates.status == "Not found":
            return _result(
                "abv",
                "Alcohol content",
                "Not verified",
                "not_applicable_malt_optional",
                "A federal alcohol statement is optional for this confirmed "
                "malt-beverage formula basis",
                applicable=False,
            )
        if reference.malt_alcohol_source == "unknown" and candidates.status == "Not found":
            return _result(
                "abv",
                "Alcohol content",
                "Review",
                "malt_abv_trigger_unknown",
                "Formula information is needed to determine whether a malt-beverage "
                "alcohol statement is required",
            )
    if reference.beverage_type == "wine" and re.search(
        r"\b(?:table|light)\s+wine\b", reference.class_type, re.I
    ):
        return _result(
            "abv",
            "Alcohol content",
            "Not verified",
            "wine_table_light_exception",
            "Numeric alcohol content can be omitted for qualifying table or light wine "
            "from 7 through 14 percent",
            applicable=False,
        )
    return _result(
        "abv",
        "Alcohol content",
        "Not verified",
        "reference_abv_unavailable",
        "A trusted alcohol value is needed to decide this rule",
    )


def _alcohol_range(value: str) -> tuple[Decimal, Decimal] | None:
    match = re.search(
        r"(?<!\d)(\d{1,3}(?:\.\d+)?)\s*%?\s*(?:to|[-])\s*"
        r"(\d{1,3}(?:\.\d+)?)\s*%",
        value,
        re.I,
    )
    if not match:
        return None
    low = Decimal(match.group(1))
    high = Decimal(match.group(2))
    return (low, high) if low <= high else (high, low)


def _proof(reference: ReferenceRecord, observed: ObservedCandidates) -> CheckResult:
    if reference.beverage_type != "distilled_spirits":
        return _result(
            "proof",
            "Proof",
            "Not verified",
            "not_applicable_beverage_type",
            "Proof comparison is not part of the selected wine or malt-beverage profile",
            applicable=False,
        )
    if reference.abv_percent is None:
        return _result(
            "proof",
            "Proof",
            "Not verified",
            "proof_requires_actual_abv",
            "A trusted alcohol value is needed before proof can be compared",
        )
    proof_candidates = observed.field("proof")
    result = compare_proof(reference.proof, reference.abv_percent, proof_candidates)
    abv_candidates = observed.field("abv")
    if proof_candidates.status != "Found" or abv_candidates.status != "Found":
        return result
    proof_evidence = proof_candidates.candidates[0].evidence
    abv_evidence = abv_candidates.candidates[0].evidence
    if proof_evidence.panel_id != abv_evidence.panel_id:
        result.state = "Mismatch"
        result.reason_code = "proof_field_of_vision_split"
        result.reason_text = "Proof must appear in the same field of vision as alcohol by volume"
        return result
    source = proof_evidence.text_snippet or ""
    same_line = (
        proof_evidence.polygon_original_pixels == abv_evidence.polygon_original_pixels
        and bool(re.search(r"%", source))
        and bool(re.search(r"\bproof\b", source, re.I))
    )
    if same_line and not re.search(r"[([]\s*\d{1,3}(?:\.\d+)?\s*proof\s*[)\]]", source, re.I):
        result.state = "Review"
        result.reason_code = "proof_distinction_requires_review"
        result.reason_text = (
            "Proof and alcohol by volume share one line without a reliably detected "
            "distinguishing enclosure"
        )
    elif result.state == "Match":
        result.reason_code = "proof_abv_relationship_and_placement_match"
        result.reason_text = (
            "Proof matches twice alcohol by volume and its field-of-vision placement is supported"
        )
    return result


def _net_contents(reference: ReferenceRecord, observed: ObservedCandidates) -> CheckResult:
    result = compare_net_contents(
        reference.net_contents_value,
        reference.net_contents_unit,
        observed.field("net_contents"),
    )
    if reference.beverage_type == "malt_beverage":
        values = [item.value for item in observed.field("net_contents").candidates]
        customary = any(
            re.search(
                r"\b(?:fl\.?\s*[o0]z\.?|fluid\s+ounces?|pints?|pts?\.?|quarts?|qts?\.?|gallons?|gals?\.?)\b",
                value,
                re.I,
            )
            for value in values
        )
        if values and not customary:
            result.state = "Mismatch"
            result.reason_code = "malt_customary_net_contents_missing"
            result.reason_text = (
                "Malt beverage net contents require a U.S. customary volume statement; "
                "metric may be additional"
            )
    return result


def _wine_appellation(reference: ReferenceRecord, observed: ObservedCandidates) -> CheckResult:
    if reference.beverage_type != "wine":
        return _result(
            "wine_appellation",
            "Wine appellation",
            "Not verified",
            "not_applicable_beverage_type",
            "Wine appellation rules do not apply to this beverage profile",
            applicable=False,
        )
    trigger = bool(
        re.search(
            r"\b(?:merlot|cabernet|chardonnay|pinot|riesling|ros[eé]|sauvignon|zinfandel|syrah|shiraz|muscat|vintage|estate\s+bottled)\b",
            reference.class_type,
            re.I,
        )
    )
    if not trigger:
        return _result(
            "wine_appellation",
            "Wine appellation",
            "Not verified",
            "wine_appellation_trigger_not_found",
            "No selected varietal, vintage, or estate-bottled trigger was found",
            applicable=False,
        )
    if reference.wine_appellation:
        return compare_text(
            "wine_appellation",
            "Wine appellation",
            reference.wine_appellation,
            observed.field("wine_appellation"),
        )
    return _result(
        "wine_appellation",
        "Wine appellation",
        "Not verified",
        "wine_appellation_not_found",
        "This wine designation can require an appellation, but no reliable appellation "
        "was supplied or read",
    )


def _wine_sulfites(reference: ReferenceRecord, observed: ObservedCandidates) -> CheckResult:
    if reference.beverage_type != "wine":
        return _result(
            "wine_sulfites",
            "Wine sulfite declaration",
            "Not verified",
            "not_applicable_beverage_type",
            "Wine sulfite rules do not apply to this beverage profile",
            applicable=False,
        )
    found = observed.field("wine_sulfites")
    if reference.wine_sulfite_status == "present":
        if found.status == "Found":
            candidate = found.candidates[0]
            return _result(
                "wine_sulfites",
                "Wine sulfite declaration",
                "Match",
                "sulfite_declaration_found",
                "A readable sulfite declaration was found",
                observed=candidate.value,
                candidate=candidate,
            )
        return _result(
            "wine_sulfites",
            "Wine sulfite declaration",
            "Not verified",
            "sulfite_declaration_not_found",
            "The expected sulfite declaration was not found in readable evidence",
        )
    if reference.wine_sulfite_status == "not_present":
        return _result(
            "wine_sulfites",
            "Wine sulfite declaration",
            "Not verified",
            "sulfite_threshold_not_triggered",
            "Trusted chemistry indicates the declaration threshold is not triggered",
            applicable=False,
        )
    return _result(
        "wine_sulfites",
        "Wine sulfite declaration",
        "Not verified",
        "sulfite_chemistry_unknown",
        "A label image cannot establish whether total sulfur dioxide reaches the "
        "declaration threshold",
    )


def _spirits_field_of_vision(
    reference: ReferenceRecord, observed: ObservedCandidates
) -> CheckResult:
    if reference.beverage_type != "distilled_spirits":
        return _result(
            "spirits_field_of_vision",
            "Spirits field of vision",
            "Not verified",
            "not_applicable_beverage_type",
            "The distilled-spirits field-of-vision rule does not apply",
            applicable=False,
        )
    fields = [observed.field(name) for name in ("brand", "class_type", "abv")]
    if any(item.status != "Found" for item in fields):
        return _result(
            "spirits_field_of_vision",
            "Spirits field of vision",
            "Not verified",
            "field_of_vision_evidence_incomplete",
            "Brand, class or type, and alcohol content were not each found unambiguously",
        )
    panels = {item.candidates[0].evidence.panel_id for item in fields}
    if len(panels) == 1:
        return _result(
            "spirits_field_of_vision",
            "Spirits field of vision",
            "Match",
            "field_of_vision_supported",
            "Brand, class or type, and alcohol content were found on the same submitted panel",
        )
    return _result(
        "spirits_field_of_vision",
        "Spirits field of vision",
        "Mismatch",
        "field_of_vision_split",
        "Brand, class or type, and alcohol content were found on different submitted panels",
    )


def _malt_class_designation(reference: ReferenceRecord) -> CheckResult:
    if reference.beverage_type != "malt_beverage":
        return _result(
            "malt_class_designation",
            "Malt beverage class designation",
            "Not verified",
            "not_applicable_beverage_type",
            "Malt-beverage class rules do not apply",
            applicable=False,
        )
    normalized = reference.class_type.strip().casefold()
    if normalized == "ipa":
        return _result(
            "malt_class_designation",
            "Malt beverage class designation",
            "Mismatch",
            "ipa_alone_not_recognized",
            "IPA alone is not a recognized class or type; add ale, beer, or India Pale Ale",
            reference=reference.class_type,
        )
    if re.search(
        r"\b(?:malt\s+beverage|beer|ale|lager|stout|porter|pilsner|india\s+pale\s+ale|near\s+beer|cereal\s+beverage)\b",
        normalized,
    ):
        return _result(
            "malt_class_designation",
            "Malt beverage class designation",
            "Match",
            "recognized_malt_class",
            "A recognized malt-beverage class designation was found",
            reference=reference.class_type,
        )
    return _result(
        "malt_class_designation",
        "Malt beverage class designation",
        "Review",
        "malt_specialty_designation_review",
        "A specialty product may require a fanciful name and statement of composition",
        reference=reference.class_type,
    )


def _warning_abv(reference: ReferenceRecord) -> Decimal | None:
    if reference.abv_percent is not None:
        return reference.abv_percent
    return None


def _panel_coverage(observed: ObservedCandidates) -> CheckResult:
    panels = observed.panels
    if _appears_front_only(observed):
        return _result(
            "panel_coverage",
            "Panel coverage",
            "Not verified",
            "panel_coverage_uncertain",
            "The submitted panel appears to omit supplemental label elements",
        )
    if panels and all(item.coverage_state == "Sufficient" for item in panels):
        return _result(
            "panel_coverage",
            "Panel coverage",
            "Match",
            "panel_coverage_sufficient",
            "The submitted panels provide sufficient label coverage",
        )
    if panels:
        return _result(
            "panel_coverage",
            "Panel coverage",
            "Review",
            "panel_coverage_uncertain",
            "One or more panels may not provide complete label coverage",
        )
    return _result(
        "panel_coverage",
        "Panel coverage",
        "Not verified",
        "panel_coverage_absent",
        "No panel coverage evidence is available",
    )


def _image_quality(observed: ObservedCandidates) -> CheckResult:
    panels = observed.panels
    if not panels or any(item.coverage_state == "Unreadable" for item in panels):
        return _result(
            "image_quality",
            "Image quality",
            "Not verified",
            "image_unreadable",
            "One or more panels are unreadable and require replacement",
        )
    if any(item.coverage_state == "Review" for item in panels):
        return _result(
            "image_quality",
            "Image quality",
            "Review",
            "image_quality_uncertain",
            "One or more image-quality signals require review",
        )
    return _result(
        "image_quality",
        "Image quality",
        "Match",
        "image_quality_sufficient",
        "The image-quality signals support automated review",
    )


def _appears_front_only(observed: ObservedCandidates) -> bool:
    if len(observed.panels) != 1 or observed.panels[0].coverage_state != "Sufficient":
        return False
    core_fields = ("brand", "class_type", "abv", "proof", "net_contents")
    core_found = sum(
        observed.field(field).status in {"Found", "Ambiguous"} for field in core_fields
    )
    supplemental_found = any(
        observed.field(field).status in {"Found", "Ambiguous"} for field in ("producer", "country")
    ) or bool(observed.warning.full_text)
    return core_found >= 4 and not supplemental_found


def _guard_degraded_evidence(
    checks: list[CheckResult], observed: ObservedCandidates
) -> list[CheckResult]:
    evidence_panels = {item.evidence_id: item.panel_id for item in observed.evidence}
    panel_quality = {item.panel_id: item.coverage_state for item in observed.panels}
    guarded: list[CheckResult] = []
    for check in checks:
        if check.state != "Mismatch" or check.evidence_ref is None:
            guarded.append(check)
            continue
        quality = panel_quality.get(evidence_panels.get(check.evidence_ref, ""))
        if quality == "Unreadable":
            guarded.append(
                check.model_copy(
                    update={
                        "state": "Not verified",
                        "reason_code": "observed_unreadable",
                        "reason_text": (
                            "The supporting image is not readable enough to verify this field"
                        ),
                    }
                )
            )
        elif quality == "Review":
            guarded.append(
                check.model_copy(
                    update={
                        "state": "Review",
                        "reason_code": "quality_degraded_observation",
                        "reason_text": (
                            "The apparent difference comes from an image that requires review"
                        ),
                    }
                )
            )
        else:
            guarded.append(check)
    return guarded
