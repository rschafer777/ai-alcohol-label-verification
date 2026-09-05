from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
from fastapi.testclient import TestClient
from labelverify.api.app import create_app
from labelverify.api.routes import _merge_reference_after_panel
from labelverify.contracts.loader import contracts
from labelverify.contracts.models import (
    AnalysisDraft,
    AnalysisResult,
    BeverageTypeCorrection,
    FieldSource,
    GroupingImage,
    OriginalDimensions,
    PanelResult,
    ReferenceRecord,
    StageTimings,
    TextCorrection,
)
from labelverify.domain.grouping import suggest_groups
from labelverify.domain.presentation import (
    apply_observation_provenance,
    check_group,
    present_checks,
    quality_summary,
    reason_short,
    statutory_tokens,
    wording_diff,
)
from labelverify.domain.types import serialize_observed
from labelverify.orchestration.revisions import (
    InvalidCorrection,
    apply_corrections,
    correction_items_for_replay,
)
from labelverify.orchestration.supervisor import SupervisorSnapshot

from .helpers import clean_observed, fake_result, found, jpeg_bytes, reference
from .test_api import runtime


def test_every_selected_check_has_a_group_short_label_and_rule_expectation() -> None:
    checks = present_checks(fake_result("present").checks, "distilled_spirits")
    assert len(checks) == 24
    assert [check_group(check.check_id) for check in checks[:3]] == ["identity"] * 3
    assert sum(check.group == "warning" for check in checks) == 10
    assert sum(check.group == "image" for check in checks) == 2
    for check in checks:
        assert check.short_label
        assert check.rule_expectation
        assert check.reason_short is not None
        assert len(check.reason_short) <= 40
    by_id = {check.check_id: check for check in checks}
    assert by_id["net_contents"].rule_expectation == "Metric statement for spirits"
    assert present_checks(fake_result("malt").checks, "malt_beverage")[5].rule_expectation == (
        "U.S. customary volume (metric may be additional)"
    )


def test_reason_short_never_exceeds_forty_characters_for_unknown_codes() -> None:
    check = (
        fake_result("long")
        .checks[0]
        .model_copy(
            update={
                "reason_code": "unmapped_code",
                "reason_text": (
                    "A very long sentence that certainly exceeds forty characters in total"
                ),
            }
        )
    )
    assert len(reason_short(check)) == 40


def test_observation_provenance_comes_from_label_evidence_not_reference() -> None:
    observed = clean_observed()
    checks = apply_observation_provenance(fake_result("provenance").checks, observed)
    brand = next(check for check in checks if check.check_id == "brand")
    assert brand.observation_provenance == "label_ocr"


def test_application_expectation_uses_field_level_reference_provenance() -> None:
    raw = fake_result("mixed-provenance").checks
    checks = [
        row.model_copy(update={"reference_display": "APPLICATION BRAND"})
        if row.check_id == "brand"
        else row.model_copy(update={"reference_display": "OCR CLASS"})
        if row.check_id == "class_type"
        else row
        for row in raw
    ]
    mixed = reference().model_copy(
        update={
            "reference_provenance": "manual",
            "field_provenance": {
                "brand_name": "trusted_application",
                "class_type": "label_ocr",
            },
        }
    )
    presented = present_checks(checks, mixed.beverage_type, mixed.reference_provenance, mixed)
    by_id = {row.check_id: row for row in presented}
    assert by_id["brand"].rule_expectation == "Application: APPLICATION BRAND"
    assert by_id["class_type"].rule_expectation != "Application: OCR CLASS"


def test_quality_summary_words_follow_signals() -> None:
    good = PanelResult(
        panelId="panel-1",
        originalDimensions=OriginalDimensions(width=10, height=10),
        qualitySignals={"laplacianVariance": 120.0, "darkFraction": 0.1, "lightFraction": 0.1},
        coverageState="Sufficient",
    )
    assert quality_summary(good).model_dump() == {"grade": "good", "issues": []}
    poor = good.model_copy(
        update={
            "coverage_state": "Review",
            "quality_signals": {"laplacianVariance": 20.0, "estimatedSkewDegrees": 3.0},
        }
    )
    assert quality_summary(poor).model_dump() == {"grade": "poor", "issues": ["blur", "skew"]}
    unreadable = good.model_copy(update={"coverage_state": "Unreadable"})
    assert quality_summary(unreadable).grade == "unreadable"


def test_wording_diff_aligns_to_the_statutory_tokens() -> None:
    expected = statutory_tokens()
    tokens, matched, total = wording_diff(
        "GOVERNMENT WARNING:",
        "(1) According to the Surgeon General, women should not drink alcoholic beverages "
        "during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic "
        "beverages impairs your ability to drive a car or operate machinery, and may cause "
        "health problems.",
    )
    assert total == len(expected)
    assert matched == total
    assert all(token.status == "match" for token in tokens)

    tokens, matched, total = wording_diff("Government Warning:", " ".join(expected[2:]))
    assert matched == total - 2
    assert [token.status for token in tokens[:3]] == ["different", "different", "match"]
    assert tokens[0].observed == "Government"

    tokens, matched, total = wording_diff(None, None)
    assert matched == 0
    assert all(token.status == "missing" for token in tokens)


