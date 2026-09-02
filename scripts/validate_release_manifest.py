"""Verify that the release manifest matches the exact Git index blobs."""

from __future__ import annotations

import argparse
from pathlib import Path

from generate_release_manifest import PROJECT_ROOT, staged_file_hashes

DEFAULT_MANIFEST = Path("docs/10-release/RELEASE_MANIFEST.sha256")


def read_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        digest, separator, relative_path = line.partition("  ")
        if separator != "  " or len(digest) != 64 or not relative_path:
            raise ValueError(f"Invalid manifest entry on line {line_number}")
        if relative_path in entries:
            raise ValueError(f"Duplicate manifest path: {relative_path}")
        entries[relative_path] = digest
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()
    manifest = args.manifest if args.manifest.is_absolute() else PROJECT_ROOT / args.manifest
    expected = read_manifest(manifest)
    actual = {path: digest for path, digest in staged_file_hashes(PROJECT_ROOT, manifest)}
    missing = sorted(actual.keys() - expected.keys())
    extra = sorted(expected.keys() - actual.keys())
    changed = sorted(
        path for path in actual.keys() & expected.keys() if actual[path] != expected[path]
    )
    if missing or extra or changed:
        print({"pass": False, "missing": missing, "extra": extra, "changed": changed})
        return 1
    print({"pass": True, "entries": len(actual)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
