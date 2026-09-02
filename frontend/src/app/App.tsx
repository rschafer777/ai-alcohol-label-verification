import { useEffect, useMemo, useRef, useState, type ChangeEvent, type ReactNode } from "react";

import { createVerificationClient, VerificationClientError } from "../api/verification-client";
import type {
  AnalysisResult,
  PublicError,
  ReferenceRecord,
  SampleAdapter,
  VerificationClient,
  VerificationResult,
} from "../contracts/types";
import { BatchWorkspace } from "../features/batch/BatchWorkspace";
import { imageSelectionIssue } from "../features/batch/grouping";
import { HistoryWorkspace } from "../features/history/HistoryWorkspace";
import { createSampleAdapter } from "../features/intake/sample-adapter";
import { ResultWorkspace } from "../features/verification/ResultWorkspace";

type Page = "home" | "processing" | "review" | "history" | "batch";

interface AppProps {
  verificationClient?: VerificationClient;
  sampleAdapter?: SampleAdapter;
}

interface RecentRecord {
  id: string;
  createdAt: string;
  displayName: string;
  beverageType: ReferenceRecord["beverageType"] | "unresolved";
  summary: VerificationResult["summary"];
  disposition: string | null;
}

function typeLabel(value: ReferenceRecord["beverageType"] | "unresolved"): string {
  if (value === "malt_beverage") return "Beer / malt";
  if (value === "distilled_spirits") return "Distilled spirits";
  if (value === "wine") return "Wine";
  return "Type uncertain";
}

function StateCard({ error, onRetry, onHome }: { error: PublicError; onRetry: () => void; onHome: () => void }) {
  return (
    <section className="state-card" role="alert">
      <p className="kicker">{error.code}</p>
      <h1>We could not finish this label</h1>
      <p>{error.message}</p>
      <p><strong>Next:</strong> {error.nextAction}</p>
      <p className="micro">Request {error.requestId}</p>
      <div className="button-row">
        {error.retryable ? <button className="btn primary" onClick={onRetry} type="button">Try again</button> : null}
        <button className="btn secondary" onClick={onHome} type="button">Back home</button>
      </div>
    </section>
  );
}

function FilePreview({ file, alt = "" }: { file: File; alt?: string }) {
  const url = useMemo(() => URL.createObjectURL(file), [file]);
  useEffect(() => () => URL.revokeObjectURL(url), [url]);
  return <img alt={alt} src={url} />;
}

function AppShell({ page, historyCount, onNavigate, children }: {
  page: Page;
  historyCount: number;
  onNavigate: (page: Page) => void;
  children: ReactNode;
}) {
  const [trayOpen, setTrayOpen] = useState(true);
  const title = page === "home" ? "Home" : page === "batch" ? "Batch review" : page === "history" ? "History" : "Label review";
  return (
    <div className={`shell ${trayOpen ? "tray-open" : "tray-closed"}`}>
      <header className="topbar">
        <button aria-controls="lv-tray" aria-expanded={trayOpen} className="icon-btn" onClick={() => setTrayOpen((value) => !value)} type="button">Menu</button>
        <div className="agency-mark" aria-hidden="true">LV</div>
        <div className="agency-name"><strong>TTB</strong><span>Alcohol and Tobacco Tax and Trade Bureau</span></div>
        <span className="top-rule" />
        <div className="product-name"><strong>LabelVerify</strong><span>Alcohol label evidence assistant</span></div>
        <span className="current-title">{title}</span>
        <span className="prototype-tag">Unofficial prototype</span>
      </header>
      <div className="notice-band">
        <strong>Synthetic or sanitized data only</strong>
        <span>Not connected to COLA</span>
        <span>No legal decisions are issued</span>
        <span>Images are kept with each completed result for evidence review</span>
      </div>
      <aside className="left-tray" id="lv-tray">
        <nav aria-label="Primary navigation">
          <button aria-current={page === "home" || page === "processing" || page === "review" ? "page" : undefined} onClick={() => onNavigate("home")} type="button"><strong>Check one label</strong><span>1 to 3 images of one product</span></button>
          <button aria-current={page === "batch" ? "page" : undefined} onClick={() => onNavigate("batch")} type="button"><strong>Check a batch</strong><span>Up to 300 products</span></button>
          <button aria-current={page === "history" ? "page" : undefined} onClick={() => onNavigate("history")} type="button"><strong>History</strong><span>{historyCount} of 500 kept</span></button>
        </nav>
        <div className="tray-foot"><span>Reviewer workspace</span><strong>Evidence-led decisions</strong></div>
      </aside>
      <main className="content">{children}</main>
      <footer>Evidence support for human review <span>History capped at 500 records</span></footer>
    </div>
  );
}