def test_grouping_merges_same_brand_neighbours_and_flags_conflicts() -> None:
    images = [
        GroupingImage(
            imageId="a",
            fileName="IMG_0001.jpg",
            brandName="CEDAR CREEK",
            beverageType="distilled_spirits",
            typeConfidence="high",
        ),
        GroupingImage(
            imageId="b",
            fileName="IMG_0002.jpg",
            brandName="Cedar Creek",
            beverageType="distilled_spirits",
            typeConfidence="high",
        ),
        GroupingImage(
            imageId="c",
            fileName="IMG_0003.jpg",
            brandName=None,
            beverageType=None,
            typeConfidence=None,
        ),
        GroupingImage(
            imageId="d",
            fileName="wine/front.jpg",
            path="batch/wine/front.jpg",
            brandName="VALLE",
            beverageType="wine",
            typeConfidence="high",
        ),
        GroupingImage(
            imageId="e",
            fileName="wine/back.jpg",
            path="batch/wine/back.jpg",
            brandName="MIRROR LAKE",
            beverageType="wine",
            typeConfidence="high",
        ),
        GroupingImage(imageId="f", fileName="broken.jpg", failed=True),
    ]
    result = suggest_groups(images)
    assert result.analyzed == 5
    assert result.failed == 1
    by_panels = {frozenset(group.panel_ids): group for group in result.groups}
    same_brand = by_panels[frozenset({"a", "b"})]
    assert same_brand.status == "ready_to_confirm"
    assert same_brand.suggested_name == "CEDAR CREEK"
    assert "Same brand and compatible class read" in same_brand.reasons
    unread = by_panels[frozenset({"c"})]
    assert unread.status == "needs_review"
    assert unread.suggested_name.startswith("Product ")
    folder = by_panels[frozenset({"d", "e"})]
    assert folder.conflict is True
    assert folder.status == "needs_review"
    assert "Two different brands read" in folder.reasons
    assert all(len(group.panel_ids) <= 3 for group in result.groups)


def test_grouping_merges_nonadjacent_same_product_but_keeps_distinct_classes() -> None:
    images = [
        GroupingImage(
            imageId="front",
            fileName="alpha.jpg",
            brandName="NORTHWIND",
            classType="Pale Ale",
            beverageType="malt_beverage",
            typeConfidence="high",
        ),
        GroupingImage(
            imageId="other",
            fileName="middle.jpg",
            brandName="CEDAR RIDGE",
            classType="Riesling",
            beverageType="wine",
            typeConfidence="high",
        ),
        GroupingImage(
            imageId="back",
            fileName="zulu.jpg",
            brandName="Northwind",
            classType=None,
            beverageType="malt_beverage",
            typeConfidence="high",
        ),
        GroupingImage(
            imageId="stout",
            fileName="stout.jpg",
            brandName="NORTHWIND",
            classType="Stout",
            beverageType="malt_beverage",
            typeConfidence="high",
        ),
    ]

    result = suggest_groups(images)
    by_panels = {frozenset(group.panel_ids): group for group in result.groups}

    assert frozenset({"front", "back"}) in by_panels
    assert frozenset({"stout"}) in by_panels


def test_grouping_prefers_fuller_compatible_brand_read() -> None:
    images = [
        GroupingImage(
            imageId="back",
            fileName="Vodka_Back.jpg",
            brandName="ORGANIC",
            beverageType="distilled_spirits",
            typeConfidence="high",
        ),
        GroupingImage(
            imageId="front",
            fileName="Vodka_Front.jpg",
            brandName="OrganicVodka",
            beverageType="distilled_spirits",
            typeConfidence="medium",
        ),
    ]

    result = suggest_groups(images)

    assert len(result.groups) == 1
    assert result.groups[0].status == "ready_to_confirm"
    assert result.groups[0].conflict is False
    assert result.groups[0].suggested_name == "OrganicVodka"


class AddPanelSupervisor:
    ready = True

    def __init__(self) -> None:
        self.paths: list[tuple[Path, ...]] = []

    def start(self) -> bool:
        return True

    def stop(self) -> None:
        return None

    def snapshot(self) -> SupervisorSnapshot:
        return SupervisorSnapshot(True, 1, 0, 0, 0, 123)

    def run(self, request_id: str, reference: ReferenceRecord, paths: tuple[Path, ...]) -> object:
        self.paths.append(paths)
        return fake_result(request_id)

    def analyze(self, request_id: str, paths: tuple[Path, ...]) -> AnalysisResult:
        self.paths.append(paths)
        result = fake_result(request_id).model_copy(
            update={
                "stage_timings": StageTimings(
                    decodeMs=1,
                    preprocessMs=2,
                    ocrMs=3,
                    candidatesMs=4,
                    compareMs=5,
                    aggregateMs=6,
                ),
                "limitations": ["Fresh panel limitation"],
            }
        )
        return AnalysisResult(
            requestId=request_id,
            buildId="test",
            profileId="all_beverages_demo_v2",
            modelIdentity="fake",
            serverDurationMs=1.0,
            panels=result.panels,
            evidence=result.evidence,
            draft=AnalysisDraft(beverageType="distilled_spirits", brandName="OLD TOM"),
            detected={},
            beverageTypeConfidence=0.9,
            beverageTypeReason="test",
            limitations=[],
            verification=result,
        )


