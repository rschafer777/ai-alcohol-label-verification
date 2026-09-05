"""Run the sealed 24-product holdout through the production analysis pipeline.

The manifest and ground truth are validation inputs only. Application modules do not
import either source. Products are evaluated as one request with one to three images.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import tempfile
import time
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from labelverify.extraction.rapidocr_adapter import RapidOcrAdapter  # noqa: E402
from labelverify.orchestration.pipeline import AnalysisJob, execute_analysis  # noqa: E402
from score_ground_truth import prepare_for_upload, score_case  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def annotated_deterministic_defects(truth: dict[str, Any]) -> list[str]:
    """Return explicit compliance defects encoded by the independent pixel record.

    Field-extraction disagreement is an OCR utility error, not evidence that the label itself
    is noncompliant. A false-clean safety failure therefore requires a machine-clean summary
    plus an independently annotated deterministic defect on the visible label.
    """

    defects: list[str] = []
    warning = truth.get("warning") or {}
    if warning.get("present") is False:
        defects.append("warning_missing")
    if warning.get("body_matches_statutory_text_exactly") is False:
        defects.append("warning_wording")
    if warning.get("heading_all_caps") is False:
        defects.append("warning_heading_uppercase")
    if warning.get("heading_bold") is False:
        defects.append("warning_heading_emphasis")
    if warning.get("body_bold") is True:
        defects.append("warning_body_not_bold")
    if truth.get("imported") is True and not truth.get("country_of_origin_statement"):
        defects.append("country_of_origin")
    return defects


def validate_seal(manifest_path: Path, manifest: dict[str, Any], image_root: Path) -> None:
    seal_path = manifest_path.with_suffix(".sha256")
    expected_manifest_hash = seal_path.read_text(encoding="utf-8").split()[0].casefold()
    actual_manifest_hash = sha256(manifest_path)
    if actual_manifest_hash != expected_manifest_hash:
        raise SystemExit("Holdout manifest seal does not match")
    truth_path = PROJECT_ROOT / manifest["sourceGroundTruth"]
    if sha256(truth_path) != str(manifest["sourceGroundTruthSha256"]).casefold():
        raise SystemExit("Ground-truth source seal does not match")
    truth_by_name = {
        case["filename"]: case
        for case in json.loads(truth_path.read_text(encoding="utf-8"))["cases"]
    }
    for product in manifest["products"]:
        explicit_hashes = [str(value).casefold() for value in product.get("fileSha256", [])]
        for index, filename in enumerate(product["files"]):
            path = image_root / filename
            if not path.is_file():
                raise SystemExit(f"Holdout image is missing: {filename}")
            if explicit_hashes:
                expected = explicit_hashes[index]
            else:
                expected = str(truth_by_name[product["truthFilename"]]["imageSha256"]).casefold()
            if sha256(path) != expected:
                raise SystemExit(f"Holdout image seal does not match: {filename}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "tests" / "validation" / "product-holdout-v1.json",
    )
    parser.add_argument(
        "--images",
        type=Path,
        default=PROJECT_ROOT / "tests" / "Test_Images",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT
        / "docs"
        / "08-validation"
        / "evidence"
        / "product-holdout-results.json",
    )
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_seal(args.manifest, manifest, args.images)
    truth_path = PROJECT_ROOT / manifest["sourceGroundTruth"]
    source_truth = {
        case["filename"]: case
        for case in json.loads(truth_path.read_text(encoding="utf-8"))["cases"]
    }

    adapter = RapidOcrAdapter(PROJECT_ROOT / "models", require_read_only=False)
    adapter.initialize()
    prepared_root = Path(tempfile.mkdtemp(prefix="labelverify-holdout-"))
    rows: list[dict[str, Any]] = []
    field_tally: dict[str, Counter[str]] = defaultdict(Counter)
    family_tally: dict[str, Counter[str]] = defaultdict(Counter)
    review_causes: Counter[str] = Counter()
    blocking_checks: Counter[str] = Counter()
    seconds: list[float] = []

    for product in manifest["products"]:
        uploads: list[Path] = []
        resized_files: list[str] = []
        for filename in product["files"]:
            upload, resized = prepare_for_upload(args.images / filename, prepared_root)
            uploads.append(upload)
            if resized:
                resized_files.append(filename)
        truth = dict(
            source_truth[product["truthFilename"]]
            if product.get("truthFilename")
            else product["truth"]
        )
        truth["beverage_type"] = product["beverageType"]
        started = time.perf_counter()
        analysis = execute_analysis(
            AnalysisJob(
                request_id=f"holdout-{product['productId']}",
                build_id="holdout",
                panel_paths=tuple(uploads),
            ),
            adapter,
        )
        elapsed = time.perf_counter() - started
        seconds.append(elapsed)
        payload = analysis.model_dump(by_alias=True, mode="json")
        verification = payload["verification"]
        fields = score_case(
            {"draft": payload["draft"], "checks": verification["checks"]}, truth
        )
        eligible = {
            key: value
            for key, value in fields.items()
            if not key.endswith("_note") and value != "n/a"
        }
        exact_count = sum(value == "exact" for value in eligible.values())
        annotated_defects = annotated_deterministic_defects(truth)
        false_clean = (
            verification["summary"] == "No differences found in checked fields"
            and bool(annotated_defects)
        )
        for field, outcome in eligible.items():
            field_tally[field][outcome] += 1
            family_tally[product["beverageType"]][outcome] += 1
        for cause in verification.get("reviewCauses", []):
            review_causes[cause["category"]] += 1
        blocking_checks.update(verification.get("blockingCheckIds", []))
        rows.append(
            {
                "productId": product["productId"],
                "beverageType": product["beverageType"],
                "files": product["files"],
                "resizedForUpload": resized_files,
                "seconds": round(elapsed, 3),
                "machineSummary": verification["summary"],
                "blockingCheckIds": verification.get("blockingCheckIds", []),
                "reviewCauses": verification.get("reviewCauses", []),
                "fieldScores": fields,
                "eligibleFieldCount": len(eligible),
                "exactFieldCount": exact_count,
                "exactFieldRate": round(exact_count / len(eligible), 4) if eligible else None,
                "annotatedDeterministicDefects": annotated_defects,
                "falseCleanAgainstAnnotatedFields": false_clean,
                "observed": payload["draft"],
            }
        )
        print(
            f"{product['productId']} {product['beverageType']:18s} "
            f"{elapsed:5.2f}s {exact_count}/{len(eligible)} exact"
        )

    ordered = sorted(seconds)
    total_eligible = sum(row["eligibleFieldCount"] for row in rows)
    total_exact = sum(row["exactFieldCount"] for row in rows)
    false_clean_count = sum(bool(row["falseCleanAgainstAnnotatedFields"]) for row in rows)
    output = {
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "manifestSha256": sha256(args.manifest),
        "productCount": len(rows),
        "familyProductCounts": dict(Counter(row["beverageType"] for row in rows)),
        "exactFieldCount": total_exact,
        "eligibleFieldCount": total_eligible,
        "exactFieldRate": round(total_exact / total_eligible, 4),
        "falseCleanCount": false_clean_count,
        "utilityDisposition": "accepted-variance-LV-VAR-002",
        "fieldTally": {key: dict(value) for key, value in sorted(field_tally.items())},
        "familyTally": {key: dict(value) for key, value in sorted(family_tally.items())},
        "reviewCauseCounts": dict(review_causes.most_common()),
        "blockingCheckCounts": dict(blocking_checks.most_common()),
        "timing": {
            "meanSeconds": round(statistics.mean(seconds), 3),
            "medianSeconds": round(statistics.median(seconds), 3),
            "p95Seconds": round(ordered[max(0, int(0.95 * len(ordered)) - 1)], 3),
            "maxSeconds": round(max(seconds), 3),
        },
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in output.items() if key != "rows"}, indent=2))
    return 0 if false_clean_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
