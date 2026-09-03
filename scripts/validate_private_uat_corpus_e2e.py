"""Exercise the private UAT image corpus through production API boundaries.

This validator does not contain product names or expected label values. It
measures admission, decoding, OCR completion, contract integrity, evidence
integrity, server grouping, product-level batch completion, and latency. Field
accuracy requires an independent human oracle and is reported separately.
"""

from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

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


def post_analysis(client: TestClient, paths: list[Path]) -> tuple[int, dict[str, Any], float]:
    files = [
        ("panels", (path.name, path.read_bytes(), SUPPORTED_TYPES[path.suffix.casefold()]))
        for path in paths
    ]
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
                detected.status in {"Found", "Ambiguous"}
                for detected in result.detected.values()
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


def markdown_cell(value: Any) -> str:
    if value is None or value == "":
        return "Not read"
    return str(value).replace("|", "/").replace("\n", " ")


def write_markdown_report(report: dict[str, Any], output: Path) -> None:
    scope = report["scope"]
    summary = report.get("summary", {})
    individual = report.get("performance", {}).get("individual", {})
    products = report.get("performance", {}).get("products", {})
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
            "70-image field-level or legal-label accuracy."
        ),
        "",
        "## Per-image production API results",
        "",
        (
            "| File | API | Time | Type | Brand | Class/type | ABV | Proof | "
            "Net contents | Producer | Origin | Machine finding |"
        ),
        "| --- | ---: | ---: | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
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
                    markdown_cell(record.get("files", [""])[0]),
                    markdown_cell(record.get("httpStatus")),
                    f"{float(record.get('durationSeconds', 0)):.3f} s",
                    markdown_cell(observed.get("beverageType")),
                    markdown_cell(observed.get("brandName")),
                    markdown_cell(observed.get("classType")),
                    markdown_cell(observed.get("abvPercent")),
                    markdown_cell(observed.get("proof")),
                    markdown_cell(net),
                    markdown_cell(observed.get("producerNameAddress")),
                    markdown_cell(observed.get("countryOfOrigin")),
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
    args = parser.parse_args()

    input_root = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    report_output = (
        args.report_output
        if args.report_output.is_absolute()
        else PROJECT_ROOT / args.report_output
    )
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
        str(case.get("filename", "")).casefold()
        for case in oracle_cases
        if case.get("filename")
    }
    matched_oracle_names = oracle_names & image_names
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
        "individualScans": [],
        "grouping": {},
        "productScans": [],
        "pass": False,
    }
    if preflight_failures or not images:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
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
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_markdown_report(report, report_output)
    print(
        json.dumps(
            {"output": str(output), "pass": report["pass"], **report["summary"]},
            indent=2,
        )
    )
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
