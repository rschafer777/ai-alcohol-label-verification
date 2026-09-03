import type { BeverageType, CheckGroup, CheckId, CheckResult, Evidence, PanelResult, VerificationResult } from "../../contracts/types";

/* Display helpers for the 24-check result. Everything here renders contract values; nothing
   recomputes a state. Presentation fields (group, ruleExpectation, reasonShort, shortLabel)
   come from the API; the fallbacks below only cover records stored before those fields existed. */

export const GROUP_ORDER: Array<{ id: CheckGroup; title: string }> = [
  { id: "identity", title: "Identity" },
  { id: "content", title: "Content statements" },
  { id: "profile", title: "Type-specific rules" },
  { id: "warning", title: "Government warning" },
  { id: "image", title: "Image & coverage" },
];

const LEGACY_GROUPS: Record<CheckId, CheckGroup> = {
  beverage_type: "identity", brand: "identity", class_type: "identity",
  abv: "content", proof: "content", net_contents: "content", producer: "content", country: "content",
  wine_appellation: "profile", wine_sulfites: "profile", spirits_field_of_vision: "profile", malt_class_designation: "profile",
  warning_applicability: "warning", warning_wording: "warning", warning_heading_uppercase: "warning", warning_heading_emphasis: "warning",
  warning_body_not_bold: "warning", warning_separation: "warning", warning_continuity: "warning", warning_contrast: "warning",
  warning_legibility: "warning", warning_physical_size: "warning", panel_coverage: "image", image_quality: "image",
};

const LEGACY_SHORT: Record<CheckId, string> = {
  beverage_type: "Type", brand: "Brand", class_type: "Class", abv: "Alcohol", proof: "Proof", net_contents: "Contents", producer: "Bottler", country: "Origin",
  wine_appellation: "Appellation", wine_sulfites: "Sulfites", spirits_field_of_vision: "Field of vision", malt_class_designation: "Malt class",
  warning_applicability: "Required", warning_wording: "Wording", warning_heading_uppercase: "Caps", warning_heading_emphasis: "Bold", warning_body_not_bold: "Body weight",
  warning_separation: "Separate", warning_continuity: "Continuous", warning_contrast: "Contrast", warning_legibility: "Legible", warning_physical_size: "Size",
  panel_coverage: "Coverage", image_quality: "Quality",
};

export const WARNING_IDS: ReadonlySet<string> = new Set(Object.entries(LEGACY_GROUPS).filter(([, group]) => group === "warning").map(([id]) => id));
export const EDITABLE_IDS: ReadonlySet<string> = new Set(["beverage_type", "brand", "class_type", "abv", "proof", "net_contents", "producer", "country", "wine_appellation"]);

export function checkGroup(check: CheckResult): CheckGroup {
  return check.group ?? LEGACY_GROUPS[check.checkId];
}

export function shortLabel(check: CheckResult): string {
  return check.shortLabel ?? LEGACY_SHORT[check.checkId];
}

/** Friendly check title used in tables and cards (the contract label minus the "Warning " prefix). */
export function displayLabel(check: CheckResult): string {
  const label = check.label;
  if (check.checkId.startsWith("warning_") && label.startsWith("Warning ")) {
    const rest = label.slice("Warning ".length);
    return rest.charAt(0).toUpperCase() + rest.slice(1);
  }
  return label;
}

export function ruleExpectation(check: CheckResult): string {
  return check.ruleExpectation ?? check.referenceDisplay ?? "Selected rule profile";
}

export function observedDisplay(check: CheckResult, result?: VerificationResult): string {
  if (!check.applicable) return "-";
  if (check.checkId === "beverage_type" && check.observedDisplay) {
    const value = check.observedDisplay;
    return value === "malt_beverage" || value === "wine" || value === "distilled_spirits" ? beverageTypeLabel(value) : value;
  }
  if (check.observedDisplay) return check.observedDisplay;
  if (result && check.checkId === "panel_coverage") return `${result.panels.length} image${result.panels.length === 1 ? "" : "s"} submitted`;
  if (result && check.checkId === "image_quality") return result.panels.map((panel) => qualityText(panel)).join(" · ");
  if (check.state === "Match") return "Supported by the label read";
  return "Not read on the label";
}

export function reasonShort(check: CheckResult): string {
  if (check.reasonShort) return check.reasonShort;
  const text = check.reasonText;
  return text.length <= 40 ? text : `${text.slice(0, 39).trimEnd()}…`;
}

