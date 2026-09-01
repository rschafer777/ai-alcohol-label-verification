from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from ops.fetch_models import make_read_only
from scripts.generate_frontend_contract import validate_frontend_contract
from scripts.validate_fixture_corpus import (
    SUMMARY_CLEAN,
    SUMMARY_DIFFERENCE,
    SUMMARY_REVIEW,
    scan_production_hardcoding,
    validate_contracts,
    validate_corpus,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_HASHES = {
    "api-contract-v1.json": "b7eb6b2e0c4082259f01fe5339dc2fe8ca3191a7831b11629c9fa202d852bb47",
    "error-registry-v1.json": "41fa16e582d528e1fe9df7ad13feed557d788daa253bf7f2b628f87dde970fa7",
    "regulatory-rules-v1.json": "6d1c9866738a1b863ff8572c29881195005861b2198c2e364c4b5ff0fbf2e6c2",
    "selected-check-registry-v1.json": (
        "521d7a1dbdb3872086083e92a6f37e459c48ad5471a09f3f92c23472b7dc8b13"
    ),
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_cg001_hashes_counts_and_limits(tmp_path: Path) -> None:
    errors, contracts = validate_contracts(PROJECT_ROOT)
    assert errors == []
    assert contracts["hashes"] == EXPECTED_HASHES
    assert len(contracts["checkIds"]) == 19
    assert len(contracts["errorCodes"]) == 27
    model = tmp_path / "model.onnx"
    model.write_bytes(b"governed model")
    make_read_only(model)
    if os.name != "nt":
        assert model.stat().st_mode & 0o222 == 0


def test_corpus_schema_oracles_counts_and_seal() -> None:
    errors, metrics = validate_corpus(PROJECT_ROOT)
    assert errors == []
    assert metrics["totalCases"] == 30
    assert metrics["developmentCases"] == 24
    assert metrics["holdoutCases"] == 6
    assert metrics["selectedChecks"] == 19
    assert metrics["mutationControls"] == 8


def test_oracle_covers_all_summaries_and_all_selected_checks() -> None:
    manifest = load_json(PROJECT_ROOT / "fixtures" / "corpus-manifest-v1.json")
    registry = load_json(PROJECT_ROOT / "contracts" / "selected-check-registry-v1.json")
    expected_ids = [row["checkId"] for row in registry["checks"]]
    summaries: set[str] = set()
    states: dict[str, set[str]] = {check_id: set() for check_id in expected_ids}
    for case in manifest["cases"]:
        oracle = load_json(PROJECT_ROOT / case["oraclePath"])
        if oracle["outcomeKind"] != "result":
            continue
        summaries.add(oracle["summary"])
        assert [row["checkId"] for row in oracle["checks"]] == expected_ids
        for row in oracle["checks"]:
            if row["applicable"]:
                states[row["checkId"]].add(row["state"])
    assert summaries == {SUMMARY_CLEAN, SUMMARY_REVIEW, SUMMARY_DIFFERENCE}
    assert all(states.values())


def test_corrected_oracle_boundaries_and_non_applicable_states() -> None:
    manifest = load_json(PROJECT_ROOT / "fixtures" / "corpus-manifest-v1.json")
    cases = {case["caseId"]: case for case in manifest["cases"]}

    clean = load_json(PROJECT_ROOT / cases["D001"]["oraclePath"])
    clean_checks = {row["checkId"]: row for row in clean["checks"]}
    assert clean_checks["country"] == {
        "applicable": False,
        "checkId": "country",
        "evidence": "forbidden",
        "minimumAlternatives": 0,
        "mustAppear": False,
        "observedHint": None,
        "reasonClass": "not_applicable",
        "state": "Not verified",
    }
    assert clean_checks["warning_applicability"]["evidence"] == "optional"

    expected_errors = {
        "D019": ("invalid_image", 422),
        "D020": ("unsupported_media_type", 415),
        "D021": ("invalid_panel_count", 422),
        "D022": ("multipart_limit_exceeded", 413),
    }
    for case_id, (code, http) in expected_errors.items():
        oracle = load_json(PROJECT_ROOT / cases[case_id]["oraclePath"])
        assert oracle["error"] == {
            "code": code,
            "http": http,
            "resultMustBeAbsent": True,
        }

    corrupt_panel = PROJECT_ROOT / cases["D019"]["panels"][0]["path"]
    assert corrupt_panel.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_corrected_missing_panel_and_mutation_expectations() -> None:
    manifest = load_json(PROJECT_ROOT / "fixtures" / "corpus-manifest-v1.json")
    cases = {case["caseId"]: case for case in manifest["cases"]}
    oracle = load_json(PROJECT_ROOT / cases["D010"]["oraclePath"])
    checks = {row["checkId"]: row for row in oracle["checks"]}
    expected_missing = {
        "producer",
        "warning_wording",
        "warning_heading_uppercase",
        "warning_heading_emphasis",
        "warning_body_not_bold",
        "warning_separation",
        "warning_continuity",
        "warning_contrast",
        "warning_legibility",
        "warning_physical_size",
    }
    assert all(checks[check_id]["state"] == "Not verified" for check_id in expected_missing)
    assert checks["warning_physical_size"]["reasonClass"] == "unsupported_measurement"
    assert checks["panel_coverage"]["state"] == "Match"
    assert checks["panel_coverage"]["reasonClass"] == "exact"

    plan = load_json(PROJECT_ROOT / "fixtures" / "mutations" / "mutation-plan-v1.json")
    mutations = {row["mutationId"]: row for row in plan["mutations"]}
    assert "producer" in mutations["M007_remove_warning_panel"]["expectedChangedChecks"]
    assert "panel_coverage" not in mutations["M007_remove_warning_panel"]["expectedChangedChecks"]
    severe_blur = mutations["M008_image_blur"]
    assert severe_blur["expectedSummary"] == SUMMARY_REVIEW
    assert set(severe_blur["expectedChangedChecks"]) == expected_missing - {"panel_coverage"} | {
        "brand",
        "class_type",
        "abv",
        "proof",
        "net_contents",
        "image_quality",
        "panel_coverage",
    }


def test_decisive_report_oracle_corrections_follow_contract_capabilities() -> None:
    manifest = load_json(PROJECT_ROOT / "fixtures" / "corpus-manifest-v1.json")
    cases = {case["caseId"]: case for case in manifest["cases"]}

    for case_id in ("D013", "D016", "H004", "H005", "H006"):
        oracle = load_json(PROJECT_ROOT / cases[case_id]["oraclePath"])
        checks = {row["checkId"]: row for row in oracle["checks"]}
        assert checks["class_type"]["state"] == "Match"
        assert checks["class_type"]["reasonClass"] == "safe_equivalence"

    unreadable = load_json(PROJECT_ROOT / cases["D017"]["oraclePath"])
    unreadable_checks = {row["checkId"]: row for row in unreadable["checks"]}
    assert unreadable_checks["warning_applicability"]["state"] == "Match"
    assert unreadable_checks["warning_applicability"]["reasonClass"] == "exact"
    assert unreadable_checks["panel_coverage"]["state"] == "Review"
    assert unreadable_checks["panel_coverage"]["reasonClass"] == "coverage_gap"
    assert unreadable_checks["image_quality"]["state"] == "Not verified"
    assert unreadable_checks["image_quality"]["reasonClass"] == "unreadable"

    missing_back = load_json(PROJECT_ROOT / cases["D018"]["oraclePath"])
    missing_back_checks = {row["checkId"]: row for row in missing_back["checks"]}
    assert missing_back_checks["warning_physical_size"]["state"] == "Not verified"
    assert missing_back_checks["warning_physical_size"]["reasonClass"] == "unsupported_measurement"


def test_holdout_oracles_are_sealed_and_distinct() -> None:
    fixtures = PROJECT_ROOT / "fixtures"
    manifest = load_json(fixtures / "holdout" / "manifest-sealed-v1.json")
    assert manifest["sealed"] is True
    assert manifest["sealedBy"] == "VV-LEAD"
    assert len(manifest["cases"]) == 6
    seal_rows = (fixtures / "holdout" / "SEAL.sha256").read_text(encoding="ascii").splitlines()
    assert len(seal_rows) >= 18
    oracle_hashes = []
    for case in manifest["cases"]:
        assert case["sealed"] is True
        oracle_path = PROJECT_ROOT / case["oraclePath"]
        oracle_hashes.append(hashlib.sha256(oracle_path.read_bytes()).hexdigest())
    assert len(set(oracle_hashes)) == 6


def test_sample_contract_is_exact_and_synthetic() -> None:
    sample = load_json(PROJECT_ROOT / "fixtures" / "sample" / "sample-manifest-v1.json")
    assert sample["sampleContractVersion"] == "1.0.0"
    assert sample["sampleId"] == "old-tom-distillery-v1"
    assert sample["syntheticOnly"] is True
    assert sample["contractHashes"] == EXPECTED_HASHES
    assert len(sample["panels"]) == 2
    assert sample["reference"] == load_json(PROJECT_ROOT / sample["referencePath"])
    assert all((PROJECT_ROOT / panel["path"]).exists() for panel in sample["panels"])


def test_production_has_no_fixture_or_oracle_hardcoding() -> None:
    assert scan_production_hardcoding(PROJECT_ROOT) == []


def test_cg004_frontend_copy_matches_all_four_root_contracts() -> None:
    assert validate_frontend_contract(PROJECT_ROOT) == []
