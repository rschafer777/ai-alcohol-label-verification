"""Run a governed image-layer diagnostic over the Test_Images corpus.

The runner validates file admission, image readability, candidate presence, and
the deterministic warning checks supported by the submitted image. It does not
invent application records and does not claim application-to-label equality.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from labelverify.contracts.loader import contracts  # noqa: E402
from labelverify.domain.warnings import warning_checks  # noqa: E402
from labelverify.extraction.candidates import locate_candidates  # noqa: E402
from labelverify.extraction.rapidocr_adapter import (  # noqa: E402
    RUNTIME_ASSETS,
    RapidOcrAdapter,
)
from labelverify.imaging.decode import (  # noqa: E402
    ImageLimitError,
    InvalidImageError,
    decode_panel,
)
from labelverify.imaging.transforms import create_ocr_views  # noqa: E402
from labelverify.security.signatures import image_media_type  # noqa: E402

DEFAULT_INPUT = Path("tests/Test_Images")
DEFAULT_ORACLE = Path("tests/Test_Images/test-oracle-v1.json")
DEFAULT_JSON_OUTPUT = Path("docs/08-validation/evidence/test-images-validation.json")
DEFAULT_REPORT_OUTPUT = Path("docs/08-validation/TEST_IMAGES_VALIDATION_REPORT.md")
DEFAULT_EXPECTED_COUNT = 50
MAX_CORPUS_IMAGES = 300
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
EXPECTED_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
VALID_ORACLE_DISPOSITIONS = {"PASS", "NEEDS_REVIEW", "DO_NOT_PASS"}
CORE_FIELDS = ("brand", "class_type", "abv", "net_contents", "producer")
WARNING_CHECK_IDS = (
    "warning_wording",
    "warning_heading_uppercase",
    "warning_heading_emphasis",
    "warning_body_not_bold",
    "warning_separation",
    "warning_continuity",
    "warning_contrast",
    "warning_legibility",
)
ORACLE_METADATA_FIELDS = (
    "oracleMethod",
    "reviewerRole",
    "reviewProcedureId",
    "reviewProcedureVersion",
    "reviewedAtUtc",
    "machineOutcomesAvailableDuringReview",
    "amendedAtUtc",
    "amendmentReason",
    "machineOutcomesUsedForClassification",
    "authorityVersion",
    "corpusInventorySha256",
    "corpusUseApproval",
)
PRODUCTION_DEPENDENCIES = (
    Path("backend/labelverify/extraction/candidates.py"),
    Path("backend/labelverify/extraction/rapidocr_adapter.py"),
    Path("backend/labelverify/imaging/decode.py"),
    Path("backend/labelverify/imaging/transforms.py"),
    Path("backend/labelverify/domain/warnings.py"),
    Path("backend/labelverify/security/signatures.py"),
    Path("contracts/api-contract-v1.json"),
    Path("contracts/regulatory-rules-v1.json"),
    Path("contracts/selected-check-registry-v1.json"),
)


class ValidationInputError(ValueError):
    """Raised when the governed corpus or oracle is incomplete or malformed."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.name


def inventory_digest(paths: list[Path], hashes: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.name.casefold()):
        digest.update(f"{path.name}\0{hashes[path.name]}\n".encode())
    return digest.hexdigest()


