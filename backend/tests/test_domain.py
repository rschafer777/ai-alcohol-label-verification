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
    assert len(checks) == 24
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


def test_probable_ocr_character_error_is_review_not_mismatch() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("OLD TOM D|STILLERY", "brand")
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    brand = by_id(checks, "brand")
    assert brand.state == "Review"
    assert brand.reason_code == "ocr_near_match"
    assert summary == "Review needed"


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


def test_net_contents_tolerates_common_ocr_zero_in_fluid_ounce_unit() -> None:
    observed = clean_observed()
    observed.fields["net_contents"] = found("12 fl 0Z", "net_contents")
    malt_reference = reference().model_copy(
        update={"net_contents_value": Decimal("12"), "net_contents_unit": "fl oz"}
    )
    checks, _ = compare_all(ComparisonInputs(malt_reference, observed))
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


def test_label_derived_domestic_producer_makes_country_not_applicable() -> None:
    label_reference = reference().model_copy(update={"reference_provenance": "label_ocr"})

    checks, summary = compare_all(ComparisonInputs(label_reference, clean_observed()))

    country = by_id(checks, "country")
    assert country.state == "Not verified"
    assert country.reason_code == "not_applicable_domestic"
    assert country.applicable is False
    assert summary == "No differences found in checked fields"


@pytest.mark.parametrize(
    ("abv", "expected_reason"),
    [
        (Decimal("0.49"), "warning_not_required"),
        (Decimal("0.50"), "warning_required"),
    ],
)
def test_warning_threshold_is_exact(abv: Decimal, expected_reason: str) -> None:
    checks = warning_checks(abv, clean_observed().warning)

    assert by_id(checks, "warning_applicability").reason_code == expected_reason


def test_unknown_warning_abv_requires_review_without_inventing_applicability() -> None:
    checks = warning_checks(None, clean_observed().warning)

    applicability = by_id(checks, "warning_applicability")
    assert applicability.state == "Review"
    assert applicability.reason_code == "warning_applicability_unknown"


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


def test_warning_body_case_and_marker_whitespace_do_not_change_wording() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].upper()
    body = body.replace("(1) ", "(1)").replace(" (2) ", "(2)")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Match"


def test_warning_punctuation_difference_is_a_review_item_never_cleared() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("General,", "General")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    # Every word is present in order; the comma the read lacks is named for the reviewer,
    # and the label is never reported clean on the machine's word.
    assert wording.state == "Review"
    assert wording.reason_code == "warning_punctuation_uncertain"
    assert "commas 1 read, 2 expected" in wording.reason_text
    assert summary == "Review needed"


def test_missing_statutory_word_inside_a_clean_read_is_a_wording_mismatch() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("should not drink", "should drink")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Mismatch"
    assert wording.reason_code == "warning_wording_difference"


def test_truncated_read_is_a_review_item_not_a_mismatch() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace(" and may cause health problems.", "")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_read_that_stops_early_is_a_review_item_not_a_mismatch() -> None:
    observed = clean_observed()
    body = "(1) ACCORDING TO THE SURGEON GENERAL WOMEN SHOULD NOT DRINK ALCOHOUJC"
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_skipped_lines_inside_a_read_are_a_review_item_not_a_mismatch() -> None:
    observed = clean_observed()
    body = "1ACCORDING TO THE SURGEON GENERAL. OF THE RISK OF BIRTH DEFECTS. (2) HEALTH PROBLEMS."
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_interruption_inside_a_fragmentary_read_is_a_review_item() -> None:
    observed = clean_observed()
    body = (
        "(1) ACCORDING TO THE SURGEON GENERAL. OF THE RISK OF BIRTH DEFECTS. (2) HEALTH PROBLEMS."
    )
    observed = replace(observed, warning=replace(observed.warning, body=body, continuous=False))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_continuity").state == "Review"


def test_interruption_inside_a_clean_read_is_a_mismatch() -> None:
    observed = clean_observed()
    observed = replace(observed, warning=replace(observed.warning, continuous=False))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_continuity").state == "Mismatch"


def test_best_read_panel_decides_the_warning_when_several_images_carry_it() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    truncated = replace(
        observed.warning, body="(1) ACCORDING TO THE SURGEON GENERAL WOMEN SHOULD NOT DRINK"
    )
    exact = observed.warning

    checks = warning_checks_across(Decimal("45"), truncated, [exact])

    assert by_id(checks, "warning_wording").state == "Match"
    assert by_id(checks, "warning_wording").reason_code == "warning_wording_exact"


