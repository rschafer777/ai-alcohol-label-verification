from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from decimal import Decimal

import pytest
from labelverify.contracts.loader import contracts
from labelverify.contracts.models import Candidate, CandidateSet, CheckResult
from labelverify.domain.aggregation import IncompleteCheckSetError, aggregate
from labelverify.domain.engine import ComparisonInputs, compare_all
from labelverify.domain.types import WarningObservation
from labelverify.domain.warnings import warning_checks

from .helpers import clean_observed, evidence, found, reference


def by_id(checks: Sequence[CheckResult], check_id: str) -> CheckResult:
    return next(item for item in checks if item.check_id == check_id)


def test_complete_clean_check_set_matches_registry_order() -> None:
    checks, summary = compare_all(ComparisonInputs(reference(), clean_observed()))
    assert [item.check_id for item in checks] == list(contracts().check_ids)
    assert len(checks) == 19
    assert summary == "No differences found in checked fields"


def test_brand_case_only_is_review_not_mismatch() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("Stone's Throw", "brand")
    checks, summary = compare_all(ComparisonInputs(reference(brand="STONE'S THROW"), observed))
    brand = by_id(checks, "brand")
    assert brand.state == "Review"
    assert summary == "Review needed"


def test_punctuation_only_brand_is_review() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("STONES THROW", "brand")
    checks, _ = compare_all(ComparisonInputs(reference(brand="STONE'S THROW"), observed))
    assert by_id(checks, "brand").reason_code == "punctuation_variation"


def test_numeric_difference_has_mismatch_precedence() -> None:
    observed = clean_observed()
    observed.fields["abv"] = found("40% Alc./Vol.", "abv")
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "abv").state == "Mismatch"
    assert summary == "Differences detected"


def test_net_contents_liters_normalize_exactly() -> None:
    observed = clean_observed()
    observed.fields["net_contents"] = found("0.75 L", "net_contents")
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "net_contents").state == "Match"


def test_conflicting_country_candidates_are_review_with_distinct_evidence() -> None:
    observed = clean_observed(imported=True)
    observed.fields["country"] = CandidateSet(
        status="Ambiguous",
        candidates=[
            Candidate(value="Canada", evidence=evidence("country", 1, x=10)),
            Candidate(value="France", evidence=evidence("country", 2, x=200)),
        ],
    )
    checks, summary = compare_all(ComparisonInputs(reference(imported=True), observed))
    country = by_id(checks, "country")
    assert country.state == "Review"
    assert len(country.alternatives) == 2
    assert summary == "Review needed"


def test_domestic_country_is_explicit_non_applicable() -> None:
    checks, _ = compare_all(ComparisonInputs(reference(), clean_observed()))
    country = by_id(checks, "country")
    assert country.applicable is False


def test_title_case_warning_heading_is_independent_mismatch() -> None:
    observed = clean_observed()
    observed = replace(
        observed,
        warning=replace(
            observed.warning,
            heading="Government Warning:",
            full_text=f"Government Warning: {contracts().rules['warning']['bodyExact']}",
        ),
    )
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "warning_heading_uppercase").state == "Mismatch"
    assert by_id(checks, "warning_wording").state == "Match"
    assert summary == "Differences detected"


def test_uppercase_warning_heading_punctuation_difference_requires_review() -> None:
    observed = clean_observed()
    observed = replace(
        observed,
        warning=replace(
            observed.warning,
            heading="GOVERNMENT WARNING",
            full_text=f"GOVERNMENT WARNING {contracts().rules['warning']['bodyExact']}",
        ),
    )

    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    heading = by_id(checks, "warning_heading_uppercase")

    assert heading.state == "Review"
    assert heading.reason_code == "warning_heading_punctuation_uncertain"
    assert summary == "Review needed"


def test_possible_ocr_punctuation_at_line_wrap_requires_review() -> None:
    observed = clean_observed()
    observed = replace(
        observed,
        warning=replace(observed.warning, punctuation_normalized=True),
    )
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")
    assert wording.state == "Review"
    assert wording.reason_code == "ocr_wrap_punctuation_uncertain"
    assert summary == "Review needed"


