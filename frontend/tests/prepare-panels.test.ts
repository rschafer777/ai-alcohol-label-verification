import { describe, expect, it, vi } from "vitest";

import { planResize, preparePanel } from "../src/api/prepare-panels";
import { createVerificationClient } from "../src/api/verification-client";
import { analysis } from "./fixtures";

const panelLimits = { pixelsPerImage: 12_000_000, fileBytes: 4_194_304 };

describe("panel preparation before upload", () => {
  it("plans a resize only when a photo exceeds the per-image limits", () => {
    expect(planResize(4000, 3000, 3_000_000, panelLimits)).toEqual({ needed: false, width: 4000, height: 3000, reason: null });

    const phone = planResize(5712, 4284, 6_000_000, panelLimits);
    expect(phone.needed).toBe(true);
    expect(phone.reason).toBe("pixels");
    expect(phone.width * phone.height).toBeLessThanOrEqual(panelLimits.pixelsPerImage);
    expect(phone.width / phone.height).toBeCloseTo(5712 / 4284, 2);

    expect(planResize(3000, 2000, 5_000_000, panelLimits)).toEqual({ needed: true, width: 3000, height: 2000, reason: "bytes" });
  });

  it("leaves a file alone when the browser cannot decode it", async () => {
    const file = new File(["x"], "photo.heic", { type: "image/heic" });
    expect(await preparePanel(file, panelLimits)).toBe(file);
  });

  it("uploads the prepared panels rather than the originals", async () => {
    const prepared = new File(["y"], "photo.jpg", { type: "image/jpeg" });
    const prepare = vi.fn(async () => [prepared]);
    const fetcher = vi.fn<(input: RequestInfo | URL, init?: RequestInit) => Promise<Response>>(async () => new Response(JSON.stringify(analysis), { status: 200, headers: { "content-type": "application/json" } }));
    const client = createVerificationClient(fetcher as unknown as typeof fetch, "fetch", prepare);

    await client.analyze({ panels: [new File(["x"], "photo.png", { type: "image/png" })], signal: new AbortController().signal });

    expect(prepare).toHaveBeenCalledTimes(1);
    const body = fetcher.mock.calls[0]![1]!.body as FormData;
    expect(body.getAll("panels")).toEqual([prepared]);
  });
});
