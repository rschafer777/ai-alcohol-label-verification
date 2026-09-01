from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.generate_fixture_corpus import generate

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def tree_hashes(root: Path) -> dict[str, str]:
    excluded_roots = {"schema"}
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file() and path.relative_to(root).parts[0] not in excluded_roots
    }


def normalized_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: normalized_json(child)
            for key, child in value.items()
            if key not in {"bytes", "sha256"}
        }
    if isinstance(value, list):
        return [normalized_json(child) for child in value]
    return value


def semantic_inventory(root: Path) -> dict[str, Any]:
    inventory: dict[str, Any] = {}
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file() or path.relative_to(root).parts[0] == "schema":
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix == ".json":
            inventory[relative] = normalized_json(json.loads(path.read_text(encoding="utf-8")))
        elif path.suffix == ".sha256":
            inventory[relative] = [
                line.split("  ", maxsplit=1)[1]
                for line in path.read_text(encoding="ascii").splitlines()
            ]
        else:
            inventory[relative] = path.suffix
    return inventory


def test_generator_reproduces_every_governed_generated_artifact(tmp_path: Path) -> None:
    generated = tmp_path / "run-a" / "fixtures"
    repeated = tmp_path / "run-b" / "fixtures"
    generate(generated, PROJECT_ROOT)
    generate(repeated, PROJECT_ROOT)
    assert tree_hashes(generated) == tree_hashes(repeated)
    assert semantic_inventory(generated) == semantic_inventory(PROJECT_ROOT / "fixtures")
    for path in generated.rglob("*"):
        if path.is_file() and path.suffix in {".json", ".sha256"}:
            assert b"\r\n" not in path.read_bytes(), path