def discover_images(
    input_root: Path,
    expected_count: int,
    governed_names: set[str] | None = None,
) -> tuple[list[Path], list[str], dict[str, str]]:
    if not input_root.is_dir():
        raise ValidationInputError(f"Input directory does not exist: {input_root}")
    if expected_count < 1 or expected_count > MAX_CORPUS_IMAGES:
        raise ValidationInputError(f"Expected count must be between 1 and {MAX_CORPUS_IMAGES}")
    all_files = sorted(
        (path for path in input_root.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(input_root).as_posix().casefold(),
    )
    nested_images = [
        path
        for path in all_files
        if path.suffix.casefold() in SUPPORTED_EXTENSIONS and path.parent != input_root
    ]
    if nested_images:
        values = ", ".join(path.relative_to(input_root).as_posix() for path in nested_images)
        raise ValidationInputError(f"The governed corpus must be flat: {values}")
    supported_paths = [
        path
        for path in all_files
        if path.parent == input_root and path.suffix.casefold() in SUPPORTED_EXTENSIONS
    ]
    paths = [
        path for path in supported_paths if governed_names is None or path.name in governed_names
    ]
    if governed_names is not None:
        missing = sorted(governed_names - {path.name for path in paths})
        if missing:
            raise ValidationInputError(f"Governed images are missing: {missing}")
    if len(paths) != expected_count:
        raise ValidationInputError(
            f"Expected {expected_count} supported images but found {len(paths)}"
        )
    folded_names = [path.name.casefold() for path in paths]
    if len(folded_names) != len(set(folded_names)):
        raise ValidationInputError("Image filenames must be unique ignoring case")

    file_limit = int(contracts().api["limits"]["fileBytes"])
    hashes: dict[str, str] = {}
    for path in paths:
        if path.stat().st_size > file_limit:
            raise ValidationInputError(f"Image exceeds the encoded size limit: {path.name}")
        with path.open("rb") as handle:
            detected = image_media_type(handle.read(16))
        expected = EXPECTED_MEDIA_TYPES[path.suffix.casefold()]
        if detected != expected:
            raise ValidationInputError(f"Image signature does not match its extension: {path.name}")
        hashes[path.name] = sha256(path)
    ignored = [path.relative_to(input_root).as_posix() for path in all_files if path not in paths]
    return paths, ignored, hashes


def declared_oracle_names(path: Path) -> set[str]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        cases = document["cases"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValidationInputError("Oracle case inventory is unavailable") from exc
    if not isinstance(cases, list):
        raise ValidationInputError("Oracle cases must be an array")
    names = {
        entry.get("filename")
        for entry in cases
        if isinstance(entry, dict) and isinstance(entry.get("filename"), str)
    }
    if len(names) != len(cases):
        raise ValidationInputError("Oracle filenames must be unique strings")
    return names


def load_oracle(
    path: Path,
    image_paths: list[Path],
    image_hashes: dict[str, str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    if not path.is_file():
        raise ValidationInputError(f"Oracle file does not exist: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationInputError("Oracle is not valid UTF-8 JSON") from exc
    if not isinstance(document, dict) or document.get("schemaVersion") != "1.0":
        raise ValidationInputError("Oracle schemaVersion must be 1.0")
    for field in ORACLE_METADATA_FIELDS:
        if field not in document:
            raise ValidationInputError(f"Oracle metadata is missing: {field}")
    string_metadata = set(ORACLE_METADATA_FIELDS) - {
        "machineOutcomesAvailableDuringReview",
        "machineOutcomesUsedForClassification",
    }
    for field in string_metadata:
        if not isinstance(document[field], str) or not document[field].strip():
            raise ValidationInputError(f"Oracle metadata must be a non-empty string: {field}")
    if not isinstance(document["machineOutcomesAvailableDuringReview"], bool):
        raise ValidationInputError(
            "Oracle must state whether machine outcomes were available during review"
        )
    if document["machineOutcomesUsedForClassification"] is not False:
        raise ValidationInputError("Oracle classification must be independent of machine outcomes")
    for timestamp_field in ("reviewedAtUtc", "amendedAtUtc"):
        try:
            timestamp = datetime.fromisoformat(document[timestamp_field].replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValidationInputError(
                f"Oracle {timestamp_field} must be a valid UTC timestamp"
            ) from exc
        if timestamp.tzinfo is None or timestamp.utcoffset() != timedelta(0):
            raise ValidationInputError(f"Oracle {timestamp_field} must be a valid UTC timestamp")
    inventory_value = document["corpusInventorySha256"]
    if len(inventory_value) != 64 or any(
        character not in "0123456789abcdef" for character in inventory_value
    ):
        raise ValidationInputError("Oracle corpus inventory hash must be lowercase SHA-256")
    expected_inventory = inventory_digest(image_paths, image_hashes)
    if document["corpusInventorySha256"] != expected_inventory:
        raise ValidationInputError("Oracle corpus inventory hash does not match the images")

    raw_cases = document.get("cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValidationInputError("Oracle cases must be a non-empty array")
    oracle: dict[str, dict[str, Any]] = {}
    folded: set[str] = set()
    for index, entry in enumerate(raw_cases, start=1):
        if not isinstance(entry, dict):
            raise ValidationInputError(f"Oracle case {index} must be an object")
        filename = entry.get("filename")
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise ValidationInputError(f"Oracle case {index} has an invalid filename")
        folded_name = filename.casefold()
        if folded_name in folded:
            raise ValidationInputError(f"Duplicate oracle filename: {filename}")
        folded.add(folded_name)
        if entry.get("expectedDisposition") not in VALID_ORACLE_DISPOSITIONS:
            raise ValidationInputError(f"Invalid oracle disposition: {filename}")
        if not isinstance(entry.get("reason"), str) or not entry["reason"].strip():
            raise ValidationInputError(f"Oracle reason is missing: {filename}")
        tags = entry.get("scenarioTags")
        if (
            not isinstance(tags, list)
            or not tags
            or not all(isinstance(tag, str) and tag.strip() for tag in tags)
            or len(tags) != len(set(tags))
        ):
            raise ValidationInputError(f"Oracle tags are invalid: {filename}")
        beverage_tags = set(tags) & {"distilled_spirits", "wine", "beer"}
        if len(beverage_tags) > 1:
            raise ValidationInputError(f"Oracle beverage scope is ambiguous: {filename}")
        oracle[filename] = entry

    image_names = {path.name for path in image_paths}
    oracle_names = set(oracle)
    if oracle_names != image_names:
        missing = sorted(image_names - oracle_names)
        extra = sorted(oracle_names - image_names)
        raise ValidationInputError(
            f"Oracle/image bijection failed; missing={missing}, extra={extra}"
        )
    metadata = {field: document[field] for field in ORACLE_METADATA_FIELDS}
    metadata["oracleSha256"] = sha256(path)
    metadata["oraclePath"] = display_path(path)
    return oracle, metadata


def candidate_payload(candidate_set: Any) -> dict[str, Any]:
    value_hashes = [
        hashlib.sha256(candidate.value.encode()).hexdigest()
        for candidate in candidate_set.candidates
    ]
    return {
        "status": candidate_set.status,
        "valueCount": len(candidate_set.candidates),
        "valueSha256": value_hashes,
    }


def warning_payload(check: Any) -> dict[str, Any]:
    return {
        "checkId": check.check_id,
        "label": check.label,
        "applicable": check.applicable,
        "state": check.state,
        "reasonCode": check.reason_code,
        "reasonText": check.reason_text,
    }


def evaluate_harness(
    observed: Any, coverage_state: str
) -> tuple[str, list[str], list[dict[str, Any]]]:
    selected = [
        check
        for check in warning_checks(Decimal("40"), observed.warning)
        if check.check_id in WARNING_CHECK_IDS
    ]
    rows = [warning_payload(check) for check in selected]
    reasons: list[str] = []
    if coverage_state == "Unreadable":
        reasons.append(
            "The image-quality check classified the image as unreadable; "
            "additional evidence is required"
        )
        return "NEEDS_REVIEW", reasons, rows

    missing = [
        field
        for field in CORE_FIELDS
        if observed.field(field).status in {"Not found", "Unreadable"}
    ]
    ambiguous = [field for field in CORE_FIELDS if observed.field(field).status == "Ambiguous"]
    if missing:
        reasons.append("Candidate not found: " + ", ".join(missing))
    if ambiguous:
        reasons.append("Candidate presence is ambiguous: " + ", ".join(ambiguous))

    mismatches = [check for check in rows if check["applicable"] and check["state"] == "Mismatch"]
    uncertain = [
        check
        for check in rows
        if check["applicable"] and check["state"] in {"Review", "Not verified"}
    ]
    if mismatches:
        reasons.extend(f"{check['label']}: {check['reasonText']}" for check in mismatches)
        if coverage_state == "Review":
            reasons.append("The apparent difference is supported by an image that requires review")
            return "NEEDS_REVIEW", reasons, rows
        return "DO_NOT_PASS", reasons, rows
    if missing or ambiguous or uncertain or coverage_state == "Review":
        reasons.extend(f"{check['label']}: {check['reasonText']}" for check in uncertain)
        if coverage_state == "Review":
            reasons.append("The image-quality check requires review")
        return "NEEDS_REVIEW", reasons, rows
    reasons.append("Candidate presence and supported warning checks cleared")
    return "PASS", reasons, rows


def process_image(
    path: Path,
    content_hash: str,
    adapter: RapidOcrAdapter,
) -> dict[str, Any]:
    started = time.perf_counter()
    limits = contracts().api["limits"]
    base: dict[str, Any] = {
        "filename": path.name,
        "relativePath": path.relative_to(PROJECT_ROOT).as_posix(),
        "sha256": content_hash,
        "bytes": path.stat().st_size,
    }
    try:
        panel = decode_panel(path, "panel-1", int(limits["pixelsPerImage"]))
        lines = adapter.extract(create_ocr_views(panel))
        public_panel = panel.public_panel()
        observed = locate_candidates(lines, [public_panel])
        disposition, reasons, warning_rows = evaluate_harness(observed, public_panel.coverage_state)
        base.update(
            {
                "harnessDisposition": disposition,
                "harnessReasons": reasons,
                "durationMs": round((time.perf_counter() - started) * 1000, 3),
                "dimensions": {"width": panel.width, "height": panel.height},
                "quality": public_panel.quality_signals,
                "coverageState": public_panel.coverage_state,
                "ocrLineCount": len(lines),
                "candidates": {
                    field: candidate_payload(observed.field(field))
                    for field in (*CORE_FIELDS, "proof", "country")
                },
                "warningObservation": {
                    "headingDetected": observed.warning.heading is not None,
                    "bodyDetected": observed.warning.body is not None,
                    "headingBold": observed.warning.heading_bold,
                    "bodyBold": observed.warning.body_bold,
                    "separated": observed.warning.separated,
                    "continuous": observed.warning.continuous,
                    "contrastSufficient": observed.warning.contrast_sufficient,
                    "legible": observed.warning.legible,
                },
                "warningChecks": warning_rows,
            }
        )
    except ImageLimitError:
        base.update(
            {
                "harnessDisposition": "NEEDS_REVIEW",
                "harnessReasons": [
                    "The decoded image exceeds the pixel limit and requires replacement"
                ],
                "durationMs": round((time.perf_counter() - started) * 1000, 3),
                "errorCode": "decoded_pixel_limit",
            }
        )
    except InvalidImageError:
        base.update(
            {
                "harnessDisposition": "NEEDS_REVIEW",
                "harnessReasons": [
                    "The file could not be decoded and requires a supported replacement image"
                ],
                "durationMs": round((time.perf_counter() - started) * 1000, 3),
                "errorCode": "invalid_image",
            }
        )
    except Exception as exc:  # pragma: no cover - retained as governed evidence
        base.update(
            {
                "harnessDisposition": "ERROR",
                "harnessReasons": [f"Local diagnostic failed: {type(exc).__name__}"],
                "durationMs": round((time.perf_counter() - started) * 1000, 3),
                "errorCode": "inference_failed",
            }
        )
    return base


def add_oracle(results: list[dict[str, Any]], oracle: dict[str, dict[str, Any]]) -> None:
    for row in results:
        expected = oracle[row["filename"]]
        row["oracleDisposition"] = expected["expectedDisposition"]
        row["oracleReason"] = expected["reason"]
        row["scenarioTags"] = expected["scenarioTags"]
        row["scope"] = "IN_SCOPE_ALL_BEVERAGES"
        expected_disposition = expected["expectedDisposition"]
        harness_disposition = row["harnessDisposition"]
        if expected_disposition == "PASS":
            if harness_disposition == "PASS":
                comparison = "TRUE_CLEAR"
            elif harness_disposition == "DO_NOT_PASS":
                comparison = "FALSE_REJECTION"
            else:
                comparison = "CONSERVATIVE_NON_CLEAR"
        elif harness_disposition == "PASS":
            comparison = "FALSE_CLEAR"
        elif expected_disposition == "NEEDS_REVIEW":
            comparison = (
                "TRUE_REVIEW" if harness_disposition == "NEEDS_REVIEW" else "OVERSTATED_REJECTION"
            )
        else:
            comparison = (
                "TRUE_DEFECT"
                if harness_disposition == "DO_NOT_PASS"
                else "CONSERVATIVE_DEFECT_HOLD"
            )
        row["comparison"] = comparison


def disposition_counts(results: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in results:
        value = str(row[key])
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def percent(numerator: int, denominator: int) -> float | None:
    return round(100 * numerator / denominator, 3) if denominator else None


def performance_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    difficult_tags = {
        "edge",
        "dark_scene",
        "small_text",
        "perspective",
        "side_label",
        "rotated_text",
        "curved_surface",
        "reflective_surface",
        "mixed_scale",
        "warning_contrast",
    }

    def is_difficult(row: dict[str, Any]) -> bool:
        return bool(difficult_tags.intersection(row.get("scenarioTags", [])))

    difficult = [row for row in results if is_difficult(row)]
    clean = [
        row
        for row in results
        if "happy_path" in row.get("scenarioTags", []) and not is_difficult(row)
    ]

    def timings(rows: list[dict[str, Any]], threshold_ms: float) -> dict[str, Any]:
        values = [float(row["durationMs"]) for row in rows]
        within = sum(value <= threshold_ms for value in values)
        return {
            "files": len(values),
            "meanMs": round(sum(values) / len(values), 3) if values else None,
            "maxMs": round(max(values), 3) if values else None,
            "withinTargetCount": within,
            "withinTargetPercent": percent(within, len(values)),
            "targetMs": threshold_ms,
        }

    all_values = [float(row["durationMs"]) for row in results]
    all_mean = round(sum(all_values) / len(all_values), 3) if all_values else None
    clean_rows = timings(clean, 5_000)
    difficult_rows = timings(difficult, 9_000)
    clean_pass = clean_rows["files"] == 0 or (
        clean_rows["withinTargetPercent"] is not None and clean_rows["withinTargetPercent"] >= 75
    )
    difficult_pass = difficult_rows["files"] == 0 or (difficult_rows["withinTargetPercent"] == 100)
    return {
        "acceptanceBands": {
            "normalImageTargetMs": 5_000,
            "difficultRecoverableImageTargetMs": 9_000,
            "batchMeanPerImageTargetMs": 5_000,
            "normalWithinTargetMinimumPercent": 75,
        },
        "allCorpusMeanMs": all_mean,
        "normalImageRows": clean_rows,
        "difficultImageRows": difficult_rows,
        "diagnosticPerformancePass": bool(
            all_mean is not None and all_mean <= 5_000 and clean_pass and difficult_pass
        ),
    }


def subset_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    oracle_counts = disposition_counts(results, "oracleDisposition")
    comparison_counts = disposition_counts(results, "comparison")
    oracle_pass = oracle_counts.get("PASS", 0)
    oracle_defect = oracle_counts.get("DO_NOT_PASS", 0)
    oracle_review = oracle_counts.get("NEEDS_REVIEW", 0)
    true_clear = comparison_counts.get("TRUE_CLEAR", 0)
    true_defect = comparison_counts.get("TRUE_DEFECT", 0)
    defect_hold = comparison_counts.get("CONSERVATIVE_DEFECT_HOLD", 0)
    true_review = comparison_counts.get("TRUE_REVIEW", 0)
    overstated_rejection = comparison_counts.get("OVERSTATED_REJECTION", 0)
    false_clear = comparison_counts.get("FALSE_CLEAR", 0)
    false_rejection = comparison_counts.get("FALSE_REJECTION", 0)
    expected_non_clear = oracle_defect + oracle_review
    contained_non_clear = true_defect + defect_hold + true_review + overstated_rejection
    return {
        "files": len(results),
        "oracleCounts": oracle_counts,
        "harnessCounts": disposition_counts(results, "harnessDisposition"),
        "comparisonCounts": comparison_counts,
        "metrics": {
            "expectedDefectContainmentPercent": percent(true_defect + defect_hold, oracle_defect),
            "expectedReviewContainmentPercent": percent(
                true_review + overstated_rejection, oracle_review
            ),
            "expectedReviewRecognitionPercent": percent(true_review, oracle_review),
            "expectedNonClearContainmentPercent": percent(contained_non_clear, expected_non_clear),
            "expectedClearRecognitionPercent": percent(true_clear, oracle_pass),
            "binaryOracleAlignmentPercent": percent(true_clear + contained_non_clear, len(results)),
            "triStateOracleAlignmentPercent": percent(
                true_clear + true_defect + true_review, len(results)
            ),
            "falseClearCount": false_clear,
            "falseRejectionCount": false_rejection,
            "overstatedRejectionCount": overstated_rejection,
        },
    }


def build_summary(results: list[dict[str, Any]], expected_count: int) -> dict[str, Any]:
    in_scope = [row for row in results if row["scope"] == "IN_SCOPE_ALL_BEVERAGES"]
    exploratory = [row for row in results if row["scope"] != "IN_SCOPE_ALL_BEVERAGES"]
    all_summary = subset_summary(results)
    in_scope_summary = subset_summary(in_scope)
    exploratory_summary = subset_summary(exploratory)
    performance = performance_summary(results)
    evidence_complete = (
        len(results) == expected_count
        and all(row["harnessDisposition"] != "ERROR" for row in results)
        and all(row["comparison"] != "NOT_SCORED" for row in results)
    )
    in_scope_oracle = in_scope_summary["oracleCounts"]
    in_scope_comparisons = in_scope_summary["comparisonCounts"]
    no_false_clear = in_scope_comparisons.get("FALSE_CLEAR", 0) == 0
    no_false_rejection = in_scope_comparisons.get("FALSE_REJECTION", 0) == 0
    expected_defects_contained = in_scope_comparisons.get(
        "TRUE_DEFECT", 0
    ) + in_scope_comparisons.get("CONSERVATIVE_DEFECT_HOLD", 0) == in_scope_oracle.get(
        "DO_NOT_PASS", 0
    )
    expected_reviews_contained = in_scope_comparisons.get(
        "TRUE_REVIEW", 0
    ) + in_scope_comparisons.get("OVERSTATED_REJECTION", 0) == in_scope_oracle.get(
        "NEEDS_REVIEW", 0
    )
    expected_reviews_recognized = in_scope_comparisons.get("TRUE_REVIEW", 0) == in_scope_oracle.get(
        "NEEDS_REVIEW", 0
    )
    expected_clears_recognized = in_scope_comparisons.get("TRUE_CLEAR", 0) == in_scope_oracle.get(
        "PASS", 0
    )
    expected_clear_rows = [row for row in in_scope if row["oracleDisposition"] == "PASS"]
    usable_evidence_rows = [
        row
        for row in expected_clear_rows
        if sum(
            candidate.get("status") not in {"Not found", "Unreadable"}
            for candidate in row.get("candidates", {}).values()
        )
        >= 4
        and row.get("warningObservation", {}).get("headingDetected") is True
        and row.get("warningObservation", {}).get("bodyDetected") is True
    ]
    usable_evidence_percent = percent(len(usable_evidence_rows), len(expected_clear_rows))
    positive_evidence_recognition = (
        usable_evidence_percent is not None and usable_evidence_percent >= 90
    )
    overall = all(
        (
            evidence_complete,
            no_false_clear,
            no_false_rejection,
            expected_defects_contained,
            expected_reviews_contained,
            expected_reviews_recognized,
            positive_evidence_recognition,
            performance["diagnosticPerformancePass"],
        )
    )
    return {
        "filesEvaluated": len(results),
        "allCorpus": all_summary,
        "selectedProfile": in_scope_summary,
        "exploratoryOutOfScope": exploratory_summary,
        "diagnosticPerformance": performance,
        "diagnosticGates": {
            "evidenceCompletePass": evidence_complete,
            "selectedProfileZeroFalseClearPass": no_false_clear,
            "selectedProfileZeroFalseRejectionPass": no_false_rejection,
            "selectedProfileExpectedDefectContainmentPass": expected_defects_contained,
            "selectedProfileExpectedReviewContainmentPass": expected_reviews_contained,
            "selectedProfileExpectedReviewRecognitionPass": expected_reviews_recognized,
            "selectedProfileExpectedClearRecognitionPass": expected_clears_recognized,
            "selectedProfilePositiveEvidenceRecognitionPass": positive_evidence_recognition,
            "selectedProfilePositiveEvidenceRecognitionPercent": usable_evidence_percent,
            "selectedProfilePositiveEvidenceRecognitionCount": len(usable_evidence_rows),
            "selectedProfileExpectedClearCount": len(expected_clear_rows),
            "diagnosticPerformancePass": performance["diagnosticPerformancePass"],
            "overallDiagnosticPass": overall,
            "status": "PASS" if overall else "FAIL",
        },
        "totalDurationMs": round(sum(row["durationMs"] for row in results), 3),
    }


def source_binding(path: Path) -> dict[str, str]:
    return {
        "path": display_path(path),
        "sha256": sha256(path),
    }


def evidence_bindings(oracle_metadata: dict[str, Any]) -> dict[str, Any]:
    model_bindings = []
    for filename, expected_hash in RUNTIME_ASSETS.items():
        path = PROJECT_ROOT / "models" / filename
        actual_hash = sha256(path)
        model_bindings.append(
            {
                "path": path.relative_to(PROJECT_ROOT).as_posix(),
                "sha256": actual_hash,
                "expectedSha256": expected_hash,
                "integrityPass": actual_hash == expected_hash,
            }
        )
    return {
        "validator": source_binding(Path(__file__).resolve()),
        "oracle": {
            "path": oracle_metadata["oraclePath"],
            "sha256": oracle_metadata["oracleSha256"],
        },
        "productionDependencies": [
            source_binding(PROJECT_ROOT / path) for path in PRODUCTION_DEPENDENCIES
        ],
        "modelAssets": model_bindings,
        "modelIntegrityPass": all(row["integrityPass"] for row in model_bindings),
    }


def build_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    all_rows = summary["allCorpus"]
    selected = summary["selectedProfile"]
    exploratory = summary["exploratoryOutOfScope"]
    performance = summary["diagnosticPerformance"]
    gates = summary["diagnosticGates"]
    selected_oracle = selected["oracleCounts"]
    selected_metrics = selected["metrics"]
    selected_defects_withheld = selected["comparisonCounts"].get("TRUE_DEFECT", 0) + selected[
        "comparisonCounts"
    ].get("CONSERVATIVE_DEFECT_HOLD", 0)
    selected_reviews_withheld = selected["comparisonCounts"].get("TRUE_REVIEW", 0) + selected[
        "comparisonCounts"
    ].get("OVERSTATED_REJECTION", 0)
    selected_true_clears = selected["comparisonCounts"].get("TRUE_CLEAR", 0)
    selected_expected_clears = selected_oracle.get("PASS", 0)
    safety_status = (
        "passed"
        if gates["selectedProfileZeroFalseClearPass"]
        and gates["selectedProfileExpectedDefectContainmentPass"]
        and gates["selectedProfileExpectedReviewContainmentPass"]
        else "failed"
    )
    recognition_status = (
        "observed" if gates["selectedProfileExpectedClearRecognitionPass"] else "not observed"
    )

    def metric_percent(value: float | None) -> str:
        return "N/A" if value is None else f"{value}%"

    lines = [
        "# Test Images Validation Report",
        "",
        f"Generated: {payload['generatedAt']}",
        "",
        "## Outcome",
        "",
        f"- Files evaluated: {summary['filesEvaluated']}",
        f"- Visual oracle pass across all files: {all_rows['oracleCounts'].get('PASS', 0)}",
        "- Visual oracle needs review across all files: "
        f"{all_rows['oracleCounts'].get('NEEDS_REVIEW', 0)}",
        "- Visual oracle do not pass across all files: "
        f"{all_rows['oracleCounts'].get('DO_NOT_PASS', 0)}",
        f"- Selected-profile files: {selected['files']}",
        f"- Selected-profile oracle pass: {selected_oracle.get('PASS', 0)}",
        f"- Selected-profile oracle needs review: {selected_oracle.get('NEEDS_REVIEW', 0)}",
        f"- Selected-profile oracle do not pass: {selected_oracle.get('DO_NOT_PASS', 0)}",
        f"- Out-of-scope files: {exploratory['files']}",
        f"- Local image harness pass: {all_rows['harnessCounts'].get('PASS', 0)}",
        f"- Local image harness needs review: {all_rows['harnessCounts'].get('NEEDS_REVIEW', 0)}",
        f"- Local image harness do not pass: {all_rows['harnessCounts'].get('DO_NOT_PASS', 0)}",
        f"- Local image harness errors: {all_rows['harnessCounts'].get('ERROR', 0)}",
        f"- Selected-profile false clearances: {selected_metrics['falseClearCount']}",
        f"- Selected-profile false rejections: {selected_metrics['falseRejectionCount']}",
        "- Selected-profile expected-defect containment: "
        f"{metric_percent(selected_metrics['expectedDefectContainmentPercent'])}",
        "- Selected-profile expected-review recognition: "
        f"{metric_percent(selected_metrics['expectedReviewRecognitionPercent'])}",
        "- Selected-profile expected-clear recognition: "
        f"{metric_percent(selected_metrics['expectedClearRecognitionPercent'])}",
        "- Selected-profile positive evidence recognition: "
        f"{metric_percent(gates['selectedProfilePositiveEvidenceRecognitionPercent'])}",
        f"- Diagnostic gate: {gates['status']}",
        "",
        "## Validation boundary",
        "",
        (
            "This is a partial local image-layer diagnostic. It exercises file admission, "
            "image decoding, preprocessing, RapidOCR, candidate presence, and selected "
            "warning checks. It does not execute the production API, worker supervisor, "
            "reference comparison, 24-check aggregation, browser workflow, or batch queue."
        ),
        "",
        (
            "The folder did not include COLA application records or a batch manifest. "
            "Application-to-label equality and candidate-value correctness are not "
            "tested. Physical warning type size is not verified without reliable scale."
        ),
        "",
        "Beer, wine, and distilled-spirits images are all included in the governed gate.",
        "",
        "## Imperfect-image decision rule",
        "",
        (
            "Angle, curvature, low light, glare, and partial framing are not compliance "
            "defects by themselves. The local pipeline attempts bounded orientation, "
            "perspective, deskew, and contrast recovery while keeping evidence mapped to "
            "the original image. If the visible required evidence is recoverable and has "
            "no identified defect, the visual oracle can pass the image-supported checks."
        ),
        "",
        (
            "If mandatory evidence is truly absent or unreadable, the correct outcome is "
            "NEEDS_REVIEW or an additional-image request, not DO_NOT_PASS and not an "
            "inferred compliance pass. The tool may correct optical distortion and OCR "
            "noise, but it must not invent unseen warning words, capitalization, emphasis, "
            "or application values. DO_NOT_PASS is reserved for a visible deterministic "
            "defect."
        ),
        "",
        "## Performance bands",
        "",
        "- Normal readable-image target: at most 5 seconds for at least 75% of cases",
        "- Difficult recoverable-image target: at most 9 seconds",
        "- Sequential batch mean target: at most 5 seconds per image",
        (f"- Current partial-harness all-corpus mean: {performance['allCorpusMeanMs']} ms"),
        (
            "- Current normal-image results within 5 seconds: "
            f"{performance['normalImageRows']['withinTargetCount']} of "
            f"{performance['normalImageRows']['files']}"
        ),
        (
            "- Current difficult-image results within 9 seconds: "
            f"{performance['difficultImageRows']['withinTargetCount']} of "
            f"{performance['difficultImageRows']['files']}"
        ),
        (
            "These timings cover the partial local image harness, not browser upload, "
            "production orchestration, or network transfer."
        ),
        "",
        "## Diagnostic finding",
        "",
        (
            f"The selected-profile safety containment observation {safety_status}: "
            f"{selected_defects_withheld} of "
            f"{selected_oracle.get('DO_NOT_PASS', 0)} expected defects and "
            f"{selected_reviews_withheld} of "
            f"{selected_oracle.get('NEEDS_REVIEW', 0)} expected review cases were withheld, "
            f"with {selected_metrics['falseClearCount']} false clearances. The selected-"
            f"profile produced {selected_metrics['falseRejectionCount']} false rejections. "
            f"Automatic clear recognition was {recognition_status}: "
            f"{selected_true_clears} of "
            f"{selected_expected_clears} visual-pass cases cleared. This diagnostic "
            "does not require automatic clearance because unscaled physical size and "
            "other human-confirmation checks remain unresolved. It does not establish "
            "full-build safety or application verification."
        ),
        "",
        "## Per-file results",
        "",
        "| File | Scope | Oracle | Local harness | Comparison | Why |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["results"]:
        reasons = row.get("harnessReasons", [])
        local_reason = "; ".join(reasons[:3])
        if len(reasons) > 3:
            local_reason += f"; {len(reasons) - 3} additional findings in JSON evidence"
        combined = (f"Oracle: {row['oracleReason']} Local: {local_reason}").replace("|", "/")
        lines.append(
            f"| {row['filename']} | {row['scope']} | {row['oracleDisposition']} | "
            f"{row['harnessDisposition']} | {row['comparison']} | {combined} |"
        )
    if gates["overallDiagnosticPass"]:
        gate_outcome = (
            "The diagnostic passes its completeness, safety-containment, disposition, "
            "and performance gates. Automatic clear recognition is reported separately "
            "because this partial image layer cannot resolve every human-confirmation check."
        )
    else:
        failures: list[str] = []
        if not gates["evidenceCompletePass"]:
            failures.append("the required evidence set is incomplete")
        if not gates["selectedProfileZeroFalseClearPass"]:
            failures.append("one or more selected-profile cases were falsely cleared")
        if not gates["selectedProfileZeroFalseRejectionPass"]:
            failures.append("one or more selected-profile visual-pass cases were falsely rejected")
        if not gates["selectedProfileExpectedDefectContainmentPass"]:
            failures.append("one or more visible deterministic defects were not contained")
        if not gates["selectedProfileExpectedReviewContainmentPass"]:
            failures.append("one or more oracle review cases were falsely cleared")
        if not gates["selectedProfileExpectedReviewRecognitionPass"]:
            failures.append("one or more oracle review cases received the wrong disposition")
        if not gates["diagnosticPerformancePass"]:
            failures.append("one or more diagnostic performance bands failed")
        gate_outcome = "The diagnostic fails overall because " + "; ".join(failures) + "."
    lines.extend(
        [
            "",
            "## Gate interpretation",
            "",
            gate_outcome,
            "",
            (
                "DO_NOT_PASS is reserved for a visible deterministic defect. OCR, image-"
                "quality, or missing-evidence uncertainty remains NEEDS_REVIEW and is not "
                "asserted as a label defect."
            ),
            "",
            "Machine-readable evidence: `docs/08-validation/evidence/test-images-validation.json`",
            "",
        ]
    )
    return "\n".join(lines)


def build_payload(
    args: argparse.Namespace,
    paths: list[Path],
    ignored_files: list[str],
    image_hashes: dict[str, str],
    oracle_metadata: dict[str, Any],
    adapter: RapidOcrAdapter,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": "2.0",
        "generatedAt": datetime.now(UTC).isoformat(),
        "inputRoot": args.input.as_posix(),
        "corpusInventorySha256": inventory_digest(paths, image_hashes),
        "ignoredUnsupportedFiles": ignored_files,
        "ignoredUnsupportedFileCount": len(ignored_files),
        "modelIdentity": adapter.model_identity,
        "validationBoundary": {
            "harnessType": "partial_local_image_layer_diagnostic",
            "noApplicationRecords": True,
            "applicationToLabelEqualityTested": False,
            "candidateValueCorrectnessTested": False,
            "physicalWarningTypeSizeTested": False,
            "productionApiTested": False,
            "workerSupervisorTested": False,
            "fullTwentyFourCheckPipelineTested": False,
            "networkUsed": False,
        },
        "corpusProvenance": {
            "source": "User-supplied local test corpus",
            "retentionApproval": oracle_metadata["corpusUseApproval"],
            "rawOcrTextPersisted": False,
            "redistributionApproved": False,
        },
        "oracleMetadata": {
            field: oracle_metadata[field]
            for field in (
                "oracleMethod",
                "reviewerRole",
                "reviewProcedureId",
                "reviewProcedureVersion",
                "reviewedAtUtc",
                "machineOutcomesUsedForClassification",
                "authorityVersion",
                "corpusInventorySha256",
                "corpusUseApproval",
                "oracleSha256",
                "oraclePath",
            )
        },
        "evidenceBindings": evidence_bindings(oracle_metadata),
        "summary": build_summary(results, args.expected_count),
        "results": results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--oracle", type=Path, default=DEFAULT_ORACLE)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--expected-count", type=int, default=DEFAULT_EXPECTED_COUNT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        input_root = (PROJECT_ROOT / args.input).resolve()
        oracle_path = (PROJECT_ROOT / args.oracle).resolve()
        governed_names = declared_oracle_names(oracle_path)
        paths, ignored_files, image_hashes = discover_images(
            input_root, args.expected_count, governed_names
        )
        oracle, oracle_metadata = load_oracle(oracle_path, paths, image_hashes)
    except ValidationInputError as exc:
        print(f"VALIDATION_INPUT_ERROR: {exc}", file=sys.stderr)
        return 2

    adapter = RapidOcrAdapter(PROJECT_ROOT / "models", require_read_only=False)
    adapter.initialize()
    results = [process_image(path, image_hashes[path.name], adapter) for path in paths]
    add_oracle(results, oracle)
    payload = build_payload(
        args,
        paths,
        ignored_files,
        image_hashes,
        oracle_metadata,
        adapter,
        results,
    )
    json_output = (PROJECT_ROOT / args.json_output).resolve()
    report_output = (PROJECT_ROOT / args.report_output).resolve()
    json_output.parent.mkdir(parents=True, exist_ok=True)
    report_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report_output.write_text(build_report(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    return 0 if payload["summary"]["diagnosticGates"]["overallDiagnosticPass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
