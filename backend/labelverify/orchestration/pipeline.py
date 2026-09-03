from __future__ import annotations

import re
import time
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from numpy.typing import NDArray

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
    OcrLine,
    PanelResult,
    ReferenceRecord,
    StageTimings,
    VerificationResult,
    VolumeUnit,
)
from labelverify.domain.beverage import infer_beverage_type
from labelverify.domain.engine import ComparisonInputs, compare_all, mark_unresolved_beverage
from labelverify.domain.normalize import parse_abv, parse_proof, punctuation_folded
from labelverify.domain.presentation import (
    bad_image,
    beverage_inference,
    present_checks,
    present_panels,
    present_wording,
    warning_evidence,
)
from labelverify.domain.types import ObservedCandidates, WarningObservation
from labelverify.extraction.candidates import locate_candidates
from labelverify.extraction.port import ExtractionPort
from labelverify.extraction.rapidocr_adapter import deduplicate_ocr_lines
from labelverify.imaging.decode import (
    DecodedPanel,
    ImageLimitError,
    InvalidImageError,
    decode_panel,
)
from labelverify.imaging.transforms import (
    ImageView,
    create_crop_ocr_view,
    create_enhanced_view,
    create_ocr_views,
)


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
    checks = present_wording(
        present_checks(checks, job.reference.beverage_type, job.reference.reference_provenance),
        observed,
    )
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
    ocr_panels, result_panels = _deduplicate_visual_panels(decoded)
    views = [view for panel in ocr_panels for view in create_ocr_views(panel)]
    preprocess_ms = _elapsed_ms(preprocess_started)
    ocr_started = time.perf_counter()
    try:
        lines = adapter.extract(views)
    except Exception as exc:
        raise PipelineFailure("inference_failed") from exc
    ocr_ms = _elapsed_ms(ocr_started)

    # Readability is decided by what OCR actually read, not by a global sharpness statistic:
    # a soft render with a clean warning is readable, a blank or blurred capture is not.
    ocr_panels = [_refine_coverage(panel, lines) for panel in ocr_panels]
    enhanced_views = [
        create_enhanced_view(panel)
        for panel in ocr_panels
        if _reads_poorly(panel, lines) and not _already_enhanced(panel, views)
    ]
    if enhanced_views:
        ocr_started = time.perf_counter()
        try:
            enhanced_lines = adapter.extract(enhanced_views)
        except Exception as exc:
            raise PipelineFailure("inference_failed") from exc
        ocr_ms += _elapsed_ms(ocr_started)
        lines = deduplicate_ocr_lines([*lines, *enhanced_lines])
        ocr_panels = [_refine_coverage(panel, lines) for panel in ocr_panels]
    result_panels = _propagate_coverage(result_panels, ocr_panels)

    candidates_started = time.perf_counter()
    public_panels = [panel.public_panel() for panel in result_panels]
    observed = locate_candidates(lines, public_panels)
    candidates_ms = _elapsed_ms(candidates_started)

    preprocess_started = time.perf_counter()
    recovery_views = _recovery_views(ocr_panels, observed)
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


# Focused re-reads per request: two per panel, three per product, warning crops first.
_MAX_PANEL_RECOVERY_VIEWS = 2
_MAX_RECOVERY_VIEWS = 3
# A panel the decoder called unreadable keeps its fields only when OCR returns a dozen lines
# at reading confidence: a soft photograph of a real label, not a blurred capture that
# yields a few garbled lines.
_SUBSTANTIAL_LINE_COUNT = 12
_SUBSTANTIAL_MEAN_CONFIDENCE = 0.75
_READABLE_LINE_COUNT = 3
_READABLE_MEAN_CONFIDENCE = 0.80
_CONFIDENT_MEAN_CONFIDENCE = 0.90
_WEAK_MEAN_CONFIDENCE = 0.70
_UNREADABLE_MEAN_CONFIDENCE = 0.45


def _panel_read_statistics(panel: DecodedPanel, lines: list[OcrLine]) -> tuple[int, float]:
    panel_lines = [line for line in lines if line.panel_id == panel.panel_id]
    confidences = [line.confidence for line in panel_lines if line.confidence is not None]
    mean = sum(confidences) / len(confidences) if confidences else 0.0
    return len(panel_lines), mean