def test_warning_body_case_and_marker_whitespace_do_not_change_wording() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].upper()
    body = body.replace("(1) ", "(1)").replace(" (2) ", "(2)")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Match"


def test_warning_punctuation_only_difference_requires_review() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("General,", "General")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_punctuation_uncertain"


def test_clear_terminal_exclamation_is_a_warning_wording_mismatch() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("problems.", "problems!")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Mismatch"
    assert wording.reason_code == "warning_wording_difference"
    assert summary == "Differences detected"


def test_minor_ocr_word_difference_requires_review_not_rejection() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("women", "womeo")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_ocr_difference_uncertain"


def test_clear_high_confidence_warning_word_substitution_is_mismatch() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("car or operate", "car and operate")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Mismatch"
    assert wording.reason_code == "warning_wording_difference"


def test_low_confidence_warning_word_substitution_requires_review() -> None:
    observed = clean_observed()
    body_evidence = observed.warning.body_evidence
    assert body_evidence is not None
    body_evidence = body_evidence.model_copy(
        update={
            "confidence_provenance": body_evidence.confidence_provenance.model_copy(
                update={"signal": 0.7}
            )
        }
    )
    body = contracts().rules["warning"]["bodyExact"].replace("car or operate", "car and operate")
    observed = replace(
        observed,
        warning=replace(observed.warning, body=body, body_evidence=body_evidence),
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_ocr_difference_uncertain"


@pytest.mark.parametrize(
    "body",
    [
        (
            "(1) According to the Surgeon General, women should not drink alcoholic "
            "beverages during pregnancy because of the risk of birth defects."
        ),
        "Please drink responsibly. Drinking and driving is dangerous.",
    ],
)
def test_material_warning_difference_remains_mismatch(body: str) -> None:
    observed = clean_observed()
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_truncated_expected_fragments_require_review_instead_of_rejection() -> None:
    observed = clean_observed()
    body = "the risk of birth defects cause health problems"
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_class_terminal_period_is_safe_but_internal_punctuation_is_not() -> None:
    observed = clean_observed()
    observed.fields["class_type"] = found("Kentucky Straight Bourbon Whiskey.", "class_type")
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "class_type").state == "Match"

    observed.fields["class_type"] = found("Kentucky Straight Bourbon, Whiskey", "class_type")
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "class_type").state == "Review"


def test_unscaled_warning_size_is_not_verified_and_prevents_clean() -> None:
    observed = clean_observed()
    observed = replace(observed, warning=replace(observed.warning, reliable_scale=False))
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    physical = by_id(checks, "warning_physical_size")
    assert physical.state == "Not verified"
    assert physical.capability == "human_confirmation"
    assert summary == "Review needed"


def test_warning_policies_have_exact_registry_completeness() -> None:
    checks, _ = compare_all(ComparisonInputs(reference(), clean_observed()))
    warning_ids = [item.check_id for item in checks if item.check_id.startswith("warning_")]
    expected = [item for item in contracts().check_ids if item.startswith("warning_")]
    assert warning_ids == expected
    assert len(warning_ids) == 10


def test_aggregation_rejects_missing_or_duplicate_checks() -> None:
    checks, _ = compare_all(ComparisonInputs(reference(), clean_observed()))
    with pytest.raises(IncompleteCheckSetError):
        aggregate(checks[:-1])
    with pytest.raises(IncompleteCheckSetError):
        aggregate(checks[:-1] + [checks[0]])


def test_missing_field_never_becomes_match() -> None:
    observed = clean_observed()
    observed.fields["producer"] = CandidateSet(status="Not found")
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "producer").state == "Not verified"
    assert summary == "Review needed"


def test_warning_style_unknown_routes_to_review() -> None:
    observed = clean_observed()
    observed = replace(
        observed,
        warning=WarningObservation(
            heading=observed.warning.heading,
            body=observed.warning.body,
            full_text=observed.warning.full_text,
            heading_evidence=observed.warning.heading_evidence,
            body_evidence=observed.warning.body_evidence,
        ),
    )
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "warning_heading_emphasis").state == "Review"
    assert summary == "Review needed"