export function provenanceLabel(check: CheckResult): string {
  if (check.reasonCode === "label_value_readable") return "Label-derived: not compared with a COLA record";
  if (check.capability === "human_confirmation") return "Needs human confirmation";
  if (check.capability === "visual_heuristic") return "Visual heuristic";
  return "OCR: original pixels";
}

export interface Tally {
  match: number;
  review: number;
  mismatch: number;
  notVerified: number;
  notApplicable: number;
}

export function tally(checks: CheckResult[]): Tally {
  const result: Tally = { match: 0, review: 0, mismatch: 0, notVerified: 0, notApplicable: 0 };
  for (const check of checks) {
    if (!check.applicable) result.notApplicable += 1;
    else if (check.state === "Match") result.match += 1;
    else if (check.state === "Review") result.review += 1;
    else if (check.state === "Mismatch") result.mismatch += 1;
    else result.notVerified += 1;
  }
  return result;
}

export function tallyText(value: Tally): string {
  return [
    value.match && `${value.match} match`,
    value.review && `${value.review} review`,
    value.mismatch && `${value.mismatch} mismatch`,
    value.notVerified && `${value.notVerified} not verified`,
    value.notApplicable && `${value.notApplicable} not applicable`,
  ].filter(Boolean).join(" · ");
}

export function beverageTypeLabel(value: BeverageType | "unresolved" | null | undefined, short = false): string {
  if (value === "malt_beverage") return "Beer / malt";
  if (value === "distilled_spirits") return short ? "Spirits" : "Distilled spirits";
  if (value === "wine") return "Wine";
  return "Type unresolved";
}

export function profileLabel(value: BeverageType | null | undefined): string {
  if (value === "malt_beverage") return "malt beverage profile";
  if (value === "distilled_spirits") return "distilled spirits profile";
  if (value === "wine") return "wine profile";
  return "type unresolved";
}

export function typeTagText(result: VerificationResult, fallbackType: BeverageType | null | undefined, imported: boolean): string {
  const inference = result.beverageInference;
  const type = inference?.type ?? fallbackType ?? null;
  const parts = [beverageTypeLabel(type)];
  if (inference) parts.push(`inferred, ${inference.confidence} confidence`);
  else parts.push("inferred");
  if (imported) parts.push("imported");
  return parts.join(" · ");
}

export function needsTypeConfirmation(result: VerificationResult): boolean {
  const inference = result.beverageInference;
  if (!inference) return false;
  return inference.confidence === "low" || inference.conflicting || inference.type == null;
}

export function qualityText(panel: PanelResult | undefined): string {
  const summary = panel?.qualitySummary;
  if (!summary) return panel ? panel.coverageState : "Unknown";
  const grade = summary.grade === "good" ? "Good" : summary.grade === "poor" ? "Poor" : "Unreadable";
  return summary.issues.length ? `${grade}: ${summary.issues.join(", ")}` : grade;
}

export function coverageText(result: VerificationResult): string {
  const coverage = result.checks.find((check) => check.checkId === "panel_coverage");
  return coverage?.observedDisplay ?? `${result.panels.length} image${result.panels.length === 1 ? "" : "s"} submitted`;
}

export function polygonPoints(evidence: Evidence): string {
  return evidence.polygonOriginalPixels.map((point) => `${point.x},${point.y}`).join(" ");
}

export function evidenceFor(result: VerificationResult, check: CheckResult | null | undefined): Evidence | null {
  if (!check?.evidenceRef) return null;
  return result.evidence.find((item) => item.evidenceId === check.evidenceRef) ?? null;
}

export function panelIndexOf(result: VerificationResult, panelId: string): number {
  const index = result.panels.findIndex((panel) => panel.panelId === panelId);
  return index < 0 ? 0 : index;
}

export function worstWarningState(checks: CheckResult[]): "Mismatch" | "Review" | "Match" {
  const rows = checks.filter((check) => WARNING_IDS.has(check.checkId) && check.applicable);
  if (rows.some((check) => check.state === "Mismatch")) return "Mismatch";
  if (rows.some((check) => check.state === "Review")) return "Review";
  return "Match";
}

/** The first check in a result that is not a Match, used for "Why" columns. */
export function firstException(result: VerificationResult): CheckResult | null {
  return result.checks.find((check) => check.applicable && check.state === "Mismatch")
    ?? result.checks.find((check) => check.applicable && check.state === "Review")
    ?? null;
}
