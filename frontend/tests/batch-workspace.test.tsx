import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { BatchWorkspace } from "../src/features/batch/BatchWorkspace";
import { batchProgress, groupFromSuggestion, mergeGroups, moveImage, splitGroup } from "../src/features/batch/batch-state";
import { filterBatchSelection } from "../src/features/batch/grouping";
import { analysis } from "./fixtures";

const historyClient = { meta: vi.fn(async () => null), list: vi.fn(), get: vi.fn(), setDisposition: vi.fn(async () => true), remove: vi.fn(), clear: vi.fn() };

describe("batch grouping workspace", () => {
  it("reads every image, shows server-suggested groups, and unlocks Run only after confirmation", async () => {
    const user = userEvent.setup();
    const front = new File(["image"], "front.jpg", { type: "image/jpeg" });
    const back = new File(["image"], "back.jpg", { type: "image/jpeg" });
    const analyze = vi.fn(async () => analysis);
    const suggestGroups = vi.fn(async () => ({ groups: [
      { groupId: "group-1", panelIds: ["img-1", "img-2"], suggestedName: "OLD TOM DISTILLERY", inferredType: "distilled_spirits" as const, confidence: "high" as const, status: "ready_to_confirm" as const, reasons: ["Same brand read on each image"], conflict: false },
    ], analyzed: 2, failed: 0 }));
    render(<BatchWorkspace batchName="Test batch" historyClient={historyClient} initialFiles={[front, back]} onExit={vi.fn()} onHistoryChanged={vi.fn()} onScreenTitle={vi.fn()} verificationClient={{ analyze, verify: vi.fn(), suggestGroups }} />);

    expect(await screen.findByRole("heading", { name: "Confirm how the images group into products" })).toBeInTheDocument();
    expect(analyze).toHaveBeenCalledTimes(2);
    expect(suggestGroups).toHaveBeenCalledTimes(1);
    const name = screen.getByLabelText("Product 1 name");
    expect(name).toHaveValue("OLD TOM DISTILLERY");
    const run = screen.getByRole("button", { name: "Run 1 product" });
    expect(run).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Confirm" }));
    expect(run).toBeEnabled();

    await user.click(run);
    await waitFor(() => expect(analyze).toHaveBeenCalledTimes(3));
    expect(await screen.findByRole("heading", { name: /Test batch: 1 product, 2 images/ })).toBeInTheDocument();
    expect(await screen.findByRole("button", { name: "Open" })).toBeInTheDocument();
  });
});

describe("batch grouping guidance", () => {
  it("shows what is left to confirm, filters to it, and confirms the remaining suggestions in one step", async () => {
    const user = userEvent.setup();
    const files = [new File(["image"], "a.jpg", { type: "image/jpeg" }), new File(["image"], "b.jpg", { type: "image/jpeg" })];
    const analyze = vi.fn(async () => analysis);
    const suggestGroups = vi.fn(async () => ({ groups: [
      { groupId: "group-1", panelIds: ["img-1"], suggestedName: "OLD TOM DISTILLERY", inferredType: "distilled_spirits" as const, confidence: "high" as const, status: "ready_to_confirm" as const, reasons: ["One image, one product"], conflict: false },
      { groupId: "group-2", panelIds: ["img-2"], suggestedName: "Product 2", inferredType: null, confidence: "low" as const, status: "needs_review" as const, reasons: ["Brand not read; confirm this product"], conflict: false },
    ], analyzed: 2, failed: 0 }));
    render(<BatchWorkspace batchName="Test batch" historyClient={historyClient} initialFiles={files} onExit={vi.fn()} onHistoryChanged={vi.fn()} onScreenTitle={vi.fn()} verificationClient={{ analyze, verify: vi.fn(), suggestGroups }} />);

    expect(await screen.findByRole("heading", { name: "Confirm how the images group into products" })).toBeInTheDocument();
    expect(screen.getByText(/0 of 2 products confirmed/)).toBeInTheDocument();
    const run = screen.getByRole("button", { name: "Run 2 products" });
    expect(run).toBeDisabled();
    expect(screen.getByText("Confirm 2 more products to unlock the run.")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Confirm all ready (1)" }));
    expect(screen.getByText(/1 of 2 products confirmed/)).toBeInTheDocument();
    expect(screen.getByText("Confirm 1 more product to unlock the run.")).toBeInTheDocument();
    expect(run).toBeDisabled();

    await user.click(screen.getByRole("button", { name: "Show the 1 that still need confirmation" }));
    expect(screen.queryByLabelText("Product 1 name")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Product 2 name")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Confirm the remaining 1 as suggested" }));
    expect(screen.getByText(/All 2 products are confirmed/)).toBeInTheDocument();
    expect(run).toBeEnabled();
    // The filter clears itself once nothing is left to confirm.
    expect(screen.getByLabelText("Product 1 name")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Show all/ })).not.toBeInTheDocument();
  });

  it("leaves conflicts out of the one-step confirmation and says so", async () => {
    const user = userEvent.setup();
    const files = [new File(["image"], "a.jpg", { type: "image/jpeg" }), new File(["image"], "b.jpg", { type: "image/jpeg" }), new File(["image"], "c.jpg", { type: "image/jpeg" })];
    const analyze = vi.fn(async () => analysis);
    const suggestGroups = vi.fn(async () => ({ groups: [
      { groupId: "group-1", panelIds: ["img-1"], suggestedName: "Product 1", inferredType: null, confidence: "low" as const, status: "needs_review" as const, reasons: ["Brand not read; confirm this product"], conflict: false },
      { groupId: "group-2", panelIds: ["img-2", "img-3"], suggestedName: "JACK DANIEL'S", inferredType: "distilled_spirits" as const, confidence: "low" as const, status: "needs_review" as const, reasons: ["Filename cues match", "Two different brands read"], conflict: true },
    ], analyzed: 3, failed: 0 }));
    render(<BatchWorkspace batchName="Test batch" historyClient={historyClient} initialFiles={files} onExit={vi.fn()} onHistoryChanged={vi.fn()} onScreenTitle={vi.fn()} verificationClient={{ analyze, verify: vi.fn(), suggestGroups }} />);

    expect(await screen.findByRole("heading", { name: "Confirm how the images group into products" })).toBeInTheDocument();
    expect(screen.getByText(/One card shows a/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Confirm the remaining 1 as suggested" }));

    expect(screen.getByText(/1 of 2 products confirmed/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Confirm the remaining/ })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Run 2 products" })).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Confirm anyway" }));
    expect(screen.getByRole("button", { name: "Run 2 products" })).toBeEnabled();
  });
});

