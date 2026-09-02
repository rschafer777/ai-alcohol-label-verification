import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/app/App";
import { analysis } from "./fixtures";

describe("LabelVerify application", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ items: [], total: 0, cap: 500, offset: 0, pageSize: 3, hasMore: false }), { status: 200, headers: { "Content-Type": "application/json" } })));
  });

  it("opens with clear single and batch entry points", () => {
    render(<App verificationClient={{ analyze: vi.fn(), verify: vi.fn() }} sampleAdapter={{ load: vi.fn() }} />);
    expect(screen.getByRole("heading", { name: "What are we checking today?" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Check one label" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Check a batch" })).toBeInTheDocument();
    expect(screen.queryByLabelText("Brand name")).not.toBeInTheDocument();
  });

  it("runs the built-in sample through one analysis call and renders 24 checks", async () => {
    const user = userEvent.setup();
    const analyze = vi.fn(async () => analysis);
    render(<App verificationClient={{ analyze, verify: vi.fn() }} sampleAdapter={{ load: vi.fn(async () => ({ reference: {} as never, panels: [new File(["image"], "sample.jpg", { type: "image/jpeg" })] })) }} />);
    await user.click(screen.getByRole("button", { name: "Use built-in sample" }));
    await waitFor(() => expect(analyze).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole("heading", { name: "OLD TOM DISTILLERY" })).toBeInTheDocument();
    expect(screen.getAllByRole("row")).toHaveLength(29);
    expect(screen.getByText(/24 selected checks/i)).toBeInTheDocument();
  });

  it("previews, reorders, and removes single-product panels before OCR", async () => {
    const user = userEvent.setup();
    render(<App verificationClient={{ analyze: vi.fn(), verify: vi.fn() }} sampleAdapter={{ load: vi.fn() }} />);
    const front = new File(["front"], "front.jpg", { type: "image/jpeg", lastModified: 1 });
    const back = new File(["back"], "back.jpg", { type: "image/jpeg", lastModified: 2 });

    await user.upload(screen.getByLabelText("Choose label images"), [front, back]);

    expect(screen.getByAltText("front.jpg preview")).toBeInTheDocument();
    expect(screen.getByAltText("back.jpg preview")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Move front.jpg down" }));
    const rows = screen.getAllByRole("listitem");
    expect(rows[0]).toHaveTextContent("back.jpg");
    expect(rows[1]).toHaveTextContent("front.jpg");
    await user.click(screen.getByRole("button", { name: "Remove front.jpg" }));
    expect(screen.queryByAltText("front.jpg preview")).not.toBeInTheDocument();
  });
});
