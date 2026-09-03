from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
BeverageType = Literal["malt_beverage", "wine", "distilled_spirits"]
VolumeUnit = Literal["mL", "L", "fl oz", "pt", "qt", "gal"]
CheckState = Literal["Match", "Mismatch", "Review", "Not verified"]
CandidateStatus = Literal["Found", "Ambiguous", "Not found", "Unreadable"]
SummaryState = Literal[
    "Differences detected",
    "Review needed",
    "No differences found in checked fields",
]


class ContractModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class ReferenceRecord(ContractModel):
    profile_id: Literal["all_beverages_demo_v2"] = Field(alias="profileId")
    beverage_type: BeverageType = Field(alias="beverageType")
    reference_provenance: Literal["label_ocr", "manual", "manifest", "sample"] = Field(
        default="manual", alias="referenceProvenance"
    )
    case_label: str | None = Field(default=None, max_length=80, alias="caseLabel")
    brand_name: NonBlank = Field(max_length=160, alias="brandName")
    class_type: NonBlank = Field(max_length=240, alias="classType")
    abv_percent: Decimal | None = Field(default=None, ge=0, le=100, alias="abvPercent")
    proof: Decimal | None = Field(default=None, ge=0)
    net_contents_value: Decimal = Field(gt=0, alias="netContentsValue")
    net_contents_unit: VolumeUnit = Field(alias="netContentsUnit")
    producer_name_address: NonBlank = Field(max_length=500, alias="producerNameAddress")
    is_imported: bool = Field(alias="isImported")
    country_of_origin: str | None = Field(default=None, max_length=80, alias="countryOfOrigin")
    wine_appellation: str | None = Field(default=None, max_length=160, alias="wineAppellation")
    wine_sulfite_status: Literal["present", "not_present", "unknown"] = Field(
        default="unknown", alias="wineSulfiteStatus"
    )
    malt_alcohol_source: Literal["added_ingredients", "none", "unknown"] = Field(
        default="unknown", alias="maltAlcoholSource"
    )

    @model_validator(mode="after")
    def validate_origin(self) -> ReferenceRecord:
        if self.is_imported and not (self.country_of_origin or "").strip():
            raise ValueError("countryOfOrigin is required when isImported is true")
        if (
            self.beverage_type == "distilled_spirits"
            and self.abv_percent is None
            and self.reference_provenance != "label_ocr"
        ):
            raise ValueError("abvPercent is required for distilled spirits")
        if (
            self.beverage_type == "malt_beverage"
            and self.malt_alcohol_source == "added_ingredients"
            and self.abv_percent is None
        ):
            raise ValueError(
                "abvPercent is required for a malt beverage with added-ingredient alcohol"
            )
        return self


