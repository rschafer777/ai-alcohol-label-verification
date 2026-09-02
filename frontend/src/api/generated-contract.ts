// Generated CG-004 contract surface. Do not hand-edit in feature work.

export const contractVersion = "1.0.0" as const;
export const profileId = "distilled_spirits_demo_v1" as const;

export const limits = {
  rawRequestBytes: 8_650_752,
  referenceBytes: 32_768,
  fileBytes: 4_194_304,
  aggregateFileBytes: 8_388_608,
  panelCountMin: 1,
  panelCountMax: 6,
  pixelsPerImage: 12_000_000,
  pixelsPerRequest: 36_000_000,
  uploadDeadlineSeconds: 20,
  serverDeadlineSeconds: 30,
  browserDeadlineSeconds: 35,
  workerDeadlineSeconds: 9.0
} as const;

export const checkIds = [
  "brand",
  "class_type",
  "abv",
  "proof",
  "net_contents",
  "producer",
  "country",
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
  caseLabel?: string | null;
  brandName: string;
  classType: string;
  abvPercent: number;
  proof?: number | null;
  netContentsValue: number;
  netContentsUnit: "mL" | "L";
  producerNameAddress: string;
  isImported: boolean;
  countryOfOrigin?: string | null;
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
}

export interface PublicError {
  requestId: string;
  code: ErrorCode | string;
  message: string;
  fieldOrPanel?: string | null;
  retryable: boolean;
  nextAction: string;
}
