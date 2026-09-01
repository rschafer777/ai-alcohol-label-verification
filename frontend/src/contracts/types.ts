export {
  browserErrorCodes,
  checkIds,
  contractVersion,
  limits,
  profileId,
  serverErrorCodes,
} from "../api/generated-contract";

export type {
  BrowserErrorCode,
  CheckAlternative,
  CheckId,
  CheckResult,
  CheckState,
  ConfidenceProvenance,
  ErrorCode,
  Evidence,
  PanelResult,
  Point,
  PublicError,
  ReferenceRecord,
  ServerErrorCode,
  VerificationResult,
  VerificationSummary,
} from "../api/generated-contract";

import type { ReferenceRecord, VerificationResult } from "../api/generated-contract";

export interface VerificationRequest {
  reference: ReferenceRecord;
  panels: File[];
  signal: AbortSignal;
}

export interface VerificationClient {
  verify(request: VerificationRequest): Promise<VerificationResult>;
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
