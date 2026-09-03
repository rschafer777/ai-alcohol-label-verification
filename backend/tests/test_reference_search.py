from __future__ import annotations

from decimal import Decimal

from labelverify.contracts.models import Candidate, CandidateSet, OcrLine, Point
from labelverify.domain.engine import ComparisonInputs, compare_all
from labelverify.domain.reference_search import find_text
from labelverify.domain.types import ObservedCandidates

from .helpers import clean_observed, found, reference


def ocr_line(text: str, order: int, *, y: int, x: int = 40, width: int = 400) -> OcrLine:
    return OcrLine(
        panelId="panel-1",
        text=text,
        polygon=[
            Point(x=x, y=y),
            Point(x=x + width, y=y),
            Point(x=x + width, y=y + 30),
            Point(x=x, y=y + 30),
        ],
        confidence=0.93,
        readingOrder=order,
        sourceView="original",
        transformId="transform-panel-1-v1",
    )


def with_lines(observed: ObservedCandidates, lines: list[OcrLine]) -> ObservedCandidates:
    return ObservedCandidates(
        fields=observed.fields,
        warning=observed.warning,
        panels=observed.panels,
        evidence=observed.evidence,
        lines=lines,
    )


def by_id(checks, check_id):  # type: ignore[no-untyped-def]
    return next(item for item in checks if item.check_id == check_id)


def test_application_brand_found_on_another_line_becomes_a_match_with_evidence() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("HARMONIE D'ESPRIT D'ECORCES", "brand")
    observed = with_lines(
        observed,
        [
            ocr_line("COINTREAU", 0, y=100),
            ocr_line("HARMONIE D'ESPRIT D'ECORCES", 1, y=300),
        ],
    )

    checks, _ = compare_all(ComparisonInputs(reference(brand="COINTREAU"), observed))
    brand = by_id(checks, "brand")

    assert brand.state == "Match"
    assert brand.reason_code == "reference_found_on_label"
    assert brand.evidence_ref is not None and brand.evidence_ref.startswith("ev_ref_brand_")
    assert any(item.evidence_id == brand.evidence_ref for item in observed.evidence)


def test_application_brand_with_different_case_stays_a_review_item() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("NAPA VALLEY", "brand")
    observed = with_lines(observed, [ocr_line("STONE'S THROW", 0, y=100)])

    checks, _ = compare_all(ComparisonInputs(reference(brand="Stone's Throw"), observed))

    assert by_id(checks, "brand").state == "Review"
    assert by_id(checks, "brand").reason_code == "case_variation"


def test_application_abv_found_on_another_line_overrides_a_mis_selected_candidate() -> None:
    observed = clean_observed()
    observed.fields["abv"] = found("12% Alc./Vol.", "abv")
    observed = with_lines(
        observed,
        [ocr_line("12% ALC BY VOL BONUS CLAIM", 0, y=100), ocr_line("45% Alc./Vol.", 1, y=200)],
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "abv").state == "Match"
    assert by_id(checks, "abv").reason_code == "reference_found_on_label"


def test_application_value_absent_from_every_line_remains_a_difference() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("RIVER BEND", "brand")
    observed = with_lines(observed, [ocr_line("RIVER BEND", 0, y=100), ocr_line("VODKA", 1, y=200)])

    checks, summary = compare_all(ComparisonInputs(reference(brand="OLD TOM DISTILLERY"), observed))

    assert by_id(checks, "brand").state == "Mismatch"
    assert summary == "Differences detected"


def test_label_derived_reference_never_searches_lines() -> None:
    observed = clean_observed()
    observed.fields["brand"] = CandidateSet(status="Not found")
    observed = with_lines(observed, [ocr_line("OLD TOM DISTILLERY", 0, y=100)])
    label_reference = reference().model_copy(update={"reference_provenance": "label_ocr"})

    checks, _ = compare_all(ComparisonInputs(label_reference, observed))

    assert by_id(checks, "brand").state == "Not verified"


def test_stacked_producer_lines_are_joined_for_the_search() -> None:
    lines = [
        ocr_line("Distilled and bottled by", 0, y=100),
        ocr_line("Northwind Spirits, Portland, Oregon", 1, y=135),
        ocr_line("750 mL", 2, y=300),
    ]

    match = find_text("Distilled and bottled by Northwind Spirits, Portland, Oregon", lines)

    assert match is not None
    assert match.quality == "exact"
    assert [line.reading_order for line in match.lines] == [0, 1]
    assert find_text("Bottled by Someone Else", lines) is None
    assert Decimal("1") == Decimal("1")


def test_application_brand_inside_the_company_address_line_stays_a_difference() -> None:
    observed = clean_observed()
    observed.fields["brand"] = found("CLEARWATER RESERVE", "brand")
    observed = with_lines(
        observed,
        [
            ocr_line("CLEARWATER RESERVE", 0, y=100),
            ocr_line("OLD TOM DISTILLERY LLC", 1, y=700),
            ocr_line("FRANKFORT, KENTUCKY 40601", 2, y=740),
        ],
    )

    checks, summary = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "brand").state == "Mismatch"
    assert summary == "Differences detected"


def test_rule_format_failure_is_never_erased_by_the_search() -> None:
    observed = clean_observed()
    abbreviated = found("45% ABV", "abv")
    abbreviated.candidates[0] = Candidate(
        value="45% ABV",
        evidence=abbreviated.candidates[0].evidence.model_copy(
            update={"text_snippet": "ALC. 45% ABV"}
        ),
    )
    observed.fields["abv"] = abbreviated
    observed = with_lines(observed, [ocr_line("ALC. 45% ABV", 0, y=100)])

    checks, summary = compare_all(ComparisonInputs(reference(), observed))

    # The application says 45 and the label says 45, but "ABV" is not an authorized
    # abbreviation (27 CFR 5.65); the label statement stands as read.
    assert by_id(checks, "abv").state == "Mismatch"
    assert by_id(checks, "abv").reason_code == "abv_abbreviation_not_authorized"
    assert summary == "Differences detected"


def test_a_percentage_outside_alcohol_context_does_not_satisfy_the_application() -> None:
    observed = clean_observed()
    observed.fields["abv"] = found("8.5% Alc./Vol.", "abv")
    observed = with_lines(
        observed,
        [ocr_line("8.5% ALC./VOL.", 0, y=100), ocr_line("CONTAINS 45% REAL FRUIT JUICE", 1, y=200)],
    )

    checks, _ = compare_all(ComparisonInputs(reference(), observed))

    assert by_id(checks, "abv").state == "Mismatch"
    assert by_id(checks, "abv").reason_code == "numeric_difference"
