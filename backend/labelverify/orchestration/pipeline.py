from __future__ import annotations

import re
import time
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import (
    AnalysisDraft,
    AnalysisResult,
    BeverageType,
    Candidate,
    CandidateSet,
    CheckResult,
    DetectedValue,
    Evidence,
    PanelResult,
    ReferenceRecord,
    StageTimings,
    VerificationResult,
    VolumeUnit,
)
from labelverify.domain.engine import ComparisonInputs, compare_all, mark_unresolved_beverage
from labelverify.domain.normalize import parse_abv, parse_proof
from labelverify.domain.presentation import (
    bad_image,
    beverage_inference,
    present_checks,
    present_panels,
    present_wording,
    warning_evidence,
)
from labelverify.domain.types import ObservedCandidates
from labelverify.extraction.candidates import locate_candidates
from labelverify.extraction.port import ExtractionPort
from labelverify.imaging.decode import ImageLimitError, InvalidImageError, decode_panel
from labelverify.imaging.transforms import create_ocr_views


class PipelineFailure(RuntimeError):
    def __init__(self, code: str, field_or_panel: str | None = None) -> None:
        super().__init__(code)
        self.code = code
        self.field_or_panel = field_or_panel


@dataclass(frozen=True)
class PipelineJob:
    request_id: str
    build_id: str
    reference: ReferenceRecord
    panel_paths: tuple[Path, ...]


@dataclass(frozen=True)
class AnalysisJob:
    request_id: str
    build_id: str
    panel_paths: tuple[Path, ...]


def execute_pipeline(job: PipelineJob, adapter: ExtractionPort) -> VerificationResult:
    started = time.perf_counter()
    stage_started = started
    limits = contracts().api["limits"]
    decoded = []
    cumulative_pixels = 0
    for index, path in enumerate(job.panel_paths, start=1):
        panel_id = f"panel-{index}"
        remaining_pixels = int(limits["pixelsPerRequest"]) - cumulative_pixels
        if remaining_pixels <= 0:
            raise PipelineFailure("decoded_pixel_limit", panel_id)
        panel_pixel_limit = min(int(limits["pixelsPerImage"]), remaining_pixels)
        try:
            panel = decode_panel(path, panel_id, panel_pixel_limit)
        except ImageLimitError as exc:
            raise PipelineFailure("decoded_pixel_limit", panel_id) from exc
        except InvalidImageError as exc:
            raise PipelineFailure("invalid_image", panel_id) from exc
        cumulative_pixels += panel.pixels
        decoded.append(panel)
    decode_ms = _elapsed_ms(stage_started)

    stage_started = time.perf_counter()
    views = [view for panel in decoded for view in create_ocr_views(panel)]
    preprocess_ms = _elapsed_ms(stage_started)

    stage_started = time.perf_counter()
    try:
        lines = adapter.extract(views)
    except Exception as exc:
        raise PipelineFailure("inference_failed") from exc
    ocr_ms = _elapsed_ms(stage_started)

    stage_started = time.perf_counter()
    public_panels = [panel.public_panel() for panel in decoded]
    observed = locate_candidates(lines, public_panels)
    candidates_ms = _elapsed_ms(stage_started)

    stage_started = time.perf_counter()
    checks, summary = compare_all(ComparisonInputs(reference=job.reference, observed=observed))
    compare_ms = _elapsed_ms(stage_started)

    stage_started = time.perf_counter()
    validate_result_integrity(public_panels, observed.evidence, checks)
    checks = present_wording(present_checks(checks, job.reference.beverage_type), observed)
    public_panels = present_panels(public_panels)
    aggregate_ms = _elapsed_ms(stage_started)
    rules = contracts().rules
    return VerificationResult(
        requestId=job.request_id,
        buildId=job.build_id,
        profileId=job.reference.profile_id,
        profileVersion=contracts().checks["registryVersion"],
        modelIdentity=adapter.model_identity,
        ruleSources=list(rules["citations"]),
        serverDurationMs=_elapsed_ms(started),
        stageTimings=StageTimings(
            decodeMs=decode_ms,
            preprocessMs=preprocess_ms,
            ocrMs=ocr_ms,
            candidatesMs=candidates_ms,
            compareMs=compare_ms,
            aggregateMs=aggregate_ms,
        ),
        panels=public_panels,
        evidence=observed.evidence,
        checks=checks,
        limitations=[
            "Machine findings support human review and are not legal approval",
            "Physical warning type size is not verified without reliable scale",
            "Formula, chemistry, permit, state-law, and origin truth require independent records",
            "Label-derived values do not establish agreement with an independent COLA application",
        ],
        summary=summary,
        warningEvidence=warning_evidence(observed),
        badImage=bad_image(public_panels),
    )


