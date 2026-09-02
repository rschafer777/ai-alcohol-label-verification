import { checkIds, profileId, type AnalysisResult, type CheckResult, type VerificationResult } from "../src/api/generated-contract";

export const checks: CheckResult[] = checkIds.map((checkId, index) => ({
  checkId,
  label: checkId.replaceAll("_", " "),
  applicable: true,
  referenceDisplay: "Required value",
  observedDisplay: "Observed value",
  state: index === 13 ? "Review" : "Match",
  reasonCode: index === 13 ? "review" : "match",
  reasonText: index === 13 ? "Human review is needed." : "The selected requirement is supported.",
  evidenceRef: index < 2 ? `ev_${checkId}_panel-1_00` : null,
  alternatives: [],
  capability: "automated_selected_check",
  policyVersion: "2.0.0",
}));

export const result: VerificationResult = {
  requestId: "req_test",
  buildId: "test",
  profileId,
  profileVersion: "2.0.0",
  modelIdentity: "test-ocr",
  ruleSources: ["https://www.ttb.gov/"],
  serverDurationMs: 1800,
  stageTimings: { ocrMs: 1200 },
  panels: [{ panelId: "panel-1", originalDimensions: { width: 1200, height: 1600 }, qualitySignals: { qualityClass: "Sufficient" }, coverageState: "Sufficient" }],
  evidence: [
    { evidenceId: "ev_beverage_type_panel-1_00", panelId: "panel-1", polygonOriginalPixels: [{ x: 10, y: 10 }, { x: 400, y: 10 }, { x: 400, y: 100 }, { x: 10, y: 100 }], sourceView: "original", transformId: "identity", textSnippet: "BOURBON WHISKEY", confidenceProvenance: { source: "ocr", signal: .98, calibratedProbability: false } },
    { evidenceId: "ev_brand_panel-1_00", panelId: "panel-1", polygonOriginalPixels: [{ x: 10, y: 120 }, { x: 500, y: 120 }, { x: 500, y: 220 }, { x: 10, y: 220 }], sourceView: "original", transformId: "identity", textSnippet: "OLD TOM DISTILLERY", confidenceProvenance: { source: "ocr", signal: .97, calibratedProbability: false } },
  ],
  checks,
  limitations: ["Physical warning type size needs reliable scale."],
  summary: "Review needed",
  historyId: "hist_test",
};

export const analysis: AnalysisResult = {
  requestId: "req_test",
  buildId: "test",
  profileId,
  modelIdentity: "test-ocr",
  serverDurationMs: 1800,
  panels: result.panels,
  evidence: result.evidence,
  draft: { beverageType: "distilled_spirits", brandName: "OLD TOM DISTILLERY", classType: "Kentucky Straight Bourbon Whiskey", abvPercent: 45, proof: 90, netContentsValue: 750, netContentsUnit: "mL", producerNameAddress: "Old Tom Distillery, Frankfort, Kentucky", isImported: false, countryOfOrigin: null, wineAppellation: null, wineSulfiteStatus: "unknown", maltAlcoholSource: "unknown" },
  detected: {},
  beverageTypeConfidence: .96,
  beverageTypeReason: "Class terms support distilled spirits.",
  limitations: [],
  verification: result,
};
