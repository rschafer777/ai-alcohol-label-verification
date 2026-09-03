import type { CheckState, VerificationSummary } from "../contracts/types";

/* Shared status vocabulary helpers: every state is a color + an icon + a word, never color alone.
   Green = passes / approved, amber = questionable / needs a human, red = rejected / defect,
   grey = not verified or not applicable, steel accent = in progress. */

export type SemanticKind = "pass" | "warn" | "fail" | "info" | "neutral";
export type Disposition = "approved" | "rejected" | "more_info_requested" | null;
export type MachineSummary = VerificationSummary | "Bad image" | "Running" | "Queued" | "Failed" | "Cancelled";

export const evidenceColors = {
  pass: "var(--lv-pass)",
  warn: "var(--lv-warn)",
  fail: "var(--lv-fail)",
  none: "var(--lv-none)",
  passText: "var(--lv-pass-text)",
  warnText: "var(--lv-warn-text)",
  failText: "var(--lv-fail-text)",
} as const;

export function stateKind(state: CheckState, applicable = true): SemanticKind {
  if (!applicable) return "neutral";
  if (state === "Match") return "pass";
  if (state === "Mismatch") return "fail";
  if (state === "Review") return "warn";
  return "neutral";
}

export function stateColor(state: CheckState, applicable = true): string {
  if (!applicable) return "transparent";
  if (state === "Match") return evidenceColors.pass;
  if (state === "Review") return evidenceColors.warn;
  if (state === "Mismatch") return evidenceColors.fail;
  return evidenceColors.none;
}

export function summaryLabel(summary: MachineSummary): string {
  if (summary === "No differences found in checked fields") return "No differences found";
  return summary;
}

export function summaryKind(summary: MachineSummary): SemanticKind {
  if (summary === "No differences found in checked fields") return "pass";
  if (summary === "Differences detected" || summary === "Failed") return "fail";
  if (summary === "Running") return "info";
  if (summary === "Queued" || summary === "Cancelled") return "neutral";
  return "warn";
}

export function summaryColor(summary: MachineSummary | null | undefined): string {
  if (!summary) return "transparent";
  const kind = summaryKind(summary);
  if (kind === "pass") return evidenceColors.pass;
  if (kind === "fail") return evidenceColors.fail;
  if (kind === "warn") return evidenceColors.warn;
  return "transparent";
}

export function dispositionLabel(value: Disposition): string {
  if (value === "approved") return "Approved";
  if (value === "rejected") return "Rejected";
  if (value === "more_info_requested") return "More info requested";
  return "Undecided";
}
