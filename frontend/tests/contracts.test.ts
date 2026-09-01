import { describe, expect, it } from "vitest";

import { limits, checkIds } from "../src/api/generated-contract";
import { parsePublicError, parseVerificationResult, ResponseContractError } from "../src/contracts/runtime";
import { completeResult } from "./fixtures";

describe("CG-001 and CG-004 frontend consumption", () => {
  it("uses the exact selected checks and limits", () => {
    expect(checkIds).toHaveLength(19);
    expect(new Set(checkIds).size).toBe(19);
    expect(limits).toMatchObject({
      fileBytes: 4_194_304,
      aggregateFileBytes: 8_388_608,
      panelCountMin: 1,
      panelCountMax: 6,
      browserDeadlineSeconds: 35,
    });
  });

  it("accepts a complete evidence-linked result", () => {
    const result = completeResult();
    expect(parseVerificationResult(result)).toEqual(result);
  });

  it("suppresses a result with a missing selected check", () => {
    const result = completeResult();
    result.checks = result.checks.slice(0, -1);
    expect(() => parseVerificationResult(result)).toThrow(ResponseContractError);
  });

  it("suppresses unresolved evidence instead of guessing", () => {
    const result = completeResult();
    const brand = result.checks.find((check) => check.checkId === "brand");
    if (!brand) throw new Error("Brand fixture is missing.");
    brand.evidenceRef = "ev_missing_panel-1_01";
    expect(() => parseVerificationResult(result)).toThrow(ResponseContractError);
  });

  it("enforces registry retryability and locator rules", () => {
    const parsed = parsePublicError({
      requestId: "request-error-1",
      code: "invalid_image",
      message: "Replace the image.",
      fieldOrPanel: "panel-1",
      retryable: true,
      nextAction: "Untrusted action",
    });
    expect(parsed).toMatchObject({ retryable: false, fieldOrPanel: "panel-1", nextAction: "Replace the identified corrupt or unreadable image" });
  });
});
