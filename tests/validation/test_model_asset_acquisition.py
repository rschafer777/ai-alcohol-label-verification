from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

import pytest
from labelverify.extraction.rapidocr_adapter import RUNTIME_ASSETS

from ops.fetch_models import _extract_archive_member, _resolve_manifest

ROOT = Path(__file__).resolve().parents[2]


def test_font_manifest_matches_the_runtime_integrity_contract() -> None:
    manifest = json.loads((ROOT / "ops/model-manifest.json").read_text(encoding="utf-8"))
    registered_assets = {
        artifact["filename"]: artifact["sha256"] for artifact in manifest["artifacts"]
    }
    font = next(
        artifact
        for artifact in manifest["artifacts"]
        if artifact["role"] == "ocr_visualization_font"
    )

    assert registered_assets == RUNTIME_ASSETS
    assert font["sourceSha256"] == (
        "fa9ca4d13871dd122f61258a80d01751d603b4d3ee14095d65453b4e846e17d7"
    )
    assert font["archiveMember"] == "dejavu-fonts-ttf-2.37/ttf/DejaVuSans.ttf"


def test_controlled_archive_member_extraction_reads_only_the_registered_file(
    tmp_path: Path,
) -> None:
    archive_path = tmp_path / "font.tar.bz2"
    expected = b"registered font bytes"
    member = tarfile.TarInfo("release/ttf/DejaVuSans.ttf")
    member.size = len(expected)
    with tarfile.open(archive_path, mode="w:bz2") as archive:
        archive.addfile(member, io.BytesIO(expected))

    output = tmp_path / "DejaVuSans.ttf.partial"
    _extract_archive_member(archive_path, member.name, output)

    assert output.read_bytes() == expected


def test_controlled_archive_member_extraction_rejects_traversal(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="Unsafe archive member path"):
        _extract_archive_member(tmp_path / "unused.tar.bz2", "../DejaVuSans.ttf", tmp_path / "out")


def test_candidate_manifest_is_governed_but_not_registered_for_runtime() -> None:
    candidate_manifest = json.loads(
        (ROOT / "ops/model-candidate-manifest.json").read_text(encoding="utf-8")
    )

    assert candidate_manifest["purpose"].startswith("Offline evaluation only")
    assert candidate_manifest["license"] == "Apache-2.0"
    assert len(candidate_manifest["artifacts"]) == 4
    assert not set(RUNTIME_ASSETS).intersection(
        artifact["filename"] for artifact in candidate_manifest["artifacts"]
    )


def test_model_manifest_path_must_be_directly_under_ops(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    (project_root / "ops").mkdir(parents=True)

    assert _resolve_manifest(project_root, Path("ops/model-manifest.json")) == (
        project_root / "ops/model-manifest.json"
    ).resolve()
    with pytest.raises(ValueError, match="directly under ops"):
        _resolve_manifest(project_root, Path("outside.json"))
