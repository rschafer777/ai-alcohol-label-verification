from __future__ import annotations

import argparse
import json
import math
import os
import platform
import sys
import threading
import time
from contextlib import suppress
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil  # type: ignore[import-untyped]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from labelverify.contracts.loader import contracts  # noqa: E402
from labelverify.contracts.models import ReferenceRecord, VerificationResult  # noqa: E402
from labelverify.orchestration.supervisor import WorkerSupervisor  # noqa: E402

WARM_RSS_THRESHOLD_BYTES = 2 * 1024 * 1024 * 1024
COLD_RSS_THRESHOLD_BYTES = 4 * 1024 * 1024 * 1024


class PeakRssSampler:
    def __init__(self, supervisor: WorkerSupervisor) -> None:
        self._supervisor = supervisor
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self.peak_bytes = 0
        self.peak_parent_bytes = 0
        self.peak_worker_bytes = 0

    def _sample(self) -> None:
        parent = psutil.Process()
        while not self._stop.is_set():
            parent_bytes = parent.memory_info().rss
            worker_bytes = 0
            child_pid = self._supervisor.snapshot().child_pid
            if child_pid is not None:
                with suppress(psutil.AccessDenied, psutil.NoSuchProcess):
                    worker_bytes = psutil.Process(child_pid).memory_info().rss
            self.peak_parent_bytes = max(self.peak_parent_bytes, parent_bytes)
            self.peak_worker_bytes = max(self.peak_worker_bytes, worker_bytes)
            self.peak_bytes = max(self.peak_bytes, parent_bytes + worker_bytes)
            self._stop.wait(0.01)

    def __enter__(self) -> PeakRssSampler:
        self._thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self._stop.set()
        self._thread.join()


