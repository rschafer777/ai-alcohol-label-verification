from __future__ import annotations

from typing import Any

from scripts.validate_product_corpus import classify_reason, compare_product_result


def row(
    check_id: str,
    reason_code: str,
    *,
    state: str = "Match",
    observed: str | None = None,
    reference: str | None = None,
) -> dict[str, Any]:
    return {
        "checkId": check_id,
        "applicable": True,
        "state": state,
        "reasonCode": reason_code,
        "observedDisplay": observed,
        "referenceDisplay": reference,
    }


def test_classify_reason_uses_independent_taxonomy() -> None:
    assert classify_reason(row("brand", "exact_match")) == "exact"
    assert classify_reason(row("brand", "case_variation")) == "case_variation"
    assert classify_reason(row("brand", "ambiguous_candidates")) == "ambiguous"
    assert classify_reason(row("brand", "observed_not_found")) == "missing"
    assert classify_reason(row("image_quality", "image_quality_uncertain")) == (
        "quality_degradation"
    )


def test_numeric_unit_conversion_is_safe_equivalence() -> None:
    value = row(
        "net_contents",
        "numeric_match",
        observed="0.75 L",
        reference="750.0 mL",
    )
    assert classify_reason(value) == "safe_equivalence"


def test_compare_product_result_reports_reason_class_difference() -> None:
    check_ids = [f"check_{index:02d}" for index in range(19)]
    actual_rows = []
    oracle_rows = []
    evidence = []
    for index, check_id in enumerate(check_ids):
        evidence_id = f"ev_case_panel-1_{index:02d}"
        evidence.append({"evidenceId": evidence_id})
        actual_rows.append(
            {
                **row(check_id, "exact_match"),
                "evidenceRef": evidence_id,
                "alternatives": [],
            }
        )
        oracle_rows.append(
            {
                "checkId": check_id,
                "applicable": True,
                "state": "Match",
                "reasonClass": "exact",
                "evidence": "required",
                "minimumAlternatives": 0,
            }
        )
    oracle_rows[0]["reasonClass"] = "case_variation"
    actual = {
        "summary": "No differences found in checked fields",
        "checks": actual_rows,
        "evidence": evidence,
    }
    oracle = {
        "summary": "No differences found in checked fields",
        "checks": oracle_rows,
    }
    failures = compare_product_result("D999", actual, oracle, check_ids)
    assert [item["category"] for item in failures] == ["reason_class"]
