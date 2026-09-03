import { useState, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import { AGENT_NAME } from "../../app/agent";
import { stateColor, type Disposition } from "../../components/status";
import { Badge, DispositionTag, SummaryTag } from "../../components/StatusTag";
import type { CheckResult, HistoryDetail } from "../../contracts/types";
import { beverageTypeLabel, displayLabel, evidenceFor, observedDisplay, panelIndexOf, reasonShort } from "../verification/check-view";
import { DecisionButtons } from "../verification/DecisionBar";
import { EvidencePolygons } from "../verification/EvidenceViewer";
import { slotTitle } from "../verification/review-images";

function asDisposition(value: string | null): Disposition {
  return value === "approved" || value === "rejected" || value === "more_info_requested" ? value : null;
}

/** True when the stored reference came from typed application values rather than the label read. */
function comparedWithApplication(reference: unknown): boolean {
  return typeof reference === "object" && reference !== null && (reference as { referenceProvenance?: unknown }).referenceProvenance === "manual";
}

export function StoredResultDrawer({ detail, onSave, onDelete }: { detail: HistoryDetail | null; onSave: (disposition: Disposition, note: string) => Promise<boolean>; onDelete: () => void }): ReactElement {
  const [panelIndex, setPanelIndex] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [disposition, setDisposition] = useState<Disposition>(asDisposition(detail?.disposition ?? null));
  const [note, setNote] = useState(detail?.reviewerNote ?? "");
  const [saveState, setSaveState] = useState("");

  if (!detail) {
    return (
      <aside aria-label="Stored result" className="card blueprint drawer">
        <Corners />
        <div className="drawer-head"><h6>Stored result</h6></div>
        <div className="drawer-empty"><span className="card-title">Select a result</span><span className="text-muted" style={{ fontSize: 13 }}>Stored images, every evidence region colored by result, the 24 checks, and your disposition appear here.</span></div>
      </aside>
    );
  }

  const result = detail.result;
  const checks = result.checks;
  const selected: CheckResult | null = checks.find((check) => check.checkId === selectedId) ?? null;
  const images = detail.panels.map((panel, index) => ({ src: panel.imageUrl, name: panel.fileName, alt: `Stored ${panel.fileName}`, title: slotTitle(index, detail.panels.length) }));
  const image = images[panelIndex] ?? images[0];
  const created = new Date(detail.createdAt);
  const when = Number.isNaN(created.getTime()) ? detail.createdAt : created.toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });
  const selectedColor = selected && selected.applicable ? stateColor(selected.state) : "var(--lv-divider)";
  const summary = result.badImage ? "Bad image" as const : detail.summary;

  function select(id: string) {
    const check = checks.find((item) => item.checkId === id);
    if (!check) return;
    if (selectedId === id) { setSelectedId(null); return; }
    setSelectedId(id);
    const evidence = evidenceFor(result, check);
    if (evidence) setPanelIndex(panelIndexOf(result, evidence.panelId));
  }

  async function save(next: Disposition, nextNote: string) {
    setDisposition(next);
    const ok = await onSave(next, nextNote);
    setSaveState(ok ? "Saved" : "Could not save. Try again.");
  }

  return (
    <aside aria-label="Stored result" className="card blueprint drawer">
      <Corners />
      <div className="drawer-head"><h6>Stored result</h6><span className="text-muted">{when} · {detail.requestId.slice(0, 10)}</span></div>
      <div><span className="card-title">{detail.displayName}</span><br /><span className="drawer-sub text-muted">{beverageTypeLabel(detail.beverageType)} · {detail.panelCount} image{detail.panelCount === 1 ? "" : "s"} · reviewed by {AGENT_NAME}{comparedWithApplication(detail.reference) ? " · compared with application values" : ""}</span></div>
      <div className="result-cells">
        <div><span className="dl-label text-muted">Machine result</span><br /><SummaryTag summary={summary} /></div>
        <div><span className="dl-label text-muted">Your disposition</span><br /><DispositionTag value={disposition} /></div>
      </div>
      <div className="thumbs">
        {images.map((item, index) => <button aria-label={`Show ${item.title}`} aria-pressed={panelIndex === index} className="thumb-btn" key={item.src} onClick={() => { setPanelIndex(index); setSelectedId(null); }} type="button"><img alt="" src={item.src} /><span>{images.length > 1 ? item.title : item.name}</span></button>)}
        <span className="hint text-muted">Select an image to open it. Regions are colored by result.</span>
      </div>
      <div className="stage">
        <div className="stage-inner">
          {image ? <img alt={image.alt} src={image.src} /> : null}
          <EvidencePolygons panelIndex={panelIndex} result={result} selected={selected} />
        </div>
      </div>
      <div className="legend large text-muted"><span><i className="pass" />Passes</span><span><i className="warn" />Questionable</span><span><i className="fail" />Rejected</span><span><i className="none" />Not verified</span></div>
      <div aria-live="polite" className="sel-caption" style={{ borderColor: selectedColor }}>
        <div className="row"><strong>{selected ? displayLabel(selected) : "All evidence regions"}</strong>{selected ? <Badge applicable={selected.applicable} state={selected.state} /> : null}</div>
        <span><span className="text-muted">Read:</span> {selected ? observedDisplay(selected, result) : `${result.evidence.filter((item) => item.panelId === result.panels[panelIndex]?.panelId).length} regions on this image`}</span>
        {selected && selected.state !== "Match" ? <span>{selected.reasonText}</span> : null}
      </div>
      <ol aria-label="Stored checks" className="check-list" tabIndex={0}>
        {checks.map((check) => (
          <li key={check.checkId}>
            <button aria-pressed={selectedId === check.checkId} className={check.applicable ? "" : "na"} onClick={() => select(check.checkId)} style={{ borderLeftColor: check.applicable ? stateColor(check.state) : "transparent" }} type="button">
              <Badge applicable={check.applicable} mini state={check.state} />
              <span><strong>{displayLabel(check)}</strong> <span className="text-muted">· {reasonShort(check)}</span></span>
            </button>
          </li>
        ))}
      </ol>
      <div className="override">
        <span className="helper text-muted">Your judgement overrides the machine result. Change it any time; the machine result stays on record.</span>
        <div className="row"><DecisionButtons onChange={(value) => void save(value, note)} value={disposition} withKeys={false} /></div>
        <input aria-label="Reviewer note" className="input" maxLength={1000} onBlur={() => { if (note !== detail.reviewerNote) void save(disposition, note); }} onChange={(event) => setNote(event.target.value)} placeholder="Note (optional)" value={note} />
        {saveState ? <span aria-live="polite" className="save-state text-muted">{saveState}</span> : null}
      </div>
      <div className="drawer-foot"><span className="text-muted">History lives in this app's database and can be lost if the demo container is replaced.</span><button className="btn btn-ghost" onClick={onDelete} type="button">{icons.trash()} Delete this record</button></div>
    </aside>
  );
}
