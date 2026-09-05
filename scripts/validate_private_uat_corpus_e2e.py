"""Exercise the private UAT image corpus through production API boundaries.

This validator does not contain product names or expected label values. It
measures admission, decoding, OCR completion, contract integrity, evidence
integrity, server grouping, product-level batch completion, and latency. Field
accuracy requires an independent human oracle and is reported separately.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import platform
import statistics
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from fastapi.testclient import TestClient
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from labelverify.api.app import create_app  # noqa: E402
from labelverify.contracts.loader import contracts  # noqa: E402
from labelverify.contracts.models import AnalysisResult, GroupingImage, GroupingResult  # noqa: E402
from labelverify.orchestration.supervisor import WorkerSupervisor  # noqa: E402
from labelverify.settings.config import Settings  # noqa: E402

SUPPORTED_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
DEFAULT_INPUT = Path("tests/Test_Images")
DEFAULT_OUTPUT = Path("test-results/private-uat-corpus-e2e.json")
DEFAULT_REPORT_OUTPUT = Path("test-results/private-uat-corpus-e2e.md")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def release_source_sha256(path: Path) -> str:
    """Hash source as the LF-normalized bytes published by this repository."""

    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def normalized_thumbnail(path: Path) -> tuple[np.ndarray, float] | None:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None or image.size == 0:
        return None
    height, width = image.shape[:2]
    thumbnail = cv2.resize(image, (64, 64), interpolation=cv2.INTER_AREA).astype(np.float32)
    return thumbnail, width / height


def discover_equivalent_cross_format_pair(images: list[Path]) -> dict[str, Any] | None:
    """Find a content-equivalent pair without using product names or expected values."""
    candidates: list[tuple[float, float, Path, Path]] = []
    thumbnails = {path: normalized_thumbnail(path) for path in images}
    for left_index, left in enumerate(images):
        left_record = thumbnails[left]
        if left_record is None:
            continue
        left_thumbnail, left_ratio = left_record
        for right in images[left_index + 1 :]:
            if left.suffix.casefold() == right.suffix.casefold():
                continue
            right_record = thumbnails[right]
            if right_record is None:
                continue
            right_thumbnail, right_ratio = right_record
            ratio_delta = abs(left_ratio - right_ratio) / max(left_ratio, right_ratio)
            if ratio_delta > 0.002:
                continue
            correlation = float(
                cv2.matchTemplate(left_thumbnail, right_thumbnail, cv2.TM_CCOEFF_NORMED)[0, 0]
            )
            mean_absolute_error = float(np.mean(np.abs(left_thumbnail - right_thumbnail)) / 255.0)
            if correlation >= 0.999 and mean_absolute_error <= 0.025:
                candidates.append((correlation, mean_absolute_error, left, right))
    if not candidates:
        return None
    correlation, mean_absolute_error, left, right = max(
        candidates, key=lambda item: (item[0], -item[1])
    )
    return {
        "paths": [left, right],
        "correlation": round(correlation, 9),
        "normalizedMeanAbsoluteError": round(mean_absolute_error, 9),
    }


def percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * quantile)))
    return round(ordered[index], 3)


def wait_ready(client: TestClient, timeout: float = 30.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if client.get("/health/ready").status_code == 200:
            return True
        time.sleep(0.2)
    return False


def validate_analysis(
    body: dict[str, Any], expected_panels: int
) -> tuple[AnalysisResult, list[str]]:
    failures: list[str] = []
    try:
        result = AnalysisResult.model_validate(body)
    except Exception as exc:
        raise ValueError(f"Analysis contract failed: {type(exc).__name__}: {exc}") from exc
    if len(result.panels) != expected_panels:
        failures.append(f"expected {expected_panels} panels, received {len(result.panels)}")
    if result.verification is None:
        failures.append("verification result missing")
    elif len(result.verification.checks) != 24:
        failures.append(f"expected 24 checks, received {len(result.verification.checks)}")
    evidence_ids = {item.evidence_id for item in result.evidence}
    for field, detected in result.detected.items():
        if detected.evidence_ref is not None and detected.evidence_ref not in evidence_ids:
            failures.append(f"{field} references missing evidence")
    if result.verification is not None:
        for check in result.verification.checks:
            if check.evidence_ref is not None and check.evidence_ref not in evidence_ids:
                failures.append(f"{check.check_id} references missing evidence")
    return result, failures


PIXEL_LIMIT = 12_000_000
PIXEL_HEADROOM = 0.97
RATE_LIMIT_RETRIES = 30


def prepare_for_upload(path: Path, prepared_root: Path) -> Path:
    """Bring a photograph inside the per-image pixel limit the way the browser does.

    The production path resizes an oversized phone photograph before upload, keeping its
    proportions and landing just under the limit; this script posts files directly, so it
    applies the same preparation.
    """

    with Image.open(path) as image:
        width, height = image.size
        if width * height <= PIXEL_LIMIT:
            return path
        scale = (PIXEL_LIMIT * PIXEL_HEADROOM / (width * height)) ** 0.5
        resized = image.convert("RGB").resize(
            (max(1, int(width * scale)), max(1, int(height * scale))), Image.LANCZOS
        )
    prepared = prepared_root / f"{path.stem}.jpg"
    resized.save(prepared, format="JPEG", quality=92)
    return prepared


def post_analysis(client: TestClient, paths: list[Path]) -> tuple[int, dict[str, Any], float]:
    prepared_root = Path(tempfile.mkdtemp(prefix="labelverify-uat-"))
    uploads = [prepare_for_upload(path, prepared_root) for path in paths]
    files = [
        (
            "panels",
            (upload.name, upload.read_bytes(), SUPPORTED_TYPES[upload.suffix.casefold()]),
        )
        for upload in uploads
    ]
    started = time.perf_counter()
    response = client.post("/api/v1/analyses?persist=false", files=files)
    # The API meters each client; a governed run waits out the limit rather than counting
    # a metered refusal as a processing failure. The wait is not processing time.
    for _attempt in range(RATE_LIMIT_RETRIES):
        if response.status_code != 429:
            break
        retry_after = response.headers.get("Retry-After")
        time.sleep(float(retry_after) if retry_after else 2.0)
        started = time.perf_counter()
        response = client.post("/api/v1/analyses?persist=false", files=files)
    elapsed = round(time.perf_counter() - started, 3)
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = {"nonJsonBody": response.text[:200]}
    return response.status_code, body, elapsed


def analysis_record(
    client: TestClient, case_id: str, paths: list[Path]
) -> tuple[dict[str, Any], AnalysisResult | None]:
    status, body, elapsed = post_analysis(client, paths)
    failures: list[str] = []
    result: AnalysisResult | None = None
    if status != 200:
        failures.append(f"HTTP {status}: {body.get('code', 'unknown error')}")
    else:
        try:
            result, failures = validate_analysis(body, len(paths))
        except ValueError as exc:
            failures.append(str(exc))
    record: dict[str, Any] = {
        "caseId": case_id,
        "files": [path.name for path in paths],
        "durationSeconds": elapsed,
        "httpStatus": status,
        "pass": not failures,
        "failures": failures,
    }
    if result is not None:
        record["observed"] = {
            "beverageType": result.draft.beverage_type,
            "brandName": result.draft.brand_name,
            "classType": result.draft.class_type,
            "abvPercent": result.draft.abv_percent,
            "proof": result.draft.proof,
            "netContentsValue": result.draft.net_contents_value,
            "netContentsUnit": result.draft.net_contents_unit,
            "producerNameAddress": result.draft.producer_name_address,
            "countryOfOrigin": result.draft.country_of_origin,
            "detectedFieldCount": sum(
                detected.status in {"Found", "Ambiguous"} for detected in result.detected.values()
            ),
            "evidenceRegionCount": len(result.evidence),
            "machineSummary": result.verification.summary if result.verification else None,
        }
    return record, result


def performance_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    values = [float(record["durationSeconds"]) for record in records]
    return {
        "count": len(values),
        "averageSeconds": round(statistics.fmean(values), 3) if values else 0.0,
        "medianSeconds": round(statistics.median(values), 3) if values else 0.0,
        "p95Seconds": percentile(values, 0.95),
        "maximumSeconds": round(max(values), 3) if values else 0.0,
        "targetAverageSeconds": 5.0,
        "hardCaseMaximumSeconds": 9.0,
        "averageTargetMet": bool(values) and statistics.fmean(values) <= 5.0,
        "hardCaseTargetMet": bool(values) and max(values) <= 9.0,
    }


def _public_artifacts(
    record: dict[str, Any], input_root: Path
) -> list[dict[str, str]]:
    existing = record.get("fileArtifacts")
    if isinstance(existing, list):
        return [dict(item) for item in existing if isinstance(item, dict)]
    artifacts: list[dict[str, str]] = []
    for value in record.get("files", []):
        path = input_root / str(value)
        artifact: dict[str, str] = {"extension": path.suffix.casefold()}
        if path.is_file():
            artifact["sha256"] = sha256(path)
        artifacts.append(artifact)
    return artifacts


def _public_observed(observed: dict[str, Any]) -> dict[str, Any]:
    """Retain technical outcomes without publishing private-image OCR text."""

    return {
        "beverageType": observed.get("beverageType"),
        "brandRead": bool(observed.get("brandName")) or bool(observed.get("brandRead")),
        "classTypeRead": bool(observed.get("classType"))
        or bool(observed.get("classTypeRead")),
        "abvPercent": observed.get("abvPercent"),
        "proof": observed.get("proof"),
        "netContentsValue": observed.get("netContentsValue"),
        "netContentsUnit": observed.get("netContentsUnit"),
        "producerNameAddressRead": bool(observed.get("producerNameAddress"))
        or bool(observed.get("producerNameAddressRead")),
        "countryOfOriginRead": bool(observed.get("countryOfOrigin"))
        or bool(observed.get("countryOfOriginRead")),
        "detectedFieldCount": observed.get("detectedFieldCount"),
        "evidenceRegionCount": observed.get("evidenceRegionCount"),
        "machineSummary": observed.get("machineSummary"),
    }


def public_evidence(report: dict[str, Any], input_root: Path) -> dict[str, Any]:
    """Data-minimize evidence before it enters the public repository."""

    sanitized = copy.deepcopy(report)
    scope = sanitized.get("scope", {})
    skipped = scope.pop("skippedFiles", [])
    if skipped:
        scope["skippedFileExtensions"] = sorted(
            {Path(str(value)).suffix.casefold() for value in skipped}
        )
    failures = sanitized.get("preflightFailures", [])
    if failures:
        sanitized["preflightFailures"] = [
            "An admitted image exceeded the governed byte limit" for _ in failures
        ]

    equivalent = sanitized.get("equivalentPanelIntegration", {})
    if isinstance(equivalent, dict):
        equivalent["fileArtifacts"] = _public_artifacts(equivalent, input_root)
        equivalent.pop("files", None)

    for collection_name in ("individualScans", "productScans"):
        records = sanitized.get(collection_name, [])
        for record in records:
            record["fileArtifacts"] = _public_artifacts(record, input_root)
            record.pop("files", None)
            record.pop("suggestedName", None)
            observed = record.get("observed")
            if isinstance(observed, dict):
                record["observed"] = _public_observed(observed)

    grouping = sanitized.get("grouping", {})
    if isinstance(grouping, dict):
        for group in grouping.get("groups", []):
            if isinstance(group, dict):
                group.pop("suggestedName", None)
    return sanitized


def markdown_cell(value: Any) -> str:
    if value is None or value == "":
        return "Not read"
    return str(value).replace("|", "/").replace("\n", " ")


def write_markdown_report(report: dict[str, Any], output: Path) -> None:
    scope = report["scope"]
    summary = report.get("summary", {})
    individual = report.get("performance", {}).get("individual", {})
    products = report.get("performance", {}).get("products", {})
    equivalent = report.get("equivalentPanelIntegration", {})
    lines = [
        "# Private UAT Corpus API and Batch Report",
        "",
        f"Generated: {report['createdAtUtc']}",
        "",
        "## Outcome",
        "",
        f"- Selected files: {scope['selectedFileCount']}",
        f"- Accepted images: {scope['acceptedImageCount']}",
        f"- Skipped non-images: {scope['skippedNonImageCount']}",
        f"- Individual API processing passes: {summary.get('individualPassCount', 0)}",
        f"- Individual API processing failures: {summary.get('individualFailCount', 0)}",
        f"- Grouped product API processing passes: {summary.get('productPassCount', 0)}",
        f"- Grouped product API processing failures: {summary.get('productFailCount', 0)}",
        f"- Suggested product groups: {report.get('grouping', {}).get('groupCount', 0)}",
        (
            "- Maximum images in a group: "
            f"{report.get('grouping', {}).get('maximumImagesPerGroup', 0)}"
        ),
        f"- Functional gate: {'PASS' if summary.get('functionalPass') else 'FAIL'}",
        f"- Performance gate: {'PASS' if summary.get('performancePass') else 'FAIL'}",
        f"- Complete gate: {'PASS' if report.get('pass') else 'FAIL'}",
        (
            "- Equivalent cross-format panel integration: "
            f"{'PASS' if equivalent.get('pass') else 'FAIL'}"
        ),
        "",
        "## Performance",
        "",
        "| Scope | Average | Median | P95 | Maximum | Average target | Hard-case target |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
        (
            f"| Individual images | {individual.get('averageSeconds', 0):.3f} s | "
            f"{individual.get('medianSeconds', 0):.3f} s | "
            f"{individual.get('p95Seconds', 0):.3f} s | "
            f"{individual.get('maximumSeconds', 0):.3f} s | "
            f"{'PASS' if individual.get('averageTargetMet') else 'FAIL'} | "
            f"{'PASS' if individual.get('hardCaseTargetMet') else 'FAIL'} |"
        ),
        (
            f"| Grouped products | {products.get('averageSeconds', 0):.3f} s | "
            f"{products.get('medianSeconds', 0):.3f} s | "
            f"{products.get('p95Seconds', 0):.3f} s | "
            f"{products.get('maximumSeconds', 0):.3f} s | "
            f"{'PASS' if products.get('averageTargetMet') else 'FAIL'} | "
            f"{'PASS' if products.get('hardCaseTargetMet') else 'FAIL'} |"
        ),
        "",
        "## Equivalent cross-format panel integration",
        "",
        (
            "A content-only scan selected two visually equivalent files with different "
            "encodings. The first analysis request after fresh application readiness "
            f"returned HTTP {equivalent.get('httpStatus', 'Not run')} in "
            f"{float(equivalent.get('durationSeconds', 0)):.3f} seconds, retained "
            f"{equivalent.get('returnedPanelCount', 0)} panel records, and recorded "
            f"{len(equivalent.get('duplicateLinks', []))} duplicate link. Worker generation "
            f"was {equivalent.get('workerGenerationBefore', 'unknown')} before and "
            f"{equivalent.get('workerGenerationAfter', 'unknown')} after the request."
        ),
        "",
        "## Accuracy boundary",
        "",
        (
            "This run proves admission, decode, OCR completion, 24-check contract integrity, "
            "original-pixel evidence integrity, grouping, product reruns, and latency through "
            "the production multipart API. It does not turn label-derived text into an "
            "independent application record."
        ),
        "",
        (
            f"The local oracle contains {scope['governedOracleCaseCount']} cases. "
            f"Exactly {scope['governedOracleExactMatchCount']} current filenames match it, "
            f"{scope['unscoredCurrentImageCount']} current images are not covered, and "
            f"{scope['missingGovernedOracleImageCount']} oracle filenames are absent. "
            "A complete current-corpus human oracle is therefore required before claiming "
            "field-level or legal-label accuracy for the current corpus."
        ),
        "",
        "## Per-image production API results",
        "",
        (
            "| Case | Artifact | API | Time | Type | Brand read | Class read | ABV | Proof | "
            "Net contents | Producer read | Origin read | Machine finding |"
        ),
        "| --- | --- | ---: | ---: | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
    ]
    for record in report.get("individualScans", []):
        observed = record.get("observed", {})
        net_value = observed.get("netContentsValue")
        net_unit = observed.get("netContentsUnit")
        net = "Not read" if net_value is None else f"{net_value:g} {net_unit or ''}".strip()
        lines.append(
            "| "
            + " | ".join(
                [
                    markdown_cell(record.get("caseId")),
                    markdown_cell(
                        str(record.get("fileArtifacts", [{}])[0].get("sha256", ""))[:12]
                    ),
                    markdown_cell(record.get("httpStatus")),
                    f"{float(record.get('durationSeconds', 0)):.3f} s",
                    markdown_cell(observed.get("beverageType")),
                    "Yes" if observed.get("brandRead") else "No",
                    "Yes" if observed.get("classTypeRead") else "No",
                    markdown_cell(observed.get("abvPercent")),
                    markdown_cell(observed.get("proof")),
                    markdown_cell(net),
                    "Yes" if observed.get("producerNameAddressRead") else "No",
                    "Yes" if observed.get("countryOfOriginRead") else "No",
                    markdown_cell(observed.get("machineSummary")),
                ]
            )
            + " |"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def runtime_settings(temporary_root: Path) -> Settings:
    return Settings(
        runtime_mode="direct",
        allowed_host=None,
        model_root=PROJECT_ROOT / "models",
        spool_root=temporary_root / "spool",
        sample_manifest=PROJECT_ROOT / "fixtures" / "sample" / "sample-manifest-v1.json",
        static_root=PROJECT_ROOT / "frontend" / "dist",
        build_id="private-uat-corpus-e2e",
        client_identity_source="direct",
        history_root=temporary_root / "history",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the private UAT image corpus.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--skip-product-runs", action="store_true")
    parser.add_argument(
        "--sanitize-existing",
        action="store_true",
        help="Data-minimize an existing evidence file without rerunning OCR.",
    )
    args = parser.parse_args()

    input_root = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    report_output = (
        args.report_output
        if args.report_output.is_absolute()
        else PROJECT_ROOT / args.report_output
    )
    if args.sanitize_existing:
        report = json.loads(output.read_text(encoding="utf-8"))
        sanitized = public_evidence(report, input_root)
        output.write_text(
            json.dumps(sanitized, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        write_markdown_report(sanitized, report_output)
        print(json.dumps({"output": str(output), "sanitized": True}))
        return 0
    all_files = sorted(
        (path for path in input_root.iterdir() if path.is_file()),
        key=lambda path: path.name.casefold(),
    )
    images = [path for path in all_files if path.suffix.casefold() in SUPPORTED_TYPES]
    skipped = [path.name for path in all_files if path.suffix.casefold() not in SUPPORTED_TYPES]
    image_names = {path.name.casefold() for path in images}
    oracle_path = input_root / "test-oracle-v1.json"
    oracle_cases: list[dict[str, Any]] = []
    if oracle_path.is_file():
        oracle_body = json.loads(oracle_path.read_text(encoding="utf-8-sig"))
        oracle_cases = list(oracle_body.get("cases", []))
    oracle_names = {
        str(case.get("filename", "")).casefold() for case in oracle_cases if case.get("filename")
    }
    matched_oracle_names = oracle_names & image_names
    equivalent_pair = discover_equivalent_cross_format_pair(images)
    limits = contracts().api["limits"]
    preflight_failures = [
        f"{path.name} exceeds {limits['fileBytes']} bytes"
        for path in images
        if path.stat().st_size > int(limits["fileBytes"])
    ]
    report: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "snapshot": {
            "validatorSha256": release_source_sha256(Path(__file__)),
            "pipelineSha256": release_source_sha256(
                PROJECT_ROOT / "backend" / "labelverify" / "orchestration" / "pipeline.py"
            ),
            "supervisorSha256": release_source_sha256(
                PROJECT_ROOT / "backend" / "labelverify" / "orchestration" / "supervisor.py"
            ),
        },
        "scope": {
            "input": input_root.name,
            "selectedFileCount": len(all_files),
            "acceptedImageCount": len(images),
            "skippedNonImageCount": len(skipped),
            "skippedFiles": skipped,
            "productSpecificRuntimeOverrides": False,
            "independentFieldOracleAvailableForCompleteCorpus": (
                bool(oracle_names) and oracle_names == image_names
            ),
            "governedOracleCaseCount": len(oracle_names),
            "governedOracleExactMatchCount": len(matched_oracle_names),
            "unscoredCurrentImageCount": len(image_names - matched_oracle_names),
            "missingGovernedOracleImageCount": len(oracle_names - image_names),
        },
        "preflightFailures": preflight_failures,
        "equivalentPanelIntegration": {},
        "individualScans": [],
        "grouping": {},
        "productScans": [],
        "pass": False,
    }
    if preflight_failures or not images:
        output.parent.mkdir(parents=True, exist_ok=True)
        sanitized = public_evidence(report, input_root)
        output.write_text(json.dumps(sanitized, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"output": str(output), "pass": False, "errors": preflight_failures}))
        return 1

    rows: list[GroupingImage] = []
    result_by_id: dict[str, AnalysisResult] = {}
    with tempfile.TemporaryDirectory(prefix="labelverify-private-uat-") as temporary:
        temporary_root = Path(temporary)
        supervisor = WorkerSupervisor(
            PROJECT_ROOT / "models",
            worker_deadline_seconds=float(limits["workerDeadlineSeconds"]),
            build_id="private-uat-corpus-e2e",
        )
        app = create_app(settings=runtime_settings(temporary_root), supervisor=supervisor)
        with TestClient(app, client=("127.0.0.1", 50100)) as client:
            equivalent_failures: list[str] = []
            if equivalent_pair is None:
                equivalent_failures.append(
                    "no visually equivalent cross-format pair met the production thresholds"
                )
                report["equivalentPanelIntegration"] = {
                    "selectionPolicy": (
                        "content-only comparison across different encodings using the "
                        "production aspect-ratio, correlation, and normalized-error thresholds"
                    ),
                    "pass": False,
                    "failures": equivalent_failures,
                }
            else:
                equivalent_paths = list(equivalent_pair["paths"])
                before = supervisor.snapshot()
                status, body, elapsed = post_analysis(client, equivalent_paths)
                after = supervisor.snapshot()
                result: AnalysisResult | None = None
                if status != 200:
                    equivalent_failures.append(
                        f"HTTP {status}: {body.get('code', 'unknown error')}"
                    )
                else:
                    try:
                        result, contract_failures = validate_analysis(body, len(equivalent_paths))
                        equivalent_failures.extend(contract_failures)
                    except ValueError as exc:
                        equivalent_failures.append(str(exc))
                duplicate_links: list[dict[str, str]] = []
                returned_panel_ids: list[str] = []
                if result is not None:
                    returned_panel_ids = [panel.panel_id for panel in result.panels]
                    for panel in result.panels:
                        duplicate_of = panel.quality_signals.get("duplicateOfPanelId")
                        if isinstance(duplicate_of, str):
                            duplicate_links.append(
                                {"panelId": panel.panel_id, "duplicateOfPanelId": duplicate_of}
                            )
                if len(returned_panel_ids) != 2:
                    equivalent_failures.append("both submitted panel records were not retained")
                if len(duplicate_links) != 1:
                    equivalent_failures.append("exactly one duplicate panel link was not returned")
                if before.generation != after.generation:
                    equivalent_failures.append("OCR worker generation changed during the request")
                if after.restarts != before.restarts:
                    equivalent_failures.append("OCR worker restarted during the request")
                if elapsed > 9.0:
                    equivalent_failures.append("request exceeded the 9-second hard-case ceiling")
                report["equivalentPanelIntegration"] = {
                    "selectionPolicy": (
                        "content-only comparison across different encodings using the "
                        "production aspect-ratio, correlation, and normalized-error thresholds"
                    ),
                    "files": [path.name for path in equivalent_paths],
                    "fileSha256": [sha256(path) for path in equivalent_paths],
                    "correlation": equivalent_pair["correlation"],
                    "normalizedMeanAbsoluteError": equivalent_pair["normalizedMeanAbsoluteError"],
                    "durationSeconds": elapsed,
                    "httpStatus": status,
                    "submittedPanelCount": 2,
                    "returnedPanelCount": len(returned_panel_ids),
                    "returnedPanelIds": returned_panel_ids,
                    "duplicateLinks": duplicate_links,
                    "workerGenerationBefore": before.generation,
                    "workerGenerationAfter": after.generation,
                    "workerRestartsBefore": before.restarts,
                    "workerRestartsAfter": after.restarts,
                    "pass": not equivalent_failures,
                    "failures": equivalent_failures,
                }
                marker = "PASS" if not equivalent_failures else "FAIL"
                print(
                    f"equivalent panels {marker} {elapsed:.3f} s "
                    f"generation {before.generation}->{after.generation}",
                    flush=True,
                )
            for index, path in enumerate(images, start=1):
                case_id = f"image-{index:03d}"
                record, result = analysis_record(client, case_id, [path])
                report["individualScans"].append(record)
                if result is not None:
                    result_by_id[case_id] = result
                rows.append(
                    GroupingImage(
                        imageId=case_id,
                        fileName=path.name,
                        path=path.name,
                        brandName=result.draft.brand_name if result else None,
                        classType=result.draft.class_type if result else None,
                        beverageType=result.draft.beverage_type if result else None,
                        typeConfidence=(
                            result.beverage_inference.confidence
                            if result and result.beverage_inference
                            else None
                        ),
                        failed=result is None,
                    )
                )
                marker = "PASS" if record["pass"] else "FAIL"
                print(
                    f"individual {index}/{len(images)} {path.name} {marker} "
                    f"{record['durationSeconds']:.3f} s",
                    flush=True,
                )
                if not supervisor.ready and not wait_ready(client):
                    break

            grouping_response = client.post(
                "/api/v1/grouping-suggestions",
                json={"images": [row.model_dump(by_alias=True, mode="json") for row in rows]},
            )
            grouping_failures: list[str] = []
            grouping: GroupingResult | None = None
            if grouping_response.status_code != 200:
                grouping_failures.append(f"HTTP {grouping_response.status_code}")
            else:
                try:
                    grouping = GroupingResult.model_validate(grouping_response.json())
                except Exception as exc:
                    grouping_failures.append(
                        f"Grouping contract failed: {type(exc).__name__}: {exc}"
                    )
            successful_ids = set(result_by_id)
            if grouping is not None:
                grouped_ids = [
                    panel_id for group in grouping.groups for panel_id in group.panel_ids
                ]
                if len(grouped_ids) != len(set(grouped_ids)):
                    grouping_failures.append("an image appears in more than one group")
                if set(grouped_ids) != successful_ids:
                    grouping_failures.append("group membership does not match successful images")
                if any(len(group.panel_ids) > 3 for group in grouping.groups):
                    grouping_failures.append("a group exceeds three images")
            report["grouping"] = {
                "httpStatus": grouping_response.status_code,
                "groupCount": len(grouping.groups) if grouping else 0,
                "readyToConfirmCount": (
                    sum(group.status == "ready_to_confirm" for group in grouping.groups)
                    if grouping
                    else 0
                ),
                "needsReviewCount": (
                    sum(group.status == "needs_review" for group in grouping.groups)
                    if grouping
                    else 0
                ),
                "maximumImagesPerGroup": (
                    max((len(group.panel_ids) for group in grouping.groups), default=0)
                    if grouping
                    else 0
                ),
                "pass": not grouping_failures,
                "failures": grouping_failures,
                "groups": (
                    [group.model_dump(by_alias=True, mode="json") for group in grouping.groups]
                    if grouping
                    else []
                ),
            }
            if grouping is not None and not args.skip_product_runs:
                paths_by_id = {f"image-{index:03d}": path for index, path in enumerate(images, 1)}
                for index, group in enumerate(grouping.groups, start=1):
                    paths = [paths_by_id[panel_id] for panel_id in group.panel_ids]
                    record, _ = analysis_record(client, f"product-{index:03d}", paths)
                    record["suggestedName"] = group.suggested_name
                    report["productScans"].append(record)
                    marker = "PASS" if record["pass"] else "FAIL"
                    print(
                        f"product {index}/{len(grouping.groups)} {marker} "
                        f"{record['durationSeconds']:.3f} s",
                        flush=True,
                    )
                    if not supervisor.ready and not wait_ready(client):
                        break

    individual_records = report["individualScans"]
    product_records = report["productScans"]
    report["performance"] = {
        "individual": performance_summary(individual_records),
        "products": performance_summary(product_records),
    }
    performance_pass = bool(
        report["performance"]["individual"]["averageTargetMet"]
        and report["performance"]["individual"]["hardCaseTargetMet"]
        and bool(report["equivalentPanelIntegration"].get("pass"))
        and (
            args.skip_product_runs
            or (
                report["performance"]["products"]["averageTargetMet"]
                and report["performance"]["products"]["hardCaseTargetMet"]
            )
        )
    )
    functional_pass = (
        len(individual_records) == len(images)
        and all(bool(record["pass"]) for record in individual_records)
        and bool(report["equivalentPanelIntegration"].get("pass"))
        and bool(report["grouping"].get("pass"))
        and (
            args.skip_product_runs
            or (
                len(product_records) == int(report["grouping"].get("groupCount", 0))
                and all(bool(record["pass"]) for record in product_records)
            )
        )
    )
    report["summary"] = {
        "individualPassCount": sum(bool(record["pass"]) for record in individual_records),
        "individualFailCount": sum(not bool(record["pass"]) for record in individual_records),
        "productPassCount": sum(bool(record["pass"]) for record in product_records),
        "productFailCount": sum(not bool(record["pass"]) for record in product_records),
        "functionalPass": functional_pass,
        "performancePass": performance_pass,
        "fieldAccuracyStatus": (
            "Complete current-corpus human oracle available"
            if oracle_names and oracle_names == image_names
            else "Complete current-corpus human oracle required"
        ),
    }
    report["pass"] = functional_pass and performance_pass
    output.parent.mkdir(parents=True, exist_ok=True)
    sanitized = public_evidence(report, input_root)
    output.write_text(json.dumps(sanitized, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(sanitized, report_output)
    print(
        json.dumps(
            {"output": str(output), "pass": report["pass"], **report["summary"]},
            indent=2,
        )
    )
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
