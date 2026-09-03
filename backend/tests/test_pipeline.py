from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from labelverify.contracts.models import (
    CheckResult,
    OcrLine,
    OriginalDimensions,
    PanelResult,
    Point,
)
from labelverify.imaging.decode import DecodedPanel
from labelverify.orchestration import pipeline as pipeline_module
from labelverify.orchestration.pipeline import (
    AnalysisJob,
    PipelineFailure,
    PipelineJob,
    execute_analysis,
    execute_pipeline,
    validate_result_integrity,
)
from PIL import Image

from .helpers import evidence, jpeg_bytes, reference


class FakeAdapter:
    model_identity = "fake-reference-blind"

    def __init__(self, texts: list[str] | None = None) -> None:
        self.texts = texts

    def initialize(self) -> None:
        return None

    def extract(self, views: object) -> list[OcrLine]:
        texts = self.texts or [
            "OLD TOM DISTILLERY",
            "Kentucky Straight Bourbon Whiskey",
            "45% Alc./Vol. 90 Proof",
            "750 mL",
            "GOVERNMENT WARNING:",
            (
                "(1) According to the Surgeon General, women should not drink "
                "alcoholic beverages during pregnancy because of the risk of birth defects."
            ),
            (
                "(2) Consumption of alcoholic beverages impairs your ability to drive a "
                "car or operate machinery, and may cause health problems."
            ),
            "BOTTLED BY: OLD HERITAGE DISTILLERY, LLC FRANKFORT, KENTUCKY",
        ]
        return [
            OcrLine(
                panelId="panel-1",
                text=text,
                polygon=[
                    Point(x=20, y=20 + index * 50),
                    Point(x=600, y=20 + index * 50),
                    Point(x=600, y=50 + index * 50),
                    Point(x=20, y=50 + index * 50),
                ],
                confidence=0.95,
                readingOrder=index,
                sourceView="original",
                transformId="transform-panel-1-v1",
            )
            for index, text in enumerate(texts)
        ]


def test_c008_pipeline_returns_complete_ordered_result(tmp_path: Path) -> None:
    path = tmp_path / "panel.jpg"
    path.write_bytes(jpeg_bytes())
    result = execute_pipeline(PipelineJob("request", "build", reference(), (path,)), FakeAdapter())
    assert result.request_id == "request"
    assert result.model_identity == "fake-reference-blind"
    assert len(result.checks) == 24
    assert result.stage_timings.decode_ms >= 0
    assert result.stage_timings.ocr_ms >= 0
    assert result.summary in {"Differences detected", "Review needed"}
    assert all(item.check_id for item in result.checks)


def test_unresolved_analysis_returns_24_reviewable_checks(tmp_path: Path) -> None:
    path = tmp_path / "panel.jpg"
    path.write_bytes(jpeg_bytes())
    adapter = FakeAdapter(
        [
            "CLOUD NINE",
            "HARD SELTZER",
            "5% Alcohol by Volume",
            "12 fl oz",
        ]
    )

    result = execute_analysis(AnalysisJob("request", "build", (path,)), adapter)

    assert result.draft.beverage_type is None
    assert result.verification is not None
    assert len(result.verification.checks) == 24
    assert result.verification.checks[0].state == "Review"
    assert result.verification.summary == "Review needed"


def test_label_first_spirits_without_readable_abv_remains_reviewable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "panel.jpg"
    path.write_bytes(jpeg_bytes())
    monkeypatch.setattr(
        pipeline_module,
        "_infer_beverage_type",
        lambda _observed: ("distilled_spirits", 0.9, "Test type evidence", False),
    )
    result = execute_analysis(
        AnalysisJob("request", "build", (path,)),
        FakeAdapter(["CLEARWATER VODKA", "750 mL"]),
    )

    assert result.verification is not None
    assert len(result.verification.checks) == 24
    proof = next(check for check in result.verification.checks if check.check_id == "proof")
    assert proof.state == "Not verified"
    assert proof.reason_code == "proof_requires_actual_abv"


def test_pipeline_invalid_image_is_typed_and_result_free(tmp_path: Path) -> None:
    path = tmp_path / "bad.img"
    path.write_bytes(b"not an image")
    with pytest.raises(PipelineFailure) as caught:
        execute_pipeline(PipelineJob("request", "build", reference(), (path,)), FakeAdapter())
    assert caught.value.code == "invalid_image"
    assert caught.value.field_or_panel == "panel-1"


