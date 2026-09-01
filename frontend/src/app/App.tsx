import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";

import { limits, type PublicError, type VerificationResult } from "../api/generated-contract";
import { createVerificationClient, VerificationClientError } from "../api/verification-client";
import type { SampleAdapter, VerificationClient } from "../contracts/types";
import { BatchWorkspace } from "../features/batch/BatchWorkspace";
import { IntakeForm } from "../features/intake/IntakeForm";
import {
  ACCEPTED_IMAGE_TYPES,
  draftHasContent,
  EMPTY_DRAFT,
  MAX_AGGREGATE_BYTES,
  MAX_FILE_BYTES,
  MAX_PANELS,
  referenceToDraft,
  toReference,
  validateDraft,
  type DraftErrors,
  type DraftField,
  type ReferenceDraft,
} from "../features/intake/model";
import { createSampleAdapter } from "../features/intake/sample-adapter";
import { ResultWorkspace } from "../features/verification/ResultWorkspace";
import "./styles.css";

type Phase = "intake" | "validating" | "submitting" | "processing" | "complete" | "cancelled" | "error";

interface AppProps {
  verificationClient?: VerificationClient;
  sampleAdapter?: SampleAdapter;
}

const FIELD_ORDER: Array<keyof DraftErrors> = [
  "caseLabel",
  "brandName",
  "classType",
  "abvPercent",
  "proof",
  "netContentsValue",
  "producerNameAddress",
  "countryOfOrigin",
  "panels",
];

function browserError(code: string, message: string, nextAction: string): PublicError {
  return { requestId: "browser", code, message, retryable: true, nextAction, fieldOrPanel: null };
}

function ResetDialog({ onCancel, onConfirm }: { onCancel: () => void; onConfirm: () => void }) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    cancelRef.current?.focus();
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") onCancel();
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onCancel]);

  return (
    <div className="dialog-backdrop">
      <div aria-describedby="reset-description" aria-labelledby="reset-title" aria-modal="true" className="dialog" role="dialog">
        <h2 id="reset-title">Start over and clear this session?</h2>
        <p id="reset-description">This clears the form, selected images, current result, evidence selection, and reviewer notes from this browser tab.</p>
        <div className="dialog-actions">
          <button className="button secondary" onClick={onCancel} ref={cancelRef} type="button">Cancel</button>
          <button className="button danger" onClick={onConfirm} type="button">Confirm and clear</button>
        </div>
      </div>
    </div>
  );
}

function ErrorBanner({ error, onRetry, onFocusLocator }: { error: PublicError; onRetry: () => void; onFocusLocator: () => void }) {
  return (
    <section className="status-banner error-banner" aria-labelledby="error-heading" role="alert">
      <div>
        <p className="eyebrow">No result was issued</p>
        <h2 id="error-heading">{error.message}</h2>
        <p>{error.nextAction}</p>
        {error.requestId && error.requestId !== "browser" && error.requestId !== "unavailable" ? <p className="request-id">Request: {error.requestId}</p> : null}
      </div>
      <div className="banner-actions">
        {error.fieldOrPanel ? <button className="button secondary" onClick={onFocusLocator} type="button">Go to the affected item</button> : null}
        {error.retryable ? <button className="button primary" onClick={onRetry} type="button">Retry verification</button> : null}
      </div>
    </section>
  );
}

function ProcessingBanner({ phase, elapsed, onCancel }: { phase: Phase; elapsed: number; onCancel: () => void }) {
  const text = phase === "submitting" ? "Uploading label panels" : "Reading and checking the label";
  return (
    <section className="status-banner processing-banner" aria-live="polite" aria-labelledby="processing-heading">
      <div className="spinner" aria-hidden="true" />
      <div>
        <p className="eyebrow">Verification in progress</p>
        <h2 id="processing-heading">{text}</h2>
        <p>Elapsed time: {elapsed.toFixed(1)} seconds. Most normal labels should finish in about 5 seconds.</p>
      </div>
      <button className="button secondary" onClick={onCancel} type="button">Cancel verification</button>
    </section>
  );
}