def test_statutory_words_are_confirmed_across_partial_reads_on_two_images() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    first_half, second_half = body.split(" (2) ", maxsplit=1)
    front = replace(observed.warning, body=first_half)
    back = replace(observed.warning, body="of the risk of birth defects. (2) " + second_half)

    checks = warning_checks_across(Decimal("45"), front, [back])
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_words_confirmed_across_images"
    assert "across 2 images" in wording.reason_text


def test_a_substitution_seen_on_every_image_stays_a_mismatch() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("car or operate", "car and operate")
    front = replace(observed.warning, body=body)
    back = replace(observed.warning, body=body)

    checks = warning_checks_across(Decimal("45"), front, [back])

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_words_cut_by_the_image_edge_are_not_substitutions() -> None:
    observed = clean_observed()
    body = (
        "(1) ccording to the Surgeon General, omen should not drink alcoholic beverages during "
        "egnancy because of the risk of birth defects. (2) onsumption of alcoholic beverages "
        "impairs your ability to drive a car or operate machinery, and may cause health problems."
    )
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_a_heading_less_fragment_with_clear_substitutions_is_a_difference() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    # The cut heading does not excuse words the fragment plainly shows changed.
    body = (
        contracts()
        .rules["warning"]["bodyExact"]
        .replace("car or operate", "car and operate")
        .replace("may cause", "will cause")
    )
    fragment = replace(observed.warning, heading=None, heading_evidence=None, body=body)

    checks = warning_checks_across(Decimal("45"), fragment, [])

    assert by_id(checks, "warning_wording").state == "Mismatch"
    assert by_id(checks, "warning_heading_uppercase").state == "Not verified"


def test_a_noisy_heading_less_fragment_asks_for_the_rest_of_the_statement() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = (
        "(1) According to the Surgeon General, women should not drink alcoholic beverages "
        "during pregnancy becuase of the risk of birth defects. (2) Consumption of alcoholic "
        "beverages impairs your abilty to drive a car or operate machinery, and may cause"
    )
    fragment = replace(observed.warning, heading=None, heading_evidence=None, body=body)

    checks = warning_checks_across(Decimal("45"), fragment, [])
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_fragment_review"


def test_a_fragment_reports_the_heading_weight_and_separation_as_out_of_view() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    fragment = replace(observed.warning, heading=None, heading_evidence=None)

    checks = warning_checks_across(Decimal("45"), fragment, [])

    for check_id in ("warning_heading_emphasis", "warning_separation"):
        assert by_id(checks, check_id).state == "Not verified"
        assert by_id(checks, check_id).reason_code == "warning_heading_not_in_view"
    # The body itself is in view, so its own measurements stand.
    assert by_id(checks, "warning_contrast").state == "Match"
    assert by_id(checks, "warning_wording").state == "Match"


def test_a_contradicting_read_on_another_image_cannot_be_confirmed_away() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    defective = replace(
        observed.warning, body=body.replace("women should not drink", "women may drink")
    )
    fragment = replace(observed.warning, heading=None, heading_evidence=None, body=body)

    checks = warning_checks_across(Decimal("45"), defective, [fragment])
    wording = by_id(checks, "warning_wording")

    # The clean read on the other image cannot clear the difference; the images disagree,
    # whichever of them carried the heading.
    assert wording.state == "Review"
    assert wording.reason_code == "warning_images_disagree"


def test_ocr_confusions_of_short_statutory_words_are_not_disagreements() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    for damaged in (
        ("the risk", "tlie risk"),
        ("should not", "should riot"),
        ("and may", "arid may"),
    ):
        alternate = replace(observed.warning, body=body.replace(*damaged))
        checks = warning_checks_across(Decimal("45"), observed.warning, [alternate])
        assert by_id(checks, "warning_wording").state == "Match", damaged


def test_a_fragment_showing_little_of_the_statute_cannot_establish_a_difference() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    fragment = replace(
        observed.warning,
        heading=None,
        heading_evidence=None,
        body="(1) According to our brewmaster, this beer is best enjoyed cold.",
    )

    checks = warning_checks_across(Decimal("45"), fragment, [])
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_fragment_review"


