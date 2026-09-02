"""Execute and retain the FR-041 total phase and terminal-state matrix."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "08-validation" / "evidence" / "total-phase-matrix.json"
TEMP_ROOT = Path(tempfile.gettempdir()).resolve()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitized(value: str) -> str:
    cleaned = value
    for path, replacement in ((ROOT, "<PROJECT_ROOT>"), (TEMP_ROOT, "<TEMP_ROOT>")):
        cleaned = cleaned.replace(str(path), replacement)
        cleaned = cleaned.replace(str(path).replace("\\", "/"), replacement)
    return cleaned


def run(command: list[str], cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    return {
        "command": sanitized(" ".join(command)),
        "exitCode": completed.returncode,
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "stdoutTail": sanitized(completed.stdout[-8000:]),
        "stderrTail": sanitized(completed.stderr[-4000:]),
    }


def cases(path: Path) -> dict[str, str]:
    root = ElementTree.parse(path).getroot()
    observed: dict[str, str] = {}
    for case in root.iter("testcase"):
        name = str(case.attrib.get("name", ""))
        failed = case.find("failure") is not None or case.find("error") is not None
        skipped = case.find("skipped") is not None
        observed[name] = "FAIL" if failed else "SKIP" if skipped else "PASS"
    return observed


def matching(observed: dict[str, str], fragments: tuple[str, ...]) -> list[str]:
    return [name for name in observed if any(fragment in name for fragment in fragments)]


def main() -> int:
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is unavailable")
    with tempfile.TemporaryDirectory(prefix="labelverify-phase-matrix-") as temporary:
        temp = Path(temporary)
        backend_xml = temp / "backend.xml"
        frontend_xml = temp / "frontend.xml"
        backend_command = [
            "uv",
            "run",
            "pytest",
            "-q",
            "backend/tests/test_lifecycle_matrix.py",
            f"--junitxml={backend_xml}",
        ]
        frontend_command = [
            npm,
            "test",
            "--",
            "--run",
            "tests/phase-matrix.test.tsx",
            "--reporter=junit",
            f"--outputFile={frontend_xml}",
        ]
        command_results = [run(backend_command, ROOT), run(frontend_command, ROOT / "frontend")]
        if not backend_xml.is_file() or not frontend_xml.is_file():
            raise RuntimeError("A phase-matrix test report was not created")
        observed = cases(backend_xml) | cases(frontend_xml)

    phase_definitions = {
        "synchronousClientValidation": ("terminates client validation locally",),
        "upload": ("upload_timeout_closes_partial_spool",),
        "parentValidation": ("parent_phase_stall_reaches_server_deadline",),
        "supervisedChildDecodeThroughInference": ("real_worker_timeout_replaces_recovers",),
        "queue": ("full_command_queue_reaches_worker_timeout", "two_slow_uploads_hold_capacity"),
        "transfer": ("response_transfer_stall_terminates_and_cleans",),
        "synchronousRenderFocusAnnouncement": (
            "renders and announces a complete response",
            "cancels in under one second",
        ),
        "cancellation": ("cancels in under one second", "route_cancellation_retains_ownership"),
        "disconnect": ("disconnect_delivery_failure_keeps_ownership",),
        "shutdown": (
            "shutdown_overlap_interrupts_owned_job",
            "shutdown_interrupts_command_enqueue_race",
        ),
        "browserDeadline": ("applies the 35 second browser terminal deadline",),
    }
    phases: list[dict[str, Any]] = []
    for phase, fragments in phase_definitions.items():
        matched = matching(observed, fragments)
        status = "PASS" if matched and all(observed[name] == "PASS" for name in matched) else "FAIL"
        phases.append({"phase": phase, "tests": matched, "status": status})

    source_paths = [
        ROOT / "backend/labelverify/security/boundary.py",
        ROOT / "backend/labelverify/orchestration/supervisor.py",
        ROOT / "backend/tests/test_lifecycle_matrix.py",
        ROOT / "frontend/src/app/App.tsx",
        ROOT / "frontend/tests/phase-matrix.test.tsx",
        Path(__file__).resolve(),
    ]
    passed = all(item["status"] == "PASS" for item in command_results + phases)
    evidence = {
        "schemaVersion": "1.0.0",
        "testId": "T-041",
        "assertionId": "T-041-A-COMPLETE-PHASE-MATRIX",
        "createdAtUtc": datetime.now(UTC).isoformat(),
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "governedDeadlinesSeconds": {"upload": 20, "server": 30, "browser": 35, "worker": 9.0},
        "sourceHashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in source_paths},
        "phases": phases,
        "commands": command_results,
        "pass": passed,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.relative_to(ROOT).as_posix(), "pass": passed}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
