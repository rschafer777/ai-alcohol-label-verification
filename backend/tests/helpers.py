from __future__ import annotations

import io
from decimal import Decimal

from labelverify.contracts.loader import contracts
from labelverify.contracts.models import (
    Candidate,
    CandidateSet,
    CheckResult,
    ConfidenceProvenance,
    Evidence,
    OriginalDimensions,
    PanelResult,
    Point,
    ReferenceRecord,
    StageTimings,
    VerificationResult,
)
from labelverify.domain.types import ObservedCandidates, WarningObservation
from PIL import Image, ImageDraw


def reference(*, imported: bool = False, brand: str = "OLD TOM DISTILLERY") -> ReferenceRecord:
    return ReferenceRecord(
        profileId="all_beverages_demo_v2",
        beverageType="distilled_spirits",
        referenceProvenance="manual",
        brandName=brand,
        classType="Kentucky Straight Bourbon Whiskey",
        abvPercent=Decimal("45"),
        proof=Decimal("90"),
        netContentsValue=Decimal("750"),
        netContentsUnit="mL",
        producerNameAddress="BOTTLED BY: OLD HERITAGE DISTILLERY, LLC FRANKFORT, KENTUCKY",
        isImported=imported,
        countryOfOrigin="Canada" if imported else None,
    )


def evidence(role: str, sequence: int = 1, *, x: int = 10, y: int = 10) -> Evidence:
    return Evidence(
        evidenceId=f"ev_{role}_panel-1_{sequence:02d}",
        panelId="panel-1",
        polygonOriginalPixels=[
            Point(x=x, y=y),
            Point(x=x + 100, y=y),
            Point(x=x + 100, y=y + 30),
            Point(x=x, y=y + 30),
        ],
        sourceView="original",
        transformId="transform-panel-1-v1",
        textSnippet=role,
        confidenceProvenance=ConfidenceProvenance(
            source="test", signal=0.99, calibratedProbability=False
        ),
    )


def found(value: str, role: str, sequence: int = 1) -> CandidateSet:
    return CandidateSet(
        status="Found",
        candidates=[Candidate(value=value, evidence=evidence(role, sequence))],
    )


def clean_observed(*, imported: bool = False) -> ObservedCandidates:
    rules = contracts().rules["warning"]
    fields = {
        "brand": found("OLD TOM DISTILLERY", "brand"),
        "class_type": found("Kentucky Straight Bourbon Whiskey", "class_type"),
        "abv": found("45% Alc./Vol.", "abv"),
        "proof": found("90 Proof", "proof"),
        "net_contents": found("750 mL", "net_contents"),
        "producer": found(
            "BOTTLED BY: OLD HERITAGE DISTILLERY, LLC FRANKFORT, KENTUCKY",
            "producer",
        ),
        "country": found("Canada", "country") if imported else CandidateSet(status="Not found"),
    }
    warning_evidence = evidence("warning", 1, x=20, y=100)
    warning = WarningObservation(
        heading=rules["headingExact"],
        body=rules["bodyExact"],
        full_text=f"{rules['headingExact']} {rules['bodyExact']}",
        heading_evidence=warning_evidence,
        body_evidence=warning_evidence,
        heading_bold=True,
        body_bold=False,
        separated=True,
        continuous=True,
        contrast_sufficient=True,
        legible=True,
        physical_size_mm=2.0,
        characters_per_inch=20.0,
        reliable_scale=True,
        scale_evidence=warning_evidence,
    )
    panel = PanelResult(
        panelId="panel-1",
        originalDimensions=OriginalDimensions(width=800, height=1200),
        qualitySignals={"qualityClass": "Sufficient"},
        coverageState="Sufficient",
    )
    all_evidence = [item.candidates[0].evidence for item in fields.values() if item.candidates]
    all_evidence.append(warning_evidence)
    return ObservedCandidates(fields, warning, [panel], all_evidence)


def jpeg_bytes() -> bytes:
    image = Image.new("RGB", (640, 900), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 40, 600, 860), outline="black", width=5)
    draw.text((80, 100), "OLD TOM DISTILLERY", fill="black")
    draw.text((80, 180), "45% Alc./Vol. 90 Proof", fill="black")
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=90)
    return output.getvalue()


def fake_result(request_id: str = "request") -> VerificationResult:
    checks = [
        CheckResult(
            checkId=check_id,
            label=check_id,
            applicable=True,
            state="Match",
            reasonCode="test_match",
            reasonText="Test match",
            alternatives=[],
            capability="test",
            policyVersion="1.0.0",
        )
        for check_id in contracts().check_ids
    ]
    return VerificationResult(
        requestId=request_id,
        buildId="test-build",
        profileId="all_beverages_demo_v2",
        profileVersion="1.0.0",
        modelIdentity="test-model",
        ruleSources=["test-rule"],
        serverDurationMs=1,
        stageTimings=StageTimings(
            decodeMs=0,
            preprocessMs=0,
            ocrMs=0,
            candidatesMs=0,
            compareMs=0,
            aggregateMs=0,
        ),
        panels=[
            PanelResult(
                panelId="panel-1",
                originalDimensions=OriginalDimensions(width=640, height=900),
                qualitySignals={"qualityClass": "Sufficient"},
                coverageState="Sufficient",
            )
        ],
        evidence=[],
        checks=checks,
        limitations=[],
        summary="No differences found in checked fields",
    )