function Home({ onSingle, onBatch, onSample, recent, sampleLoading }: {
  onSingle: (files: File[]) => void;
  onBatch: (files: File[]) => void;
  onSample: () => void;
  recent: RecentRecord[];
  sampleLoading: boolean;
}) {
  const singleInput = useRef<HTMLInputElement>(null);
  const batchInput = useRef<HTMLInputElement>(null);
  const [singleFiles, setSingleFiles] = useState<File[]>([]);
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [singleIssue, setSingleIssue] = useState("");
  const [batchIssue, setBatchIssue] = useState("");

  function setSingleSelection(files: File[]) {
    const issue = imageSelectionIssue(files, 3);
    setSingleIssue(issue ?? "");
    setSingleFiles(issue ? [] : files);
  }

  function setBatchSelection(files: File[]) {
    const issue = imageSelectionIssue(files, 900);
    setBatchIssue(issue ?? "");
    setBatchFiles(issue ? [] : files);
  }

  function chooseSingle(event: ChangeEvent<HTMLInputElement>) {
    setSingleSelection(Array.from(event.target.files ?? []));
    event.target.value = "";
  }

  function chooseBatch(event: ChangeEvent<HTMLInputElement>) {
    setBatchSelection(Array.from(event.target.files ?? []));
    event.target.value = "";
  }

  function moveSingle(index: number, offset: -1 | 1) {
    setSingleFiles((current) => {
      const destination = index + offset;
      if (destination < 0 || destination >= current.length) return current;
      const next = [...current];
      const selected = next[index];
      const displaced = next[destination];
      if (!selected || !displaced) return current;
      next[index] = displaced;
      next[destination] = selected;
      return next;
    });
  }

  return (
    <div className="home-page">
      <section className="home-heading">
        <div><p className="kicker">Beer | Wine | Distilled spirits</p><h1>What are we checking today?</h1></div>
        <p>Drop label photos. LabelVerify reads them, infers the beverage type, and runs the selected TTB checks. You make the decision.</p>
      </section>
      <div className="door-grid">
        <section className="blueprint door-card" aria-labelledby="single-heading">
          <div className="section-row"><h2 id="single-heading">Check one label</h2><span>1 to 3 images of one product</span></div>
          <div className="drop-panel" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); setSingleSelection(Array.from(event.dataTransfer.files)); }}>
            <span className="large-icon" aria-hidden="true">+</span>
            <strong>Drop label images here</strong>
            <span>Front, back, or neck. JPEG, PNG, or WebP, 4 MB each.</span>
            <div className="button-row">
              <button className="btn secondary" onClick={() => singleInput.current?.click()} type="button">Choose images</button>
              <button className="btn ghost" disabled={sampleLoading} onClick={onSample} type="button">{sampleLoading ? "Loading sample" : "Use built-in sample"}</button>
            </div>
            <input aria-label="Choose label images" ref={singleInput} className="sr-only" accept="image/jpeg,image/png,image/webp" multiple onChange={chooseSingle} type="file" />
          </div>
          {singleIssue ? <p className="form-error" role="alert">{singleIssue}</p> : null}
          <ul className="file-chips">{singleFiles.map((file, index) => <li key={`${file.name}-${file.lastModified}`}><span>{index + 1}</span><FilePreview alt={`${file.name} preview`} file={file} /><strong>{file.name}</strong><div className="file-actions"><button aria-label={`Move ${file.name} up`} disabled={index === 0} onClick={() => moveSingle(index, -1)} type="button">Up</button><button aria-label={`Move ${file.name} down`} disabled={index === singleFiles.length - 1} onClick={() => moveSingle(index, 1)} type="button">Down</button><button aria-label={`Remove ${file.name}`} onClick={() => setSingleFiles((files) => files.filter((_, item) => item !== index))} type="button">Remove</button></div></li>)}</ul>
          <div className="door-footer"><span>Reads and checks in one step. Usually about 5 seconds.</span><button className="btn primary" disabled={!singleFiles.length} onClick={() => onSingle(singleFiles)} type="button">Read and check label</button></div>
        </section>
        <section className="blueprint door-card" aria-labelledby="batch-heading">
          <div className="section-row"><h2 id="batch-heading">Check a batch</h2><span>Up to 300 products and 900 images</span></div>
          <div className="drop-panel" onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); setBatchSelection(Array.from(event.dataTransfer.files)); }}>
            <span className="large-icon" aria-hidden="true">+</span>
            <strong>Drop a folder of labels</strong>
            <span>No spreadsheet needed. We suggest product groups, then you confirm them.</span>
            <button className="btn secondary" onClick={() => batchInput.current?.click()} type="button">Choose folder</button>
            <input aria-label="Choose batch folder" ref={batchInput} className="sr-only" {...({ webkitdirectory: "", directory: "" } as Record<string, string>)} multiple onChange={chooseBatch} type="file" />
          </div>
          {batchIssue ? <p className="form-error" role="alert">{batchIssue}</p> : null}
          <ol className="batch-steps"><li><strong>1 Analyze</strong><span>Read image cues</span></li><li><strong>2 Confirm groups</strong><span>Up to 3 images each</span></li><li><strong>3 Work exceptions</strong><span>Review only what needs you</span></li></ol>
          <div className="door-footer"><span>{batchFiles.length ? `${batchFiles.length} images selected` : "Images stay local until processing starts"}</span><button className="btn primary" disabled={!batchFiles.length} onClick={() => onBatch(batchFiles)} type="button">Analyze images</button></div>
        </section>
      </div>
      <section className="recent-section">
        <div className="section-row"><h2>Recent</h2><span>{recent.length ? "Latest completed checks" : "No completed checks yet"}</span></div>
        <div className="table-wrap"><table><thead><tr><th>When</th><th>Product</th><th>Type</th><th>Machine result</th><th>Your disposition</th></tr></thead><tbody>{recent.map((item) => <tr key={item.id}><td>{new Date(item.createdAt).toLocaleString()}</td><th scope="row">{item.displayName}</th><td>{typeLabel(item.beverageType)}</td><td>{item.summary}</td><td>{item.disposition ? item.disposition.replaceAll("_", " ") : "Undecided"}</td></tr>)}{!recent.length ? <tr><td colSpan={5}>Completed results will appear here.</td></tr> : null}</tbody></table></div>
      </section>
    </div>
  );
}

