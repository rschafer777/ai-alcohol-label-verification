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
from labelverify.domain.beverage import infer_beverage_type
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
from labelverify.extraction.rapidocr_adapter import deduplicate_ocr_lines
from labelverify.imaging.decode import (
    DecodedPanel,
    ImageLimitError,
    InvalidImageError,
    decode_panel,
)
from labelverify.imaging.transforms import ImageView, create_crop_ocr_view, create_ocr_views


class PipelineFailure(RuntimeError):
    def __init__(
        self,
        code: str,
        field_or_panel: str | None = None,
        *,
        comparisons: list[dict[str, object]] | None = None,
        next_action: str | None = None,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.field_or_panel = field_or_panel
        self.comparisons = comparisons or []
        self.next_action = next_action


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
            raise _decoded_pixel_failure(panel_id, exc) from exc
        except InvalidImageError as exc:
            raise PipelineFailure("invalid_image", panel_id) from exc
        cumulative_pixels += panel.pixels
        decoded.append(panel)
    decode_ms = _elapsed_ms(stage_started)

    public_panels, observed, preprocess_ms, ocr_ms, candidates_ms = _extract_observed(
        decoded, adapter
    )

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
            raise _decoded_pixel_failure(panel_id, exc) from exc
        except InvalidImageError as exc:
            raise PipelineFailure("invalid_image", panel_id) from exc
        cumulative_pixels += panel.pixels
        decoded.append(panel)
    decode_ms = _elapsed_ms(stage_started)
    public_panels, observed, preprocess_ms, ocr_ms, candidates_ms = _extract_observed(
        decoded, adapter
    )
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


def _extract_observed(
    decoded: list[DecodedPanel], adapter: ExtractionPort
) -> tuple[list[PanelResult], ObservedCandidates, float, float, float]:
    preprocess_started = time.perf_counter()
    views = [view for panel in decoded for view in create_ocr_views(panel)]
    preprocess_ms = _elapsed_ms(preprocess_started)
    ocr_started = time.perf_counter()
    try:
        lines = adapter.extract(views)
    except Exception as exc:
        raise PipelineFailure("inference_failed") from exc
    ocr_ms = _elapsed_ms(ocr_started)
    candidates_started = time.perf_counter()
    public_panels = [panel.public_panel() for panel in decoded]
    observed = locate_candidates(lines, public_panels)
    candidates_ms = _elapsed_ms(candidates_started)

    preprocess_started = time.perf_counter()
    recovery_views = _recovery_views(decoded, observed)
    preprocess_ms += _elapsed_ms(preprocess_started)
    if recovery_views:
        ocr_started = time.perf_counter()
        try:
            recovery_lines = adapter.extract(recovery_views)
        except Exception as exc:
            raise PipelineFailure("inference_failed") from exc
        ocr_ms += _elapsed_ms(ocr_started)
        candidates_started = time.perf_counter()
        lines = deduplicate_ocr_lines([*lines, *recovery_lines])
        observed = locate_candidates(lines, public_panels)
        candidates_ms += _elapsed_ms(candidates_started)
    return public_panels, observed, preprocess_ms, ocr_ms, candidates_ms


def _decoded_pixel_failure(panel_id: str, exc: ImageLimitError) -> PipelineFailure:
    return PipelineFailure(
        "decoded_pixel_limit",
        panel_id,
        comparisons=[
            {
                "label": "Image width",
                "expected": f"{exc.suggested_width:,} px or fewer at this aspect ratio",
                "actual": f"{exc.width:,} px",
                "passed": exc.width <= exc.suggested_width,
            },
            {
                "label": "Image height",
                "expected": f"{exc.suggested_height:,} px or fewer at this aspect ratio",
                "actual": f"{exc.height:,} px",
                "passed": exc.height <= exc.suggested_height,
            },
            {
                "label": "Decoded pixels",
                "expected": f"{exc.max_pixels:,} or fewer",
                "actual": f"{exc.pixels:,}",
                "passed": False,
            },
        ],
        next_action=(
            f"Resize this image to {exc.suggested_width:,} x {exc.suggested_height:,} pixels "
            "or smaller while preserving its aspect ratio, keep it at or below 4 MB, and retry."
        ),
    )


def _recovery_views(
    decoded: list[DecodedPanel], observed: ObservedCandidates
) -> list[ImageView]:
    recovery: list[ImageView] = []
    missing_content = any(
        observed.field(field).status in {"Not found", "Unreadable"}
        for field in ("abv", "net_contents")
    )
    missing_brand = _brand_needs_recovery(observed)
    missing_producer = observed.field("producer").status in {"Not found", "Unreadable"}
    missing_warning = observed.warning.heading is None or observed.warning.body is None
    if not (missing_brand or missing_content or missing_producer or missing_warning):
        return recovery

    for panel in decoded:
        panel_views: list[ImageView] = []
        if missing_brand:
            class_anchor = _field_anchor(observed, "class_type", panel.panel_id)
            if class_anchor is not None:
                left, top, right, bottom = class_anchor
                center_x = (left + right) // 2
                if panel.coverage_state == "Sufficient":
                    half_width = max(
                        round((right - left) * 0.85), round(panel.width * 0.16)
                    )
                    crop_top = top - round(panel.height * 0.24)
                else:
                    half_width = max(
                        round((right - left) * 0.85), round(panel.width * 0.10)
                    )
                    crop_top = top - round(panel.height * 0.10)
                panel_views.append(
                    create_crop_ocr_view(
                        panel,
                        (
                            center_x - half_width,
                            crop_top,
                            center_x + half_width,
                            bottom + round(panel.height * 0.04),
                        ),
                        f"transform-{panel.panel_id}-brand-detail-v1",
                        max_side=1800,
                    )
                )
        landscape_rotated_detail = (
            panel.width >= panel.height
            and panel.coverage_state == "Sufficient"
            and (missing_producer or missing_warning)
        )
        if missing_content and not landscape_rotated_detail:
            anchor = _field_anchor(observed, "class_type", panel.panel_id) or _field_anchor(
                observed, "brand", panel.panel_id
            )
            if anchor is not None:
                left, top, right, bottom = anchor
                center_x = (left + right) // 2
                if (
                    panel.width < panel.height
                    and abs(center_x - panel.width / 2) >= panel.width * 0.15
                ):
                    crop_left = 0 if center_x < panel.width / 2 else panel.width // 2
                    crop_right = crop_left + panel.width // 2
                else:
                    half_width = max((right - left) * 2, round(panel.width * 0.25))
                    crop_left = center_x - half_width
                    crop_right = center_x + half_width
                panel_views.append(
                    create_crop_ocr_view(
                        panel,
                        (
                            crop_left,
                            bottom + round(panel.height * 0.026),
                            crop_right,
                            bottom + round(panel.height * 0.111),
                        ),
                        f"transform-{panel.panel_id}-content-detail-v1",
                    )
                )
        if missing_producer:
            content_anchor = _field_anchor(
                observed, "net_contents", panel.panel_id
            ) or _field_anchor(observed, "abv", panel.panel_id)
            if content_anchor is not None:
                left, top, right, bottom = content_anchor
                center_x = (left + right) // 2
                half_width = max((right - left) * 2, round(panel.width * 0.14))
                panel_views.append(
                    create_crop_ocr_view(
                        panel,
                        (
                            center_x - half_width,
                            top - round(panel.height * 0.03),
                            center_x + half_width,
                            bottom + round(panel.height * 0.16),
                        ),
                        f"transform-{panel.panel_id}-producer-detail-v1",
                        max_side=1400,
                    )
                )
        warning_anchor = _warning_anchor(observed, panel.panel_id)
        if missing_producer and warning_anchor is not None:
            left, top, right, bottom = warning_anchor
            center_x = (left + right) // 2
            half_width = max((right - left), round(panel.width * 0.30))
            panel_views.append(
                create_crop_ocr_view(
                    panel,
                    (
                        center_x - half_width,
                        top - round(panel.height * 0.03),
                        center_x + half_width,
                        bottom + round(panel.height * 0.30),
                    ),
                    f"transform-{panel.panel_id}-warning-detail-v1",
                )
            )
        if (
            warning_anchor is None
            and panel.width < panel.height
            and (missing_producer or missing_warning)
        ):
            panel_views.append(
                create_crop_ocr_view(
                    panel,
                    (
                        round(panel.width * 0.12),
                        round(panel.height * 0.48),
                        round(panel.width * 0.88),
                        round(panel.height * 0.92),
                    ),
                    f"transform-{panel.panel_id}-lower-label-detail-v1",
                )
            )
        if panel.width >= panel.height and (missing_producer or missing_warning):
            detail_top = round(panel.height * 0.12)
            detail_bottom = round(panel.height * 0.94)
            right_left = round(panel.width * 0.62)
            right_bounds = (right_left, detail_top, panel.width, detail_bottom)
            if panel.coverage_state == "Sufficient":
                panel_views.append(
                    create_crop_ocr_view(
                        panel,
                        right_bounds,
                        f"transform-{panel.panel_id}-right-detail-rotated-v1",
                        rotate_clockwise=True,
                        max_side=1200,
                    )
                )
            else:
                panel_views.append(
                    create_crop_ocr_view(
                        panel,
                        right_bounds,
                        f"transform-{panel.panel_id}-right-detail-v1",
                        max_side=1200,
                    )
                )
        recovery.extend(panel_views[:3])
    return recovery


def _brand_needs_recovery(observed: ObservedCandidates) -> bool:
    brand = _selected_candidate(observed.field("brand"))
    class_type = _selected_candidate(observed.field("class_type"))
    if brand is None:
        return True
    if class_type is None or brand.evidence.panel_id != class_type.evidence.panel_id:
        return False
    brand_bounds = _evidence_bounds(brand.evidence)
    class_bounds = _evidence_bounds(class_type.evidence)
    brand_height = max(1, brand_bounds[3] - brand_bounds[1])
    class_height = max(1, class_bounds[3] - class_bounds[1])
    vertical_gap = class_bounds[1] - brand_bounds[3]
    return not (0 <= vertical_gap <= max(brand_height, class_height) * 6)


def _field_anchor(
    observed: ObservedCandidates, field: str, panel_id: str
) -> tuple[int, int, int, int] | None:
    candidates = [
        candidate
        for candidate in observed.field(field).candidates
        if candidate.evidence.panel_id == panel_id
    ]
    if not candidates:
        return None
    evidence = max(
        candidates,
        key=lambda item: item.evidence.confidence_provenance.signal or 0.0,
    ).evidence
    return _evidence_bounds(evidence)


def _warning_anchor(
    observed: ObservedCandidates, panel_id: str
) -> tuple[int, int, int, int] | None:
    evidence = observed.warning.body_evidence or observed.warning.heading_evidence
    if evidence is None or evidence.panel_id != panel_id:
        return None
    return _evidence_bounds(evidence)


def _evidence_bounds(evidence: Evidence) -> tuple[int, int, int, int]:
    points = evidence.polygon_original_pixels
    return (
        min(point.x for point in points),
        min(point.y for point in points),
        max(point.x for point in points),
        max(point.y for point in points),
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
    return infer_beverage_type(observed)


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