def _refine_coverage(panel: DecodedPanel, lines: list[OcrLine]) -> DecodedPanel:
    count, mean = _panel_read_statistics(panel, lines)
    signals = dict(panel.quality_signals)
    signals["ocrLineCount"] = float(count)
    signals["ocrMeanConfidence"] = round(mean, 3)
    state: Literal["Sufficient", "Review", "Unreadable"]
    confident_read = (count >= _READABLE_LINE_COUNT and mean >= _READABLE_MEAN_CONFIDENCE) or (
        count >= 1 and mean >= _CONFIDENT_MEAN_CONFIDENCE
    )
    substantial_read = count >= _SUBSTANTIAL_LINE_COUNT and mean >= _SUBSTANTIAL_MEAN_CONFIDENCE
    if confident_read:
        # Decode found a blurred, dark, or blank capture; a confident read shows text was
        # recovered from it, but the image itself is still a reviewer's call, never clean.
        state = "Review" if panel.coverage_state == "Unreadable" else "Sufficient"
    elif panel.coverage_state == "Unreadable":
        # A soft capture that OCR still reads at length keeps its fields for the reviewer;
        # a capture that yields only a few weak lines does not.
        state = "Review" if substantial_read else "Unreadable"
    elif (
        count == 0
        or (count < 2 and mean < _WEAK_MEAN_CONFIDENCE)
        or mean < _UNREADABLE_MEAN_CONFIDENCE
    ):
        state = "Unreadable"
    else:
        state = "Review"
    signals["qualityClass"] = state
    return replace(panel, quality_signals=signals, coverage_state=state)


def _reads_poorly(panel: DecodedPanel, lines: list[OcrLine]) -> bool:
    count, mean = _panel_read_statistics(panel, lines)
    return count < _READABLE_LINE_COUNT or mean < _WEAK_MEAN_CONFIDENCE


def _already_enhanced(panel: DecodedPanel, views: list[ImageView]) -> bool:
    return any(view.panel_id == panel.panel_id and "clahe" in view.transform_id for view in views)


def _propagate_coverage(
    result_panels: list[DecodedPanel], ocr_panels: list[DecodedPanel]
) -> list[DecodedPanel]:
    """Give retained duplicate uploads the readability of the panel that was actually read."""

    by_id = {panel.panel_id: panel for panel in ocr_panels}
    propagated: list[DecodedPanel] = []
    for panel in result_panels:
        source_id = panel.quality_signals.get("duplicateOfPanelId")
        source = by_id.get(panel.panel_id)
        if source is None and isinstance(source_id, str):
            source = by_id.get(source_id)
        if source is None:
            propagated.append(panel)
            continue
        signals = dict(source.quality_signals)
        if isinstance(source_id, str):
            signals["duplicateOfPanelId"] = source_id
        propagated.append(
            replace(panel, quality_signals=signals, coverage_state=source.coverage_state)
        )
    return propagated


def _deduplicate_visual_panels(
    decoded: list[DecodedPanel],
) -> tuple[list[DecodedPanel], list[DecodedPanel]]:
    """Avoid repeat OCR for visually equivalent uploads while retaining their records."""

    canonical: list[DecodedPanel] = []
    result_panels: list[DecodedPanel] = []
    thumbnails: list[NDArray[np.float32]] = []
    for panel in decoded:
        thumbnail = cv2.resize(
            cv2.cvtColor(panel.rgb, cv2.COLOR_RGB2GRAY),
            (64, 64),
            interpolation=cv2.INTER_AREA,
        ).astype(np.float32)
        duplicate_index = next(
            (
                index
                for index, existing in enumerate(thumbnails)
                if _visual_panels_equivalent(panel, canonical[index], thumbnail, existing)
            ),
            None,
        )
        if duplicate_index is None:
            canonical.append(panel)
            thumbnails.append(thumbnail)
            result_panels.append(panel)
            continue
        quality_signals = dict(panel.quality_signals)
        quality_signals["duplicateOfPanelId"] = canonical[duplicate_index].panel_id
        result_panels.append(replace(panel, quality_signals=quality_signals))
    return canonical, result_panels


