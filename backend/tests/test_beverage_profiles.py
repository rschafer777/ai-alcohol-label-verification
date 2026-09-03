from dataclasses import replace
from decimal import Decimal

from labelverify.contracts.models import CandidateSet, ReferenceRecord
from labelverify.domain.engine import ComparisonInputs, compare_all
from labelverify.orchestration.pipeline import _infer_beverage_type

from .helpers import clean_observed, found, reference
from .test_domain import by_id


def found_with_source(value: str, source: str, role: str = "abv") -> CandidateSet:
    candidates = found(value, role)
    candidate = candidates.candidates[0]
    return CandidateSet(
        status="Found",
        candidates=[
            candidate.model_copy(
                update={"evidence": candidate.evidence.model_copy(update={"text_snippet": source})}
            )
        ],
    )


def wine_reference() -> ReferenceRecord:
    return ReferenceRecord(
        profileId="all_beverages_demo_v2",
        beverageType="wine",
        referenceProvenance="label_ocr",
        brandName="CEDAR RIDGE",
        classType="Chardonnay",
        abvPercent=Decimal("13.5"),
        netContentsValue=Decimal("750"),
        netContentsUnit="mL",
        producerNameAddress="BOTTLED BY CEDAR RIDGE WINERY NAPA, CALIFORNIA",
        isImported=False,
        wineAppellation="Napa Valley",
        wineSulfiteStatus="present",
    )


def malt_reference() -> ReferenceRecord:
    return ReferenceRecord(
        profileId="all_beverages_demo_v2",
        beverageType="malt_beverage",
        referenceProvenance="label_ocr",
        brandName="NORTHWIND",
        classType="Ale",
        abvPercent=Decimal("5"),
        netContentsValue=Decimal("12"),
        netContentsUnit="fl oz",
        producerNameAddress="BREWED BY NORTHWIND BREWING SEATTLE, WASHINGTON",
        isImported=False,
        maltAlcoholSource="added_ingredients",
    )


def test_wine_profile_activates_wine_rules_and_common_fields() -> None:
    observed = clean_observed()
    observed.fields.update(
        {
            "brand": found("CEDAR RIDGE", "brand"),
            "class_type": found("Chardonnay", "class_type"),
            "abv": found("13.5% Alc. by Vol.", "abv"),
            "proof": CandidateSet(status="Not found"),
            "net_contents": found("750 mL", "net_contents"),
            "producer": found("BOTTLED BY CEDAR RIDGE WINERY NAPA, CALIFORNIA", "producer"),
            "wine_appellation": found("Napa Valley", "wine_appellation"),
            "wine_sulfites": found("CONTAINS SULFITES", "wine_sulfites"),
        }
    )

    checks, summary = compare_all(ComparisonInputs(wine_reference(), observed))

    assert by_id(checks, "beverage_type").state == "Match"
    assert by_id(checks, "wine_appellation").state == "Match"
    assert by_id(checks, "wine_sulfites").state == "Match"
    assert by_id(checks, "spirits_field_of_vision").applicable is False
    assert by_id(checks, "malt_class_designation").applicable is False
    assert by_id(checks, "country").reason_code == "not_applicable_domestic"
    assert summary == "No differences found in checked fields"


def test_malt_profile_activates_malt_rules_and_customary_volume() -> None:
    observed = clean_observed()
    observed.fields.update(
        {
            "brand": found("NORTHWIND", "brand"),
            "class_type": found("Ale", "class_type"),
            "abv": found("5% Alc. by Vol.", "abv"),
            "proof": CandidateSet(status="Not found"),
            "net_contents": found("12 fl oz", "net_contents"),
            "producer": found("BREWED BY NORTHWIND BREWING SEATTLE, WASHINGTON", "producer"),
        }
    )

    checks, summary = compare_all(ComparisonInputs(malt_reference(), observed))

    assert by_id(checks, "beverage_type").state == "Match"
    assert by_id(checks, "malt_class_designation").state == "Match"
    assert by_id(checks, "abv").state == "Match"
    assert by_id(checks, "net_contents").state == "Match"
    assert by_id(checks, "wine_appellation").applicable is False
    assert by_id(checks, "spirits_field_of_vision").applicable is False
    assert by_id(checks, "country").reason_code == "not_applicable_domestic"
    assert summary == "No differences found in checked fields"


