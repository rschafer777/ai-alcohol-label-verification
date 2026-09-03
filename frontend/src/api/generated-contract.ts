// Generated CG-004 contract surface. Do not hand-edit in feature work.

export const contractVersion = "2.0.0" as const;
export const profileId = "all_beverages_demo_v2" as const;

export const limits = {
  rawRequestBytes: 13_631_488,
  referenceBytes: 32_768,
  fileBytes: 4_194_304,
  aggregateFileBytes: 12_582_912,
  panelCountMin: 1,
  panelCountMax: 3,
  pixelsPerImage: 12_000_000,
  pixelsPerRequest: 36_000_000,
  uploadDeadlineSeconds: 20,
  serverDeadlineSeconds: 30,
  browserDeadlineSeconds: 35,
  workerDeadlineSeconds: 9.0
} as const;

export const checkIds = [
  "beverage_type",
  "brand",
  "class_type",
  "abv",
  "proof",
  "net_contents",
  "producer",
  "country",
  "wine_appellation",
  "wine_sulfites",
  "spirits_field_of_vision",
  "malt_class_designation",
  "warning_applicability",
  "warning_wording",
  "warning_heading_uppercase",
  "warning_heading_emphasis",
  "warning_body_not_bold",
  "warning_separation",
  "warning_continuity",
  "warning_contrast",
  "warning_legibility",
  "warning_physical_size",
  "panel_coverage",
  "image_quality"
] as const;

export const serverErrorCodes = [
  "invalid_host",
  "invalid_client_identity",
  "invalid_content_length",
  "content_length_mismatch",
  "invalid_multipart",
  "origin_not_allowed",
  "upload_timeout",
  "request_too_large",
  "multipart_limit_exceeded",
  "unsupported_media_type",
  "invalid_reference",
  "invalid_panel_count",
  "invalid_image",
  "decoded_pixel_limit",
  "client_rate_limited",
  "global_start_rate_limited",
  "verification_capacity_busy",
  "worker_queue_busy",
  "not_ready",
  "inference_failed",
  "internal_error",
  "inference_timeout",
  "request_deadline_exceeded"
] as const;

export const browserErrorCodes = [
  "verification_cancelled",
  "client_deadline_exceeded",
  "response_contract_invalid",
  "network_unavailable"
] as const;

export type CheckId = (typeof checkIds)[number];
export type ServerErrorCode = (typeof serverErrorCodes)[number];
export type BrowserErrorCode = (typeof browserErrorCodes)[number];
export type ErrorCode = ServerErrorCode | BrowserErrorCode;
export type CheckState = "Match" | "Mismatch" | "Review" | "Not verified";
export type VerificationSummary =
  | "No differences found in checked fields"
  | "Review needed"
  | "Differences detected";

export interface ReferenceRecord {
  profileId: typeof profileId;
  beverageType: "malt_beverage" | "wine" | "distilled_spirits";
  referenceProvenance: "label_ocr" | "manual" | "manifest" | "sample";
  caseLabel?: string | null;
  brandName: string;
  classType: string;
  abvPercent: number | null;
  proof?: number | null;
  netContentsValue: number;
  netContentsUnit: "mL" | "L" | "fl oz" | "pt" | "qt" | "gal";
  producerNameAddress: string;
  isImported: boolean;
  countryOfOrigin?: string | null;
  wineAppellation?: string | null;
  wineSulfiteStatus: "present" | "not_present" | "unknown";
  maltAlcoholSource: "added_ingredients" | "none" | "unknown";
}

export interface DetectedValue {
  value: string | number | boolean | null;
  status: "Found" | "Ambiguous" | "Not found" | "Unreadable";
  evidenceRef?: string | null;
  alternatives: string[];
  confidenceSignal?: number | null;
}

export interface AnalysisDraft {
  beverageType: ReferenceRecord["beverageType"] | null;
  brandName: string | null;
  classType: string | null;
  abvPercent: number | null;
  proof: number | null;
  netContentsValue: number | null;
  netContentsUnit: ReferenceRecord["netContentsUnit"] | null;
  producerNameAddress: string | null;
  isImported: boolean;
  countryOfOrigin: string | null;
  wineAppellation: string | null;
  wineSulfiteStatus: ReferenceRecord["wineSulfiteStatus"];
  maltAlcoholSource: ReferenceRecord["maltAlcoholSource"];
}

