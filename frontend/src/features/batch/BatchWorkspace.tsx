import { useEffect, useMemo, useRef, useState, type ChangeEvent } from "react";

import { VerificationClientError } from "../../api/verification-client";
import { limits } from "../../api/generated-contract";
import type { SampleAdapter, VerificationClient } from "../../contracts/types";
import { ResultWorkspace } from "../verification/ResultWorkspace";
import {
  batchCsv,
  batchDetailsJson,
  MAX_BATCH_SELECTED_ENTRIES,
  MAX_BATCH_ITEMS,
  readBatchDirectory,
  resultState,
  toQueueItems,
  type BatchItemState,
  type BatchParseIssue,
  type BatchQueueItem,
} from "./model";

interface BatchWorkspaceProps {
  verificationClient: VerificationClient;
  sampleAdapter: SampleAdapter;
}

type Filter = "all" | "attention" | "match" | "review" | "difference" | "bad_image" | "error" | "cancelled" | "queued";

const TEMPLATE = [
  "case_id,brand_name,class_type,abv_percent,proof,net_contents_value,net_contents_unit,producer_name_address,is_imported,country_of_origin,panel_paths",
  'CASE-001,OLD TOM DISTILLERY,Kentucky Straight Bourbon Whiskey,45,90,750,mL,"OLD TOM DISTILLERY LLC FRANKFORT KENTUCKY 40601",false,,CASE-001/front.png|CASE-001/back.png',
].join("\r\n");

const FILTERS: Array<{ value: Filter; label: string }> = [
  { value: "all", label: "All" },
  { value: "attention", label: "Needs attention" },
  { value: "match", label: "No differences" },
  { value: "review", label: "Needs review" },
  { value: "difference", label: "Differences" },
  { value: "bad_image", label: "Bad image" },
  { value: "error", label: "Errors" },
  { value: "cancelled", label: "Cancelled" },
  { value: "queued", label: "Queued" },
];

const ATTENTION_STATES: BatchItemState[] = ["review", "difference", "bad_image", "error", "cancelled"];

function statusLabel(state: BatchItemState): string {
  const labels: Record<BatchItemState, string> = {
    queued: "Queued",
    running: "Running",
    match: "No differences",
    review: "Needs review",
    difference: "Differences",
    bad_image: "Bad image",
    error: "Error",
    cancelled: "Cancelled",
  };
  return labels[state];
}