class Point(ContractModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class ConfidenceProvenance(ContractModel):
    source: str
    signal: float | None = None
    calibrated_probability: Literal[False] = Field(default=False, alias="calibratedProbability")


class Evidence(ContractModel):
    evidence_id: str = Field(pattern=r"^ev_[a-z0-9_-]+$", alias="evidenceId")
    panel_id: str = Field(pattern=r"^panel-[1-3]$", alias="panelId")
    polygon_original_pixels: list[Point] = Field(
        min_length=4, max_length=4, alias="polygonOriginalPixels"
    )
    source_view: Literal["original", "derived"] = Field(alias="sourceView")
    transform_id: str = Field(alias="transformId")
    text_snippet: str | None = Field(default=None, alias="textSnippet")
    confidence_provenance: ConfidenceProvenance = Field(alias="confidenceProvenance")


class Alternative(ContractModel):
    value: str
    evidence_ref: str = Field(alias="evidenceRef")


CheckGroup = Literal["identity", "content", "profile", "warning", "image"]


class WordingToken(ContractModel):
    """One statutory-token slot of the government warning diff (handoff REQ-11)."""

    expected: str | None = None
    observed: str | None = None
    status: Literal["match", "missing", "extra", "different"]


class QualitySummary(ContractModel):
    """Plain-language image quality for one panel (handoff REQ-9)."""

    grade: Literal["good", "poor", "unreadable"]
    issues: list[str] = Field(default_factory=list)


class BeverageInference(ContractModel):
    """Beverage type inference summary for the review header (handoff REQ-10)."""

    type: BeverageType | None = None
    confidence: Literal["high", "medium", "low"]
    reason: str
    conflicting: bool = False


class WarningEvidence(ContractModel):
    """Separate heading and body evidence for the warning crop (handoff REQ-12)."""

    heading_ref: str | None = Field(default=None, alias="headingRef")
    body_ref: str | None = Field(default=None, alias="bodyRef")


class CheckResult(ContractModel):
    check_id: str = Field(alias="checkId")
    label: str
    applicable: bool
    reference_display: str | None = Field(default=None, alias="referenceDisplay")
    observed_display: str | None = Field(default=None, alias="observedDisplay")
    state: CheckState
    reason_code: str = Field(alias="reasonCode")
    reason_text: str = Field(alias="reasonText")
    evidence_ref: str | None = Field(default=None, alias="evidenceRef")
    alternatives: list[Alternative] = Field(default_factory=list)
    capability: str
    policy_version: str = Field(alias="policyVersion")
    # Display-only presentation fields (handoff REQ-3, REQ-4, REQ-5, REQ-11).
    group: CheckGroup | None = None
    short_label: str | None = Field(default=None, alias="shortLabel")
    rule_expectation: str | None = Field(default=None, alias="ruleExpectation")
    reason_short: str | None = Field(default=None, max_length=40, alias="reasonShort")
    wording_diff: list[WordingToken] | None = Field(default=None, alias="wordingDiff")
    matched_words: int | None = Field(default=None, ge=0, alias="matchedWords")
    total_words: int | None = Field(default=None, ge=0, alias="totalWords")


class OriginalDimensions(ContractModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class PanelResult(ContractModel):
    panel_id: str = Field(pattern=r"^panel-[1-3]$", alias="panelId")
    original_dimensions: OriginalDimensions = Field(alias="originalDimensions")
    quality_signals: dict[str, float | bool | str] = Field(alias="qualitySignals")
    coverage_state: Literal["Sufficient", "Review", "Unreadable"] = Field(alias="coverageState")
    quality_summary: QualitySummary | None = Field(default=None, alias="qualitySummary")


class StageTimings(ContractModel):
    decode_ms: float = Field(ge=0, alias="decodeMs")
    preprocess_ms: float = Field(ge=0, alias="preprocessMs")
    ocr_ms: float = Field(ge=0, alias="ocrMs")
    candidates_ms: float = Field(ge=0, alias="candidatesMs")
    compare_ms: float = Field(ge=0, alias="compareMs")
    aggregate_ms: float = Field(ge=0, alias="aggregateMs")


class VerificationResult(ContractModel):
    request_id: str = Field(alias="requestId")
    build_id: str = Field(alias="buildId")
    profile_id: str = Field(alias="profileId")
    profile_version: str = Field(alias="profileVersion")
    model_identity: str = Field(alias="modelIdentity")
    rule_sources: list[str] = Field(alias="ruleSources")
    server_duration_ms: float = Field(ge=0, alias="serverDurationMs")
    stage_timings: StageTimings = Field(alias="stageTimings")
    panels: list[PanelResult]
    evidence: list[Evidence]
    checks: list[CheckResult]
    limitations: list[str]
    summary: SummaryState
    history_id: str | None = Field(default=None, alias="historyId")
    beverage_inference: BeverageInference | None = Field(default=None, alias="beverageInference")
    warning_evidence: WarningEvidence | None = Field(default=None, alias="warningEvidence")
    bad_image: bool = Field(default=False, alias="badImage")
    supersedes: str | None = None


class DetectedValue(ContractModel):
    value: str | float | bool | None = None
    status: CandidateStatus
    evidence_ref: str | None = Field(default=None, alias="evidenceRef")
    alternatives: list[str] = Field(default_factory=list)
    confidence_signal: float | None = Field(default=None, ge=0, le=1, alias="confidenceSignal")


class AnalysisDraft(ContractModel):
    beverage_type: BeverageType | None = Field(default=None, alias="beverageType")
    brand_name: str | None = Field(default=None, alias="brandName")
    class_type: str | None = Field(default=None, alias="classType")
    abv_percent: float | None = Field(default=None, ge=0, le=100, alias="abvPercent")
    proof: float | None = Field(default=None, ge=0)
    net_contents_value: float | None = Field(default=None, gt=0, alias="netContentsValue")
    net_contents_unit: VolumeUnit | None = Field(default=None, alias="netContentsUnit")
    producer_name_address: str | None = Field(default=None, alias="producerNameAddress")
    is_imported: bool = Field(default=False, alias="isImported")
    country_of_origin: str | None = Field(default=None, alias="countryOfOrigin")
    wine_appellation: str | None = Field(default=None, alias="wineAppellation")
    wine_sulfite_status: Literal["present", "not_present", "unknown"] = Field(
        default="unknown", alias="wineSulfiteStatus"
    )
    malt_alcohol_source: Literal["added_ingredients", "none", "unknown"] = Field(
        default="unknown", alias="maltAlcoholSource"
    )


class AnalysisResult(ContractModel):
    request_id: str = Field(alias="requestId")
    build_id: str = Field(alias="buildId")
    profile_id: Literal["all_beverages_demo_v2"] = Field(alias="profileId")
    model_identity: str = Field(alias="modelIdentity")
    server_duration_ms: float = Field(ge=0, alias="serverDurationMs")
    panels: list[PanelResult]
    evidence: list[Evidence]
    draft: AnalysisDraft
    detected: dict[str, DetectedValue]
    beverage_type_confidence: float | None = Field(
        default=None, ge=0, le=1, alias="beverageTypeConfidence"
    )
    beverage_type_reason: str = Field(alias="beverageTypeReason")
    beverage_inference: BeverageInference | None = Field(default=None, alias="beverageInference")
    limitations: list[str]
    verification: VerificationResult | None = None


class GroupingImage(ContractModel):
    """One analyzed image submitted for grouping (handoff REQ-14)."""

    image_id: str = Field(min_length=1, max_length=120, alias="imageId")
    file_name: str = Field(min_length=1, max_length=260, alias="fileName")
    path: str | None = Field(default=None, max_length=1024)
    brand_name: str | None = Field(default=None, max_length=160, alias="brandName")
    class_type: str | None = Field(default=None, max_length=240, alias="classType")
    beverage_type: BeverageType | None = Field(default=None, alias="beverageType")
    type_confidence: Literal["high", "medium", "low"] | None = Field(
        default=None, alias="typeConfidence"
    )
    failed: bool = False


class GroupingRequest(ContractModel):
    images: list[GroupingImage] = Field(min_length=1, max_length=900)


class GroupSuggestion(ContractModel):
    group_id: str = Field(alias="groupId")
    panel_ids: list[str] = Field(min_length=1, max_length=3, alias="panelIds")
    suggested_name: str = Field(alias="suggestedName")
    inferred_type: BeverageType | None = Field(default=None, alias="inferredType")
    confidence: Literal["high", "medium", "low"]
    status: Literal["ready_to_confirm", "needs_review"]
    reasons: list[str]
    conflict: bool = False


class GroupingResult(ContractModel):
    groups: list[GroupSuggestion]
    analyzed: int = Field(ge=0)
    failed: int = Field(ge=0)


class PublicError(ContractModel):
    request_id: str = Field(alias="requestId")
    code: str
    message: str
    field_or_panel: str | None = Field(default=None, alias="fieldOrPanel")
    retryable: bool
    next_action: str = Field(alias="nextAction")


class OcrLine(ContractModel):
    panel_id: str = Field(alias="panelId")
    text: str
    polygon: list[Point] = Field(min_length=4, max_length=4)
    confidence: float | None = Field(default=None, ge=0, le=1)
    reading_order: int = Field(ge=0, alias="readingOrder")
    source_view: Literal["original", "derived"] = Field(alias="sourceView")
    transform_id: str = Field(alias="transformId")
    ink_density: float | None = Field(default=None, ge=0, le=1, alias="inkDensity")
    local_contrast: float | None = Field(default=None, ge=0, le=1, alias="localContrast")


class Candidate(ContractModel):
    value: str
    evidence: Evidence


class CandidateSet(ContractModel):
    status: CandidateStatus
    candidates: list[Candidate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_count(self) -> CandidateSet:
        if self.status == "Found" and len(self.candidates) != 1:
            raise ValueError("Found requires exactly one candidate")
        if self.status == "Ambiguous" and len(self.candidates) < 2:
            raise ValueError("Ambiguous requires at least two candidates")
        if self.status in {"Not found", "Unreadable"} and self.candidates:
            raise ValueError("Absent candidates cannot contain evidence")
        return self
