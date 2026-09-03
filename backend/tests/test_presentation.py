from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient
from labelverify.api.app import create_app
from labelverify.contracts.loader import contracts
from labelverify.contracts.models import (
    AnalysisDraft,
    AnalysisResult,
    GroupingImage,
    OriginalDimensions,
    PanelResult,
    ReferenceRecord,
)
from labelverify.domain.grouping import suggest_groups
from labelverify.domain.presentation import (
    check_group,
    present_checks,
    quality_summary,
    reason_short,
    statutory_tokens,
    wording_diff,
)
from labelverify.orchestration.supervisor import SupervisorSnapshot

from .helpers import fake_result, jpeg_bytes
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
        result = fake_result(request_id)
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
            f"/api/v1/history/{first_id}/panels",
            files={"panels": ("second.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert added.status_code == 200, added.text
        body = added.json()
        assert body["verification"]["supersedes"] == first_id
        assert body["verification"]["historyId"] != first_id
        assert len(supervisor.paths[-1]) == 2
        assert client.get("/api/v1/history").json()["total"] == 2
        detail = client.get(f"/api/v1/history/{body['verification']['historyId']}").json()
        assert detail["panelCount"] == 2
        assert detail["result"]["supersedes"] == first_id

        missing = client.post(
            "/api/v1/history/hist_0000/panels",
            files={"panels": ("third.jpg", jpeg_bytes(), "image/jpeg")},
        )
        assert missing.status_code == 404


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