function downloadText(filename: string, contents: string, type = "text/csv;charset=utf-8") {
  const url = URL.createObjectURL(new Blob([contents], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function BatchWorkspace({ verificationClient, sampleAdapter }: BatchWorkspaceProps) {
  const [queue, setQueue] = useState<BatchQueueItem[]>([]);
  const [issues, setIssues] = useState<BatchParseIssue[]>([]);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [elapsedMs, setElapsedMs] = useState(0);
  const [filter, setFilter] = useState<Filter>("all");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [disposition, setDisposition] = useState("");
  const controllerRef = useRef<AbortController | null>(null);
  const cancelRef = useRef(false);
  const timerRef = useRef<number | null>(null);
  const summaryRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => () => {
    cancelRef.current = true;
    controllerRef.current?.abort();
    if (timerRef.current !== null) window.clearInterval(timerRef.current);
  }, []);

  const completed = queue.filter((item) => !["queued", "running"].includes(item.state)).length;
  const processed = queue.filter((item) => ["match", "review", "difference", "bad_image", "error"].includes(item.state));
  const averageMs = processed.length
    ? processed.reduce((total, item) => total + (item.durationMs ?? 0), 0) / processed.length
    : 0;
  const remaining = queue.filter((item) => item.state === "queued").length;
  const filtered = useMemo(
    () => filter === "all"
      ? queue
      : queue.filter((item) => filter === "attention" ? ATTENTION_STATES.includes(item.state) : item.state === filter),
    [filter, queue],
  );
  const selected = queue.find((item) => item.id === selectedId) ?? null;
  const current = queue.find((item) => item.state === "running") ?? null;

  async function loadDirectory(event: ChangeEvent<HTMLInputElement>) {
    const selection = event.target.files;
    if (!selection?.length) return;
    if (selection.length > MAX_BATCH_SELECTED_ENTRIES) {
      event.target.value = "";
      setQueue([]);
      setIssues([{
        row: null,
        message: `The selected folder exceeds the ${MAX_BATCH_SELECTED_ENTRIES}-entry limit.`,
      }]);
      return;
    }
    const files = Array.from(selection);
    event.target.value = "";
    setLoading(true);
    setSelectedId(null);
    try {
      const parsed = await readBatchDirectory(files);
      setQueue(toQueueItems(parsed.items));
      setIssues(parsed.issues);
    } finally {
      setLoading(false);
    }
  }

  async function loadDemo() {
    setLoading(true);
    setIssues([]);
    setSelectedId(null);
    try {
      const sample = await sampleAdapter.load();
      const inputs = Array.from({ length: 10 }, (_, index) => {
        const reference = { ...sample.reference, caseLabel: `DEMO-${String(index + 1).padStart(2, "0")}` };
        if (index === 1) reference.brandName = "Old Tom Distillery";
        if (index === 2) reference.abvPercent = 46;
        if (index === 3) {
          reference.netContentsValue = 1;
          reference.netContentsUnit = "L";
        }
        return {
          id: reference.caseLabel ?? `DEMO-${index + 1}`,
          manifestRow: index + 2,
          reference,
          panels: sample.panels,
          panelPaths: sample.panels.map((panel) => panel.name),
          ingressError: null,
        };
      });
      setQueue(toQueueItems(inputs));
    } catch {
      setIssues([{ row: null, message: "The built-in batch could not be loaded." }]);
    } finally {
      setLoading(false);
    }
  }

  function updateItem(index: number, update: Partial<BatchQueueItem>) {
    setQueue((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, ...update } : item));
  }

  async function processItem(index: number, item: BatchQueueItem): Promise<void> {
    if (!item.reference || item.ingressError) return;
    const controller = new AbortController();
    controllerRef.current = controller;
    updateItem(index, { state: "running", error: null, result: null, durationMs: null });
    const started = performance.now();
    let timedOut = false;
    const deadline = window.setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, limits.browserDeadlineSeconds * 1000);
    try {
      const result = await verificationClient.verify({
        reference: item.reference,
        panels: item.panels,
        signal: controller.signal,
      });
      const durationMs = performance.now() - started;
      if (controller.signal.aborted || cancelRef.current) {
        updateItem(index, { state: "cancelled", error: null, result: null, durationMs });
      } else {
        updateItem(index, { state: resultState(result), result, error: null, durationMs });
      }
    } catch (error) {
      const durationMs = performance.now() - started;
      if (timedOut) {
        updateItem(index, {
          state: "error",
          error: `This application exceeded the ${limits.browserDeadlineSeconds}-second browser deadline. Retry it or use a clearer image.`,
          result: null,
          durationMs,
        });
      } else if (controller.signal.aborted || cancelRef.current) {
        updateItem(index, { state: "cancelled", error: null, result: null, durationMs });
      } else {
        const message = error instanceof VerificationClientError
          ? `${error.detail.message} ${error.detail.nextAction}`
          : "The verifier could not process this application.";
        updateItem(index, { state: "error", error: message, result: null, durationMs });
      }
    } finally {
      window.clearTimeout(deadline);
      controllerRef.current = null;
    }
  }

  async function runBatch() {
    if (running || !queue.some((item) => item.state === "queued" || (["error", "cancelled"].includes(item.state) && !item.ingressError))) return;
    cancelRef.current = false;
    setRunning(true);
    setElapsedMs(0);
    const started = performance.now();
    timerRef.current = window.setInterval(() => setElapsedMs(performance.now() - started), 200);
    const snapshot = queue.map((item) =>
      ["error", "cancelled"].includes(item.state) && !item.ingressError
        ? { ...item, state: "queued" as const, error: null, result: null, durationMs: null }
        : item,
    );
    setQueue(snapshot);
    for (let index = 0; index < snapshot.length; index += 1) {
      if (cancelRef.current) break;
      const item = snapshot[index];
      if (!item || item.state !== "queued") continue;
      await processItem(index, item);
    }
    if (cancelRef.current) {
      setQueue((current) => current.map((item) => item.state === "queued" ? { ...item, state: "cancelled" } : item));
    }
    if (timerRef.current !== null) window.clearInterval(timerRef.current);
    timerRef.current = null;
    setElapsedMs(performance.now() - started);
    setRunning(false);
  }

  function cancelBatch() {
    cancelRef.current = true;
    controllerRef.current?.abort();
  }

  async function retryOne(item: BatchQueueItem) {
    if (running || item.ingressError) return;
    const index = queue.findIndex((candidate) => candidate.id === item.id);
    if (index < 0) return;
    cancelRef.current = false;
    setRunning(true);
    await processItem(index, item);
    setRunning(false);
  }

  function openDetails(item: BatchQueueItem) {
    if (!item.result) return;
    setSelectedId(item.id);
    setSelectedEvidenceId(item.result.evidence[0]?.evidenceId ?? null);
    setNote("");
    setDisposition("");
    window.setTimeout(() => summaryRef.current?.focus(), 0);
  }

  if (selected?.result) {
    return (
      <div className="batch-detail-page">
        <button className="button secondary" onClick={() => setSelectedId(null)} type="button">Back to batch results</button>
        <ResultWorkspace
          disposition={disposition}
          note={note}
          onDispositionChange={setDisposition}
          onNoteChange={setNote}
          onSelectEvidence={setSelectedEvidenceId}
          onStartOver={() => setSelectedId(null)}
          result={selected.result}
          selectedEvidenceId={selectedEvidenceId}
          sourcePanels={selected.panels}
          summaryRef={summaryRef}
        />
      </div>
    );
  }

  return (
    <div className="batch-page">
      <section className="card batch-intro" aria-labelledby="batch-heading">
        <p className="eyebrow">Local batch review</p>
        <h1 id="batch-heading">Check up to {MAX_BATCH_ITEMS} applications</h1>
        <p className="lede">Choose one folder containing a manifest and its label images. Applications run one at a time through the same local OCR and rule pipeline, with progress and isolated errors.</p>
        <div className="batch-intake-actions">
          <label className={`button primary ${running || loading ? "disabled-label" : ""}`}>
            Choose batch folder
            <input
              {...({ webkitdirectory: "", directory: "" } as Record<string, string>)}
              accept=".csv,image/jpeg,image/png,image/webp"
              disabled={running || loading}
              multiple
              onChange={loadDirectory}
              type="file"
            />
          </label>
          <button className="button secondary" disabled={running || loading} onClick={loadDemo} type="button">Try a 10-application batch</button>
          <button className="button tertiary" onClick={() => downloadText("labelverify-batch-template.csv", TEMPLATE)} type="button">Download manifest template</button>
        </div>
        <p className="field-help">The folder must contain one manifest.csv. Separate multiple panel paths with | or ;. Files remain in this browser session and each application keeps the existing per-request limits.</p>
      </section>

      {issues.length ? (
        <section className="status-banner error-banner" aria-labelledby="batch-issues-heading" role="alert">
          <div>
            <p className="eyebrow">Batch intake issues</p>
            <h2 id="batch-issues-heading">{issues.length} row or folder issue{issues.length === 1 ? "" : "s"}</h2>
            <ul>{issues.map((issue, index) => <li key={`${issue.row}-${index}`}>{issue.row ? `Row ${issue.row}: ` : ""}{issue.message}</li>)}</ul>
            {queue.length ? <p>Valid rows remain queued and can still be processed.</p> : null}
          </div>
        </section>
      ) : null}

      {queue.length ? (
        <section className="card batch-queue" aria-labelledby="batch-queue-heading">
          <div className="section-heading">
            <div>
              <p className="step-label">Batch queue</p>
              <h2 id="batch-queue-heading">{completed} of {queue.length} completed</h2>
            </div>
            <div className="batch-summary">
              <span>Elapsed: {(elapsedMs / 1000).toFixed(1)}s</span>
              <span>Current: {current?.id ?? "None"}</span>
              <span>Average: {averageMs ? `${(averageMs / 1000).toFixed(1)}s` : "Pending"}</span>
              <span>Estimated remaining: {averageMs ? `${Math.ceil(remaining * averageMs / 1000)}s` : "Pending"}</span>
            </div>
          </div>
          <progress aria-label="Batch progress" max={queue.length} value={completed}>{completed} of {queue.length}</progress>
          <div className="batch-controls">
            {running
              ? <button className="button danger" onClick={cancelBatch} type="button">Cancel batch</button>
              : <button className="button primary" onClick={runBatch} type="button">{completed ? "Process remaining and retry errors" : "Start batch"}</button>}
            <button className="button secondary" disabled={!completed} onClick={() => downloadText("labelverify-batch-results.csv", batchCsv(queue))} type="button">Export results CSV</button>
            <button className="button secondary" disabled={!completed} onClick={() => downloadText("labelverify-batch-details.json", batchDetailsJson(queue), "application/json;charset=utf-8")} type="button">Export detailed JSON</button>
          </div>
          <div className="batch-filters" aria-label="Filter batch results">
            {FILTERS.map((item) => (
              <button aria-pressed={filter === item.value} key={item.value} onClick={() => setFilter(item.value)} type="button">
                {item.label} ({item.value === "all"
                  ? queue.length
                  : queue.filter((candidate) => item.value === "attention" ? ATTENTION_STATES.includes(candidate.state) : candidate.state === item.value).length})
              </button>
            ))}
          </div>
          <div className="batch-table-wrap">
            <table>
              <thead><tr><th scope="col">Case</th><th scope="col">Status</th><th scope="col">Time</th><th scope="col">Problem summary</th><th scope="col">Action</th></tr></thead>
              <tbody>
                {filtered.map((item) => (
                  <tr className={`batch-state-${item.state}`} key={`${item.manifestRow}-${item.id}`}>
                    <th scope="row">{item.id}</th>
                    <td><span className="batch-status">{statusLabel(item.state)}</span></td>
                    <td>{item.durationMs == null ? "-" : `${(item.durationMs / 1000).toFixed(1)}s`}</td>
                    <td>{item.error ?? item.result?.summary ?? "Waiting to run"}</td>
                    <td>
                      {item.result ? <button className="button secondary compact-button" onClick={() => openDetails(item)} type="button">Open details</button> : null}
                      {["error", "cancelled"].includes(item.state) && !item.ingressError ? <button className="button secondary compact-button" disabled={running} onClick={() => retryOne(item)} type="button">Retry</button> : null}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : null}
    </div>
  );
}
