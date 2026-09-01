"""Run and retain the governed post-fix lifecycle and security evidence package."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = ROOT / "docs" / "08-validation" / "evidence" / "security-post-fix"
LIFECYCLE_OUTPUT = EVIDENCE_ROOT / "lifecycle-matrix.json"
PRIOR_FAILED_OUTPUT = EVIDENCE_ROOT / "lifecycle-matrix-concurrent-load-failed.json"
SOURCE_OUTPUT = EVIDENCE_ROOT / "source-security-scan.json"
REPORT_OUTPUT = EVIDENCE_ROOT / "SECURITY_POST_FIX_REPORT.md"

SNAPSHOT_PATHS = (
    "backend/labelverify/api/app.py",
    "backend/labelverify/api/multipart.py",
    "backend/labelverify/api/routes.py",
    "backend/labelverify/imaging/decode.py",
    "backend/labelverify/orchestration/pipeline.py",
    "backend/labelverify/orchestration/supervisor.py",
    "backend/labelverify/security/boundary.py",
    "backend/labelverify/security/identity.py",
    "backend/labelverify/security/rate_limit.py",
    "backend/tests/test_api.py",
    "backend/tests/test_lifecycle_matrix.py",
    "backend/tests/test_multipart.py",
    "backend/tests/test_security.py",
    "backend/tests/test_supervisor_boundary.py",
    "contracts/api-contract-v1.json",
    "contracts/error-registry-v1.json",
    "frontend/src/api/verification-client.ts",
    "frontend/src/features/intake/sample-adapter.ts",
    "pyproject.toml",
    "scripts/run_security_post_fix_validation.py",
    "uv.lock",
)

FOCUSED_TESTS = (
    "backend/tests/test_lifecycle_matrix.py",
    "backend/tests/test_api.py",
    "backend/tests/test_multipart.py",
    "backend/tests/test_security.py",
    "backend/tests/test_supervisor_boundary.py",
)

ASSERTION_TESTS: tuple[tuple[str, str, str, str, int], ...] = (
    (
        "T-029-A-SUCCESS-CLEANUP",
        "FR-029",
        "Successful verification closes uploads and removes the request spool.",
        "test_valid_verification_is_complete_no_store_and_cleans_spool",
        1,
    ),
    (
        "T-029-A-VALIDATION-CLEANUP",
        "FR-029",
        "Validation rejection is result-free and leaves no request ownership.",
        "test_invalid_reference_is_result_free_and_does_not_run_worker",
        1,
    ),
    (
        "T-029-A-PARTIAL-PARSER-CLEANUP",
        "FR-029",
        "Parser-owned rolled files close on ordinary failure and cancellation.",
        "test_partial_spool_closes_for_every_exception",
        2,
    ),
    (
        "T-008-A-UPLOAD-TIMEOUT-CLEANUP",
        "FR-008",
        "A controlled upload timeout closes the partial spool and releases counters.",
        "test_t029_upload_timeout_closes_partial_spool_and_ownership",
        1,
    ),
    (
        "T-008-A-CONCURRENT-SLOW-ADMISSION",
        "FR-008",
        "Two slow uploads hold both admissions and a third is rejected before body read.",
        "test_t041_two_slow_uploads_hold_capacity_and_third_reads_no_body",
        1,
    ),
    (
        "T-008-A-NEAR-LIMIT-SPOOL",
        "FR-008",
        "Two concurrent exact per-file and aggregate-limit requests clean all spool state.",
        "test_t029_near_limit_requests_cleanup_files_handles_and_reservations",
        1,
    ),
    (
        "T-041-A-REPEATED-ROUTE-CANCELLATION",
        "FR-041",
        "Repeated route cancellation retains ownership until worker completion.",
        "test_t041_route_cancellation_retains_ownership_until_worker_finishes",
        3,
    ),
    (
        "T-041-A-DISCONNECT-OWNERSHIP",
        "FR-041",
        "Repeated response delivery failure retains ownership until worker completion.",
        "test_t041_disconnect_delivery_failure_keeps_ownership_until_worker_finishes",
        3,
    ),
    (
        "T-009-A-REAL-CHILD-STALL-RECOVERY",
        "FR-009",
        "A real spawned child stall is terminated, replaced, readied, and recovered.",
        "test_t009_real_worker_timeout_replaces_recovers_and_stops",
        1,
    ),
    (
        "T-029-A-SHUTDOWN-OWNERSHIP",
        "FR-029",
        "Shutdown overlap interrupts the owned job and returns with zero child ownership.",
        "test_t029_shutdown_overlap_interrupts_owned_job_and_reaches_zero",
        1,
    ),
    (
        "T-029-A-SHUTDOWN-ENQUEUE-RACE",
        "FR-029",
        "Shutdown interrupts a blocked command enqueue and releases all job ownership.",
        "test_t029_shutdown_interrupts_command_enqueue_race",
        1,
    ),
    (
        "T-029-A-CONTENT-PATH-CANARY",
        "FR-029",
        "User content and local path canaries reach neither response nor captured logs.",
        "test_t029_content_and_path_canaries_never_reach_response_or_logs",
        1,
    ),
)


def sha256_repository_text(path: Path) -> str:
    """Hash text using Git's canonical LF representation.

    The governed snapshot contains repository text files only. Normalizing CRLF
    before hashing keeps evidence identical to the Git blob that reviewers and
    CI receive, even when a Windows checkout presents CRLF working-tree bytes.
    """

    payload = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(payload).hexdigest()


def source_snapshot() -> dict[str, Any]:
    files = {relative: sha256_repository_text(ROOT / relative) for relative in SNAPSHOT_PATHS}
    identity = hashlib.sha256(
        "".join(f"{path}:{digest}\n" for path, digest in files.items()).encode()
    ).hexdigest()
    return {"snapshotId": identity, "files": files}


def sanitize_output(value: str) -> str:
    sanitized = value.replace(str(ROOT), "<repo>").replace(str(Path.home()), "<home>")
    sanitized = re.sub(r"(?i)[a-z]:\\users\\[^\\\r\n]+", r"C:\\Users\\<user>", sanitized)
    lines = sanitized.splitlines()
    return "\n".join(lines[-40:])


def run_command(
    command_id: str,
    display: str,
    arguments: list[str],
    *,
    junit_path: Path | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        arguments,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    duration_ms = round((time.perf_counter() - started) * 1000, 3)
    record: dict[str, Any] = {
        "commandId": command_id,
        "command": display,
        "exitCode": completed.returncode,
        "durationMs": duration_ms,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "stdoutTail": sanitize_output(completed.stdout),
        "stderrTail": sanitize_output(completed.stderr),
    }
    if junit_path is not None:
        record["junit"] = parse_junit(junit_path)
    return record


def parse_junit(path: Path) -> list[dict[str, str]]:
    root = ET.parse(path).getroot()
    records: list[dict[str, str]] = []
    for case in root.iter("testcase"):
        status = "PASS"
        if case.find("failure") is not None or case.find("error") is not None:
            status = "FAIL"
        elif case.find("skipped") is not None:
            status = "BLOCKED"
        records.append(
            {
                "classname": str(case.attrib.get("classname", "")),
                "name": str(case.attrib.get("name", "")),
                "status": status,
            }
        )
    return records


def assertion_records(test_cases: list[dict[str, str]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for assertion_id, feature, expected, test_name, minimum_count in ASSERTION_TESTS:
        matches = [case for case in test_cases if case["name"].startswith(test_name)]
        passing = sum(case["status"] == "PASS" for case in matches)
        status = "PASS" if len(matches) >= minimum_count and passing == len(matches) else "FAIL"
        records.append(
            {
                "testId": feature.replace("FR", "T"),
                "featureRequirement": feature,
                "assertionId": assertion_id,
                "scope": "local",
                "expected": expected,
                "observed": {
                    "matchedCases": len(matches),
                    "passedCases": passing,
                    "minimumRequired": minimum_count,
                    "testName": test_name,
                },
                "status": status,
                "compositeState": "FINAL_PASS" if status == "PASS" else "FAIL",
                "executorRole": "INT-LEAD security remediation",
                "reviewerRole": "independent final RT re-review required",
                "linkedDefect": "RT2-F002",
            }
        )
    return records


def runtime_source_files() -> list[Path]:
    backend = sorted((ROOT / "backend" / "labelverify").rglob("*.py"))
    frontend = sorted(
        path for path in (ROOT / "frontend" / "src").rglob("*") if path.suffix in {".ts", ".tsx"}
    )
    return backend + frontend


def scan_python_imports(paths: list[Path]) -> list[dict[str, str]]:
    forbidden = {"aiohttp", "httpx", "requests", "socket", "urllib"}
    findings: list[dict[str, str]] = []
    for path in paths:
        if path.suffix != ".py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                root_name = name.split(".", 1)[0]
                if root_name in forbidden:
                    findings.append(
                        {
                            "path": path.relative_to(ROOT).as_posix(),
                            "module": name,
                            "line": str(node.lineno),
                        }
                    )
    return findings


def scan_runtime_sources() -> dict[str, Any]:
    paths = runtime_source_files()
    private_path_pattern = re.compile(r"(?i)([a-z]:\\users\\|/users/|/home/|file://)")
    url_pattern = re.compile(r"https?://[a-z0-9]", re.IGNORECASE)
    log_pattern = re.compile(
        r"(?i)(\blogging\b|\blogger\b|\bprint\s*\(|console\.(log|error|warn|debug)\s*\()"
    )
    private_path_findings: list[dict[str, Any]] = []
    external_url_literals: list[dict[str, Any]] = []
    logging_findings: list[dict[str, Any]] = []
    unicode_dash_findings: list[dict[str, Any]] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT).as_posix()
        for line_number, line in enumerate(text.splitlines(), start=1):
            if private_path_pattern.search(line):
                private_path_findings.append({"path": relative, "line": line_number})
            if url_pattern.search(line):
                external_url_literals.append({"path": relative, "line": line_number})
            if log_pattern.search(line):
                logging_findings.append({"path": relative, "line": line_number})
            if any("\u2010" <= character <= "\u2015" for character in line):
                unicode_dash_findings.append({"path": relative, "line": line_number})
    forbidden_imports = scan_python_imports(paths)
    status = (
        "PASS"
        if not (
            private_path_findings
            or external_url_literals
            or logging_findings
            or unicode_dash_findings
            or forbidden_imports
        )
        else "FAIL"
    )
    return {
        "status": status,
        "scope": [path.relative_to(ROOT).as_posix() for path in paths],
        "contentAndPath": {
            "status": "PASS"
            if not private_path_findings and not logging_findings and not unicode_dash_findings
            else "FAIL",
            "privatePathFindings": private_path_findings,
            "loggingCallFindings": logging_findings,
            "unicodeDashFindings": unicode_dash_findings,
        },
        "noRequiredRuntimeEgress": {
            "status": "PASS" if not forbidden_imports and not external_url_literals else "FAIL",
            "forbiddenPythonImports": forbidden_imports,
            "externalUrlLiterals": external_url_literals,
            "basis": (
                "Runtime application sources contain no outbound client import or external URL "
                "literal. Frontend fetch targets are same-origin relative paths or server-governed "
                "sample paths. "
                "Build-time model fetching is outside the runtime application source set."
            ),
        },
        "networkLevelDeployedEgress": {
            "status": "BLOCKED",
            "reason": (
                "The Azure demo is authorized, but no deny-by-default network policy is selected. "
                "Source inspection cannot prove platform firewall enforcement or "
                "restricted-egress behavior."
            ),
        },
    }


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def write_report(lifecycle: dict[str, Any], source_scan: dict[str, Any]) -> None:
    assertions = lifecycle["assertions"]
    commands = lifecycle["commands"]
    lines = [
        "# Security Post-Fix Lifecycle Report",
        "",
        "Status: " + ("PASS" if lifecycle["pass"] else "FAIL"),
        "",
        "## Snapshot binding",
        "",
        f"Snapshot ID: `{lifecycle['snapshot']['snapshotId']}`",
        "",
        "The evidence hashes the runtime boundary, parser, routes, supervisor, imaging path, "
        "focused tests, contracts, lock, and this runner. Hashes are in `lifecycle-matrix.json`.",
        "",
        "## Local assertions",
        "",
        "| Assertion | FR | Status | Observed |",
        "|---|---|---|---|",
    ]
    for record in assertions:
        observed = record["observed"]
        lines.append(
            f"| `{record['assertionId']}` | `{record['featureRequirement']}` | "
            f"{record['status']} | {observed['passedCases']} of {observed['matchedCases']} cases |"
        )
    lines.extend(
        [
            f"| `T-029-A-RUNTIME-CONTENT-PATH-SCAN` | `FR-029` | "
            f"{source_scan['contentAndPath']['status']} | Runtime source and canary scan |",
            f"| `T-029-A-NO-RUNTIME-EGRESS-SOURCE` | `FR-029` | "
            f"{source_scan['noRequiredRuntimeEgress']['status']} | "
            "Source-backed call-path result |",
            f"| `T-029-A-NETWORK-EGRESS-ENFORCEMENT` | `FR-029` | "
            f"{source_scan['networkLevelDeployedEgress']['status']} | "
            "Deny-by-default platform policy proof unavailable |",
            "",
            "## Commands",
            "",
            "| Command | Status | Exit |",
            "|---|---|---:|",
        ]
    )
    for record in commands:
        lines.append(f"| `{record['command']}` | {record['status']} | {record['exitCode']} |")
    lines.extend(
        [
            "",
            "## Disposition",
            "",
            "All requested local lifecycle, cleanup, worker recovery, canary, and source-backed "
            "no-runtime-egress assertions pass. Network-level deployed egress remains BLOCKED "
            "because the authorized Azure demo does not establish a deny-by-default platform "
            "policy. This report does not promote that external control to PASS.",
            "",
        ]
    )
    REPORT_OUTPUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    if LIFECYCLE_OUTPUT.exists():
        prior = json.loads(LIFECYCLE_OUTPUT.read_text(encoding="utf-8"))
        if prior.get("pass") is False:
            write_json(PRIOR_FAILED_OUTPUT, prior)
    started_at = datetime.now(UTC).isoformat()
    before = source_snapshot()
    with tempfile.TemporaryDirectory(prefix="labelverify-security-post-fix-") as temporary:
        junit_path = Path(temporary) / "focused.xml"
        focused_arguments = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            *FOCUSED_TESTS,
            f"--junitxml={junit_path}",
        ]
        commands = [
            run_command(
                "focused-security-lifecycle",
                "uv run pytest -q " + " ".join(FOCUSED_TESTS),
                focused_arguments,
                junit_path=junit_path,
            ),
            run_command(
                "ruff-check",
                "uv run ruff check backend tests scripts ops",
                [sys.executable, "-m", "ruff", "check", "backend", "tests", "scripts", "ops"],
            ),
            run_command(
                "ruff-format-check",
                (
                    "uv run ruff format --check backend/labelverify/orchestration/supervisor.py "
                    "backend/labelverify/security/rate_limit.py "
                    "backend/tests/test_lifecycle_matrix.py "
                    "scripts/run_security_post_fix_validation.py"
                ),
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "format",
                    "--check",
                    "backend/labelverify/orchestration/supervisor.py",
                    "backend/labelverify/security/rate_limit.py",
                    "backend/tests/test_lifecycle_matrix.py",
                    "scripts/run_security_post_fix_validation.py",
                ],
            ),
            run_command(
                "strict-mypy",
                "uv run mypy",
                [sys.executable, "-m", "mypy"],
            ),
            run_command(
                "full-backend-validation",
                "uv run pytest -q backend/tests tests",
                [sys.executable, "-m", "pytest", "-q", "backend/tests", "tests"],
            ),
        ]
    focused = commands[0]
    test_cases = list(focused.get("junit", []))
    assertions = assertion_records(test_cases)
    source_scan = scan_runtime_sources()
    after = source_snapshot()
    source_stable = before == after
    command_pass = all(record["status"] == "PASS" for record in commands)
    assertion_pass = all(record["status"] == "PASS" for record in assertions)
    local_source_pass = source_scan["status"] == "PASS"
    lifecycle = {
        "schemaVersion": "1.0.0",
        "evidenceId": "T-029-T-041-SECURITY-POST-FIX",
        "createdAtUtc": started_at,
        "completedAtUtc": datetime.now(UTC).isoformat(),
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "logicalCpuCount": os.cpu_count(),
        },
        "snapshot": before,
        "sourceStableDuringRun": source_stable,
        "governedLimits": {
            "rawRequestBytes": 8_650_752,
            "fileBytes": 4_194_304,
            "aggregateFileBytes": 8_388_608,
            "uploadDeadlineSeconds": 20.0,
            "serverDeadlineSeconds": 30.0,
            "workerDeadlineSeconds": 6.25,
            "admissions": 2,
            "reservationBytesPerAdmission": 17_301_504,
        },
        "controlledFaults": {
            "uploadTimeoutTestSeconds": 0.05,
            "workerTimeoutTestSeconds": 0.2,
            "note": (
                "Fault-injection deadlines apply only to isolated test instances. Production "
                "contract limits and defaults are unchanged."
            ),
        },
        "assertions": assertions,
        "commands": commands,
        "blockedAssertions": [
            {
                "testId": "T-029",
                "featureRequirement": "FR-029",
                "assertionId": "T-029-A-NETWORK-EGRESS-ENFORCEMENT",
                "scope": "deployed",
                "status": "BLOCKED",
                "compositeState": "INCOMPLETE",
                "reason": source_scan["networkLevelDeployedEgress"]["reason"],
            }
        ],
        "pass": command_pass and assertion_pass and local_source_pass and source_stable,
    }
    source_evidence = {
        "schemaVersion": "1.0.0",
        "evidenceId": "T-029-SOURCE-SECURITY-SCAN",
        "createdAtUtc": lifecycle["completedAtUtc"],
        "snapshotId": before["snapshotId"],
        **source_scan,
    }
    write_json(LIFECYCLE_OUTPUT, lifecycle)
    write_json(SOURCE_OUTPUT, source_evidence)
    write_report(lifecycle, source_scan)
    print(
        json.dumps(
            {
                "lifecycleEvidence": LIFECYCLE_OUTPUT.relative_to(ROOT).as_posix(),
                "sourceEvidence": SOURCE_OUTPUT.relative_to(ROOT).as_posix(),
                "report": REPORT_OUTPUT.relative_to(ROOT).as_posix(),
                "localPass": lifecycle["pass"],
                "networkLevelDeployedEgress": "BLOCKED",
            },
            indent=2,
        )
    )
    return 0 if lifecycle["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
