import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { VerificationClientError } from "../src/api/verification-client";
import { App } from "../src/app/App";
import type { SampleAdapter, VerificationClient, VerificationRequest } from "../src/contracts/types";
import type { VerificationResult } from "../src/api/generated-contract";
import { completeResult, loadedSample, sampleFile, sampleReference } from "./fixtures";

function sampleAdapter(): SampleAdapter {
  return { load: vi.fn(async () => loadedSample()) };
}

function successfulClient(): VerificationClient {
  return { verify: vi.fn(async () => completeResult()) };
}

async function loadBuiltInSample(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole("button", { name: "Try the built-in sample" }));
  await screen.findByDisplayValue("OLD TOM DISTILLERY");
}

describe("LabelVerify intake and result journey", () => {
  it("shows an honest, simple first load and focuses the first invalid field", async () => {
    const user = userEvent.setup();
    render(<App sampleAdapter={sampleAdapter()} verificationClient={successfulClient()} />);

    expect(screen.getAllByText("Unofficial prototype").length).toBeGreaterThan(0);
    expect(screen.getByText(/Use synthetic or sanitized data only/)).toBeInTheDocument();
    expect(screen.queryByText(/TTB approved/i)).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Verify label" }));
    const brand = screen.getByLabelText("Brand name");
    await waitFor(() => expect(brand).toHaveFocus());
    expect(screen.getByText("Brand name is required.")).toBeInTheDocument();
    expect(screen.getByText("Add 1 to 6 label panels.")).toBeInTheDocument();
    expect(screen.getByLabelText("Label panel images")).toHaveAttribute("tabindex", "-1");
  });

  it("shows and requires country only for imported products without losing the current value", async () => {
    const user = userEvent.setup();
    render(<App sampleAdapter={sampleAdapter()} verificationClient={successfulClient()} />);
    const imported = screen.getByRole("checkbox", { name: "This product is imported" });

    expect(screen.queryByLabelText("Country of origin")).not.toBeInTheDocument();
    await user.click(imported);
    const country = screen.getByLabelText("Country of origin");
    await user.type(country, "Canada");
    await user.click(imported);
    expect(screen.queryByLabelText("Country of origin")).not.toBeInTheDocument();
    await user.click(imported);
    expect(screen.getByLabelText("Country of origin")).toHaveValue("Canada");
  });

  it("loads the typed sample, renders all 19 rows, focuses evidence, and guards reset", async () => {
    const user = userEvent.setup();
    render(<App sampleAdapter={sampleAdapter()} verificationClient={successfulClient()} />);
    await loadBuiltInSample(user);

    expect(screen.getByText("1 of 6 added")).toBeInTheDocument();
    expect(screen.getByText(/Sample loaded/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Verify label" }));

    const summary = await screen.findByRole("heading", { name: "No differences found in checked fields" });
    expect(summary).toHaveFocus();
    expect(screen.getByText("19 applicable")).toBeInTheDocument();
    expect(screen.getByText("Focused evidence")).toBeInTheDocument();
    expect(screen.getByText("OLD TOM DISTILLERY", { selector: ".selected-evidence span" })).toBeInTheDocument();
    expect(screen.getByText(/not an approval score/)).toBeInTheDocument();

    await user.type(screen.getByLabelText("Reviewer note (optional)"), "Needs a second look.");
    await user.click(screen.getByRole("button", { name: "Start over" }));
    const dialog = screen.getByRole("dialog", { name: "Start over and clear this session?" });
    await user.click(within(dialog).getByRole("button", { name: "Cancel" }));
    expect(screen.getByLabelText("Reviewer note (optional)")).toHaveValue("Needs a second look.");

    await user.click(screen.getByRole("button", { name: "Start over" }));
    await user.click(screen.getByRole("button", { name: "Confirm and clear" }));
    expect(await screen.findByRole("heading", { name: "Check label details against an application" })).toBeInTheDocument();
    expect(screen.getByLabelText("Brand name")).toHaveValue("");
  });

  it("cancels within the browser flow and preserves editable sample work", async () => {
    const user = userEvent.setup();
    const pendingClient: VerificationClient = {
      verify: vi.fn(({ signal }: VerificationRequest): Promise<VerificationResult> => new Promise((_, reject) => {
        signal.addEventListener("abort", () => reject(new DOMException("Cancelled", "AbortError")), { once: true });
      })),
    };
    render(<App sampleAdapter={sampleAdapter()} verificationClient={pendingClient} />);
    await loadBuiltInSample(user);
    await user.click(screen.getByRole("button", { name: "Verify label" }));
    await user.click(await screen.findByRole("button", { name: "Cancel verification" }));

    expect(await screen.findByRole("heading", { name: "Verification cancelled" })).toBeInTheDocument();
    expect(screen.getByLabelText("Brand name")).toHaveValue("OLD TOM DISTILLERY");
    expect(screen.getByText("1 of 6 added")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Verify label" })).toBeEnabled();
  });

  it("preserves work across a retryable error and succeeds without re-entry", async () => {
    const user = userEvent.setup();
    const verify = vi
      .fn<VerificationClient["verify"]>()
      .mockRejectedValueOnce(new VerificationClientError({
        requestId: "request-error-2",
        code: "verification_capacity_busy",
        message: "The verifier is busy.",
        retryable: true,
        nextAction: "Retry shortly",
        fieldOrPanel: null,
      }))
      .mockResolvedValueOnce(completeResult());

    render(<App sampleAdapter={sampleAdapter()} verificationClient={{ verify }} />);
    await loadBuiltInSample(user);
    await user.click(screen.getByRole("button", { name: "Verify label" }));
    expect(await screen.findByRole("heading", { name: "The verifier is busy." })).toBeInTheDocument();
    expect(screen.getByLabelText("Brand name")).toHaveValue("OLD TOM DISTILLERY");
    await user.click(screen.getByRole("button", { name: "Retry verification" }));
    expect(await screen.findByRole("heading", { name: "No differences found in checked fields" })).toBeInTheDocument();
    expect(verify).toHaveBeenCalledTimes(2);
  });

  it("supports six panels, reordering, removal, replacement, and ordered submission", async () => {
    const user = userEvent.setup();
    const initialPanels = Array.from({ length: 6 }, (_, index) => sampleFile(`panel-${index + 1}.png`));
    const adapter: SampleAdapter = { load: vi.fn(async () => ({ reference: sampleReference, panels: initialPanels })) };
    const verify = vi.fn(async (request: VerificationRequest): Promise<VerificationResult> => {
      expect(request.panels).toHaveLength(6);
      return completeResult();
    });
    render(<App sampleAdapter={adapter} verificationClient={{ verify }} />);
    await loadBuiltInSample(user);
    expect(screen.getByText("6 of 6 added")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Move panel-6.png up" }));
    const list = screen.getByRole("list", { name: "Selected label panels" });
    expect(within(list).getAllByRole("listitem")[4]).toHaveTextContent("panel-6.png");
    await user.click(screen.getByRole("button", { name: "Remove panel-5.png" }));
    expect(screen.getByText("5 of 6 added")).toBeInTheDocument();

    const replacement = sampleFile("replacement.png");
    const input = document.getElementById("field-panels");
    if (!(input instanceof HTMLInputElement)) throw new Error("Panel input is missing.");
    await user.upload(input, replacement);
    expect(screen.getByText("6 of 6 added")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Verify label" }));
    await screen.findByRole("heading", { name: "No differences found in checked fields" });
    const request = verify.mock.calls[0]?.[0];
    expect(request?.panels.map((file: File) => file.name)).toEqual([
      "panel-1.png",
      "panel-2.png",
      "panel-3.png",
      "panel-4.png",
      "panel-6.png",
      "replacement.png",
    ]);
  });

  it("renders every material ambiguity as a separately named evidence action", async () => {
    const user = userEvent.setup();
    const result = completeResult();
    result.summary = "Review needed";
    result.evidence.push(
      {
        evidenceId: "ev_country_panel-1_01",
        panelId: "panel-1",
        polygonOriginalPixels: [{ x: 8, y: 30 }, { x: 38, y: 30 }, { x: 38, y: 40 }, { x: 8, y: 40 }],
        sourceView: "original",
        transformId: "original",
        textSnippet: "PRODUCT OF CANADA",
        confidenceProvenance: { source: "rapidocr", signal: 0.8, calibratedProbability: false },
      },
      {
        evidenceId: "ev_country_panel-1_02",
        panelId: "panel-1",
        polygonOriginalPixels: [{ x: 8, y: 50 }, { x: 30, y: 50 }, { x: 30, y: 60 }, { x: 8, y: 60 }],
        sourceView: "original",
        transformId: "original",
        textSnippet: "USA",
        confidenceProvenance: { source: "rapidocr", signal: 0.72, calibratedProbability: false },
      },
    );
    const country = result.checks.find((check) => check.checkId === "country");
    if (!country) throw new Error("Country fixture is missing.");
    country.state = "Review";
    country.reasonCode = "ambiguous_candidates";
    country.reasonText = "Two plausible countries were found. Human review is required.";
    country.evidenceRef = null;
    country.alternatives = [
      { value: "CANADA", evidenceRef: "ev_country_panel-1_01" },
      { value: "USA", evidenceRef: "ev_country_panel-1_02" },
    ];

    render(<App sampleAdapter={sampleAdapter()} verificationClient={{ verify: vi.fn(async () => result) }} />);
    await loadBuiltInSample(user);
    await user.click(screen.getByRole("button", { name: "Verify label" }));
    await screen.findByRole("heading", { name: "Review needed" });
    const canada = screen.getByRole("button", { name: "Show CANADA" });
    const usa = screen.getByRole("button", { name: "Show USA" });
    expect(canada).toBeInTheDocument();
    expect(usa).toBeInTheDocument();
    await user.click(canada);
    expect(screen.getByText("PRODUCT OF CANADA", { selector: ".selected-evidence span" })).toBeInTheDocument();
    expect(canada).toHaveAttribute("aria-pressed", "true");
    expect(usa).toHaveAttribute("aria-pressed", "false");
  });

  it("uses truthful fallback text when a rule check has no scalar display value", async () => {
    const user = userEvent.setup();
    const result = completeResult();
    const warning = result.checks.find((check) => check.checkId === "warning_wording");
    if (!warning) throw new Error("Warning wording fixture is missing.");
    warning.referenceDisplay = null;
    warning.observedDisplay = null;

    render(<App sampleAdapter={sampleAdapter()} verificationClient={{ verify: vi.fn(async () => result) }} />);
    await loadBuiltInSample(user);
    await user.click(screen.getByRole("button", { name: "Verify label" }));
    await screen.findByRole("heading", { name: "No differences found in checked fields" });

    const row = screen.getByRole("article", { name: "Warning Wording" });
    expect(within(row).getByText("Rule-based requirement")).toBeInTheDocument();
    expect(within(row).getByText("Condition satisfied")).toBeInTheDocument();
    expect(within(row).queryByText("Not found")).not.toBeInTheDocument();
  });
});
