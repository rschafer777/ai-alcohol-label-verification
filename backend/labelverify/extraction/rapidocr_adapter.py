from __future__ import annotations

import hashlib
import os
import re
from collections import OrderedDict
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from labelverify.contracts.models import OcrLine
from labelverify.imaging.transforms import ImageView

MODEL_ASSETS = {
    "en_PP-OCRv3_det_infer.onnx": (
        "ea07c15d38ac40cd69da3c493444ec75b44ff23840553ff8ba102c1219ed39c2"
    ),
    "en_PP-OCRv4_rec_infer.onnx": (
        "e8770c967605983d1570cdf5352041dfb68fa0c21664f49f47b155abd3e0e318"
    ),
    "ch_ppocr_mobile_v2.0_cls_infer.onnx": (
        "e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c"
    ),
}
FONT_ASSET = {"DejaVuSans.ttf": "7da195a74c55bef988d0d48f9508bd5d849425c1770dba5d7bfc6ce9ed848954"}
RUNTIME_ASSETS = MODEL_ASSETS | FONT_ASSET
OCR_INFERENCE_LANES = 2
OCR_INTRA_OP_THREADS_PER_LANE = 2
OCR_OUTPUT_CACHE_ENTRIES = 2048
_MIN_LOCAL_CONTRAST = 24.0
_MIN_FOREGROUND_FRACTION = 0.02
_MAX_FOREGROUND_FRACTION = 0.65
_COLLAPSED_WARNING_HEADING = re.compile(r"^governmentwarning\s*:$", re.I)


