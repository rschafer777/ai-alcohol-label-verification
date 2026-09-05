"""Compare governed OCR recognizers on the sealed product holdout.

All candidates use the same PP-OCRv3 English detector, preprocessing, extraction,
deterministic rule engine, and hardware. Only the recognition model and dictionary vary.
"""

from __future__ import annotations

import argparse
import gc
import json
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

from labelverify.extraction.rapidocr_adapter import (  # noqa: E402
    MODEL_ASSETS,
    RapidOcrAdapter,
    RecognizerConfig,
)
from labelverify.orchestration.pipeline import AnalysisJob, execute_analysis  # noqa: E402
from score_ground_truth import prepare_for_upload, score_case  # noqa: E402
from score_product_holdout import sha256, validate_seal  # noqa: E402

WEAK_FIELDS = {"brand", "class", "producer", "country"}
PROTECTED_FIELDS = {"type", "abv", "proof", "net", "warning_found", "wording"}
MODELS: dict[str, RecognizerConfig | None] = {
    "ppocrv4-english": None,
    "ppocrv5-english-mobile": RecognizerConfig(
        filename="en_PP-OCRv5_rec_mobile_infer.onnx",
        sha256="c3461add59bb4323ecba96a492ab75e06dda42467c9e3d0c18db5d1d21924be8",
        lang="en",
        ocr_version="PP-OCRv5",
        keys_filename="ppocrv5_en_dict.txt",
        keys_sha256="e025a66d31f327ba0c232e03f407ae8d105e1e709e7ccb3f408aa778c24e70d6",
    ),
    "ppocrv5-latin-mobile": RecognizerConfig(
        filename="latin_PP-OCRv5_rec_mobile_infer.onnx",
        sha256="b20bd37c168a570f583afbc8cd7925603890efbcdc000a59e22c269d160b5f5a",
        lang="latin",
        ocr_version="PP-OCRv5",
        keys_filename="ppocrv5_latin_dict.txt",
        keys_sha256="3c0a8a79b612653c25f765271714f71281e4e955962c153e272b7b8c1d2b13ff",
    ),
}


