"""Normalize private UAT images to the production upload contract.

The operation preserves aspect ratio and file format. It does not change color,
tone, contrast, sharpness, or label content. Files already within the contract
are not rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from labelverify.contracts.loader import contracts  # noqa: E402

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_INPUT = Path("tests/Test_Images")
DEFAULT_REPORT = Path("test-results/test-image-normalization.json")
SAFETY_PIXEL_TARGET = 11_500_000


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def fitted_size(width: int, height: int, target_pixels: int) -> tuple[int, int]:
    scale = min(1.0, math.sqrt(target_pixels / (width * height)))
    next_width = max(1, math.floor(width * scale))
    next_height = max(1, math.floor(height * scale))
    while next_width * next_height > target_pixels:
        if next_width >= next_height:
            next_width -= 1
        else:
            next_height -= 1
    return next_width, next_height


def encode(image: Image.Image, suffix: str, info: dict[str, Any]) -> bytes:
    output = io.BytesIO()
    common: dict[str, Any] = {}
    if isinstance(info.get("icc_profile"), bytes):
        common["icc_profile"] = info["icc_profile"]
    if isinstance(info.get("dpi"), tuple):
        common["dpi"] = info["dpi"]
    if suffix in {".jpg", ".jpeg"}:
        image.convert("RGB").save(
            output,
            format="JPEG",
            quality=92,
            optimize=True,
            progressive=True,
            subsampling=0,
            **common,
        )
    elif suffix == ".png":
        image.save(output, format="PNG", optimize=True, compress_level=9, **common)
    else:
        image.save(output, format="WEBP", quality=92, method=6, **common)
    return output.getvalue()


def normalize(path: Path, max_pixels: int, max_bytes: int, apply: bool) -> dict[str, Any]:
    original = path.read_bytes()
    with Image.open(io.BytesIO(original)) as source:
        source.load()
        image = ImageOps.exif_transpose(source)
        before_size = image.size
        target_size = (
            fitted_size(*before_size, min(max_pixels, SAFETY_PIXEL_TARGET))
            if before_size[0] * before_size[1] > max_pixels
            else before_size
        )
        changed = target_size != before_size or len(original) > max_bytes
        if not changed:
            normalized = original
        else:
            working = image.resize(target_size, Image.Resampling.LANCZOS)
            normalized = encode(working, path.suffix.casefold(), dict(source.info))
            while len(normalized) > max_bytes:
                next_pixels = math.floor(target_size[0] * target_size[1] * 0.9)
                target_size = fitted_size(*target_size, next_pixels)
                working = image.resize(target_size, Image.Resampling.LANCZOS)
                normalized = encode(working, path.suffix.casefold(), dict(source.info))
    if apply and changed:
        path.write_bytes(normalized)
    return {
        "filename": path.name,
        "changed": changed,
        "before": {
            "width": before_size[0],
            "height": before_size[1],
            "pixels": before_size[0] * before_size[1],
            "bytes": len(original),
            "sha256": sha256_bytes(original),
        },
        "after": {
            "width": target_size[0],
            "height": target_size[1],
            "pixels": target_size[0] * target_size[1],
            "bytes": len(normalized),
            "sha256": sha256_bytes(normalized),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize private LabelVerify UAT images.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    input_root = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    report_path = args.report if args.report.is_absolute() else PROJECT_ROOT / args.report
    if not input_root.is_dir():
        parser.error(f"Input directory does not exist: {input_root}")
    limits = contracts().api["limits"]
    max_pixels = int(limits["pixelsPerImage"])
    max_bytes = int(limits["fileBytes"])
    images = sorted(
        (
            path
            for path in input_root.iterdir()
            if path.is_file() and path.suffix.casefold() in SUPPORTED_EXTENSIONS
        ),
        key=lambda path: path.name.casefold(),
    )
    rows = [normalize(path, max_pixels, max_bytes, args.apply) for path in images]
    report = {
        "schemaVersion": "1.0.0",
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "mode": "apply" if args.apply else "dry-run",
        "input": input_root.name,
        "limits": {
            "maximumDecodedPixelsPerImage": max_pixels,
            "normalizationTargetPixels": min(max_pixels, SAFETY_PIXEL_TARGET),
            "maximumEncodedBytesPerImage": max_bytes,
            "aspectRatioPreserved": True,
            "visualEnhancementsApplied": False,
        },
        "summary": {
            "imageCount": len(rows),
            "changedCount": sum(bool(row["changed"]) for row in rows),
            "unchangedCount": sum(not bool(row["changed"]) for row in rows),
            "pass": all(
                row["after"]["pixels"] <= max_pixels and row["after"]["bytes"] <= max_bytes
                for row in rows
            ),
        },
        "files": rows,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), **report["summary"]}, indent=2))
    return 0 if report["summary"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