def execute_analysis(job: AnalysisJob, adapter: ExtractionPort) -> AnalysisResult:
    started = time.perf_counter()
    stage_started = started
    limits = contracts().api["limits"]
    decoded = []
    cumulative_pixels = 0
    for index, path in enumerate(job.panel_paths, start=1):
        panel_id = f"panel-{index}"
        remaining_pixels = int(limits["pixelsPerRequest"]) - cumulative_pixels
        if remaining_pixels <= 0:
            raise PipelineFailure("decoded_pixel_limit", panel_id)
        panel_pixel_limit = min(int(limits["pixelsPerImage"]), remaining_pixels)
        try:
            panel = decode_panel(path, panel_id, panel_pixel_limit)
        except ImageLimitError as exc:
            raise PipelineFailure("decoded_pixel_limit", panel_id) from exc
        except InvalidImageError as exc:
            raise PipelineFailure("invalid_image", panel_id) from exc
        cumulative_pixels += panel.pixels
        decoded.append(panel)
    decode_ms = _elapsed_ms(stage_started)
    stage_started = time.perf_counter()
    views = [view for panel in decoded for view in create_ocr_views(panel)]
    preprocess_ms = _elapsed_ms(stage_started)
    stage_started = time.perf_counter()
    try:
        lines = adapter.extract(views)
    except Exception as exc:
        raise PipelineFailure("inference_failed") from exc
    ocr_ms = _elapsed_ms(stage_started)
    stage_started = time.perf_counter()
    public_panels = [panel.public_panel() for panel in decoded]
    observed = locate_candidates(lines, public_panels)
    candidates_ms = _elapsed_ms(stage_started)
    beverage_type, confidence, reason, conflicting = _infer_beverage_type(observed)
    inference = beverage_inference(beverage_type, confidence, reason, conflicting=conflicting)
    detected = {
        name: _detected_value(observed.field(name))
        for name in (
            "brand",
            "class_type",
            "abv",
            "proof",
            "net_contents",
            "producer",
            "country",
            "wine_appellation",
            "wine_sulfites",
        )
    }
    net_value, net_unit = _net_components(_selected_text(observed.field("net_contents")))
    draft = AnalysisDraft(
        beverageType=beverage_type,
        brandName=_selected_text(observed.field("brand")),
        classType=_selected_text(observed.field("class_type")),
        abvPercent=_decimal_float(parse_abv(_selected_text(observed.field("abv")) or "")),
        proof=_decimal_float(parse_proof(_selected_text(observed.field("proof")) or "")),
        netContentsValue=net_value,
        netContentsUnit=net_unit,
        producerNameAddress=_selected_text(observed.field("producer")),
        isImported=observed.field("country").status in {"Found", "Ambiguous"},
        countryOfOrigin=_selected_text(observed.field("country")),
        wineAppellation=_selected_text(observed.field("wine_appellation")),
        wineSulfiteStatus=(
            "present"
            if observed.field("wine_sulfites").status in {"Found", "Ambiguous"}
            else "unknown"
        ),
        maltAlcoholSource="unknown",
    )
    reference = ReferenceRecord(
        profileId="all_beverages_demo_v2",
        beverageType=beverage_type or "malt_beverage",
        referenceProvenance="label_ocr",
        brandName=draft.brand_name or "Brand not detected",
        classType=draft.class_type or "Class or type not detected",
        abvPercent=(Decimal(str(draft.abv_percent)) if draft.abv_percent is not None else None),
        proof=Decimal(str(draft.proof)) if draft.proof is not None else None,
        netContentsValue=Decimal(str(draft.net_contents_value or 1)),
        netContentsUnit=draft.net_contents_unit or "mL",
        producerNameAddress=draft.producer_name_address or "Producer not detected",
        isImported=draft.is_imported,
        countryOfOrigin=draft.country_of_origin,
        wineAppellation=draft.wine_appellation,
        wineSulfiteStatus=draft.wine_sulfite_status,
        maltAlcoholSource=draft.malt_alcohol_source,
    )
    compare_started = time.perf_counter()
    checks, summary = compare_all(ComparisonInputs(reference=reference, observed=observed))
    if beverage_type is None:
        checks, summary = mark_unresolved_beverage(checks)
    compare_ms = _elapsed_ms(compare_started)
    verify_started = time.perf_counter()
    validate_result_integrity(public_panels, observed.evidence, checks)
    checks = present_wording(present_checks(checks, beverage_type), observed)
    public_panels = present_panels(public_panels)
    aggregate_ms = _elapsed_ms(verify_started)
    rules = contracts().rules
    verification = VerificationResult(
        requestId=job.request_id,
        buildId=job.build_id,
        profileId="all_beverages_demo_v2",
        profileVersion=contracts().checks["registryVersion"],
        modelIdentity=adapter.model_identity,
        ruleSources=list(rules["citations"]),
        serverDurationMs=_elapsed_ms(started),
        stageTimings=StageTimings(
            decodeMs=decode_ms,
            preprocessMs=preprocess_ms,
            ocrMs=ocr_ms,
            candidatesMs=candidates_ms,
            compareMs=compare_ms,
            aggregateMs=aggregate_ms,
        ),
        panels=public_panels,
        evidence=observed.evidence,
        checks=checks,
        limitations=[
            "Machine findings support human review and are not legal approval",
            "Physical warning type size is not verified without reliable scale",
            "Formula, chemistry, permit, state-law, and origin truth require independent records",
            "Label-derived values do not establish agreement with an independent COLA application",
        ],
        summary=summary,
        beverageInference=inference,
        warningEvidence=warning_evidence(observed),
        badImage=bad_image(public_panels),
    )
    validate_result_integrity(public_panels, observed.evidence, [])
    return AnalysisResult(
        requestId=job.request_id,
        buildId=job.build_id,
        profileId="all_beverages_demo_v2",
        modelIdentity=adapter.model_identity,
        serverDurationMs=_elapsed_ms(started),
        panels=public_panels,
        evidence=observed.evidence,
        draft=draft,
        detected=detected,
        beverageTypeConfidence=confidence,
        beverageTypeReason=reason,
        beverageInference=inference,
        limitations=[
            "Detected values came from label images and are not independent application data",
            "Review the beverage type and any uncertain field before recording a disposition",
            "Formula, chemistry, permit, state-law, and physical-scale facts need other evidence",
        ],
        verification=verification,
    )


