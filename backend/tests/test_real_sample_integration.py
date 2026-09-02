from __future__ import annotations

import json
import time
from pathlib import Path

from labelverify.contracts.models import ReferenceRecord
from labelverify.orchestration.supervisor import WorkerSupervisor

PIXEL_SUPPORTED_WARNING_NONMATCHES = {
    "warning_wording": "Review",
    "warning_physical_size": "Not verified",
}


def test_warmed_supervised_sample_finishes_before_worker_deadline() -> None:
    project_root = Path(__file__).resolve().parents[2]
    reference = ReferenceRecord.model_validate(
        json.loads((project_root / "fixtures" / "sample" / "reference.json").read_text())
    )
    panels = tuple(
        project_root / "fixtures" / "sample" / "panels" / f"panel-{index}.png" for index in (1, 2)
    )
    supervisor = WorkerSupervisor(
        project_root / "models",
        worker_deadline_seconds=9.0,
        build_id="real-sample-integration",
    )
    try:
        assert supervisor.start(readiness_timeout=15.0)
        started = time.perf_counter()
        result = supervisor.run("real-sample", reference, panels)
        elapsed = time.perf_counter() - started
    finally:
        supervisor.stop()

    assert elapsed < 9.0
    assert result.server_duration_ms < 5_000
    assert result.stage_timings.ocr_ms < 5_000
    assert len(result.checks) == 19
    assert result.summary == "Review needed"
    nonmatches = {
        check.check_id: check.state
        for check in result.checks
        if check.applicable and check.state != "Match"
    }
    assert nonmatches == PIXEL_SUPPORTED_WARNING_NONMATCHES


def test_governed_six_panel_case_finishes_before_worker_deadline() -> None:
    project_root = Path(__file__).resolve().parents[2]
    manifest = json.loads((project_root / "fixtures" / "corpus-manifest-v1.json").read_text())
    matching_cases = [
        case
        for case in manifest["cases"]
        if "six_panel" in case["scenarioTags"] and case["expectedKind"] == "result"
    ]
    assert len(matching_cases) == 1
    case = matching_cases[0]
    reference = ReferenceRecord.model_validate(
        json.loads((project_root / case["referencePath"]).read_text())
    )
    panels = tuple(project_root / panel["path"] for panel in case["panels"])
    assert len(panels) == 6
    supervisor = WorkerSupervisor(
        project_root / "models",
        worker_deadline_seconds=9.0,
        build_id="governed-six-panel-integration",
    )
    try:
        assert supervisor.start(readiness_timeout=15.0)
        started = time.perf_counter()
        result = supervisor.run("governed-six-panel", reference, panels)
        elapsed = time.perf_counter() - started
        reversed_started = time.perf_counter()
        reversed_result = supervisor.run(
            "governed-six-panel-reversed", reference, tuple(reversed(panels))
        )
        reversed_elapsed = time.perf_counter() - reversed_started
    finally:
        supervisor.stop()

    assert elapsed < 9.0
    assert result.server_duration_ms < 9_000
    assert result.stage_timings.ocr_ms < 9_000
    assert len(result.checks) == 19
    assert result.summary == "Review needed"
    nonmatches = {
        check.check_id: check.state
        for check in result.checks
        if check.applicable and check.state != "Match"
    }
    assert nonmatches == PIXEL_SUPPORTED_WARNING_NONMATCHES
    assert reversed_elapsed < 9.0
    assert reversed_result.server_duration_ms < 9_000
    assert reversed_result.stage_timings.ocr_ms < 9_000
    assert reversed_result.summary == result.summary
    assert [
        (check.check_id, check.applicable, check.state, check.reason_code)
        for check in reversed_result.checks
    ] == [
        (check.check_id, check.applicable, check.state, check.reason_code)
        for check in result.checks
    ]
