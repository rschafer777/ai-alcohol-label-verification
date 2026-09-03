from __future__ import annotations

import hashlib
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace

import cv2
import labelverify.extraction.rapidocr_adapter as rapidocr_adapter_module
import numpy as np
import pytest
import rapidocr
from labelverify.contracts.models import OcrLine, Point
from labelverify.extraction.rapidocr_adapter import (
    ModelIntegrityError,
    RapidOcrAdapter,
    _restore_warning_separator,
    deduplicate_ocr_lines,
    text_metrics,
)
from labelverify.imaging.transforms import ImageView
from numpy.typing import NDArray


def test_runtime_font_is_hash_verified_with_the_models(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    font = tmp_path / "DejaVuSans.ttf"
    font.write_bytes(b"governed open font")
    expected_hash = hashlib.sha256(font.read_bytes()).hexdigest()
    monkeypatch.setattr(
        rapidocr_adapter_module,
        "RUNTIME_ASSETS",
        {font.name: expected_hash},
    )
    adapter = RapidOcrAdapter(tmp_path, require_read_only=False)

    adapter.verify_assets()
    font.write_bytes(b"tampered")

    with pytest.raises(ModelIntegrityError, match="DejaVuSans.ttf"):
        adapter.verify_assets()


def test_initialize_supplies_the_governed_local_font_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: list[dict[str, object]] = []
    warmup_calls = 0

    class FakeRapidOcr:
        def __init__(self, *, params: dict[str, object]) -> None:
            captured.append(params)

        def __call__(self, image: object) -> SimpleNamespace:
            nonlocal warmup_calls
            del image
            warmup_calls += 1
            return SimpleNamespace(boxes=None, txts=None, scores=None)

    adapter = RapidOcrAdapter(tmp_path, require_read_only=False)
    monkeypatch.setattr(adapter, "verify_assets", lambda: None)
    monkeypatch.setattr(rapidocr, "RapidOCR", FakeRapidOcr)

    adapter.initialize()

    assert len(captured) == 2
    assert warmup_calls == 2
    assert all(
        params["Global.font_path"] == str(tmp_path / "DejaVuSans.ttf") for params in captured
    )
    assert all(params["EngineConfig.onnxruntime.intra_op_num_threads"] == 2 for params in captured)


class CountingEngine:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, image: object) -> SimpleNamespace:
        del image
        self.calls += 1
        return SimpleNamespace(
            boxes=[np.asarray([[1, 1], [20, 1], [20, 12], [1, 12]], dtype=np.float32)],
            txts=["OLD TOM"],
            scores=[0.98],
        )


class BarrierEngine(CountingEngine):
    def __init__(self, barrier: Barrier) -> None:
        super().__init__()
        self._barrier = barrier

    def __call__(self, image: object) -> SimpleNamespace:
        self._barrier.wait(timeout=1.0)
        return super().__call__(image)


def view(
    panel_id: str,
    image: NDArray[np.uint8],
    *,
    original_width: int = 80,
    original_height: int = 40,
    scale_x: float = 1.0,
    scale_y: float = 1.0,
) -> ImageView:
    return ImageView(
        panel_id=panel_id,
        image=image,
        source_view="original",
        transform_id=f"transform-{panel_id}-bounded-v1",
        original_width=original_width,
        original_height=original_height,
        scale_x=scale_x,
        scale_y=scale_y,
    )


def test_identical_views_reuse_inference_and_preserve_panel_identity(tmp_path: Path) -> None:
    image = np.full((40, 80, 3), 255, dtype=np.uint8)
    adapter = RapidOcrAdapter(tmp_path, require_read_only=False)
    engine = CountingEngine()
    adapter._engines = (engine,)

    lines = adapter.extract([view("panel-1", image), view("panel-2", image.copy())])

    assert engine.calls == 1
    assert [line.panel_id for line in lines] == ["panel-1", "panel-2"]
    assert [line.reading_order for line in lines] == [0, 1]
    assert [line.transform_id for line in lines] == [
        "transform-panel-1-bounded-v1",
        "transform-panel-2-bounded-v1",
    ]


