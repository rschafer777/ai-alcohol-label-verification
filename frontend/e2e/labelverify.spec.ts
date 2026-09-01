import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function expectNoSeriousAccessibilityViolations(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  const blocking = results.violations.filter((item) => item.impact === "serious" || item.impact === "critical");
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
}

test("sample journey is accessible, truthful, non-persistent, and reversible", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Check label details against an application" })).toBeVisible();
  await expectNoSeriousAccessibilityViolations(page);

  await page.getByRole("button", { name: "Try the built-in sample" }).click();
  await expect(page.getByLabel("Brand name")).toHaveValue("OLD TOM DISTILLERY");
  await page.getByRole("button", { name: "Verify label" }).click();

  const summary = page.getByRole("heading", { name: "Review needed" });
  await expect(summary).toBeVisible();
  await expect(summary).toBeFocused();
  await expect(page.getByRole("article")).toHaveCount(19);
  const warningWording = page.getByRole("article").filter({
    has: page.getByRole("heading", { name: "Warning wording" }),
  });
  await expect(warningWording.locator(".state-label")).toHaveText("Review");
  const physicalSize = page.getByRole("article").filter({
    has: page.getByRole("heading", { name: "Warning physical size" }),
  });
  await expect(physicalSize.locator(".state-label")).toHaveText("Not verified");
  await expect(page.getByText("Not found", { exact: true })).toHaveCount(0);
  await expectNoSeriousAccessibilityViolations(page);

  const viewer = page.locator(".image-transform");
  await page.getByRole("button", { name: "Zoom in" }).click();
  await expect(viewer).toHaveClass(/zoom-125/);
  await page.getByRole("button", { name: "Rotate" }).click();
  await expect(viewer).toHaveClass(/rotate-90/);
  await page.getByRole("button", { name: "Enhanced display" }).click();
  await expect(page.getByText("Display-only contrast enhancement. Findings do not change.")).toBeVisible();
  await page.getByRole("button", { name: "Fit and reset" }).click();
  await expect(page.getByRole("button", { name: "Original" })).toHaveAttribute("aria-pressed", "true");
  await expect(viewer).toHaveClass(/zoom-100/);
  await expect(viewer).toHaveClass(/rotate-0/);

  const browserState = await page.evaluate(async () => ({
    cacheKeys: await caches.keys(),
    localStorageKeys: Object.keys(localStorage),
    sessionStorageKeys: Object.keys(sessionStorage),
  }));
  expect(browserState).toEqual({ cacheKeys: [], localStorageKeys: [], sessionStorageKeys: [] });

  await page.getByLabel("Reviewer note (optional)").fill("UAT note");
  await page.getByRole("button", { name: "Start over" }).click();
  const dialog = page.getByRole("dialog", { name: "Start over and clear this session?" });
  await dialog.getByRole("button", { name: "Cancel" }).click();
  await expect(page.getByLabel("Reviewer note (optional)")).toHaveValue("UAT note");

  await page.getByRole("button", { name: "Start over" }).click();
  await page.getByRole("button", { name: "Confirm and clear" }).click();
  await expect(page.getByRole("heading", { name: "Check label details against an application" })).toBeVisible();
  await expect(page.getByLabel("Brand name")).toHaveValue("");
});
