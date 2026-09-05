from __future__ import annotations

import re
import time
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from labelverify.contracts.models import (
    BeverageInference,
    BeverageType,
    BeverageTypeCorrection,
    Candidate,
    CandidateSet,
    ConfidenceProvenance,
    CorrectionItem,
    Evidence,
    ProducerCorrection,
    ReferenceRecord,
    StageTimings,
    TextCorrection,
    VerificationResult,
)
from labelverify.domain.aggregation import aggregate, review_causes
from labelverify.domain.beverage import infer_beverage_type
from labelverify.domain.engine import ComparisonInputs, compare_all, mark_unresolved_beverage
from labelverify.domain.normalize import is_domestic_origin, parse_abv, parse_proof
from labelverify.domain.presentation import (
    apply_observation_provenance,
    bad_image,
    beverage_inference,
    present_checks,
    present_panels,
    present_wording,
    warning_evidence,
)
from labelverify.domain.types import ObservedCandidates, serialize_observed
from labelverify.orchestration.pipeline import valid_polygon, validate_result_integrity

_TEXT_FIELDS = {
    "brand_name": ("brand_name", "brand"),
    "class_type": ("class_type", "class_type"),
    "producer_name_address": ("producer_name_address", "producer"),
    "country_of_origin": ("country_of_origin", "country"),
    "wine_appellation": ("wine_appellation", "wine_appellation"),
}
_VOLUME = re.compile(
    r"(?P<value>\d+(?:[.,]\d+)?)\s*(?P<unit>m\s*l|l|fl\s*\.?\s*oz|pt|qt|gal)\b",
    re.I,
)
_ABV_RANGE = re.compile(
    r"(?<!\d)(?P<low>\d{1,3}(?:[.,]\d+)?)\s*%?\s*(?:to|-)\s*"
    r"(?P<high>\d{1,3}(?:[.,]\d+)?)\s*(?:%|\bpercent\b)",
    re.I,
)


class InvalidCorrection(ValueError):
    pass


def correction_items_for_replay(
    events: list[object], *, panel_hashes: dict[str, str]
) -> list[CorrectionItem]:
    """Collapse an audit log to each field's latest value and retained source region.

    A fresh OCR snapshot produced after adding an image does not contain correction-created
    evidence identifiers. Each event therefore carries its source panel, polygon, and image
    hash; replay uses all four values from the latest event for that field.
    """

    ordered_fields: list[str] = []
    replay: dict[str, dict[str, object]] = {}
    for raw in events:
        if not isinstance(raw, dict):
            raise InvalidCorrection("Stored correction history is malformed")
        field = raw.get("field")
        visible_text = raw.get("visibleText")
        family = raw.get("family")
        source_panel = raw.get("sourcePanelId")
        source_polygon = raw.get("sourcePolygon")
        source_hash = raw.get("sourceImageSha256")
        if not isinstance(field, str) or not field:
            raise InvalidCorrection("Stored correction history is incomplete")
        if field == "beverage_type":
            if not isinstance(family, str) or not family:
                family = visible_text
        elif not isinstance(visible_text, str) or not visible_text:
            raise InvalidCorrection("Stored correction history is incomplete")
        if not isinstance(source_panel, str) or not isinstance(source_polygon, list):
            raise InvalidCorrection("Stored correction history is incomplete")
        if not isinstance(source_hash, str) or panel_hashes.get(source_panel) != source_hash:
            raise InvalidCorrection("Stored correction evidence no longer matches its image")
        if field not in replay:
            ordered_fields.append(field)
        replay[field] = {
            "panelId": source_panel,
            "polygon": source_polygon,
            "visibleText": visible_text,
            "family": family,
        }
    items: list[CorrectionItem] = []
    for field in ordered_fields:
        value = replay[field]
        locator = {"panelId": value["panelId"], "polygon": value["polygon"]}
        if field == "beverage_type":
            items.append(
                BeverageTypeCorrection.model_validate(
                    {"field": "beverage_type", "family": value["family"], **locator}
                )
            )
        elif field == "producer_name_address":
            items.append(
                ProducerCorrection.model_validate(
                    {
                        "field": "producer_name_address",
                        "visibleText": value["visibleText"],
                        **locator,
                    }
                )
            )
        else:
            items.append(
                TextCorrection.model_validate(
                    {
                        "field": field,
                        "visibleText": value["visibleText"],
                        **locator,
                    }
                )
            )
    return items


