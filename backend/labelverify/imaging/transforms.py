from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import cv2
import numpy as np
from numpy.typing import NDArray

from labelverify.contracts.models import Point
from labelverify.imaging.decode import DecodedPanel


@dataclass(frozen=True)
class ImageView:
    panel_id: str
    image: NDArray[np.uint8]
    source_view: Literal["original", "derived"]
    transform_id: str
    original_width: int
    original_height: int
    scale_x: float
    scale_y: float
    inverse_matrix: NDArray[np.float64] | None = None

    def to_original_polygon(self, polygon: Any) -> list[Point]:
        transformed: NDArray[Any] = np.asarray(
            polygon,
            dtype=np.float64,
        ).reshape(-1, 1, 2)
        if self.inverse_matrix is not None:
            if self.inverse_matrix.shape == (3, 3):
                transformed = cv2.perspectiveTransform(transformed, self.inverse_matrix)
            else:
                transformed = cv2.transform(transformed, self.inverse_matrix)
        points: list[tuple[int, int]] = []
        for raw_x, raw_y in transformed.reshape(-1, 2):
            x = min(self.original_width - 1, max(0, round(float(raw_x) / self.scale_x)))
            y = min(self.original_height - 1, max(0, round(float(raw_y) / self.scale_y)))
            points.append((x, y))
        return normalize_clockwise(points)


