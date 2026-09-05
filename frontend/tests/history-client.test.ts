import { describe, expect, it, vi } from "vitest";

import { createHistoryClient } from "../src/api/history-client";
import { result } from "./fixtures";

describe("history correction client", () => {
  it("sends the governed correction request and reads the revision envelope", async () => {
    const fetcher = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      void input;
      void init;
      return new Response(JSON.stringify({
        historyId: "hist_revision_2",
        rootId: "hist_root",
        parentId: "hist_revision_1",
        revision: 2,
        result: { ...result, historyId: "hist_revision_2", revision: 2, revisionKind: "correction" },
      }), { status: 200, headers: { "Content-Type": "application/json" } });
    });
    const client = createHistoryClient(fetcher as unknown as typeof fetch);

    const revised = await client.correct!("hist_revision_1", {
      expectedRevision: 1,
      reason: "Reviewer confirmed visible text",
      corrections: [{
        field: "beverage_type",
        family: "wine",
        evidenceRef: "ev_class_panel-1_01",
      }],
    });

    expect(revised.historyId).toBe("hist_revision_2");
    expect(revised.revisionKind).toBe("correction");
    const request = fetcher.mock.calls[0]![1]!;
    expect(JSON.parse(String(request.body))).toEqual({
      expectedRevision: 1,
      reason: "Reviewer confirmed visible text",
      corrections: [{
        field: "beverage_type",
        family: "wine",
        evidenceRef: "ev_class_panel-1_01",
      }],
    });
  });
});
