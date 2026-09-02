from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts import validate_test_images as target


def oracle_document(
    image_paths: list[Path],
    hashes: dict[str, str],
    cases: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schemaVersion": "1.0",
        "oracleMethod": "Visual review independent of machine evaluation",
        "reviewerRole": "test reviewer",
        "reviewProcedureId": "TEST-V1",
        "reviewProcedureVersion": "1.0",
        "reviewedAtUtc": "2026-09-01T00:00:00Z",
        "machineOutcomesAvailableDuringReview": True,
        "amendedAtUtc": "2026-09-01T00:01:00Z",
        "amendmentReason": "test policy clarification",
        "machineOutcomesUsedForClassification": False,
        "authorityVersion": "test-authority-v1",
        "corpusInventorySha256": target.inventory_digest(image_paths, hashes),
        "corpusUseApproval": "local test only",
        "cases": cases,
    }


def write_oracle(path: Path, document: dict[str, Any]) -> None:
    path.write_text(json.dumps(document), encoding="utf-8")


def case(filename: str, disposition: str = "PASS") -> dict[str, Any]:
    return {
        "filename": filename,
        "expectedDisposition": disposition,
        "reason": "governed reason",
        "scenarioTags": ["distilled_spirits"],
    }


def result(
    oracle: str,
    harness: str,
    comparison: str,
    *,
    scope: str = "IN_SCOPE_ALL_BEVERAGES",
) -> dict[str, Any]:
    row = {
        "filename": "case.jpg",
        "scope": scope,
        "oracleDisposition": oracle,
        "harnessDisposition": harness,
        "comparison": comparison,
        "durationMs": 1.0,
        "oracleReason": "reason",
        "harnessReasons": ["finding"],
    }
    if oracle == "PASS":
        row["candidates"] = {
            field: {"status": "Found"}
            for field in ("brand", "class_type", "abv", "net_contents")
        }
        row["warningObservation"] = {"headingDetected": True, "bodyDetected": True}
    return row


def test_load_oracle_requires_exact_bijection(tmp_path: Path) -> None:
    image_paths = [tmp_path / "a.jpg", tmp_path / "b.jpg"]
    hashes = {"a.jpg": "a" * 64, "b.jpg": "b" * 64}
    oracle_path = tmp_path / "oracle.json"
    document = oracle_document(image_paths, hashes, [case("a.jpg")])
    write_oracle(oracle_path, document)

    with pytest.raises(target.ValidationInputError, match="bijection"):
        target.load_oracle(oracle_path, image_paths, hashes)


def test_load_oracle_rejects_duplicate_and_invalid_disposition(tmp_path: Path) -> None:
    image_paths = [tmp_path / "a.jpg"]
    hashes = {"a.jpg": "a" * 64}
    oracle_path = tmp_path / "oracle.json"
    duplicate = oracle_document(image_paths, hashes, [case("a.jpg"), case("a.jpg")])
    write_oracle(oracle_path, duplicate)
    with pytest.raises(target.ValidationInputError, match="Duplicate"):
        target.load_oracle(oracle_path, image_paths, hashes)

    invalid = oracle_document(image_paths, hashes, [case("a.jpg", "MAYBE")])
    write_oracle(oracle_path, invalid)
    with pytest.raises(target.ValidationInputError, match="disposition"):
        target.load_oracle(oracle_path, image_paths, hashes)


