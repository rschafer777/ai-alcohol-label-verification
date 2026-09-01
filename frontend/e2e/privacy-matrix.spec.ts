import { mkdir, writeFile } from "node:fs/promises";

import { expect, test, type BrowserContext, type Page } from "@playwright/test";

interface BrowserState {
  cacheKeys: string[];
  historyState: unknown;
  indexedDatabases: string[];
  localStorageKeys: string[];
  serviceWorkerScopes: string[];
  sessionStorageKeys: string[];
}

async function browserState(page: Page): Promise<BrowserState> {
  return page.evaluate(async () => ({
    cacheKeys: await caches.keys(),
    historyState: history.state,
    indexedDatabases: typeof indexedDB.databases === "function"
      ? (await indexedDB.databases()).map((item) => item.name ?? "")
      : [],
    localStorageKeys: Object.keys(localStorage),
    serviceWorkerScopes: (await navigator.serviceWorker.getRegistrations()).map((item) => item.scope),
    sessionStorageKeys: Object.keys(sessionStorage),
  }));
}

function expectClean(state: BrowserState) {
  expect(state).toEqual({
    cacheKeys: [],
    historyState: null,
    indexedDatabases: [],
    localStorageKeys: [],
    serviceWorkerScopes: [],
    sessionStorageKeys: [],
  });
}

async function loadSample(page: Page) {
  await page.getByRole("button", { name: "Try the built-in sample" }).click();
  await expect(page.getByLabel("Brand name")).toHaveValue("OLD TOM DISTILLERY");
}

async function freshPage(context: BrowserContext): Promise<Page> {
  const page = await context.newPage();
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Check label details against an application" })).toBeVisible();
  return page;
}

test("complete browser privacy lifecycle remains content-free", async ({ page, context }, testInfo) => {
  test.skip(testInfo.project.name !== "chrome", "One canonical Chrome privacy matrix is retained.");
  const observed: Record<string, unknown> = {};

  const documentResponse = await page.goto("/");
  expect(documentResponse?.ok()).toBe(true);
  observed.firstLoad = await browserState(page);
  expectClean(observed.firstLoad as BrowserState);

  await loadSample(page);
  const verificationResponsePromise = page.waitForResponse((response) =>
    response.url().endsWith("/api/v1/verifications") && response.request().method() === "POST"
  );
  await page.getByRole("button", { name: "Verify label" }).click();
  const verificationResponse = await verificationResponsePromise;
  await expect(page.getByRole("heading", { name: "Review needed" })).toBeVisible();
  expect(verificationResponse.headers()["cache-control"]).toContain("no-store");
  await page.getByLabel("Reviewer note (optional)").fill("privacy matrix canary note");
  observed.success = await browserState(page);
  expectClean(observed.success as BrowserState);

  await page.getByRole("button", { name: "Start over" }).click();
  await page.getByRole("button", { name: "Confirm and clear" }).click();
  observed.startOver = await browserState(page);
  expectClean(observed.startOver as BrowserState);

  await loadSample(page);
  await page.reload();
  await expect(page.getByLabel("Brand name")).toHaveValue("");
  observed.refresh = await browserState(page);
  expectClean(observed.refresh as BrowserState);

  await loadSample(page);
  await page.close();
  page = await freshPage(context);
  await expect(page.getByLabel("Brand name")).toHaveValue("");
  observed.closeReopen = await browserState(page);
  expectClean(observed.closeReopen as BrowserState);

  await page.route("**/api/v1/verifications", async (route) => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      headers: { "Cache-Control": "no-store, private" },
      body: JSON.stringify({
        requestId: "request-privacy-error",
        code: "verification_capacity_busy",
        message: "The verifier is busy.",
        retryable: true,
        nextAction: "Untrusted action",
        fieldOrPanel: null,
      }),
    });
  });
  await loadSample(page);
  await page.getByRole("button", { name: "Verify label" }).click();
  await expect(page.getByRole("heading", { name: "The verifier is busy." })).toBeVisible();
  observed.error = await browserState(page);
  expectClean(observed.error as BrowserState);
  await page.unroute("**/api/v1/verifications");

  await page.route("**/api/v1/verifications", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 1_500));
    await route.abort("timedout").catch(() => undefined);
  });
  const cancelStarted = Date.now();
  await page.getByRole("button", { name: "Verify label" }).click();
  await page.getByRole("button", { name: "Cancel verification" }).click();
  await expect(page.getByRole("heading", { name: "Verification cancelled" })).toBeVisible();
  const cancelElapsedMs = Date.now() - cancelStarted;
  expect(cancelElapsedMs).toBeLessThan(1_000);
  expect(page.getByLabel("Brand name")).toHaveValue("OLD TOM DISTILLERY");
  observed.cancel = await browserState(page);
  observed.cancelElapsedMs = cancelElapsedMs;
  expectClean(observed.cancel as BrowserState);

  const evidence = {
    schemaVersion: "1.0.0",
    testId: "T-039",
    assertionId: "T-039-A-FULL-BROWSER-PRIVACY-MATRIX",
    project: testInfo.project.name,
    verificationCacheControl: verificationResponse.headers()["cache-control"] ?? null,
    observed,
    pass: true,
  };
  const output = new URL("../../docs/08-validation/evidence/browser-privacy-matrix.json", import.meta.url);
  await mkdir(new URL("../../docs/08-validation/evidence/", import.meta.url), { recursive: true });
  await writeFile(output, `${JSON.stringify(evidence, null, 2)}\n`, "utf-8");
});
