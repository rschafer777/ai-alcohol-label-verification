from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonBlank = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
BeverageType = Literal["malt_beverage", "wine", "distilled_spirits"]
VolumeUnit = Literal["mL", "L", "fl oz", "pt", "qt", "gal"]
CheckState = Literal["Match", "Mismatch", "Review", "Not verified"]
FieldSource = Literal[
    "label_ocr",
    "reviewer_corrected",
    "trusted_application",
    "manifest",
    "sample",
]
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
    field_provenance: dict[str, FieldSource] = Field(default_factory=dict, alias="fieldProvenance")
    case_label: str | None = Field(default=None, max_length=80, alias="caseLabel")
    brand_name: NonBlank = Field(max_length=160, alias="brandName")
    class_type: NonBlank = Field(max_length=240, alias="classType")
    abv_percent: Decimal | None = Field(default=None, ge=0, le=100, alias="abvPercent")
    proof: Decimal | None = Field(default=None, ge=0)
    net_contents_value: Decimal = Field(gt=0, alias="netContentsValue")
    net_contents_unit: VolumeUnit = Field(alias="netContentsUnit")
    producer_name_address: NonBlank = Field(max_length=1000, alias="producerNameAddress")
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

    def source_for(self, field_name: str) -> FieldSource:
        explicit = self.field_provenance.get(field_name)
        if explicit is not None:
            return explicit
        if self.reference_provenance == "manual":
            return "trusted_application"
        return self.reference_provenance


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
    observation_provenance: FieldSource | None = Field(default=None, alias="observationProvenance")


class ReviewCause(ContractModel):
    check_id: str = Field(alias="checkId")
    category: Literal[
        "missing_evidence",
        "ocr_uncertainty",
        "presentation_uncertainty",
        "trusted_context_missing",
        "conflicting_evidence",
        "policy_review",
    ]
    reason_code: str = Field(alias="reasonCode")
    evidence_ref: str | None = Field(default=None, alias="evidenceRef")


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
    blocking_check_ids: list[str] = Field(default_factory=list, alias="blockingCheckIds")
    review_causes: list[ReviewCause] = Field(default_factory=list, alias="reviewCauses")
    root_id: str | None = Field(default=None, alias="rootId")
    parent_id: str | None = Field(default=None, alias="parentId")
    revision: int = Field(default=1, ge=1)
    revision_kind: Literal["original", "correction", "panel_added"] = Field(
        default="original", alias="revisionKind"
    )
    # The faithful extraction snapshot is persisted for zero-OCR corrections but is never
    # exposed by the public API.
    observation_snapshot: dict[str, object] | None = Field(
        default=None, exclude=True, alias="observationSnapshot"
    )


CorrectionField = Literal[
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
]


class CorrectionLocator(ContractModel):
    evidence_ref: str | None = Field(default=None, pattern=r"^ev_[a-z0-9_-]+$", alias="evidenceRef")
    panel_id: str | None = Field(default=None, pattern=r"^panel-[1-3]$", alias="panelId")
    polygon: list[Point] | None = Field(default=None, min_length=4, max_length=4)

    @model_validator(mode="after")
    def validate_locator(self) -> CorrectionLocator:
        has_evidence = self.evidence_ref is not None
        has_polygon = self.panel_id is not None and self.polygon is not None
        has_partial_polygon = (self.panel_id is None) != (self.polygon is None)
        if has_partial_polygon or has_evidence == has_polygon:
            raise ValueError("Provide either evidenceRef or both panelId and a four-point polygon")
        return self


class BeverageTypeCorrection(CorrectionLocator):
    field: Literal["beverage_type"]
    family: BeverageType


class TextCorrection(CorrectionLocator):
    field: Literal[
        "brand_name",
        "class_type",
        "alcohol_content",
        "proof",
        "net_contents",
        "country_of_origin",
        "wine_appellation",
        "wine_sulfite_declaration",
    ]
    visible_text: NonBlank = Field(max_length=500, alias="visibleText")


class ProducerCorrection(CorrectionLocator):
    field: Literal["producer_name_address"]
    visible_text: NonBlank = Field(max_length=1000, alias="visibleText")

    @model_validator(mode="after")
    def validate_lines(self) -> ProducerCorrection:
        if len(self.visible_text.splitlines()) > 5:
            raise ValueError("Producer correction may contain at most five lines")
        return self


CorrectionItem = Annotated[
    BeverageTypeCorrection | TextCorrection | ProducerCorrection,
    Field(discriminator="field"),
]


class CorrectionRequest(ContractModel):
    expected_revision: int = Field(ge=1, alias="expectedRevision")
    reason: NonBlank = Field(max_length=500)
    actor_label: str | None = Field(default=None, max_length=80, alias="actorLabel")
    corrections: list[CorrectionItem] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def validate_unique_fields(self) -> CorrectionRequest:
        fields = [item.field for item in self.corrections]
        if len(fields) != len(set(fields)):
            raise ValueError("Each corrected field may appear only once")
        return self


class CorrectionResponse(ContractModel):
    history_id: str = Field(alias="historyId")
    root_id: str = Field(alias="rootId")
    parent_id: str = Field(alias="parentId")
    revision: int = Field(ge=2)
    result: VerificationResult


class DetectedValue(ContractModel):
    value: str | float | bool | None = None
    status: CandidateStatus
    evidence_ref: str | None = Field(default=None, alias="evidenceRef")
    alternatives: list[str] = Field(default_factory=list)
    confidence_signal: float | None = Field(default=None, ge=0, le=1, alias="confidenceSignal")


class AnalysisDraft(ContractModel):
    reference_provenance: Literal["label_ocr", "manual", "manifest", "sample"] = Field(
        default="label_ocr", alias="referenceProvenance"
    )
    field_provenance: dict[str, FieldSource] = Field(default_factory=dict, alias="fieldProvenance")
    case_label: str | None = Field(default=None, max_length=80, alias="caseLabel")
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


class ErrorComparison(ContractModel):
    label: str
    expected: str
    actual: str
    passed: bool


class PublicError(ContractModel):
    request_id: str = Field(alias="requestId")
    code: str
    message: str
    field_or_panel: str | None = Field(default=None, alias="fieldOrPanel")
    retryable: bool
    next_action: str = Field(alias="nextAction")
    comparisons: list[ErrorComparison] = Field(default_factory=list)


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
    # Typography signals measured on the OCR view that produced the line. Stroke width and
    # ink height are in view pixels so their ratio is scale-free; the contrast ratio follows
    # the WCAG 2.x relative-luminance definition (1.0 = no contrast, 21.0 = black on white).
    stroke_px: float | None = Field(default=None, ge=0, alias="strokePx")
    ink_height_px: float | None = Field(default=None, ge=0, alias="inkHeightPx")
    contrast_ratio: float | None = Field(default=None, ge=1, le=21, alias="contrastRatio")


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
