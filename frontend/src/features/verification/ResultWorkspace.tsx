import { useEffect, useMemo, useState } from "react";

import type { AnalysisResult, CheckResult, Evidence, VerificationResult } from "../../contracts/types";

type Layout = "table" | "cards" | "image";
type Disposition = "approved" | "rejected" | "more_info_requested" | null;

interface ResultWorkspaceProps {
  analysis: AnalysisResult;
  result: VerificationResult;
  sourcePanels: File[];
  onStartOver: () => void;
  onAddFiles?: (files: File[]) => void;
}

const WARNING_IDS = new Set([
  "warning_applicability", "warning_wording", "warning_heading_uppercase",
  "warning_heading_emphasis", "warning_body_not_bold", "warning_separation",
  "warning_continuity", "warning_contrast", "warning_legibility", "warning_physical_size",
]);

const GROUPS: Array<{ name: string; ids: string[] }> = [
  { name: "Identity", ids: ["beverage_type", "brand", "class_type"] },
  { name: "Content statements", ids: ["abv", "proof", "net_contents", "producer", "country"] },
  { name: "Type-specific rules", ids: ["wine_appellation", "wine_sulfites", "spirits_field_of_vision", "malt_class_designation"] },
  { name: "Government warning", ids: [...WARNING_IDS] },
  { name: "Image and coverage", ids: ["panel_coverage", "image_quality"] },
];

const REQUIRED_WARNING = "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems.";

function stateClass(value: string): string {
  if (value === "Match") return "pass";
  if (value === "Mismatch") return "fail";
  if (value === "Review") return "warn";
  return "none";
}

function StatusTag({ value }: { value: string }) {
  const icon = value === "Match" || value.includes("No differences") ? "OK" : value === "Mismatch" || value.includes("Differences") ? "X" : value === "Review" || value.includes("Review") ? "?" : "-";
  return <span className={`status-tag ${stateClass(value)}`}><span aria-hidden="true">{icon}</span>{value}</span>;
}

function typeLabel(value: string | null): string {
  if (value === "malt_beverage") return "Beer / malt beverage";
  if (value === "distilled_spirits") return "Distilled spirits";
  if (value === "wine") return "Wine";
  return "Type uncertain";
}

function groupFor(check: CheckResult): string {
  return GROUPS.find((group) => group.ids.includes(check.checkId))?.name ?? "Other";
}

function CheckTable({ checks, selected, onSelect }: { checks: CheckResult[]; selected: string | null; onSelect: (id: string | null) => void }) {
  return (
    <div className="checks-groups">
      {GROUPS.map((group) => {
        const rows = checks.filter((check) => group.ids.includes(check.checkId));
        if (!rows.length) return null;
        return <section className="check-group" key={group.name}><div className="group-title"><h3>{group.name}</h3><span>{rows.filter((item) => item.state === "Match").length} match | {rows.filter((item) => item.state === "Review").length} review | {rows.filter((item) => item.state === "Mismatch").length} mismatch</span></div><div aria-label={`${group.name} checks`} className="table-wrap" tabIndex={0}><table className="checks-table"><thead><tr><th>Check</th><th>Rule expects</th><th>Read on label</th><th>Result</th><th>Evidence</th></tr></thead><tbody>{rows.map((check) => <tr className={selected === check.checkId ? "selected" : ""} key={check.checkId}><th scope="row">{check.label}{!check.applicable ? <small>Not applicable</small> : null}</th><td>{check.referenceDisplay ?? "Selected rule profile"}</td><td>{check.observedDisplay ?? "Not reliably read"}</td><td><StatusTag value={check.state} /><small>{check.reasonText}</small></td><td>{check.evidenceRef ? <button aria-pressed={selected === check.checkId} className="show-btn" onClick={() => onSelect(selected === check.checkId ? null : check.checkId)} type="button">Show</button> : <span className="micro">None</span>}</td></tr>)}</tbody></table></div></section>;
      })}
    </div>
  );
}

