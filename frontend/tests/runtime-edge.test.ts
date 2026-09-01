import { describe, expect, it } from "vitest";

import { internalError, parsePublicError, parseVerificationResult, ResponseContractError } from "../src/contracts/runtime";
import { completeResult } from "./fixtures";

function expectContractFailure(value: unknown) {
  expect(() => parseVerificationResult(value)).toThrow(ResponseContractError);
}

describe("response contract adversarial boundaries", () => {
  it("rejects malformed schemas and duplicate identifiers", () => {
    expectContractFailure({});

    const duplicatePanels = completeResult();
    duplicatePanels.panels.push({ ...duplicatePanels.panels[0]! });
    expectContractFailure(duplicatePanels);

    const duplicateEvidence = completeResult();
    duplicateEvidence.evidence.push({ ...duplicateEvidence.evidence[0]! });
    expectContractFailure(duplicateEvidence);

    const duplicateChecks = completeResult();
    duplicateChecks.checks[1] = { ...duplicateChecks.checks[0]! };
    expectContractFailure(duplicateChecks);
  });

  it("rejects missing, out-of-bounds, unordered, and degenerate evidence", () => {
    const missingPanel = completeResult();
    missingPanel.evidence[0]!.panelId = "panel-2";
    expectContractFailure(missingPanel);

    const outOfBounds = completeResult();
    outOfBounds.evidence[0]!.polygonOriginalPixels[2]!.x = 100;
    expectContractFailure(outOfBounds);

    const unordered = completeResult();
    const points = unordered.evidence[0]!.polygonOriginalPixels;
    unordered.evidence[0]!.polygonOriginalPixels = [points[2]!, points[3]!, points[0]!, points[1]!];
    expectContractFailure(unordered);

    const degenerate = completeResult();
    degenerate.evidence[0]!.polygonOriginalPixels = [
      { x: 10, y: 10 }, { x: 20, y: 10 }, { x: 30, y: 10 }, { x: 40, y: 10 },
    ];
    expectContractFailure(degenerate);
  });

  it("rejects ambiguous alternatives without distinct valid evidence", () => {
    const missing = completeResult();
    missing.checks[0]!.alternatives = [{ value: "A", evidenceRef: "ev_missing" }];
    expectContractFailure(missing);

    const duplicateReference = completeResult();
    duplicateReference.checks[0]!.alternatives = [
      { value: "A", evidenceRef: "ev_brand_panel-1_01" },
      { value: "B", evidenceRef: "ev_brand_panel-1_01" },
    ];
    expectContractFailure(duplicateReference);

    const duplicateRegion = completeResult();
    duplicateRegion.evidence.push({
      ...duplicateRegion.evidence[0]!,
      evidenceId: "ev_brand_panel-1_02",
    });
    duplicateRegion.checks[0]!.alternatives = [
      { value: "A", evidenceRef: "ev_brand_panel-1_01" },
      { value: "B", evidenceRef: "ev_brand_panel-1_02" },
    ];
    expectContractFailure(duplicateRegion);
  });

  it("rejects unknown public errors and produces a safe internal error", () => {
    expect(parsePublicError({})).toBeNull();
    expect(parsePublicError({
      requestId: "request-x",
      code: "unknown_code",
      message: "Unknown",
      retryable: true,
      nextAction: "Unknown",
      fieldOrPanel: null,
    })).toBeNull();
    expect(internalError("request-internal")).toMatchObject({
      requestId: "request-internal",
      code: "internal_error",
      fieldOrPanel: null,
    });
  });
});
