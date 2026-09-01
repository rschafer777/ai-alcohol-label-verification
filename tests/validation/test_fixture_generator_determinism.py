from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image, ImageFilter, UnidentifiedImageError

from scripts.generate_fixture_corpus import generate
from scripts.validate_fixture_corpus import validate_corpus

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IMAGE_SUFFIXES = {".gif", ".png"}
EXPECTED_METRICS = {
    "totalCases": 30,
    "developmentCases": 24,
    "holdoutCases": 6,
    "selectedChecks": 19,
    "scenarioTags": 50,
    "mutationControls": 8,
}


def tree_hashes(root: Path) -> dict[str, str]:
    excluded_roots = {"schema"}
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file() and path.relative_to(root).parts[0] not in excluded_roots
    }


def normalized_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        path_value = value.get("path")
        is_panel_descriptor = (
            isinstance(path_value, str) and Path(path_value).suffix.lower() in IMAGE_SUFFIXES
        )
        return {
            key: normalized_metadata(child)
            for key, child in value.items()
            if not (is_panel_descriptor and key in {"bytes", "sha256"})
        }
    if isinstance(value, list):
        return [normalized_metadata(child) for child in value]
    return value


def semantic_inventory(root: Path) -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.relative_to(root).parts[0] == "schema":
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix == ".json":
            inventory[relative] = normalized_metadata(json.loads(path.read_text(encoding="utf-8")))
        elif path.suffix == ".sha256":
            inventory[relative] = [
                line.split("  ", maxsplit=1)[1]
                for line in path.read_text(encoding="ascii").splitlines()
            ]
        elif path.suffix.lower() in IMAGE_SUFFIXES:
            inventory[relative] = path.suffix.lower()
        else:
            inventory[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return inventory


def dilated_ink_mask(image: Image.Image) -> NDArray[np.bool_]:
    gray = image.convert("L")
    mask = gray.point(lambda value: 255 if value < 220 else 0)
    return np.asarray(mask.filter(ImageFilter.MaxFilter(5)), dtype=np.uint8) > 0


def assert_raster_content_equivalent(actual_path: Path, expected_path: Path) -> None:
    try:
        with Image.open(actual_path) as actual_source:
            actual_source.load()
            actual_format = actual_source.format
            actual_size = actual_source.size
            actual = actual_source.convert("RGB")
        with Image.open(expected_path) as expected_source:
            expected_source.load()
            expected_format = expected_source.format
            expected_size = expected_source.size
            expected = expected_source.convert("RGB")
    except UnidentifiedImageError:
        assert actual_path.read_bytes() == expected_path.read_bytes()
        return

    assert actual_format == expected_format
    assert actual_size == expected_size
    actual_mask = dilated_ink_mask(actual)
    expected_mask = dilated_ink_mask(expected)
    actual_fraction = float(actual_mask.mean())
    expected_fraction = float(expected_mask.mean())
    fraction_tolerance = max(0.006, expected_fraction * 0.30)
    assert abs(actual_fraction - expected_fraction) <= fraction_tolerance
    union = np.logical_or(actual_mask, expected_mask).sum()
    intersection = np.logical_and(actual_mask, expected_mask).sum()
    assert union > 0
    assert float(intersection / union) >= 0.72


def validate_generated_project(project_root: Path) -> None:
    shutil.copytree(PROJECT_ROOT / "contracts", project_root / "contracts")
    errors, metrics = validate_corpus(project_root)
    assert errors == []
    assert metrics == EXPECTED_METRICS


def test_generator_reproduces_every_governed_generated_artifact(tmp_path: Path) -> None:
    generated_root = tmp_path / "run-a"
    repeated_root = tmp_path / "run-b"
    generated = generated_root / "fixtures"
    repeated = repeated_root / "fixtures"
    generate(generated, PROJECT_ROOT)
    generate(repeated, PROJECT_ROOT)

    assert tree_hashes(generated) == tree_hashes(repeated)
    validate_generated_project(generated_root)
    validate_generated_project(repeated_root)
    assert semantic_inventory(generated) == semantic_inventory(PROJECT_ROOT / "fixtures")

    for path in generated.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".json", ".sha256"}:
            assert b"\r\n" not in path.read_bytes(), path
        if path.suffix.lower() in IMAGE_SUFFIXES:
            relative = path.relative_to(generated)
            assert_raster_content_equivalent(path, PROJECT_ROOT / "fixtures" / relative)

    governed_panel = PROJECT_ROOT / "fixtures/development/cases/D001/panels/panel-1.png"
    with Image.open(governed_panel) as governed_source:
        blank = Image.new("RGB", governed_source.size, governed_source.getpixel((0, 0)))
    blank_path = tmp_path / "blank-panel.png"
    blank.save(blank_path, format="PNG")
    with pytest.raises(AssertionError):
        assert_raster_content_equivalent(blank_path, governed_panel)
