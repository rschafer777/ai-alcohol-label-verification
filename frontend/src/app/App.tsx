import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";

import { createHistoryClient, type HistoryClient } from "../api/history-client";
import { createVerificationClient, VerificationClientError } from "../api/verification-client";
import { limits } from "../api/generated-contract";
import { StateCard } from "../components/StateCard";
import type { Disposition } from "../components/status";
import type { AnalysisResult, BeverageType, CheckResult, HistorySummary, PublicError, SampleAdapter, VerificationClient, VerificationResult } from "../contracts/types";
import { BatchWorkspace } from "../features/batch/BatchWorkspace";
import { FirstRunTips } from "../features/home/FirstRunTips";
import { readFirstRunDismissed, writeFirstRunDismissed } from "../features/home/first-run";
import { Home } from "../features/home/Home";
import { History } from "../features/history/History";
import { enteredFields, hasApplicationValues, referenceFromApplication, type ApplicationInput } from "../features/intake/application";
import { createSampleAdapter } from "../features/intake/sample-adapter";
import { ProcessingStage, type ProcessingPhase } from "../features/verification/ProcessingStage";
import { ReviewWorkspace } from "../features/verification/ReviewWorkspace";
import type { ManualEvidenceSelection, ReviewImage, SlotUpload } from "../features/verification/review-images";
import { CORRECTION_API_FIELDS, imagesForFiles, revokeImages } from "../features/verification/single-flow";
import { AppShell } from "./AppShell";
import type { TrayDestination } from "./LeftTray";

type Route = { name: "home" } | { name: "batch" } | { name: "history"; recordId: string | null };
type SinglePhase = "idle" | "uploading" | "analyzing" | "verifying" | "complete" | "error";

interface AppProps {
  verificationClient?: VerificationClient;
  sampleAdapter?: SampleAdapter;
  historyClient?: HistoryClient;
}

