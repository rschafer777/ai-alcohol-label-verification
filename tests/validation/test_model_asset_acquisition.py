from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path

import pytest
from labelverify.extraction.rapidocr_adapter import RUNTIME_ASSETS

from ops.fetch_models import _extract_archive_member

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