def test_load_oracle_rejects_inventory_hash_mismatch(tmp_path: Path) -> None:
    image_paths = [tmp_path / "a.jpg"]
    hashes = {"a.jpg": "a" * 64}
    oracle_path = tmp_path / "oracle.json"
    document = oracle_document(image_paths, hashes, [case("a.jpg")])
    document["corpusInventorySha256"] = "0" * 64
    write_oracle(oracle_path, document)

    with pytest.raises(target.ValidationInputError, match="inventory hash"):
        target.load_oracle(oracle_path, image_paths, hashes)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("reviewerRole", "", "non-empty string"),
        ("reviewProcedureId", 7, "non-empty string"),
        ("reviewedAtUtc", "2026-09-01", "valid UTC timestamp"),
        ("corpusUseApproval", None, "non-empty string"),
        (
            "machineOutcomesUsedForClassification",
            True,
            "independent of machine outcomes",
        ),
        (
            "machineOutcomesAvailableDuringReview",
            "yes",
            "whether machine outcomes were available",
        ),
    ],
)
def test_load_oracle_rejects_malformed_metadata(
    tmp_path: Path, field: str, value: Any, message: str
) -> None:
    image_paths = [tmp_path / "a.jpg"]
    hashes = {"a.jpg": "a" * 64}
    oracle_path = tmp_path / "oracle.json"
    document = oracle_document(image_paths, hashes, [case("a.jpg")])
    document[field] = value
    write_oracle(oracle_path, document)

    with pytest.raises(target.ValidationInputError, match=message):
        target.load_oracle(oracle_path, image_paths, hashes)


def test_oracle_accepts_needs_review_as_distinct_from_visible_defect(tmp_path: Path) -> None:
    image_paths = [tmp_path / "a.jpg"]
    hashes = {"a.jpg": "a" * 64}
    oracle_path = tmp_path / "oracle.json"
    document = oracle_document(image_paths, hashes, [case("a.jpg", "NEEDS_REVIEW")])
    write_oracle(oracle_path, document)

    oracle, _ = target.load_oracle(oracle_path, image_paths, hashes)

    assert oracle["a.jpg"]["expectedDisposition"] == "NEEDS_REVIEW"


def test_summary_fails_closed_for_false_clear() -> None:
    rows = [result("DO_NOT_PASS", "PASS", "FALSE_CLEAR")]
    summary = target.build_summary(rows, expected_count=1)

    assert summary["diagnosticGates"] == {
        "evidenceCompletePass": True,
        "selectedProfileZeroFalseClearPass": False,
        "selectedProfileZeroFalseRejectionPass": True,
        "selectedProfileExpectedDefectContainmentPass": False,
        "selectedProfileExpectedReviewContainmentPass": True,
        "selectedProfileExpectedReviewRecognitionPass": True,
        "selectedProfileExpectedClearRecognitionPass": True,
        "selectedProfilePositiveEvidenceRecognitionPass": False,
        "selectedProfilePositiveEvidenceRecognitionPercent": None,
        "selectedProfilePositiveEvidenceRecognitionCount": 0,
        "selectedProfileExpectedClearCount": 0,
        "diagnosticPerformancePass": True,
        "overallDiagnosticPass": False,
        "status": "FAIL",
    }


def test_summary_reports_expected_clear_recognition_without_forcing_unsafe_clearance() -> None:
    rows = [result("PASS", "NEEDS_REVIEW", "CONSERVATIVE_NON_CLEAR")]
    summary = target.build_summary(rows, expected_count=1)

    assert summary["selectedProfile"]["metrics"]["expectedClearRecognitionPercent"] == 0
    assert summary["diagnosticGates"]["selectedProfileExpectedClearRecognitionPass"] is False
    assert summary["diagnosticGates"]["overallDiagnosticPass"] is True


def test_oracle_pass_to_harness_rejection_is_an_explicit_blocking_failure() -> None:
    rows = [{"filename": "case.jpg", "harnessDisposition": "DO_NOT_PASS"}]
    oracle = {
        "case.jpg": {
            "expectedDisposition": "PASS",
            "reason": "governed reason",
            "scenarioTags": ["distilled_spirits"],
        }
    }

    target.add_oracle(rows, oracle)
    rows[0].update(
        {
            "durationMs": 1.0,
            "oracleReason": "governed reason",
            "harnessReasons": ["finding"],
        }
    )
    summary = target.build_summary(rows, expected_count=1)

    assert rows[0]["comparison"] == "FALSE_REJECTION"
    assert summary["selectedProfile"]["metrics"]["falseRejectionCount"] == 1
    assert summary["diagnosticGates"]["selectedProfileZeroFalseRejectionPass"] is False
    assert summary["diagnosticGates"]["overallDiagnosticPass"] is False