class ModelIntegrityError(RuntimeError):
    """Raised when bundled OCR assets do not satisfy readiness."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class RapidOcrAdapter:
    def __init__(self, model_root: Path, *, require_read_only: bool = True) -> None:
        self._model_root = model_root
        self._require_read_only = require_read_only
        self._engines: tuple[Any, ...] = ()
        self._output_cache: OrderedDict[tuple[object, ...], Any] = OrderedDict()
        self._model_identity = "rapidocr-3.4.2:" + MODEL_ASSETS["en_PP-OCRv4_rec_infer.onnx"][:12]

    @property
    def model_identity(self) -> str:
        return self._model_identity

    def verify_assets(self) -> None:
        for filename, expected_hash in RUNTIME_ASSETS.items():
            path = self._model_root / filename
            if not path.is_file() or _sha256(path) != expected_hash:
                raise ModelIntegrityError(f"OCR model asset failed integrity: {filename}")
            if self._require_read_only and os.name != "nt" and path.stat().st_mode & 0o222:
                raise ModelIntegrityError(f"OCR model asset must be read-only: {filename}")

    def initialize(self) -> None:
        self.verify_assets()
        self._output_cache.clear()
        from rapidocr import RapidOCR  # type: ignore[import-untyped]
        from rapidocr.utils.typings import LangDet, LangRec  # type: ignore[import-untyped]

        params = {
            "Rec.lang_type": LangRec.EN,
            "Det.lang_type": LangDet.EN,
            "EngineConfig.onnxruntime.intra_op_num_threads": OCR_INTRA_OP_THREADS_PER_LANE,
            "EngineConfig.onnxruntime.inter_op_num_threads": 1,
            "EngineConfig.onnxruntime.enable_cpu_mem_arena": False,
            "Global.font_path": str(self._model_root / "DejaVuSans.ttf"),
            "Global.log_level": "error",
            "Global.max_side_len": 3000,
            "Det.limit_side_len": 1440,
            "Det.model_path": str(self._model_root / "en_PP-OCRv3_det_infer.onnx"),
            "Rec.model_path": str(self._model_root / "en_PP-OCRv4_rec_infer.onnx"),
            "Cls.model_path": str(self._model_root / "ch_ppocr_mobile_v2.0_cls_infer.onnx"),
        }
        # Warm a label-shaped tensor so the first reviewer request does not pay
        # the ONNX allocation and graph setup cost for a production-sized image.
        warmup = np.full((960, 720, 3), 255, dtype=np.uint8)
        cv2.putText(warmup, "LABEL VERIFY", (40, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 3)
        cv2.putText(
            warmup,
            "45% Alc./Vol. 750 mL",
            (40, 320),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (0, 0, 0),
            2,
        )
        engines = tuple(
            _initialize_engine(RapidOCR, params, None) for _ in range(OCR_INFERENCE_LANES)
        )
        with ThreadPoolExecutor(max_workers=OCR_INFERENCE_LANES) as executor:
            list(executor.map(_warm_engine, engines, (warmup.copy() for _ in engines)))
        self._engines = engines

    def extract(self, views: Sequence[ImageView]) -> list[OcrLine]:
        if not self._engines:
            raise RuntimeError("RapidOCR adapter is not initialized")
        unique_views: list[ImageView] = []
        cache_indexes: dict[tuple[object, ...], int] = {}
        view_indexes: list[int] = []
        for view in views:
            cache_key = _view_cache_key(view)
            cache_index = cache_indexes.get(cache_key)
            if cache_index is None:
                cache_index = len(unique_views)
                cache_indexes[cache_key] = cache_index
                unique_views.append(view)
            view_indexes.append(cache_index)
        outputs = self._run_inference(unique_views)

        lines: list[OcrLine] = []
        reading_order = 0
        for view, output_index in zip(views, view_indexes, strict=True):
            output = outputs[output_index]
            boxes = getattr(output, "boxes", None)
            texts = getattr(output, "txts", None)
            scores = getattr(output, "scores", None)
            if boxes is None or texts is None:
                continue
            for index, (box, text) in enumerate(zip(boxes, texts, strict=True)):
                confidence = float(scores[index]) if scores is not None else None
                polygon = view.to_original_polygon(box)
                recognized_text = _restore_warning_separator(str(text), view.image, box)
                line = OcrLine(
                    panelId=view.panel_id,
                    text=recognized_text,
                    polygon=polygon,
                    confidence=confidence,
                    readingOrder=reading_order,
                    sourceView=view.source_view,
                    transformId=view.transform_id,
                    inkDensity=_ink_density(view.image, box),
                    localContrast=_local_contrast(view.image, box),
                )
                lines.append(line)
                reading_order += 1
        return deduplicate_ocr_lines(lines)

    def _run_inference(self, views: Sequence[ImageView]) -> list[Any]:
        if not views:
            return []
        keys = [_view_cache_key(view) for view in views]
        missing_indexes: list[int] = []
        for index, key in enumerate(keys):
            cached = self._output_cache.pop(key, None)
            if cached is None:
                missing_indexes.append(index)
            else:
                self._output_cache[key] = cached
        if missing_indexes:
            missing_views = [views[index] for index in missing_indexes]
            missing_outputs = self._run_engine_inference(missing_views)
            for index, output in zip(missing_indexes, missing_outputs, strict=True):
                self._output_cache[keys[index]] = output
            while len(self._output_cache) > OCR_OUTPUT_CACHE_ENTRIES:
                self._output_cache.popitem(last=False)
        return [self._output_cache[key] for key in keys]

    def _run_engine_inference(self, views: Sequence[ImageView]) -> list[Any]:
        lane_count = min(len(self._engines), len(views))
        if lane_count == 1:
            return [self._engines[0](view.image) for view in views]
        lane_inputs = [
            [(index, views[index]) for index in range(lane, len(views), lane_count)]
            for lane in range(lane_count)
        ]
        with ThreadPoolExecutor(max_workers=lane_count) as executor:
            lane_outputs = executor.map(
                _run_inference_lane,
                self._engines[:lane_count],
                lane_inputs,
            )
        indexed_outputs = [item for lane_output in lane_outputs for item in lane_output]
        return [output for _, output in sorted(indexed_outputs)]


def _view_cache_key(view: ImageView) -> tuple[object, ...]:
    return (
        view.image.shape,
        view.image.dtype.str,
        hashlib.sha256(view.image.tobytes(order="C")).digest(),
    )


def _run_inference_lane(
    engine: Any, indexed_views: Sequence[tuple[int, ImageView]]
) -> list[tuple[int, Any]]:
    return [(index, engine(view.image)) for index, view in indexed_views]


def _initialize_engine(engine_factory: Any, params: dict[str, Any], warmup: Any | None) -> Any:
    engine = engine_factory(params=params)
    if warmup is not None:
        engine(warmup)
    return engine


def _warm_engine(engine: Any, warmup: Any) -> None:
    engine(warmup)


def deduplicate_ocr_lines(lines: list[OcrLine]) -> list[OcrLine]:
    selected: dict[tuple[str, str, int, int], OcrLine] = {}
    for line in lines:
        key = (
            line.panel_id,
            " ".join(line.text.casefold().split()),
            line.polygon[0].x // 12,
            line.polygon[0].y // 12,
        )
        current = selected.get(key)
        if current is None or (line.confidence or 0) > (current.confidence or 0):
            selected[key] = line
    ordered = sorted(
        selected.values(),
        key=lambda item: (
            int(item.panel_id.split("-")[1]),
            min(p.y for p in item.polygon),
            min(p.x for p in item.polygon),
        ),
    )
    return [item.model_copy(update={"reading_order": index}) for index, item in enumerate(ordered)]


def _ink_density(image: np.ndarray[Any, Any], polygon: Any) -> float | None:
    points = np.asarray(polygon, dtype=np.float32)
    x0 = max(0, int(np.floor(points[:, 0].min())))
    y0 = max(0, int(np.floor(points[:, 1].min())))
    x1 = min(image.shape[1], int(np.ceil(points[:, 0].max())) + 1)
    y1 = min(image.shape[0], int(np.ceil(points[:, 1].max())) + 1)
    if x1 <= x0 or y1 <= y0:
        return None
    crop = image[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if crop.ndim == 3 else crop
    gray_values: NDArray[np.float32] = np.asarray(gray, dtype=np.float32)
    lower = float(np.percentile(gray_values, 5))
    upper = float(np.percentile(gray_values, 95))
    if upper - lower < _MIN_LOCAL_CONTRAST:
        return None

    border = np.concatenate(
        (gray_values[0, :], gray_values[-1, :], gray_values[:, 0], gray_values[:, -1])
    )
    background = float(np.median(border))
    midpoint = (lower + upper) / 2
    foreground = gray_values <= midpoint if background >= midpoint else gray_values >= midpoint
    fraction = float(np.mean(foreground))
    if not _MIN_FOREGROUND_FRACTION <= fraction <= _MAX_FOREGROUND_FRACTION:
        return None
    return round(fraction, 5)


def _local_contrast(image: np.ndarray[Any, Any], polygon: Any) -> float | None:
    points = np.asarray(polygon, dtype=np.float32)
    x0 = max(0, int(np.floor(points[:, 0].min())))
    y0 = max(0, int(np.floor(points[:, 1].min())))
    x1 = min(image.shape[1], int(np.ceil(points[:, 0].max())) + 1)
    y1 = min(image.shape[0], int(np.ceil(points[:, 1].max())) + 1)
    if x1 <= x0 or y1 <= y0:
        return None
    crop = image[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if crop.ndim == 3 else crop
    gray_values: NDArray[np.float32] = np.asarray(gray, dtype=np.float32)
    lower = float(np.percentile(gray_values, 5))
    upper = float(np.percentile(gray_values, 95))
    return round((upper - lower) / 255, 5)


def _restore_warning_separator(text: str, image: np.ndarray[Any, Any], polygon: Any) -> str:
    """Restore an OCR-collapsed warning space only when the pixels show a word gap."""

    value = text.strip()
    if _COLLAPSED_WARNING_HEADING.fullmatch(value) is None:
        return text
    if not _has_warning_word_gap(image, polygon):
        return text
    return f"{value[:10]} {value[10:]}"


def _has_warning_word_gap(image: np.ndarray[Any, Any], polygon: Any) -> bool:
    points = np.asarray(polygon, dtype=np.float32)
    x0 = max(0, int(np.floor(points[:, 0].min())))
    y0 = max(0, int(np.floor(points[:, 1].min())))
    x1 = min(image.shape[1], int(np.ceil(points[:, 0].max())) + 1)
    y1 = min(image.shape[0], int(np.ceil(points[:, 1].max())) + 1)
    if x1 <= x0 or y1 <= y0:
        return False
    crop = image[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if crop.ndim == 3 else crop
    gray_values: NDArray[np.float32] = np.asarray(gray, dtype=np.float32)
    lower = float(np.percentile(gray_values, 5))
    upper = float(np.percentile(gray_values, 95))
    if upper - lower < _MIN_LOCAL_CONTRAST:
        return False

    border = np.concatenate(
        (gray_values[0, :], gray_values[-1, :], gray_values[:, 0], gray_values[:, -1])
    )
    background = float(np.median(border))
    midpoint = (lower + upper) / 2
    foreground = gray_values <= midpoint if background >= midpoint else gray_values >= midpoint
    column_fraction = np.mean(foreground, axis=0)
    width = int(column_fraction.shape[0])
    expected_boundary = width * 10 / 17
    search_radius = max(3, round(width * 0.08))
    search_start = max(0, round(expected_boundary) - search_radius)
    search_end = min(width, round(expected_boundary) + search_radius + 1)
    low_ink = column_fraction <= 0.03
    minimum_gap = max(3, round(width * 0.012))
    edge_margin = max(1, round(width * 0.02))
    runs = _true_runs(low_ink, edge_margin, width - edge_margin)
    candidates = [run for run in runs if run[0] < search_end and run[1] >= search_start]
    if not candidates:
        return False
    candidate = max(candidates, key=lambda run: run[2])
    other_longest = max((run[2] for run in runs if run != candidate), default=0)
    dominance_threshold = int(np.ceil(other_longest * 1.5))
    return candidate[2] >= max(minimum_gap, dominance_threshold)


def _true_runs(values: NDArray[np.bool_], start: int, end: int) -> list[tuple[int, int, int]]:
    runs: list[tuple[int, int, int]] = []
    run_start: int | None = None
    for index in range(start, end):
        if values[index] and run_start is None:
            run_start = index
        elif not values[index] and run_start is not None:
            runs.append((run_start, index - 1, index - run_start))
            run_start = None
    if run_start is not None:
        runs.append((run_start, end - 1, end - run_start))
    return runs
