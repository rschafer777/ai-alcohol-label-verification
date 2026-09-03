import { useEffect, useRef, useState, type ReactElement, type ReactNode } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import type { Disposition } from "../../components/status";
import { SummaryTag } from "../../components/StatusTag";
import type { BeverageType, CheckResult, VerificationResult } from "../../contracts/types";
import { beverageTypeLabel, evidenceFor, needsTypeConfirmation, panelIndexOf, profileLabel, tally, tallyText, typeTagText } from "./check-view";
import { CheckCards, CheckRail, CheckTable } from "./CheckTable";
import { DecisionBar } from "./DecisionBar";
import { EvidenceViewer } from "./EvidenceViewer";
import type { ReviewImage, SlotUpload } from "./review-images";
import { WarningInspect } from "./WarningInspect";

export type Layout = "table" | "cards" | "image";

export interface ReviewWorkspaceProps {
  result: VerificationResult;
  brandName: string;
  beverageType: BeverageType | null;
  imported: boolean;
  images: ReviewImage[];
  addedFrom?: number;
  inBatch?: boolean;
  rail?: ReactNode;
  disposition: Disposition;
  note: string;
  saveState?: string;
  onDisposition: (value: Disposition) => void;
  onNote: (value: string) => void;
  onSave: () => void;
  onNextException?: () => void;
  onBack: () => void;
  onAddImage?: ((file: File, slot: number) => void) | null;
  upload?: SlotUpload | null;
  onCorrect?: ((check: CheckResult, value: string) => void) | null;
  correctedIds?: ReadonlySet<string>;
  onConfirmType?: ((type: BeverageType) => void) | null;
  /** Application fields the reviewer typed; the result compares the label with them. */
  comparedWith?: string[] | null;
}

const EMPTY: ReadonlySet<string> = new Set();

const LAYOUTS: Array<{ value: Layout; label: string; icon: ReactElement; hint: string }> = [
  { value: "table", label: "Table", icon: icons.table(), hint: "Every check in one table, grouped by section" },
  { value: "cards", label: "Cards", icon: icons.cards(), hint: "One card per check with its reason and evidence" },
  { value: "image", label: "Image first", icon: icons.image(16), hint: "A larger image with the checks as a compact list beside it" },
];

