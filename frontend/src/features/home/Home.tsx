import { useRef, useState, type ChangeEvent, type DragEvent, type ReactElement } from "react";

import { FilePreview } from "../../components/FilePreview";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import { DispositionTag, SummaryTag } from "../../components/StatusTag";
import type { HistorySummary } from "../../contracts/types";
import { filterBatchSelection, imageSelectionIssue, type SkippedBatchFile } from "../batch/grouping";
import { EMPTY_APPLICATION, type ApplicationInput } from "../intake/application";
import { ApplicationDetails } from "../intake/ApplicationDetails";
import { beverageTypeLabel } from "../verification/check-view";
import { whenLabel } from "./format";

const DIRECTORY_ATTRS = { webkitdirectory: "", directory: "" } as Record<string, string>;

export function Home({ onSingle, onBatch, onSample, onOpenHistory, onOpenRecord, recent, historyTotal, historyCap, sampleLoading }: {
  onSingle: (files: File[], application: ApplicationInput) => void;
  onBatch: (files: File[]) => void;
  onSample: () => void;
  onOpenHistory: () => void;
  onOpenRecord: (id: string) => void;
  recent: HistorySummary[];
  historyTotal: number;
  historyCap: number;
  sampleLoading: boolean;
}): ReactElement {
  const singleInput = useRef<HTMLInputElement>(null);
  const batchInput = useRef<HTMLInputElement>(null);
  const [singleFiles, setSingleFiles] = useState<File[]>([]);
  const [batchFiles, setBatchFiles] = useState<File[]>([]);
  const [singleIssue, setSingleIssue] = useState("");
  const [batchIssue, setBatchIssue] = useState("");
  const [batchSkipped, setBatchSkipped] = useState<SkippedBatchFile[]>([]);
  const [dragging, setDragging] = useState<"single" | "batch" | null>(null);
  const [application, setApplication] = useState<ApplicationInput>(EMPTY_APPLICATION);
  const [applicationOpen, setApplicationOpen] = useState(false);

  function addSingle(files: File[]) {
    const next = [...singleFiles, ...files];
    const issue = imageSelectionIssue(next, 3);
    setSingleIssue(issue ?? "");
    if (!issue) setSingleFiles(next);
  }

  function moveSingle(from: number, to: number) {
    if (to < 0 || to >= singleFiles.length) return;
    setSingleFiles((files) => {
      const next = [...files];
      const [moved] = next.splice(from, 1);
      if (!moved) return files;
      next.splice(to, 0, moved);
      return next;
    });
  }

  function chooseBatch(files: File[]) {
    const selection = filterBatchSelection(files, 900);
    setBatchFiles(selection.accepted);
    setBatchSkipped(selection.skipped);
    setBatchIssue(selection.accepted.length ? "" : "This folder does not contain a supported image under 4 MB.");
  }

  function onDrop(kind: "single" | "batch") {
    return (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setDragging(null);
      const files = Array.from(event.dataTransfer.files);
      if (kind === "single") addSingle(files);
      else chooseBatch(files);
    };
  }

  function onDragOver(kind: "single" | "batch") {
    return (event: DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      if (dragging !== kind) setDragging(kind);
    };
  }

  function roleFor(index: number, count: number): string {
    if (count === 1) return `${singleFiles[index]?.type.replace("image/", "").toUpperCase() ?? "image"}`;
    return index === 0 ? "Front" : index === 1 ? "Back" : "Added";
  }

  return (
    <main className="home" data-screen-label="Home">
      <header className="home-header">
        <div><h6 className="kicker">Beer · Wine · Distilled spirits</h6><h1>What are we checking today?</h1></div>
        <p className="text-muted">Drop the label photos. LabelVerify reads them, works out the beverage type, and runs the TTB checks for that type. You make the call.</p>
      </header>

      <div className="doors">
        <section aria-labelledby="door-one" className="card blueprint door">
          <Corners />
          <div className="door-head"><h2 id="door-one">Check one label</h2><span className="text-muted">1-3 images of one product</span></div>
          <div aria-label="Drop label images or choose files" className={`dropzone${dragging === "single" ? " dragging" : ""}`} onClick={() => singleInput.current?.click()} onDragLeave={() => setDragging(null)} onDragOver={onDragOver("single")} onDrop={onDrop("single")} role="group">
            <span className="drop-icon">{icons.image(28)}</span>
            <strong>Drop label images here</strong>
            <span className="helper text-muted">Front, back, neck: up to 3. JPEG, PNG or WebP, 4 MB each.</span>
            <div className="drop-actions" onClick={(event) => event.stopPropagation()}>
              <button className="btn btn-secondary btn-hit" onClick={() => singleInput.current?.click()} type="button">Choose images</button>
              <button className="btn btn-ghost btn-hit" disabled={sampleLoading} onClick={onSample} type="button">{sampleLoading ? "Loading sample…" : "Use the built-in sample"}</button>
            </div>
            <input accept="image/jpeg,image/png,image/webp" aria-label="Choose label images" className="sr-only" multiple onChange={(event: ChangeEvent<HTMLInputElement>) => { addSingle(Array.from(event.target.files ?? [])); event.target.value = ""; }} ref={singleInput} type="file" />
          </div>
          {singleIssue ? <p className="form-error" role="alert">{singleIssue}</p> : null}
          {singleFiles.length ? (
            <ul className="file-chips">
              {singleFiles.map((file, index) => (
                <li key={`${file.name}-${file.lastModified}-${index}`}>
                  <figure className="file-chip">
                    <FilePreview alt={`${file.name} preview`} file={file} />
                    <figcaption>{file.name}<br /><span className="text-muted">{roleFor(index, singleFiles.length)}</span></figcaption>
                    <div className="file-chip-actions">
                      <button aria-label={`Move ${file.name} earlier`} className="btn btn-ghost btn-icon" disabled={index === 0} onClick={() => moveSingle(index, index - 1)} type="button">↑</button>
                      <button aria-label={`Move ${file.name} later`} className="btn btn-ghost btn-icon" disabled={index === singleFiles.length - 1} onClick={() => moveSingle(index, index + 1)} type="button">↓</button>
                      <button aria-label={`Remove ${file.name}`} className="btn btn-ghost btn-icon" onClick={() => setSingleFiles((files) => files.filter((_, item) => item !== index))} type="button">{icons.x()}</button>
                    </div>
                  </figure>
                </li>
              ))}
            </ul>
          ) : null}
          <ApplicationDetails onChange={setApplication} onToggle={setApplicationOpen} open={applicationOpen} value={application} />
          <div className="door-foot">
            <span className="note text-muted">Reads and checks in one step · usually about 5 seconds</span>
            <button className="btn btn-primary blueprint" disabled={!singleFiles.length} onClick={() => onSingle(singleFiles, application)} type="button"><Corners />Read &amp; check label {icons.arrow()}</button>
          </div>
        </section>

        <section aria-labelledby="door-batch" className="card blueprint door">
          <Corners />
          <div className="door-head"><h2 id="door-batch">Check a batch</h2><span className="text-muted">Up to 300 products · 900 images</span></div>
          <div aria-label="Drop a folder of label images" className={`dropzone${dragging === "batch" ? " dragging" : ""}`} onClick={() => batchInput.current?.click()} onDragLeave={() => setDragging(null)} onDragOver={onDragOver("batch")} onDrop={onDrop("batch")} role="group">
            <span className="drop-icon">{icons.folder(28)}</span>
            <strong>Drop a folder of labels</strong>
            <span className="helper narrow text-muted">No spreadsheet needed. We group the images into products and ask you to confirm before anything runs.</span>
            <div className="drop-actions" onClick={(event) => event.stopPropagation()}>
              <button className="btn btn-secondary btn-hit" onClick={() => batchInput.current?.click()} type="button">Choose folder</button>
            </div>
            <input aria-label="Choose batch folder" className="sr-only" multiple onChange={(event: ChangeEvent<HTMLInputElement>) => { chooseBatch(Array.from(event.target.files ?? [])); event.target.value = ""; }} ref={batchInput} type="file" {...DIRECTORY_ATTRS} />
          </div>
          {batchIssue ? <p className="form-error" role="alert">{batchIssue}</p> : null}
          {batchFiles.length ? <div aria-live="polite" className="batch-selection-status" role="status"><div><strong>0 of {batchFiles.length} processed</strong><span className="text-muted">{batchFiles.length} supported image{batchFiles.length === 1 ? "" : "s"} ready{batchSkipped.length ? ` · ${batchSkipped.length} file${batchSkipped.length === 1 ? "" : "s"} skipped` : ""}</span></div><progress aria-label="Batch processing progress" max={batchFiles.length} value={0} />{batchSkipped.length ? <details><summary>Skipped files</summary><ul>{batchSkipped.slice(0, 20).map((item, index) => <li key={`${item.name}-${index}`}>{item.name}: {item.reason}</li>)}</ul>{batchSkipped.length > 20 ? <p>{batchSkipped.length - 20} more skipped files</p> : null}</details> : null}</div> : null}
          <ol className="batch-steps">
            <li><strong>1 Analyze</strong><br /><span className="text-muted">Every image is read. Live count, time per image.</span></li>
            <li><strong>2 Confirm groups</strong><br /><span className="text-muted">Fix any product we grouped wrong.</span></li>
            <li><strong>3 Work exceptions</strong><br /><span className="text-muted">Open only what needs a human.</span></li>
          </ol>
          <div className="door-foot end">
            {batchFiles.length ? <span className="note text-muted">{batchFiles.length} image{batchFiles.length === 1 ? "" : "s"} ready</span> : null}
            <button className="btn btn-secondary" disabled={!batchFiles.length} onClick={() => onBatch(batchFiles)} type="button">Analyze images {icons.arrow()}</button>
          </div>
        </section>
      </div>

      <section aria-labelledby="recent-h" className="recent">
        <div className="recent-head"><h4 id="recent-h">Recent</h4><a href="#/history" onClick={(event) => { event.preventDefault(); onOpenHistory(); }}>All history · {historyTotal} of {historyCap}</a></div>
        <div className="table-wrap">
          <table className="table reflow">
            <thead><tr><th>When</th><th>Product</th><th>Type</th><th>Machine result</th><th>Your disposition</th><th /></tr></thead>
            <tbody>
              {recent.map((item) => (
                <tr key={item.id}>
                  <td className="text-muted nowrap" data-label="When">{whenLabel(item.createdAt)}</td>
                  <td data-label="Product">{item.displayName}</td>
                  <td data-label="Type">{beverageTypeLabel(item.beverageType, true)}</td>
                  <td data-label="Machine result"><SummaryTag summary={item.summary} /></td>
                  <td data-label="Your disposition"><DispositionTag value={item.disposition} /></td>
                  <td className="right"><button className="btn btn-ghost" onClick={() => onOpenRecord(item.id)} type="button">Open</button></td>
                </tr>
              ))}
              {!recent.length ? <tr><td className="text-muted" colSpan={6}>No completed checks yet. When you finish a check it appears here with its images, findings and your disposition.</td></tr> : null}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
