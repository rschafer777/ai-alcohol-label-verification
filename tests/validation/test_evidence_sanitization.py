from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]


def _privacy_runner() -> ModuleType:
    path = ROOT / "scripts/scan_public_personal_details.py"
    specification = importlib.util.spec_from_file_location("scan_public_personal_details", path)
    assert specification is not None and specification.loader is not None
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_personal_detail_scan_parses_terms_and_finds_case_insensitively() -> None:
    privacy_runner = _privacy_runner()
    terms = privacy_runner.parse_terms('["ExamplePerson", "Second Example"]')
    assert privacy_runner.find_matches("roles only", terms) == []
    assert privacy_runner.find_matches("ExamplePerson appears", terms) == [0]
    assert privacy_runner.find_matches("second example appears", terms) == [1]
