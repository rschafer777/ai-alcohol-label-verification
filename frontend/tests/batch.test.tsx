import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { App } from "../src/app/App";
import type { SampleAdapter, VerificationClient } from "../src/contracts/types";
import {
  batchCsv,
  batchDetailsJson,
  MAX_BATCH_MANIFEST_BYTES,
  MAX_BATCH_SELECTED_ENTRIES,
  parseCsv,
  readBatchDirectory,
  resultState,
  toQueueItems,
} from "../src/features/batch/model";
import { completeResult, loadedSample } from "./fixtures";

function locatedFile(path: string, contents: BlobPart, type: string): File {
  const file = new File([contents], path.split("/").at(-1) ?? "file", { type });
  Object.defineProperty(file, "webkitRelativePath", { value: `batch/${path}` });
  if (typeof file.text !== "function") {
    Object.defineProperty(file, "text", { value: async () => String(contents) });
  }
  return file;
}

const HEADER = "case_id,brand_name,class_type,abv_percent,proof,net_contents_value,net_contents_unit,producer_name_address,is_imported,country_of_origin,panel_paths";

describe("batch manifest and exports", () => {
  it("accounts for valid and invalid rows while preserving manifest order", async () => {
    const manifest = [
      HEADER,
      'CASE-001,OLD TOM DISTILLERY,Bourbon,45,90,750,mL,"Producer, Kentucky",false,,CASE-001/front.png',
      "CASE-002,STONE'S THROW,Wine,12,,750,mL,Producer,false,,CASE-002/front.png",
      "CASE-003,MISSING IMAGE,Vodka,40,80,750,mL,Producer,false,,CASE-003/front.png",
    ].join("\r\n");
    const parsed = await readBatchDirectory([
      locatedFile("manifest.csv", manifest, "text/csv"),
      locatedFile("CASE-001/front.png", new Uint8Array([1]), "image/png"),
      locatedFile("CASE-002/front.png", new Uint8Array([2]), "image/png"),
    ]);

    expect(parsed.items).toHaveLength(3);
    expect(parsed.items.map((item) => item.id)).toEqual(["CASE-001", "CASE-002", "CASE-003"]);
    expect(parsed.items[0]?.reference?.producerNameAddress).toBe("Producer, Kentucky");
    expect(parsed.items[2]?.ingressError).toContain("panel file was not found");
    const queue = toQueueItems(parsed.items);
    expect(queue.map((item) => item.state)).toEqual(["queued", "queued", "error"]);
  });

  it("rejects traversal, unreferenced files, and file ownership ambiguity", async () => {
    const traversal = [HEADER, "CASE-001,Brand,Vodka,40,80,750,mL,Producer,false,,../front.png"].join("\n");
    const traversalResult = await readBatchDirectory([
      locatedFile("manifest.csv", traversal, "text/csv"),
      locatedFile("front.png", new Uint8Array([1]), "image/png"),
    ]);
    expect(traversalResult.items).toEqual([]);
    expect(traversalResult.issues[0]?.message).toContain("unreferenced files");

    const shared = [
      HEADER,
      "CASE-001,Brand,Vodka,40,80,750,mL,Producer,false,,shared.png",
      "CASE-002,Brand,Vodka,40,80,750,mL,Producer,false,,shared.png",
    ].join("\n");
    const sharedResult = await readBatchDirectory([
      locatedFile("manifest.csv", shared, "text/csv"),
      locatedFile("shared.png", new Uint8Array([1]), "image/png"),
    ]);
    expect(sharedResult.items).toHaveLength(2);
    expect(sharedResult.items.every((item) => item.ingressError?.includes("multiple applications"))).toBe(true);
  });

  it("requires strict UTF-8, nonblank data, exact row width, and physical row numbers", async () => {
    const invalidUtf8 = await readBatchDirectory([
      locatedFile("manifest.csv", new Uint8Array([0xc3, 0x28]), "text/csv"),
    ]);
    expect(invalidUtf8.items).toEqual([]);
    expect(invalidUtf8.issues[0]?.message).toContain("valid UTF-8");

    const blankOnly = await readBatchDirectory([
      locatedFile("manifest.csv", `${HEADER}\n\n`, "text/csv"),
    ]);
    expect(blankOnly.items).toEqual([]);
    expect(blankOnly.issues[0]?.message).toContain("nonblank data row");

    const overwide = await readBatchDirectory([
      locatedFile(
        "manifest.csv",
        `${HEADER}\nCASE-001,Brand,Vodka,40,80,750,mL,Producer,false,,front.png,unexpected`,
        "text/csv",
      ),
      locatedFile("front.png", new Uint8Array([1]), "image/png"),
    ]);
    expect(overwide.items).toEqual([]);
    expect(overwide.issues).toEqual([
      expect.objectContaining({ row: 2, message: expect.stringContaining("12 fields") }),
    ]);

    const physicalRows = await readBatchDirectory([
      locatedFile(
        "manifest.csv",
        [
          HEADER,
          "",
          "CASE-003,Brand,Vodka,40,80,750,mL,Producer,false,,missing.png",
        ].join("\n"),
        "text/csv",
      ),
    ]);
    expect(physicalRows.items[0]?.manifestRow).toBe(3);
    expect(physicalRows.issues[0]?.row).toBe(3);
  });

  it("requires imported country data and rejects an invalid import flag", async () => {
    const imported = await readBatchDirectory([
      locatedFile(
        "manifest.csv",
        `${HEADER}\nCASE-001,Brand,Vodka,40,80,750,mL,Producer,yes,CANADA,front.png`,
        "text/csv",
      ),
      locatedFile("front.png", new Uint8Array([1]), "image/png"),
    ]);
    expect(imported.items[0]?.reference?.isImported).toBe(true);
    expect(imported.items[0]?.reference?.countryOfOrigin).toBe("CANADA");

    const invalid = await readBatchDirectory([
      locatedFile(
        "manifest.csv",
        `${HEADER}\nCASE-002,Brand,Vodka,40,80,750,mL,Producer,maybe,,front.png`,
        "text/csv",
      ),
      locatedFile("front.png", new Uint8Array([1]), "image/png"),
    ]);
    expect(invalid.items[0]?.reference).toBeNull();
    expect(invalid.items[0]?.ingressError).toContain("is_imported must be true or false");
  });

  it("neutralizes spreadsheet formulas and exports complete detail JSON", () => {
    const queue = toQueueItems([{
      id: "=HYPERLINK(\"bad\")",
      manifestRow: 2,
      reference: null,
      panels: [],
      panelPaths: [],
      ingressError: "Invalid row",
    }]);
    const csv = batchCsv(queue);
    expect(csv).toContain("'=HYPERLINK");
    const details = JSON.parse(batchDetailsJson(queue)) as { applications: Array<{ manifestRow: number; status: string }> };
    expect(details.applications).toEqual([expect.objectContaining({ manifestRow: 2, status: "error" })]);
  });

  it("classifies every batch result state without treating review as a difference", () => {
    const unreadable = completeResult();
    unreadable.checks = unreadable.checks.map((check) => check.checkId === "image_quality"
      ? { ...check, state: "Not verified", reasonCode: "image_unreadable" }
      : check);
    const unreadableByReason = completeResult();
    unreadableByReason.checks = unreadableByReason.checks.map((check) => check.checkId === "image_quality"
      ? { ...check, reasonCode: "image_unreadable" }
      : check);

    expect(resultState(unreadable)).toBe("bad_image");
    expect(resultState(unreadableByReason)).toBe("bad_image");
    expect(resultState(completeResult())).toBe("match");
    expect(resultState(completeResult({ summary: "Review needed" }))).toBe("review");
    expect(resultState(completeResult({ summary: "Differences detected" }))).toBe("difference");
  });

  it("parses escaped CSV quotes and rejects malformed quoted fields", () => {
    expect(parseCsv('one,"two ""quoted"""\n')).toEqual([["one", 'two "quoted"']]);
    expect(() => parseCsv('one,un"expected"')).toThrow("unexpected quote");
    expect(() => parseCsv('one,"unclosed')).toThrow("unclosed quoted value");
  });

  it("exports completed result timings, identifiers, and check states", () => {
    const sample = loadedSample();
    const queue = toQueueItems([{
      id: "CASE-001",
      manifestRow: 2,
      reference: sample.reference,
      panels: sample.panels,
      panelPaths: ["CASE-001/front.png"],
      ingressError: null,
    }]);
    queue[0] = {
      ...queue[0]!,
      state: "match",
      result: completeResult(),
      durationMs: 123.6,
    };

    const csv = batchCsv(queue);
    expect(csv).toContain("CASE-001,match,No differences found in checked fields,124,1200,request-test-1");
    const details = JSON.parse(batchDetailsJson(queue)) as {
      applications: Array<{ clientDurationMs: number; result: { requestId: string } }>;
    };
    expect(details.applications[0]).toEqual(expect.objectContaining({ clientDurationMs: 124 }));
    expect(details.applications[0]?.result.requestId).toBe("request-test-1");
  });

  it("bounds folder entries and manifest bytes and accounts for 300 ordered rows", async () => {
    const tooManyEntries = Array.from(
      { length: MAX_BATCH_SELECTED_ENTRIES + 1 },
      (_, index) => locatedFile(`file-${index}.png`, new Uint8Array([1]), "image/png"),
    );
    const entryResult = await readBatchDirectory(tooManyEntries);
    expect(entryResult.items).toEqual([]);
    expect(entryResult.issues[0]?.message).toContain("entries");

    const oversizedManifest = locatedFile(
      "manifest.csv",
      new Uint8Array(MAX_BATCH_MANIFEST_BYTES + 1),
      "text/csv",
    );
    const sizeResult = await readBatchDirectory([oversizedManifest]);
    expect(sizeResult.items).toEqual([]);
    expect(sizeResult.issues[0]?.message).toContain("1 MiB");

    const rows = Array.from({ length: 300 }, (_, index) => {
      const caseId = `CASE-${String(index + 1).padStart(3, "0")}`;
      return `${caseId},Brand,Vodka,40,80,750,mL,Producer,false,,${caseId}/front.png`;
    });
    const fullResult = await readBatchDirectory([
      locatedFile("manifest.csv", [HEADER, ...rows].join("\n"), "text/csv"),
    ]);
    expect(fullResult.items).toHaveLength(300);
    expect(fullResult.items[0]).toEqual(expect.objectContaining({ id: "CASE-001", manifestRow: 2 }));
    expect(fullResult.items[299]).toEqual(expect.objectContaining({ id: "CASE-300", manifestRow: 301 }));
    expect(fullResult.issues).toHaveLength(300);
  });
});