def _visual_panels_equivalent(
    candidate: DecodedPanel,
    existing: DecodedPanel,
    candidate_thumbnail: NDArray[np.float32],
    existing_thumbnail: NDArray[np.float32],
) -> bool:
    candidate_ratio = candidate.width / candidate.height
    existing_ratio = existing.width / existing.height
    if abs(candidate_ratio - existing_ratio) / max(candidate_ratio, existing_ratio) > 0.002:
        return False
    candidate_std = float(candidate_thumbnail.std())
    existing_std = float(existing_thumbnail.std())
    if candidate_std < 1.0 or existing_std < 1.0:
        return float(np.mean(np.abs(candidate_thumbnail - existing_thumbnail))) <= 0.5
    candidate_normalized = (candidate_thumbnail - float(candidate_thumbnail.mean())) / candidate_std
    existing_normalized = (existing_thumbnail - float(existing_thumbnail.mean())) / existing_std
    correlation = float(
        np.corrcoef(candidate_normalized.ravel(), existing_normalized.ravel())[0, 1]
    )
    normalized_error = float(np.mean(np.abs(candidate_normalized - existing_normalized)))
    return correlation >= 0.999 and normalized_error <= 0.025


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


def _recovery_views(decoded: list[DecodedPanel], observed: ObservedCandidates) -> list[ImageView]:
    """Targeted second reads at higher resolution.

    The first pass reads each panel once at a bounded size. Small statutory text, above all
    the government warning, is then re-read from an enlarged crop of the region the first
    pass located, and missing fields get one focused crop each. Every crop keeps original
    pixel coordinates so evidence still points at the source image.
    """

    recovery: list[ImageView] = []
    warning = observed.warning
    missing_content = any(
        observed.field(field).status in {"Not found", "Unreadable"}
        for field in ("abv", "net_contents")
    )
    missing_brand = observed.field("brand").status in {"Not found", "Unreadable"}
    missing_producer = observed.field("producer").status in {"Not found", "Unreadable"}

    for panel in decoded:
        panel_views: list[ImageView] = []
        panel_warning = _warning_for_panel(observed, panel.panel_id)
        warning_anchor = _warning_anchor(observed, panel.panel_id)
        heading_anchor = _warning_heading_anchor(observed, panel.panel_id)
        if (
            panel_warning is not None
            and warning_anchor is not None
            and heading_anchor is not None
            and not _warning_settled(panel_warning)
        ):
            panel_views.append(
                _warning_detail_view(
                    panel,
                    warning_anchor,
                    heading_anchor,
                    body_complete=_warning_body_complete(panel_warning),
                )
            )
        elif warning.heading is None:
            panel_views.extend(_warning_search_views(panel))
        if missing_brand:
            class_anchor = _field_anchor(observed, "class_type", panel.panel_id)
            if class_anchor is not None:
                left, top, right, bottom = class_anchor
                center_x = (left + right) // 2
                if panel.coverage_state == "Sufficient":
                    half_width = max(round((right - left) * 0.85), round(panel.width * 0.16))
                    crop_top = top - round(panel.height * 0.24)
                else:
                    half_width = max(round((right - left) * 0.85), round(panel.width * 0.10))
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
                        max_side=1200,
                    )
                )
        if missing_content and len(panel_views) < 3:
            anchor = _field_anchor(observed, "class_type", panel.panel_id) or _field_anchor(
                observed, "brand", panel.panel_id
            )
            if anchor is not None:
                left, top, right, bottom = anchor
                center_x = (left + right) // 2
                half_width = max((right - left) * 2, round(panel.width * 0.30))
                panel_views.append(
                    create_crop_ocr_view(
                        panel,
                        (
                            center_x - half_width,
                            bottom + round(panel.height * 0.01),
                            center_x + half_width,
                            bottom + round(panel.height * 0.16),
                        ),
                        f"transform-{panel.panel_id}-content-detail-v1",
                        max_side=1200,
                    )
                )
        if missing_producer and len(panel_views) < 3:
            content_anchor = _field_anchor(
                observed, "net_contents", panel.panel_id
            ) or _field_anchor(observed, "abv", panel.panel_id)
            if content_anchor is not None:
                left, top, right, bottom = content_anchor
                center_x = (left + right) // 2
                half_width = max((right - left) * 2, round(panel.width * 0.20))
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
                        max_side=1200,
                    )
                )
        # At most two focused reads per panel keep the second pass inside the time budget.
        recovery.extend(panel_views[:_MAX_PANEL_RECOVERY_VIEWS])
    # Across a multi-panel product the warning re-reads come first and the total stays
    # inside three views so a two-panel request keeps its latency budget.
    recovery.sort(key=lambda view: 0 if "warning-detail" in view.transform_id else 1)
    return recovery[:_MAX_RECOVERY_VIEWS]


