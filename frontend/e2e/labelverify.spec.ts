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

export async function dismissFirstRunTips(page: Page) {
  const gotIt = page.getByRole("button", { name: "Got it" });
  if (await gotIt.isVisible().catch(() => false)) await gotIt.click();
}

test("label-first sample supports evidence, warning review, disposition, and history", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("dialog", { name: "First-time tips" })).toBeVisible();
  await expectNoSeriousAccessibilityViolations(page);
  await dismissFirstRunTips(page);
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Check one label" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Check a batch" })).toBeVisible();
  await expect(page.getByText("Unofficial prototype")).toBeVisible();
  await expect(page.getByLabel("Brand name")).toHaveCount(0);
  await expectNoSeriousAccessibilityViolations(page);

  const analysisResponsePromise = page.waitForResponse(
    (response) => response.url().endsWith("/api/v1/analyses") && response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Use the built-in sample" }).click();
  await expect(page.getByRole("heading", { name: "Reading the label" })).toBeVisible();
  const analysisResponse = await analysisResponsePromise;
  expect(analysisResponse.ok()).toBe(true);
  expect(analysisResponse.headers()["cache-control"]).toContain("no-store");
  const payload = await analysisResponse.json();
  expect(payload.verification.checks).toHaveLength(24);
  expect(payload.verification.checks.every((check: { group?: string; ruleExpectation?: string; reasonShort?: string }) => check.group && check.ruleExpectation && check.reasonShort)).toBe(true);

  await expect(page.getByRole("heading", { name: "OLD TOM DISTILLERY" })).toBeVisible();
  await expect(page.getByText(/24 checks · distilled spirits profile/)).toBeVisible();
  await expect(page.getByRole("group", { name: "Label images" }).getByRole("button", { pressed: true })).toHaveCount(1);
  await expect(page.locator(".stage-inner polygon")).not.toHaveCount(0);
  await expectNoSeriousAccessibilityViolations(page);

  await page.getByRole("button", { name: "Show", exact: true }).first().click();
  await expect(page.locator(".stage-inner polygon")).toHaveCount(1);
  await page.getByRole("button", { name: "Show all regions" }).click();
  await expect(page.locator(".stage-inner polygon").count()).resolves.toBeGreaterThan(1);
  await page.keyboard.press("2");
  await expect(page.getByText(/Viewing/)).toContainText("panel-2");

  await page.getByRole("radio", { name: "Cards" }).click();
  await expect(page.locator("article.check-card")).toHaveCount(24);
  await page.getByRole("radio", { name: "Image first" }).click();
  await expect(page.locator(".check-rail button")).toHaveCount(24);
  await page.getByRole("radio", { name: "Table" }).click();
  await page.getByRole("button", { name: "Expand 10 checks" }).click();
  await expect(page.getByRole("table", { name: "Government warning checks" })).toBeVisible();

  await page.getByRole("button", { name: "Inspect warning" }).first().click();
  await expect(page.getByRole("heading", { name: "Government warning statement" })).toBeVisible();
  await expect(page.getByRole("row")).toHaveCount(11);
  await expect(page.getByText(/of 43 words match/)).toBeVisible();
  await expectNoSeriousAccessibilityViolations(page);
  await page.getByRole("button", { name: /Warning looks compliant/ }).click();

  await page.keyboard.press("a");
  await expect(page.getByRole("button", { name: /Approve/ })).toHaveAttribute("aria-pressed", "true");
  await page.getByLabel("Reviewer note").fill("Browser UAT sample");
  await page.getByRole("button", { name: /Save & check another/ }).click();
  await expect(page.getByRole("heading", { name: "What are we checking today?" })).toBeVisible();
  await expect(page.getByRole("table").getByText("OLD TOM DISTILLERY")).toBeVisible();

  await page.getByRole("button", { name: /^History/ }).click();
  await expect(page.getByRole("heading", { name: "Completed checks" })).toBeVisible();
  await page.getByRole("button", { name: "Open" }).first().click();
  await expect(page.getByRole("complementary", { name: "Stored result" })).toContainText("OLD TOM DISTILLERY");
  await expect(page.getByRole("complementary", { name: "Stored result" }).getByText("Approved")).toBeVisible();
  await expect(page.locator(".drawer .stage-inner polygon").count()).resolves.toBeGreaterThan(1);
  await page.locator(".drawer .check-list button").nth(1).click();
  await expect(page.locator(".drawer .stage-inner polygon")).toHaveCount(1);
  await expectNoSeriousAccessibilityViolations(page);
});
