from __future__ import annotations

import hashlib
import logging
import os
import re
from collections import OrderedDict
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from difflib import SequenceMatcher
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
# Components shorter than this share of the line extent are dots, commas, and specks.
_LETTER_HEIGHT_FLOOR = 0.3
# Boxes whose heights differ by more than this factor never describe one printed line.
_MAX_HEIGHT_RATIO = 1.8
_MIN_LETTER_COMPONENTS = 3
_MIN_FOREGROUND_FRACTION = 0.02
_MAX_FOREGROUND_FRACTION = 0.65
_COLLAPSED_WARNING_HEADING = re.compile(r"^governmentwarning\s*:$", re.I)

_LOGGER = logging.getLogger(__name__)


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
            "Global.use_cls": False,
            "Det.limit_side_len": 1280,
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
                try:
                    polygon = view.to_original_polygon(box)
                except ValueError:
                    # The detector can return a collapsed box on dense or stretched type;
                    # it carries no readable region and must not fail the whole request.
                    _LOGGER.warning(
                        "dropped a collapsed text box on %s (%r)", view.transform_id, text
                    )
                    continue
                recognized_text = _restore_warning_separator(str(text), view.image, box)
                metrics = text_metrics(view.image, box)
                line = OcrLine(
                    panelId=view.panel_id,
                    text=recognized_text,
                    polygon=polygon,
                    confidence=confidence,
                    readingOrder=reading_order,
                    sourceView=view.source_view,
                    transformId=view.transform_id,
                    inkDensity=metrics.ink_density,
                    localContrast=metrics.local_contrast,
                    strokePx=metrics.stroke_px,
                    inkHeightPx=metrics.ink_height_px,
                    contrastRatio=metrics.contrast_ratio,
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
    """Fuse repeated reads of one physical text region into one line.

    The pipeline reads a panel through several views (bounded original, contrast-enhanced,
    and enlarged crops). Each view returns its own box for the same printed line, often with
    a slightly different transcription, and a crop can also return a fragment of a line that
    was cut by the crop boundary. Region overlap, not text equality, therefore decides what is
    a duplicate: boxes on the same panel that share most of their vertical extent and most of
    the narrower box's width are one region. The fullest confident reading represents the
    region so fragments cannot become extra candidates or duplicate warning sentences.
    """

    if not lines:
        return []
    boxes = [_bounds(line) for line in lines]
    parent = list(range(len(lines)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    # Boxes are visited by panel and top edge, so the inner loop stops at the first box
    # that starts below the current box's bottom edge; nothing after it can overlap.
    order = sorted(range(len(lines)), key=lambda index: (lines[index].panel_id, boxes[index][1]))
    for position, first in enumerate(order):
        for second in order[position + 1 :]:
            if lines[first].panel_id != lines[second].panel_id:
                break
            if boxes[second][1] >= boxes[first][3]:
                break
            if not _same_region(boxes[first], boxes[second]):
                continue
            if lines[first].transform_id == lines[second].transform_id:
                # One view reads a printed line twice only as a duplicate detection whose
                # texts nearly agree ("12 FL. OZ" and "12 FL. 0Z"); overlapping boxes with
                # different texts are distinct lines (a small line inside a tall box).
                if _near_identical_reads(lines[first], lines[second]):
                    parent[find(second)] = find(first)
                continue
            if _compatible_reads(lines[first], lines[second]):
                parent[find(second)] = find(first)

    clusters: dict[int, list[int]] = {}
    for index in range(len(lines)):
        clusters.setdefault(find(index), []).append(index)
    selected = [_fuse_cluster([lines[index] for index in members]) for members in clusters.values()]
    ordered = sorted(
        selected,
        key=lambda item: (
            int(item.panel_id.split("-")[1]),
            min(p.y for p in item.polygon),
            min(p.x for p in item.polygon),
        ),
    )
    return [item.model_copy(update={"reading_order": index}) for index, item in enumerate(ordered)]


def _bounds(line: OcrLine) -> tuple[int, int, int, int]:
    xs = [point.x for point in line.polygon]
    ys = [point.y for point in line.polygon]
    return min(xs), min(ys), max(xs), max(ys)


def _same_region(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> bool:
    first_height = max(1, first[3] - first[1])
    second_height = max(1, second[3] - second[1])
    # Two reads of one printed line have the same line height whatever view they came
    # from; a small box inside a much taller one is a different line (or a whole column of
    # rotated text) and must keep its own place.
    if max(first_height, second_height) > _MAX_HEIGHT_RATIO * min(first_height, second_height):
        return False
    vertical_overlap = max(0, min(first[3], second[3]) - max(first[1], second[1]))
    smaller_height = min(first_height, second_height)
    if vertical_overlap / smaller_height < 0.6:
        return False
    horizontal_overlap = max(0, min(first[2], second[2]) - max(first[0], second[0]))
    smaller_width = max(1, min(first[2] - first[0], second[2] - second[0]))
    return horizontal_overlap / smaller_width >= 0.6


def _near_identical_reads(first: OcrLine, second: OcrLine) -> bool:
    first_text = "".join(character for character in first.text.casefold() if character.isalnum())
    second_text = "".join(character for character in second.text.casefold() if character.isalnum())
    if not first_text or not second_text:
        return False
    return SequenceMatcher(None, first_text, second_text, autojunk=False).ratio() >= 0.8


def _compatible_reads(first: OcrLine, second: OcrLine) -> bool:
    """Whether two overlapping boxes from different views read the same printed text.

    Readings of one line agree on most letters, or one is a fragment of the other. Two
    confident readings with nothing in common are two different lines whose boxes happen
    to overlap, and each keeps its place.
    """

    first_text = "".join(character for character in first.text.casefold() if character.isalnum())
    second_text = "".join(character for character in second.text.casefold() if character.isalnum())
    if not first_text or not second_text:
        return True
    if first_text in second_text or second_text in first_text:
        return True
    ratio = SequenceMatcher(None, first_text, second_text, autojunk=False).ratio()
    if ratio >= 0.4:
        return True
    # A weak reading of the region may be garbage; it merges into the stronger reading
    # only when it is short, so it cannot drag a real line into a different box.
    weak = min((first, second), key=lambda item: item.confidence or 0.0)
    return (weak.confidence or 0.0) < 0.8 and len(weak.text.strip()) <= 12


def _fuse_cluster(members: list[OcrLine]) -> OcrLine:
    if len(members) == 1:
        return members[0]
    widest = max(_bounds(item)[2] - _bounds(item)[0] for item in members)

    def reading_score(item: OcrLine) -> tuple[float, int, int]:
        width = _bounds(item)[2] - _bounds(item)[0]
        letters = sum(character.isalnum() for character in item.text)
        return (
            0.6 * (width / max(1, widest)) + 0.4 * (item.confidence or 0.0),
            letters,
            1 if item.source_view == "original" else 0,
        )

    best = max(members, key=reading_score)
    # Typography metrics come from the reading made at the highest resolution because stroke
    # width and contrast are more reliable with more pixels per character.
    measured = [item for item in members if item.ink_height_px is not None]
    if measured:
        source = max(measured, key=lambda item: item.ink_height_px or 0.0)
        if source is not best:
            best = best.model_copy(
                update={
                    "ink_density": source.ink_density,
                    "local_contrast": source.local_contrast,
                    "stroke_px": source.stroke_px,
                    "ink_height_px": source.ink_height_px,
                    "contrast_ratio": source.contrast_ratio,
                }
            )
    return best


@dataclass(frozen=True)
class TextMetrics:
    ink_density: float | None = None
    local_contrast: float | None = None
    stroke_px: float | None = None
    ink_height_px: float | None = None
    contrast_ratio: float | None = None


def text_metrics(image: np.ndarray[Any, Any], polygon: Any) -> TextMetrics:
    """Measure ink coverage, contrast, and stroke geometry inside one OCR box.

    All values describe the view pixels that OCR actually read. The stroke width is the
    classic area-over-half-perimeter estimate of the mean stroke thickness, and the ink height
    is the letter height of the line (the upper quartile of connected-component heights, which
    tracks the cap or ascender height and ignores dots, commas, and parentheses), so
    ``stroke_px / ink_height_px`` compares type weight independently of scale and letter case.
    The contrast ratio is WCAG relative luminance between the ink core and the surrounding
    background.
    """

    points = np.asarray(polygon, dtype=np.float32)
    x0 = max(0, int(np.floor(points[:, 0].min())))
    y0 = max(0, int(np.floor(points[:, 1].min())))
    x1 = min(image.shape[1], int(np.ceil(points[:, 0].max())) + 1)
    y1 = min(image.shape[0], int(np.ceil(points[:, 1].max())) + 1)
    if x1 <= x0 or y1 <= y0:
        return TextMetrics()
    crop = image[y0:y1, x0:x1]
    gray = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY) if crop.ndim == 3 else crop
    gray_values: NDArray[np.float32] = np.asarray(gray, dtype=np.float32)
    # Thin strokes can cover under five percent of a loose box, so the ink extreme is taken
    # at the second percentile rather than the fifth.
    lower = float(np.percentile(gray_values, 2))
    upper = float(np.percentile(gray_values, 98))
    local_contrast = round((upper - lower) / 255, 5)
    if upper - lower < _MIN_LOCAL_CONTRAST:
        return TextMetrics(local_contrast=local_contrast)

    border = np.concatenate(
        (gray_values[0, :], gray_values[-1, :], gray_values[:, 0], gray_values[:, -1])
    )
    background = float(np.median(border))
    midpoint = (lower + upper) / 2
    dark_ink = background >= midpoint
    foreground = gray_values <= midpoint if dark_ink else gray_values >= midpoint
    fraction = float(np.mean(foreground))
    if not _MIN_FOREGROUND_FRACTION <= fraction <= _MAX_FOREGROUND_FRACTION:
        return TextMetrics(local_contrast=local_contrast)
    mask = foreground.astype(np.uint8)
    ink_height = _letter_height(mask)
    kernel = np.ones((3, 3), dtype=np.uint8)
    eroded = cv2.erode(mask, kernel)
    perimeter = int(np.count_nonzero(mask - eroded))
    stroke = round(2.0 * float(mask.sum()) / perimeter, 3) if perimeter > 0 else None
    core = eroded if int(eroded.sum()) >= 8 else mask
    ink_luminance = _relative_luminance(crop, core > 0)
    background_luminance = _relative_luminance(crop, _background_ring(mask))
    contrast_ratio = None
    if ink_luminance is not None and background_luminance is not None:
        lighter = max(ink_luminance, background_luminance)
        darker = min(ink_luminance, background_luminance)
        contrast_ratio = round(min(21.0, (lighter + 0.05) / (darker + 0.05)), 3)
    return TextMetrics(
        ink_density=round(fraction, 5),
        local_contrast=local_contrast,
        stroke_px=stroke,
        ink_height_px=ink_height,
        contrast_ratio=contrast_ratio,
    )


def _letter_height(mask: NDArray[np.uint8]) -> float | None:
    """Letter height of a text line from its connected components.

    The full ink extent of a line is inflated by parentheses, descenders, and stray marks,
    and a body line that opens with "(1)" would then look lighter than it is. The upper
    quartile of component heights lands on the capitals and ascenders in both all-capital
    and mixed-case text (the shorter x-height letters are the majority in mixed case, but
    never three quarters of a line), while dots, commas, and specks fall below the height
    floor and the rare parenthesis sits above the quartile.
    """

    rows = np.flatnonzero(mask.any(axis=1))
    if rows.size == 0:
        return None
    extent = float(rows.max() - rows.min() + 1)
    count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if count <= 1:
        return extent
    heights = np.asarray(stats[1:, cv2.CC_STAT_HEIGHT], dtype=np.float32)
    letters = heights[heights >= _LETTER_HEIGHT_FLOOR * extent]
    if letters.size < _MIN_LETTER_COMPONENTS:
        return extent
    return float(np.percentile(letters, 75))


def _background_ring(mask: NDArray[np.uint8]) -> NDArray[np.bool_]:
    """Background pixels clear of the anti-aliased ink edge."""

    kernel = np.ones((3, 3), dtype=np.uint8)
    near = cv2.dilate(mask, kernel, iterations=2)
    clear = np.asarray(near == 0, dtype=np.bool_)
    if int(clear.sum()) >= 16:
        return clear
    ring = np.asarray((near > 0) & (mask == 0), dtype=np.bool_)
    if int(ring.sum()) >= 8:
        return ring
    return np.asarray(mask == 0, dtype=np.bool_)


def _relative_luminance(crop: np.ndarray[Any, Any], selection: NDArray[np.bool_]) -> float | None:
    if not bool(selection.any()):
        return None
    pixels = np.asarray(crop[selection], dtype=np.float32) / 255.0
    if pixels.ndim == 1:
        pixels = np.stack([pixels, pixels, pixels], axis=1)
    linear = np.where(pixels <= 0.03928, pixels / 12.92, ((pixels + 0.055) / 1.055) ** 2.4)
    luminance = 0.2126 * linear[:, 0] + 0.7152 * linear[:, 1] + 0.0722 * linear[:, 2]
    return float(np.median(luminance))


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