describe("batch workspace", () => {
  it("runs the 10-application demo sequentially and opens detailed evidence", async () => {
    const user = userEvent.setup();
    const adapter: SampleAdapter = { load: vi.fn(async () => loadedSample()) };
    let active = 0;
    let peak = 0;
    const verify = vi.fn<VerificationClient["verify"]>(async ({ reference }) => {
      active += 1;
      peak = Math.max(peak, active);
      await Promise.resolve();
      active -= 1;
      if (reference.brandName === "Old Tom Distillery") return completeResult({ summary: "Review needed" });
      if (reference.abvPercent === 46 || reference.netContentsUnit === "L") return completeResult({ summary: "Differences detected" });
      return completeResult();
    });

    render(<App sampleAdapter={adapter} verificationClient={{ verify }} />);
    await user.click(screen.getByRole("button", { name: "Batch" }));
    await user.click(screen.getByRole("button", { name: "Try a 10-application batch" }));
    expect(await screen.findByRole("heading", { name: "0 of 10 completed" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Start batch" }));
    await waitFor(() => expect(screen.getByRole("heading", { name: "10 of 10 completed" })).toBeInTheDocument());

    expect(verify).toHaveBeenCalledTimes(10);
    expect(peak).toBe(1);
    expect(screen.getByRole("button", { name: "No differences (7)" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Needs review (1)" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Differences (2)" })).toBeInTheDocument();
    await user.click(screen.getAllByRole("button", { name: "Open details" })[0]!);
    expect(await screen.findByRole("button", { name: "Back to batch results" })).toBeInTheDocument();
  });

  it("keeps a late result cancelled and permits a focused retry", async () => {
    const user = userEvent.setup();
    const adapter: SampleAdapter = { load: vi.fn(async () => loadedSample()) };
    let resolveFirst: ((result: ReturnType<typeof completeResult>) => void) | undefined;
    const firstResult = new Promise<ReturnType<typeof completeResult>>((resolve) => {
      resolveFirst = resolve;
    });
    const verify = vi.fn<VerificationClient["verify"]>(async () => {
      if (verify.mock.calls.length === 1) return firstResult;
      return completeResult();
    });

    render(<App sampleAdapter={adapter} verificationClient={{ verify }} />);
    await user.click(screen.getByRole("button", { name: "Batch" }));
    await user.click(screen.getByRole("button", { name: "Try a 10-application batch" }));
    await user.click(screen.getByRole("button", { name: "Start batch" }));
    await waitFor(() => expect(verify).toHaveBeenCalledTimes(1));
    await user.click(screen.getByRole("button", { name: "Cancel batch" }));
    resolveFirst?.(completeResult());

    await waitFor(() => expect(screen.getByRole("button", { name: "Cancelled (10)" })).toBeInTheDocument());
    expect(screen.getByRole("button", { name: "No differences (0)" })).toBeInTheDocument();

    await user.click(screen.getAllByRole("button", { name: "Retry" })[0]!);
    await waitFor(() => expect(verify).toHaveBeenCalledTimes(2));
    expect(await screen.findByRole("button", { name: "Cancelled (9)" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "No differences (1)" })).toBeInTheDocument();
  });

  it("isolates a failed row and continues later rows", async () => {
    const user = userEvent.setup();
    const adapter: SampleAdapter = { load: vi.fn(async () => loadedSample()) };
    const verify = vi.fn<VerificationClient["verify"]>(async () => {
      if (verify.mock.calls.length === 1) throw new Error("simulated row failure");
      return completeResult();
    });

    render(<App sampleAdapter={adapter} verificationClient={{ verify }} />);
    await user.click(screen.getByRole("button", { name: "Batch" }));
    await user.click(screen.getByRole("button", { name: "Try a 10-application batch" }));
    await user.click(screen.getByRole("button", { name: "Start batch" }));

    await waitFor(() => expect(screen.getByRole("heading", { name: "10 of 10 completed" })).toBeInTheDocument());
    expect(verify).toHaveBeenCalledTimes(10);
    expect(screen.getByRole("button", { name: "Errors (1)" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "No differences (9)" })).toBeInTheDocument();
  });
});
