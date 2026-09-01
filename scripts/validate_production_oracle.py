"""Run the production pipeline against the independent governed corpus oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import tempfile
import time
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from labelverify.api.app import create_app
from labelverify.contracts.models import VerificationResult
from labelverify.extraction.rapidocr_adapter import MODEL_ASSETS
from labelverify.orchestration.supervisor import WorkerSupervisor
from labelverify.settings.config import Settings

from scripts.validate_fixture_corpus import validate_corpus

DEFAULT_OUTPUT = Path("docs/08-validation/evidence/production-oracle-corpus.json")
DEFAULT_BUILD_ID = "vv-production-oracle-v1"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def governed_path(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    fixtures_root = (root / "fixtures").resolve()
    if not candidate.is_relative_to(fixtures_root):
        raise ValueError(f"Path escapes the governed fixture root: {relative}")
    return candidate


def failure(
    case_id: str,
    category: str,
    expected: Any,
    observed: Any,
    *,
    check_id: str | None = None,
    row_index: int | None = None,
) -> dict[str, Any]:
    suffix = f"-{check_id}" if check_id else ""
    return {
        "failureId": f"{case_id}-{category.upper().replace('_', '-')}{suffix}",
        "category": category,
        "checkId": check_id,
        "rowIndex": row_index,
        "expected": expected,
        "observed": observed,
    }


def compare_result(
    case_id: str,
    actual: dict[str, Any],
    oracle: dict[str, Any],
    ordered_check_ids: list[str],
) -> list[dict[str, Any]]:
    """Compare one production result without importing production expected logic."""

    failures: list[dict[str, Any]] = []
    if actual.get("summary") != oracle.get("summary"):
        failures.append(
            failure(case_id, "summary", oracle.get("summary"), actual.get("summary"))
        )

    oracle_checks = oracle.get("checks")
    actual_checks = actual.get("checks")
    if not isinstance(oracle_checks, list) or not isinstance(actual_checks, list):
        failures.append(
            failure(
                case_id,
                "check_rows",
                "19 ordered oracle and production rows",
                {
                    "oracleType": type(oracle_checks).__name__,
                    "actualType": type(actual_checks).__name__,
                },
            )
        )
        return failures

    oracle_ids = [row.get("checkId") for row in oracle_checks]
    actual_ids = [row.get("checkId") for row in actual_checks]
    if oracle_ids != ordered_check_ids:
        failures.append(failure(case_id, "oracle_order", ordered_check_ids, oracle_ids))
    if actual_ids != ordered_check_ids:
        failures.append(failure(case_id, "production_order", ordered_check_ids, actual_ids))
    if len(oracle_checks) != 19 or len(actual_checks) != 19:
        failures.append(
            failure(
                case_id,
                "check_count",
                {"oracle": 19, "production": 19},
                {"oracle": len(oracle_checks), "production": len(actual_checks)},
            )
        )

    evidence_rows = actual.get("evidence")
    evidence_ids = {
        row.get("evidenceId")
        for row in evidence_rows
        if isinstance(row, dict) and isinstance(row.get("evidenceId"), str)
    } if isinstance(evidence_rows, list) else set()

    for index, check_id in enumerate(ordered_check_ids):
        if index >= len(oracle_checks) or index >= len(actual_checks):
            continue
        expected_row = oracle_checks[index]
        actual_row = actual_checks[index]
        if expected_row.get("checkId") != check_id or actual_row.get("checkId") != check_id:
            continue
        for property_name in ("applicable", "state"):
            if actual_row.get(property_name) != expected_row.get(property_name):
                failures.append(
                    failure(
                        case_id,
                        property_name,
                        expected_row.get(property_name),
                        actual_row.get(property_name),
                        check_id=check_id,
                        row_index=index,
                    )
                )

        primary_ref = actual_row.get("evidenceRef")
        alternatives = actual_row.get("alternatives")
        alternative_refs = [
            row.get("evidenceRef")
            for row in alternatives
            if isinstance(row, dict) and isinstance(row.get("evidenceRef"), str)
        ] if isinstance(alternatives, list) else []
        linked_refs = ([primary_ref] if isinstance(primary_ref, str) else []) + alternative_refs
        invalid_refs = [ref for ref in linked_refs if ref not in evidence_ids]
        if invalid_refs:
            failures.append(
                failure(
                    case_id,
                    "evidence_reference",
                    "all linked evidence IDs present in the result evidence collection",
                    invalid_refs,
                    check_id=check_id,
                    row_index=index,
                )
            )

        evidence_rule = expected_row.get("evidence")
        if evidence_rule == "required" and not linked_refs:
            failures.append(
                failure(
                    case_id,
                    "evidence_required",
                    "one or more linked evidence records",
                    0,
                    check_id=check_id,
                    row_index=index,
                )
            )
        if evidence_rule == "forbidden" and linked_refs:
            failures.append(
                failure(
                    case_id,
                    "evidence_forbidden",
                    0,
                    len(linked_refs),
                    check_id=check_id,
                    row_index=index,
                )
            )
        minimum_alternatives = int(expected_row.get("minimumAlternatives", 0))
        if len(alternative_refs) < minimum_alternatives:
            failures.append(
                failure(
                    case_id,
                    "alternatives",
                    {"minimum": minimum_alternatives},
                    {"count": len(alternative_refs)},
                    check_id=check_id,
                    row_index=index,
                )
            )
    return failures


def compare_error(
    case_id: str,
    status_code: int,
    actual: dict[str, Any],
    oracle: dict[str, Any],
) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    expected = oracle.get("error", {})
    if status_code != expected.get("http"):
        failures.append(failure(case_id, "http_status", expected.get("http"), status_code))
    if actual.get("code") != expected.get("code"):
        failures.append(failure(case_id, "error_code", expected.get("code"), actual.get("code")))
    has_result = "summary" in actual or "checks" in actual
    if expected.get("resultMustBeAbsent") is True and has_result:
        failures.append(failure(case_id, "result_absence", True, False))
    return failures


def verify_model_assets(
    model_root: Path,
    manifest_path: Path,
    expected_assets: dict[str, str] | None = None,
) -> tuple[list[dict[str, Any]], list[str]]:
    manifest = load_json(manifest_path)
    declared = {row["filename"]: row["sha256"] for row in manifest.get("artifacts", [])}
    expected = expected_assets if expected_assets is not None else MODEL_ASSETS
    errors: list[str] = []
    if declared != expected:
        errors.append("The model manifest and production model registry differ")
    records: list[dict[str, Any]] = []
    for filename, expected_hash in sorted(expected.items()):
        path = model_root / filename
        actual_hash = sha256_file(path) if path.is_file() else None
        matches = actual_hash == expected_hash
        records.append(
            {
                "filename": filename,
                "expectedSha256": expected_hash,
                "actualSha256": actual_hash,
                "bytes": path.stat().st_size if path.is_file() else None,
                "matches": matches,
            }
        )
        if not matches:
            errors.append(f"Model hash mismatch: {filename}")
    return records, errors


def request_files(root: Path, case: dict[str, Any]) -> list[tuple[str, tuple[Any, ...]]]:
    reference_path = governed_path(root, case["referencePath"])
    files: list[tuple[str, tuple[Any, ...]]] = [
        (
            "reference",
            (None, reference_path.read_text(encoding="utf-8"), "application/json"),
        )
    ]
    for panel in case.get("panels", []):
        path = governed_path(root, panel["path"])
        files.append(
            (
                "panels",
                (path.name, path.read_bytes(), str(panel["mimeType"])),
            )
        )
    return files


@contextmanager
def api_harness(
    root: Path,
    build_id: str,
    worker_deadline_seconds: float,
    readiness_timeout: float,
) -> Iterator[tuple[TestClient, WorkerSupervisor, dict[str, Any]]]:
    supervisor = WorkerSupervisor(
        root / "models",
        worker_deadline_seconds=worker_deadline_seconds,
        build_id=build_id,
    )
    started = time.perf_counter()
    if not supervisor.start(readiness_timeout=readiness_timeout):
        raise RuntimeError("The hash-verifying production worker did not become ready")
    ready_ms = round((time.perf_counter() - started) * 1000, 3)
    snapshot = supervisor.snapshot()
    with tempfile.TemporaryDirectory(prefix="labelverify-oracle-") as spool:
        settings = Settings(
            runtime_mode="direct",
            allowed_host=None,
            model_root=root / "models",
            spool_root=Path(spool),
            sample_manifest=root / "fixtures" / "sample" / "sample-manifest-v1.json",
            static_root=root / "frontend" / "dist",
            build_id=build_id,
        )
        app = create_app(settings=settings, supervisor=supervisor)
        try:
            with TestClient(app, client=("127.0.0.1", 50000)) as client:
                yield client, supervisor, {
                    "readyMs": ready_ms,
                    "generation": snapshot.generation,
                    "childPid": snapshot.child_pid,
                    "workerDeadlineSeconds": worker_deadline_seconds,
                }
        finally:
            supervisor.stop()


def run_case(
    root: Path,
    client: TestClient,
    case: dict[str, Any],
    ordered_check_ids: list[str],
) -> dict[str, Any]:
    case_id = str(case["caseId"])
    oracle = load_json(governed_path(root, case["oraclePath"]))
    started = time.perf_counter()
    response = client.post("/api/v1/verifications", files=request_files(root, case))
    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    try:
        body = response.json()
    except json.JSONDecodeError:
        body = {"nonJsonBody": response.text[:200]}
    failures: list[dict[str, Any]]
    observed: dict[str, Any]
    if case["expectedKind"] == "result":
        if response.status_code != 200:
            failures = [failure(case_id, "result_status", 200, response.status_code)]
            if isinstance(body, dict) and body.get("code"):
                failures.append(failure(case_id, "unexpected_error", None, body.get("code")))
            observed = {
                "kind": "error",
                "httpStatus": response.status_code,
                "code": body.get("code") if isinstance(body, dict) else None,
            }
        else:
            try:
                result = VerificationResult.model_validate(body)
                result_body = result.model_dump(by_alias=True, mode="json")
                failures = compare_result(case_id, result_body, oracle, ordered_check_ids)
                observed = {
                    "kind": "result",
                    "httpStatus": response.status_code,
                    "summary": result.summary,
                    "checkCount": len(result.checks),
                    "evidenceCount": len(result.evidence),
                    "serverDurationMs": result.server_duration_ms,
                    "modelIdentity": result.model_identity,
                    "buildId": result.build_id,
                }
            except Exception as exc:
                failures = [
                    failure(
                        case_id,
                        "result_contract",
                        "valid VerificationResult",
                        f"{type(exc).__name__}: {exc}",
                    )
                ]
                observed = {"kind": "invalid_result", "httpStatus": response.status_code}
    else:
        if not isinstance(body, dict):
            body = {"nonJsonBody": str(body)[:200]}
        failures = compare_error(case_id, response.status_code, body, oracle)
        observed = {
            "kind": "error" if "code" in body else "unknown",
            "httpStatus": response.status_code,
            "code": body.get("code"),
            "resultPresent": "summary" in body or "checks" in body,
        }
    expected_summary = oracle.get("summary")
    false_clean = (
        case["expectedKind"] == "result"
        and expected_summary != "No differences found in checked fields"
        and observed.get("summary") == "No differences found in checked fields"
    )
    return {
        "caseId": case_id,
        "partition": case["partition"],
        "sealed": bool(case["sealed"]),
        "expectedKind": case["expectedKind"],
        "executionPath": (
            "production_api_controlled_timeout"
            if case.get("fault") == "inference_timeout"
            else "production_api"
        ),
        "durationMs": duration_ms,
        "expected": {
            "summary": expected_summary,
            "errorCode": oracle.get("error", {}).get("code"),
            "checkCount": len(oracle.get("checks", [])),
        },
        "observed": observed,
        "falseClean": false_clean,
        "failureCount": len(failures),
        "failures": failures,
        "pass": not failures,
    }


def wait_for_replacement(supervisor: WorkerSupervisor, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if supervisor.ready:
            return
        time.sleep(0.05)


def run_cases(
    root: Path,
    cases: list[dict[str, Any]],
    ordered_check_ids: list[str],
    worker_deadline_seconds: float,
    timeout_fault_seconds: float,
    readiness_timeout: float,
    build_id: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    startups: list[dict[str, Any]] = []
    index = 0
    while index < len(cases):
        timeout_fault = cases[index].get("fault") == "inference_timeout"
        segment: list[dict[str, Any]] = []
        while index < len(cases):
            current_fault = cases[index].get("fault") == "inference_timeout"
            if current_fault != timeout_fault:
                break
            segment.append(cases[index])
            index += 1
            if timeout_fault:
                break
        deadline = timeout_fault_seconds if timeout_fault else worker_deadline_seconds
        with api_harness(root, build_id, deadline, readiness_timeout) as harness:
            client, supervisor, startup = harness
            startups.append(startup)
            for case in segment:
                record = run_case(root, client, case, ordered_check_ids)
                records.append(record)
                marker = "PASS" if record["pass"] else "FAIL"
                print(
                    f"case {len(records):02d}/{len(cases):02d} {case['caseId']} {marker} "
                    f"{record['durationMs']} ms",
                    flush=True,
                )
                if not supervisor.ready:
                    wait_for_replacement(supervisor, readiness_timeout)
    return records, startups


def report_hashes(root: Path, oracle_paths: list[str]) -> dict[str, Any]:
    contract_paths = sorted((root / "contracts").glob("*-v1.json"), key=lambda path: path.name)
    source_paths = sorted((root / "backend" / "labelverify").rglob("*.py"))
    source_paths.extend(
        root / "scripts" / name
        for name in (
            "generate_fixture_corpus.py",
            "validate_production_oracle.py",
        )
    )
    return {
        "validatorSha256": sha256_file(Path(__file__)),
        "supervisorSha256": sha256_file(
            root / "backend" / "labelverify" / "orchestration" / "supervisor.py"
        ),
        "pipelineSha256": sha256_file(
            root / "backend" / "labelverify" / "orchestration" / "pipeline.py"
        ),
        "corpusManifestSha256": sha256_file(root / "fixtures" / "corpus-manifest-v1.json"),
        "holdoutSealSha256": sha256_file(root / "fixtures" / "holdout" / "SEAL.sha256"),
        "modelManifestSha256": sha256_file(root / "ops" / "model-manifest.json"),
        "contracts": {path.name: sha256_file(path) for path in contract_paths},
        "productionSource": {
            path.relative_to(root).as_posix(): sha256_file(path)
            for path in source_paths
        },
        "oracles": {
            path: sha256_file(governed_path(root, path)) for path in sorted(oracle_paths)
        },
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare the production WorkerSupervisor pipeline with all governed oracles."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--build-id", default=DEFAULT_BUILD_ID)
    parser.add_argument("--readiness-timeout", type=float, default=30.0)
    parser.add_argument("--worker-deadline", type=float, default=6.25)
    parser.add_argument("--timeout-fault-deadline", type=float, default=0.001)
    args = parser.parse_args()
    if min(args.readiness_timeout, args.worker_deadline, args.timeout_fault_deadline) <= 0:
        parser.error("Timeout values must be positive")

    root = Path(__file__).resolve().parents[1]
    output = args.output if args.output.is_absolute() else root / args.output
    manifest = load_json(root / "fixtures" / "corpus-manifest-v1.json")
    cases = manifest.get("cases", [])
    registry = load_json(root / "contracts" / "selected-check-registry-v1.json")
    ordered_check_ids = [row["checkId"] for row in registry["checks"]]
    fixture_errors, fixture_metrics = validate_corpus(root)
    model_records, model_errors = verify_model_assets(
        root / "models", root / "ops" / "model-manifest.json"
    )
    preflight_errors = fixture_errors + model_errors
    if len(cases) != 30:
        preflight_errors.append(f"Expected 30 manifest cases, found {len(cases)}")
    if sum(case.get("partition") == "holdout" for case in cases) != 6:
        preflight_errors.append("Expected exactly 6 holdout cases")
    if len(ordered_check_ids) != 19:
        preflight_errors.append(f"Expected 19 ordered checks, found {len(ordered_check_ids)}")

    report: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "evidenceId": "T-032-A-PRODUCTION-ORACLE-CORPUS",
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "command": "uv run python scripts/validate_production_oracle.py",
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
        "snapshot": report_hashes(root, [case["oraclePath"] for case in cases]),
        "preflight": {
            "pass": not preflight_errors,
            "errors": preflight_errors,
            "fixtureMetrics": fixture_metrics,
            "modelAssets": model_records,
        },
        "execution": {
            "serial": True,
            "worker": "labelverify.orchestration.supervisor.WorkerSupervisor",
            "workerDeadlineSeconds": args.worker_deadline,
            "controlledTimeoutDeadlineSeconds": args.timeout_fault_deadline,
            "cases": [],
            "workerStartups": [],
        },
        "totals": {},
        "pass": False,
    }
    if preflight_errors:
        report["totals"] = {
            "manifestCases": len(cases),
            "attemptedCases": 0,
            "passedCases": 0,
            "failedCases": 0,
            "holdoutCases": sum(case.get("partition") == "holdout" for case in cases),
            "falseCleanCount": 0,
            "failureCount": len(preflight_errors),
        }
        write_report(output, report)
        print(json.dumps({"output": str(output), "pass": False, "errors": preflight_errors}))
        return 1

    try:
        records, startups = run_cases(
            root,
            cases,
            ordered_check_ids,
            args.worker_deadline,
            args.timeout_fault_deadline,
            args.readiness_timeout,
            args.build_id,
        )
    except Exception as exc:
        report["execution"]["fatalError"] = f"{type(exc).__name__}: {exc}"
        records = report["execution"]["cases"]
        startups = report["execution"]["workerStartups"]
    report["execution"]["cases"] = records
    report["execution"]["workerStartups"] = startups
    failures = [item for record in records for item in record["failures"]]
    false_clean_count = sum(bool(record["falseClean"]) for record in records)
    fatal_error = report["execution"].get("fatalError")
    passed = (
        not fatal_error
        and len(records) == len(cases)
        and not failures
        and false_clean_count == 0
    )
    report["totals"] = {
        "manifestCases": len(cases),
        "attemptedCases": len(records),
        "passedCases": sum(bool(record["pass"]) for record in records),
        "failedCases": sum(not bool(record["pass"]) for record in records),
        "developmentCases": sum(record["partition"] == "development" for record in records),
        "holdoutCases": sum(record["partition"] == "holdout" for record in records),
        "falseCleanCount": false_clean_count,
        "failureCount": len(failures) + int(fatal_error is not None),
    }
    report["pass"] = passed
    write_report(output, report)
    summary = {
        "output": str(output),
        "pass": passed,
        **report["totals"],
    }
    print(json.dumps(summary, indent=2))
    if failures:
        print(json.dumps({"failures": failures}, indent=2))
    if fatal_error:
        print(json.dumps({"fatalError": fatal_error}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