export type CheckGroup = "identity" | "content" | "profile" | "warning" | "image";

export interface WordingToken {
  expected?: string | null;
  observed?: string | null;
  status: "match" | "missing" | "extra" | "different";
}

export interface QualitySummary {
  grade: "good" | "poor" | "unreadable";
  issues: string[];
}

export interface BeverageInference {
  type?: ReferenceRecord["beverageType"] | null;
  confidence: "high" | "medium" | "low";
  reason: string;
  conflicting: boolean;
}

export interface WarningEvidence {
  headingRef?: string | null;
  bodyRef?: string | null;
}

export interface AnalysisResult {
  requestId: string;
  buildId: string;
  profileId: typeof profileId;
  modelIdentity: string;
  serverDurationMs: number;
  panels: PanelResult[];
  evidence: Evidence[];
  draft: AnalysisDraft;
  detected: Record<string, DetectedValue>;
  beverageTypeConfidence: number | null;
  beverageTypeReason: string;
  beverageInference?: BeverageInference | null;
  limitations: string[];
  verification: VerificationResult | null;
}

export interface Point {
  x: number;
  y: number;
}

export interface ConfidenceProvenance {
  source: string;
  signal: number | null;
  calibratedProbability: false;
}

export interface Evidence {
  evidenceId: string;
  panelId: string;
  polygonOriginalPixels: [Point, Point, Point, Point];
  sourceView: "original" | "derived";
  transformId: string;
  textSnippet?: string | null;
  confidenceProvenance: ConfidenceProvenance;
}

export interface PanelResult {
  panelId: string;
  originalDimensions: { width: number; height: number };
  qualitySignals: Record<string, number | boolean | string | null>;
  coverageState: string;
  qualitySummary?: QualitySummary | null;
}

export interface CheckAlternative {
  value: string;
  evidenceRef: string;
}

export interface CheckResult {
  checkId: CheckId;
  label: string;
  applicable: boolean;
  referenceDisplay?: string | null;
  observedDisplay?: string | null;
  state: CheckState;
  reasonCode: string;
  reasonText: string;
  evidenceRef?: string | null;
  alternatives: CheckAlternative[];
  capability: string;
  policyVersion: string;
  group?: CheckGroup | null;
  shortLabel?: string | null;
  ruleExpectation?: string | null;
  reasonShort?: string | null;
  wordingDiff?: WordingToken[] | null;
  matchedWords?: number | null;
  totalWords?: number | null;
}

export interface VerificationResult {
  requestId: string;
  buildId: string;
  profileId: typeof profileId;
  profileVersion: string;
  modelIdentity: string;
  ruleSources: string[];
  serverDurationMs: number;
  stageTimings: Record<string, number>;
  panels: PanelResult[];
  evidence: Evidence[];
  checks: CheckResult[];
  limitations: string[];
  summary: VerificationSummary;
  historyId?: string | null;
  beverageInference?: BeverageInference | null;
  warningEvidence?: WarningEvidence | null;
  badImage?: boolean;
  supersedes?: string | null;
}

export interface GroupingImage {
  imageId: string;
  fileName: string;
  path?: string | null;
  brandName?: string | null;
  classType?: string | null;
  beverageType?: ReferenceRecord["beverageType"] | null;
  typeConfidence?: "high" | "medium" | "low" | null;
  failed?: boolean;
}

export interface GroupSuggestion {
  groupId: string;
  panelIds: string[];
  suggestedName: string;
  inferredType?: ReferenceRecord["beverageType"] | null;
  confidence: "high" | "medium" | "low";
  status: "ready_to_confirm" | "needs_review";
  reasons: string[];
  conflict: boolean;
}

export interface GroupingResult {
  groups: GroupSuggestion[];
  analyzed: number;
  failed: number;
}

export interface PublicError {
  requestId: string;
  code: ErrorCode | string;
  message: string;
  fieldOrPanel?: string | null;
  retryable: boolean;
  nextAction: string;
}
