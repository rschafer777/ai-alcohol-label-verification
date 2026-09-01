import { describe, expect, it } from "vitest";

import {
  draftHasContent,
  EMPTY_DRAFT,
  MAX_AGGREGATE_BYTES,
  MAX_FILE_BYTES,
  MAX_PANELS,
  referenceToDraft,
  toReference,
  validateDraft,
  type ReferenceDraft,
} from "../src/features/intake/model";
import { sampleFile, sampleReference } from "./fixtures";

function completeDraft(overrides: Partial<ReferenceDraft> = {}): ReferenceDraft {
  return {
    ...referenceToDraft(sampleReference),
    ...overrides,
  };
}

describe("intake model boundaries", () => {
  it("round trips normalized reference values and optional fields", () => {
    const draft = completeDraft({
      caseLabel: "  Case 7  ",
      proof: "",
      isImported: true,
      countryOfOrigin: "  Canada  ",
    });
    expect(toReference(draft)).toMatchObject({
      caseLabel: "Case 7",
      brandName: "OLD TOM DISTILLERY",
      proof: null,
      isImported: true,
      countryOfOrigin: "Canada",
    });
    expect(referenceToDraft({ ...sampleReference, caseLabel: null, proof: null, countryOfOrigin: null })).toMatchObject({
      caseLabel: "",
      proof: "",
      countryOfOrigin: "",
    });
  });

  it("reports every scalar validation boundary", () => {
    const errors = validateDraft(completeDraft({
      caseLabel: "x".repeat(81),
      brandName: " ",
      classType: "x".repeat(241),
      abvPercent: "101",
      proof: "not-a-number",
      netContentsValue: "0",
      producerNameAddress: "x".repeat(501),
      isImported: true,
      countryOfOrigin: " ",
    }), []);
    expect(errors).toEqual({
      brandName: "Brand name is required.",
      classType: "Class or type must be 240 characters or fewer.",
      abvPercent: "Alcohol by volume must be 100 or less.",
      proof: "Proof must be 0 or greater.",
      netContentsValue: "Net contents must be a number greater than 0.",
      producerNameAddress: "Producer name and address must be 500 characters or fewer.",
      caseLabel: "Case label must be 80 characters or fewer.",
      countryOfOrigin: "Country of origin is required.",
      panels: "Add 1 to 6 label panels.",
    });
    expect(validateDraft(completeDraft({ abvPercent: "not-a-number", netContentsValue: "" }), [sampleFile()])).toMatchObject({
      abvPercent: "Alcohol by volume must be a number greater than 0.",
      netContentsValue: "Net contents is required.",
    });
  });

  it("reports each file policy in precedence order", () => {
    const draft = completeDraft();
    expect(validateDraft(draft, Array.from({ length: MAX_PANELS + 1 }, (_, index) => sampleFile(`${index}.png`))).panels)
      .toBe("Add 1 to 6 label panels.");
    expect(validateDraft(draft, [new File(["text"], "label.txt", { type: "text/plain" })]).panels)
      .toBe("Use JPEG, PNG, or WebP images only.");
    expect(validateDraft(draft, [new File([new Uint8Array(MAX_FILE_BYTES + 1)], "large.png", { type: "image/png" })]).panels)
      .toBe("Each image must be 4 MiB or smaller.");
    const third = Math.floor(MAX_AGGREGATE_BYTES / 3) + 1;
    expect(validateDraft(draft, [
      new File([new Uint8Array(third)], "one.png", { type: "image/png" }),
      new File([new Uint8Array(third)], "two.png", { type: "image/png" }),
      new File([new Uint8Array(third)], "three.png", { type: "image/png" }),
    ]).panels).toBe("All images together must be 8 MiB or smaller.");
    expect(validateDraft(draft, [sampleFile()])).toEqual({});
  });

  it("detects meaningful draft content without treating the default unit as work", () => {
    expect(draftHasContent(EMPTY_DRAFT)).toBe(false);
    expect(draftHasContent({ ...EMPTY_DRAFT, netContentsUnit: "L" })).toBe(true);
    expect(draftHasContent({ ...EMPTY_DRAFT, isImported: true })).toBe(true);
    expect(draftHasContent({ ...EMPTY_DRAFT, brandName: "A" })).toBe(true);
  });
});