def test_unreadable_source_never_produces_warning_mismatches() -> None:
    observed = clean_observed()
    observed = replace(
        observed,
        fields={name: CandidateSet(status="Unreadable") for name in observed.fields},
        warning=WarningObservation(source_unreadable=True),
        panels=[observed.panels[0].model_copy(update={"coverage_state": "Unreadable"})],
        evidence=[],
    )

    checks, summary = compare_all(ComparisonInputs(reference(), observed))

    assert all(item.state != "Mismatch" for item in checks)
    assert by_id(checks, "brand").reason_code == "observed_unreadable"
    assert by_id(checks, "warning_applicability").state == "Match"
    assert by_id(checks, "warning_wording").reason_code == "observed_unreadable"
    assert summary == "Review needed"


def test_review_quality_downgrades_apparent_difference() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("WRONG BRAND", "brand")
    observed = replace(
        observed,
        panels=[observed.panels[0].model_copy(update={"coverage_state": "Review"})],
    )

    checks, summary = compare_all(ComparisonInputs(reference(), observed))

    brand = by_id(checks, "brand")
    assert brand.state == "Review"
    assert brand.reason_code == "quality_degraded_observation"
    assert summary == "Review needed"


def test_front_only_submission_reports_panel_coverage_gap() -> None:
    observed = clean_observed(imported=True)
    observed.fields["producer"] = CandidateSet(status="Not found")
    observed.fields["country"] = CandidateSet(status="Not found")
    observed = replace(observed, warning=WarningObservation())

    checks, summary = compare_all(ComparisonInputs(reference(imported=True), observed))

    coverage = by_id(checks, "panel_coverage")
    assert coverage.state == "Not verified"
    assert coverage.reason_code == "panel_coverage_uncertain"
    assert summary == "Review needed"


def test_missing_warning_makes_dependent_presentation_checks_not_verified() -> None:
    observed = clean_observed()
    observed = replace(observed, warning=WarningObservation())

    checks, summary = compare_all(ComparisonInputs(reference(), observed))

    missing_warning_details = [
        item
        for item in checks
        if item.check_id.startswith("warning_")
        and item.check_id not in {"warning_applicability", "warning_physical_size"}
    ]
    assert all(item.state == "Not verified" for item in missing_warning_details)
    assert by_id(checks, "warning_physical_size").reason_code == "reliable_scale_unavailable"
    assert summary == "Review needed"


def test_multi_panel_submission_does_not_infer_generator_only_panel_roles() -> None:
    observed = clean_observed(imported=True)
    observed.fields["producer"] = CandidateSet(status="Not found")
    observed = replace(
        observed,
        warning=WarningObservation(),
        panels=[
            observed.panels[0].model_copy(update={"panel_id": f"panel-{index}"})
            for index in range(1, 4)
        ],
    )

    checks, _ = compare_all(ComparisonInputs(reference(imported=True), observed))

    assert by_id(checks, "panel_coverage").state == "Match"


def test_physical_size_result_links_scale_evidence() -> None:
    observed = clean_observed()

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    physical = by_id(checks, "warning_physical_size")
    scale_evidence = observed.warning.scale_evidence
    assert scale_evidence is not None
    assert physical.state == "Match"
    assert physical.evidence_ref == scale_evidence.evidence_id


@pytest.mark.parametrize(
    ("capacity", "unit", "size_mm", "characters_per_inch", "expected_state"),
    [
        (Decimal("237"), "mL", 1.0, 40.0, "Match"),
        (Decimal("237.01"), "mL", 1.0, 25.0, "Mismatch"),
        (Decimal("3"), "L", 2.0, 25.0, "Match"),
        (Decimal("3.001"), "L", 2.0, 12.0, "Mismatch"),
        (Decimal("3.001"), "L", 3.0, 13.0, "Mismatch"),
        (Decimal("3.001"), "L", 3.0, 12.0, "Match"),
    ],
)
def test_warning_size_and_character_density_follow_container_tiers(
    capacity: Decimal,
    unit: str,
    size_mm: float,
    characters_per_inch: float,
    expected_state: str,
) -> None:
    observed = replace(
        clean_observed().warning,
        physical_size_mm=size_mm,
        characters_per_inch=characters_per_inch,
    )
    checks = warning_checks(Decimal("45"), observed, capacity, unit)
    assert by_id(checks, "warning_physical_size").state == expected_state