def apply_corrections(
    reference: ReferenceRecord,
    observed: ObservedCandidates,
    corrections: list[CorrectionItem],
    *,
    panel_hashes: dict[str, str],
) -> tuple[ReferenceRecord, ObservedCandidates, list[dict[str, object]]]:
    """Overlay reviewer reads on a faithful observation snapshot without running OCR."""

    evidence_by_id = {item.evidence_id: item for item in observed.evidence}
    reference_values = reference.model_dump()
    provenance = dict(reference.field_provenance)
    fields = dict(observed.fields)
    evidence = list(observed.evidence)
    events: list[dict[str, object]] = []

    for item in corrections:
        source = evidence_by_id.get(item.evidence_ref or "")
        if item.evidence_ref is not None and source is None:
            raise InvalidCorrection(f"Unknown evidence reference for {item.field}")
        if item.evidence_ref is None:
            source = _manual_source(item, observed)
        if source is None:  # pragma: no cover - guarded by the locator contract
            raise InvalidCorrection(f"Correction evidence is incomplete for {item.field}")
        source_hash = panel_hashes.get(source.panel_id)
        if source_hash is None:
            raise InvalidCorrection("Correction evidence has no retained source image")
        visible_text = _visible_text(item)
        raw_visible_text = (
            item.family
            if isinstance(item, BeverageTypeCorrection)
            else item.visible_text.replace("\r\n", "\n").replace("\r", "\n")
        )
        corrected_evidence = Evidence(
            evidenceId=f"ev_corr_{uuid4().hex}",
            panelId=source.panel_id,
            polygonOriginalPixels=source.polygon_original_pixels,
            sourceView=source.source_view,
            transformId=source.transform_id,
            textSnippet=visible_text,
            confidenceProvenance=ConfidenceProvenance(
                source="reviewer_corrected", calibratedProbability=False
            ),
        )
        evidence.append(corrected_evidence)
        candidate = Candidate(value=visible_text, evidence=corrected_evidence)
        updates_reference = reference.source_for(item.field) in {
            "label_ocr",
            "reviewer_corrected",
        }
        if updates_reference:
            provenance[item.field] = "reviewer_corrected"

        if item.field in _TEXT_FIELDS:
            reference_field, observed_field = _TEXT_FIELDS[item.field]
            if updates_reference:
                reference_values[reference_field] = visible_text
            fields[observed_field] = CandidateSet(status="Found", candidates=[candidate])
            if item.field == "country_of_origin" and updates_reference:
                reference_values["is_imported"] = not is_domestic_origin(visible_text)
            derived: dict[str, object] = (
                _producer_components(visible_text)
                if item.field == "producer_name_address"
                else {"text": visible_text}
            )
        elif item.field == "beverage_type":
            family = _beverage_type(visible_text)
            if updates_reference:
                reference_values["beverage_type"] = family
            fields["beverage_type"] = CandidateSet(
                status="Found",
                candidates=[candidate.model_copy(update={"value": family})],
            )
            derived = {"family": family}
        elif item.field == "alcohol_content":
            parsed = parse_abv(visible_text)
            range_match = _ABV_RANGE.search(visible_text)
            if parsed is None and range_match is not None:
                parsed = Decimal(range_match.group("low").replace(",", "."))
            if parsed is None:
                raise InvalidCorrection("Alcohol content must contain a percent value")
            if updates_reference:
                reference_values["abv_percent"] = parsed
            fields["abv"] = CandidateSet(status="Found", candidates=[candidate])
            derived = _abv_details(raw_visible_text, parsed)
        elif item.field == "proof":
            parsed = parse_proof(visible_text)
            if parsed is None:
                raise InvalidCorrection("Proof must contain a numeric proof value")
            if updates_reference:
                reference_values["proof"] = parsed
            fields["proof"] = CandidateSet(status="Found", candidates=[candidate])
            derived = _proof_details(raw_visible_text, parsed)
        elif item.field == "net_contents":
            value, unit = _net_contents(visible_text)
            if updates_reference:
                reference_values["net_contents_value"] = value
                reference_values["net_contents_unit"] = unit
            fields["net_contents"] = CandidateSet(status="Found", candidates=[candidate])
            derived = _net_details(raw_visible_text, value, unit)
        elif item.field == "wine_sulfite_declaration":
            normalized = visible_text.casefold()
            if not re.search(r"\bcontains?\s+sul(?:f|ph)ites?\b", normalized):
                raise InvalidCorrection(
                    "A sulfite correction must transcribe a visible contains-sulfites statement"
                )
            status = "present"
            if updates_reference:
                reference_values["wine_sulfite_status"] = status
            fields["wine_sulfites"] = CandidateSet(status="Found", candidates=[candidate])
            derived = {"status": status, "printedStatement": raw_visible_text}
        else:  # pragma: no cover - the request contract enforces the allowlist
            raise InvalidCorrection(f"Unsupported correction field: {item.field}")
        events.append(
            {
                "field": item.field,
                "rawVisibleText": raw_visible_text,
                "visibleText": visible_text,
                "oldValue": source.text_snippet,
                "originalSnippet": source.text_snippet,
                "correctedValue": visible_text,
                "sourceEvidenceRef": item.evidence_ref,
                "sourcePanelId": source.panel_id,
                "sourcePolygon": [point.model_dump() for point in source.polygon_original_pixels],
                "sourceImageSha256": source_hash,
                "derivedValue": derived,
                "correctedEvidenceRef": corrected_evidence.evidence_id,
                **({"family": visible_text} if item.field == "beverage_type" else {}),
            }
        )

    corrected_fields = {item.field for item in corrections}
    if (
        "class_type" in corrected_fields
        and "beverage_type" not in corrected_fields
        and reference.source_for("beverage_type") != "reviewer_corrected"
    ):
        provisional = ObservedCandidates(
            fields=fields,
            warning=observed.warning,
            panels=observed.panels,
            evidence=evidence,
            lines=observed.lines,
            warning_alternates=observed.warning_alternates,
        )
        inferred, _, _, _ = infer_beverage_type(provisional)
        if inferred is None:
            raise InvalidCorrection(
                "The corrected class leaves beverage type unresolved; confirm beverage type too"
            )
        class_candidate = fields["class_type"].candidates[0]
        fields["beverage_type"] = CandidateSet(
            status="Found",
            candidates=[class_candidate.model_copy(update={"value": inferred})],
        )
        if reference.source_for("beverage_type") == "label_ocr":
            reference_values["beverage_type"] = inferred

    reference_values["field_provenance"] = provenance
    corrected_reference = ReferenceRecord.model_validate(reference_values)
    corrected_observed = ObservedCandidates(
        fields=fields,
        warning=observed.warning,
        panels=observed.panels,
        evidence=evidence,
        lines=observed.lines,
        warning_alternates=observed.warning_alternates,
    )
    return corrected_reference, corrected_observed, events


