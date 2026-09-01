from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.validate_production_oracle import (
    compare_error,
    compare_result,
    report_hashes,
    verify_model_assets,
)


def checks() -> list[str]:
    registry = json.loads(
        Path("contracts/selected-check-registry-v1.json").read_text(encoding="utf-8")
    )
    return [row["checkId"] for row in registry["checks"]]


def exact_pair() -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    ordered = checks()
    oracle_rows = []
    actual_rows = []
    evidence = []
    for index, check_id in enumerate(ordered):
        rule = "required" if index == 0 else "optional"
        evidence_ref = None
        if rule == "required":
            evidence_ref = f"ev_{check_id}"
            evidence.append({"evidenceId": evidence_ref})
        oracle_rows.append(
            {
                "checkId": check_id,
                "applicable": True,
                "state": "Match",
                "evidence": rule,
                "minimumAlternatives": 0,
            }
        )
        actual_rows.append(
            {
                "checkId": check_id,
                "applicable": True,
                "state": "Match",
                "evidenceRef": evidence_ref,
                "alternatives": [],
            }
        )
    oracle = {"summary": "No differences found in checked fields", "checks": oracle_rows}
    actual = {
        "summary": "No differences found in checked fields",
        "checks": actual_rows,
        "evidence": evidence,
    }
    return actual, oracle, ordered


def test_compare_result_accepts_exact_order_state_applicability_and_evidence() -> None:
    actual, oracle, ordered = exact_pair()
    assert compare_result("D001", actual, oracle, ordered) == []


def test_compare_result_reports_summary_state_applicability_and_evidence() -> None:
    actual, oracle, ordered = exact_pair()
    actual["summary"] = "Review needed"
    actual["checks"][0]["state"] = "Review"
    actual["checks"][0]["applicable"] = False
    actual["checks"][0]["evidenceRef"] = None
    categories = {
        item["category"] for item in compare_result("D001", actual, oracle, ordered)
    }
    assert categories == {"summary", "state", "applicable", "evidence_required"}


def test_compare_result_reports_order_count_and_missing_evidence_target() -> None:
    actual, oracle, ordered = exact_pair()
    actual["checks"][0], actual["checks"][1] = actual["checks"][1], actual["checks"][0]
    actual["checks"] = actual["checks"][:-1]
    actual["evidence"] = []
    categories = {
        item["category"] for item in compare_result("D001", actual, oracle, ordered)
    }
    assert {"production_order", "check_count"} <= categories


def test_compare_result_enforces_forbidden_evidence_and_minimum_alternatives() -> None:
    actual, oracle, ordered = exact_pair()
    oracle["checks"][1]["evidence"] = "forbidden"
    oracle["checks"][2]["minimumAlternatives"] = 2
    actual["checks"][1]["evidenceRef"] = "ev_forbidden"
    actual["checks"][2]["alternatives"] = [{"evidenceRef": "ev_one"}]
    actual["evidence"].extend([{"evidenceId": "ev_forbidden"}, {"evidenceId": "ev_one"}])
    categories = {
        item["category"] for item in compare_result("D001", actual, oracle, ordered)
    }
    assert categories == {"evidence_forbidden", "alternatives"}


def test_compare_error_requires_exact_status_code_and_result_absence() -> None:
    oracle = {
        "error": {"http": 422, "code": "invalid_image", "resultMustBeAbsent": True}
    }
    assert compare_error("D019", 422, {"code": "invalid_image"}, oracle) == []
    failures = compare_error(
        "D019",
        500,
        {"code": "internal_error", "summary": "Review needed"},
        oracle,
    )
    assert {item["category"] for item in failures} == {
        "http_status",
        "error_code",
        "result_absence",
    }


def test_verify_model_assets_checks_manifest_registry_and_file_hashes(tmp_path: Path) -> None:
    model_root = tmp_path / "models"
    model_root.mkdir()
    content = b"governed-model"
    expected_hash = hashlib.sha256(content).hexdigest()
    (model_root / "model.onnx").write_bytes(content)
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "artifacts": [
                    {"filename": "model.onnx", "sha256": expected_hash},
                ]
            }
        ),
        encoding="utf-8",
    )
    records, errors = verify_model_assets(
        model_root,
        manifest,
        {"model.onnx": expected_hash},
    )
    assert errors == []
    assert records[0]["matches"] is True
    (model_root / "model.onnx").write_bytes(b"changed")
    _, errors = verify_model_assets(model_root, manifest, {"model.onnx": expected_hash})
    assert errors == ["Model hash mismatch: model.onnx"]


def test_report_snapshot_binds_transitive_production_source() -> None:
    snapshot = report_hashes(Path.cwd(), [])

    production_source = snapshot["productionSource"]
    assert "backend/labelverify/extraction/rapidocr_adapter.py" in production_source
    assert "backend/labelverify/domain/warnings.py" in production_source
    assert "backend/labelverify/orchestration/supervisor.py" in production_source
    assert "scripts/generate_fixture_corpus.py" in production_source
    assert all(len(value) == 64 for value in production_source.values())
