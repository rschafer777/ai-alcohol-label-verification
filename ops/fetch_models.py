"""Fetch governed OCR models during a controlled build stage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tarfile
import urllib.request
from pathlib import Path, PurePosixPath
from typing import NotRequired, TypedDict, cast


class Artifact(TypedDict):
    role: str
    filename: str
    url: str
    sha256: str
    sourceSha256: NotRequired[str]
    archiveMember: NotRequired[str]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_artifact(artifact: Artifact, target_dir: Path) -> None:
    target = target_dir / artifact["filename"]
    if target.exists() and sha256_file(target) == artifact["sha256"]:
        make_read_only(target)
        return

    source_partial = target.with_suffix(target.suffix + ".source.partial")
    output_partial = target.with_suffix(target.suffix + ".partial")
    source_partial.unlink(missing_ok=True)
    output_partial.unlink(missing_ok=True)
    request = urllib.request.Request(
        artifact["url"],
        headers={"User-Agent": "LabelVerify controlled image build"},
    )
    with (
        urllib.request.urlopen(request, timeout=60) as response,
        source_partial.open("wb") as output,
    ):
        while block := response.read(1024 * 1024):
            output.write(block)

    expected_source_hash = artifact.get("sourceSha256", artifact["sha256"])
    actual_source_hash = sha256_file(source_partial)
    if actual_source_hash != expected_source_hash:
        source_partial.unlink(missing_ok=True)
        raise RuntimeError(
            f"Source hash mismatch for {artifact['filename']}: "
            f"expected {expected_source_hash}, got {actual_source_hash}"
        )

    archive_member = artifact.get("archiveMember")
    if archive_member is None:
        source_partial.replace(output_partial)
    else:
        try:
            _extract_archive_member(source_partial, archive_member, output_partial)
        finally:
            source_partial.unlink(missing_ok=True)

    actual_output_hash = sha256_file(output_partial)
    if actual_output_hash != artifact["sha256"]:
        output_partial.unlink(missing_ok=True)
        raise RuntimeError(
            f"Output hash mismatch for {artifact['filename']}: "
            f"expected {artifact['sha256']}, got {actual_output_hash}"
        )
    output_partial.replace(target)
    make_read_only(target)


def _extract_archive_member(source: Path, member_name: str, output: Path) -> None:
    member_path = PurePosixPath(member_name)
    if member_path.is_absolute() or ".." in member_path.parts:
        raise RuntimeError(f"Unsafe archive member path: {member_name}")
    with tarfile.open(source, mode="r:bz2") as archive:
        try:
            member = archive.getmember(member_name)
        except KeyError as exc:
            raise RuntimeError(f"Archive member is missing: {member_name}") from exc
        if not member.isfile() or member.issym() or member.islnk():
            raise RuntimeError(f"Archive member is not a regular file: {member_name}")
        extracted = archive.extractfile(member)
        if extracted is None:
            raise RuntimeError(f"Archive member cannot be read: {member_name}")
        with extracted, output.open("wb") as destination:
            while block := extracted.read(1024 * 1024):
                destination.write(block)


def make_read_only(path: Path) -> None:
    """Enforce the runtime model-integrity permission contract on POSIX hosts."""

    if os.name != "nt":
        path.chmod(path.stat().st_mode & ~0o222)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target_directory", type=Path)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("ops/model-manifest.json"),
        help="Governed manifest under ops (default: ops/model-manifest.json)",
    )
    return parser.parse_args()


def _resolve_manifest(project_root: Path, requested: Path) -> Path:
    candidate = requested if requested.is_absolute() else project_root / requested
    resolved = candidate.resolve()
    ops_root = (project_root / "ops").resolve()
    if resolved.parent != ops_root:
        raise ValueError("Model manifests must be stored directly under ops")
    return resolved


def main() -> int:
    args = _parse_args()
    project_root = Path(__file__).resolve().parents[1]
    manifest_path = _resolve_manifest(project_root, args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target_dir = args.target_directory.resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    for raw_artifact in manifest["artifacts"]:
        fetch_artifact(cast(Artifact, raw_artifact), target_dir)

    for raw_artifact in manifest["artifacts"]:
        target = target_dir / raw_artifact["filename"]
        print(f"{raw_artifact['sha256']}  {target.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
