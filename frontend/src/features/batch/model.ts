import {
  checkIds,
  profileId,
  type ReferenceRecord,
  type VerificationResult,
} from "../../api/generated-contract";
import {
  ACCEPTED_IMAGE_TYPES,
  MAX_AGGREGATE_BYTES,
  MAX_FILE_BYTES,
  MAX_PANELS,
} from "../intake/model";

export const MAX_BATCH_ITEMS = 300;
export const BATCH_MANIFEST_NAME = "manifest.csv";
export const MAX_BATCH_MANIFEST_BYTES = 1_048_576;
export const MAX_BATCH_SELECTED_ENTRIES = MAX_BATCH_ITEMS * MAX_PANELS + 1;

export type BatchItemState = "queued" | "running" | "match" | "review" | "difference" | "bad_image" | "error" | "cancelled";

export interface BatchInput {
  id: string;
  manifestRow: number;
  reference: ReferenceRecord | null;
  panels: File[];
  panelPaths: string[];
  ingressError: string | null;
}

export interface BatchParseIssue {
  row: number | null;
  message: string;
}

export interface BatchParseResult {
  items: BatchInput[];
  issues: BatchParseIssue[];
}

export interface BatchQueueItem extends BatchInput {
  state: BatchItemState;
  result: VerificationResult | null;
  error: string | null;
  durationMs: number | null;
}

const REQUIRED_HEADERS = [
  "case_id", "brand_name", "class_type", "abv_percent", "net_contents_value",
  "net_contents_unit", "producer_name_address", "is_imported", "panel_paths",
] as const;
const OPTIONAL_HEADERS = ["proof", "country_of_origin"] as const;
const SUPPORTED_HEADERS = new Set<string>([...REQUIRED_HEADERS, ...OPTIONAL_HEADERS]);

interface Inventory {
  entries: Array<readonly [string, File]>;
  manifest: readonly [string, File] | null;
  issues: BatchParseIssue[];
  fatal: boolean;
}

function inventoryBatchDirectory(files: File[]): Inventory {
  const issues: BatchParseIssue[] = [];
  const normalizedFiles = new Map<string, File>();
  const caseFoldedPaths = new Map<string, string>();
  let fatal = false;

  for (const file of files) {
    const candidate = (file as File & { webkitRelativePath?: string }).webkitRelativePath || file.name;
    const path = normalizeRelativePath(candidate);
    if (!path) {
      issues.push({ row: null, message: `Invalid selected file path: ${candidate || "unnamed file"}.` });
      fatal = true;
      continue;
    }
    const folded = path.toLocaleLowerCase("en-US");
    const caseCollision = caseFoldedPaths.get(folded);
    if (normalizedFiles.has(path) || (caseCollision && caseCollision !== path)) {
      issues.push({ row: null, message: `Duplicate or case-ambiguous file path: ${path}.` });
      fatal = true;
      continue;
    }
    normalizedFiles.set(path, file);
    caseFoldedPaths.set(folded, path);
  }

  const manifests = [...normalizedFiles.entries()].filter(([path]) =>
    path === BATCH_MANIFEST_NAME || path.endsWith(`/${BATCH_MANIFEST_NAME}`),
  );
  if (manifests.length !== 1) {
    issues.push({
      row: null,
      message: manifests.length === 0
        ? `The selected folder must contain exactly one ${BATCH_MANIFEST_NAME}.`
        : `The selected folder contains more than one ${BATCH_MANIFEST_NAME}.`,
    });
    fatal = true;
  }
  return {
    entries: [...normalizedFiles.entries()],
    manifest: manifests.length === 1 ? (manifests[0] ?? null) : null,
    issues,
    fatal,
  };
}