describe("batch state helpers", () => {
  const groups = [
    groupFromSuggestion({ groupId: "g1", panelIds: ["a", "b"], suggestedName: "A", inferredType: "wine", confidence: "high", status: "ready_to_confirm", reasons: [], conflict: false }),
    groupFromSuggestion({ groupId: "g2", panelIds: ["c"], suggestedName: "C", inferredType: "wine", confidence: "high", status: "ready_to_confirm", reasons: [], conflict: false }),
  ];

  it("moves, splits, and merges while returning edited groups to needs confirmation", () => {
    const moved = moveImage(groups, "a", "g2");
    expect(moved.map((group) => group.imageIds)).toEqual([["b"], ["c", "a"]]);
    expect(moved.every((group) => group.status === "needs_confirmation" && !group.confirmed)).toBe(true);
    const split = splitGroup(groups, "g1");
    expect(split).toHaveLength(3);
    const merged = mergeGroups(groups, ["g1", "g2"]);
    expect(merged).toHaveLength(1);
    expect(merged[0]?.imageIds).toEqual(["a", "b", "c"]);
    expect(moveImage(groups, "c", null).at(-1)?.imageIds).toEqual(["c"]);
  });

  it("reports progress counts and holds ETA until three products finish", () => {
    const running = groups.map((group, index) => ({ ...group, runStatus: index === 0 ? ("running" as const) : ("queued" as const) }));
    const progress = batchProgress(running, 3, "running", 1200, 0);
    expect(progress.counts).toMatchObject({ total: 2, remaining: 2, running: 1, queued: 1, complete: 0 });
    expect(progress.current?.productId).toBe("g1");
    expect(progress.timing.etaMs).toBeNull();
  });

  it("accepts supported folder images while reporting non-image and oversized files", () => {
    const image = new File(["image"], "front.jpg", { type: "image/jpeg" });
    const metadata = new File(["{}"], "test-oracle-v1.json", { type: "application/json" });
    // A supported photo above the byte limit is shrunk in the browser later, so it is accepted;
    // an untyped file of that size cannot be re-encoded and is reported.
    const phonePhoto = new File([new Uint8Array(4_194_305)], "phone.jpg", { type: "image/jpeg" });
    const oversized = new File([new Uint8Array(4_194_305)], "large.png", { type: "" });

    const selection = filterBatchSelection([image, metadata, phonePhoto, oversized]);

    expect(selection.accepted).toEqual([image, phonePhoto]);
    expect(selection.skipped).toEqual([
      { name: "test-oracle-v1.json", reason: "unsupported type" },
      { name: "large.png", reason: "over 4 MB" },
    ]);
  });
});