def test_malt_profile_accepts_common_ocr_zero_for_fluid_ounce_unit() -> None:
    observed = clean_observed()
    observed.fields.update(
        {
            "brand": found("NORTHWIND", "brand"),
            "class_type": found("Ale", "class_type"),
            "abv": found("5% Alc. by Vol.", "abv"),
            "proof": CandidateSet(status="Not found"),
            "net_contents": found("12 fl 0Z", "net_contents"),
            "producer": found("BREWED BY NORTHWIND BREWING SEATTLE, WASHINGTON", "producer"),
        }
    )

    checks, _ = compare_all(ComparisonInputs(malt_reference(), observed))

    assert by_id(checks, "net_contents").state == "Match"


def test_malt_profile_rejects_prohibited_range_and_excess_precision() -> None:
    observed = clean_observed()
    observed.fields["class_type"] = found("Ale", "class_type")
    observed.fields["abv"] = found_with_source("5.25%", "5.25% Alc. by Vol.")

    checks, _ = compare_all(ComparisonInputs(malt_reference(), observed))
    assert by_id(checks, "abv").reason_code == "malt_alcohol_precision_invalid"

    observed.fields["abv"] = found_with_source("5%", "5% to 6% Alcohol by Volume")
    checks, _ = compare_all(ComparisonInputs(malt_reference(), observed))
    assert by_id(checks, "abv").reason_code == "alcohol_range_not_authorized"


def test_wine_profile_applies_range_span_and_fourteen_percent_boundary() -> None:
    observed = clean_observed()
    observed.fields["class_type"] = found("Chardonnay Wine", "class_type")
    observed.fields["abv"] = found_with_source("12%", "12% to 14% Alcohol by Volume")

    reference = wine_reference().model_copy(update={"reference_provenance": "manual"})
    checks, _ = compare_all(ComparisonInputs(reference, observed))
    assert by_id(checks, "abv").reason_code == "wine_alcohol_range_supported"

    observed.fields["abv"] = found_with_source("12%", "12% to 15% Alcohol by Volume")
    checks, _ = compare_all(ComparisonInputs(reference, observed))
    assert by_id(checks, "abv").reason_code == "wine_alcohol_range_invalid"


def test_label_derived_wine_range_requires_independent_actual_value() -> None:
    observed = clean_observed()
    observed.fields["class_type"] = found("Chardonnay Wine", "class_type")
    observed.fields["abv"] = found_with_source("12%", "12% to 14% Alcohol by Volume")

    checks, _ = compare_all(ComparisonInputs(wine_reference(), observed))

    alcohol = by_id(checks, "abv")
    assert alcohol.state == "Review"
    assert alcohol.reason_code == "wine_alcohol_range_requires_actual_value"


def test_wine_brand_and_class_split_across_panels_requires_review() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("CEDAR RIDGE", "brand")
    class_candidate = found("Chardonnay", "class_type").candidates[0]
    second_panel_evidence = class_candidate.evidence.model_copy(update={"panel_id": "panel-2"})
    observed.fields["class_type"] = CandidateSet(
        status="Found",
        candidates=[class_candidate.model_copy(update={"evidence": second_panel_evidence})],
    )

    checks, _ = compare_all(ComparisonInputs(wine_reference(), observed))

    assert by_id(checks, "class_type").reason_code == "wine_brand_label_placement_review"


def test_malt_abv_trigger_stays_unresolved_without_formula_facts() -> None:
    reference = malt_reference().model_copy(
        update={"abv_percent": None, "malt_alcohol_source": "unknown"}
    )
    observed = clean_observed()
    observed.fields.update(
        {
            "brand": found("NORTHWIND", "brand"),
            "class_type": found("Ale", "class_type"),
            "abv": CandidateSet(status="Not found"),
            "proof": CandidateSet(status="Not found"),
            "net_contents": found("12 fl oz", "net_contents"),
            "producer": found("BREWED BY NORTHWIND BREWING SEATTLE, WASHINGTON", "producer"),
        }
    )

    checks, summary = compare_all(ComparisonInputs(reference, observed))

    assert by_id(checks, "abv").reason_code == "malt_abv_trigger_unknown"
    assert by_id(checks, "warning_applicability").reason_code == ("warning_applicability_unknown")
    assert summary == "Review needed"


def test_beverage_type_inference_distinguishes_all_three_profiles() -> None:
    for class_type, expected in (
        ("Kentucky Straight Bourbon Whiskey", "distilled_spirits"),
        ("Chardonnay Wine", "wine"),
        ("India Pale Ale", "malt_beverage"),
    ):
        observed = clean_observed()
        observed.fields["class_type"] = found(class_type, "class_type")

        beverage_type, confidence, _, _ = _infer_beverage_type(observed)

        assert beverage_type == expected
        assert confidence is not None and confidence >= 0.72


