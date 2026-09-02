import { useEffect, useMemo, useRef, useState } from "react";

import { VerificationClientError } from "../../api/verification-client";
import type { VerificationClient } from "../../contracts/types";
import { ResultWorkspace } from "../verification/ResultWorkspace";
import {
  canonicalPath,
  imageSelectionIssue,
  spreadsheetSafeCsvCell,
  suggestProductGroups,
  type SuggestedGroup,
} from "./grouping";

interface BatchWorkspaceProps {
  initialFiles: File[];
  onFilesConsumed: () => void;
  verificationClient: VerificationClient;
}

function machineLabel(group: SuggestedGroup): string {
  if (group.status === "running") return "Running";
  if (group.status === "queued") return "Queued";
  if (group.status === "cancelled") return "Cancelled";
  if (group.status === "failed") return "Failed";
  return group.result?.summary ?? "Waiting";
}

function download(filename: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function FilePreview({ file }: { file: File }) {
  const url = useMemo(() => URL.createObjectURL(file), [file]);
  useEffect(() => () => URL.revokeObjectURL(url), [url]);
  return <img alt="" loading="lazy" src={url} />;
}

export function BatchWorkspace({ initialFiles, onFilesConsumed, verificationClient }: BatchWorkspaceProps) {
  const initialIssue = imageSelectionIssue(initialFiles, 900);
  const [groups, setGroups] = useState<SuggestedGroup[]>(() => initialIssue ? [] : suggestProductGroups(initialFiles));
  const [stage, setStage] = useState<"select" | "confirm" | "run">(initialFiles.length && !initialIssue ? "confirm" : "select");
  const [selectionIssue, setSelectionIssue] = useState(initialIssue ?? "");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [activeId, setActiveId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "attention" | "complete" | "failed">("all");
  const [elapsedMs, setElapsedMs] = useState(0);
  const input = useRef<HTMLInputElement>(null);
  const consumedInitialFiles = useRef(false);
  const cancel = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const runTimer = useRef<number | null>(null);

  useEffect(() => {
    if (!consumedInitialFiles.current && initialFiles.length) {
      consumedInitialFiles.current = true;
      onFilesConsumed();
    }
  }, [initialFiles.length, onFilesConsumed]);
  useEffect(() => () => {
    cancel.current = true;
    controller.current?.abort();
    if (runTimer.current !== null) window.clearInterval(runTimer.current);
  }, []);

  const completed = groups.filter((group) => group.status === "complete").length;
  const failed = groups.filter((group) => group.status === "failed").length;
  const remaining = groups.filter((group) => ["queued", "running"].includes(group.status)).length;
  const durations = groups.flatMap((group) => group.durationMs == null ? [] : [group.durationMs]);
  const averageMs = durations.length ? durations.reduce((sum, value) => sum + value, 0) / durations.length : 0;
  const active = groups.find((group) => group.id === activeId) ?? null;
  const filtered = useMemo(() => groups.filter((group) => filter === "all" || filter === "attention" && (group.status === "failed" || group.result?.summary !== "No differences found in checked fields") || filter === "complete" && group.status === "complete" || filter === "failed" && group.status === "failed"), [filter, groups]);

  function choose(files: File[]) {
    const issue = imageSelectionIssue(files, 900);
    if (issue) {
      setGroups([]);
      setStage("select");
      setSelectionIssue(issue);
      return;
    }
    setSelectionIssue("");
    setGroups(suggestProductGroups(files));
    setStage(files.length ? "confirm" : "select");
    setSelected(new Set());
  }

  function update(id: string, patch: Partial<SuggestedGroup>) {
    setGroups((current) => current.map((group) => group.id === id ? { ...group, ...patch } : group));
  }

  function confirm(id: string) {
    const group = groups.find((item) => item.id === id);
    if (!group?.name.trim()) return;
    update(id, { name: group.name.trim(), confirmed: true, status: "ready" });
  }

  function mergeSelected() {
    const merge = groups.filter((group) => selected.has(group.id));
    const files = merge.flatMap((group) => group.files);
    if (merge.length < 2 || files.length > 3) return;
    const first = merge[0];
    if (!first) return;
    setGroups((current) => [{ ...first, files, name: first.name, confirmed: false, status: "needs_confirmation", reason: "Manually merged. Confirm before running." }, ...current.filter((group) => !selected.has(group.id))]);
    setSelected(new Set());
  }

  function splitSelected() {
    const split = groups.filter((group) => selected.has(group.id) && group.files.length > 1);
    if (!split.length) return;
    setGroups((current) => current.flatMap((group) => selected.has(group.id) && group.files.length > 1 ? group.files.map((file, index) => ({ ...group, id: `${group.id}-split-${index + 1}`, name: `${group.name} ${index + 1}`, files: [file], confirmed: false, status: "needs_confirmation" as const, reason: "Manually split. Confirm as a separate product." })) : [group]));
    setSelected(new Set());
  }

  async function processGroup(group: SuggestedGroup): Promise<void> {
    const nextController = new AbortController();
    controller.current = nextController;
    update(group.id, { status: "running", attempts: group.attempts + 1, error: null });
    const started = performance.now();
    try {
      const analysis = await verificationClient.analyze({ panels: group.files, signal: nextController.signal });
      const durationMs = performance.now() - started;
      if (cancel.current || nextController.signal.aborted) update(group.id, { status: "cancelled", durationMs });
      else if (analysis.verification) update(group.id, { analysis, result: analysis.verification, status: "complete", durationMs });
      else update(group.id, { analysis, status: "failed", durationMs, error: "Beverage type needs human confirmation before rule checks can run." });
    } catch (caught) {
      const durationMs = performance.now() - started;
      if (cancel.current || nextController.signal.aborted) update(group.id, { status: "cancelled", durationMs });
      else update(group.id, { status: "failed", durationMs, error: caught instanceof VerificationClientError ? caught.detail.message : "Processing failed." });
    }
  }

  async function run() {
    if (
      !groups.length
      || groups.length > 300
      || groups.some((group) => !group.confirmed || !group.name.trim())
    ) return;
    cancel.current = false;
    setStage("run");
    const started = performance.now();
    runTimer.current = window.setInterval(
      () => setElapsedMs(performance.now() - started),
      100,
    );
    setGroups((current) => current.map((group) => ({ ...group, status: "queued", error: null })));
    try {
      for (const snapshot of groups) {
        if (cancel.current) break;
        await processGroup(snapshot);
      }
    } finally {
      if (runTimer.current !== null) window.clearInterval(runTimer.current);
      runTimer.current = null;
      setElapsedMs(performance.now() - started);
    }
    if (cancel.current) setGroups((current) => current.map((group) => group.status === "queued" ? { ...group, status: "cancelled" } : group));
  }

  async function retry(group: SuggestedGroup) {
    cancel.current = false;
    await processGroup(group);
  }

  async function retryFailed() {
    for (const group of groups.filter((item) => item.status === "failed")) {
      if (cancel.current) break;
      await retry(group);
    }
  }

  function exportCsv() {
    const header = "product,machine_result,duration_seconds,attempts,request_id";
    const rows = groups.map((group) => [group.name, machineLabel(group), ((group.durationMs ?? 0) / 1000).toFixed(2), group.attempts, group.result?.requestId ?? ""].map(spreadsheetSafeCsvCell).join(","));
    download("labelverify-batch-results.csv", [header, ...rows].join("\r\n"), "text/csv;charset=utf-8");
  }

  if (active?.analysis && active.result) return <div><button className="btn ghost" onClick={() => setActiveId(null)} type="button">Back to batch</button><ResultWorkspace analysis={active.analysis} onStartOver={() => setActiveId(null)} result={active.result} sourcePanels={active.files} /></div>;

  if (stage === "select") return <section className="batch-select blueprint"><p className="kicker">Check a batch | step 1 of 3</p><h1>Choose a folder of label images</h1><p>No spreadsheet is required. Folder and filename cues create conservative product suggestions. You confirm every group before processing.</p>{selectionIssue ? <p className="form-error" role="alert">{selectionIssue}</p> : null}<button className="btn primary" onClick={() => input.current?.click()} type="button">Choose batch folder</button><input aria-label="Choose batch folder" ref={input} className="sr-only" {...({ webkitdirectory: "", directory: "" } as Record<string, string>)} multiple onChange={(event) => { choose(Array.from(event.target.files ?? [])); event.target.value = ""; }} type="file" /></section>;

  if (stage === "confirm") return (
    <section className="grouping-page">
      <div className="page-heading">
        <div>
          <p className="kicker">Check a batch | step 2 of 3</p>
          <h1>Confirm how the images group into products</h1>
          {groups.length > 300 ? <p className="form-error" role="alert">This batch currently has {groups.length} product groups. Merge related images until there are no more than 300 products.</p> : null}
        </div>
        <dl className="heading-stats">
          <div><dt>Images</dt><dd>{groups.reduce((sum, group) => sum + group.files.length, 0)}</dd></div>
          <div><dt>Suggested products</dt><dd>{groups.length}</dd></div>
          <div><dt>Need confirmation</dt><dd>{groups.filter((group) => !group.confirmed).length}</dd></div>
        </dl>
      </div>
      <div className="group-toolbar">
        <span>Select cards to merge or split. Rename any product before confirming.</span>
        <button className="btn secondary" disabled={selected.size < 2 || groups.filter((group) => selected.has(group.id)).reduce((sum, group) => sum + group.files.length, 0) > 3} onClick={mergeSelected} type="button">Merge selected</button>
        <button className="btn secondary" disabled={!groups.some((group) => selected.has(group.id) && group.files.length > 1)} onClick={splitSelected} type="button">Split into separate products</button>
        <button className="btn ghost" disabled={groups.some((group) => !group.name.trim())} onClick={() => setGroups((current) => current.map((group) => ({ ...group, name: group.name.trim(), confirmed: true, status: "ready" })))} type="button">Confirm all ready</button>
        <button className="btn primary" disabled={!groups.length || groups.length > 300 || groups.some((group) => !group.confirmed || !group.name.trim())} onClick={() => void run()} type="button">Run {groups.length} products</button>
      </div>
      <div className="group-wall">
        {groups.map((group, ordinal) => (
          <article className={`blueprint group-card ${group.confirmed ? "ready" : ""}`} key={group.id}>
            <label className="group-select"><input checked={selected.has(group.id)} onChange={(event) => setSelected((current) => { const next = new Set(current); if (event.target.checked) next.add(group.id); else next.delete(group.id); return next; })} type="checkbox" /> Select</label>
            <div className="section-row"><p className="kicker">Product {ordinal + 1}</p><span className={`status-tag ${group.confirmed ? "pass" : "warn"}`}>{group.confirmed ? "Ready" : "Needs confirmation"}</span></div>
            <div className="group-thumbs">{group.files.map((file) => <figure key={canonicalPath(file)}><FilePreview file={file} /><figcaption>{file.name}</figcaption></figure>)}</div>
            <label className="group-name">Product name<input aria-label={`Product ${ordinal + 1} name`} maxLength={80} onChange={(event) => update(group.id, { name: event.target.value, confirmed: false, status: "needs_confirmation" })} value={group.name} /></label>
            {!group.name.trim() ? <p className="form-error" role="alert">Enter a product name before confirming.</p> : null}
            <p>{group.reason}</p>
            <div className="section-row"><span>{group.files.length} of 3 images</span><button className="btn secondary" disabled={group.confirmed || !group.name.trim()} onClick={() => confirm(group.id)} type="button">{group.confirmed ? "Confirmed" : "Confirm as product"}</button></div>
          </article>
        ))}
      </div>
    </section>
  );

  return <section className="batch-run-page"><div className="page-heading"><div><p className="kicker">Check a batch | step 3 of 3</p><h1>{groups.length} products | {groups.reduce((sum, group) => sum + group.files.length, 0)} images</h1></div><div className="button-row"><button className="btn secondary" onClick={() => { cancel.current = true; controller.current?.abort(); }} type="button">Cancel remaining</button><button className="btn secondary" disabled={!failed} onClick={() => void retryFailed()} type="button">Retry failed ({failed})</button><button className="btn secondary" disabled={!completed} onClick={exportCsv} type="button">CSV</button><button className="btn secondary" disabled={!completed} onClick={() => download("labelverify-batch-details.json", JSON.stringify(groups.map((group) => ({ name: group.name, files: group.files.map((file) => file.name), result: group.result, error: group.error })), null, 2), "application/json")} type="button">Detailed JSON</button></div></div><div className="stats-strip">{[["Products", groups.length], ["Images", groups.reduce((sum, group) => sum + group.files.length, 0)], ["Processed", completed + failed], ["Remaining", remaining], ["Running", groups.filter((group) => group.status === "running").length], ["Queued", groups.filter((group) => group.status === "queued").length], ["Review", groups.filter((group) => group.result?.summary === "Review needed").length], ["Differences", groups.filter((group) => group.result?.summary === "Differences detected").length], ["Failed", failed], ["Active time", `${(elapsedMs / 1000).toFixed(1)}s`], ["Average", averageMs ? `${(averageMs / 1000).toFixed(1)}s` : "Pending"], ["ETA", averageMs ? `${Math.ceil(remaining * averageMs / 1000)}s` : "Pending"]].map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div><progress max={groups.length} value={completed + failed}>{completed + failed} of {groups.length}</progress><div className="batch-filters">{(["all", "attention", "complete", "failed"] as const).map((value) => <button aria-pressed={filter === value} key={value} onClick={() => setFilter(value)} type="button">{value}</button>)}</div><div className="table-wrap"><table><thead><tr><th>Product</th><th>Type</th><th>Images</th><th>Machine result</th><th>Why</th><th>Time</th><th>Attempts</th><th>Action</th></tr></thead><tbody>{filtered.map((group) => <tr key={group.id}><th scope="row">{group.name}</th><td>{group.analysis?.draft.beverageType?.replaceAll("_", " ") ?? "Pending"}</td><td>{group.files.length}</td><td>{machineLabel(group)}</td><td>{group.error ?? group.result?.checks.find((check) => check.state !== "Match")?.reasonText ?? "No exception"}</td><td>{group.durationMs == null ? "-" : `${(group.durationMs / 1000).toFixed(1)}s`}</td><td>{group.attempts}</td><td>{group.result ? <button className="show-btn" onClick={() => setActiveId(group.id)} type="button">Open</button> : group.status === "failed" ? <button className="show-btn" onClick={() => void retry(group)} type="button">Retry</button> : null}</td></tr>)}</tbody></table></div></section>;
}
