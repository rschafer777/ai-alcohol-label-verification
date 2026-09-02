from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cv2
import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageOps, UnidentifiedImageError

from labelverify.contracts.models import OriginalDimensions, PanelResult


class InvalidImageError(ValueError):
    """Raised for corrupt or unsupported decoded image content."""


class ImageLimitError(ValueError):
    """Raised when decoded image dimensions exceed the governed limit."""


@dataclass(frozen=True)
class DecodedPanel:
    panel_id: str
    rgb: NDArray[np.uint8]
    width: int
    height: int
    pixels: int
    quality_signals: dict[str, float | bool | str]
    coverage_state: Literal["Sufficient", "Review", "Unreadable"]

    def public_panel(self) -> PanelResult:
        return PanelResult(
            panelId=self.panel_id,
            originalDimensions=OriginalDimensions(width=self.width, height=self.height),
            qualitySignals=self.quality_signals,
            coverageState=self.coverage_state,
        )


def decode_panel(path: Path, panel_id: str, max_pixels: int) -> DecodedPanel:
    try:
        with Image.open(path) as source:
            _validate_dimensions(source.size, max_pixels)
            source.verify()
        with Image.open(path) as source:
            _validate_dimensions(source.size, max_pixels)
            normalized = ImageOps.exif_transpose(source)
            width, height = normalized.size
            pixels = width * height
            normalized.load()
            rgb = np.asarray(normalized.convert("RGB"), dtype=np.uint8).copy()
    except ImageLimitError:
        raise
    except (OSError, UnidentifiedImageError, ValueError) as exc:
        raise InvalidImageError("Image content could not be decoded") from exc

    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    laplacian = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_luma = float(gray.mean())
    dark_fraction = float(np.mean(gray <= 8))
    light_fraction = float(np.mean(gray >= 247))
    clipped_highlight_fraction = float(np.mean(gray >= 252))
    estimated_skew_degrees = _estimated_skew_degrees(np.asarray(gray, dtype=np.uint8))
    coverage: Literal["Sufficient", "Review", "Unreadable"]
    if laplacian < 18.0 or dark_fraction > 0.90 or light_fraction > 0.98:
        coverage = "Unreadable"
    elif (
        laplacian < 55.0
        or dark_fraction > 0.55
        or light_fraction > 0.80
        or abs(estimated_skew_degrees) >= 1.5
    ):
        coverage = "Review"
    else:
        coverage = "Sufficient"
    quality: dict[str, float | bool | str] = {
        "laplacianVariance": round(laplacian, 3),
        "meanLuma": round(mean_luma, 3),
        "darkFraction": round(dark_fraction, 5),
        "lightFraction": round(light_fraction, 5),
        "clippedHighlightFraction": round(clipped_highlight_fraction, 5),
        "estimatedSkewDegrees": round(estimated_skew_degrees, 3),
        "qualityClass": coverage,
    }
    return DecodedPanel(panel_id, rgb, width, height, pixels, quality, coverage)


def _validate_dimensions(dimensions: tuple[int, int], max_pixels: int) -> None:
    width, height = dimensions
    if width <= 0 or height <= 0:
        raise InvalidImageError("Decoded image dimensions are invalid")
    if width * height > max_pixels:
        raise ImageLimitError("Decoded image exceeds the available pixel limit")


def _estimated_skew_degrees(gray: NDArray[np.uint8]) -> float:
    edges = cv2.Canny(gray, 60, 180)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=max(35, min(gray.shape[:2]) // 12),
        minLineLength=max(40, min(gray.shape[:2]) // 5),
        maxLineGap=12,
    )
    if lines is None:
        return 0.0
    angles: list[float] = []
    for x1, y1, x2, y2 in lines[:, 0]:
        angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        while angle <= -45:
            angle += 90
        while angle > 45:
            angle -= 90
        if abs(angle) <= 15:
            angles.append(angle)
    return float(np.median(angles)) if len(angles) >= 2 else 0.0
