from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import threading
import time
from collections import Counter
from contextlib import suppress
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psutil  # type: ignore[import-untyped]

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from labelverify.contracts.loader import contracts  # noqa: E402
from labelverify.contracts.models import ReferenceRecord  # noqa: E402
from labelverify.orchestration.supervisor import WorkerSupervisor  # noqa: E402

DEFAULT_THRESHOLDS_SECONDS = {10: 50.0, 20: 100.0, 300: 1500.0}
SUMMARY_CLEAN = "No differences found in checked fields"
RSS_THRESHOLD_BYTES = 2 * 1024 * 1024 * 1024


@dataclass(frozen=True)
class BatchScenario:
    case_id: str
    reference: ReferenceRecord
    panels: tuple[Path, ...]
    expected_summary: str


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


def load_case(root: Path, partition: str, case_id: str) -> BatchScenario:
    case_root = root / "fixtures" / partition / "cases" / case_id
    manifest = json.loads((case_root / "case-manifest.json").read_text(encoding="utf-8"))
    oracle = json.loads((root / manifest["oraclePath"]).read_text(encoding="utf-8"))
    manifest = json.loads((case_root / "case-manifest.json").read_text(encoding="utf-8"))
    reference = ReferenceRecord.model_validate(
        json.loads((root / manifest["referencePath"]).read_text(encoding="utf-8"))
    )
    panels = tuple(root / panel["path"] for panel in manifest["panels"])
    if not panels:
        raise RuntimeError(f"The governed panels are missing for {case_id}.")
    return BatchScenario(case_id, reference, panels, str(oracle["summary"]))


def load_scenarios(root: Path) -> tuple[BatchScenario, ...]:
    return (
        load_case(root, "holdout", "H006"),
        load_case(root, "development", "D001"),
        load_case(root, "development", "D004"),
    )


def run_batch(root: Path, count: int) -> dict[str, Any]:
    scenarios = load_scenarios(root)
    supervisor = WorkerSupervisor(root / "models", build_id="local-batch-validation")
    checkpoints = sorted(point for point in DEFAULT_THRESHOLDS_SECONDS if point <= count)
    summaries: Counter[str] = Counter()
    expected_summaries: Counter[str] = Counter()
    durations_ms: list[float] = []
    request_ids: set[str] = set()
    false_clean_count = 0
    checkpoint_records: dict[str, dict[str, Any]] = {}
    started = time.perf_counter()
    try:
        if not supervisor.start(readiness_timeout=20.0):
            raise RuntimeError("The OCR worker did not become ready.")
        initial_snapshot = asdict(supervisor.snapshot())
        batch_started = time.perf_counter()
        with PeakRssSampler(supervisor) as memory:
            for index in range(1, count + 1):
                scenario = scenarios[(index - 1) % len(scenarios)]
                request_id = f"batch-{index:03d}-{scenario.case_id}"
                if request_id in request_ids:
                    raise RuntimeError(f"Duplicate request ID at batch item {index}")
                request_ids.add(request_id)
                item_started = time.perf_counter()
                result = supervisor.run(request_id, scenario.reference, scenario.panels)
                item_ms = (time.perf_counter() - item_started) * 1000
                durations_ms.append(item_ms)
                summaries[result.summary] += 1
                expected_summaries[scenario.expected_summary] += 1
                if result.summary == SUMMARY_CLEAN and scenario.expected_summary != SUMMARY_CLEAN:
                    false_clean_count += 1
                if (
                    result.summary != scenario.expected_summary
                    or len(result.checks) != len(contracts().check_ids)
                ):
                    raise RuntimeError(f"Batch item {index} returned an unexpected result")
                if index in checkpoints:
                    elapsed_seconds = time.perf_counter() - batch_started
                    threshold = DEFAULT_THRESHOLDS_SECONDS[index]
                    checkpoint_records[str(index)] = {
                        "elapsedSeconds": round(elapsed_seconds, 3),
                        "thresholdSeconds": threshold,
                        "pass": elapsed_seconds <= threshold,
                    }
                if index % 10 == 0 or index == count:
                    elapsed = time.perf_counter() - batch_started
                    print(
                        f"batch {index}/{count}: {elapsed:.3f} seconds elapsed",
                        flush=True,
                    )
        peak_rss_bytes = memory.peak_bytes
        peak_parent_rss_bytes = memory.peak_parent_bytes
        peak_worker_rss_bytes = memory.peak_worker_bytes
        final_snapshot = asdict(supervisor.snapshot())
    finally:
        supervisor.stop()
    elapsed_seconds = time.perf_counter() - batch_started
    total_seconds = time.perf_counter() - started
    return {
        "requestedCount": count,
        "completedCount": len(durations_ms),
        "uniqueRequestIdCount": len(request_ids),
        "scenarioCaseIds": [scenario.case_id for scenario in scenarios],
        "expectedSummaryCounts": dict(expected_summaries),
        "summaryCounts": dict(summaries),
        "falseCleanCount": false_clean_count,
        "elapsedSeconds": round(elapsed_seconds, 3),
        "totalIncludingReadinessSeconds": round(total_seconds, 3),
        "averageItemMs": round(sum(durations_ms) / len(durations_ms), 3),
        "maximumItemMs": round(max(durations_ms), 3),
        "peakParentAndWorkerRssBytes": peak_rss_bytes,
        "peakParentRssBytes": peak_parent_rss_bytes,
        "peakWorkerRssBytes": peak_worker_rss_bytes,
        "rssThresholdBytesExclusive": RSS_THRESHOLD_BYTES,
        "initialSupervisorSnapshot": initial_snapshot,
        "finalSupervisorSnapshot": final_snapshot,
        "checkpoints": checkpoint_records,
        "pass": (
            len(durations_ms) == count
            and len(request_ids) == count
            and summaries == expected_summaries
            and false_clean_count == 0
            and final_snapshot["active_jobs"] == 0
            and final_snapshot["timeouts"] == 0
            and final_snapshot["restarts"] == 0
            and peak_rss_bytes < RSS_THRESHOLD_BYTES
            and all(record["pass"] for record in checkpoint_records.values())
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run governed local batch validation.")
    parser.add_argument("--count", type=int, default=300)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/08-validation/evidence/local-batch-performance.json"),
    )
    args = parser.parse_args()
    if args.count < 1 or args.count > 300:
        parser.error("Count must be from 1 through 300.")

    report: dict[str, Any] = {
        "schemaVersion": "1.0.0",
        "measuredAtUtc": datetime.now(UTC).isoformat(),
        "environment": {
            "platform": platform.system(),
            "python": platform.python_version(),
            "logicalCpuCount": os.cpu_count(),
        },
        "executionModel": "one warmed local OCR worker; sequential applications",
        "result": run_batch(PROJECT_ROOT, args.count),
    }
    report["pass"] = report["result"]["pass"]
    output = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "pass": report["pass"]}, indent=2))
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
