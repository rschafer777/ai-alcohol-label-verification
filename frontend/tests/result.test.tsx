import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ReviewWorkspace } from "../src/features/verification/ReviewWorkspace";
import { result } from "./fixtures";

const images = [{ src: "blob:test-preview", name: "label.jpg", alt: "label.jpg label image", title: "Front" }];

function renderReview(overrides: Partial<Parameters<typeof ReviewWorkspace>[0]> = {}) {
  const onDisposition = vi.fn();
  const onBack = vi.fn();
  render(<ReviewWorkspace beverageType="distilled_spirits" brandName="OLD TOM DISTILLERY" disposition={null} images={images} imported={false} note="" onBack={onBack} onDisposition={onDisposition} onNote={vi.fn()} onSave={vi.fn()} result={result} {...overrides} />);
  return { onDisposition, onBack };
}

describe("review workspace", () => {
  it("shows the dotted map, focuses one region on Show, and restores with Show all regions", async () => {
    const user = userEvent.setup();
    renderReview();
    expect(screen.getByRole("heading", { name: "OLD TOM DISTILLERY" })).toBeInTheDocument();
    expect(screen.getByText(/24 checks · distilled spirits profile/)).toBeInTheDocument();
    expect(screen.getByText("All evidence regions")).toBeInTheDocument();
    expect(document.querySelectorAll(".stage-inner polygon")).toHaveLength(2);

    await user.click(screen.getAllByRole("button", { name: "Show" })[0]!);
    expect(document.querySelectorAll(".stage-inner polygon")).toHaveLength(1);
    expect(screen.getByText("“BOURBON WHISKEY”")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Show all regions" }));
    expect(document.querySelectorAll(".stage-inner polygon")).toHaveLength(2);
  });

  it("zooms with the mouse wheel over the image and pans by dragging when enlarged", () => {
    renderReview();
    const stage = screen.getByLabelText("Label image with evidence regions");
    const inner = document.querySelector(".stage-inner") as HTMLElement;
    expect(screen.getByRole("button", { name: "Reset zoom to 100%" })).toHaveTextContent("100%");

    fireEvent.wheel(stage, { deltaY: -100, clientX: 0, clientY: 0 });
    expect(screen.getByRole("button", { name: "Reset zoom to 100%" })).toHaveTextContent("110%");
    expect(stage).toHaveClass("zoomed");

    fireEvent.pointerDown(stage, { button: 0, pointerId: 1, clientX: 100, clientY: 100 });
    fireEvent.pointerMove(stage, { pointerId: 1, clientX: 130, clientY: 120 });
    fireEvent.pointerUp(stage, { pointerId: 1 });
    expect(inner.style.transform).toContain("translate(30px, 20px)");

    fireEvent.wheel(stage, { deltaY: 100, clientX: 0, clientY: 0 });
    expect(screen.getByRole("button", { name: "Reset zoom to 100%" })).toHaveTextContent("100%");
    expect(inner.style.transform).toContain("translate(0px, 0px)");
    expect(stage).not.toHaveClass("zoomed");

    fireEvent.keyDown(stage, { key: "+" });
    expect(screen.getByRole("button", { name: "Reset zoom to 100%" })).toHaveTextContent("125%");
    fireEvent.keyDown(stage, { key: "ArrowRight" });
    expect(inner.style.transform).toContain("translate(-40px, 0px)");
    fireEvent.click(screen.getByRole("button", { name: "Reset zoom to 100%" }));
    expect(inner.style.transform).toContain("translate(0px, 0px) scale(1)");
  });

  it("offers the view switcher at the head of the checks with icons", () => {
    renderReview();
    const group = screen.getByRole("radiogroup", { name: "View as" });
    expect(group.closest(".checks-head")).not.toBeNull();
    expect(within(group).getAllByRole("radio")).toHaveLength(3);
    expect(within(group).getByRole("radio", { name: "Table" })).toHaveAttribute("aria-checked", "true");
    expect(within(group).getByRole("radio", { name: "Table" }).querySelector("svg")).not.toBeNull();
  });

  it("collapses the warning group into ten mini badges and expands on request", async () => {
    const user = userEvent.setup();
    renderReview();
    const strip = document.querySelector(".warning-strip");
    expect(strip).not.toBeNull();
    expect(within(strip as HTMLElement).getAllByText(/Match|Review/)).toHaveLength(10);
    await user.click(screen.getByRole("button", { name: "Expand 10 checks" }));
    expect(screen.getByRole("table", { name: "Government warning checks" })).toBeInTheDocument();
  });

  it("switches layouts, opens the warning inspect view, and records dispositions from the keyboard", async () => {
    const user = userEvent.setup();
    const { onDisposition } = renderReview();
    await user.click(screen.getByRole("radio", { name: "Cards" }));
    expect(document.querySelectorAll("article.check-card")).toHaveLength(24);
    await user.click(screen.getByRole("radio", { name: "Image first" }));
    expect(document.querySelectorAll(".check-rail button")).toHaveLength(24);

    await user.click(screen.getAllByRole("button", { name: "Inspect warning" })[0]!);
    expect(screen.getByRole("heading", { name: "Government warning statement" })).toBeInTheDocument();
    expect(screen.getByText("Review · 1 of 10")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Back to all checks" }));

    await user.keyboard("a");
    expect(onDisposition).toHaveBeenLastCalledWith("approved");
    await user.click(screen.getByRole("button", { name: /Reject/ }));
    expect(onDisposition).toHaveBeenLastCalledWith("rejected");
  });

  it("shows the low-confidence type strip only when the inference asks for it", () => {
    const onConfirmType = vi.fn();
    renderReview({ onConfirmType, result: { ...result, beverageInference: { type: "wine", confidence: "low", reason: "weak signal", conflicting: false } } });
    expect(screen.getByText("We read this as Wine, but with low confidence.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Confirm & re-check" })).toBeInTheDocument();
  });
});