def create_ocr_views(panel: DecodedPanel, max_working_pixels: int = 2_073_600) -> list[ImageView]:
    scale = min(1.0, (max_working_pixels / panel.pixels) ** 0.5)
    width = max(1, round(panel.width * scale))
    height = max(1, round(panel.height * scale))
    base_raw = (
        panel.rgb
        if width == panel.width and height == panel.height
        else cv2.resize(panel.rgb, (width, height), interpolation=cv2.INTER_AREA)
    )
    base = np.asarray(base_raw, dtype=np.uint8)
    scale_x = width / panel.width
    scale_y = height / panel.height
    original = ImageView(
        panel.panel_id,
        base,
        "original" if scale == 1.0 else "derived",
        f"transform-{panel.panel_id}-bounded-v1",
        panel.width,
        panel.height,
        scale_x,
        scale_y,
    )
    perspective = _perspective_recovery(base)
    deskew = None if perspective is not None else _deskew_recovery(base)
    recovery = perspective or deskew
    if panel.coverage_state == "Sufficient" and recovery is None:
        return [original]
    recovered_image = recovery[0] if recovery is not None else base
    inverse_matrix = recovery[1] if recovery is not None else None
    transform_name = recovery[2] if recovery is not None else "bounded"
    if panel.coverage_state != "Sufficient":
        gray = cv2.cvtColor(recovered_image, cv2.COLOR_RGB2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
        recovered_image = np.asarray(cv2.cvtColor(clahe, cv2.COLOR_GRAY2RGB), dtype=np.uint8)
        transform_name += "-clahe"
    enhanced = ImageView(
        panel.panel_id,
        recovered_image,
        "derived",
        f"transform-{panel.panel_id}-{transform_name}-v1",
        panel.width,
        panel.height,
        scale_x,
        scale_y,
        inverse_matrix,
    )
    return [original, enhanced]


def create_crop_ocr_view(
    panel: DecodedPanel,
    bounds: tuple[int, int, int, int],
    transform_id: str,
    *,
    rotate_clockwise: bool = False,
    max_side: int = 1440,
) -> ImageView:
    """Create a focused OCR view while preserving original-pixel evidence coordinates."""

    x0, y0, x1, y1 = bounds
    x0 = max(0, min(panel.width - 1, x0))
    y0 = max(0, min(panel.height - 1, y0))
    x1 = max(x0 + 1, min(panel.width, x1))
    y1 = max(y0 + 1, min(panel.height, y1))
    crop = np.asarray(panel.rgb[y0:y1, x0:x1], dtype=np.uint8)
    crop_height, crop_width = crop.shape[:2]
    scale = min(2.0, max_side / max(crop_width, crop_height))
    width = max(1, round(crop_width * scale))
    height = max(1, round(crop_height * scale))
    resized = (
        crop
        if width == crop_width and height == crop_height
        else cv2.resize(
            crop,
            (width, height),
            interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA,
        )
    )
    if rotate_clockwise:
        image = np.asarray(cv2.rotate(resized, cv2.ROTATE_90_CLOCKWISE), dtype=np.uint8)
        inverse = np.asarray(
            [
                [0.0, 1.0 / scale, float(x0)],
                [-1.0 / scale, 0.0, float(y0) + (height - 1) / scale],
            ],
            dtype=np.float64,
        )
    else:
        image = np.asarray(resized, dtype=np.uint8)
        inverse = np.asarray(
            [
                [1.0 / scale, 0.0, float(x0)],
                [0.0, 1.0 / scale, float(y0)],
            ],
            dtype=np.float64,
        )
    return ImageView(
        panel.panel_id,
        image,
        "derived",
        transform_id,
        panel.width,
        panel.height,
        1.0,
        1.0,
        inverse,
    )


def _deskew_recovery(
    image: NDArray[np.uint8],
) -> tuple[NDArray[np.uint8], NDArray[np.float64], str] | None:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 60, 180)
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=max(35, min(image.shape[:2]) // 12),
        minLineLength=max(40, min(image.shape[:2]) // 5),
        maxLineGap=12,
    )
    if lines is None:
        return None
    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        angle = float(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
        while angle <= -45:
            angle += 90
        while angle > 45:
            angle -= 90
        if abs(angle) <= 15:
            angles.append(angle)
    if len(angles) < 2:
        return None
    angle = float(np.median(angles))
    if abs(angle) < 1.5 or abs(angle) > 15:
        return None
    height, width = image.shape[:2]
    center = (width / 2, height / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    cosine = abs(matrix[0, 0])
    sine = abs(matrix[0, 1])
    output_width = int(height * sine + width * cosine)
    output_height = int(height * cosine + width * sine)
    matrix[0, 2] += output_width / 2 - center[0]
    matrix[1, 2] += output_height / 2 - center[1]
    corrected = cv2.warpAffine(
        image,
        matrix,
        (output_width, output_height),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    inverse = np.asarray(cv2.invertAffineTransform(matrix), dtype=np.float64)
    return np.asarray(corrected, dtype=np.uint8), inverse, "deskew"


def _perspective_recovery(
    image: NDArray[np.uint8],
) -> tuple[NDArray[np.uint8], NDArray[np.float64], str] | None:
    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    image_area = float(width * height)
    candidates: list[tuple[float, NDArray[np.float32]]] = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        polygon = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
        area = abs(float(cv2.contourArea(polygon)))
        acceptable_area = image_area * 0.15 <= area <= image_area * 0.90
        if len(polygon) == 4 and cv2.isContourConvex(polygon) and acceptable_area:
            candidates.append((area, polygon.reshape(4, 2).astype(np.float32)))
    if not candidates:
        return None
    points = max(candidates, key=lambda item: item[0])[1]
    ordered = _order_quad(points)
    top = float(np.linalg.norm(ordered[1] - ordered[0]))
    bottom = float(np.linalg.norm(ordered[2] - ordered[3]))
    left = float(np.linalg.norm(ordered[3] - ordered[0]))
    right = float(np.linalg.norm(ordered[2] - ordered[1]))
    width_ratio = abs(top - bottom) / max(top, bottom, 1.0)
    height_ratio = abs(left - right) / max(left, right, 1.0)
    if max(width_ratio, height_ratio) < 0.08:
        return None
    output_width = max(32, round(max(top, bottom)))
    output_height = max(32, round(max(left, right)))
    destination = np.asarray(
        [
            [0, 0],
            [output_width - 1, 0],
            [output_width - 1, output_height - 1],
            [0, output_height - 1],
        ],
        dtype=np.float32,
    )
    matrix = cv2.getPerspectiveTransform(ordered, destination)
    corrected = cv2.warpPerspective(
        image,
        matrix,
        (output_width, output_height),
        flags=cv2.INTER_CUBIC,
    )
    inverse = np.asarray(np.linalg.inv(np.asarray(matrix, dtype=np.float64)), dtype=np.float64)
    return np.asarray(corrected, dtype=np.uint8), inverse, "perspective"


def _order_quad(points: NDArray[np.float32]) -> NDArray[np.float32]:
    ordered = np.empty((4, 2), dtype=np.float32)
    sums = points.sum(axis=1)
    differences = np.diff(points, axis=1).reshape(-1)
    ordered[0] = points[np.argmin(sums)]
    ordered[2] = points[np.argmax(sums)]
    ordered[1] = points[np.argmin(differences)]
    ordered[3] = points[np.argmax(differences)]
    return ordered


def normalize_clockwise(points: list[tuple[int, int]]) -> list[Point]:
    if len(points) != 4:
        raise ValueError("Evidence polygon must contain four points")
    center_x = sum(item[0] for item in points) / 4
    center_y = sum(item[1] for item in points) / 4
    ordered = sorted(
        points,
        key=lambda point: __import__("math").atan2(point[1] - center_y, point[0] - center_x),
    )
    area = sum(
        ordered[index][0] * ordered[(index + 1) % 4][1]
        - ordered[(index + 1) % 4][0] * ordered[index][1]
        for index in range(4)
    )
    if area < 0:
        ordered.reverse()
    start = min(range(4), key=lambda index: (ordered[index][1], ordered[index][0]))
    ordered = ordered[start:] + ordered[:start]
    if abs(area) == 0:
        raise ValueError("Evidence polygon must have non-zero area")
    return [Point(x=x, y=y) for x, y in ordered]