export async function readBatchDirectory(files: File[]): Promise<BatchParseResult> {
  if (files.length > MAX_BATCH_SELECTED_ENTRIES) {
    return {
      items: [],
      issues: [{
        row: null,
        message: `A batch folder may contain no more than ${MAX_BATCH_SELECTED_ENTRIES} entries.`,
      }],
    };
  }
  const inventory = inventoryBatchDirectory(files);
  const manifestEntry = inventory.manifest;
  if (!manifestEntry || inventory.fatal) return { items: [], issues: inventory.issues };

  const [manifestPath, manifestFile] = manifestEntry;
  if (manifestFile.size > MAX_BATCH_MANIFEST_BYTES) {
    return {
      items: [],
      issues: [{ row: null, message: "The manifest exceeds the 1 MiB limit." }],
    };
  }
  const rootPrefix = manifestPath.slice(0, -BATCH_MANIFEST_NAME.length);
  const fileMap = new Map<string, File>();
  const caseFoldedRelativePaths = new Map<string, string>();
  for (const [path, file] of inventory.entries) {
    const relative = rootPrefix && path.startsWith(rootPrefix) ? path.slice(rootPrefix.length) : path;
    if (relative === BATCH_MANIFEST_NAME) continue;
    fileMap.set(relative, file);
    caseFoldedRelativePaths.set(relative.toLocaleLowerCase("en-US"), relative);
  }

  let rows: string[][];
  try {
    const bytes = await manifestFile.arrayBuffer();
    const source = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
    rows = parseCsv(source);
  } catch (error) {
    const message = error instanceof TypeError
      ? "The manifest must be valid UTF-8."
      : error instanceof Error ? error.message : "The manifest CSV is invalid.";
    return { items: [], issues: [{ row: null, message }] };
  }
  if (rows.length < 2) {
    return { items: [], issues: [{ row: null, message: "The manifest must include a header and at least one data row." }] };
  }
  const headerRow = rows[0];
  if (!headerRow) {
    return { items: [], issues: [{ row: null, message: "The manifest must include a header and at least one data row." }] };
  }
  const headers = headerRow.map((value) => value.trim().toLowerCase());
  const duplicateHeaders = headers.filter((header, index) => headers.indexOf(header) !== index);
  const missingHeaders = REQUIRED_HEADERS.filter((header) => !headers.includes(header));
  const unknownHeaders = headers.filter((header) => !SUPPORTED_HEADERS.has(header));
  if (duplicateHeaders.length || missingHeaders.length || unknownHeaders.length) {
    const messages = [
      duplicateHeaders.length ? `Duplicate headers: ${[...new Set(duplicateHeaders)].join(", ")}.` : "",
      missingHeaders.length ? `Missing headers: ${missingHeaders.join(", ")}.` : "",
      unknownHeaders.length ? `Unsupported headers: ${[...new Set(unknownHeaders)].join(", ")}.` : "",
    ].filter(Boolean);
    return { items: [], issues: [{ row: 1, message: messages.join(" ") }] };
  }

  const dataRows = rows
    .slice(1)
    .map((row, index) => ({ row, rowNumber: index + 2 }))
    .filter(({ row }) => row.some((value) => value.trim()));
  if (!dataRows.length) {
    return { items: [], issues: [{ row: null, message: "The manifest must include at least one nonblank data row." }] };
  }
  if (dataRows.length > MAX_BATCH_ITEMS) {
    return { items: [], issues: [{ row: null, message: `A batch may contain no more than ${MAX_BATCH_ITEMS} applications.` }] };
  }

  const wrongWidthRows = dataRows.filter(({ row }) => row.length !== headers.length);
  if (wrongWidthRows.length) {
    return {
      items: [],
      issues: wrongWidthRows.map(({ row, rowNumber }) => ({
        row: rowNumber,
        message: `The row contains ${row.length} fields; the header defines ${headers.length}.`,
      })),
    };
  }

  const issues: BatchParseIssue[] = [];
  const items = dataRows.map(({ row, rowNumber }) => {
    const values = Object.fromEntries(headers.map((header, column) => [header, (row[column] ?? "").trim()]));
    return parseRow(values, rowNumber, fileMap, caseFoldedRelativePaths, issues);
  });

  const ownersByPath = new Map<string, BatchInput[]>();
  for (const item of items) {
    for (const path of item.panelPaths) {
      const owners = ownersByPath.get(path) ?? [];
      owners.push(item);
      ownersByPath.set(path, owners);
    }
  }
  for (const [path, owners] of ownersByPath) {
    if (owners.length < 2) continue;
    for (const owner of owners) {
      addIngressError(owner, `panel file is assigned to multiple applications: ${path}`);
      issues.push({ row: owner.manifestRow, message: `Panel file is assigned to multiple applications: ${path}.` });
    }
  }

  const unreferenced = [...fileMap.keys()].filter((path) => !ownersByPath.has(path));
  if (unreferenced.length) {
    return {
      items: [],
      issues: [{ row: null, message: `The folder contains unreferenced files. Remove them or add them to panel_paths: ${unreferenced.slice(0, 8).join(", ")}${unreferenced.length > 8 ? ", and more" : ""}.` }],
    };
  }

  const seenIds = new Map<string, BatchInput>();
  for (const item of items) {
    const foldedId = item.id.toLocaleLowerCase("en-US");
    const first = seenIds.get(foldedId);
    if (first) {
      addIngressError(first, `case_id is duplicated: ${item.id}`);
      addIngressError(item, `case_id is duplicated: ${item.id}`);
      issues.push({ row: item.manifestRow, message: `case_id must be unique: ${item.id}.` });
    } else {
      seenIds.set(foldedId, item);
    }
  }
  return { items, issues };
}

