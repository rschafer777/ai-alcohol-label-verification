import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/app/App";
import type { VerificationClient, VerificationRequest } from "../src/contracts/types";
import type { VerificationResult } from "../src/api/generated-contract";
import { completeResult, loadedSample } from "./fixtures";

function adapter() {
  return { load: vi.fn(async () => loadedSample()) };
}

async function loadSample(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole("button", { name: "Try the built-in sample" }));
  await screen.findByDisplayValue("OLD TOM DISTILLERY");
}

afterEach(() => {
  vi.useRealTimers();
});

describe("T-041 browser phase and terminal matrix", () => {
  it("terminates client validation locally without starting transport", async () => {
    const user = userEvent.setup();
    const verify = vi.fn<VerificationClient["verify"]>();
    render(<App sampleAdapter={adapter()} verificationClient={{ verify }} />);

    const started = performance.now();
    await user.click(screen.getByRole("button", { name: "Verify label" }));
    await waitFor(() => expect(screen.getByLabelText("Brand name")).toHaveFocus());

    expect(performance.now() - started).toBeLessThan(1_000);
    expect(verify).not.toHaveBeenCalled();
    expect(screen.getByText("Brand name is required.")).toHaveAttribute("role", "alert");
  });

  it("applies the 35 second browser terminal deadline to a stalled request", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime });
    const stalledClient: VerificationClient = {
      verify: vi.fn(({ signal }: VerificationRequest): Promise<VerificationResult> => new Promise((_, reject) => {
        signal.addEventListener("abort", () => reject(new DOMException("Deadline", "AbortError")), { once: true });
      })),
    };
    render(<App sampleAdapter={adapter()} verificationClient={stalledClient} />);
    await loadSample(user);
    await user.click(screen.getByRole("button", { name: "Verify label" }));
    expect(screen.getByRole("heading", { name: "Uploading label panels" })).toBeInTheDocument();

    await act(async () => vi.advanceTimersByTime(100));
    expect(screen.getByRole("heading", { name: "Reading and checking the label" })).toBeInTheDocument();
    await act(async () => vi.advanceTimersByTime(35_000));

    expect(screen.getByRole("heading", { name: "Verification did not finish within 35 seconds." })).toBeInTheDocument();
    expect(screen.getByLabelText("Brand name")).toHaveValue("OLD TOM DISTILLERY");
    expect(screen.queryByText("No differences found in checked fields")).not.toBeInTheDocument();
  });

  it("cancels in under one second and ignores a late result", async () => {
    const user = userEvent.setup();
    let resolveResult: ((value: VerificationResult) => void) | undefined;
    const delayedClient: VerificationClient = {
      verify: vi.fn(() => new Promise<VerificationResult>((resolve) => { resolveResult = resolve; })),
    };
    render(<App sampleAdapter={adapter()} verificationClient={delayedClient} />);
    await loadSample(user);
    await user.click(screen.getByRole("button", { name: "Verify label" }));

    const started = performance.now();
    await user.click(screen.getByRole("button", { name: "Cancel verification" }));
    expect(performance.now() - started).toBeLessThan(1_000);
    expect(screen.getByRole("heading", { name: "Verification cancelled" })).toBeInTheDocument();
    expect(screen.getByText("Verification cancelled. Your form and selected files are unchanged.")).toHaveAttribute("aria-live", "polite");

    await act(async () => resolveResult?.(completeResult()));
    expect(screen.getByRole("heading", { name: "Verification cancelled" })).toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: "No differences found in checked fields" })).not.toBeInTheDocument();
    expect(screen.getByLabelText("Brand name")).toHaveValue("OLD TOM DISTILLERY");
  });

  it("renders and announces a complete response with managed focus", async () => {
    const user = userEvent.setup();
    render(<App sampleAdapter={adapter()} verificationClient={{ verify: vi.fn(async () => completeResult()) }} />);
    await loadSample(user);
    await user.click(screen.getByRole("button", { name: "Verify label" }));

    const summary = await screen.findByRole("heading", { name: "No differences found in checked fields" });
    expect(summary).toHaveFocus();
    expect(summary.closest("section")).toHaveAttribute("aria-live", "polite");
    expect(screen.getAllByRole("article")).toHaveLength(19);
  });
});