def _warning_body_complete(warning: WarningObservation) -> bool:
    """True when the read body already carries about as many words as the statute."""

    expected = len(str(contracts().rules["warning"]["bodyExact"]).split())
    return warning.body is not None and len(warning.body.split()) >= expected - 3


def _warning_heading_anchor(
    observed: ObservedCandidates, panel_id: str
) -> tuple[int, int, int, int] | None:
    observation = _warning_for_panel(observed, panel_id)
    evidence = observation.heading_evidence if observation is not None else None
    if evidence is None or evidence.panel_id != panel_id:
        return None
    return _evidence_bounds(evidence)


def _warning_settled(warning: WarningObservation) -> bool:
    """True when the first read already carries the statutory body with high confidence."""

    if warning.heading is None or warning.body is None or warning.body_evidence is None:
        return False
    expected = punctuation_folded(str(contracts().rules["warning"]["bodyExact"]))
    signal = warning.body_evidence.confidence_provenance.signal or 0.0
    return punctuation_folded(warning.body) == expected and signal >= 0.9


def _warning_detail_view(
    panel: DecodedPanel,
    anchor: tuple[int, int, int, int],
    heading_anchor: tuple[int, int, int, int],
    *,
    body_complete: bool,
) -> ImageView:
    """Crop the statement region at up to twice its native size for a second read.

    The heading height is the scale unit. A body that is still short of the statutory word
    count is extended well below the last line read, so lines the first pass missed are
    inside the crop; a complete body only gets a small margin.
    """

    left, top, right, bottom = anchor
    width = max(1, right - left)
    line_height = max(4, heading_anchor[3] - heading_anchor[1])
    margin_x = max(round(width * 0.15), round(panel.width * 0.02))
    extend_below = round(line_height * 1.5) if body_complete else line_height * 12
    return create_crop_ocr_view(
        panel,
        (
            min(left, heading_anchor[0]) - margin_x,
            min(top, heading_anchor[1]) - round(line_height * 0.6),
            max(right, heading_anchor[2]) + margin_x,
            bottom + extend_below,
        ),
        f"transform-{panel.panel_id}-warning-detail-v2",
        max_side=1400,
    )


def _warning_search_views(panel: DecodedPanel) -> list[ImageView]:
    """Enlarged reads of where a warning usually sits when the first pass found none."""

    if panel.width >= panel.height:
        bounds = (
            round(panel.width * 0.55),
            round(panel.height * 0.10),
            panel.width,
            round(panel.height * 0.95),
        )
        if panel.coverage_state == "Sufficient":
            return [
                create_crop_ocr_view(
                    panel,
                    bounds,
                    f"transform-{panel.panel_id}-right-detail-rotated-v1",
                    rotate_clockwise=True,
                    max_side=1400,
                )
            ]
        return [
            create_crop_ocr_view(
                panel, bounds, f"transform-{panel.panel_id}-right-detail-v1", max_side=1400
            )
        ]
    return [
        create_crop_ocr_view(
            panel,
            (
                round(panel.width * 0.08),
                round(panel.height * 0.45),
                round(panel.width * 0.92),
                round(panel.height * 0.95),
            ),
            f"transform-{panel.panel_id}-lower-label-detail-v1",
            max_side=1800,
        )
    ]


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


def _warning_for_panel(observed: ObservedCandidates, panel_id: str) -> WarningObservation | None:
    """The statement as read on one panel, whichever panel carried the primary read."""

    for observation in (observed.warning, *observed.warning_alternates):
        evidence = observation.heading_evidence or observation.body_evidence
        if evidence is not None and evidence.panel_id == panel_id:
            return observation
    return None


def _warning_anchor(
    observed: ObservedCandidates, panel_id: str
) -> tuple[int, int, int, int] | None:
    observation = _warning_for_panel(observed, panel_id)
    if observation is None:
        return None
    evidence = observation.body_evidence or observation.heading_evidence
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