def test_beverage_type_uses_class_evidence_when_brand_contains_a_type_word() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("OrganicVodka", "brand")
    observed.fields["class_type"] = found("100% NEUTRAL SPIRITS DISTILLED", "class_type")

    beverage_type, confidence, _, conflicting = _infer_beverage_type(observed)

    assert beverage_type == "distilled_spirits"
    assert confidence is not None and confidence >= 0.80
    assert conflicting is False


def test_beverage_type_does_not_use_brand_only_as_regulatory_class_evidence() -> None:
    for brand in ("OrganicVodka", "Tequila Mockingbird", "Beer Garden", "Wine Country"):
        observed = clean_observed()
        observed.fields["brand"] = found(brand, "brand")
        observed.fields["class_type"] = CandidateSet(status="Not found", candidates=[])

        beverage_type, confidence, _, conflicting = _infer_beverage_type(observed)

        assert beverage_type is None
        assert confidence is None
        assert conflicting is False


def test_beverage_type_repairs_joined_ocr_connector_without_product_knowledge() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("STRAWBERRY", "brand")
    observed.fields["class_type"] = found(
        "GRAPE WINEWITH NATURAL FLAVORS", "class_type"
    )

    beverage_type, confidence, _, conflicting = _infer_beverage_type(observed)

    assert beverage_type == "wine"
    assert confidence is not None and confidence >= 0.80
    assert conflicting is False


def test_spirits_proof_requires_supported_distinction_and_same_panel() -> None:
    observed = clean_observed()
    abv = observed.fields["abv"].candidates[0]
    proof = observed.fields["proof"].candidates[0]
    shared = abv.evidence.model_copy(update={"text_snippet": "45% Alc./Vol. 90 Proof"})
    observed.fields["abv"] = CandidateSet(
        status="Found", candidates=[abv.model_copy(update={"evidence": shared})]
    )
    observed.fields["proof"] = CandidateSet(
        status="Found", candidates=[proof.model_copy(update={"evidence": shared})]
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "proof").reason_code == "proof_distinction_requires_review"

    enclosed = shared.model_copy(update={"text_snippet": "45% Alc./Vol. (90 Proof)"})
    observed.fields["abv"] = CandidateSet(
        status="Found", candidates=[abv.model_copy(update={"evidence": enclosed})]
    )
    observed.fields["proof"] = CandidateSet(
        status="Found", candidates=[proof.model_copy(update={"evidence": enclosed})]
    )
    checks, _ = compare_all(ComparisonInputs(reference(), observed))
    assert by_id(checks, "proof").reason_code == ("proof_abv_relationship_and_placement_match")


def test_beverage_type_inference_uses_whole_terms_and_routes_conflicts_to_review() -> None:
    observed = clean_observed()
    observed.fields["class_type"] = found("Original Recipe", "class_type")
    beverage_type, _, _, _ = _infer_beverage_type(observed)
    assert beverage_type is None

    observed.fields["class_type"] = found("Hard Seltzer", "class_type")
    beverage_type, _, _, _ = _infer_beverage_type(observed)
    assert beverage_type is None

    observed.fields["class_type"] = found("Wine barrel aged beer", "class_type")
    beverage_type, _, _, _ = _infer_beverage_type(observed)
    assert beverage_type is None

    observed.fields["class_type"] = found("Bourbon Whiskey Barrel Aged Stout", "class_type")
    beverage_type, _, _, _ = _infer_beverage_type(observed)
    assert beverage_type is None


def test_spirits_field_of_vision_requires_same_submitted_panel() -> None:
    observed = clean_observed()
    off_panel = found("45% Alc./Vol.", "abv")
    candidate = off_panel.candidates[0]
    off_panel = found("45% Alc./Vol.", "abv")
    off_panel.candidates[0] = candidate.model_copy(
        update={"evidence": candidate.evidence.model_copy(update={"panel_id": "panel-2"})}
    )
    observed.fields["abv"] = off_panel
    observed = replace(
        observed,
        panels=[
            observed.panels[0],
            observed.panels[0].model_copy(update={"panel_id": "panel-2"}),
        ],
        evidence=[*observed.evidence, off_panel.candidates[0].evidence],
    )

    checks, _ = compare_all(
        ComparisonInputs(
            malt_reference().model_copy(
                update={
                    "beverage_type": "distilled_spirits",
                    "class_type": "Kentucky Straight Bourbon Whiskey",
                    "brand_name": "OLD TOM DISTILLERY",
                    "net_contents_value": Decimal("750"),
                    "net_contents_unit": "mL",
                }
            ),
            observed,
        )
    )

    assert by_id(checks, "spirits_field_of_vision").reason_code == "field_of_vision_split"
