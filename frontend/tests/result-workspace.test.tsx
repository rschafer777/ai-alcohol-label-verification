import { createRef } from "react";
import { fireEvent, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ResultWorkspace } from "../src/features/verification/ResultWorkspace";
import { completeResult, sampleFile } from "./fixtures";

function renderWorkspace(overrides: Parameters<typeof ResultWorkspace>[0] extends never ? never : Partial<Parameters<typeof ResultWorkspace>[0]> = {}) {
  const props = {
    result: completeResult(),
    sourcePanels: [sampleFile()],
    selectedEvidenceId: "ev_brand_panel-1_01",
    note: "",
    disposition: "",
    summaryRef: createRef<HTMLHeadingElement>(),
    onSelectEvidence: vi.fn(),
    onNoteChange: vi.fn(),
    onDispositionChange: vi.fn(),
    onStartOver: vi.fn(),
    ...overrides,
  };
  return { ...render(<ResultWorkspace {...props} />), props };
}

describe("result evidence workspace", () => {
  it("operates all display-only viewer controls and review fields", async () => {
    const user = userEvent.setup();
    const { container, props } = renderWorkspace();

    await user.click(screen.getByRole("button", { name: "Enhanced display" }));
    expect(screen.getByText(/Display-only contrast enhancement/)).toBeInTheDocument();
    expect(container.querySelector(".image-transform")).toHaveClass("enhanced");

    const zoomOut = screen.getByRole("button", { name: "Zoom out" });
    await user.click(zoomOut);
    expect(zoomOut).toBeDisabled();
    const zoomIn = screen.getByRole("button", { name: "Zoom in" });
    for (let index = 0; index < 5; index += 1) await user.click(zoomIn);
    expect(zoomIn).toBeDisabled();
    await user.click(screen.getByRole("button", { name: "Rotate" }));
    expect(container.querySelector(".image-transform")).toHaveClass("rotate-90");
    await user.click(screen.getByRole("button", { name: "Fit and reset" }));
    expect(screen.getByRole("button", { name: "Original" })).toHaveAttribute("aria-pressed", "true");
    expect(container.querySelector(".image-transform")).toHaveClass("zoom-100", "rotate-0");

    await user.click(screen.getByRole("button", { name: "Show on label" }));
    expect(props.onSelectEvidence).toHaveBeenCalledWith("ev_brand_panel-1_01");
    await user.selectOptions(screen.getByLabelText("Session disposition (optional)"), "reviewed");
    expect(props.onDispositionChange).toHaveBeenCalledWith("reviewed");
    fireEvent.change(screen.getByLabelText("Reviewer note (optional)"), { target: { value: "Reviewed" } });
    expect(props.onNoteChange).toHaveBeenCalledWith("Reviewed");
    await user.click(screen.getByRole("button", { name: "Start over" }));
    expect(props.onStartOver).toHaveBeenCalledOnce();
  });

  it("renders all semantic states and truthful empty fallbacks", () => {
    const result = completeResult({
      summary: "Differences detected",
      limitations: [],
      evidence: [],
    });
    result.checks[0] = {
      ...result.checks[0]!,
      evidenceRef: null,
      referenceDisplay: null,
      observedDisplay: null,
      state: "Mismatch",
    };
    result.checks[1] = {
      ...result.checks[1]!,
      referenceDisplay: null,
      observedDisplay: null,
      state: "Review",
    };
    result.checks[2] = {
      ...result.checks[2]!,
      referenceDisplay: null,
      observedDisplay: null,
      state: "Not verified",
    };
    result.checks[3] = {
      ...result.checks[3]!,
      applicable: false,
      referenceDisplay: null,
      observedDisplay: null,
      state: "Not verified",
    };

    renderWorkspace({ result, sourcePanels: [], selectedEvidenceId: null });
    expect(screen.getByRole("heading", { name: "Differences detected" })).toBeInTheDocument();
    expect(screen.getByText(/Original panel preview is unavailable/)).toBeInTheDocument();
    expect(screen.getByText(/Choose Show on label/)).toBeInTheDocument();
    expect(screen.getByText("No additional result limitations were reported.")).toBeInTheDocument();

    const difference = screen.getByRole("article", { name: result.checks[0]!.label });
    expect(within(difference).getByText("Difference")).toBeInTheDocument();
    expect(within(difference).getByText("Condition not satisfied")).toBeInTheDocument();
    const review = screen.getByRole("article", { name: result.checks[1]!.label });
    expect(within(review).getByText("Review required")).toBeInTheDocument();
    const unverified = screen.getByRole("article", { name: result.checks[2]!.label });
    expect(within(unverified).getByText("Not verified", { selector: "dd" })).toBeInTheDocument();
    const notApplicable = screen.getByRole("article", { name: result.checks[3]!.label });
    expect(within(notApplicable).getAllByText("Not applicable").length).toBeGreaterThan(0);
    expect(screen.getAllByText("No visual evidence is available for this check.").length).toBeGreaterThan(0);
  });

  it("uses the review summary class and selected panel fallback", () => {
    const result = completeResult({ summary: "Review needed" });
    result.evidence[0]!.panelId = "panel-2";
    result.panels.push({
      panelId: "panel-2",
      originalDimensions: { width: 100, height: 100 },
      qualitySignals: {},
      coverageState: "complete",
    });
    renderWorkspace({ result, sourcePanels: [sampleFile("front.png"), sampleFile("back.png")] });
    expect(screen.getByRole("heading", { name: "Review needed" }).closest("section")).toHaveClass("summary-review");
    expect(screen.getByAltText("Original label panel-2")).toBeInTheDocument();
  });
});