def truth_for(
    product: dict[str, Any], source_truth: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    truth = dict(
        source_truth[product["truthFilename"]]
        if product.get("truthFilename")
        else product["truth"]
    )
    truth["beverage_type"] = product["beverageType"]
    return truth


def run_model(
    name: str,
    config: RecognizerConfig | None,
    products: list[dict[str, Any]],
    source_truth: dict[str, dict[str, Any]],
    image_root: Path,
    prepared_root: Path,
) -> dict[str, Any]:
    adapter = RapidOcrAdapter(
        PROJECT_ROOT / "models", require_read_only=False, recognizer=config
    )
    adapter.initialize()
    rows: list[dict[str, Any]] = []
    tally: dict[str, Counter[str]] = defaultdict(Counter)
    for product in products:
        uploads = [
            prepare_for_upload(image_root / filename, prepared_root)[0]
            for filename in product["files"]
        ]
        started = time.perf_counter()
        analysis = execute_analysis(
            AnalysisJob(
                request_id=f"bakeoff-{name}-{product['productId']}",
                build_id="bakeoff",
                panel_paths=tuple(uploads),
            ),
            adapter,
        )
        elapsed = time.perf_counter() - started
        payload = analysis.model_dump(by_alias=True, mode="json")
        verification = payload["verification"]
        scores = score_case(
            {"draft": payload["draft"], "checks": verification["checks"]},
            truth_for(product, source_truth),
        )
        for field, outcome in scores.items():
            if not field.endswith("_note") and outcome != "n/a":
                tally[field][outcome] += 1
        false_clean = verification[
            "summary"
        ] == "No differences found in checked fields" and any(
            outcome not in {"exact", "n/a"}
            for field, outcome in scores.items()
            if not field.endswith("_note")
        )
        rows.append(
            {
                "productId": product["productId"],
                "seconds": round(elapsed, 3),
                "summary": verification["summary"],
                "falseCleanAgainstAnnotatedFields": false_clean,
                "fieldScores": scores,
            }
        )
        print(f"{name:27s} {product['productId']} {elapsed:5.2f}s")
    del adapter
    gc.collect()
    return {
        "modelIdentity": (
            "rapidocr-3.4.2:" + (
                config.sha256 if config else MODEL_ASSETS["en_PP-OCRv4_rec_infer.onnx"]
            )[:12]
        ),
        "recognizerSha256": (
            config.sha256 if config else MODEL_ASSETS["en_PP-OCRv4_rec_infer.onnx"]
        ),
        "fieldTally": {field: dict(counts) for field, counts in sorted(tally.items())},
        "falseCleanCount": sum(row["falseCleanAgainstAnnotatedFields"] for row in rows),
        "meanSeconds": round(sum(row["seconds"] for row in rows) / len(rows), 3),
        "rows": rows,
    }


def compare(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    baseline_rows = {row["productId"]: row for row in baseline["rows"]}
    gains: list[dict[str, str]] = []
    losses: list[dict[str, str]] = []
    protected_regressions: list[dict[str, str]] = []
    for row in candidate["rows"]:
        before = baseline_rows[row["productId"]]["fieldScores"]
        after = row["fieldScores"]
        for field in set(before) & set(after):
            if field.endswith("_note") or before[field] == "n/a" or after[field] == "n/a":
                continue
            change = {
                "productId": row["productId"],
                "field": field,
                "before": before[field],
                "after": after[field],
            }
            if field in WEAK_FIELDS and before[field] != "exact" and after[field] == "exact":
                gains.append(change)
            if field in WEAK_FIELDS and before[field] == "exact" and after[field] != "exact":
                losses.append(change)
            if field in PROTECTED_FIELDS and before[field] == "exact" and after[field] != "exact":
                protected_regressions.append(change)
    gained_families = sorted({item["field"] for item in gains})
    new_false_clean = max(0, candidate["falseCleanCount"] - baseline["falseCleanCount"])
    passes = (
        len(gains) - len(losses) >= 5
        and len(gained_families) >= 2
        and not losses
        and not protected_regressions
        and new_false_clean == 0
    )
    return {
        "weakFieldGains": gains,
        "weakFieldLosses": losses,
        "netWeakFieldGains": len(gains) - len(losses),
        "gainedFieldFamilies": gained_families,
        "protectedFieldRegressions": protected_regressions,
        "newFalseCleanCount": new_false_clean,
        "passesPromotionGate": passes,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        type=Path,
        default=PROJECT_ROOT / "tests/validation/product-holdout-v1.json",
    )
    parser.add_argument(
        "--images", type=Path, default=PROJECT_ROOT / "tests/Test_Images"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "docs/08-validation/evidence/ocr-bakeoff.json",
    )
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    validate_seal(args.manifest, manifest, args.images)
    source_truth = {
        case["filename"]: case
        for case in json.loads(
            (PROJECT_ROOT / manifest["sourceGroundTruth"]).read_text(encoding="utf-8")
        )["cases"]
    }
    prepared_root = Path(tempfile.mkdtemp(prefix="labelverify-bakeoff-"))
    outcomes = {
        name: run_model(
            name,
            config,
            manifest["products"],
            source_truth,
            args.images,
            prepared_root,
        )
        for name, config in MODELS.items()
    }
    baseline = outcomes["ppocrv4-english"]
    comparisons = {
        name: compare(baseline, outcome)
        for name, outcome in outcomes.items()
        if name != "ppocrv4-english"
    }
    promoted = [name for name, value in comparisons.items() if value["passesPromotionGate"]]
    decision = promoted[0] if len(promoted) == 1 else "retain-ppocrv4-english"
    output = {
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "manifestSha256": sha256(args.manifest),
        "candidateModelManifestSha256": sha256(
            PROJECT_ROOT / "ops/model-candidate-manifest.json"
        ),
        "detector": {
            "name": "PP-OCRv3 English detector",
            "sha256": MODEL_ASSETS["en_PP-OCRv3_det_infer.onnx"],
            "sameWeightsAndConfigurationForEveryCandidate": True,
        },
        "controlledVariables": [
            "input products and image bytes",
            "PP-OCRv3 detector weights and configuration",
            "preprocessing and candidate extraction",
            "deterministic rules",
            "hardware and process settings",
        ],
        "methodologyLimitations": [
            "Each recognizer was measured in a separate complete pipeline pass, so detector "
            "weights and configuration were identical but detector output boxes were not replayed.",
            "An identical frozen-box replay is required before a future candidate can be promoted. "
            "It was not run here because both candidates already failed protected-field gates.",
        ],
        "license": "Apache-2.0",
        "modelSource": "RapidAI RapidOCR v3.4.0 model registry derived from PaddleOCR",
        "promotionGate": {
            "minimumNetWeakFieldGains": 5,
            "minimumGainedFieldFamilies": 2,
            "maximumLostCorrectWeakFields": 0,
            "maximumNewFalseClean": 0,
            "maximumProtectedFieldRegressions": 0,
        },
        "comparisons": comparisons,
        "decision": decision,
        "models": outcomes,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"decision": decision, "comparisons": comparisons}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