function CheckCards({ checks, selected, onSelect }: { checks: CheckResult[]; selected: string | null; onSelect: (id: string | null) => void }) {
  return <div className="check-cards">{checks.map((check) => <article className={`check-card ${selected === check.checkId ? "selected" : ""}`} key={check.checkId}><div className="section-row"><h3>{check.label}</h3><StatusTag value={check.state} /></div><dl><div><dt>Rule expects</dt><dd>{check.referenceDisplay ?? "Selected profile requirement"}</dd></div><div><dt>Read on label</dt><dd>{check.observedDisplay ?? "Not reliably read"}</dd></div></dl><p>{check.reasonText}</p><div className="section-row"><span className="micro">{groupFor(check)} | {check.capability}</span>{check.evidenceRef ? <button className="show-btn" onClick={() => onSelect(selected === check.checkId ? null : check.checkId)} type="button">Show on label</button> : null}</div></article>)}</div>;
}

function CheckRail({ checks, selected, onSelect }: { checks: CheckResult[]; selected: string | null; onSelect: (id: string | null) => void }) {
  const active = checks.find((check) => check.checkId === selected) ?? checks[0];
  return <div className="image-first"><div className="check-rail">{checks.map((check) => <button className={selected === check.checkId ? "selected" : ""} key={check.checkId} onClick={() => onSelect(check.checkId)} type="button"><span>{check.label}</span><StatusTag value={check.state} /></button>)}</div>{active ? <article className="blueprint selected-check"><div className="section-row"><h2>{active.label}</h2><StatusTag value={active.state} /></div><h3>Rule expects</h3><p>{active.referenceDisplay ?? "Selected profile requirement"}</p><h3>Read on label</h3><p>{active.observedDisplay ?? "Not reliably read"}</p><p>{active.reasonText}</p></article> : null}</div>;
}

function EvidenceViewer({ result, files, selectedCheckId, onClear, onAddFiles }: { result: VerificationResult; files: File[]; selectedCheckId: string | null; onClear: () => void; onAddFiles?: (files: File[]) => void }) {
  const [panelIndex, setPanelIndex] = useState(0);
  const [zoom, setZoom] = useState(100);
  const [rotation, setRotation] = useState(0);
  const [enhanced, setEnhanced] = useState(false);
  const urls = useMemo(() => files.map((file) => URL.createObjectURL(file)), [files]);
  useEffect(() => () => urls.forEach((url) => URL.revokeObjectURL(url)), [urls]);
  const panel = result.panels[panelIndex];
  const check = result.checks.find((item) => item.checkId === selectedCheckId);
  const selectedEvidence = result.evidence.find((item) => item.evidenceId === check?.evidenceRef);
  const visibleEvidence = selectedEvidence ? [selectedEvidence] : result.evidence.filter((item) => item.panelId === panel?.panelId);
  const dimensions = panel?.originalDimensions;
  return (
    <section className="viewer-pane" aria-labelledby="viewer-heading">
      <div className="viewer-tools"><h2 id="viewer-heading">Label images <span>{files.length} of 3</span></h2><button onClick={() => setZoom(Math.max(50, zoom - 25))} type="button">Zoom -</button><strong>{zoom}%</strong><button onClick={() => setZoom(Math.min(250, zoom + 25))} type="button">Zoom +</button><button onClick={() => setRotation((rotation + 90) % 360)} type="button">Rotate</button><button aria-pressed={enhanced} onClick={() => setEnhanced((value) => !value)} type="button">Enhance</button></div>
      <div className="image-slots" role="group" aria-label="Label images">{[0, 1, 2].map((index) => files[index] ? <button aria-pressed={panelIndex === index} className={panelIndex === index ? "selected" : ""} key={index} onClick={() => setPanelIndex(index)} type="button"><img alt="" src={urls[index]} /><span><strong>Image {index + 1}</strong><small>{files[index]?.name}</small></span></button> : <label className="empty-slot" key={index}><strong>Add image</strong><small>Image {index + 1} of 3</small><input accept="image/jpeg,image/png,image/webp" className="sr-only" onChange={(event) => { const added = Array.from(event.target.files ?? []); if (added.length) onAddFiles?.(added); }} type="file" /></label>)}</div>
      <div className="viewer-meta"><span>Viewing <strong>{files[panelIndex]?.name ?? "image"}</strong></span><span>Coverage: <strong>{panel?.coverageState ?? "Unknown"}</strong></span><span>Solid outline is selected evidence. Dotted outlines show all located fields.</span></div>
      <div aria-label="Scrollable label evidence image" className="image-stage" tabIndex={0}><div className={`image-transform ${enhanced ? "enhanced" : ""}`} style={{ transform: `scale(${zoom / 100}) rotate(${rotation}deg)` }}>{urls[panelIndex] ? <img alt={`Label evidence from ${files[panelIndex]?.name ?? "uploaded image"}`} src={urls[panelIndex]} /> : null}{dimensions ? <svg aria-hidden="true" className="evidence-overlay" preserveAspectRatio="none" viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}>{visibleEvidence.map((evidence: Evidence) => <polygon className={selectedEvidence ? stateClass(check?.state ?? "") : "map"} key={evidence.evidenceId} points={evidence.polygonOriginalPixels.map((point) => `${point.x},${point.y}`).join(" ")} />)}</svg> : null}</div></div>
      <div className={`evidence-caption ${stateClass(check?.state ?? "")}`} aria-live="polite"><strong>{check?.label ?? "All evidence regions"}</strong><span>{selectedEvidence?.textSnippet ? `Read: ${selectedEvidence.textSnippet}` : `${visibleEvidence.length} regions located on this image`}</span>{selectedEvidence ? <button className="show-btn" onClick={onClear} type="button">Show all regions</button> : null}</div>
    </section>
  );
}