function parseRow(
  values: Record<string, string>,
  rowNumber: number,
  fileMap: Map<string, File>,
  caseFoldedRelativePaths: Map<string, string>,
  issues: BatchParseIssue[],
): BatchInput {
  const rowIssues: string[] = [];
  const requiredText = (key: string, label: string, maxLength: number): string => {
    const value = values[key] ?? "";
    if (!value) rowIssues.push(`${label} is required`);
    else if (value.length > maxLength) rowIssues.push(`${label} exceeds ${maxLength} characters`);
    return value;
  };
  const numberValue = (key: string, label: string, maximum?: number): number => {
    const raw = values[key] ?? "";
    const parsed = Number(raw);
    if (!raw || !Number.isFinite(parsed) || parsed <= 0 || (maximum !== undefined && parsed > maximum)) rowIssues.push(`${label} is invalid`);
    return parsed;
  };

  const sourceId = requiredText("case_id", "case_id", 80);
  const id = sourceId || `ROW-${rowNumber}`;
  const imported = parseBoolean(values.is_imported ?? "", rowIssues);
  const unit = values.net_contents_unit;
  if (unit !== "mL" && unit !== "L") rowIssues.push("net_contents_unit must be mL or L");
  const country = values.country_of_origin ?? "";
  if (imported && !country) rowIssues.push("country_of_origin is required for imported products");
  const proofRaw = values.proof ?? "";
  const proof = proofRaw ? Number(proofRaw) : null;
  if (proofRaw && (!Number.isFinite(proof) || Number(proof) < 0)) rowIssues.push("proof is invalid");

  const rawPanelPaths = (values.panel_paths ?? "").split(/[|;]/).map((value) => value.trim()).filter(Boolean);
  const panelPaths: string[] = [];
  for (const rawPath of rawPanelPaths) {
    const normalized = normalizeRelativePath(rawPath);
    if (!normalized) {
      rowIssues.push(`panel path must be relative and cannot contain traversal: ${rawPath}`);
      continue;
    }
    const canonical = caseFoldedRelativePaths.get(normalized.toLocaleLowerCase("en-US"));
    if (canonical && canonical !== normalized) {
      rowIssues.push(`panel path case does not match the selected file: ${rawPath}`);
      continue;
    }
    if (panelPaths.includes(normalized)) {
      rowIssues.push(`panel path is duplicated in the row: ${normalized}`);
      continue;
    }
    panelPaths.push(normalized);
  }
  if (panelPaths.length < 1 || panelPaths.length > MAX_PANELS) rowIssues.push(`panel_paths must contain 1 to ${MAX_PANELS} files separated by | or ;`);

  const panels = panelPaths.map((path) => fileMap.get(path));
  panelPaths.forEach((path, index) => {
    const file = panels[index];
    if (!file) rowIssues.push(`panel file was not found: ${path}`);
    else if (!isAcceptedImage(file, path)) rowIssues.push(`unsupported image type: ${path}`);
    else if (file.size > MAX_FILE_BYTES) rowIssues.push(`panel exceeds 4 MiB: ${path}`);
  });
  const resolvedPanels = panels.filter((file): file is File => Boolean(file));
  if (resolvedPanels.reduce((total, file) => total + file.size, 0) > MAX_AGGREGATE_BYTES) rowIssues.push("panel files exceed the 8 MiB per-application limit");

  const reference: ReferenceRecord = {
    profileId,
    caseLabel: sourceId || null,
    brandName: requiredText("brand_name", "brand_name", 160),
    classType: requiredText("class_type", "class_type", 240),
    abvPercent: numberValue("abv_percent", "abv_percent", 100),
    proof,
    netContentsValue: numberValue("net_contents_value", "net_contents_value"),
    netContentsUnit: unit === "L" ? "L" : "mL",
    producerNameAddress: requiredText("producer_name_address", "producer_name_address", 500),
    isImported: imported,
    countryOfOrigin: imported ? country : null,
  };
  const ingressError = rowIssues.length ? `${rowIssues.join("; ")}.` : null;
  if (ingressError) issues.push({ row: rowNumber, message: ingressError });
  return { id, manifestRow: rowNumber, reference: ingressError ? null : reference, panels: resolvedPanels, panelPaths, ingressError };
}