def test_aggregation_rejects_no_applicable_checks_and_unknown_state() -> None:
    checks, _ = compare_all(ComparisonInputs(reference(), clean_observed()))
    no_applicable = [item.model_copy(update={"applicable": False}) for item in checks]
    with pytest.raises(IncompleteCheckSetError, match="At least one"):
        aggregate(no_applicable)

    unknown = [item.model_copy() for item in checks]
    unknown[0] = unknown[0].model_copy(update={"state": "Unexpected"})
    with pytest.raises(IncompleteCheckSetError, match="Unknown check state"):
        aggregate(unknown)


def test_class_safe_equivalence_and_incomplete_designation_paths() -> None:
    observed = clean_observed()
    observed.fields["class_type"] = found("Kentucky   Straight Bourbon Whiskey", "class_type")
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "class_type").reason_code == "safe_representation_match"

    observed.fields["class_type"] = found("Bourbon Whiskey", "class_type")
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "class_type").reason_code == "incomplete_plausible_designation"


def test_numeric_parse_and_proof_policy_paths() -> None:
    observed = clean_observed()
    observed.fields["abv"] = found("ABV unreadable", "abv")
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "abv").reason_code == "ambiguous_numeric_parse"

    no_proof_reference = reference().model_copy(update={"proof": None})
    observed.fields["abv"] = found("45% Alc./Vol.", "abv")
    observed.fields["proof"] = CandidateSet(status="Not found")
    checks, _ = compare_all(ComparisonInputs(no_proof_reference, observed))
    assert by_id(checks, "proof").applicable is False

    observed.fields["proof"] = found("90 Proof", "proof")
    checks, _ = compare_all(ComparisonInputs(no_proof_reference, observed))
    assert by_id(checks, "proof").reason_code == "proof_abv_relationship_match"

    inconsistent_reference = reference().model_copy(update={"proof": Decimal("80")})
    observed.fields["proof"] = found("80 Proof", "proof")
    checks, _ = compare_all(ComparisonInputs(inconsistent_reference, observed))
    assert by_id(checks, "proof").reason_code == "reference_abv_proof_inconsistent"


def test_producer_whitespace_is_a_safe_match() -> None:
    observed = clean_observed()
    observed.fields["producer"] = found(
        "BOTTLED BY: OLD HERITAGE DISTILLERY, LLC\nFRANKFORT, KENTUCKY",
        "producer",
    )
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "producer").reason_code == "safe_whitespace_match"


def test_warning_below_threshold_and_failure_branches() -> None:
    below_threshold = warning_checks(Decimal("0.4"), WarningObservation())
    assert len(below_threshold) == 10
    assert all(not item.applicable for item in below_threshold[1:])

    observed = clean_observed().warning
    failure = replace(
        observed,
        heading=None,
        body="Changed required wording.",
        full_text="Changed required wording.",
        heading_bold=False,
        body_bold=True,
        separated=False,
        continuous=False,
        contrast_sufficient=False,
        legible=False,
        physical_size_mm=1.5,
    )
    checks = warning_checks(Decimal("45"), failure)
    assert by_id(checks, "warning_wording").state == "Mismatch"
    assert by_id(checks, "warning_heading_uppercase").state == "Not verified"
    assert by_id(checks, "warning_heading_emphasis").state == "Review"
    assert by_id(checks, "warning_body_not_bold").state == "Review"
    assert by_id(checks, "warning_physical_size").reason_code == "physical_size_below_required"


def test_visual_weight_heuristics_cannot_create_a_deterministic_rejection() -> None:
    observed = clean_observed().warning
    uncertain_weight = replace(observed, heading_bold=False, body_bold=True)

    checks = warning_checks(Decimal("45"), uncertain_weight)

    assert by_id(checks, "warning_heading_emphasis").state == "Review"
    assert by_id(checks, "warning_body_not_bold").state == "Review"
    assert all(
        check.state != "Mismatch"
        for check in checks
        if check.check_id in {"warning_heading_emphasis", "warning_body_not_bold"}
    )