class UnresolvedSupervisor(AddPanelSupervisor):
    def analyze(self, request_id: str, paths: tuple[Path, ...]) -> AnalysisResult:
        resolved = super().analyze(request_id, paths)
        return resolved.model_copy(
            update={
                "draft": AnalysisDraft(brandName="CLOUD NINE", classType="Hard Seltzer"),
                "beverage_type_confidence": None,
                "beverage_type_reason": "Conflicting or insufficient type evidence",
                "beverage_inference": None,
                "verification": resolved.verification.model_copy(
                    update={"beverage_inference": None}
                )
                if resolved.verification is not None
                else None,
            }
        )


class ResolvedThenUnresolvedSupervisor(UnresolvedSupervisor):
    def analyze(self, request_id: str, paths: tuple[Path, ...]) -> AnalysisResult:
        if not self.paths:
            return AddPanelSupervisor.analyze(self, request_id, paths)
        return super().analyze(request_id, paths)


class FreshPanelSupervisor(AddPanelSupervisor):
    def analyze(self, request_id: str, paths: tuple[Path, ...]) -> AnalysisResult:
        resolved = super().analyze(request_id, paths)
        if len(self.paths) == 1:
            return resolved
        fresh_observed = clean_observed()
        fresh_observed.fields["brand"] = found("FRESH LABEL", "brand")
        fresh_verification = resolved.verification
        assert fresh_verification is not None
        return resolved.model_copy(
            update={
                "draft": resolved.draft.model_copy(update={"brand_name": "FRESH LABEL"}),
                "verification": fresh_verification.model_copy(
                    update={"observation_snapshot": serialize_observed(fresh_observed)}
                ),
            }
        )


class MixedSourcePanelSupervisor(AddPanelSupervisor):
    def analyze(self, request_id: str, paths: tuple[Path, ...]) -> AnalysisResult:
        resolved = super().analyze(request_id, paths)
        return resolved.model_copy(
            update={
                "draft": AnalysisDraft(
                    beverageType="distilled_spirits",
                    brandName="FRESH OCR BRAND",
                    classType="FRESH OCR CLASS",
                    abvPercent=47,
                    proof=94,
                    netContentsValue=750,
                    netContentsUnit="mL",
                    producerNameAddress="FRESH OCR PRODUCER, AUSTIN, TEXAS",
                )
            }
        )


class MixedSourceUnresolvedSupervisor(UnresolvedSupervisor):
    def analyze(self, request_id: str, paths: tuple[Path, ...]) -> AnalysisResult:
        unresolved = super().analyze(request_id, paths)
        return unresolved.model_copy(
            update={
                "draft": unresolved.draft.model_copy(
                    update={
                        "brand_name": "FRESH OCR BRAND",
                        "class_type": "FRESH OCR CLASS",
                        "abv_percent": 11.5,
                        "net_contents_value": 750,
                        "net_contents_unit": "mL",
                    }
                )
            }
        )