function focusFirstError(errors: DraftErrors) {
  const first = FIELD_ORDER.find((field) => errors[field]);
  if (!first) return;
  const targetId = first === "panels" ? "choose-panels" : `field-${first}`;
  window.setTimeout(() => document.getElementById(targetId)?.focus(), 0);
}

function fieldIdFromLocator(locator?: string | null): string | null {
  if (!locator) return null;
  const normalized = locator.replace(/^reference\./, "");
  const allowed = new Set([
    "caseLabel",
    "brandName",
    "classType",
    "abvPercent",
    "proof",
    "netContentsValue",
    "netContentsUnit",
    "producerNameAddress",
    "isImported",
    "countryOfOrigin",
  ]);
  if (allowed.has(normalized)) return `field-${normalized}`;
  if (/^panel-[1-6]$/.test(normalized) || normalized === "panels") return "choose-panels";
  return null;
}

export function App({ verificationClient, sampleAdapter }: AppProps) {
  const client = useMemo(() => verificationClient ?? createVerificationClient(), [verificationClient]);
  const samples = useMemo(() => sampleAdapter ?? createSampleAdapter(), [sampleAdapter]);
  const [workspace, setWorkspace] = useState<"single" | "batch">("single");
  const [draft, setDraft] = useState<ReferenceDraft>(EMPTY_DRAFT);
  const [panels, setPanels] = useState<File[]>([]);
  const [errors, setErrors] = useState<DraftErrors>({});
  const [phase, setPhase] = useState<Phase>("intake");
  const [elapsed, setElapsed] = useState(0);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [publicError, setPublicError] = useState<PublicError | null>(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState<string | null>(null);
  const [reviewerNote, setReviewerNote] = useState("");
  const [disposition, setDisposition] = useState("");
  const [resetOpen, setResetOpen] = useState(false);
  const [sampleLoading, setSampleLoading] = useState(false);
  const [sampleMessage, setSampleMessage] = useState("");
  const summaryRef = useRef<HTMLHeadingElement>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const activeRequestRef = useRef(0);
  const intervalRef = useRef<number | null>(null);
  const deadlineRef = useRef<number | null>(null);

  const active = phase === "validating" || phase === "submitting" || phase === "processing";
  const hasWork = draftHasContent(draft) || panels.length > 0 || Boolean(result) || Boolean(reviewerNote) || Boolean(disposition);

  function clearTimers() {
    if (intervalRef.current !== null) window.clearInterval(intervalRef.current);
    if (deadlineRef.current !== null) window.clearTimeout(deadlineRef.current);
    intervalRef.current = null;
    deadlineRef.current = null;
  }

  useEffect(() => () => {
    activeRequestRef.current += 1;
    controllerRef.current?.abort();
    clearTimers();
  }, []);

  useLayoutEffect(() => {
    if (phase !== "complete" || !result) return;
    clearTimers();
    summaryRef.current?.focus();
  }, [phase, result]);

  function changeField<K extends DraftField>(field: K, value: ReferenceDraft[K]) {
    setDraft((current) => ({ ...current, [field]: value }));
    setErrors((current) => {
      const next = { ...current };
      delete next[field];
      return next;
    });
    setSampleMessage("");
  }

  function addPanels(incoming: File[]) {
    if (!incoming.length) return;
    const all = [...panels, ...incoming];
    let message = "";
    if (all.length > MAX_PANELS) message = "Add no more than 6 label panels.";
    else if (incoming.some((file) => !ACCEPTED_IMAGE_TYPES.includes(file.type as (typeof ACCEPTED_IMAGE_TYPES)[number]))) message = "Use JPEG, PNG, or WebP images only.";
    else if (incoming.some((file) => file.size > MAX_FILE_BYTES)) message = "Each image must be 4 MiB or smaller.";
    else if (all.reduce((sum, file) => sum + file.size, 0) > MAX_AGGREGATE_BYTES) message = "All images together must be 8 MiB or smaller.";

    if (message) {
      setErrors((current) => ({ ...current, panels: message }));
      focusFirstError({ panels: message });
      return;
    }
    setPanels(all);
    setErrors((current) => {
      const next = { ...current };
      delete next.panels;
      return next;
    });
    setSampleMessage("");
  }

  function movePanel(index: number, direction: -1 | 1) {
    setPanels((current) => {
      const next = [...current];
      const target = index + direction;
      const item = next[index];
      if (!item || target < 0 || target >= next.length) return current;
      next.splice(index, 1);
      next.splice(target, 0, item);
      return next;
    });
  }

  function removePanel(index: number) {
    setPanels((current) => current.filter((_, itemIndex) => itemIndex !== index));
  }

  async function loadSample() {
    setSampleLoading(true);
    setSampleMessage("Loading the built-in sample.");
    try {
      const loaded = await samples.load();
      setDraft(referenceToDraft(loaded.reference));
      setPanels(loaded.panels);
      setErrors({});
      setPublicError(null);
      setResult(null);
      setPhase("intake");
      setSampleMessage("Sample loaded. Review it or choose Verify label.");
    } catch {
      setSampleMessage("The built-in sample could not be loaded. You can still enter a record and add images manually.");
    } finally {
      setSampleLoading(false);
    }
  }

  function finishWithError(error: PublicError) {
    clearTimers();
    controllerRef.current = null;
    setResult(null);
    setSelectedEvidenceId(null);
    setPublicError(error);
    setPhase("error");
  }

  async function verify() {
    if (active) return;
    const activatedAt = performance.now();
    setPhase("validating");
    setPublicError(null);
    setResult(null);
    setSelectedEvidenceId(null);
    const nextErrors = validateDraft(draft, panels);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) {
      setPhase("intake");
      focusFirstError(nextErrors);
      return;
    }

    const requestId = activeRequestRef.current + 1;
    activeRequestRef.current = requestId;
    const controller = new AbortController();
    controllerRef.current = controller;
    const started = activatedAt;
    setElapsed(0);
    setPhase("submitting");
    intervalRef.current = window.setInterval(() => {
      setElapsed((performance.now() - started) / 1000);
      setPhase((current) => current === "submitting" ? "processing" : current);
    }, 100);
    const remainingBrowserBudget = Math.max(0, limits.browserDeadlineSeconds * 1000 - (performance.now() - started));
    deadlineRef.current = window.setTimeout(() => {
      if (activeRequestRef.current !== requestId) return;
      activeRequestRef.current += 1;
      controller.abort();
      finishWithError(browserError(
        "client_deadline_exceeded",
        "Verification did not finish within 35 seconds.",
        "Retry with smaller files or a stable connection",
      ));
    }, remainingBrowserBudget);

    try {
      const nextResult = await client.verify({ reference: toReference(draft), panels, signal: controller.signal });
      if (activeRequestRef.current !== requestId || controller.signal.aborted) return;
      setElapsed((performance.now() - started) / 1000);
      setPublicError(null);
      setResult(nextResult);
      setSelectedEvidenceId(nextResult.evidence[0]?.evidenceId ?? null);
      setPhase("complete");
    } catch (error) {
      if (activeRequestRef.current !== requestId || controller.signal.aborted) return;
      if (error instanceof VerificationClientError) finishWithError(error.detail);
      else finishWithError(browserError("network_unavailable", "The verifier could not be reached.", "Check your connection and retry"));
    }
  }

  function cancelVerification() {
    if (!active) return;
    activeRequestRef.current += 1;
    controllerRef.current?.abort();
    controllerRef.current = null;
    clearTimers();
    setResult(null);
    setPublicError(null);
    setSelectedEvidenceId(null);
    setPhase("cancelled");
  }

  function resetSession() {
    activeRequestRef.current += 1;
    controllerRef.current?.abort();
    clearTimers();
    setDraft(EMPTY_DRAFT);
    setPanels([]);
    setErrors({});
    setPhase("intake");
    setElapsed(0);
    setResult(null);
    setPublicError(null);
    setSelectedEvidenceId(null);
    setReviewerNote("");
    setDisposition("");
    setSampleMessage("");
    setResetOpen(false);
    window.setTimeout(() => document.getElementById("start-heading")?.focus(), 0);
  }

  function requestReset() {
    if (hasWork) setResetOpen(true);
    else resetSession();
  }

  function focusErrorLocator() {
    const id = fieldIdFromLocator(publicError?.fieldOrPanel);
    if (id) document.getElementById(id)?.focus();
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="brand-mark" aria-hidden="true">LV</div>
        <div><strong>LabelVerify</strong><span>Alcohol label evidence assistant</span></div>
        <nav aria-label="Verification mode" className="workspace-switcher">
          <button aria-current={workspace === "single" ? "page" : undefined} disabled={active} onClick={() => setWorkspace("single")} type="button">One label</button>
          <button aria-current={workspace === "batch" ? "page" : undefined} disabled={active} onClick={() => setWorkspace("batch")} type="button">Batch</button>
        </nav>
        <span className="prototype-badge">Unofficial prototype</span>
      </header>

      <aside className="prototype-notice" aria-label="Prototype data notice">
        <strong>Use synthetic or sanitized data only.</strong>
        <span>This standalone prototype is not connected to COLA, does not issue legal decisions, and does not save your session.</span>
      </aside>

      <main>
        {workspace === "batch" ? <BatchWorkspace sampleAdapter={samples} verificationClient={client} /> : (
          <>
            <div className="live-status visually-hidden" aria-live="polite">
              {phase === "cancelled" ? "Verification cancelled. Your form and selected files are unchanged." : ""}
            </div>
            {phase === "complete" && result ? (
              <ResultWorkspace
                disposition={disposition}
                note={reviewerNote}
                onDispositionChange={setDisposition}
                onNoteChange={setReviewerNote}
                onSelectEvidence={setSelectedEvidenceId}
                onStartOver={requestReset}
                result={result}
                selectedEvidenceId={selectedEvidenceId}
                sourcePanels={panels}
                summaryRef={summaryRef}
              />
            ) : (
              <>
                {active ? <ProcessingBanner elapsed={elapsed} onCancel={cancelVerification} phase={phase} /> : null}
                {phase === "cancelled" ? (
                  <section className="status-banner cancelled-banner" aria-live="polite">
                    <div><p className="eyebrow">Cancelled</p><h2>Verification cancelled</h2><p>Your application values and selected images are unchanged. You can verify again or start over.</p></div>
                  </section>
                ) : null}
                {publicError ? <ErrorBanner error={publicError} onFocusLocator={focusErrorLocator} onRetry={verify} /> : null}
                {sampleMessage && !sampleLoading ? <p className="sample-status" aria-live="polite">{sampleMessage}</p> : null}
                <IntakeForm
                  disabled={active}
                  draft={draft}
                  errors={errors}
                  onAddPanels={addPanels}
                  onFieldChange={changeField}
                  onMovePanel={movePanel}
                  onRemovePanel={removePanel}
                  onStartOver={requestReset}
                  onTrySample={loadSample}
                  onVerify={verify}
                  panels={panels}
                  sampleLoading={sampleLoading}
                />
              </>
            )}
          </>
        )}
      </main>

      <footer>
        <span>Evidence support for human review</span>
        <span>Current browser session only</span>
      </footer>

      {resetOpen ? <ResetDialog onCancel={() => setResetOpen(false)} onConfirm={resetSession} /> : null}
    </div>
  );
}
