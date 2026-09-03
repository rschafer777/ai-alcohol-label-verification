import type { CheckResult, Evidence, VerificationResult } from "../../contracts/types";
import { evidenceFor } from "./check-view";

export const STATUTORY_HEADING = "GOVERNMENT WARNING:";
export const STATUTORY_BODY = "(1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.";

export const CROP_W = 600;
export const CROP_H = 420;

export function byId(checks: CheckResult[], id: string): CheckResult | undefined {
  return checks.find((check) => check.checkId === id);
}

function findEvidence(result: VerificationResult, ref: string | null | undefined): Evidence | null {
  if (!ref) return null;
  return result.evidence.find((item) => item.evidenceId === ref) ?? null;
}

export function warningEvidencePair(result: VerificationResult): { heading: Evidence | null; body: Evidence | null } {
  const heading = findEvidence(result, result.warningEvidence?.headingRef) ?? evidenceFor(result, byId(result.checks, "warning_heading_uppercase"));
  const body = findEvidence(result, result.warningEvidence?.bodyRef) ?? evidenceFor(result, byId(result.checks, "warning_wording"));
  return { heading, body };
}
