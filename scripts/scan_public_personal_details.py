"""Scan the exact staged public archive using a non-public personal-term list."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tarfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMS_ENV = "LABELVERIFY_PROHIBITED_PERSONAL_TERMS"
DEFAULT_OUTPUT = ROOT / "docs/08-validation/evidence/public-personal-detail-scan.json"


def parse_terms(raw: str | None) -> list[str]:
    if raw is None or not raw.strip():
        raise ValueError(f"{TERMS_ENV} must contain a JSON array of non-empty strings")
    parsed = json.loads(raw)
    if not isinstance(parsed, list) or not parsed:
        raise ValueError(f"{TERMS_ENV} must contain a non-empty JSON array")
    terms: list[str] = []
    seen: set[str] = set()
    for value in parsed:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{TERMS_ENV} entries must be non-empty strings")
        term = value.strip()
        folded = term.casefold()
        if folded not in seen:
            terms.append(term)
            seen.add(folded)
    return terms


def find_matches(text: str, terms: list[str]) -> list[int]:
    matches: list[int] = []
    for index, term in enumerate(terms):
        pattern = re.compile(rf"(?<!\w){re.escape(term)}(?!\w)", re.IGNORECASE)
        if pattern.search(text):
            matches.append(index)
    return matches


def staged_archive() -> tuple[str, bytes]:
    tree = subprocess.run(
        ["git", "write-tree"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    archive = subprocess.run(
        ["git", "archive", "--format=tar", tree], cwd=ROOT, check=True, capture_output=True
    ).stdout
    return tree, archive


def scan_archive(
    archive: bytes, terms: list[str], excluded_paths: set[str]
) -> tuple[int, list[dict[str, object]]]:
    scanned_files = 0
    findings: list[dict[str, object]] = []
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as staged_tree:
        for member in staged_tree.getmembers():
            if not member.isfile() or member.name in excluded_paths:
                continue
            scanned_files += 1
            path_matches = find_matches(member.name, terms)
            if path_matches:
                findings.append(
                    {"path": member.name, "surface": "path", "termIndexes": path_matches}
                )
            extracted = staged_tree.extractfile(member)
            content = extracted.read().decode("utf-8", errors="ignore") if extracted else ""
            content_matches = find_matches(content, terms)
            if content_matches:
                findings.append(
                    {"path": member.name, "surface": "content", "termIndexes": content_matches}
                )
    return scanned_files, findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        terms = parse_terms(os.environ.get(TERMS_ENV))
        tree, archive = staged_archive()
    except (ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 2

    excluded_paths: set[str] = set()
    try:
        relative_output = output.resolve().relative_to(ROOT).as_posix()
        excluded_paths.add(relative_output)
    except ValueError:
        pass
    scanned_files, findings = scan_archive(archive, terms, excluded_paths)
    report = {
        "schemaVersion": "1.0.0",
        "evidenceId": "T-035-B-PUBLIC-PERSONAL-DETAIL-SCAN",
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "sourceTree": tree,
        "termSource": f"non-public environment variable {TERMS_ENV}",
        "termCount": len(terms),
        "scannedFileCount": scanned_files,
        "excludedPaths": sorted(excluded_paths),
        "findingCount": len(findings),
        "findings": findings,
        "pass": not findings,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "sourceTree": tree,
                "termCount": len(terms),
                "scannedFileCount": scanned_files,
                "findingCount": len(findings),
                "pass": not findings,
            }
        )
    )
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