def nearest_rank(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = max(0, math.ceil(len(ordered) * percentile) - 1)
    return ordered[index]


def load_sample(root: Path) -> tuple[ReferenceRecord, tuple[Path, ...], str]:
    fixture_root = root / "fixtures" / "sample"
    manifest = json.loads((fixture_root / "sample-manifest-v1.json").read_text(encoding="utf-8"))
    reference = ReferenceRecord.model_validate(
        json.loads((fixture_root / "reference.json").read_text(encoding="utf-8"))
    )
    panels = tuple(sorted((fixture_root / "panels").glob("panel-*.png")))
    if not panels:
        raise RuntimeError("The governed sample panels are missing.")
    expected_summary = str(manifest["expectedSummary"])
    return reference, panels, expected_summary


def result_record(result: VerificationResult, wall_ms: float) -> dict[str, Any]:
    applicable = [check for check in result.checks if check.applicable]
    return {
        "wallMs": round(wall_ms, 3),
        "serverDurationMs": round(result.server_duration_ms, 3),
        "summary": result.summary,
        "checkCount": len(result.checks),
        "applicableCount": len(applicable),
        "allApplicableMatch": all(check.state == "Match" for check in applicable),
    }


def run_warm(
    root: Path,
    reference: ReferenceRecord,
    panels: tuple[Path, ...],
    expected_summary: str,
    count: int,
) -> dict[str, Any]:
    supervisor = WorkerSupervisor(root / "models", build_id="local-performance-validation")
    records: list[dict[str, Any]] = []
    try:
        if not supervisor.start(readiness_timeout=20.0):
            raise RuntimeError("The OCR worker did not become ready.")
        with PeakRssSampler(supervisor) as memory:
            for iteration in range(1, count + 1):
                started = time.perf_counter()
                result = supervisor.run(f"warm-{iteration:02d}", reference, panels)
                record = result_record(result, (time.perf_counter() - started) * 1000)
                record["iteration"] = iteration
                records.append(record)
                print(f"warm {iteration}/{count}: {record['wallMs']} ms", flush=True)
        peak_rss = memory.peak_bytes
        peak_parent_rss = memory.peak_parent_bytes
        peak_worker_rss = memory.peak_worker_bytes
    finally:
        supervisor.stop()
    wall_values = [float(record["wallMs"]) for record in records]
    complete = all(
        record["summary"] == expected_summary and record["checkCount"] == len(contracts().check_ids)
        for record in records
    )
    return {
        "runs": records,
        "runCount": len(records),
        "completeRunCount": sum(
            record["summary"] == expected_summary
            and record["checkCount"] == len(contracts().check_ids)
            for record in records
        ),
        "expectedSummary": expected_summary,
        "p95WallMs": nearest_rank(wall_values, 0.95),
        "maxWallMs": max(wall_values),
        "peakParentAndWorkerRssBytes": peak_rss,
        "peakParentRssBytes": peak_parent_rss,
        "peakWorkerRssBytes": peak_worker_rss,
        "rssThresholdBytesExclusive": WARM_RSS_THRESHOLD_BYTES,
        "thresholdMs": 5000,
        "pass": (
            complete
            and len(records) == count
            and nearest_rank(wall_values, 0.95) <= 5000
            and peak_rss < WARM_RSS_THRESHOLD_BYTES
        ),
    }


def run_cold(
    root: Path,
    reference: ReferenceRecord,
    panels: tuple[Path, ...],
    expected_summary: str,
    count: int,
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    peak_rss = 0
    peak_parent_rss = 0
    peak_worker_rss = 0
    for iteration in range(1, count + 1):
        supervisor = WorkerSupervisor(root / "models", build_id="local-performance-validation")
        started = time.perf_counter()
        try:
            with PeakRssSampler(supervisor) as memory:
                ready = supervisor.start(readiness_timeout=20.0)
                ready_ms = (time.perf_counter() - started) * 1000
                if not ready:
                    raise RuntimeError(f"Cold worker {iteration} did not become ready.")
                result_started = time.perf_counter()
                result = supervisor.run(f"cold-{iteration:02d}", reference, panels)
                result_ms = (time.perf_counter() - result_started) * 1000
                total_ms = (time.perf_counter() - started) * 1000
            peak_rss = max(peak_rss, memory.peak_bytes)
            peak_parent_rss = max(peak_parent_rss, memory.peak_parent_bytes)
            peak_worker_rss = max(peak_worker_rss, memory.peak_worker_bytes)
        finally:
            supervisor.stop()
        record = result_record(result, result_ms)
        record.update(
            {
                "iteration": iteration,
                "readyMs": round(ready_ms, 3),
                "firstResultMs": round(result_ms, 3),
                "readyThroughFirstResultMs": round(total_ms, 3),
            }
        )
        records.append(record)
        print(f"cold {iteration}/{count}: {record['readyThroughFirstResultMs']} ms", flush=True)
    total_values = [float(record["readyThroughFirstResultMs"]) for record in records]
    complete = all(
        record["summary"] == expected_summary and record["checkCount"] == len(contracts().check_ids)
        for record in records
    )
    return {
        "runs": records,
        "runCount": len(records),
        "completeRunCount": sum(
            record["summary"] == expected_summary
            and record["checkCount"] == len(contracts().check_ids)
            for record in records
        ),
        "expectedSummary": expected_summary,
        "p95ReadyThroughFirstResultMs": nearest_rank(total_values, 0.95),
        "maxReadyThroughFirstResultMs": max(total_values),
        "peakParentAndWorkerRssBytes": peak_rss,
        "peakParentRssBytes": peak_parent_rss,
        "peakWorkerRssBytes": peak_worker_rss,
        "rssThresholdBytesExclusive": COLD_RSS_THRESHOLD_BYTES,
        "thresholdMsExclusive": 10000,
        "scope": (
            "Worker spawn, model verification and warmup, readiness, and first governed result"
        ),
        "pass": (
            complete
            and len(records) == count
            and nearest_rank(total_values, 0.95) < 10000
            and peak_rss < COLD_RSS_THRESHOLD_BYTES
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run governed local performance validation.")
    parser.add_argument("--warm-runs", type=int, default=30)
    parser.add_argument("--cold-runs", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/08-validation/evidence/local-performance.json"),
    )
    args = parser.parse_args()
    if args.warm_runs < 1 or args.cold_runs < 1:
        parser.error("Run counts must be positive.")

    root = PROJECT_ROOT
    reference, panels, expected_summary = load_sample(root)
    report: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "measuredAtUtc": datetime.now(UTC).isoformat(),
        "environment": {
            "platform": platform.system(),
            "python": platform.python_version(),
            "logicalCpuCount": os.cpu_count(),
        },
        "sampleCaseId": "S001",
        "warm": run_warm(root, reference, panels, expected_summary, args.warm_runs),
        "cold": run_cold(root, reference, panels, expected_summary, args.cold_runs),
    }
    report["pass"] = report["warm"]["pass"] and report["cold"]["pass"]
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "pass": report["pass"]}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