def test_identical_pixels_reuse_inference_across_analysis_calls(tmp_path: Path) -> None:
    image = np.full((40, 80, 3), 255, dtype=np.uint8)
    adapter = RapidOcrAdapter(tmp_path, require_read_only=False)
    engine = CountingEngine()
    adapter._engines = (engine,)

    first = adapter.extract([view("panel-1", image)])
    second = adapter.extract([view("panel-2", image.copy())])

    assert engine.calls == 1
    assert first[0].panel_id == "panel-1"
    assert second[0].panel_id == "panel-2"


def test_cached_pixels_replay_each_views_coordinate_mapping(tmp_path: Path) -> None:
    image = np.full((40, 80, 3), 255, dtype=np.uint8)
    adapter = RapidOcrAdapter(tmp_path, require_read_only=False)
    engine = CountingEngine()
    adapter._engines = (engine,)

    lines = adapter.extract(
        [
            view("panel-1", image),
            view(
                "panel-2",
                image.copy(),
                original_width=160,
                original_height=80,
                scale_x=0.5,
                scale_y=0.5,
            ),
        ]
    )

    assert engine.calls == 1
    assert [(point.x, point.y) for point in lines[0].polygon] == [
        (1, 1),
        (20, 1),
        (20, 12),
        (1, 12),
    ]
    assert [(point.x, point.y) for point in lines[1].polygon] == [
        (2, 2),
        (40, 2),
        (40, 24),
        (2, 24),
    ]


def test_unique_views_use_two_bounded_inference_lanes(tmp_path: Path) -> None:
    barrier = Barrier(2)
    engines = (BarrierEngine(barrier), BarrierEngine(barrier))
    adapter = RapidOcrAdapter(tmp_path, require_read_only=False)
    adapter._engines = engines
    views = [
        view(f"panel-{index}", np.full((40, 80, 3), index, dtype=np.uint8)) for index in range(1, 5)
    ]

    lines = adapter.extract(views)

    assert [engine.calls for engine in engines] == [2, 2]
    assert [line.panel_id for line in lines] == [
        "panel-1",
        "panel-2",
        "panel-3",
        "panel-4",
    ]
    assert [line.reading_order for line in lines] == [0, 1, 2, 3]


def test_foreground_density_is_polarity_independent_and_bounded() -> None:
    light = np.full((40, 100), 245, dtype=np.uint8)
    dark = np.full((40, 100), 10, dtype=np.uint8)
    light[10:30, 20:50] = 10
    dark[10:30, 20:50] = 245
    polygon = [[0, 0], [99, 0], [99, 39], [0, 39]]

    light_density = text_metrics(light, polygon).ink_density
    dark_density = text_metrics(dark, polygon).ink_density

    assert light_density is not None
    assert dark_density is not None
    assert light_density == dark_density
    assert light_density < 0.25


def test_low_local_contrast_has_no_typography_signal() -> None:
    image = np.full((40, 100), 30, dtype=np.uint8)
    image[10:30, 20:50] = 45
    polygon = [[0, 0], [99, 0], [99, 39], [0, 39]]

    metrics = text_metrics(image, polygon)
    assert metrics.ink_density is None
    assert metrics.stroke_px is None
    assert metrics.contrast_ratio is None


def test_local_contrast_distinguishes_clear_and_faint_text() -> None:
    clear = np.full((40, 100), 245, dtype=np.uint8)
    faint = np.full((40, 100), 245, dtype=np.uint8)
    clear[10:30, 20:80] = 10
    faint[10:30, 20:80] = 205
    polygon = [[0, 0], [99, 0], [99, 39], [0, 39]]

    clear_metrics = text_metrics(clear, polygon)
    faint_metrics = text_metrics(faint, polygon)

    assert clear_metrics.local_contrast is not None
    assert faint_metrics.local_contrast is not None
    assert clear_metrics.local_contrast > 0.8
    assert faint_metrics.local_contrast < 0.3
    # WCAG relative luminance: near-black on near-white exceeds the 4.5 body-text ratio,
    # light gray on near-white stays below the 3.0 minimum.
    assert clear_metrics.contrast_ratio is not None and clear_metrics.contrast_ratio > 10
    assert faint_metrics.contrast_ratio is not None and faint_metrics.contrast_ratio < 3.0