def test_summary_passes_only_complete_selected_profile_matrix() -> None:
    rows = [
        result("PASS", "PASS", "TRUE_CLEAR"),
        result("DO_NOT_PASS", "DO_NOT_PASS", "TRUE_DEFECT"),
        result("NEEDS_REVIEW", "NEEDS_REVIEW", "TRUE_REVIEW"),
    ]
    summary = target.build_summary(rows, expected_count=3)

    assert summary["diagnosticGates"]["overallDiagnosticPass"] is True
    assert summary["diagnosticGates"]["status"] == "PASS"


def test_report_uses_calculated_counts_and_partial_harness_boundary() -> None:
    rows = [result("DO_NOT_PASS", "NEEDS_REVIEW", "CONSERVATIVE_DEFECT_HOLD")]
    payload = {
        "generatedAt": "2026-09-01T00:00:00Z",
        "summary": target.build_summary(rows, expected_count=1),
        "results": rows,
    }

    report = target.build_report(payload)

    assert "1 of 1 expected defects" in report
    assert "partial local image-layer diagnostic" in report
    assert "does not establish full-build safety" in report
    assert "all 22 expected failures" not in report
    assert "clears no images" not in report
    assert "DO_NOT_PASS is reserved for a visible deterministic defect" in report
    assert "uncertainty remains NEEDS_REVIEW" in report


def test_report_uses_actual_nonzero_clear_count_when_recognition_fails() -> None:
    rows = [
        result("PASS", "PASS", "TRUE_CLEAR"),
        result("PASS", "NEEDS_REVIEW", "CONSERVATIVE_NON_CLEAR"),
    ]
    payload = {
        "generatedAt": "2026-09-01T00:00:00Z",
        "summary": target.build_summary(rows, expected_count=2),
        "results": rows,
    }

    report = target.build_report(payload)

    assert (
        "Automatic clear recognition was not observed: "
        "1 of 2 visual-pass cases cleared"
    ) in report
    assert "clears no images" not in report


def test_report_describes_a_complete_matrix_as_passed() -> None:
    rows = [
        result("PASS", "PASS", "TRUE_CLEAR"),
        result("DO_NOT_PASS", "DO_NOT_PASS", "TRUE_DEFECT"),
        result("NEEDS_REVIEW", "NEEDS_REVIEW", "TRUE_REVIEW"),
    ]
    payload = {
        "generatedAt": "2026-09-01T00:00:00Z",
        "summary": target.build_summary(rows, expected_count=3),
        "results": rows,
    }

    report = target.build_report(payload)

    assert "safety containment observation passed" in report
    assert "Automatic clear recognition was observed: 1 of 1 visual-pass cases cleared" in report
    assert "diagnostic passes its completeness, safety-containment" in report


def test_unreadable_image_requires_review_instead_of_label_rejection() -> None:
    class MissingField:
        status = "Not found"

    class Warning:
        source_unreadable = True
        heading = None
        body = None
        full_text = None
        punctuation_normalized = False
        heading_evidence = None
        body_evidence = None
        heading_bold = None
        body_bold = None
        separated = None
        continuous = None
        contrast_sufficient = None
        legible = None
        physical_size_mm = None
        reliable_scale = False
        scale_evidence = None

    class Observed:
        warning = Warning()

        @staticmethod
        def field(_name: str) -> MissingField:
            return MissingField()

    disposition, reasons, _ = target.evaluate_harness(Observed(), "Unreadable")

    assert disposition == "NEEDS_REVIEW"
    assert "additional evidence" in reasons[0]