function WarningInspect({ checks, evidence, onBack }: { checks: CheckResult[]; evidence: Evidence[]; onBack: () => void }) {
  const rows = checks.filter((check) => WARNING_IDS.has(check.checkId));
  const worst = rows.some((check) => check.state === "Mismatch") ? "Mismatch" : rows.some((check) => check.state === "Review") ? "Review" : "Match";
  const observed = evidence.find((item) => item.evidenceId === rows.find((item) => item.checkId === "warning_wording")?.evidenceRef)?.textSnippet;
  return <section className="warning-page"><div className="review-header"><button className="btn ghost" onClick={onBack} type="button">Back to all 24 checks</button><h1>Government warning statement</h1><span className="neutral-tag">27 CFR Part 16 | exact text required</span><StatusTag value={worst} /></div><div className="warning-grid"><article className="blueprint warning-copy"><p className="kicker">Required text</p><p><strong>GOVERNMENT WARNING:</strong> {REQUIRED_WARNING.replace("GOVERNMENT WARNING: ", "")}</p></article><article className="blueprint warning-copy"><p className="kicker">Read on label</p><p>{observed ?? "The complete warning could not be read reliably from the submitted images."}</p></article></div><div className="table-wrap"><table className="checks-table"><thead><tr><th>Check</th><th>Rule expects</th><th>Read on label</th><th>Result</th></tr></thead><tbody>{rows.map((check) => <tr key={check.checkId}><th scope="row">{check.label}</th><td>{check.referenceDisplay ?? "Part 16 requirement"}</td><td>{check.observedDisplay ?? "Not reliably read"}</td><td><StatusTag value={check.state} /><small>{check.reasonText}</small></td></tr>)}</tbody></table></div><div className="decision-bar"><span>Warning detail does not change the overall machine result.</span><button className="btn primary" onClick={onBack} type="button">Continue review</button></div></section>;
}