def test_letter_height_ignores_parentheses_and_dots() -> None:
    from labelverify.extraction.rapidocr_adapter import _letter_height

    mask = np.zeros((60, 400), dtype=np.uint8)
    # Ten capital letters 30 px tall, two parentheses 40 px tall, three dots 4 px tall.
    for index in range(10):
        mask[15:45, 20 + index * 30 : 40 + index * 30] = 1
    mask[10:50, 330:336] = 1
    mask[10:50, 350:356] = 1
    for index in range(3):
        mask[41:45, 370 + index * 8 : 374 + index * 8] = 1

    assert _letter_height(mask) == 30.0

    # Mixed case: six x-height letters (21 px) and four ascender letters (30 px) measure
    # the ascender height, the same reference as a capital.
    mixed = np.zeros((60, 400), dtype=np.uint8)
    for index in range(6):
        mixed[24:45, 20 + index * 30 : 40 + index * 30] = 1
    for index in range(4):
        mixed[15:45, 220 + index * 30 : 240 + index * 30] = 1
    assert _letter_height(mixed) == 30.0


def test_deduplicate_keeps_distinct_lines_from_one_view_and_dissimilar_reads() -> None:
    tall = make_line("BOURBON", (100, 100, 700, 400), confidence=0.98, view="original")
    inside = make_line("750 ML", (300, 200, 500, 260), confidence=0.97, view="original")
    assert {item.text for item in deduplicate_ocr_lines([tall, inside])} == {"BOURBON", "750 ML"}

    rows = [
        make_line(
            text,
            (100, 100 + index * 10, 700, 130 + index * 10),
            confidence=0.95,
            view="original",
        )
        for index, text in enumerate(("women should not drink", "because of the risk", "of birth"))
    ]
    assert len(deduplicate_ocr_lines(rows)) == 3

    duplicate_detection = [
        make_line("12 FL. OZ", (100, 100, 300, 140), confidence=0.98, view="original"),
        make_line("12 FL. 0Z", (102, 101, 298, 139), confidence=0.93, view="original"),
    ]
    assert [item.text for item in deduplicate_ocr_lines(duplicate_detection)] == ["12 FL. OZ"]

    other_view = make_line("BOURBON", (102, 98, 698, 402), confidence=0.9, view="crop")
    fused = deduplicate_ocr_lines([tall, other_view])
    assert [item.text for item in fused] == ["BOURBON"]

    unrelated = make_line("750 ML", (102, 98, 698, 402), confidence=0.95, view="crop")
    assert len(deduplicate_ocr_lines([tall, unrelated])) == 2

    # A weak small read inside a tall column of rotated text keeps its own place.
    column = make_line("GOVERNMENT WARNING (1) ACCORDING", (100, 100, 160, 900), confidence=0.9)
    small = make_line("750ML", (110, 400, 150, 440), confidence=0.75, view="crop")
    assert {item.text for item in deduplicate_ocr_lines([column, small])} == {
        "GOVERNMENT WARNING (1) ACCORDING",
        "750ML",
    }


def test_stroke_width_follows_bar_thickness_and_ink_height() -> None:
    thin = np.full((60, 200), 245, dtype=np.uint8)
    thick = np.full((60, 200), 245, dtype=np.uint8)
    for start in (20, 60, 100, 140):
        thin[10:50, start : start + 3] = 10
        thick[10:50, start : start + 9] = 10
    polygon = [[0, 0], [199, 0], [199, 59], [0, 59]]

    thin_metrics = text_metrics(thin, polygon)
    thick_metrics = text_metrics(thick, polygon)

    assert thin_metrics.ink_height_px == 40 and thick_metrics.ink_height_px == 40
    assert thin_metrics.stroke_px is not None and thick_metrics.stroke_px is not None
    assert 2.0 <= thin_metrics.stroke_px <= 4.5
    assert 7.0 <= thick_metrics.stroke_px <= 11.0


def make_line(
    text: str,
    box: tuple[int, int, int, int],
    *,
    confidence: float,
    panel: str = "panel-1",
    view: str = "original",
    ink_height: float | None = None,
) -> OcrLine:
    x0, y0, x1, y1 = box
    return OcrLine(
        panelId=panel,
        text=text,
        polygon=[Point(x=x0, y=y0), Point(x=x1, y=y0), Point(x=x1, y=y1), Point(x=x0, y=y1)],
        confidence=confidence,
        readingOrder=0,
        sourceView="original" if view == "original" else "derived",
        transformId=f"transform-{panel}-{view}-v1",
        inkHeightPx=ink_height,
        strokePx=None if ink_height is None else ink_height / 8,
    )