function Processing({ files, elapsed, onCancel }: { files: File[]; elapsed: number; onCancel: () => void }) {
  return (
    <section className="processing-page" aria-live="polite">
      <div className="section-row"><p className="kicker">Check one label</p><button className="btn ghost" onClick={onCancel} type="button">Cancel</button></div>
      <div className="processing-card blueprint">
        <div className="processing-thumbs">{files.map((file) => <div className="scan-thumb" key={file.name}><FilePreview file={file} /><span /></div>)}</div>
        <div><div className="processing-title"><h1 tabIndex={-1}>Reading the label</h1><strong>{elapsed.toFixed(1)} s</strong></div><p>OCR is locating the text, inferring beverage type, and checking the applicable rule profile.</p><ol className="process-steps"><li className="done"><strong>Uploaded</strong><span>{files.length} image{files.length === 1 ? "" : "s"}</span></li><li className="active"><strong>Reading label</strong><span>Local OCR and evidence mapping</span></li><li><strong>Checking rules</strong><span>Beer, wine, or spirits profile</span></li></ol><p className="micro">Most labels finish in about 5 seconds. Harder images may take longer and are never rejected solely because of resolution.</p></div>
      </div>
    </section>
  );
}

export function App({ verificationClient, sampleAdapter }: AppProps) {
  const client = useMemo(() => verificationClient ?? createVerificationClient(), [verificationClient]);
  const samples = useMemo(() => sampleAdapter ?? createSampleAdapter(), [sampleAdapter]);
  const [page, setPage] = useState<Page>("home");
  const [files, setFiles] = useState<File[]>([]);
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [result, setResult] = useState<VerificationResult | null>(null);
  const [error, setError] = useState<PublicError | null>(null);
  const [elapsed, setElapsed] = useState(0);
  const [historyCount, setHistoryCount] = useState(0);
  const [recent, setRecent] = useState<RecentRecord[]>([]);
  const [sampleLoading, setSampleLoading] = useState(false);
  const controller = useRef<AbortController | null>(null);
  const timer = useRef<number | null>(null);

  async function refreshRecent() {
    try {
      const response = await fetch("/api/v1/history?pageSize=3");
      if (!response.ok) return;
      const payload = await response.json() as { total: number; items: RecentRecord[] };
      setHistoryCount(payload.total);
      setRecent(payload.items);
    } catch {
      setHistoryCount(0);
    }
  }

  useEffect(() => {
    const loadTimer = window.setTimeout(() => void refreshRecent(), 0);
    return () => {
      window.clearTimeout(loadTimer);
      controller.current?.abort();
      if (timer.current !== null) window.clearInterval(timer.current);
    };
  }, []);

  function reset() {
    controller.current?.abort();
    if (timer.current !== null) window.clearInterval(timer.current);
    setFiles([]);
    setAnalysis(null);
    setResult(null);
    setError(null);
    setElapsed(0);
    setPage("home");
    void refreshRecent();
  }

  async function runSingle(selected: File[]) {
    const nextController = new AbortController();
    controller.current = nextController;
    setFiles(selected);
    setError(null);
    setResult(null);
    setPage("processing");
    const started = performance.now();
    timer.current = window.setInterval(() => setElapsed((performance.now() - started) / 1000), 100);
    try {
      const nextAnalysis = await client.analyze({ panels: selected, signal: nextController.signal });
      if (nextController.signal.aborted) return;
      setAnalysis(nextAnalysis);
      if (!nextAnalysis.verification) {
        setError({ requestId: nextAnalysis.requestId, code: "beverage_type_uncertain", message: "The beverage type could not be inferred reliably from the submitted images.", retryable: true, nextAction: "Add a clearer class or type panel and retry", fieldOrPanel: "panels" });
        return;
      }
      setResult(nextAnalysis.verification);
      setPage("review");
      void refreshRecent();
    } catch (caught) {
      if (nextController.signal.aborted) return;
      setError(caught instanceof VerificationClientError ? caught.detail : { requestId: "unavailable", code: "network_unavailable", message: "The verifier could not be reached.", retryable: true, nextAction: "Check the connection and retry", fieldOrPanel: null });
    } finally {
      if (timer.current !== null) window.clearInterval(timer.current);
      timer.current = null;
      setElapsed((performance.now() - started) / 1000);
      if (!nextController.signal.aborted) setPage((current) => current === "processing" ? "review" : current);
    }
  }

  async function loadSample() {
    setSampleLoading(true);
    try {
      const loaded = await samples.load();
      await runSingle(loaded.panels.slice(0, 3));
    } catch {
      setError({ requestId: "sample", code: "sample_unavailable", message: "The built-in sample could not be loaded.", retryable: true, nextAction: "Choose your own images", fieldOrPanel: null });
      setPage("review");
    } finally {
      setSampleLoading(false);
    }
  }

  function navigate(next: Page) {
    if (next === "home") reset();
    else setPage(next);
  }

  let body: ReactNode;
  if (page === "processing") body = <Processing elapsed={elapsed} files={files} onCancel={reset} />;
  else if (page === "review") body = error ? <StateCard error={error} onHome={reset} onRetry={() => void runSingle(files)} /> : result && analysis ? <ResultWorkspace analysis={analysis} onAddFiles={(added) => void runSingle([...files, ...added].slice(0, 3))} onStartOver={reset} result={result} sourcePanels={files} /> : <StateCard error={{ requestId: "unavailable", code: "result_unavailable", message: "No result is available.", retryable: true, nextAction: "Retry the label", fieldOrPanel: null }} onHome={reset} onRetry={() => void runSingle(files)} />;
  else if (page === "batch") body = <BatchWorkspace initialFiles={batchFiles} onFilesConsumed={() => setBatchFiles([])} verificationClient={client} />;
  else if (page === "history") body = <HistoryWorkspace onCountChange={setHistoryCount} />;
  else body = <Home onBatch={(selected) => { setBatchFiles(selected); setPage("batch"); }} onSample={() => void loadSample()} onSingle={(selected) => void runSingle(selected)} recent={recent} sampleLoading={sampleLoading} />;

  return <AppShell historyCount={historyCount} onNavigate={navigate} page={page}>{body}</AppShell>;
}