export function ResultWorkspace({ analysis, result, sourcePanels, onStartOver, onAddFiles }: ResultWorkspaceProps) {
  const [layout, setLayout] = useState<Layout>("table");
  const [selectedCheckId, setSelectedCheckId] = useState<string | null>(null);
  const [warningOpen, setWarningOpen] = useState(false);
  const [disposition, setDisposition] = useState<Disposition>(null);
  const [note, setNote] = useState("");
  const [saveState, setSaveState] = useState("");
  const checks = result.checks;
  const tally = { match: checks.filter((item) => item.state === "Match").length, review: checks.filter((item) => item.state === "Review").length, mismatch: checks.filter((item) => item.state === "Mismatch").length, unverified: checks.filter((item) => item.state === "Not verified").length };

  async function save() {
    if (result.historyId) {
      const response = await fetch(`/api/v1/history/${result.historyId}/disposition`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ disposition, reviewerNote: note }) });
      setSaveState(response.ok ? "Saved" : "Could not save. Retry before leaving.");
      if (!response.ok) return;
    }
    onStartOver();
  }

  useEffect(() => {
    function shortcut(event: KeyboardEvent) {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
      if (event.key.toLowerCase() === "a") setDisposition("approved");
      if (event.key.toLowerCase() === "r") setDisposition("rejected");
      if (event.key.toLowerCase() === "m") setDisposition("more_info_requested");
      if (event.key.toLowerCase() === "w") setWarningOpen(true);
    }
    window.addEventListener("keydown", shortcut);
    return () => window.removeEventListener("keydown", shortcut);
  }, []);

  if (warningOpen) return <WarningInspect checks={checks} evidence={result.evidence} onBack={() => setWarningOpen(false)} />;
  return (
    <section className="review-page">
      <div className="review-header"><button className="btn ghost" onClick={onStartOver} type="button">Start over</button><div><h1>{analysis.draft.brandName ?? "Product label"}</h1><span className="neutral-tag">{typeLabel(analysis.draft.beverageType)} | inferred, {analysis.beverageTypeConfidence ? `${Math.round(analysis.beverageTypeConfidence * 100)}% signal` : "review needed"}</span></div><span className="review-time">{sourcePanels.length} image{sourcePanels.length === 1 ? "" : "s"} | {(result.serverDurationMs / 1000).toFixed(1)} s</span><div><small>Machine result</small><StatusTag value={result.summary} /></div><div className="segmented" aria-label="Review layout">{(["table", "cards", "image"] as Layout[]).map((value) => <button aria-pressed={layout === value} key={value} onClick={() => setLayout(value)} type="button">{value === "image" ? "Image first" : value[0]?.toUpperCase() + value.slice(1)}</button>)}</div></div>
      <div className={`review-body layout-${layout}`}><EvidenceViewer files={sourcePanels} onAddFiles={onAddFiles} onClear={() => setSelectedCheckId(null)} result={result} selectedCheckId={selectedCheckId} /><section className="checks-pane"><div className="checks-heading"><div><p className="kicker">24 selected checks | {typeLabel(analysis.draft.beverageType)}</p><h2>{tally.match} match | {tally.review} review | {tally.mismatch} mismatch | {tally.unverified} not verified</h2></div><button className="btn secondary" onClick={() => setWarningOpen(true)} type="button">Inspect warning</button></div>{layout === "table" ? <CheckTable checks={checks} onSelect={setSelectedCheckId} selected={selectedCheckId} /> : layout === "cards" ? <CheckCards checks={checks} onSelect={setSelectedCheckId} selected={selectedCheckId} /> : <CheckRail checks={checks} onSelect={setSelectedCheckId} selected={selectedCheckId} />}<details><summary>Limitations reported with this result ({result.limitations.length})</summary><ul>{result.limitations.map((item) => <li key={item}>{item}</li>)}</ul><p className="micro">Model {result.modelIdentity} | Policy {result.profileVersion} | Request {result.requestId}</p></details></section></div>
      <div className="decision-bar"><div><small>Your disposition</small><strong>{disposition ? disposition.replaceAll("_", " ") : "Undecided"}</strong></div><button aria-pressed={disposition === "approved"} className="btn disposition approve" onClick={() => setDisposition("approved")} type="button">Approve A</button><button aria-pressed={disposition === "rejected"} className="btn disposition reject" onClick={() => setDisposition("rejected")} type="button">Reject R</button><button aria-pressed={disposition === "more_info_requested"} className="btn disposition more" onClick={() => setDisposition("more_info_requested")} type="button">Request more info M</button><label className="note-field"><span className="sr-only">Reviewer note</span><input maxLength={1000} onChange={(event) => setNote(event.target.value)} placeholder="Note (optional). Stays with this record." value={note} /></label><span aria-live="polite" className="micro">{saveState}</span><button className="btn primary" onClick={() => void save()} type="button">Save and check another</button></div>
    </section>
  );
}
