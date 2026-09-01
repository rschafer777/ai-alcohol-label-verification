"""Fetch governed OCR models during a controlled build stage."""

from __future__ import annotations

import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from typing import TypedDict, cast


class Artifact(TypedDict):
    role: str
    filename: str
    url: str
    sha256: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fetch_artifact(artifact: Artifact, target_dir: Path) -> None:
    target = target_dir / artifact["filename"]
    if target.exists() and sha256_file(target) == artifact["sha256"]:
        return

    partial = target.with_suffix(target.suffix + ".partial")
    request = urllib.request.Request(
        artifact["url"],
        headers={"User-Agent": "LabelVerify controlled image build"},
    )
    with urllib.request.urlopen(request, timeout=60) as response, partial.open("wb") as output:
        while block := response.read(1024 * 1024):
            output.write(block)

    actual = sha256_file(partial)
    if actual != artifact["sha256"]:
        partial.unlink(missing_ok=True)
        raise RuntimeError(
            f"Hash mismatch for {artifact['filename']}: expected {artifact['sha256']}, got {actual}"
        )
    partial.replace(target)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python ops/fetch_models.py TARGET_DIRECTORY", file=sys.stderr)
        return 2

    project_root = Path(__file__).resolve().parents[1]
    manifest_path = project_root / "ops" / "model-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    target_dir = Path(sys.argv[1]).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    for raw_artifact in manifest["artifacts"]:
        fetch_artifact(cast(Artifact, raw_artifact), target_dir)

    for raw_artifact in manifest["artifacts"]:
        target = target_dir / raw_artifact["filename"]
        print(f"{raw_artifact['sha256']}  {target.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
