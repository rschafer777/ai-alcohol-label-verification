import { copyFile, mkdir, mkdtemp, readFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const PROJECT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");

test("browser confirms and completes 300 conservatively grouped products", async ({ page }, testInfo) => {
  test.skip(process.env.LABELVERIFY_RUN_BATCH_CAPACITY !== "1", "Run only for capacity evidence.");
  test.skip(testInfo.project.name !== "chrome", "One canonical Chrome capacity run is sufficient.");
  test.setTimeout(300_000);

  await page.goto("/");
  const sampleResponsePromise = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/analyses") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Use built-in sample" }).click();
  const samplePayload = await (await sampleResponsePromise).json();
  await page.getByRole("button", { name: "Start over" }).click();

  const temporaryRoot = await mkdtemp(join(tmpdir(), "labelverify-browser-batch-"));
  try {
    const source = join(PROJECT_ROOT, "fixtures/development/cases/D001/panels/panel-1.png");
    for (let index = 1; index <= 300; index += 1) {
      const target = join(temporaryRoot, `product-${String(index).padStart(3, "0")}`, "front.png");
      await mkdir(dirname(target), { recursive: true });
      await copyFile(source, target);
    }

    await page.getByRole("button", { name: /^Check a batch/ }).first().click();
    await page.locator('input[type="file"][webkitdirectory]').setInputFiles(temporaryRoot);
    await expect(page.getByRole("heading", { name: "Confirm how the images group into products" })).toBeVisible();
    const suggestedProducts = page.getByText("Suggested products").locator("..");
    await expect(suggestedProducts.getByText("300", { exact: true })).toBeVisible();
    await page.getByRole("button", { name: "Confirm all ready" }).click();

    let sequence = 0;
    await page.route("**/api/v1/analyses", async (route) => {
      sequence += 1;
      const payload = {
        ...samplePayload,
        requestId: `batch-${sequence}`,
        verification: {
          ...samplePayload.verification,
          requestId: `batch-${sequence}`,
          historyId: `history-${sequence}`,
        },
      };
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(payload) });
    });

    await page.getByRole("button", { name: "Run 300 products" }).click();
    await expect(page.getByText("300 products | 300 images")).toBeVisible();
    await expect(page.locator("progress")).toHaveAttribute("value", "300", { timeout: 180_000 });
    expect(sequence).toBe(300);

    const csvEvent = page.waitForEvent("download");
    await page.getByRole("button", { name: "CSV" }).click();
    const csvPath = join(temporaryRoot, "results.csv");
    await (await csvEvent).saveAs(csvPath);
    expect((await readFile(csvPath, "utf-8")).trimEnd().split("\r\n")).toHaveLength(301);

    const jsonEvent = page.waitForEvent("download");
    await page.getByRole("button", { name: "Detailed JSON" }).click();
    const jsonPath = join(temporaryRoot, "details.json");
    await (await jsonEvent).saveAs(jsonPath);
    expect(JSON.parse(await readFile(jsonPath, "utf-8"))).toHaveLength(300);
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true, maxRetries: 10, retryDelay: 500 });
  }
});