def _visible_text(item: CorrectionItem) -> str:
    if isinstance(item, BeverageTypeCorrection):
        return item.family
    return "\n".join(line.strip() for line in item.visible_text.splitlines()).strip()


def _decimal_precision(value: str) -> int:
    normalized = value.replace(",", ".")
    return len(normalized.partition(".")[2]) if "." in normalized else 0


def _abv_details(raw: str, parsed: Decimal) -> dict[str, object]:
    percent = re.search(r"(?P<number>\d+(?:[.,]\d+)?)\s*(?P<form>%|\bpercent\b)", raw, re.I)
    abbreviation = re.search(r"\b(?:ABV|ALC(?:OHOL)?\.?\s*(?:BY|/)\s*VOL\.?)(?=\W|$)", raw, re.I)
    range_match = _ABV_RANGE.search(raw)
    number = percent.group("number") if percent else str(parsed)
    return {
        "abvPercent": str(parsed),
        "range": (
            {
                "minimum": range_match.group("low").replace(",", "."),
                "maximum": range_match.group("high").replace(",", "."),
            }
            if range_match
            else None
        ),
        "percentForm": percent.group(0) if percent else None,
        "abbreviation": abbreviation.group(0) if abbreviation else None,
        "decimalPrecision": _decimal_precision(number),
    }


