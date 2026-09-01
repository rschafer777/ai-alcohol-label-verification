from __future__ import annotations

import importlib.util
import tempfile
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]


def _phase_runner() -> ModuleType:
    path = ROOT / "scripts/run_total_phase_matrix.py"
    specification = importlib.util.spec_from_file_location("run_total_phase_matrix", path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_total_phase_evidence_sanitizes_project_and_temp_paths() -> None:
    runner = _phase_runner()
    project_path = str(ROOT / "backend/tests/test_lifecycle_matrix.py")
    temp_path = str(Path(tempfile.gettempdir()) / "labelverify-phase-matrix-test" / "report.xml")

    observed = runner.sanitized(f"{project_path}\n{temp_path}")

    assert str(ROOT) not in observed
    assert str(Path(tempfile.gettempdir()).resolve()) not in observed
    assert "<PROJECT_ROOT>" in observed
    assert "<TEMP_ROOT>" in observed
