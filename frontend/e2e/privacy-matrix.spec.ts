import { expect, test, type Page } from "@playwright/test";

interface BrowserState {
  cacheKeys: string[];
  indexedDatabases: string[];
  localStorageKeys: string[];
  serviceWorkerScopes: string[];
  sessionStorageKeys: string[];
}

async function browserState(page: Page): Promise<BrowserState> {
  return page.evaluate(async () => ({
    cacheKeys: await caches.keys(),
    indexedDatabases: typeof indexedDB.databases === "function"
      ? (await indexedDB.databases()).map((item) => item.name ?? "")
      : [],
    localStorageKeys: Object.keys(localStorage),
    serviceWorkerScopes: (await navigator.serviceWorker.getRegistrations()).map(
      (item) => item.scope,
    ),
    sessionStorageKeys: Object.keys(sessionStorage),
  }));
}

function expectClean(state: BrowserState) {
  expect(state).toEqual({
    cacheKeys: [],
    indexedDatabases: [],
    localStorageKeys: [],
    serviceWorkerScopes: [],
    sessionStorageKeys: [],
  });
}

test("browser storage stays content-free while server history is explicit", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "chrome", "One canonical browser lifecycle is sufficient.");
  await page.goto("/");
  expectClean(await browserState(page));

  const responsePromise = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/analyses") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Use built-in sample" }).click();
  const response = await responsePromise;
  await expect(page.getByRole("heading", { name: "OLD TOM DISTILLERY" })).toBeVisible();
  expect(response.headers()["cache-control"]).toContain("no-store");
  expectClean(await browserState(page));

  await page.reload();
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();
  expectClean(await browserState(page));

  await page.route("**/api/v1/analyses", async (route) => {
    await route.fulfill({
      status: 503,
      contentType: "application/json",
      headers: { "Cache-Control": "no-store, private" },
      body: JSON.stringify({
        requestId: "request-browser-error",
        code: "verification_capacity_busy",
        message: "The verifier is busy.",
        retryable: true,
        nextAction: "Wait and retry",
        fieldOrPanel: null,
      }),
    });
  });
  await page.getByRole("button", { name: "Use built-in sample" }).click();
  await expect(page.getByRole("heading", { name: "We could not finish this label" })).toBeVisible();
  expectClean(await browserState(page));
  await page.unroute("**/api/v1/analyses");

  await page.getByRole("button", { name: "Back home" }).click();
  await page.route("**/api/v1/analyses", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 2_000));
    await route.abort("timedout").catch(() => undefined);
  });
  await page.getByRole("button", { name: "Use built-in sample" }).click();
  await expect(page.getByRole("heading", { name: "Reading the label" })).toBeVisible();
  await page.getByRole("button", { name: "Cancel" }).click();
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();
  expectClean(await browserState(page));
});
