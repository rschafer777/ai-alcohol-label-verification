from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from labelverify.contracts.models import (
    Alternative,
    Candidate,
    CandidateSet,
    CheckResult,
    CheckState,
)
from labelverify.domain.normalize import (
    casefolded,
    parse_abv,
    parse_proof,
    parse_volume_ml,
    punctuation_folded,
    reference_volume_ml,
    whitespace,
)

POLICY_VERSION = "1.0.0"
AUTOMATED = "automated_selected_check"


def _result(
    check_id: str,
    label: str,
    state: CheckState,
    reason_code: str,
    reason_text: str,
    *,
    applicable: bool = True,
    reference: str | None = None,
    observed: str | None = None,
    candidate: Candidate | None = None,
    candidates: list[Candidate] | None = None,
    capability: str = AUTOMATED,
) -> CheckResult:
    material = candidates or []
    return CheckResult(
        checkId=check_id,
        label=label,
        applicable=applicable,
        referenceDisplay=reference,
        observedDisplay=observed,
        state=state,
        reasonCode=reason_code,
        reasonText=reason_text,
        evidenceRef=candidate.evidence.evidence_id if candidate else None,
        alternatives=[
            Alternative(value=item.value, evidenceRef=item.evidence.evidence_id)
            for item in material
        ],
        capability=capability,
        policyVersion=POLICY_VERSION,
    )


def _absent(
    check_id: str, label: str, reference: str | None, candidate_set: CandidateSet
) -> CheckResult | None:
    if candidate_set.status == "Unreadable":
        return _result(
            check_id,
            label,
            "Not verified",
            "observed_unreadable",
            "The label evidence is not readable enough to verify this field",
            reference=reference,
        )
    if candidate_set.status == "Not found":
        return _result(
            check_id,
            label,
            "Not verified",
            "observed_not_found",
            "No readable label evidence was found for this field",
            reference=reference,
        )
    if candidate_set.status == "Ambiguous":
        return _result(
            check_id,
            label,
            "Review",
            "ambiguous_candidates",
            "More than one plausible observed value requires review",
            reference=reference,
            observed="; ".join(item.value for item in candidate_set.candidates),
            candidate=candidate_set.candidates[0],
            candidates=candidate_set.candidates,
        )
    return None


def compare_text(
    check_id: str,
    label: str,
    reference: str,
    candidate_set: CandidateSet,
    *,
    safe_equivalence: Callable[[str, str], bool] | None = None,
) -> CheckResult:
    absent = _absent(check_id, label, reference, candidate_set)
    if absent:
        return absent
    candidate = candidate_set.candidates[0]
    observed = candidate.value
    if observed == reference:
        return _result(
            check_id,
            label,
            "Match",
            "exact_match",
            "The observed value exactly matches the reference",
            reference=reference,
            observed=observed,
            candidate=candidate,
        )
    if safe_equivalence and safe_equivalence(reference, observed):
        return _result(
            check_id,
            label,
            "Match",
            "safe_representation_match",
            "The observed value uses an explicitly safe equivalent representation",
            reference=reference,
            observed=observed,
            candidate=candidate,
        )
    if casefolded(observed) == casefolded(reference):
        return _result(
            check_id,
            label,
            "Review",
            "case_variation",
            "The value differs only by capitalization and requires reviewer judgment",
            reference=reference,
            observed=observed,
            candidate=candidate,
        )
    if punctuation_folded(observed) == punctuation_folded(reference):
        return _result(
            check_id,
            label,
            "Review",
            "punctuation_variation",
            "The value differs by punctuation and requires reviewer judgment",
            reference=reference,
            observed=observed,
            candidate=candidate,
        )
    return _result(
        check_id,
        label,
        "Mismatch",
        "definite_difference",
        "Readable label evidence differs from the reference",
        reference=reference,
        observed=observed,
        candidate=candidate,
    )


def compare_class(reference: str, candidates: CandidateSet) -> CheckResult:
    def safe(left: str, right: str) -> bool:
        normalized_left = whitespace(left)
        normalized_right = whitespace(right)
        if normalized_left == normalized_right:
            return True
        return _without_terminal_period(normalized_left) == _without_terminal_period(
            normalized_right
        )

    result = compare_text("class_type", "Class/type", reference, candidates, safe_equivalence=safe)
    if result.state == "Mismatch" and candidates.status == "Found":
        left = set(punctuation_folded(reference).split())
        right = set(punctuation_folded(candidates.candidates[0].value).split())
        if left and right and (left < right or right < left):
            result.state = "Review"
            result.reason_code = "incomplete_plausible_designation"
            result.reason_text = (
                "The observed designation is incomplete or expanded and requires review"
            )
    return result