def test_decoded_pixel_error_gives_actual_limit_and_exact_correction(
    tmp_path: Path,
) -> None:
    path = tmp_path / "large.png"
    Image.new("RGB", (4_000, 3_001), "white").save(path)

    with pytest.raises(PipelineFailure) as caught:
        execute_analysis(AnalysisJob("request", "build", (path,)), FakeAdapter())

    failure = caught.value
    assert failure.code == "decoded_pixel_limit"
    assert failure.field_or_panel == "panel-1"
    assert [item["label"] for item in failure.comparisons] == [
        "Image width",
        "Image height",
        "Decoded pixels",
    ]
    assert failure.comparisons[-1] == {
        "label": "Decoded pixels",
        "expected": "12,000,000 or fewer",
        "actual": "12,004,000",
        "passed": False,
    }
    assert failure.next_action is not None
    assert "preserving its aspect ratio" in failure.next_action


def test_cumulative_pixel_budget_is_passed_before_fourth_decode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    limits_seen: list[int] = []

    def fake_decode(path: Path, panel_id: str, max_pixels: int) -> DecodedPanel:
        del path
        limits_seen.append(max_pixels)
        return DecodedPanel(
            panel_id=panel_id,
            rgb=np.zeros((1, 1, 3), dtype=np.uint8),
            width=4_000,
            height=3_000,
            pixels=12_000_000,
            quality_signals={"qualityClass": "Sufficient"},
            coverage_state="Sufficient",
        )

    monkeypatch.setattr(pipeline_module, "decode_panel", fake_decode)
    paths = tuple(tmp_path / f"panel-{index}.img" for index in range(1, 5))
    with pytest.raises(PipelineFailure) as caught:
        execute_pipeline(PipelineJob("request", "build", reference(), paths), FakeAdapter())
    assert caught.value.code == "decoded_pixel_limit"
    assert caught.value.field_or_panel == "panel-4"
    assert limits_seen == [12_000_000, 12_000_000, 12_000_000]


def test_brand_recovery_detects_brand_candidate_below_class_as_suspicious() -> None:
    observed = pipeline_module.locate_candidates(
        [
            OcrLine(
                panelId="panel-1",
                text="PALE ALE",
                polygon=[
                    Point(x=100, y=300),
                    Point(x=300, y=300),
                    Point(x=300, y=340),
                    Point(x=100, y=340),
                ],
                confidence=0.95,
                readingOrder=0,
                sourceView="original",
                transformId="transform-panel-1-v1",
            ),
            OcrLine(
                panelId="panel-1",
                text="SEATTLE.WHINGION",
                polygon=[
                    Point(x=100, y=600),
                    Point(x=300, y=600),
                    Point(x=300, y=640),
                    Point(x=100, y=640),
                ],
                confidence=0.95,
                readingOrder=1,
                sourceView="original",
                transformId="transform-panel-1-v1",
            ),
        ],
        [
            PanelResult(
                panelId="panel-1",
                originalDimensions=OriginalDimensions(width=800, height=1000),
                qualitySignals={},
                coverageState="Sufficient",
            )
        ],
    )

    assert pipeline_module._brand_needs_recovery(observed) is True


def test_integrity_rejects_out_of_bounds_evidence() -> None:
    panel = PanelResult(
        panelId="panel-1",
        originalDimensions=OriginalDimensions(width=100, height=100),
        qualitySignals={},
        coverageState="Sufficient",
    )
    invalid = evidence("bad", x=50, y=90)
    check = CheckResult(
        checkId="brand",
        label="Brand",
        applicable=True,
        state="Match",
        reasonCode="x",
        reasonText="x",
        evidenceRef=invalid.evidence_id,
        alternatives=[],
        capability="test",
        policyVersion="1",
    )
    with pytest.raises(PipelineFailure):
        validate_result_integrity([panel], [invalid], [check])


def test_integrity_rejects_missing_evidence_reference() -> None:
    panel = PanelResult(
        panelId="panel-1",
        originalDimensions=OriginalDimensions(width=200, height=200),
        qualitySignals={},
        coverageState="Sufficient",
    )
    check = CheckResult(
        checkId="brand",
        label="Brand",
        applicable=True,
        state="Match",
        reasonCode="x",
        reasonText="x",
        evidenceRef="ev_missing_panel-1_01",
        alternatives=[],
        capability="test",
        policyVersion="1",
    )
    with pytest.raises(PipelineFailure):
        validate_result_integrity([panel], [], [check])
