import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/app/App";
import { analysis } from "./fixtures";

const emptyPage = { items: [], total: 0, cap: 500, offset: 0, pageSize: 3, hasMore: false };
const historyClient = { meta: vi.fn(async () => null), list: vi.fn(async () => emptyPage), get: vi.fn(async () => null), setDisposition: vi.fn(async () => true), remove: vi.fn(async () => true), clear: vi.fn(async () => 0) };

describe("LabelVerify application", () => {
  beforeEach(() => {
    window.localStorage.setItem("lv.firstRunDismissed", "1");
    window.location.hash = "";
  });

  it("opens with the TTB bar, notice band, tray, and the two doors", () => {
    render(<App historyClient={historyClient} sampleAdapter={{ load: vi.fn() }} verificationClient={{ analyze: vi.fn(), verify: vi.fn() }} />);
    expect(screen.getByRole("heading", { name: "What are we checking today?" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Check one label" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Check a batch" })).toBeInTheDocument();
    expect(screen.getByText("Unofficial prototype")).toBeInTheDocument();
    expect(screen.getByText("Synthetic or sanitized data only")).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Primary" })).toBeInTheDocument();
    expect(screen.queryByLabelText("Brand name")).not.toBeInTheDocument();
  });

  it("shows the first-run tips once and remembers the dismissal", async () => {
    window.localStorage.removeItem("lv.firstRunDismissed");
    const user = userEvent.setup();
    render(<App historyClient={historyClient} sampleAdapter={{ load: vi.fn() }} verificationClient={{ analyze: vi.fn(), verify: vi.fn() }} />);
    expect(screen.getByRole("dialog", { name: "First-time tips" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Don't show again" }));
    expect(screen.queryByRole("dialog", { name: "First-time tips" })).not.toBeInTheDocument();
    expect(window.localStorage.getItem("lv.firstRunDismissed")).toBe("1");
  });

  it("runs the built-in sample through one analysis call and lands in the review workspace", async () => {
    const user = userEvent.setup();
    const analyze = vi.fn(async () => analysis);
    render(<App historyClient={historyClient} sampleAdapter={{ load: vi.fn(async () => ({ reference: {} as never, panels: [new File(["image"], "sample.jpg", { type: "image/jpeg" })] })) }} verificationClient={{ analyze, verify: vi.fn() }} />);
    await user.click(screen.getByRole("button", { name: "Use the built-in sample" }));
    await waitFor(() => expect(analyze).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole("heading", { name: "OLD TOM DISTILLERY" })).toBeInTheDocument();
    expect(screen.getByText(/24 checks · distilled spirits profile/)).toBeInTheDocument();
    expect(screen.getByText("Your disposition")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Approve/ }));
    await user.click(screen.getByRole("button", { name: /Save & check another/ }));
    await waitFor(() => expect(historyClient.setDisposition).toHaveBeenCalledWith("hist_test", "approved", ""));
    expect(await screen.findByRole("heading", { name: "What are we checking today?" })).toBeInTheDocument();
  });

  it("previews selected images with a remove control before reading", async () => {
    const user = userEvent.setup();
    render(<App historyClient={historyClient} sampleAdapter={{ load: vi.fn() }} verificationClient={{ analyze: vi.fn(), verify: vi.fn() }} />);
    const front = new File(["front"], "front.jpg", { type: "image/jpeg", lastModified: 1 });
    const back = new File(["back"], "back.jpg", { type: "image/jpeg", lastModified: 2 });
    await user.upload(screen.getByLabelText("Choose label images"), [front, back]);
    expect(screen.getByAltText("front.jpg preview")).toBeInTheDocument();
    expect(screen.getByAltText("back.jpg preview")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Read & check label" })).toBeEnabled();
    await user.click(screen.getByRole("button", { name: "Remove front.jpg" }));
    expect(screen.queryByAltText("front.jpg preview")).not.toBeInTheDocument();
  });

  it("navigates to History from the tray and shows the drawer placeholder", async () => {
    const user = userEvent.setup();
    render(<App historyClient={historyClient} sampleAdapter={{ load: vi.fn() }} verificationClient={{ analyze: vi.fn(), verify: vi.fn() }} />);
    await user.click(screen.getByRole("button", { name: /^History/ }));
    expect(await screen.findByRole("heading", { name: "Completed checks" })).toBeInTheDocument();
    expect(screen.getByText("Select a result")).toBeInTheDocument();
  });
});
