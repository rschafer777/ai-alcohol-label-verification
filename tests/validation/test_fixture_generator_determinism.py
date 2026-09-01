from __future__ import annotations

import hashlib
from pathlib import Path

from scripts.generate_fixture_corpus import generate

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def tree_hashes(root: Path) -> dict[str, str]:
    excluded_roots = {"schema"}
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"), key=lambda item: item.as_posix())
        if path.is_file() and path.relative_to(root).parts[0] not in excluded_roots
    }


def test_generator_reproduces_every_governed_generated_artifact(tmp_path: Path) -> None:
    generated = tmp_path / "fixtures"
    generate(generated, PROJECT_ROOT)
    assert tree_hashes(generated) == tree_hashes(PROJECT_ROOT / "fixtures")