function parseRoute(hash: string): Route {
  const path = hash.replace(/^#/, "");
  if (path.startsWith("/batch")) return { name: "batch" };
  if (path.startsWith("/history")) {
    const id = path.split("/")[2];
    return { name: "history", recordId: id ? decodeURIComponent(id) : null };
  }
  return { name: "home" };
}

function readTrayOpen(): boolean {
  try {
    return window.localStorage.getItem("lv.trayOpen") !== "0";
  } catch {
    return true;
  }
}

const TIMEOUT_ERROR: PublicError = { requestId: "browser", code: "client_deadline_exceeded", message: `This took longer than ${limits.browserDeadlineSeconds} seconds.`, retryable: true, nextAction: "Try again or check the label by eye", fieldOrPanel: null };

function correctedBeverageType(value: string): BeverageType | null {
  if (value === "malt_beverage" || value === "wine" || value === "distilled_spirits") return value;
  return null;
}

export function App({ verificationClient, sampleAdapter, historyClient }: AppProps) {
  const client = useMemo(() => verificationClient ?? createVerificationClient(), [verificationClient]);
  const samples = useMemo(() => sampleAdapter ?? createSampleAdapter(), [sampleAdapter]);
  const history = useMemo(() => historyClient ?? createHistoryClient(), [historyClient]);

  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.hash));
  // Under 900 px the tray is an overlay, so it starts closed and closes after each navigation.
  const narrow = () => typeof window.matchMedia === "function" && window.matchMedia("(max-width: 900px)").matches;
  const [trayOpen, setTrayOpen] = useState(() => readTrayOpen() && !narrow());
  const [helpOpen, setHelpOpen] = useState(false);
  const [firstRun, setFirstRun] = useState(() => !readFirstRunDismissed());
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyCap, setHistoryCap] = useState(500);
  const [recent, setRecent] = useState<HistorySummary[]>([]);
  const [deadlineSeconds, setDeadlineSeconds] = useState<number>(limits.browserDeadlineSeconds);
  const [batchFiles, setBatchFiles] = useState<File[] | null>(null);
  const [batchTitle, setBatchTitle] = useState("Batch");

  // Single-label session
  const [files, setFiles] = useState<File[]>([]);
  const [images, setImages] = useState<ReviewImage[]>([]);
  const [phase, setPhase] = useState<SinglePhase>("idle");
  const [processingPhase, setProcessingPhase] = useState<ProcessingPhase>("uploading");
  const [elapsed, setElapsed] = useState(0);
  const [uploadSeconds, setUploadSeconds] = useState<number | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<PublicError | null>(null);
  const [disposition, setDisposition] = useState<Disposition>(null);
  const [note, setNote] = useState("");
  const [saveState, setSaveState] = useState("");
  const [correctedIds, setCorrectedIds] = useState<Set<string>>(new Set());
  const [correctedBrand, setCorrectedBrand] = useState<string | null>(null);
  const [upload, setUpload] = useState<SlotUpload | null>(null);
  const [sampleLoading, setSampleLoading] = useState(false);
  const [addedFrom, setAddedFrom] = useState<number>(Number.POSITIVE_INFINITY);
  const [comparedWith, setComparedWith] = useState<string[] | null>(null);
  const controller = useRef<AbortController | null>(null);
  const timer = useRef<number | null>(null);
  const deadline = useRef<number | null>(null);

  const refreshRecent = useCallback(async () => {
    try {
      const page = await history.list({ pageSize: 3 });
      setHistoryTotal(page.total);
      setHistoryCap(page.cap);
      setRecent(page.items);
    } catch {
      /* the Recent table simply stays empty when history is unreachable */
    }
  }, [history]);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      void refreshRecent();
      void history.meta().then((meta) => { if (meta) { setDeadlineSeconds(meta.limits.browserDeadlineSeconds); setHistoryCap(meta.history.cap); } });
    }, 0);
    const onHash = () => setRoute(parseRoute(window.location.hash));
    window.addEventListener("hashchange", onHash);
    return () => {
      window.clearTimeout(handle);
      window.removeEventListener("hashchange", onHash);
      controller.current?.abort();
      if (timer.current !== null) window.clearInterval(timer.current);
      if (deadline.current !== null) window.clearTimeout(deadline.current);
    };
  }, [history, refreshRecent]);

  function go(next: Route) {
    const hash = next.name === "home" ? "#/" : next.name === "batch" ? "#/batch" : next.recordId ? `#/history/${encodeURIComponent(next.recordId)}` : "#/history";
    if (window.location.hash !== hash) window.location.hash = hash;
    setRoute(next);
  }

  function stopTimers() {
    if (timer.current !== null) window.clearInterval(timer.current);
    timer.current = null;
    if (deadline.current !== null) window.clearTimeout(deadline.current);
    deadline.current = null;
  }

  function resetSession(keepFiles = false) {
    controller.current?.abort();
    stopTimers();
    if (!keepFiles) {
      revokeImages(images);
      setFiles([]);
      setImages([]);
    }
    setAnalysis(null);
    setResult(null);
    setError(null);
    setElapsed(0);
    setUploadSeconds(null);
    setDisposition(null);
    setNote("");
    setSaveState("");
    setCorrectedIds(new Set());
    setCorrectedBrand(null);
    setUpload(null);
    setAddedFrom(Number.POSITIVE_INFINITY);
    setComparedWith(null);
    setPhase("idle");
  }

  function startOver() {
    resetSession();
    go({ name: "home" });
    void refreshRecent();
  }

  function fail(caught: unknown, signal: AbortSignal) {
    if (signal.aborted) return;
    setError(caught instanceof VerificationClientError ? caught.detail : { requestId: "unavailable", code: "network_unavailable", message: "The verifier could not be reached.", retryable: true, nextAction: "Check the connection and retry", fieldOrPanel: null });
    setPhase("error");
  }

  async function runSingle(selected: File[], application: ApplicationInput | null = null) {
    controller.current?.abort();
    stopTimers();
    const nextController = new AbortController();
    controller.current = nextController;
    revokeImages(images);
    setFiles(selected);
    setImages(imagesForFiles(selected));
    setAddedFrom(Number.POSITIVE_INFINITY);
    setError(null);
    setResult(null);
    setAnalysis(null);
    setDisposition(null);
    setNote("");
    setSaveState("");
    setCorrectedIds(new Set());
    setCorrectedBrand(null);
    setComparedWith(null);
    setPhase("uploading");
    setProcessingPhase("uploading");
    setUploadSeconds(null);
    go({ name: "home" });
    const startedAt = performance.now();
    setElapsed(0);
    timer.current = window.setInterval(() => setElapsed((performance.now() - startedAt) / 1000), 100);
    deadline.current = window.setTimeout(() => {
      nextController.abort();
      setError(TIMEOUT_ERROR);
      setPhase("error");
      stopTimers();
    }, deadlineSeconds * 1000);
    try {
      const nextAnalysis = await client.analyze({
        panels: selected,
        signal: nextController.signal,
        onUploadProgress: (progress) => {
          if (progress.loaded >= progress.total) {
            setUploadSeconds((performance.now() - startedAt) / 1000);
            setProcessingPhase("reading");
            setPhase("analyzing");
          }
        },
      });
      if (nextController.signal.aborted) return;
      setProcessingPhase("checking");
      setAnalysis(nextAnalysis);
      // Application values entered by the reviewer turn the label read into a comparison
      // with the application: the same images are checked against the typed record.
      const reference = application && hasApplicationValues(application) ? referenceFromApplication(application, nextAnalysis) : null;
      if (reference && application) {
        const compared = await client.verify({ reference, panels: selected, signal: nextController.signal });
        if (nextController.signal.aborted) return;
        setResult(compared);
        setComparedWith(enteredFields(application));
        if (application.brandName.trim()) setCorrectedBrand(application.brandName.trim());
        setPhase("complete");
        void refreshRecent();
        return;
      }
      if (!nextAnalysis.verification) {
        setError({ requestId: nextAnalysis.requestId, code: "beverage_type_uncertain", message: "The beverage type could not be inferred reliably from the submitted images.", retryable: true, nextAction: "Add a clearer class or type panel and retry", fieldOrPanel: "panels" });
        setPhase("error");
        return;
      }
      setResult(nextAnalysis.verification);
      setPhase("complete");
      void refreshRecent();
    } catch (caught) {
      fail(caught, nextController.signal);
    } finally {
      if (controller.current === nextController) stopTimers();
      setElapsed((performance.now() - startedAt) / 1000);
    }
  }

  async function loadSample() {
    setSampleLoading(true);
    try {
      const loaded = await samples.load();
      await runSingle(loaded.panels.slice(0, 3));
    } catch {
      setError({ requestId: "sample", code: "sample_unavailable", message: "The built-in sample could not be loaded.", retryable: true, nextAction: "Choose your own images", fieldOrPanel: null });
      setPhase("error");
    } finally {
      setSampleLoading(false);
    }
  }

  async function addImage(file: File, slot: number) {
    if (!result || !analysis) return;
    const nextController = new AbortController();
    controller.current = nextController;
    setUpload({ slot, name: file.name, pct: 0, stage: "Uploading…" });
    const historyId = result.historyId;
    try {
      let nextAnalysis: AnalysisResult;
      if (historyId && client.addPanel) {
        nextAnalysis = await client.addPanel({
          historyId,
          expectedRevision: result.revision ?? 1,
          panel: file,
          signal: nextController.signal,
          onUploadProgress: (progress) => {
            const pct = Math.min(60, Math.round((progress.loaded / Math.max(1, progress.total)) * 60));
            setUpload({ slot, name: file.name, pct, stage: pct >= 60 ? "Reading label…" : "Uploading…" });
          },
        });
      } else {
        nextAnalysis = await client.analyze({ panels: [...files, file].slice(0, 3), signal: nextController.signal });
      }
      if (nextController.signal.aborted) return;
      if (!nextAnalysis.verification) throw new VerificationClientError({ requestId: nextAnalysis.requestId, code: "beverage_type_uncertain", message: "The beverage type could not be inferred from the enlarged image set.", retryable: true, nextAction: "Confirm the type", fieldOrPanel: "panels" });
      setUpload({ slot, name: file.name, pct: 90, stage: "Checking rules…" });
      const nextFiles = [...files, file].slice(0, 3);
      const nextAddedFrom = Math.min(addedFrom, files.length);
      revokeImages(images);
      setFiles(nextFiles);
      setImages(imagesForFiles(nextFiles, nextAddedFrom));
      setAddedFrom(nextAddedFrom);
      setAnalysis(nextAnalysis);
      setResult(nextAnalysis.verification);
      setCorrectedIds(new Set());
      setUpload(null);
      void refreshRecent();
    } catch (caught) {
      setUpload(null);
      if (!nextController.signal.aborted) setSaveState(caught instanceof VerificationClientError ? `${caught.detail.message} ${caught.detail.nextAction}.` : "The image could not be added.");
    }
  }

  async function correct(check: CheckResult, value: string, locator?: ManualEvidenceSelection) {
    if (!analysis || !result?.historyId || !history.correct) return;
    const field = CORRECTION_API_FIELDS[check.checkId];
    if (!field) return;
    const evidenceRef = check.evidenceRef ?? (check.checkId === "beverage_type"
      ? result.checks.find((item) => item.checkId === "class_type")?.evidenceRef
      : null);
    if (!evidenceRef && !locator) {
      setSaveState("Select area, then drag a rectangle around the visible label text before saving.");
      return;
    }
    const family = field === "beverage_type" ? correctedBeverageType(value) : null;
    if (field === "beverage_type" && !family) {
      setSaveState("Choose Beer / malt, Wine, or Distilled spirits.");
      return;
    }
    const sourceLocator = evidenceRef ? { evidenceRef } : locator;
    if (!sourceLocator) return;
    setSaveState("Saving correction...");
    try {
      const correction = field === "beverage_type"
        ? {
            field: "beverage_type" as const,
            family: family as BeverageType,
            ...sourceLocator,
          }
        : { field, visibleText: value, ...sourceLocator };
      const nextResult = await history.correct(result.historyId, {
        expectedRevision: result.revision ?? 1,
        reason: "Reviewer corrected the field from visible retained label evidence",
        corrections: [correction],
      });
      setResult(nextResult);
      setCorrectedIds(new Set([...correctedIds, check.checkId]));
      if (field === "brand_name") setCorrectedBrand(value);
      if (field === "beverage_type") {
        setAnalysis({ ...analysis, draft: { ...analysis.draft, beverageType: family } });
      }
      setSaveState("");
      void refreshRecent();
    } catch (caught) {
      setSaveState(caught instanceof Error ? caught.message : "The correction could not be saved.");
    }
  }

  async function confirmType(type: BeverageType) {
    const check = result?.checks.find((item) => item.checkId === "beverage_type");
    if (!check) return;
    await correct(check, type);
  }

  async function saveAndNext() {
    if (result?.historyId) {
      const ok = await history.setDisposition(result.historyId, disposition, note);
      setSaveState(ok ? "Saved" : "Could not save. Retry before leaving.");
      if (!ok) return;
    }
    startOver();
  }

  function navigate(destination: TrayDestination) {
    setHelpOpen(false);
    if (narrow()) setTrayOpen(false);
    if (destination === "home") {
      if (phase !== "idle") resetSession();
      go({ name: "home" });
      void refreshRecent();
    } else if (destination === "batch") {
      go({ name: "batch" });
    } else go({ name: "history", recordId: null });
  }

  const current: TrayDestination | null = route.name === "home" ? "home" : route.name === "batch" ? "batch" : "history";
  const [batchScreenTitle, setBatchScreenTitle] = useState("Batch");
  const screenTitle = route.name === "home"
    ? (phase === "idle" ? "Check one label" : phase === "complete" ? "Review" : phase === "error" ? "Check one label" : "Reading label")
    : route.name === "batch" ? batchScreenTitle : "History";

  let body: ReactNode;
  if (route.name === "batch") {
    body = batchFiles
      ? <BatchWorkspace batchName={batchTitle} historyClient={historyClient} initialFiles={batchFiles} onExit={() => { setBatchFiles(null); go({ name: "home" }); }} onHistoryChanged={() => void refreshRecent()} onScreenTitle={setBatchScreenTitle} verificationClient={client} />
      : <div className="states"><StateCard error={{ requestId: "batch", code: "history_empty", message: "Choose a folder of label images from the home screen to start a batch.", retryable: false, nextAction: "Choose a folder on the home screen", fieldOrPanel: null }} onPrimary={() => go({ name: "home" })} standalone /></div>;
  } else if (route.name === "history") {
    body = <History historyClient={historyClient} initialRecordId={route.recordId} onCountChange={(total, cap) => { setHistoryTotal(total); setHistoryCap(cap); }} />;
  } else if (phase === "uploading" || phase === "analyzing" || phase === "verifying") {
    body = <ProcessingStage deadlineSeconds={deadlineSeconds} elapsedSeconds={elapsed} files={files} onCancel={startOver} phase={processingPhase} uploadSeconds={uploadSeconds} />;
  } else if (phase === "error" && error) {
    body = <div className="states"><StateCard error={error} onPrimary={error.retryable && files.length ? () => void runSingle(files) : startOver} onSecondary={startOver} standalone /></div>;
  } else if (phase === "complete" && result && analysis) {
    body = (
      <ReviewWorkspace
        addedFrom={addedFrom}
        beverageType={analysis.draft.beverageType}
        brandName={correctedBrand ?? analysis.draft.brandName ?? "Product label"}
        comparedWith={comparedWith}
        correctedIds={correctedIds}
        disposition={disposition}
        images={images}
        imported={analysis.draft.isImported}
        note={note}
        onAddImage={files.length < 3 ? (file, slot) => void addImage(file, slot) : null}
        onBack={startOver}
        onConfirmType={(type) => void confirmType(type)}
        onCorrect={(check, value) => void correct(check, value)}
        onDisposition={setDisposition}
        onNote={setNote}
        onSave={() => void saveAndNext()}
        result={result}
        saveState={saveState}
        upload={upload}
      />
    );
  } else {
    body = (
      <>
        <Home historyCap={historyCap} historyTotal={historyTotal} onBatch={(selected) => { setBatchFiles(selected); const first = selected[0] as (File & { webkitRelativePath?: string }) | undefined; setBatchTitle(first?.webkitRelativePath?.split("/")[0] || "Batch"); go({ name: "batch" }); }} onOpenHistory={() => go({ name: "history", recordId: null })} onOpenRecord={(id) => go({ name: "history", recordId: id })} onSample={() => void loadSample()} onSingle={(selected, application) => void runSingle(selected, application)} recent={recent} sampleLoading={sampleLoading} />
        {firstRun ? <FirstRunTips onClose={() => setFirstRun(false)} onDismissForever={() => { writeFirstRunDismissed(); setFirstRun(false); }} /> : null}
      </>
    );
  }

  return (
    <AppShell current={current} helpOpen={helpOpen} historyCap={historyCap} historyTotal={historyTotal} onNavigate={navigate} onToggleHelp={() => setHelpOpen((value) => !value)} onToggleTray={() => setTrayOpen((value) => { try { window.localStorage.setItem("lv.trayOpen", value ? "0" : "1"); } catch { /* ignore */ } return !value; })} screenTitle={screenTitle} trayOpen={trayOpen}>
      {body}
    </AppShell>
  );
}
