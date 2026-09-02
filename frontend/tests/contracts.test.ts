import { describe, expect, it } from "vitest";

import { checkIds, limits, profileId } from "../src/api/generated-contract";
import { parseAnalysisResult, parseVerificationResult } from "../src/contracts/runtime";
import {
  imageSelectionIssue,
  spreadsheetSafeCsvCell,
  suggestProductGroups,
} from "../src/features/batch/grouping";
import { analysis, result } from "./fixtures";

function image(name: string, path = name): File {
  const file = new File(["image"], name, { type: "image/jpeg" });
  Object.defineProperty(file, "webkitRelativePath", { value: path });
  return file;
}

describe("governed frontend contract", () => {
  it("uses the final multi-beverage limits and 24 ordered checks", () => {
    expect(profileId).toBe("all_beverages_demo_v2");
    expect(checkIds).toHaveLength(24);
    expect(limits.panelCountMax).toBe(3);
    expect(limits.fileBytes).toBe(4_194_304);
  });

  it("validates the combined single-pass analysis and verification result", () => {
    expect(parseVerificationResult(result).checks).toHaveLength(24);
    expect(parseAnalysisResult(analysis).verification?.historyId).toBe("hist_test");
  });

  it("groups up to three related panels without merging different product folders", () => {
    const groups = suggestProductGroups([
      image("front.jpg", "batch/alpha/front.jpg"),
      image("back.jpg", "batch/alpha/back.jpg"),
      image("neck.jpg", "batch/alpha/neck.jpg"),
      image("side.jpg", "batch/alpha/side.jpg"),
      image("front.jpg", "batch/beta/front.jpg"),
    ]);
    expect(groups).toHaveLength(3);
    expect(groups.map((group) => group.files.length)).toEqual([3, 1, 1]);
  });

  it("checks file limits and neutralizes spreadsheet formula cells", () => {
    const unsupported = new File(["image"], "label.gif", { type: "image/gif" });
    expect(imageSelectionIssue([unsupported], 3)).toContain("not a JPEG");
    const oversized = new File([new Uint8Array(limits.fileBytes + 1)], "large.jpg", {
      type: "image/jpeg",
    });
    expect(imageSelectionIssue([oversized], 3)).toContain("larger than 4 MB");
    expect(spreadsheetSafeCsvCell("=2+2")).toBe("\"'=2+2\"");
    expect(spreadsheetSafeCsvCell("ordinary")).toBe("\"ordinary\"");
  });
});