def test_grouping_endpoint_and_add_panel_supersede_flow(tmp_path: Path) -> None:
    supervisor = AddPanelSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        grouped = client.post(
            "/api/v1/grouping-suggestions",
            json={
                "images": [
                    {
                        "imageId": "x",
                        "fileName": "a.jpg",
                        "brandName": "BRAND",
                        "beverageType": "wine",
                        "typeConfidence": "high",
                    },
                ]
            },
        )
        assert grouped.status_code == 200, grouped.text
        assert grouped.json()["groups"][0]["status"] == "ready_to_confirm"
        assert client.post("/api/v1/grouping-suggestions", json={"images": []}).status_code == 422

        analyzed = client.post(
            "/api/v1/analyses",
            files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert analyzed.status_code == 200, analyzed.text
        first_id = analyzed.json()["verification"]["historyId"]

        added = client.post(
            f"/api/v1/history/{first_id}/panels?expectedRevision=1",
            files={"panels": ("second.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert added.status_code == 200, added.text
        body = added.json()
        assert body["verification"]["supersedes"] == first_id
        assert body["verification"]["historyId"] != first_id
        assert len(supervisor.paths[-1]) == 2
        assert client.get("/api/v1/history").json()["total"] == 1
        detail = client.get(f"/api/v1/history/{body['verification']['historyId']}").json()
        assert detail["panelCount"] == 2
        assert detail["result"]["supersedes"] == first_id
        assert detail["revision"] == 2
        assert len(detail["revisions"]) == 2

        missing = client.post(
            "/api/v1/history/hist_0000/panels",
            files={"panels": ("third.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert missing.status_code == 404


def test_added_panel_refreshes_label_derived_reference_without_false_mismatch(
    tmp_path: Path,
) -> None:
    supervisor = FreshPanelSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        original = client.post(
            "/api/v1/analyses",
            files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
        ).json()["verification"]
        added = client.post(
            f"/api/v1/history/{original['historyId']}/panels?expectedRevision=1",
            files={"panels": ("second.jpg", jpeg_bytes(), "image/jpeg")},
        )

        assert added.status_code == 200, added.text
        result = added.json()["verification"]
        brand = next(row for row in result["checks"] if row["checkId"] == "brand")
        assert brand["state"] == "Match"
        assert brand["referenceDisplay"] == "FRESH LABEL"
        assert brand["observedDisplay"] == "FRESH LABEL"
        detail = client.get(f"/api/v1/history/{result['historyId']}").json()
        assert detail["reference"]["brandName"] == "FRESH LABEL"


def test_added_panel_preserves_explicit_mixed_provenance_for_every_field() -> None:
    previous = reference().model_copy(
        update={
            "reference_provenance": "manual",
            "field_provenance": {
                "beverage_type": "trusted_application",
                "brand_name": "trusted_application",
                "class_type": "label_ocr",
                "alcohol_content": "label_ocr",
                "proof": "label_ocr",
                "net_contents": "label_ocr",
                "producer_name_address": "label_ocr",
                "country_of_origin": "label_ocr",
                "wine_appellation": "label_ocr",
                "wine_sulfite_declaration": "label_ocr",
                "malt_alcohol_source": "trusted_application",
            },
            "malt_alcohol_source": "added_ingredients",
        }
    )
    fresh = reference(brand="FRESH LABEL").model_copy(
        update={
            "reference_provenance": "label_ocr",
            "class_type": "Fresh class",
            "malt_alcohol_source": "none",
        }
    )

    merged = _merge_reference_after_panel(previous, fresh)

    assert merged.brand_name == previous.brand_name
    assert merged.class_type == "Fresh class"
    assert merged.malt_alcohol_source == "added_ingredients"
    assert set(merged.field_provenance) == {
        "beverage_type",
        "brand_name",
        "class_type",
        "alcohol_content",
        "proof",
        "net_contents",
        "producer_name_address",
        "country_of_origin",
        "wine_appellation",
        "wine_sulfite_declaration",
        "malt_alcohol_source",
    }
    assert merged.field_provenance["class_type"] == "label_ocr"
    assert merged.field_provenance["malt_alcohol_source"] == "trusted_application"


def test_added_panel_replaces_stale_label_family_with_unresolved_state(tmp_path: Path) -> None:
    supervisor = ResolvedThenUnresolvedSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        original = client.post(
            "/api/v1/analyses",
            files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
        ).json()["verification"]
        added = client.post(
            f"/api/v1/history/{original['historyId']}/panels?expectedRevision=1",
            files={"panels": ("conflicting.jpg", jpeg_bytes(), "image/jpeg")},
        )

        assert added.status_code == 200, added.text
        body = added.json()
        assert body["draft"]["beverageType"] is None
        assert body["verification"]["beverageInference"] is None
        type_check = next(
            row for row in body["verification"]["checks"] if row["checkId"] == "beverage_type"
        )
        assert type_check["state"] == "Review"
        detail = client.get(f"/api/v1/history/{body['verification']['historyId']}").json()
        assert detail["reference"]["beverageType"] is None


def test_correction_replay_uses_the_latest_value_and_latest_source_locator() -> None:
    events = [
        {
            "field": "brand_name",
            "visibleText": "FIRST READ",
            "sourcePanelId": "panel-1",
            "sourcePolygon": [
                {"x": 10, "y": 10},
                {"x": 110, "y": 10},
                {"x": 110, "y": 40},
                {"x": 10, "y": 40},
            ],
            "sourceImageSha256": "a" * 64,
        },
        {
            "field": "brand_name",
            "visibleText": "LATEST READ",
            "sourcePanelId": "panel-2",
            "sourcePolygon": [
                {"x": 20, "y": 20},
                {"x": 220, "y": 20},
                {"x": 220, "y": 80},
                {"x": 20, "y": 80},
            ],
            "sourceImageSha256": "b" * 64,
        },
    ]

    replay = correction_items_for_replay(
        events, panel_hashes={"panel-1": "a" * 64, "panel-2": "b" * 64}
    )

    assert len(replay) == 1
    assert replay[0].panel_id == "panel-2"
    assert replay[0].visible_text == "LATEST READ"  # type: ignore[union-attr]
    assert replay[0].polygon is not None
    assert replay[0].polygon[0].model_dump() == {"x": 20, "y": 20}


def test_class_correction_reinfers_family_and_rejects_conflicting_class() -> None:
    label_reference = reference().model_copy(update={"reference_provenance": "label_ocr"})
    observed = clean_observed()
    wine = TextCorrection(
        field="class_type",
        visibleText="Riesling",
        evidenceRef="ev_class_type_panel-1_01",
    )

    corrected_reference, corrected_observed, _ = apply_corrections(
        label_reference,
        observed,
        [wine],
        panel_hashes={"panel-1": "a" * 64},
    )

    assert corrected_reference.beverage_type == "wine"
    assert corrected_observed.field("beverage_type").candidates[0].value == "wine"

    conflicting = TextCorrection(
        field="class_type",
        visibleText="Riesling Ale",
        evidenceRef="ev_class_type_panel-1_01",
    )
    with pytest.raises(InvalidCorrection, match="confirm beverage type too"):
        apply_corrections(
            label_reference,
            observed,
            [conflicting],
            panel_hashes={"panel-1": "a" * 64},
        )


def test_class_correction_does_not_override_reviewer_corrected_family() -> None:
    label_reference = reference().model_copy(update={"reference_provenance": "label_ocr"})
    observed = clean_observed()
    corrected_reference, corrected_observed, _ = apply_corrections(
        label_reference,
        observed,
        [
            BeverageTypeCorrection(
                field="beverage_type",
                family="wine",
                evidenceRef="ev_class_type_panel-1_01",
            )
        ],
        panel_hashes={"panel-1": "a" * 64},
    )

    final_reference, final_observed, _ = apply_corrections(
        corrected_reference,
        corrected_observed,
        [
            TextCorrection(
                field="class_type",
                visibleText="Kentucky Bourbon Whiskey",
                evidenceRef="ev_class_type_panel-1_01",
            )
        ],
        panel_hashes={"panel-1": "a" * 64},
    )

    assert final_reference.beverage_type == "wine"
    assert final_reference.source_for("beverage_type") == "reviewer_corrected"
    assert final_observed.field("beverage_type").candidates[0].value == "wine"


def test_sulfite_correction_requires_a_visible_presence_statement() -> None:
    label_reference = reference().model_copy(
        update={"reference_provenance": "label_ocr", "beverage_type": "wine"}
    )
    observed = clean_observed()
    absence = TextCorrection(
        field="wine_sulfite_declaration",
        visibleText="Not present",
        evidenceRef="ev_class_type_panel-1_01",
    )
    with pytest.raises(InvalidCorrection, match="contains-sulfites statement"):
        apply_corrections(
            label_reference,
            observed,
            [absence],
            panel_hashes={"panel-1": "a" * 64},
        )

    presence = TextCorrection(
        field="wine_sulfite_declaration",
        visibleText="Contains Sulfites",
        evidenceRef="ev_class_type_panel-1_01",
    )
    corrected_reference, corrected_observed, events = apply_corrections(
        label_reference,
        observed,
        [presence],
        panel_hashes={"panel-1": "a" * 64},
    )
    assert corrected_reference.wine_sulfite_status == "present"
    assert corrected_observed.field("wine_sulfites").candidates[0].value == "Contains Sulfites"
    assert events[0]["derivedValue"] == {
        "status": "present",
        "printedStatement": "Contains Sulfites",
    }


def test_numeric_correction_audit_retains_printed_forms_units_and_precision() -> None:
    label_reference = reference().model_copy(update={"reference_provenance": "label_ocr"})
    corrections = [
        TextCorrection(
            field="alcohol_content",
            visibleText="11.50% ALC/VOL.",
            evidenceRef="ev_abv_panel-1_01",
        ),
        TextCorrection(
            field="proof",
            visibleText="23.0 PROOF",
            evidenceRef="ev_proof_panel-1_01",
        ),
        TextCorrection(
            field="net_contents",
            visibleText="1.50 L",
            evidenceRef="ev_net_contents_panel-1_01",
        ),
    ]

    _, _, events = apply_corrections(
        label_reference,
        clean_observed(),
        corrections,
        panel_hashes={"panel-1": "a" * 64},
    )
    derived = {event["field"]: event["derivedValue"] for event in events}
    assert derived["alcohol_content"] == {
        "abvPercent": "11.50",
        "range": None,
        "percentForm": "11.50%",
        "abbreviation": "ALC/VOL.",
        "decimalPrecision": 2,
    }
    assert derived["proof"] == {
        "proof": "23.0",
        "proofWording": "23.0 PROOF",
        "decimalPrecision": 1,
    }
    assert derived["net_contents"] == {
        "value": "1.50",
        "unit": "L",
        "printedUnit": "L",
        "decimalPrecision": 2,
    }

    _, _, range_events = apply_corrections(
        label_reference,
        clean_observed(),
        [
            TextCorrection(
                field="alcohol_content",
                visibleText="7.0% to 10.00% ALC/VOL.",
                evidenceRef="ev_abv_panel-1_01",
            )
        ],
        panel_hashes={"panel-1": "a" * 64},
    )
    assert range_events[0]["derivedValue"] == {
        "abvPercent": "7.0",
        "range": {"minimum": "7.0", "maximum": "10.00"},
        "percentForm": "7.0%",
        "abbreviation": "ALC/VOL.",
        "decimalPrecision": 1,
    }


def test_unresolved_type_stays_unresolved_until_reviewer_cites_label_evidence(
    tmp_path: Path,
) -> None:
    app = create_app(  # type: ignore[arg-type]
        settings=runtime(tmp_path), supervisor=UnresolvedSupervisor()
    )
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        original = client.post(
            "/api/v1/analyses",
            files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
        ).json()["verification"]
        added = client.post(
            f"/api/v1/history/{original['historyId']}/panels?expectedRevision=1",
            files={"panels": ("second.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert added.status_code == 200, added.text
        assert added.json()["draft"]["beverageType"] is None
        assert added.json()["verification"]["beverageInference"] is None
        current_id = added.json()["verification"]["historyId"]
        detail = client.get(f"/api/v1/history/{current_id}").json()
        assert detail["reference"]["beverageType"] is None

        missing_type = client.post(
            f"/api/v1/history/{current_id}/corrections",
            json={
                "expectedRevision": 2,
                "reason": "Correct the visible brand only",
                "corrections": [
                    {
                        "field": "brand_name",
                        "visibleText": "CLOUD NINE",
                        "panelId": "panel-1",
                        "polygon": [
                            {"x": 10, "y": 10},
                            {"x": 100, "y": 10},
                            {"x": 100, "y": 50},
                            {"x": 10, "y": 50},
                        ],
                    }
                ],
            },
        )
        assert missing_type.status_code == 422
        assert missing_type.json()["code"] == "invalid_correction"

        resolved = client.post(
            f"/api/v1/history/{current_id}/corrections",
            json={
                "expectedRevision": 2,
                "reason": "Reviewer confirmed the visible beverage family",
                "corrections": [
                    {
                        "field": "beverage_type",
                        "family": "malt_beverage",
                        "panelId": "panel-1",
                        "polygon": [
                            {"x": 10, "y": 10},
                            {"x": 100, "y": 10},
                            {"x": 100, "y": 50},
                            {"x": 10, "y": 50},
                        ],
                    }
                ],
            },
        )
        assert resolved.status_code == 200, resolved.text
        assert resolved.json()["result"]["beverageInference"]["type"] == "malt_beverage"


def test_correction_creates_zero_ocr_revision(tmp_path: Path) -> None:
    supervisor = AddPanelSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        analyzed = client.post(
            "/api/v1/analyses",
            files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert analyzed.status_code == 200, analyzed.text
        original = analyzed.json()["verification"]
        original_id = original["historyId"]
        calls_before = len(supervisor.paths)

        corrected = client.post(
            f"/api/v1/history/{original_id}/corrections",
            json={
                "expectedRevision": 1,
                "reason": "Reviewer confirmed the visible brand",
                "actorLabel": "Reviewer",
                "corrections": [
                    {
                        "field": "brand_name",
                        "visibleText": "OLD TOM DISTILLERY",
                        "evidenceRef": "ev_brand_panel-1_01",
                    }
                ],
            },
        )
        assert corrected.status_code == 200, corrected.text
        envelope = corrected.json()
        assert envelope["revision"] == 2
        assert envelope["parentId"] == original_id
        body = envelope["result"]
        assert body["revisionKind"] == "correction"
        assert body["stageTimings"]["ocrMs"] == 0
        assert len(supervisor.paths) == calls_before
        brand = next(item for item in body["checks"] if item["checkId"] == "brand")
        assert brand["observationProvenance"] == "reviewer_corrected"
        assert brand["reasonCode"] == "reviewer_corrected_label_value"
        listing = client.get("/api/v1/history").json()
        assert listing["total"] == 1
        assert listing["items"][0]["revision"] == 2

        corrected_id = body["historyId"]
        added = client.post(
            f"/api/v1/history/{corrected_id}/panels?expectedRevision=2",
            files={"panels": ("second.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert added.status_code == 200, added.text
        added_body = added.json()
        assert added_body["draft"]["brandName"] == "OLD TOM DISTILLERY"
        assert added_body["verification"]["revision"] == 3
        assert added_body["verification"]["revisionKind"] == "panel_added"
        assert added_body["verification"]["stageTimings"]["ocrMs"] == 3
        assert "Fresh panel limitation" in added_body["verification"]["limitations"]
        added_brand = next(
            item for item in added_body["verification"]["checks"] if item["checkId"] == "brand"
        )
        assert added_brand["observationProvenance"] == "reviewer_corrected"
        added_detail = client.get(
            f"/api/v1/history/{added_body['verification']['historyId']}"
        ).json()
        assert len(added_detail["corrections"]) == 1
        audit = added_detail["corrections"][0]
        assert audit["oldValue"] == "brand"
        assert audit["correctedValue"] == "OLD TOM DISTILLERY"
        assert audit["rawVisibleText"] == "OLD TOM DISTILLERY"
        assert audit["derivedValue"] == {"text": "OLD TOM DISTILLERY"}
        assert audit["sourcePanelId"] == "panel-1"
        assert len(audit["sourcePolygon"]) == 4
        assert len(audit["sourceImageSha256"]) == 64
        assert audit["reason"] == "Reviewer confirmed the visible brand"
        assert audit["actorLabel"] == "Reviewer"
        assert audit["createdAt"].endswith("+00:00")
        assert len(added_detail["revisions"]) == 3

        stale = client.post(
            f"/api/v1/history/{original_id}/corrections",
            json={
                "expectedRevision": 1,
                "reason": "Stale write",
                "corrections": [
                    {
                        "field": "brand_name",
                        "visibleText": "OLD TOM",
                        "evidenceRef": "ev_brand_panel-1_01",
                    }
                ],
            },
        )
        assert stale.status_code == 409
        assert stale.json()["code"] == "revision_conflict"


def test_trusted_application_reference_survives_correction_and_added_panel(
    tmp_path: Path,
) -> None:
    supervisor = AddPanelSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    trusted = ReferenceRecord(
        profileId="all_beverages_demo_v2",
        beverageType="distilled_spirits",
        referenceProvenance="manual",
        fieldProvenance={
            "beverage_type": "trusted_application",
            "brand_name": "trusted_application",
        },
        brandName="APPLICATION BRAND",
        classType="Whiskey",
        abvPercent=40,
        proof=80,
        netContentsValue=750,
        netContentsUnit="mL",
        producerNameAddress="APPLICATION PRODUCER, DENVER, COLORADO",
        isImported=False,
    )
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        created = client.post(
            "/api/v1/verifications",
            data={"reference": trusted.model_dump_json(by_alias=True)},
            files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert created.status_code == 200, created.text
        original_id = created.json()["historyId"]

        corrected = client.post(
            f"/api/v1/history/{original_id}/corrections",
            json={
                "expectedRevision": 1,
                "reason": "Reviewer corrected the label observation",
                "corrections": [
                    {
                        "field": "brand_name",
                        "visibleText": "LABEL BRAND",
                        "evidenceRef": "ev_brand_panel-1_01",
                    }
                ],
            },
        )
        assert corrected.status_code == 200, corrected.text
        corrected_result = corrected.json()["result"]
        corrected_id = corrected_result["historyId"]
        brand = next(row for row in corrected_result["checks"] if row["checkId"] == "brand")
        assert brand["state"] == "Mismatch"
        assert brand["referenceDisplay"] == "APPLICATION BRAND"
        assert brand["observedDisplay"] == "LABEL BRAND"
        assert brand["observationProvenance"] == "reviewer_corrected"
        detail = client.get(f"/api/v1/history/{corrected_id}").json()
        assert detail["reference"]["brandName"] == "APPLICATION BRAND"

        added = client.post(
            f"/api/v1/history/{corrected_id}/panels?expectedRevision=2",
            files={"panels": ("second.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert added.status_code == 200, added.text
        added_result = added.json()["verification"]
        added_brand = next(row for row in added_result["checks"] if row["checkId"] == "brand")
        assert added_brand["state"] == "Mismatch"
        assert added_brand["referenceDisplay"] == "APPLICATION BRAND"
        assert added_brand["observedDisplay"] == "LABEL BRAND"
        added_detail = client.get(f"/api/v1/history/{added_result['historyId']}").json()
        assert added_detail["reference"]["brandName"] == "APPLICATION BRAND"


def _mixed_source_reference(*, beverage_source: FieldSource) -> ReferenceRecord:
    return ReferenceRecord(
        profileId="all_beverages_demo_v2",
        beverageType="distilled_spirits",
        referenceProvenance="manual",
        fieldProvenance={
            "beverage_type": beverage_source,
            "brand_name": "trusted_application",
            "class_type": "label_ocr",
            "alcohol_content": "label_ocr",
            "proof": "label_ocr",
            "net_contents": "label_ocr",
            "producer_name_address": "label_ocr",
            "country_of_origin": "label_ocr",
            "wine_appellation": "label_ocr",
            "wine_sulfite_declaration": "label_ocr",
            "malt_alcohol_source": "label_ocr",
        },
        brandName="APPLICATION BRAND",
        classType="INITIAL OCR CLASS",
        abvPercent=Decimal("40"),
        proof=Decimal("80"),
        netContentsValue=Decimal("750"),
        netContentsUnit="mL",
        producerNameAddress="INITIAL OCR PRODUCER, DENVER, COLORADO",
        isImported=False,
    )


def _correct_class_and_add_panel(
    client: TestClient, reference_record: ReferenceRecord
) -> dict[str, Any]:
    created = client.post(
        "/api/v1/verifications",
        data={"reference": reference_record.model_dump_json(by_alias=True)},
        files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
    )
    assert created.status_code == 200, created.text
    corrected = client.post(
        f"/api/v1/history/{created.json()['historyId']}/corrections",
        json={
            "expectedRevision": 1,
            "reason": "Reviewer confirmed the visible class",
            "corrections": [
                {
                    "field": "class_type",
                    "visibleText": "REVIEWER CLASS",
                    "evidenceRef": "ev_class_type_panel-1_01",
                }
            ],
        },
    )
    assert corrected.status_code == 200, corrected.text
    corrected_result = corrected.json()["result"]
    added = client.post(
        f"/api/v1/history/{corrected_result['historyId']}/panels?expectedRevision=2",
        files={"panels": ("second.jpg", jpeg_bytes(), "image/jpeg")},
    )
    assert added.status_code == 200, added.text
    return cast(dict[str, Any], added.json())


def test_resolved_add_panel_response_reconciles_values_and_mixed_provenance(
    tmp_path: Path,
) -> None:
    app = create_app(
        settings=runtime(tmp_path), supervisor=MixedSourcePanelSupervisor()  # type: ignore[arg-type]
    )
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        body = _correct_class_and_add_panel(
            client, _mixed_source_reference(beverage_source="trusted_application")
        )
        draft = body["draft"]
        assert draft["brandName"] == "APPLICATION BRAND"
        assert draft["classType"] == "REVIEWER CLASS"
        assert draft["abvPercent"] == 47
        assert draft["fieldProvenance"]["brand_name"] == "trusted_application"
        assert draft["fieldProvenance"]["class_type"] == "reviewer_corrected"
        assert draft["fieldProvenance"]["alcohol_content"] == "label_ocr"
        detail = client.get(
            f"/api/v1/history/{body['verification']['historyId']}"
        ).json()
        assert detail["reference"]["brandName"] == draft["brandName"]
        assert detail["reference"]["classType"] == draft["classType"]
        assert float(detail["reference"]["abvPercent"]) == draft["abvPercent"]


def test_unresolved_add_panel_response_reconciles_values_and_mixed_provenance(
    tmp_path: Path,
) -> None:
    app = create_app(
        settings=runtime(tmp_path),
        supervisor=MixedSourceUnresolvedSupervisor(),  # type: ignore[arg-type]
    )
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        body = _correct_class_and_add_panel(
            client, _mixed_source_reference(beverage_source="label_ocr")
        )
        draft = body["draft"]
        assert draft["beverageType"] is None
        assert draft["brandName"] == "APPLICATION BRAND"
        assert draft["classType"] == "REVIEWER CLASS"
        assert draft["abvPercent"] == 11.5
        assert draft["fieldProvenance"]["beverage_type"] == "label_ocr"
        assert draft["fieldProvenance"]["brand_name"] == "trusted_application"
        assert draft["fieldProvenance"]["class_type"] == "reviewer_corrected"
        assert draft["fieldProvenance"]["alcohol_content"] == "label_ocr"
        detail = client.get(
            f"/api/v1/history/{body['verification']['historyId']}"
        ).json()
        assert detail["reference"] == draft


def test_correction_accepts_manual_panel_polygon_when_ocr_has_no_region(
    tmp_path: Path,
) -> None:
    supervisor = AddPanelSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        analyzed = client.post(
            "/api/v1/analyses",
            files={"panels": ("first.jpg", jpeg_bytes(), "image/jpeg")},
        )
        original_id = analyzed.json()["verification"]["historyId"]
        corrected = client.post(
            f"/api/v1/history/{original_id}/corrections",
            json={
                "expectedRevision": 1,
                "reason": "Reviewer bounded visible label text",
                "corrections": [
                    {
                        "field": "country_of_origin",
                        "visibleText": "Canada",
                        "panelId": "panel-1",
                        "polygon": [
                            {"x": 10, "y": 10},
                            {"x": 200, "y": 10},
                            {"x": 200, "y": 80},
                            {"x": 10, "y": 80},
                        ],
                    }
                ],
            },
        )
        assert corrected.status_code == 200, corrected.text
        result = corrected.json()["result"]
        country = next(row for row in result["checks"] if row["checkId"] == "country")
        assert country["observedDisplay"] == "Canada"
        assert country["observationProvenance"] == "reviewer_corrected"


def test_manual_correction_rejects_boundary_and_degenerate_polygons() -> None:
    label_reference = reference().model_copy(update={"reference_provenance": "label_ocr"})
    observed = clean_observed()
    for polygon in (
        [
            {"x": 10, "y": 10},
            {"x": 800, "y": 10},
            {"x": 800, "y": 40},
            {"x": 10, "y": 40},
        ],
        [
            {"x": 10, "y": 10},
            {"x": 20, "y": 10},
            {"x": 30, "y": 10},
            {"x": 40, "y": 10},
        ],
    ):
        with pytest.raises(InvalidCorrection, match="polygon is invalid"):
            apply_corrections(
                label_reference,
                observed,
                [
                    TextCorrection.model_validate(
                        {
                            "field": "brand_name",
                            "visibleText": "VISIBLE BRAND",
                            "panelId": "panel-1",
                            "polygon": polygon,
                        }
                    )
                ],
                panel_hashes={"panel-1": "a" * 64},
            )

    corrected, _, _ = apply_corrections(
        label_reference,
        observed,
        [
            TextCorrection.model_validate(
                {
                    "field": "brand_name",
                    "visibleText": "VISIBLE BRAND",
                    "panelId": "panel-1",
                    "polygon": [
                        {"x": 10, "y": 10},
                        {"x": 799, "y": 10},
                        {"x": 799, "y": 40},
                        {"x": 10, "y": 40},
                    ],
                }
            )
        ],
        panel_hashes={"panel-1": "a" * 64},
    )
    assert corrected.brand_name == "VISIBLE BRAND"


def test_grouping_endpoint_accepts_maximum_shape_request(tmp_path: Path) -> None:
    supervisor = AddPanelSupervisor()
    app = create_app(settings=runtime(tmp_path), supervisor=supervisor)  # type: ignore[arg-type]
    long_path = "batch/product/" + ("p" * 1010)
    images = [
        {
            "imageId": f"{index:03d}" + ("i" * 117),
            "fileName": ("f" * 256) + ".jpg",
            "path": long_path,
            "brandName": "B" * 160,
            "classType": "C" * 240,
            "beverageType": "wine",
            "typeConfidence": "high",
            "failed": False,
        }
        for index in range(900)
    ]
    payload = {"images": images}
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    assert len(encoded) > 512 * 1024
    assert len(encoded) < int(contracts().api["limits"]["groupingRequestBytes"])

    with TestClient(app, client=("127.0.0.1", 50000)) as client:
        response = client.post("/api/v1/grouping-suggestions", json=payload)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["analyzed"] == 900
    assert body["failed"] == 0
    assert len(body["groups"]) == 300
    assert all(len(group["panelIds"]) == 3 for group in body["groups"])
