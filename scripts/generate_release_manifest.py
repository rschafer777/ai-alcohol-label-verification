"""Generate the deterministic SHA-256 manifest for the public candidate."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
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
    "docs/10-release/FINAL_RT_SIGNOFF.md",
}
NON_REDISTRIBUTABLE_IMAGE_SUFFIXES = {".jpeg", ".jpg", ".png", ".webp"}


def is_excluded(relative: Path, output_relative: str) -> bool:
    relative_text = relative.as_posix()
    if any(part in EXCLUDED_PARTS for part in relative.parts):
        return True
    if relative.suffix.casefold() in EXCLUDED_SUFFIXES:
        return True
    if relative.name.endswith("~"):
        return True
    if relative.name == ".env" or (
        relative.name.startswith(".env.") and relative.name != ".env.example"
    ):
        return True
    if (
        relative.parts[:2] == ("tests", "Test_Images")
        and relative.suffix.casefold() in NON_REDISTRIBUTABLE_IMAGE_SUFFIXES
    ):
        return True
    return relative_text in EXCLUDED_GENERATED_CONFIGS or relative_text == output_relative


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
        if is_excluded(relative, output_relative):
            continue
        selected.append(path)
    return sorted(selected, key=lambda item: item.relative_to(root).as_posix())


def staged_file_hashes(root: Path, output: Path) -> list[tuple[str, str]]:
    """Hash the exact blob bytes in the Git index, not working-tree bytes."""

    output_relative = output.relative_to(root).as_posix()
    listed = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "-z"],
        check=True,
        capture_output=True,
    ).stdout
    entries: list[tuple[str, str]] = []
    for encoded_name in listed.split(b"\0"):
        if not encoded_name:
            continue
        relative_text = encoded_name.decode("utf-8", errors="surrogateescape")
        relative = Path(relative_text)
        if is_excluded(relative, output_relative):
            continue
        staged_bytes = subprocess.run(
            ["git", "-C", str(root), "show", f":{relative_text}"],
            check=True,
            capture_output=True,
        ).stdout
        entries.append((relative.as_posix(), sha256_bytes(staged_bytes)))
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
