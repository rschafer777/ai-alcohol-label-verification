from __future__ import annotations

from typing import Literal

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import CheckResult, ReviewCause, SummaryState


class IncompleteCheckSetError(ValueError):
    """Raised when selected-check aggregation is incomplete or duplicated."""


def validate_check_set(checks: list[CheckResult]) -> None:
    expected = contracts().check_ids
    actual = tuple(item.check_id for item in checks)
    if len(actual) != len(set(actual)):
        raise IncompleteCheckSetError("Duplicate selected check")
    if actual != expected:
        raise IncompleteCheckSetError("Selected checks are missing, extra, or out of order")


def aggregate(checks: list[CheckResult]) -> SummaryState:
    validate_check_set(checks)
    applicable = [item for item in checks if item.applicable]
    if not applicable:
        raise IncompleteCheckSetError("At least one selected check must be applicable")
    allowed_states = {"Match", "Mismatch", "Review", "Not verified"}
    if any(item.state not in allowed_states for item in applicable):
        raise IncompleteCheckSetError("Unknown check state")
    if any(item.state == "Mismatch" for item in applicable):
        return "Differences detected"
    if any(item.state in {"Review", "Not verified"} for item in applicable):
        return "Review needed"
    if all(item.state == "Match" for item in applicable):
        return "No differences found in checked fields"
    raise IncompleteCheckSetError("Unknown check state")  # pragma: no cover


_CONFLICT_MARKERS = ("conflict", "ambiguous", "several_candidates", "multiple")
_PRESENTATION_MARKERS = (
    "presentation",
    "contrast",
    "legibility",
    "bold",
    "weight",
    "separation",
    "continuous",
    "size",
    "scale",
)
_OCR_MARKERS = ("ocr", "unreadable", "punctuation", "fragment", "near_match")
_CONTEXT_MARKERS = ("context", "import_status", "applicability", "formula", "state_law")
_MISSING_MARKERS = ("not_found", "missing", "absent", "not_read", "incomplete")


def review_causes(checks: list[CheckResult], summary: SummaryState) -> list[ReviewCause]:
    """Explain every row that makes the overall result require human review."""

    if summary != "Review needed":
        return []
    causes: list[ReviewCause] = []
    for check in checks:
        if not check.applicable or check.state not in {"Review", "Not verified"}:
            continue
        reason = check.reason_code.casefold()
        category: Literal[
            "missing_evidence",
            "ocr_uncertainty",
            "presentation_uncertainty",
            "trusted_context_missing",
            "conflicting_evidence",
            "policy_review",
        ]
        if any(marker in reason for marker in _CONFLICT_MARKERS):
            category = "conflicting_evidence"
        elif any(marker in reason for marker in _PRESENTATION_MARKERS):
            category = "presentation_uncertainty"
        elif any(marker in reason for marker in _OCR_MARKERS):
            category = "ocr_uncertainty"
        elif any(marker in reason for marker in _CONTEXT_MARKERS):
            category = "trusted_context_missing"
        elif any(marker in reason for marker in _MISSING_MARKERS):
            category = "missing_evidence"
        else:
            category = "policy_review"
        causes.append(
            ReviewCause(
                checkId=check.check_id,
                category=category,
                reasonCode=check.reason_code,
                evidenceRef=check.evidence_ref,
            )
        )
    return causes