def _detected_value(candidates: CandidateSet) -> DetectedValue:
    selected = _selected_candidate(candidates)
    return DetectedValue(
        value=selected.value if selected else None,
        status=candidates.status,
        evidenceRef=selected.evidence.evidence_id if selected else None,
        alternatives=[item.value for item in candidates.candidates],
        confidenceSignal=(selected.evidence.confidence_provenance.signal if selected else None),
    )


def _selected_candidate(candidates: CandidateSet) -> Candidate | None:
    if not candidates.candidates:
        return None
    return max(
        candidates.candidates,
        key=lambda item: item.evidence.confidence_provenance.signal or 0.0,
    )


def _selected_text(candidates: CandidateSet) -> str | None:
    selected = _selected_candidate(candidates)
    return selected.value if selected else None


def _infer_beverage_type(
    observed: ObservedCandidates,
) -> tuple[BeverageType | None, float | None, str, bool]:
    values = " ".join(item.value.casefold() for item in observed.field("class_type").candidates)
    groups: dict[BeverageType, tuple[str, ...]] = {
        "distilled_spirits": (
            "bourbon",
            "whiskey",
            "whisky",
            "vodka",
            "gin",
            "rum",
            "tequila",
            "brandy",
            "liqueur",
            "cordial",
            "distilled spirits",
        ),
        "wine": (
            "wine",
            "merlot",
            "cabernet",
            "chardonnay",
            "pinot",
            "riesling",
            "rose",
            "rosé",
            "sauvignon",
            "zinfandel",
            "syrah",
            "shiraz",
            "muscat",
            "sangria",
            "vermouth",
            "champagne",
        ),
        "malt_beverage": (
            "malt beverage",
            "beer",
            "ale",
            "lager",
            "stout",
            "porter",
            "pilsner",
            "ipa",
        ),
    }
    scores = {
        name: sum(
            bool(re.search(rf"(?<!\w){re.escape(term)}(?!\w)", values, re.I)) for term in terms
        )
        for name, terms in groups.items()
    }
    matched_families = [name for name, score in scores.items() if score > 0]
    if len(matched_families) != 1:
        return (
            None,
            None,
            "The label did not provide one unambiguous beverage-type signal",
            len(matched_families) > 1,
        )
    winner = matched_families[0]
    best = scores[winner]
    confidence = min(0.98, 0.72 + 0.08 * best)
    return winner, confidence, f"Detected class or type terms support {winner}", False