def test_a_substitution_survives_boxes_that_split_the_printed_lines() -> None:
    observed = clean_observed()
    words = (
        contracts().rules["warning"]["bodyExact"].replace("should not drink", "may drink").split()
    )
    lines: list[str] = []
    for start in range(0, len(words), 6):
        row = words[start : start + 6]
        lines.extend([" ".join(row[:2]), " ".join(row[2:])] if len(row) > 2 else [" ".join(row)])
    body_lines = tuple(line for line in lines if line)
    observed = replace(
        observed,
        warning=replace(observed.warning, body=" ".join(body_lines), body_lines=body_lines),
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_a_substitution_both_images_read_is_not_a_disagreement() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("should not drink", "may drink")
    slipped = (
        body.replace("Surgeon", "Surgeom")
        .replace("machinery", "machinory")
        .replace("pregnancy", "pregnency")
        .replace("defects", "defecls")
    )
    primary = replace(observed.warning, body=slipped)
    fragment = replace(observed.warning, heading=None, heading_evidence=None, body=body)

    checks = warning_checks_across(Decimal("45"), primary, [fragment])

    assert by_id(checks, "warning_wording").reason_code != "warning_images_disagree"


def test_a_very_long_fused_token_does_not_crash_the_comparison() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("health problems.", "of" * 1200)
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state in {"Review", "Mismatch"}


def test_two_complete_reads_that_disagree_on_a_word_go_to_review() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    defective = replace(
        observed.warning, body=body.replace("women should not drink", "women may drink")
    )
    clean = replace(observed.warning, body=body)

    for primary, other in ((defective, clean), (clean, defective)):
        checks = warning_checks_across(Decimal("45"), primary, [other])
        wording = by_id(checks, "warning_wording")
        assert wording.state == "Review"
        assert wording.reason_code == "warning_images_disagree"


def test_a_word_dropped_on_one_image_yields_to_a_clean_read_on_another() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    dropped = replace(observed.warning, body=body.replace("should not drink", "should drink"))
    clean = replace(observed.warning, body=body)

    checks = warning_checks_across(Decimal("45"), dropped, [clean])

    assert by_id(checks, "warning_wording").state == "Match"


def test_a_garbled_read_made_of_statutory_word_pieces_is_a_review_item() -> None:
    observed = clean_observed()
    lines = (
        "SURGEON GENERAL",
        "to a daily diet.2.000 calories a day",
        "CONSUMPTIONOF",
        "KOF BIRTH DEFECTS.",
        "COHOLIC BEVERAGES",
        "ARS YOUR ABILITY",
        "HPROBLEMS",
        "MAYCAUSE",
    )
    observed = replace(
        observed, warning=replace(observed.warning, body=" ".join(lines), body_lines=lines)
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_ocr_difference_uncertain"


def test_a_glued_and_fragmented_read_on_one_line_is_a_review_item() -> None:
    observed = clean_observed()
    body = (
        "(1ACCORDING TO THE SURGEON GENERALWOMEN SHOULD NKAICOHOLIC BEVERAGES DURING "
        "PREGNANCY BECAUSE OF THERISK OF CONUMPTION OFALCOHOLIC BEVERAGES MPAIRS YOUR "
        "ABILITY CONSUMPTION OFALCOHOLICBEVERAGEST"
    )
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_replacement_text_using_inflected_statutory_words_is_a_difference() -> None:
    observed = clean_observed()
    lines = (
        "Please drink responsibly. Women who are",
        "pregnant should consider avoiding alcohol.",
        "Drinking and driving is dangerous and",
        "alcohol may affect your health.",
    )
    observed = replace(
        observed, warning=replace(observed.warning, body=" ".join(lines), body_lines=lines)
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_a_number_under_the_heading_is_not_a_read_of_the_statement() -> None:
    observed = clean_observed()
    observed = replace(
        observed, warning=replace(observed.warning, body="2105900750", body_lines=("2105900750",))
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_different_text_made_of_whole_words_is_still_a_difference() -> None:
    observed = clean_observed()
    body = (
        "This product contains alcohol and may impair your ability to drive a car. "
        "Do not drink while pregnant."
    )
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_a_read_cut_inside_the_first_clause_is_not_a_missing_second_clause() -> None:
    observed = clean_observed()
    body = (
        "1 ACCORDING TO THE SUR GEON GENERAL,WOMEN SHOULD NOT DRINK ALCCHOLIC BEVERAGES "
        "DURING PREGNANCY BECAUSE OF THE RISK"
    )
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_a_complete_first_clause_with_no_second_clause_is_a_difference() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].split(" (2) ", maxsplit=1)[0]
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_a_shortened_word_inside_a_line_is_a_substitution() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("alcoholic beverages", "alcohol")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_a_word_fragment_at_the_end_of_a_read_line_is_a_cut() -> None:
    observed = clean_observed()
    lines = (
        "(1)According to the Surgeon General, women should not drink alco",
        "beverages during pregnancy because of the risk of birth defects. (2) Consumption",
        "of alcoholic beverages impairs your ability to drive a car or operate machinery,",
        "and may cause health problems.",
    )
    observed = replace(
        observed,
        warning=replace(observed.warning, body=" ".join(lines), body_lines=lines),
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Review"


def test_the_same_word_fragment_inside_a_read_line_is_a_substitution() -> None:
    observed = clean_observed()
    lines = (
        "(1) According to the Surgeon General, women should not drink alco beverages during",
        "pregnancy because of the risk of birth defects. (2) Consumption of alcoholic",
        "beverages impairs your ability to drive a car or operate machinery, and may",
        "cause health problems.",
    )
    observed = replace(
        observed,
        warning=replace(observed.warning, body=" ".join(lines), body_lines=lines),
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_a_garbled_short_word_on_another_image_is_not_a_disagreement() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    garbled = replace(observed.warning, body=body.replace("the risk", "the rjsx"))

    checks = warning_checks_across(Decimal("45"), observed.warning, [garbled])

    assert by_id(checks, "warning_wording").state == "Match"


def test_a_complete_fragment_with_another_word_disagrees_with_a_clean_read() -> None:
    from labelverify.domain.warnings import warning_checks_across

    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    fragment = replace(
        observed.warning,
        heading=None,
        heading_evidence=None,
        body=body.replace("women should not drink", "women may drink"),
    )

    checks = warning_checks_across(Decimal("45"), observed.warning, [fragment])
    wording = by_id(checks, "warning_wording")

    assert wording.reason_code == "warning_images_disagree"
    assert '"may"' in wording.reason_text and '"should not"' in wording.reason_text


def test_heavily_damaged_noisy_read_is_a_review_item_not_a_mismatch() -> None:
    observed = clean_observed()
    body = (
        "(1) Accordng to the Surgeon General wome stoold not drink alcobolic beverages "
        "durg pgancy because of the rit of birth deiecs. (2) Consumption of alcoholic "
        "beverages epers yr ablity to drive a car or operate rachiney and may cause "
        "health problems."
    )
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_ocr_difference_uncertain"


def test_two_clear_substitutions_beside_one_slip_are_a_wording_mismatch() -> None:
    observed = clean_observed()
    body = (
        contracts()
        .rules["warning"]["bodyExact"]
        .replace("car or operate", "car and operate")
        .replace("may cause", "will cause")
        .replace("Surgeon", "Surgeom")
    )
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "warning_wording").state == "Mismatch"


def test_warning_unconfusable_punctuation_difference_requires_review() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"].replace("General,", "General?")
    observed = replace(observed, warning=replace(observed.warning, body=body))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")

    assert wording.state == "Review"
    assert wording.reason_code == "warning_punctuation_uncertain"


def test_ocr_marker_and_glued_digit_forms_are_the_same_words() -> None:
    observed = clean_observed()
    body = contracts().rules["warning"]["bodyExact"]
    glued = body.replace("(1) According", "1According").replace("(2) Consumption", "2Consumption")
    observed = replace(observed, warning=replace(observed.warning, body=glued))

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    # Digits fused to the next word are unresolved marker brackets, an OCR signature.
    assert by_id(checks, "warning_wording").state == "Match"

    # A marker read with one bracket may be printed that way; the reviewer confirms it.
    half = body.replace("(2) Consumption", "2) Consumption")
    observed = replace(observed, warning=replace(observed.warning, body=half))
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    wording = by_id(checks, "warning_wording")
    assert wording.state == "Review"
    assert "opening parentheses 1 read, 2 expected" in wording.reason_text


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


def test_unscaled_warning_size_is_reported_for_a_human_without_blocking_clean() -> None:
    observed = clean_observed()
    observed = replace(observed, warning=replace(observed.warning, reliable_scale=False))
    checks, summary = compare_all(ComparisonInputs(reference(), observed))
    physical = by_id(checks, "warning_physical_size")
    assert physical.state == "Not verified"
    assert physical.capability == "human_confirmation"
    # Millimeters cannot come from an unscaled photograph, so the row is informational.
    assert physical.applicable is False
    assert summary == "No differences found in checked fields"


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
    assert by_id(checks, "proof").reason_code == ("proof_abv_relationship_and_placement_match")

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
    # Body text without a heading is a fragment: the heading's weight and the block's
    # separation are outside the image, while the body's own measurements stand.
    assert by_id(checks, "warning_heading_emphasis").state == "Not verified"
    assert by_id(checks, "warning_heading_emphasis").reason_code == "warning_heading_not_in_view"
    assert by_id(checks, "warning_separation").state == "Not verified"
    assert by_id(checks, "warning_body_not_bold").state == "Review"
    assert by_id(checks, "warning_contrast").state == "Mismatch"
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
