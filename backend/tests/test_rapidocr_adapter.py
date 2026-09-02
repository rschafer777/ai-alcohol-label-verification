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
from labelverify.extraction.rapidocr_adapter import (
    ModelIntegrityError,
    RapidOcrAdapter,
    _ink_density,
    _local_contrast,
    _restore_warning_separator,
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
        params["Global.font_path"] == str(tmp_path / "DejaVuSans.ttf")
        for params in captured
    )
    assert all(
        params["EngineConfig.onnxruntime.intra_op_num_threads"] == 1
        for params in captured
    )


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
        view(f"panel-{index}", np.full((40, 80, 3), index, dtype=np.uint8))
        for index in range(1, 5)
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

    light_density = _ink_density(light, polygon)
    dark_density = _ink_density(dark, polygon)

    assert light_density is not None
    assert dark_density is not None
    assert light_density == dark_density
    assert light_density < 0.25


def test_low_local_contrast_has_no_typography_signal() -> None:
    image = np.full((40, 100), 30, dtype=np.uint8)
    image[10:30, 20:50] = 45
    polygon = [[0, 0], [99, 0], [99, 39], [0, 39]]

    assert _ink_density(image, polygon) is None


def test_local_contrast_distinguishes_clear_and_faint_text() -> None:
    clear = np.full((40, 100), 245, dtype=np.uint8)
    faint = np.full((40, 100), 245, dtype=np.uint8)
    clear[10:30, 20:80] = 10
    faint[10:30, 20:80] = 205
    polygon = [[0, 0], [99, 0], [99, 39], [0, 39]]

    clear_contrast = _local_contrast(clear, polygon)
    faint_contrast = _local_contrast(faint, polygon)

    assert clear_contrast is not None
    assert faint_contrast is not None
    assert clear_contrast > 0.8
    assert faint_contrast < 0.3


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
