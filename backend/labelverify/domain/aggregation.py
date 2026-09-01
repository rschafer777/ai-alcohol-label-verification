from __future__ import annotations

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import CheckResult, SummaryState


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
