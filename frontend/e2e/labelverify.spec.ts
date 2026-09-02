import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

async function expectNoSeriousAccessibilityViolations(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  const blocking = results.violations.filter(
    (item) => item.impact === "serious" || item.impact === "critical",
  );
  expect(blocking, JSON.stringify(blocking, null, 2)).toEqual([]);
}

test("label-first sample supports evidence, warning review, disposition, and history", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Check one label" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Check a batch" })).toBeVisible();
  await expect(page.getByLabel("Brand name")).toHaveCount(0);
  await expectNoSeriousAccessibilityViolations(page);

  const analysisResponsePromise = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/analyses") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Use built-in sample" }).click();
  const analysisResponse = await analysisResponsePromise;
  expect(analysisResponse.ok()).toBe(true);
  expect(analysisResponse.headers()["cache-control"]).toContain("no-store");

  await expect(page.getByRole("heading", { name: "OLD TOM DISTILLERY" })).toBeVisible();
  await expect(page.getByText(/24 selected checks/)).toBeVisible();
  await expect(page.getByRole("row")).toHaveCount(29);
  await expectNoSeriousAccessibilityViolations(page);

  await page.getByRole("button", { name: "Show", exact: true }).first().click();
  await expect(page.getByText(/^Read:/)).toBeVisible();
  await page.getByRole("button", { name: "Cards" }).click();
  await expect(page.locator("article.check-card")).toHaveCount(24);
  await page.getByRole("button", { name: "Image first" }).click();
  await expect(page.locator(".check-rail button")).toHaveCount(24);

  await page.getByRole("button", { name: "Inspect warning" }).click();
  await expect(page.getByRole("heading", { name: "Government warning statement" })).toBeVisible();
  await expect(page.getByRole("row")).toHaveCount(11);
  await page.getByRole("button", { name: "Continue review" }).click();

  await page.keyboard.press("a");
  await expect(page.getByRole("button", { name: "Approve A" })).toHaveAttribute("aria-pressed", "true");
  await page.getByLabel("Reviewer note").fill("Browser UAT sample");
  await page.getByRole("button", { name: "Save and check another" }).click();
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();

  await page.getByRole("button", { name: /^History/ }).click();
  await expect(page.getByRole("heading", { name: "Completed checks" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Open" }).first()).toBeVisible();
  await page.getByRole("button", { name: "Open" }).first().click();
  await expect(page.getByText("Stored result")).toBeVisible();
  await expect(page.getByRole("button", { name: "Show on label" }).first()).toBeVisible();
  await page.getByRole("button", { name: "Show on label" }).first().click();
  await expect(page.getByRole("img", { name: "Selected evidence location" })).toBeVisible();
});
