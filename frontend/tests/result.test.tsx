import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ResultWorkspace } from "../src/features/verification/ResultWorkspace";
import { analysis, result } from "./fixtures";

describe("review workspace", () => {
  it("supports evidence localization, alternate layouts, warning detail, and dispositions", async () => {
    const user = userEvent.setup();
    render(<ResultWorkspace analysis={analysis} onStartOver={vi.fn()} result={result} sourcePanels={[new File(["image"], "label.jpg", { type: "image/jpeg" })]} />);
    expect(screen.getByText("24 selected checks | Distilled spirits")).toBeInTheDocument();
    await user.click(screen.getAllByRole("button", { name: "Show" })[0]!);
    expect(screen.getByText("Read: BOURBON WHISKEY")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cards" }));
    expect(screen.getAllByRole("article")).toHaveLength(24);
    await user.click(screen.getByRole("button", { name: "Inspect warning" }));
    expect(screen.getByRole("heading", { name: "Government warning statement" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Continue review" }));
    await user.click(screen.getByRole("button", { name: "Approve A" }));
    expect(screen.getByRole("button", { name: "Approve A" })).toHaveAttribute("aria-pressed", "true");
  });
});