_NET_COMPONENTS = re.compile(
    r"(?<!\d)(\d+(?:\.\d+)?)\s*(fl\.?\s*oz\.?|fluid\s+ounces?|pints?|pts?\.?|"
    r"quarts?|qts?\.?|gallons?|gals?\.?|ml|m[lL]|lit(?:er|re)s?|[lL])\b",
    re.I,
)


def _net_components(value: str | None) -> tuple[float | None, VolumeUnit | None]:
    if not value:
        return None, None
    match = _NET_COMPONENTS.search(value)
    if not match:
        return None, None
    unit = re.sub(r"[.\s]", "", match.group(2).casefold())
    if unit in {"l", "liter", "litre", "liters", "litres"}:
        canonical: VolumeUnit = "L"
    elif unit in {"floz", "fluidounce", "fluidounces"}:
        canonical = "fl oz"
    elif unit in {"pint", "pints", "pt", "pts"}:
        canonical = "pt"
    elif unit in {"quart", "quarts", "qt", "qts"}:
        canonical = "qt"
    elif unit in {"gallon", "gallons", "gal", "gals"}:
        canonical = "gal"
    else:
        canonical = "mL"
    return float(match.group(1)), canonical


def _decimal_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def validate_result_integrity(
    panels: list[PanelResult], evidence: list[Evidence], checks: list[CheckResult]
) -> None:
    panel_map = {panel.panel_id: panel for panel in panels}
    if len(panel_map) != len(panels):
        raise PipelineFailure("internal_error")
    evidence_map = {item.evidence_id: item for item in evidence}
    if len(evidence_map) != len(evidence):
        raise PipelineFailure("internal_error")
    for item in evidence:
        panel = panel_map.get(item.panel_id)
        if panel is None or not _valid_polygon(
            item,
            int(panel.original_dimensions.width),
            int(panel.original_dimensions.height),
        ):
            raise PipelineFailure("internal_error")
    for check in checks:
        if check.evidence_ref is not None and check.evidence_ref not in evidence_map:
            raise PipelineFailure("internal_error")
        alternative_refs = [item.evidence_ref for item in check.alternatives]
        if len(alternative_refs) != len(set(alternative_refs)):
            raise PipelineFailure("internal_error")
        for alternative in check.alternatives:
            if alternative.evidence_ref not in evidence_map:
                raise PipelineFailure("internal_error")
        if len(alternative_refs) > 1:
            regions = {
                (
                    evidence_map[ref].panel_id,
                    tuple(
                        (point.x, point.y) for point in evidence_map[ref].polygon_original_pixels
                    ),
                )
                for ref in alternative_refs
            }
            if len(regions) != len(alternative_refs):
                raise PipelineFailure("internal_error")


def _valid_polygon(evidence: Evidence, width: int, height: int) -> bool:
    points = evidence.polygon_original_pixels
    if len(points) != 4:
        return False
    if any(point.x < 0 or point.x >= width or point.y < 0 or point.y >= height for point in points):
        return False
    if (points[0].y, points[0].x) != min((point.y, point.x) for point in points):
        return False
    signed_area = sum(
        points[index].x * points[(index + 1) % 4].y - points[(index + 1) % 4].x * points[index].y
        for index in range(4)
    )
    return signed_area > 0


def _elapsed_ms(started: float) -> float:
    return round((time.perf_counter() - started) * 1000, 3)
