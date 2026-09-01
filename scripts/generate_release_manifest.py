"""Generate the deterministic SHA-256 manifest for the public candidate."""

from __future__ import annotations

import argparse
import hashlib
import io
import subprocess
import tarfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path("docs/10-release/RELEASE_MANIFEST.sha256")
EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "coverage",
    "dist",
    "frontend-coverage-json",
    "htmlcov",
    "models",
    "node_modules",
    "playwright-report",
    "test-results",
}
EXCLUDED_SUFFIXES = {
    ".bak",
    ".log",
    ".partial",
    ".pyc",
    ".pyo",
    ".swp",
    ".tmp",
    ".tsbuildinfo",
}
EXCLUDED_GENERATED_CONFIGS = {
    ".coverage",
    "AGENTS.md",
    "docs/08-validation/evidence/frontend-coverage-detail.txt",
    "docs/08-validation/evidence/frontend-coverage.txt",
    "docs/08-validation/evidence/python-coverage.json",
    "docs/08-validation/evidence/python-coverage.txt",
    "frontend/vite.config.d.ts",
    "frontend/vite.config.js",
    "frontend/vitest.config.d.ts",
    "frontend/vitest.config.js",
}
NON_REDISTRIBUTABLE_IMAGE_SUFFIXES = {".jpeg", ".jpg", ".png", ".webp"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def included_files(root: Path, output: Path) -> list[Path]:
    output_relative = output.relative_to(root).as_posix()
    selected: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        relative_text = relative.as_posix()
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix.casefold() in EXCLUDED_SUFFIXES:
            continue
        if path.name.endswith("~"):
            continue
        if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
            continue
        if (
            relative.parts[:2] == ("tests", "Test_Images")
            and path.suffix.casefold() in NON_REDISTRIBUTABLE_IMAGE_SUFFIXES
        ):
            continue
        if relative_text in EXCLUDED_GENERATED_CONFIGS or relative_text == output_relative:
            continue
        selected.append(path)
    return sorted(selected, key=lambda item: item.relative_to(root).as_posix())


def staged_file_hashes(root: Path, output: Path) -> list[tuple[str, str]]:
    """Hash the normalized bytes in the Git index, not working-tree bytes."""

    output_relative = output.relative_to(root).as_posix()
    tree = subprocess.run(
        ["git", "-C", str(root), "write-tree"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    archive = subprocess.run(
        ["git", "-C", str(root), "archive", "--format=tar", tree],
        check=True,
        capture_output=True,
    ).stdout
    entries: list[tuple[str, str]] = []
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as staged_tree:
        for member in staged_tree.getmembers():
            if not member.isfile() or member.name == output_relative:
                continue
            extracted = staged_tree.extractfile(member)
            if extracted is None:  # pragma: no cover - tarfile contract guard
                raise RuntimeError(f"Could not read staged file: {member.name}")
            entries.append((member.name, sha256_bytes(extracted.read())))
    return sorted(entries, key=lambda item: item[0])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{digest}  {relative_path}"
        for relative_path, digest in staged_file_hashes(PROJECT_ROOT, output)
    ]
    output.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(lines)} file hashes to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