def _proof_details(raw: str, parsed: Decimal) -> dict[str, object]:
    wording = re.search(r"(?P<number>\d+(?:[.,]\d+)?)\s*(?:°\s*)?proof\b", raw, re.I)
    number = wording.group("number") if wording else str(parsed)
    return {
        "proof": str(parsed),
        "proofWording": wording.group(0) if wording else None,
        "decimalPrecision": _decimal_precision(number),
    }


def _net_details(raw: str, value: Decimal, unit: str) -> dict[str, object]:
    printed = _VOLUME.search(raw)
    number = printed.group("value") if printed else str(value)
    return {
        "value": str(value),
        "unit": unit,
        "printedUnit": printed.group("unit") if printed else None,
        "decimalPrecision": _decimal_precision(number),
    }


def _manual_source(item: CorrectionItem, observed: ObservedCandidates) -> Evidence:
    if item.panel_id is None or item.polygon is None:
        raise InvalidCorrection(f"Correction evidence is incomplete for {item.field}")
    panel = next((row for row in observed.panels if row.panel_id == item.panel_id), None)
    if panel is None:
        raise InvalidCorrection(f"Unknown source panel for {item.field}")
    evidence = Evidence(
        evidenceId=f"ev_manual_{uuid4().hex}",
        panelId=item.panel_id,
        polygonOriginalPixels=item.polygon,
        sourceView="original",
        transformId="reviewer_polygon",
        textSnippet=None,
        confidenceProvenance=ConfidenceProvenance(
            source="reviewer_corrected", calibratedProbability=False
        ),
    )
    if not valid_polygon(
        evidence,
        int(panel.original_dimensions.width),
        int(panel.original_dimensions.height),
    ):
        raise InvalidCorrection(f"Correction polygon is invalid for {item.panel_id}")
    return evidence


