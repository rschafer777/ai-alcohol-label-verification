import { copyFile, mkdir, mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test } from "@playwright/test";

const PROJECT_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const EVIDENCE_PATH = join(
  PROJECT_ROOT,
  "docs",
  "08-validation",
  "evidence",
  "browser-batch-capacity.json",
);

interface ReferenceFixture {
  abvPercent: number;
  brandName: string;
  classType: string;
  countryOfOrigin: string | null;
  isImported: boolean;
  netContentsUnit: "mL" | "L";
  netContentsValue: number;
  producerNameAddress: string;
  proof: number | null;
}

interface ExportedApplication {
  caseId: string;
  input: ReferenceFixture;
  result: { checks: unknown[]; requestId: string; summary: string };
  status: string;
}

function csvCell(value: string | number | boolean | null): string {
  const text = value == null ? "" : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

async function fixture(path: string): Promise<ReferenceFixture> {
  return JSON.parse(await readFile(join(PROJECT_ROOT, path), "utf-8")) as ReferenceFixture;
}

test("governed 300-application browser batch is complete, mixed, cancellable, and exportable", async ({ page }, testInfo) => {
  test.skip(process.env.LABELVERIFY_RUN_BATCH_CAPACITY !== "1", "Run only for governed batch evidence.");
  test.skip(testInfo.project.name !== "chrome", "One canonical Chrome capacity run is retained.");
  test.setTimeout(1_800_000);

  const temporaryRoot = await mkdtemp(join(tmpdir(), "labelverify-browser-batch-"));
  const cleanReference = await fixture("fixtures/holdout/cases/H006/reference.json");
  const reviewReference = await fixture("fixtures/development/cases/D001/reference.json");
  const differenceReference = await fixture("fixtures/development/cases/D004/reference.json");
  const scenarios = [
    {
      expectedStatus: "match",
      panel: "fixtures/holdout/cases/H006/panels/panel-1.png",
      reference: cleanReference,
    },
    {
      expectedStatus: "review",
      panel: "fixtures/development/cases/D001/panels/panel-1.png",
      reference: reviewReference,
    },
    {
      expectedStatus: "difference",
      panel: "fixtures/development/cases/D004/panels/panel-1.png",
      reference: differenceReference,
    },
  ] as const;

  const header = [
    "case_id",
    "brand_name",
    "class_type",
    "abv_percent",
    "proof",
    "net_contents_value",
    "net_contents_unit",
    "producer_name_address",
    "is_imported",
    "country_of_origin",
    "panel_paths",
  ].join(",");
  const rows: string[] = [header];
  const expectedByCase = new Map<string, string>();
  for (let index = 0; index < 300; index += 1) {
    const scenario = scenarios[index % scenarios.length]!;
    const caseId = `BROWSER-${String(index + 1).padStart(3, "0")}`;
    const relativePanel = `${caseId}/panel.png`;
    const targetPanel = join(temporaryRoot, relativePanel);
    await mkdir(dirname(targetPanel), { recursive: true });
    await copyFile(join(PROJECT_ROOT, scenario.panel), targetPanel);
    const reference = scenario.reference;
    rows.push([
      caseId,
      reference.brandName,
      reference.classType,
      reference.abvPercent,
      reference.proof,
      reference.netContentsValue,
      reference.netContentsUnit,
      reference.producerNameAddress.replaceAll(/\s+/g, " "),
      reference.isImported,
      reference.countryOfOrigin,
      relativePanel,
    ].map(csvCell).join(","));
    expectedByCase.set(caseId, scenario.expectedStatus);
  }
  await writeFile(join(temporaryRoot, "manifest.csv"), `${rows.join("\r\n")}\r\n`, "utf-8");

  try {
    await page.goto("/");
    await page.getByRole("button", { name: "Batch" }).click();
    const folderInput = page.locator('input[type="file"][webkitdirectory]');
    await folderInput.setInputFiles(temporaryRoot);
    await expect(page.getByRole("heading", { name: "0 of 300 completed" })).toBeVisible();

    await page.getByRole("button", { name: "Start batch" }).click();
    await page.getByRole("button", { name: "Cancel batch" }).click();
    await expect(page.getByRole("button", { name: "Cancelled (300)" })).toBeVisible();
    await page.waitForTimeout(4_000);
    await page.getByRole("button", { name: "Retry", exact: true }).first().click();
    await expect(page.getByRole("button", { name: "Cancelled (299)" })).toBeVisible();
    await expect(page.getByRole("button", { name: "No differences (1)" })).toBeVisible();

    await folderInput.setInputFiles(temporaryRoot);
    await expect(page.getByRole("heading", { name: "0 of 300 completed" })).toBeVisible();
    const started = Date.now();
    await page.getByRole("button", { name: "Start batch" }).click();
    await page.getByRole("heading", { name: "300 of 300 completed" }).waitFor({
      state: "visible",
      timeout: 1_500_000,
    });
    const elapsedSeconds = (Date.now() - started) / 1000;

    await expect(page.getByRole("button", { name: "No differences (100)", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Needs review (100)", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Differences (100)", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Errors (0)", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "Bad image (0)", exact: true })).toBeVisible();

    const csvEvent = page.waitForEvent("download");
    await page.getByRole("button", { name: "Export results CSV" }).click();
    const csvDownload = await csvEvent;
    const csvPath = join(temporaryRoot, "results.csv");
    await csvDownload.saveAs(csvPath);
    const csv = await readFile(csvPath, "utf-8");

    const jsonEvent = page.waitForEvent("download");
    await page.getByRole("button", { name: "Export detailed JSON" }).click();
    const jsonDownload = await jsonEvent;
    const jsonPath = join(temporaryRoot, "details.json");
    await jsonDownload.saveAs(jsonPath);
    const details = JSON.parse(await readFile(jsonPath, "utf-8")) as {
      applications: ExportedApplication[];
    };

    const ids = details.applications.map((item) => item.caseId);
    const requestIds = details.applications.map((item) => item.result.requestId);
    const falseCleanCount = details.applications.filter(
      (item) => item.status === "match" && expectedByCase.get(item.caseId) !== "match",
    ).length;
    expect(details.applications).toHaveLength(300);
    expect(new Set(ids).size).toBe(300);
    expect(new Set(requestIds).size).toBe(300);
    expect(details.applications.every((item) => item.result.checks.length === 19)).toBe(true);
    expect(falseCleanCount).toBe(0);
    expect(csv.trimEnd().split("\r\n")).toHaveLength(301);
    expect(elapsedSeconds).toBeLessThanOrEqual(1_500);

    const browserState = await page.evaluate(async () => ({
      cacheKeys: await caches.keys(),
      indexedDatabases: typeof indexedDB.databases === "function"
        ? (await indexedDB.databases()).map((item) => item.name ?? "")
        : [],
      localStorageKeys: Object.keys(localStorage),
      sessionStorageKeys: Object.keys(sessionStorage),
    }));
    expect(browserState).toEqual({
      cacheKeys: [],
      indexedDatabases: [],
      localStorageKeys: [],
      sessionStorageKeys: [],
    });

    await writeFile(EVIDENCE_PATH, `${JSON.stringify({
      schemaVersion: "1.0.0",
      measuredAtUtc: new Date().toISOString(),
      browserProject: testInfo.project.name,
      requestedCount: 300,
      completedCount: details.applications.length,
      uniqueCaseIdCount: new Set(ids).size,
      uniqueRequestIdCount: new Set(requestIds).size,
      expectedAndObservedStatusCounts: {
        difference: 100,
        match: 100,
        review: 100,
      },
      falseCleanCount,
      checkRows: details.applications.reduce(
        (total, item) => total + item.result.checks.length,
        0,
      ),
      csvRowCountIncludingHeader: csv.trimEnd().split("\r\n").length,
      detailedJsonApplicationCount: details.applications.length,
      cancellationObserved: true,
      retryObserved: true,
      browserStorageState: browserState,
      elapsedSeconds: Number(elapsedSeconds.toFixed(3)),
      thresholdSeconds: 1_500,
      pass: true,
    }, null, 2)}\n`, "utf-8");
  } finally {
    await page.close().catch(() => undefined);
    await rm(temporaryRoot, {
      recursive: true,
      force: true,
      maxRetries: 10,
      retryDelay: 500,
    });
  }
});
