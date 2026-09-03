import { useCallback, useEffect, useMemo, useRef, useState, type ReactElement } from "react";

import { createHistoryClient, type HistoryClient } from "../../api/history-client";
import { VerificationClientError } from "../../api/verification-client";
import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import { Spinner } from "../../components/Spinner";
import { FilePreview } from "../../components/FilePreview";
import { StateCard } from "../../components/StateCard";
import type { Disposition } from "../../components/status";
import type { GroupingImage, PublicError, VerificationClient } from "../../contracts/types";
import { slotTitle } from "../verification/review-images";
import { ReviewWorkspace } from "../verification/ReviewWorkspace";
import { batchProgress, confirmAllReady, confirmGroup, groupFromSuggestion, isException, mergeGroups, moveImage, renameGroup, splitGroup, summaryOf, type BatchGroup, type BatchImage, type BatchStage } from "./batch-state";
import { BatchRail } from "./BatchRail";
import { BatchRun } from "./BatchRun";
import { canonicalPath, spreadsheetSafeCsvCell, suggestProductGroups } from "./grouping";
import { GroupingWall } from "./GroupingWall";

interface BatchWorkspaceProps {
  initialFiles: File[];
  batchName: string;
  verificationClient: VerificationClient;
  historyClient?: HistoryClient;
  onExit: () => void;
  onHistoryChanged: () => void;
  onScreenTitle: (title: string) => void;
}