function addIngressError(item: BatchInput, message: string): void {
  item.ingressError = item.ingressError ? `${item.ingressError} ${message}.` : `${message}.`;
  item.reference = null;
}

function parseBoolean(value: string, issues: string[]): boolean {
  const normalized = value.trim().toLowerCase();
  if (["true", "1", "yes"].includes(normalized)) return true;
  if (["false", "0", "no"].includes(normalized)) return false;
  issues.push("is_imported must be true or false");
  return false;
}

function normalizeRelativePath(value: string): string | null {
  const slashNormalized = value.replaceAll("\\", "/");
  if (!slashNormalized || slashNormalized.startsWith("/") || /^[A-Za-z]:\//.test(slashNormalized)) return null;
  const normalized = slashNormalized.replace(/^\.\//, "");
  if (!normalized || normalized.split("/").some((part) => part === ".." || part === "." || part === "")) return null;
  return normalized;
}

function isAcceptedImage(file: File, path: string): boolean {
  if (ACCEPTED_IMAGE_TYPES.includes(file.type as (typeof ACCEPTED_IMAGE_TYPES)[number])) return true;
  if (file.type) return false;
  return /\.(?:jpe?g|png|webp)$/i.test(path);
}

export function parseCsv(source: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [];
  let field = "";
  let quoted = false;
  for (let index = 0; index < source.length; index += 1) {
    const character = source[index];
    if (quoted) {
      if (character === '"' && source[index + 1] === '"') { field += '"'; index += 1; }
      else if (character === '"') quoted = false;
      else field += character;
    } else if (character === '"') {
      if (field) throw new Error("The manifest contains an unexpected quote.");
      quoted = true;
    } else if (character === ",") { row.push(field); field = ""; }
    else if (character === "\n") { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
    else field += character;
  }
  if (quoted) throw new Error("The manifest contains an unclosed quoted value.");
  if (field || row.length) { row.push(field.replace(/\r$/, "")); rows.push(row); }
  return rows;
}

export function resultState(result: VerificationResult): BatchItemState {
  const imageQuality = result.checks.find((check) => check.checkId === "image_quality");
  if (imageQuality?.state === "Not verified" || imageQuality?.reasonCode === "image_unreadable") return "bad_image";
  if (result.summary === "No differences found in checked fields") return "match";
  if (result.summary === "Review needed") return "review";
  return "difference";
}

export function toQueueItems(items: BatchInput[]): BatchQueueItem[] {
  return items.map((item) => ({ ...item, state: item.ingressError ? "error" : "queued", result: null, error: item.ingressError, durationMs: null }));
}

export function batchCsv(items: BatchQueueItem[]): string {
  const header = ["manifest_row", "case_id", "status", "summary", "client_duration_ms", "server_duration_ms", "request_id", "error", ...checkIds.map((checkId) => `${checkId}_state`)];
  const rows = items.map((item) => {
    const stateByCheck = new Map(item.result?.checks.map((check) => [check.checkId, check.state]) ?? []);
    return [
      String(item.manifestRow), item.id, item.state, item.result?.summary ?? "",
      item.durationMs == null ? "" : String(Math.round(item.durationMs)),
      item.result ? String(item.result.serverDurationMs) : "", item.result?.requestId ?? "", item.error ?? "",
      ...checkIds.map((checkId) => stateByCheck.get(checkId) ?? ""),
    ];
  });
  return [header, ...rows].map((row) => row.map(csvCell).join(",")).join("\r\n");
}

export function batchDetailsJson(items: BatchQueueItem[]): string {
  return JSON.stringify({
    schemaVersion: "1.0.0",
    exportedAt: new Date().toISOString(),
    applications: items.map((item) => ({
      manifestRow: item.manifestRow,
      caseId: item.id,
      status: item.state,
      input: item.reference,
      panelPaths: item.panelPaths,
      clientDurationMs: item.durationMs == null ? null : Math.round(item.durationMs),
      error: item.error,
      result: item.result,
    })),
  }, null, 2);
}

function csvCell(source: string): string {
  const value = /^[=+\-@\t\r]/.test(source) ? `'${source}` : source;
  return /[",\r\n]/.test(value) ? `"${value.replaceAll('"', '""')}"` : value;
}
