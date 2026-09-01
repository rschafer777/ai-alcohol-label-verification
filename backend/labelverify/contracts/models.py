from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
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
    profile_id: Literal["distilled_spirits_demo_v1"] = Field(alias="profileId")
    case_label: str | None = Field(default=None, max_length=80, alias="caseLabel")
    brand_name: NonBlank = Field(max_length=160, alias="brandName")
    class_type: NonBlank = Field(max_length=240, alias="classType")
    abv_percent: Decimal = Field(gt=0, le=100, alias="abvPercent")
    proof: Decimal | None = Field(default=None, ge=0)
    net_contents_value: Decimal = Field(gt=0, alias="netContentsValue")
    net_contents_unit: Literal["mL", "L"] = Field(alias="netContentsUnit")
    producer_name_address: NonBlank = Field(max_length=500, alias="producerNameAddress")
    is_imported: bool = Field(alias="isImported")
    country_of_origin: str | None = Field(default=None, max_length=80, alias="countryOfOrigin")

    @model_validator(mode="after")
    def validate_origin(self) -> ReferenceRecord:
        if self.is_imported and not (self.country_of_origin or "").strip():
            raise ValueError("countryOfOrigin is required when isImported is true")
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
    panel_id: str = Field(pattern=r"^panel-[1-6]$", alias="panelId")
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


class OriginalDimensions(ContractModel):
    width: int = Field(gt=0)
    height: int = Field(gt=0)


class PanelResult(ContractModel):
    panel_id: str = Field(pattern=r"^panel-[1-6]$", alias="panelId")
    original_dimensions: OriginalDimensions = Field(alias="originalDimensions")
    quality_signals: dict[str, float | bool | str] = Field(alias="qualitySignals")
    coverage_state: Literal["Sufficient", "Review", "Unreadable"] = Field(alias="coverageState")


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