function download(filename: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function toPublicError(caught: unknown): PublicError {
  if (caught instanceof VerificationClientError) return caught.detail;
  return { requestId: "unavailable", code: "network_unavailable", message: "The verifier could not be reached.", retryable: true, nextAction: "Check the connection and retry", fieldOrPanel: null };
}

export function BatchWorkspace({ initialFiles, batchName, verificationClient, historyClient, onExit, onHistoryChanged, onScreenTitle }: BatchWorkspaceProps): ReactElement {
  const history = useMemo(() => historyClient ?? createHistoryClient(), [historyClient]);
  const [images] = useState<BatchImage[]>(() => initialFiles.map((file, index) => ({ id: `img-${index + 1}`, file, url: URL.createObjectURL(file), path: canonicalPath(file) })));
  const imageMap = useMemo(() => new Map(images.map((image) => [image.id, image])), [images]);
  const [stage, setStage] = useState<BatchStage>("analyzing");
  const [analyzed, setAnalyzed] = useState(0);
  const [failed, setFailed] = useState(0);
  const [analysisMs, setAnalysisMs] = useState(0);
  const [activeImageName, setActiveImageName] = useState("");
  const [groups, setGroups] = useState<BatchGroup[]>([]);
  const [undoStack, setUndoStack] = useState<BatchGroup[][]>([]);
  const [activeMs, setActiveMs] = useState(0);
  const [retries, setRetries] = useState(0);
  const [openId, setOpenId] = useState<string | null>(null);
  const [saveState, setSaveState] = useState("");
  const [fatal, setFatal] = useState<PublicError | null>(null);
  const cancel = useRef(false);
  const controller = useRef<AbortController | null>(null);
  const timer = useRef<number | null>(null);
  const started = useRef(false);
  const groupsRef = useRef<BatchGroup[]>([]);
  useEffect(() => {
    groupsRef.current = groups;
  }, [groups]);

  const patchGroup = useCallback((id: string, patch: Partial<BatchGroup> | ((group: BatchGroup) => Partial<BatchGroup>)) => {
    setGroups((current) => current.map((group) => group.id === id ? { ...group, ...(typeof patch === "function" ? patch(group) : patch) } : group));
  }, []);

  useEffect(() => () => {
    cancel.current = true;
    controller.current?.abort();
    if (timer.current !== null) window.clearInterval(timer.current);
    images.forEach((image) => URL.revokeObjectURL(image.url));
  }, [images]);

  useEffect(() => {
    onScreenTitle(openId ? "Batch · review" : stage === "analyzing" ? "Batch · analyzing" : stage === "confirmation" || stage === "grouping" ? "Batch · confirm groups" : "Batch · run");
  }, [openId, stage, onScreenTitle]);

  const edit = useCallback((update: (current: BatchGroup[]) => BatchGroup[]) => {
    setGroups((current) => {
      const next = update(current);
      if (next !== current) setUndoStack((stack) => [...stack.slice(-19), current]);
      return next;
    });
  }, []);

  // Step 1: read every image once (not stored), then ask the server for grouping suggestions.
  useEffect(() => {
    if (started.current) return;
    started.current = true;
    let active = true;
    (async () => {
      const startedAt = performance.now();
      const rows: GroupingImage[] = [];
      const failedIds = new Set<string>();
      for (const image of images) {
        if (!active || cancel.current) return;
        setActiveImageName(image.file.name);
        const nextController = new AbortController();
        controller.current = nextController;
        try {
          const analysis = await verificationClient.analyze({ panels: [image.file], signal: nextController.signal, persist: false });
          setAnalyzed((value) => value + 1);
          rows.push({ imageId: image.id, fileName: image.file.name, path: image.path, brandName: analysis.draft.brandName, classType: analysis.draft.classType, beverageType: analysis.beverageInference?.type ?? analysis.draft.beverageType, typeConfidence: analysis.beverageInference?.confidence ?? (analysis.draft.beverageType ? "medium" : "low"), failed: false });
        } catch {
          if (nextController.signal.aborted) return;
          failedIds.add(image.id);
          setFailed((value) => value + 1);
          rows.push({ imageId: image.id, fileName: image.file.name, path: image.path, failed: true });
        }
        setAnalysisMs(performance.now() - startedAt);
      }
      setActiveImageName("");
      if (!active) return;
      try {
        if (verificationClient.suggestGroups) {
          const suggestion = await verificationClient.suggestGroups({ images: rows });
          setGroups(suggestion.groups.map(groupFromSuggestion));
        } else {
          setGroups(suggestProductGroups(images.filter((image) => !failedIds.has(image.id)).map((image) => image.file)).map((group, index) => groupFromSuggestion({ groupId: `group-${index + 1}`, panelIds: group.files.map((file) => images.find((image) => image.file === file)?.id ?? ""), suggestedName: group.name, inferredType: null, confidence: "low", status: "needs_review", reasons: [group.reason], conflict: false })));
        }
        setStage("confirmation");
      } catch (caught) {
        setFatal(toPublicError(caught));
      }
    })();
    return () => { active = false; };
  }, [images, verificationClient]);

  // Step 3: run confirmed products one at a time through the same analysis endpoint.
  async function processGroup(id: string): Promise<void> {
    const group = groupsRef.current.find((item) => item.id === id);
    if (!group) return;
    const files = group.imageIds.map((imageId) => imageMap.get(imageId)?.file).filter((file): file is File => !!file);
    const nextController = new AbortController();
    controller.current = nextController;
    patchGroup(id, (current) => ({ runStatus: "running", attempts: current.attempts + 1, error: null }));
    const t0 = performance.now();
    try {
      const analysis = await verificationClient.analyze({ panels: files, signal: nextController.signal });
      const durationMs = performance.now() - t0;
      if (cancel.current || nextController.signal.aborted) patchGroup(id, { runStatus: "cancelled", durationMs });
      else if (analysis.verification) patchGroup(id, { analysis, result: analysis.verification, runStatus: "complete", durationMs });
      else patchGroup(id, { analysis, runStatus: "failed", durationMs, error: { requestId: analysis.requestId, code: "beverage_type_uncertain", message: "Beverage type needs human confirmation before the checks can run.", retryable: true, nextAction: "Confirm the type", fieldOrPanel: null } });
    } catch (caught) {
      const durationMs = performance.now() - t0;
      if (cancel.current || nextController.signal.aborted) patchGroup(id, { runStatus: "cancelled", durationMs });
      else patchGroup(id, { runStatus: "failed", durationMs, error: toPublicError(caught) });
    }
    onHistoryChanged();
  }

  async function runAll(ids: string[]) {
    cancel.current = false;
    setStage("running");
    const startedAt = performance.now() - activeMs;
    timer.current = window.setInterval(() => setActiveMs(performance.now() - startedAt), 100);
    setGroups((current) => current.map((group) => ids.includes(group.id) ? { ...group, runStatus: "queued", error: null } : group));
    try {
      for (const id of ids) {
        if (cancel.current) break;
        await processGroup(id);
      }
    } finally {
      if (timer.current !== null) window.clearInterval(timer.current);
      timer.current = null;
      setActiveMs(performance.now() - startedAt);
    }
    setGroups((current) => {
      const next = current.map((group) => group.runStatus === "queued" ? { ...group, runStatus: "cancelled" as const } : group);
      const anyFailed = next.some((group) => group.runStatus === "failed");
      const anyCancelled = next.some((group) => group.runStatus === "cancelled");
      setStage(cancel.current || anyCancelled ? "cancelled" : anyFailed ? "completed_with_errors" : "completed");
      return next;
    });
  }

  function start() {
    void runAll(groups.map((group) => group.id));
  }

  function retryFailed() {
    const ids = groups.filter((group) => group.runStatus === "failed" || group.runStatus === "cancelled").map((group) => group.id);
    if (!ids.length) return;
    setRetries((value) => value + ids.length);
    void runAll(ids);
  }

  function retryOne(id: string) {
    setRetries((value) => value + 1);
    void runAll([id]);
  }

  function nextException(afterId: string | null) {
    const list = groups.filter((group) => group.result && isException(group) && group.disposition === null);
    if (!list.length) { setOpenId(null); return; }
    const index = afterId ? list.findIndex((group) => group.id === afterId) : -1;
    const next = list[index + 1] ?? list[0];
    if (next) setOpenId(next.id);
  }

  async function saveDisposition(group: BatchGroup, disposition: Disposition, note: string) {
    patchGroup(group.id, { disposition, note });
    const historyId = group.result?.historyId;
    if (!historyId) return;
    const ok = await history.setDisposition(historyId, disposition, note);
    setSaveState(ok ? "Saved" : "Could not save. Retry before leaving.");
    if (ok) onHistoryChanged();
  }

  function exportCsv() {
    const header = "product,type,images,machine_result,why,duration_seconds,attempts,disposition,note,request_id";
    const rows = groups.map((group) => [group.name, group.analysis?.draft.beverageType ?? group.inferredType ?? "", group.imageIds.length, summaryOf(group) ?? "", group.error?.message ?? "", ((group.durationMs ?? 0) / 1000).toFixed(2), group.attempts, group.disposition ?? "", group.note, group.result?.requestId ?? ""].map(spreadsheetSafeCsvCell).join(","));
    download("labelverify-batch-results.csv", [header, ...rows].join("\r\n"), "text/csv;charset=utf-8");
  }

  function exportJson() {
    download("labelverify-batch-details.json", JSON.stringify(groups.map((group) => ({ name: group.name, files: group.imageIds.map((id) => imageMap.get(id)?.file.name), status: group.runStatus, attempts: group.attempts, durationMs: group.durationMs, disposition: group.disposition, note: group.note, result: group.result, error: group.error })), null, 2), "application/json");
  }

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) return;
      if (openId === null && (stage === "running" || stage === "completed" || stage === "completed_with_errors" || stage === "cancelled") && event.key.toLowerCase() === "e") nextException(null);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  if (fatal) return <div className="states"><StateCard error={fatal} onPrimary={onExit} onSecondary={onExit} standalone /></div>;

  const open = openId ? groups.find((group) => group.id === openId) : null;
  if (open?.result && open.analysis) {
    const files = open.imageIds.map((id) => imageMap.get(id)).filter((image): image is BatchImage => !!image);
    const reviewImages = files.map((image, index) => ({ src: image.url, name: image.file.name, alt: `${image.file.name} label image`, title: slotTitle(index, files.length) }));
    return (
      <ReviewWorkspace
        beverageType={open.analysis.draft.beverageType}
        brandName={open.analysis.draft.brandName ?? open.name}
        disposition={open.disposition}
        imported={open.analysis.draft.isImported}
        images={reviewImages}
        inBatch
        note={open.note}
        onBack={() => { setOpenId(null); setSaveState(""); }}
        onDisposition={(value) => void saveDisposition(open, value, open.note)}
        onNextException={() => nextException(open.id)}
        onNote={(value) => patchGroup(open.id, { note: value })}
        onSave={() => void saveDisposition(open, open.disposition, open.note)}
        rail={<BatchRail currentId={open.id} groups={groups} images={imageMap} onOpen={(id) => { setOpenId(id); setSaveState(""); }} />}
        result={open.result}
        saveState={saveState}
      />
    );
  }

  if (stage === "analyzing") {
    const total = images.length;
    const done = analyzed + failed;
    const averageMs = done ? analysisMs / done : 0;
    const ratePerMinute = averageMs ? 60_000 / averageMs : 0;
    const remainingMs = averageMs * Math.max(0, total - done);
    return (
      <main aria-live="polite" className="batch-analyzing" data-screen-label="Batch analyzing">
        <div className="processing-head"><h6 className="kicker">Check a batch · step 1 of 3</h6><button className="btn btn-ghost" onClick={() => { cancel.current = true; controller.current?.abort(); onExit(); }} type="button">Cancel</button></div>
        <section className="card blueprint processing-card">
          <Corners />
          <div className="processing-main">
            <div className="processing-title"><h2 tabIndex={-1}>Reading {total} image{total === 1 ? "" : "s"}</h2><span className="elapsed">{(analysisMs / 1000).toFixed(1)} s elapsed</span></div>
            <div className="batch-live-progress"><div><strong>{done} / {total} processed</strong><span className="text-muted">{activeImageName ? `Reading ${activeImageName}` : "Preparing results"}</span></div><progress aria-label={`${done} of ${total} batch images processed`} max={total} value={done} /><div className="batch-progress-metrics"><span>{averageMs ? `${(averageMs / 1000).toFixed(1)} s per image` : "Measuring speed"}</span><span>{ratePerMinute ? `${ratePerMinute.toFixed(1)} images per minute` : "Rate pending"}</span><span>{done < total && remainingMs ? `About ${Math.ceil(remainingMs / 1000)} s remaining` : done === total ? "Analysis complete" : "Estimate pending"}</span><span>{failed} skipped after read error</span></div></div>
            <ol className="stages">
              <li className="reached"><span className="stage-label">{done < total ? <Spinner /> : icons.check()} Analyze</span><span className="stage-detail text-muted">{done} of {total} read · {failed} failed{done ? ` · ${(analysisMs / done / 1000).toFixed(1)} s per image` : ""}</span></li>
              <li className={done === total ? "reached" : ""}><span className="stage-label">{icons.clock()} Confirm groups</span><span className="stage-detail text-muted">We suggest one product per brand or folder; you confirm.</span></li>
              <li><span className="stage-label">{icons.clock()} Work exceptions</span><span className="stage-detail text-muted">Only what needs a human.</span></li>
            </ol>
            <div className="analyze-grid">
              {images.map((image, index) => <div className={`scan-thumb${index < done ? " done" : ""}`} key={image.id}><FilePreview alt={image.file.name} file={image.file} />{index === done ? <div aria-hidden="true" className="scan-sweep" /> : null}</div>)}
            </div>
            <p className="processing-note text-muted">Every image is read once so we can group it by the brand on the label. Nothing is stored until you confirm the products.</p>
          </div>
        </section>
      </main>
    );
  }

  if (stage === "confirmation" || stage === "grouping") {
    return (
      <GroupingWall
        analysisMs={analysisMs}
        analyzed={analyzed}
        canUndo={undoStack.length > 0}
        failed={failed}
        groups={groups}
        images={imageMap}
        onConfirm={(id) => setGroups((current) => confirmGroup(current, id))}
        onConfirmAll={() => setGroups((current) => confirmAllReady(current))}
        onDropImage={(imageId, target) => edit((current) => moveImage(current, imageId, target))}
        onMerge={(ids) => edit((current) => mergeGroups(current, ids))}
        onMove={(imageId, target) => edit((current) => moveImage(current, imageId, target))}
        onRename={(id, name) => setGroups((current) => renameGroup(current, id, name))}
        onRun={start}
        onSplit={(id) => edit((current) => splitGroup(current, id))}
        onUndo={() => setUndoStack((stack) => { const previous = stack.at(-1); if (previous) setGroups(previous); return stack.slice(0, -1); })}
      />
    );
  }

  const progress = batchProgress(groups, groups.reduce((sum, group) => sum + group.imageIds.length, 0), stage, activeMs, retries);
  return (
    <BatchRun
      batchName={batchName}
      groups={groups}
      images={imageMap}
      onBack={() => { if (stage === "running") { cancel.current = true; controller.current?.abort(); } setStage("confirmation"); }}
      onCancel={() => { cancel.current = true; controller.current?.abort(); }}
      onExportCsv={exportCsv}
      onExportJson={exportJson}
      onNextException={() => nextException(null)}
      onOpen={(id) => { setOpenId(id); setSaveState(""); }}
      onRetry={retryOne}
      onRetryFailed={retryFailed}
      progress={progress}
    />
  );
}