def recompute_revision(
    previous: VerificationResult,
    reference: ReferenceRecord,
    observed: ObservedCandidates,
    *,
    request_id: str,
    build_id: str,
    revision_kind: Literal["correction", "panel_added"] = "correction",
    prior_beverage_inference: BeverageInference | None = None,
    force_unresolved_type: bool = False,
) -> VerificationResult:
    """Recompute the comparison and aggregate from a correction-only observation overlay."""

    started = time.perf_counter()
    compare_started = time.perf_counter()
    checks, summary = compare_all(ComparisonInputs(reference=reference, observed=observed))
    inference_type: BeverageType | None = reference.beverage_type
    type_was_corrected = reference.source_for("beverage_type") == "reviewer_corrected"
    if force_unresolved_type:
        checks, summary = mark_unresolved_beverage(checks)
        inference_type = None
        type_was_corrected = False
    elif type_was_corrected:
        checks = [
            check.model_copy(
                update={
                    "state": "Match",
                    "reason_code": "reviewer_corrected_label_value",
                    "reason_text": (
                        "The reviewer confirmed the beverage type from retained label evidence"
                    ),
                    "observed_display": inference_type,
                    "reference_display": inference_type,
                }
            )
            if check.check_id == "beverage_type"
            else check
            for check in checks
        ]
        summary = aggregate(checks)
    compare_ms = (time.perf_counter() - compare_started) * 1000

    aggregate_started = time.perf_counter()
    validate_result_integrity(observed.panels, observed.evidence, checks)
    checks = apply_observation_provenance(
        present_wording(
            present_checks(
                checks,
                None if force_unresolved_type else reference.beverage_type,
                reference.reference_provenance,
                reference,
            ),
            observed,
        ),
        observed,
    )
    checks = [
        check.model_copy(
            update={
                "reason_code": "reviewer_corrected_label_value",
                "reason_text": "The reviewer corrected this value from retained label evidence",
                "reason_short": "Reviewer corrected",
            }
        )
        if check.observation_provenance == "reviewer_corrected" and check.state == "Match"
        else check
        for check in checks
    ]
    causes = review_causes(checks, summary)
    panels = present_panels(observed.panels)
    aggregate_ms = (time.perf_counter() - aggregate_started) * 1000
    total_ms = (time.perf_counter() - started) * 1000
    limitations = list(previous.limitations)
    if revision_kind == "correction":
        correction_note = "Reviewer corrections are stored as a new immutable revision"
        if correction_note not in limitations:
            limitations.append(correction_note)
    prior_timings = previous.stage_timings
    upstream_timings = (
        {
            "decodeMs": prior_timings.decode_ms,
            "preprocessMs": prior_timings.preprocess_ms,
            "ocrMs": prior_timings.ocr_ms,
            "candidatesMs": prior_timings.candidates_ms,
        }
        if revision_kind == "panel_added"
        else {"decodeMs": 0, "preprocessMs": 0, "ocrMs": 0, "candidatesMs": 0}
    )
    corrected_inference = (
        infer_beverage_type(observed)
        if revision_kind == "correction" and not force_unresolved_type
        else None
    )
    inference = (
        None
        if force_unresolved_type
        else beverage_inference(
            inference_type,
            1.0,
            "Reviewer-confirmed from retained label evidence",
            conflicting=False,
        )
        if type_was_corrected
        else (
            beverage_inference(
                corrected_inference[0],
                corrected_inference[1],
                corrected_inference[2],
                conflicting=corrected_inference[3],
            )
            if corrected_inference is not None and corrected_inference[0] is not None
            else (
                previous.beverage_inference
                if previous.beverage_inference is not None
                else prior_beverage_inference
            )
        )
    )
    return VerificationResult(
        requestId=request_id,
        buildId=build_id,
        profileId=reference.profile_id,
        profileVersion=previous.profile_version,
        modelIdentity=previous.model_identity,
        ruleSources=previous.rule_sources,
        serverDurationMs=(
            previous.server_duration_ms + total_ms if revision_kind == "panel_added" else total_ms
        ),
        stageTimings=StageTimings(
            **upstream_timings,
            compareMs=compare_ms,
            aggregateMs=aggregate_ms,
        ),
        panels=panels,
        evidence=observed.evidence,
        checks=checks,
        limitations=limitations,
        summary=summary,
        beverageInference=inference,
        warningEvidence=warning_evidence(observed),
        badImage=bad_image(panels),
        blockingCheckIds=[cause.check_id for cause in causes],
        reviewCauses=causes,
        revisionKind=revision_kind,
        observationSnapshot=serialize_observed(observed),
    )


def _beverage_type(value: str) -> str:
    normalized = value.casefold().replace("/", " ")
    if "wine" in normalized:
        return "wine"
    if "beer" in normalized or "malt" in normalized or "ale" in normalized:
        return "malt_beverage"
    if "spirit" in normalized or "liquor" in normalized:
        return "distilled_spirits"
    raise InvalidCorrection("Beverage type must be beer or malt, wine, or distilled spirits")


def _net_contents(value: str) -> tuple[Decimal, str]:
    match = _VOLUME.search(value)
    if match is None:
        raise InvalidCorrection("Net contents must contain a numeric value and supported unit")
    number = Decimal(match.group("value").replace(",", "."))
    raw_unit = re.sub(r"[.\s]", "", match.group("unit")).casefold()
    unit = {"ml": "mL", "l": "L", "floz": "fl oz"}.get(raw_unit, raw_unit)
    return number, unit


def _producer_components(value: str) -> dict[str, object]:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    role = re.search(
        r"\b(?:produced|bottled|distilled|brewed|vinted|cellared|imported|packed)\s+by\b",
        value,
        re.I,
    )
    return {
        "rolePhrase": role.group(0) if role else None,
        "lines": lines,
        "normalizedText": " ".join(value.split()),
    }
