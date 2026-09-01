import { describe, expect, it, vi } from "vitest";

import { createVerificationClient } from "../src/api/verification-client";
import { completeResult, sampleFile, sampleReference } from "./fixtures";

describe("verification multipart transport", () => {
  it("sends reference JSON as a text field and panels as file fields", async () => {
    const capturedBodies: FormData[] = [];
    const fetcher = vi.fn(async (_input: RequestInfo | URL, init?: RequestInit) => {
      if (!(init?.body instanceof FormData)) throw new Error("Expected multipart FormData.");
      capturedBodies.push(init.body);
      return new Response(JSON.stringify(completeResult()), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    });
    const client = createVerificationClient(fetcher);
    const panel = sampleFile();

    await client.verify({
      reference: sampleReference,
      panels: [panel],
      signal: new AbortController().signal,
    });

    const capturedBody = capturedBodies[0];
    if (!capturedBody) throw new Error("Multipart body was not captured.");
    const referencePart = capturedBody.get("reference");
    expect(typeof referencePart).toBe("string");
    expect(referencePart).toBe(JSON.stringify(sampleReference));
    expect(referencePart).not.toBeInstanceOf(File);

    const panelPart = capturedBody.get("panels");
    expect(panelPart).toBeInstanceOf(File);
    expect((panelPart as File).name).toBe(panel.name);
  });
});