export function ReviewWorkspace(props: ReviewWorkspaceProps): ReactElement {
  const { result, brandName, beverageType, imported, images, addedFrom, inBatch = false, rail, disposition, note, saveState = "", onDisposition, onNote, onSave, onNextException, onBack, onAddImage = null, upload = null, onCorrect = null, correctedIds = EMPTY, onConfirmType = null, comparedWith = null } = props;
  const [layout, setLayout] = useState<Layout>("table");
  const [panelIndex, setPanelIndex] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [warningExpanded, setWarningExpanded] = useState(false);
  const [inspecting, setInspecting] = useState(false);
  const [typeChoice, setTypeChoice] = useState<BeverageType | null>(beverageType);
  const [typeDismissed, setTypeDismissed] = useState(false);
  const summaryRef = useRef<HTMLSpanElement>(null);
  const checks = result.checks;
  const selected = checks.find((check) => check.checkId === selectedId) ?? null;

  // A new result (re-check, added image, next product) clears the selection during render,
  // the React-recommended alternative to a setState-in-effect; focus then moves to the summary.
  const [seenRequestId, setSeenRequestId] = useState(result.requestId);
  if (seenRequestId !== result.requestId) {
    setSeenRequestId(result.requestId);
    setSelectedId(null);
    if (panelIndex > images.length - 1) setPanelIndex(Math.max(0, images.length - 1));
  }
  useEffect(() => {
    summaryRef.current?.focus();
  }, [result.requestId]);

  function select(id: string) {
    const check = checks.find((item) => item.checkId === id);
    if (!check) return;
    if (selectedId === id) {
      setSelectedId(null);
      return;
    }
    setSelectedId(id);
    const evidence = evidenceFor(result, check);
    if (evidence) setPanelIndex(panelIndexOf(result, evidence.panelId));
  }

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      const target = event.target as HTMLElement | null;
      if (target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) return;
      if (event.metaKey || event.ctrlKey || event.altKey) return;
      const key = event.key.toLowerCase();
      if (inspecting) {
        if (key === "escape") setInspecting(false);
        return;
      }
      if (key === "a") onDisposition("approved");
      else if (key === "r") onDisposition("rejected");
      else if (key === "m") onDisposition("more_info_requested");
      else if (key === "w") setInspecting(true);
      else if (key === "e" && inBatch && onNextException) onNextException();
      else if (key === "1" || key === "2" || key === "3") {
        const index = Number(key) - 1;
        if (images[index]) { setPanelIndex(index); setSelectedId(null); }
      } else if (key === "arrowdown" || key === "arrowup") {
        event.preventDefault();
        const ids: string[] = checks.map((check) => check.checkId);
        const current = selectedId ? ids.indexOf(selectedId) : -1;
        const next = key === "arrowdown" ? Math.min(ids.length - 1, current + 1) : Math.max(0, current - 1);
        const id = ids[next];
        if (id) setSelectedId(id);
      } else if (key === "enter" && selectedId) {
        const evidence = evidenceFor(result, selected);
        if (evidence) setPanelIndex(panelIndexOf(result, evidence.panelId));
      } else if (key === "escape") {
        if (selectedId) setSelectedId(null);
        else onBack();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [checks, images, inBatch, inspecting, onBack, onDisposition, onNextException, result, selected, selectedId]);

  if (inspecting) return <WarningInspect images={images} onBack={() => setInspecting(false)} result={result} />;

  const showTypeConfirm = !!onConfirmType && !typeDismissed && needsTypeConfirmation(result);
  const count = images.length;
  const listProps = { result, checks, selectedId, correctedIds, onSelect: select, onInspectWarning: () => setInspecting(true), onCorrect };
  const summary = result.badImage ? "Bad image" as const : result.summary;

  return (
    <main className="review" data-screen-label="Review">
      <header className="review-header">
        <button className="btn btn-ghost" onClick={onBack} type="button">{icons.back()} {inBatch ? "Batch" : "Start over"}</button>
        <h2>{brandName}</h2>
        <span className="tag tag-neutral">{typeTagText(result, beverageType, imported)}</span>
        {comparedWith && comparedWith.length ? <span className="tag tag-info">Compared with application: {comparedWith.join(", ")}</span> : null}
        <span className="meta text-muted">{count} image{count === 1 ? "" : "s"} · read &amp; checked in {(result.serverDurationMs / 1000).toFixed(1)} s</span>
        <span className="machine"><span className="text-muted">Machine result</span><span ref={summaryRef} tabIndex={-1}><SummaryTag summary={summary} /></span></span>
      </header>

      {showTypeConfirm ? (
        <div className="type-confirm" role="alert">
          <span>{icons.help()}</span>
          <strong>{result.beverageInference?.type ? `We read this as ${beverageTypeLabel(result.beverageInference.type)}, but with low confidence.` : "We could not settle the beverage type from the label."}</strong>
          <span className="text-muted">Which is it? The checks change with the type.</span>
          <div aria-label="Beverage type" className="seg" role="radiogroup">
            {(["malt_beverage", "wine", "distilled_spirits"] as BeverageType[]).map((value) => <button aria-checked={typeChoice === value} className="seg-opt" key={value} onClick={() => setTypeChoice(value)} role="radio" type="button">{beverageTypeLabel(value)}</button>)}
          </div>
          <button className="btn btn-primary blueprint" disabled={!typeChoice} onClick={() => { if (typeChoice && onConfirmType) { setTypeDismissed(true); onConfirmType(typeChoice); } }} type="button"><Corners />Confirm &amp; re-check</button>
        </div>
      ) : null}

      <div className={`review-body layout-${layout}${inBatch ? " with-rail" : ""}`}>
        {inBatch ? rail : null}
        <EvidenceViewer addedFrom={addedFrom} images={images} onAddImage={onAddImage} onClearSelection={() => setSelectedId(null)} onSelectPanel={(index) => { setPanelIndex(index); setSelectedId(null); }} panelIndex={panelIndex} result={result} selected={selected} upload={upload} />
        <section aria-labelledby="checks-h" className="checks" tabIndex={0}>
          <div className="checks-head">
            <h6 id="checks-h">24 checks · {profileLabel(result.beverageInference?.type ?? beverageType)}</h6>
            <span className="tally text-muted">{tallyText(tally(checks))}</span>
            <div className="view-switch">
              <span className="view-switch-label text-muted">View as</span>
              <div aria-label="View as" className="seg seg-strong" role="radiogroup">
                {LAYOUTS.map(({ value, label, icon, hint }) => <button aria-checked={layout === value} className="seg-opt" key={value} onClick={() => setLayout(value)} role="radio" title={hint} type="button">{icon} {label}</button>)}
              </div>
            </div>
            <span className="columns text-muted">Columns: what the rule expects · what we read on the label · machine result</span>
          </div>
          {layout === "table" ? <CheckTable {...listProps} onToggleWarning={() => setWarningExpanded((value) => !value)} warningExpanded={warningExpanded} /> : layout === "cards" ? <CheckCards {...listProps} /> : <CheckRail {...listProps} />}
          <details className="limitations">
            <summary>Limitations reported with this result ({result.limitations.length})</summary>
            <ul className="text-muted">{result.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
            <p className="text-muted">Capability {result.modelIdentity} · Policy {result.profileVersion} · Request {result.requestId}</p>
          </details>
        </section>
      </div>

      <DecisionBar disposition={disposition} inBatch={inBatch} note={note} onDisposition={onDisposition} onNext={() => onNextException?.()} onNote={onNote} onSave={onSave} saveState={saveState} />
    </main>
  );
}