def _without_terminal_period(value: str) -> str:
    if value.endswith(".") and not value.endswith(".."):
        return value[:-1].rstrip()
    return value


def compare_numeric(
    check_id: str,
    label: str,
    reference: Decimal,
    candidates: CandidateSet,
    parser: Callable[[str], Decimal | None],
    reference_display: str,
) -> CheckResult:
    absent = _absent(check_id, label, reference_display, candidates)
    if absent:
        return absent
    candidate = candidates.candidates[0]
    observed_value = parser(candidate.value)
    if observed_value is None:
        return _result(
            check_id,
            label,
            "Review",
            "ambiguous_numeric_parse",
            "The observed numeric value could not be parsed unambiguously",
            reference=reference_display,
            observed=candidate.value,
            candidate=candidate,
        )
    if observed_value == reference:
        return _result(
            check_id,
            label,
            "Match",
            "numeric_match",
            "The parsed observed value matches the reference",
            reference=reference_display,
            observed=candidate.value,
            candidate=candidate,
        )
    return _result(
        check_id,
        label,
        "Mismatch",
        "numeric_difference",
        "The parsed observed value differs from the reference",
        reference=reference_display,
        observed=candidate.value,
        candidate=candidate,
    )


def compare_abv(reference: Decimal, candidates: CandidateSet) -> CheckResult:
    return compare_numeric(
        "abv", "Alcohol content", reference, candidates, parse_abv, f"{reference}%"
    )


def compare_proof(
    reference_proof: Decimal | None,
    reference_abv: Decimal,
    candidates: CandidateSet,
) -> CheckResult:
    if reference_proof is None and candidates.status == "Not found":
        return _result(
            "proof",
            "Proof",
            "Not verified",
            "not_applicable",
            "Proof is not present in the reference or readable label evidence",
            applicable=False,
        )
    expected = reference_proof if reference_proof is not None else reference_abv * Decimal(2)
    result = compare_numeric(
        "proof", "Proof", expected, candidates, parse_proof, f"{expected} proof"
    )
    if result.state == "Match" and reference_proof is None:
        result.reason_code = "proof_abv_relationship_match"
        result.reason_text = "Observed proof matches the two-times-ABV relationship"
    if reference_proof is not None and reference_proof != reference_abv * Decimal(2):
        result.state = "Review"
        result.reason_code = "reference_abv_proof_inconsistent"
        result.reason_text = "The reference ABV and proof relationship requires review"
    return result


def compare_net_contents(
    reference_value: Decimal, reference_unit: str, candidates: CandidateSet
) -> CheckResult:
    expected = reference_volume_ml(reference_value, reference_unit)
    return compare_numeric(
        "net_contents",
        "Net contents",
        expected,
        candidates,
        parse_volume_ml,
        f"{reference_value} {reference_unit}",
    )


def compare_producer(reference: str, candidates: CandidateSet) -> CheckResult:
    def safe(left: str, right: str) -> bool:
        return casefolded(left) == casefolded(right)

    result = compare_text("producer", "Producer/name and address", reference, candidates)
    if candidates.status == "Found" and whitespace(reference) == whitespace(
        candidates.candidates[0].value
    ):
        result.state = "Match"
        result.reason_code = "safe_whitespace_match"
        result.reason_text = "The value matches after safe line-wrap and whitespace normalization"
    elif result.state == "Mismatch" and safe(reference, candidates.candidates[0].value):
        result.state = "Review"
        result.reason_code = "producer_formatting_variation"
        result.reason_text = "Producer formatting requires reviewer judgment"
    return result


def compare_country(imported: bool, reference: str | None, candidates: CandidateSet) -> CheckResult:
    if not imported:
        return _result(
            "country",
            "Country of origin",
            "Not verified",
            "not_applicable_domestic",
            "Country of origin is not applicable for the domestic reference",
            applicable=False,
        )
    return compare_text("country", "Country of origin", reference or "", candidates)
