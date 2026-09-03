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

// The only browser storage the app may hold is two content-free UI preferences
// (tray open/closed, first-run tips dismissed). Label images, results and notes never land here.
const ALLOWED_LOCAL_KEYS = ["lv.firstRunDismissed", "lv.trayOpen"];

function expectClean(state: BrowserState) {
  expect(state.localStorageKeys.filter((key) => !ALLOWED_LOCAL_KEYS.includes(key))).toEqual([]);
  expect({ ...state, localStorageKeys: [] }).toEqual({
    cacheKeys: [],
    indexedDatabases: [],
    localStorageKeys: [],
    serviceWorkerScopes: [],
    sessionStorageKeys: [],
  });
}

async function dismissTips(page: Page) {
  const button = page.getByRole("button", { name: "Don't show again" });
  if (await button.isVisible().catch(() => false)) await button.click();
}

test("browser storage stays content-free while server history is explicit", async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== "chrome", "One canonical browser lifecycle is sufficient.");
  await page.goto("/");
  expectClean(await browserState(page));
  await dismissTips(page);
  expect((await browserState(page)).localStorageKeys).toEqual(["lv.firstRunDismissed"]);
  expect(await page.evaluate(() => localStorage.getItem("lv.firstRunDismissed"))).toBe("1");

  const responsePromise = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/analyses") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Use the built-in sample" }).click();
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
  await page.getByRole("button", { name: "Use the built-in sample" }).click();
  await expect(page.getByText("Another label is being read")).toBeVisible();
  expectClean(await browserState(page));
  await page.unroute("**/api/v1/analyses");

  await page.getByRole("button", { name: "Cancel" }).click();
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();
  await page.route("**/api/v1/analyses", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 2_000));
    await route.abort("timedout").catch(() => undefined);
  });
  await page.getByRole("button", { name: "Use the built-in sample" }).click();
  await expect(page.getByRole("heading", { name: "Reading the label" })).toBeVisible();
  await page.getByRole("button", { name: "Cancel" }).click();
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();
  expectClean(await browserState(page));
});
