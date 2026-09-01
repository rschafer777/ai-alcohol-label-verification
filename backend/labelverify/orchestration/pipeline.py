from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import (
    CheckResult,
    Evidence,
    PanelResult,
    ReferenceRecord,
    StageTimings,
    VerificationResult,
)
from labelverify.domain.engine import ComparisonInputs, compare_all
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
            "The prototype implements the distilled-spirits selected-check profile only",
        ],
        summary=summary,
    )


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
