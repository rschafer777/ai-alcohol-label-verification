import {
  checkIds,
  profileId,
  type CheckResult,
  type ReferenceRecord,
  type VerificationResult,
} from "../src/api/generated-contract";
import type { LoadedSample } from "../src/contracts/types";

export const sampleReference: ReferenceRecord = {
  profileId,
  caseLabel: "Sample case",
  brandName: "OLD TOM DISTILLERY",
  classType: "Kentucky Straight Bourbon Whiskey",
  abvPercent: 45,
  proof: 90,
  netContentsValue: 750,
  netContentsUnit: "mL",
  producerNameAddress: "Old Heritage Distillery LLC\nFrankfort, Kentucky",
  isImported: false,
  countryOfOrigin: null,
};

export function sampleFile(name = "old-tom-front.png"): File {
  return new File([new Uint8Array([1, 2, 3])], name, { type: "image/png" });
}

export function loadedSample(): LoadedSample {
  return { reference: sampleReference, panels: [sampleFile()] };
}

function labelFor(checkId: string): string {
  return checkId.split("_").map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(" ");
}

export function completeResult(overrides: Partial<VerificationResult> = {}): VerificationResult {
  const checks: CheckResult[] = checkIds.map((checkId) => ({
    checkId,
    label: labelFor(checkId),
    applicable: true,
    referenceDisplay: checkId === "brand" ? "OLD TOM DISTILLERY" : "Expected value",
    observedDisplay: checkId === "brand" ? "OLD TOM DISTILLERY" : "Observed value",
    state: "Match",
    reasonCode: "exact_match",
    reasonText: "The checked value matches the application value.",
    evidenceRef: checkId === "brand" ? "ev_brand_panel-1_01" : null,
    alternatives: [],
    capability: "supported",
    policyVersion: "1.0.0",
  }));

  return {
    requestId: "request-test-1",
    buildId: "build-test-1",
    profileId,
    profileVersion: "1.0.0",
    modelIdentity: "rapidocr-test",
    ruleSources: ["rules-v1"],
    serverDurationMs: 1200,
    stageTimings: { total: 1200 },
    panels: [{ panelId: "panel-1", originalDimensions: { width: 100, height: 100 }, qualitySignals: {}, coverageState: "complete" }],
    evidence: [{
      evidenceId: "ev_brand_panel-1_01",
      panelId: "panel-1",
      polygonOriginalPixels: [{ x: 10, y: 10 }, { x: 50, y: 10 }, { x: 50, y: 20 }, { x: 10, y: 20 }],
      sourceView: "original",
      transformId: "original",
      textSnippet: "OLD TOM DISTILLERY",
      confidenceProvenance: { source: "rapidocr", signal: 0.95, calibratedProbability: false },
    }],
    checks,
    limitations: ["Physical type size needs human confirmation without a reliable scale."],
    summary: "No differences found in checked fields",
    ...overrides,
  };
}
