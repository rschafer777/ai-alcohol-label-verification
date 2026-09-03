export {
  browserErrorCodes,
  checkIds,
  contractVersion,
  groupingLimits,
  limits,
  profileId,
  serverErrorCodes,
} from "../api/generated-contract";

export type {
  BrowserErrorCode,
  AnalysisDraft,
  AnalysisResult,
  BeverageInference,
  CheckAlternative,
  CheckGroup,
  CheckId,
  CheckResult,
  CheckState,
  ConfidenceProvenance,
  ErrorCode,
  ErrorComparison,
  Evidence,
  GroupingImage,
  GroupingResult,
  GroupSuggestion,
  PanelResult,
  Point,
  PublicError,
  QualitySummary,
  ReferenceRecord,
  ServerErrorCode,
  VerificationResult,
  VerificationSummary,
  WarningEvidence,
  WordingToken,
} from "../api/generated-contract";

import type { AnalysisResult, GroupingImage, GroupingResult, ReferenceRecord, VerificationResult, VerificationSummary } from "../api/generated-contract";

export type BeverageType = ReferenceRecord["beverageType"];

/** Upload progress for the processing stepper and the image-slot progress bar. */
export interface UploadProgress {
  loaded: number;
  total: number;
}

export interface AnalysisRequest {
  panels: File[];
  signal: AbortSignal;
  onUploadProgress?: (progress: UploadProgress) => void;
  /** false = read only, do not store a History record (batch grouping pass). */
  persist?: boolean;
}

export interface AddPanelRequest {
  historyId: string;
  panel: File;
  signal: AbortSignal;
  onUploadProgress?: (progress: UploadProgress) => void;
}

export interface VerificationRequest {
  reference: ReferenceRecord;
  panels: File[];
  signal: AbortSignal;
}

export interface GroupingRequest {
  images: GroupingImage[];
  signal?: AbortSignal;
}

export interface VerificationClient {
  analyze(request: AnalysisRequest): Promise<AnalysisResult>;
  verify(request: VerificationRequest): Promise<VerificationResult>;
  addPanel?(request: AddPanelRequest): Promise<AnalysisResult>;
  suggestGroups?(request: GroupingRequest): Promise<GroupingResult>;
}

export interface SamplePanelAsset {
  panelId: string;
  label: string;
  fileName: string;
  mimeType: "image/jpeg" | "image/png" | "image/webp";
  url: string;
}

export interface SamplePackage {
  reference: ReferenceRecord;
  panels: SamplePanelAsset[];
}

export interface LoadedSample {
  reference: ReferenceRecord;
  panels: File[];
}

export interface SampleAdapter {
  load(signal?: AbortSignal): Promise<LoadedSample>;
}

/** History records as returned by GET /api/v1/history and GET /api/v1/history/{id}. */
export interface HistoryPanel {
  panelId: string;
  fileName: string;
  imageUrl: string;
}

export interface HistorySummary {
  id: string;
  createdAt: string;
  requestId: string;
  displayName: string;
  beverageType: BeverageType | "unresolved";
  summary: VerificationSummary;
  disposition: string | null;
  reviewerNote: string;
  panelCount: number;
  panels: HistoryPanel[];
}

export interface HistoryDetail extends HistorySummary {
  reference: unknown;
  result: VerificationResult;
}

export interface HistoryPage {
  items: HistorySummary[];
  total: number;
  cap: number;
  offset: number;
  pageSize: number;
  hasMore: boolean;
}

export interface MetaResponse {
  buildId: string;
  limits: { browserDeadlineSeconds: number; fileBytes: number; panelCountMax: number };
  history: { cap: number; retainsImages: boolean };
}
