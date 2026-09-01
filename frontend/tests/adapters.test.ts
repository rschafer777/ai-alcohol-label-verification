import { describe, expect, it, vi } from "vitest";

import { createVerificationClient, VerificationClientError } from "../src/api/verification-client";
import { createSampleAdapter } from "../src/features/intake/sample-adapter";
import { completeResult, sampleFile, sampleReference } from "./fixtures";

function request(signal = new AbortController().signal) {
  return { reference: sampleReference, panels: [sampleFile()], signal };
}

describe("verification client failures", () => {
  it("converts a network failure to a retryable public error", async () => {
    const client = createVerificationClient(vi.fn(async () => { throw new Error("offline"); }) as typeof fetch);
    await expect(client.verify(request())).rejects.toMatchObject({
      detail: { code: "network_unavailable", retryable: true },
    });
  });

  it("preserves an abort from the caller", async () => {
    const controller = new AbortController();
    controller.abort();
    const abort = new DOMException("Cancelled", "AbortError");
    const client = createVerificationClient(vi.fn(async () => { throw abort; }) as typeof fetch);
    await expect(client.verify(request(controller.signal))).rejects.toBe(abort);
  });

  it("handles unreadable JSON, registered errors, and invalid success contracts", async () => {
    const unreadable = createVerificationClient(vi.fn(async () => new Response("not-json", { status: 200 })) as typeof fetch);
    await expect(unreadable.verify(request())).rejects.toMatchObject({ detail: { code: "internal_error" } });

    const rejected = createVerificationClient(vi.fn(async () => new Response(JSON.stringify({
      requestId: "request-bad-image",
      code: "invalid_image",
      message: "Replace it.",
      retryable: true,
      nextAction: "untrusted",
      fieldOrPanel: "panel-1",
    }), { status: 415, headers: { "Content-Type": "application/json" } })) as typeof fetch);
    await expect(rejected.verify(request())).rejects.toMatchObject({
      detail: { code: "invalid_image", retryable: false, fieldOrPanel: "panel-1" },
    });

    const invalidError = createVerificationClient(vi.fn(async () => new Response(JSON.stringify({ no: "contract" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    })) as typeof fetch);
    await expect(invalidError.verify(request())).rejects.toMatchObject({ detail: { code: "internal_error" } });

    const invalidResult = completeResult();
    invalidResult.checks = invalidResult.checks.slice(1);
    const invalidSuccess = createVerificationClient(vi.fn(async () => new Response(JSON.stringify(invalidResult), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    })) as typeof fetch);
    await expect(invalidSuccess.verify(request())).rejects.toBeInstanceOf(VerificationClientError);
    await expect(invalidSuccess.verify(request())).rejects.toMatchObject({
      detail: { code: "response_contract_invalid", requestId: "request-test-1" },
    });
  });
});

describe("built-in sample adapter", () => {
  it("loads a typed manifest and all panels", async () => {
    const fetcher = vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).includes("samples/distilled")) {
        return new Response(JSON.stringify({
          reference: sampleReference,
          panels: [
            { panelId: "panel-1", label: "Front", fileName: "front.png", mimeType: "image/png", url: "/front.png" },
            { panelId: "panel-2", label: "Back", fileName: "back.jpg", mimeType: "image/jpeg", url: "/back.jpg" },
          ],
        }), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      return new Response(new Blob([new Uint8Array([1, 2, 3])]), { status: 200 });
    });
    const loaded = await createSampleAdapter(fetcher as typeof fetch).load();
    expect(loaded.reference.brandName).toBe("OLD TOM DISTILLERY");
    expect(loaded.panels.map((panel) => [panel.name, panel.type])).toEqual([
      ["front.png", "image/png"],
      ["back.jpg", "image/jpeg"],
    ]);
  });

  it("rejects unavailable or malformed sample resources", async () => {
    const unavailable = createSampleAdapter(vi.fn(async () => new Response(null, { status: 503 })) as typeof fetch);
    await expect(unavailable.load()).rejects.toThrow("built-in sample is unavailable");

    const malformed = createSampleAdapter(vi.fn(async () => new Response(JSON.stringify({ bad: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    })) as typeof fetch);
    await expect(malformed.load()).rejects.toThrow();

    const panelUnavailable = createSampleAdapter(vi.fn(async (input: RequestInfo | URL) => {
      if (String(input).includes("samples/distilled")) {
        return new Response(JSON.stringify({
          reference: sampleReference,
          panels: [{ panelId: "panel-1", label: "Front", fileName: "front.png", mimeType: "image/png", url: "/front.png" }],
        }), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      return new Response(null, { status: 404 });
    }) as typeof fetch);
    await expect(panelUnavailable.load()).rejects.toThrow("sample panel is unavailable");
  });
});