def test_line_fusion_keeps_the_fullest_reading_of_one_region_and_drops_fragments() -> None:
    lines = [
        make_line("Distilled Vodka", (1201, 1311, 1700, 1394), confidence=0.98),
        make_line("ed Vodka", (1420, 1316, 1699, 1392), confidence=1.0, view="crop", ink_height=40),
        make_line("DEFECTS.2CONSUMPTION OFALCOHOLIC", (983, 1999, 1476, 2057), confidence=0.92),
        make_line("DEFECTS.(2C", (984, 1998, 1149, 2051), confidence=0.90, view="crop"),
        make_line(
            "CONSUMPTION OF ALCOHOLIC", (1128, 2006, 1478, 2054), confidence=0.96, view="crop"
        ),
        make_line("750 mL", (1391, 2018, 1575, 2079), confidence=1.0),
        make_line("Another panel", (1201, 1311, 1700, 1394), confidence=0.5, panel="panel-2"),
    ]

    fused = deduplicate_ocr_lines(lines)

    texts = [line.text for line in fused]
    assert texts == [
        "Distilled Vodka",
        "DEFECTS.2CONSUMPTION OFALCOHOLIC",
        "750 mL",
        "Another panel",
    ]
    assert [line.reading_order for line in fused] == [0, 1, 2, 3]
    # The higher-resolution crop supplied the typography measurement for the fused region.
    assert fused[0].ink_height_px == 40 and fused[0].stroke_px == 5.0


def test_collapsed_warning_separator_is_restored_when_pixels_show_word_gap() -> None:
    image = np.full((40, 170), 255, dtype=np.uint8)
    image[8:32, 5:98] = 0
    image[8:32, 106:165] = 0
    polygon = [[0, 0], [169, 0], [169, 39], [0, 39]]

    repaired = _restore_warning_separator("GOVERNMENTWARNING:", image, polygon)

    assert repaired == "GOVERNMENT WARNING:"


def test_collapsed_warning_separator_is_not_invented_without_pixel_gap() -> None:
    image = np.full((40, 170), 255, dtype=np.uint8)
    image[8:32, 5:165] = 0
    polygon = [[0, 0], [169, 0], [169, 39], [0, 39]]

    unchanged = _restore_warning_separator("GOVERNMENTWARNING:", image, polygon)

    assert unchanged == "GOVERNMENTWARNING:"


def test_collapsed_warning_separator_is_not_invented_for_rendered_adjacent_glyphs() -> None:
    combinations = (
        (cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1),
        (cv2.FONT_HERSHEY_SIMPLEX, 1.5, 1),
        (cv2.FONT_HERSHEY_DUPLEX, 1.0, 1),
        (cv2.FONT_HERSHEY_DUPLEX, 1.5, 1),
        (cv2.FONT_HERSHEY_TRIPLEX, 1.0, 1),
    )
    for font, scale, thickness in combinations:
        image, polygon = rendered_text("GOVERNMENTWARNING:", font, scale, thickness)

        unchanged = _restore_warning_separator("GOVERNMENTWARNING:", image, polygon)

        assert unchanged == "GOVERNMENTWARNING:"


def test_collapsed_ocr_separator_is_restored_for_rendered_spaced_glyphs() -> None:
    combinations = (
        (cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1),
        (cv2.FONT_HERSHEY_DUPLEX, 1.5, 1),
        (cv2.FONT_HERSHEY_TRIPLEX, 1.0, 1),
    )
    for font, scale, thickness in combinations:
        image, polygon = rendered_text("GOVERNMENT WARNING:", font, scale, thickness)

        repaired = _restore_warning_separator("GOVERNMENTWARNING:", image, polygon)

        assert repaired == "GOVERNMENT WARNING:"


def rendered_text(
    text: str, font: int, scale: float, thickness: int
) -> tuple[NDArray[np.uint8], list[list[int]]]:
    (width, height), _ = cv2.getTextSize(text, font, scale, thickness)
    image = np.full((height + 20, width + 20, 3), 255, dtype=np.uint8)
    cv2.putText(
        image,
        text,
        (10, height + 5),
        font,
        scale,
        (0, 0, 0),
        thickness,
        cv2.LINE_AA,
    )
    foreground = np.any(image < 250, axis=2)
    ys, xs = np.where(foreground)
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    polygon = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    return image, polygon
