"""Score the production pipeline against the pixel ground truth and the disposition oracle.

This is an evaluation harness only. It runs every supported image in ``tests/Test_Images``
through ``execute_analysis`` exactly as the API does, then compares the label-derived draft
and the government-warning checks with ``pixel-ground-truth-v1.json`` (field values read
from the pixels) and ``test-oracle-v1.json`` (expected dispositions). Nothing in the runtime
imports this module or reads either file.

Usage:
    uv run python scripts/score_ground_truth.py [--input tests/Test_Images] [--output PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from labelverify.extraction.rapidocr_adapter import RapidOcrAdapter  # noqa: E402
from labelverify.orchestration.pipeline import (  # noqa: E402
    AnalysisJob,
    PipelineFailure,
    execute_analysis,
)

_CASE_ONLY = re.compile(r"capital letters|upper ?case|all caps|mixed case", re.I)
SUPPORTED = {".jpg", ".jpeg", ".png", ".webp"}
SUMMARY_TO_DISPOSITION = {
    "No differences found in checked fields": "PASS",
    "Differences detected": "DO_NOT_PASS",
    "Review needed": "NEEDS_REVIEW",
}


def oracle_conflict_reason(
    oracle_case: dict[str, Any] | None, truth: dict[str, Any] | None
) -> str | None:
    """Identify direct contradictions between two independent validation sources."""

    if oracle_case is None or truth is None:
        return None
    reason = str(oracle_case.get("reason") or "").casefold()
    warning = truth.get("warning") or {}
    if "warning body" in reason and "bold" in reason and warning.get("body_bold") is False:
        return "Oracle says the warning body is bold; pixel ground truth says it is not bold"
    if "warning" in reason and "missing" in reason and warning.get("present") is True:
        return "Oracle says the warning is missing; pixel ground truth says it is present"
    if "title case" in reason and warning.get("heading_all_caps") is True:
        return "Oracle says the heading is title case; pixel ground truth says it is all caps"
    return None


def fold(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(re.sub(r"[^\w\s]", " ", str(value).casefold()).split())


def text_match(expected: Any, observed: Any) -> str:
    expected_text, observed_text = fold(expected), fold(observed)
    if not expected_text and not observed_text:
        return "n/a"
    if not expected_text or not observed_text:
        return "miss"
    if expected_text == observed_text:
        return "exact"
    if expected_text in observed_text or observed_text in expected_text:
        return "contain"
    expected_words, observed_words = set(expected_text.split()), set(observed_text.split())
    if expected_words and len(expected_words & observed_words) / len(expected_words) >= 0.6:
        return "partial"
    return "wrong"


def number_match(expected: Any, observed: Any) -> str:
    if expected is None and observed is None:
        return "n/a"
    if expected is None or observed is None:
        return "miss"
    try:
        return "exact" if abs(float(expected) - float(observed)) < 0.01 else "wrong"
    except (TypeError, ValueError):
        return "wrong"


def net_match(expected: str | None, value: float | None, unit: str | None) -> str:
    if not expected and value is None:
        return "n/a"
    if not expected or value is None:
        return "miss"
    match = re.search(r"(\d+(?:\.\d+)?)\s*(ml|l|liter|litre|fl\.?\s*oz|oz)", expected, re.I)
    if not match:
        return "wrong"
    unit_text = re.sub(r"[.\s]", "", match.group(2).lower())
    canonical = {"ml": "mL", "l": "L", "liter": "L", "litre": "L", "floz": "fl oz", "oz": "fl oz"}
    same_unit = canonical.get(unit_text, unit_text) == unit
    return "exact" if abs(float(match.group(1)) - value) < 0.01 and same_unit else "wrong"


def proof_number(text: str | None) -> float | None:
    if not text:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(match.group(1)) if match else None


def score_case(record: dict[str, Any], truth: dict[str, Any]) -> dict[str, str]:
    draft = record["draft"]
    checks = {check["checkId"]: check for check in record["checks"]}
    result: dict[str, str] = {}
    truth_type = truth.get("beverage_type")
    if truth_type == "unknown":
        result["type"] = "n/a"
    elif truth_type == draft["beverageType"]:
        result["type"] = "exact"
    else:
        result["type"] = "miss" if draft["beverageType"] is None else "wrong"
    result["brand"] = text_match(truth.get("brand_name"), draft["brandName"])
    result["class"] = text_match(truth.get("class_type"), draft["classType"])
    result["abv"] = number_match(truth.get("abv_percent"), draft["abvPercent"])
    result["proof"] = number_match(proof_number(truth.get("proof_statement")), draft["proof"])
    result["net"] = net_match(
        truth.get("net_contents"), draft["netContentsValue"], draft["netContentsUnit"]
    )
    result["producer"] = text_match(
        truth.get("producer_name_address"), draft["producerNameAddress"]
    )
    origin = truth.get("country_of_origin_statement")
    country = (
        re.sub(
            r"^(?:product of|produit de|wine of|made in|hecho en|imported from)\s*",
            "",
            str(origin),
            flags=re.I,
        )
        if origin
        else None
    )
    result["country"] = text_match(country, draft["countryOfOrigin"])
    warning = truth.get("warning") or {}
    wording = checks.get("warning_wording", {})
    machine_found = wording.get("reasonCode") not in {
        None,
        "warning_not_found",
        "observed_unreadable",
    }
    if bool(warning.get("present")) == machine_found:
        result["warning_found"] = "exact"
    else:
        result["warning_found"] = "miss" if warning.get("present") else "wrong"
    exact_words = warning.get("body_matches_statutory_text_exactly")
    defects = [str(item) for item in warning.get("wording_defects") or []]
    if exact_words is False and defects and all(_CASE_ONLY.search(item) for item in defects):
        # The ground truth records letter case literally. 27 CFR 16.22 fixes the case of
        # the heading only, so a body set in capitals is compared as its words.
        exact_words = True
        result["wording_note"] = "case_only_defect"
    state = wording.get("state")
    if not warning.get("present") or exact_words is None:
        result["wording"] = "n/a"
    elif exact_words:
        result["wording"] = {
            "Match": "exact",
            "Review": "review",
            "Mismatch": "false_reject",
            "Not verified": "miss",
        }.get(str(state), "other")
    else:
        result["wording"] = {
            "Mismatch": "exact",
            "Review": "review",
            "Match": "false_pass",
            "Not verified": "miss",
        }.get(str(state), "other")
    return result


PIXEL_LIMIT = 12_000_000
PIXEL_HEADROOM = 0.97


def prepare_for_upload(path: Path, prepared_root: Path) -> tuple[Path, bool]:
    """Bring a photograph inside the per-image pixel limit the way the browser does.

    The production path resizes an oversized phone photograph before upload, keeping its
    proportions and landing just under the limit; the harness feeds files directly, so it
    applies the same preparation and records that it did.
    """

    with Image.open(path) as image:
        width, height = image.size
        if width * height <= PIXEL_LIMIT:
            return path, False
        scale = (PIXEL_LIMIT * PIXEL_HEADROOM / (width * height)) ** 0.5
        resized = image.convert("RGB").resize(
            (max(1, int(width * scale)), max(1, int(height * scale))), Image.LANCZOS
        )
    prepared = prepared_root / f"{path.stem}.jpg"
    resized.save(prepared, format="JPEG", quality=92)
    return prepared, True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "tests" / "Test_Images")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "docs" / "08-validation" / "evidence" / "ground-truth-scores.json",
    )
    args = parser.parse_args()
    truth_path = args.input / "pixel-ground-truth-v1.json"
    oracle_path = args.input / "test-oracle-v1.json"
    truths = {
        case["filename"]: case
        for case in json.loads(truth_path.read_text(encoding="utf-8"))["cases"]
    }
    oracle = {
        case["filename"]: case
        for case in json.loads(oracle_path.read_text(encoding="utf-8"))["cases"]
    }
    adapter = RapidOcrAdapter(PROJECT_ROOT / "models", require_read_only=False)
    adapter.initialize()
    files = sorted(
        (path for path in args.input.iterdir() if path.suffix.casefold() in SUPPORTED),
        key=lambda path: path.name.casefold(),
    )
    rows: list[dict[str, Any]] = []
    confusion: dict[str, int] = {}
    tally: dict[str, dict[str, int]] = {}
    seconds: list[float] = []
    prepared_root = Path(tempfile.mkdtemp(prefix="labelverify-score-"))
    for path in files:
        upload, prepared = prepare_for_upload(path, prepared_root)
        started = time.perf_counter()
        try:
            result = execute_analysis(
                AnalysisJob(request_id="score", build_id="score", panel_paths=(upload,)), adapter
            )
        except PipelineFailure as exc:
            # A photograph the production path refuses is recorded, not skipped, so the
            # count of processed images stays honest.
            elapsed = time.perf_counter() - started
            rows.append(
                {
                    "file": path.name,
                    "seconds": round(elapsed, 3),
                    "machineDisposition": "NOT_PROCESSED",
                    "oracleDisposition": (
                        oracle[path.name]["expectedDisposition"] if path.name in oracle else None
                    ),
                    "summary": f"not processed: {exc}",
                    "preparedForUpload": prepared,
                }
            )
            print(f"{path.name[:44]:44s} {elapsed:5.2f}s NOT_PROCESSED {exc}")
            continue
        elapsed = time.perf_counter() - started
        seconds.append(elapsed)
        payload = result.model_dump(by_alias=True, mode="json")
        verification = payload["verification"]
        disposition = (
            "NEEDS_REVIEW"
            if verification["badImage"]
            else SUMMARY_TO_DISPOSITION[verification["summary"]]
        )
        row: dict[str, Any] = {
            "file": path.name,
            "seconds": round(elapsed, 3),
            "machineDisposition": disposition,
            "oracleDisposition": (
                oracle[path.name]["expectedDisposition"] if path.name in oracle else None
            ),
            "summary": verification["summary"],
            "preparedForUpload": prepared,
        }
        if path.name in oracle:
            conflict = oracle_conflict_reason(oracle[path.name], truths.get(path.name))
            if conflict:
                row["oracleExcludedReason"] = conflict
            else:
                key = f"{oracle[path.name]['expectedDisposition']}->{disposition}"
                confusion[key] = confusion.get(key, 0) + 1
        if path.name in truths:
            scores = score_case(
                {"draft": payload["draft"], "checks": verification["checks"]}, truths[path.name]
            )
            row["fields"] = scores
            for field, outcome in scores.items():
                if field.endswith("_note"):
                    continue
                tally.setdefault(field, {})
                tally[field][outcome] = tally[field].get(outcome, 0) + 1
        rows.append(row)
        print(f"{path.name[:44]:44s} {elapsed:5.2f}s {disposition:12s} {row.get('fields', {})}")
    exact = sum(
        count for key, count in confusion.items() if key.split("->")[0] == key.split("->")[1]
    )
    ordered = sorted(seconds)
    summary = {
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "imageCount": len(rows),
        "oracleMatchedCount": sum(confusion.values()),
        "oracleExcludedConflictCount": sum(
            bool(row.get("oracleExcludedReason")) for row in rows
        ),
        "oracleExactAgreement": exact,
        "falseClean": confusion.get("DO_NOT_PASS->PASS", 0),
        "falseReject": confusion.get("PASS->DO_NOT_PASS", 0),
        "confusion": confusion,
        "fieldTally": tally,
        "timing": {
            "meanSeconds": round(statistics.mean(seconds), 3),
            "medianSeconds": round(statistics.median(seconds), 3),
            "p95Seconds": round(ordered[max(0, int(0.95 * len(ordered)) - 1)], 3),
            "maxSeconds": round(max(seconds), 3),
            "overFiveSeconds": sum(value > 5 for value in seconds),
        },
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "rows"}, indent=1))
    return 0 if summary["falseClean"] == 0 and summary["falseReject"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
