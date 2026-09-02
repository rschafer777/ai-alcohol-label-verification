import { useEffect, useState } from "react";

import type { Evidence, ReferenceRecord, VerificationResult } from "../../contracts/types";

interface HistorySummary {
  id: string;
  createdAt: string;
  requestId: string;
  displayName: string;
  beverageType: ReferenceRecord["beverageType"] | "unresolved";
  summary: VerificationResult["summary"];
  disposition: string | null;
  reviewerNote: string;
  panelCount: number;
  panels: Array<{ panelId: string; fileName: string; imageUrl: string }>;
}

interface HistoryDetail extends HistorySummary {
  reference: unknown;
  result: VerificationResult;
}

interface HistoryResponse {
  items: HistorySummary[];
  total: number;
  cap: number;
  offset: number;
  pageSize: number;
  hasMore: boolean;
}

function typeLabel(value: ReferenceRecord["beverageType"] | "unresolved"): string {
  if (value === "malt_beverage") return "Beer / malt";
  if (value === "distilled_spirits") return "Distilled spirits";
  if (value === "wine") return "Wine";
  return "Type uncertain";
}

function statusClass(value: string): string {
  if (value.includes("No differences") || value === "approved") return "pass";
  if (value.includes("Differences") || value === "rejected") return "fail";
  return "warn";
}

function polygonPoints(evidence: Evidence): string {
  return evidence.polygonOriginalPixels.map((point) => `${point.x},${point.y}`).join(" ");
}

export function HistoryWorkspace({ onCountChange }: { onCountChange: (count: number) => void }) {
  const [data, setData] = useState<HistoryResponse>({ items: [], total: 0, cap: 500, offset: 0, pageSize: 25, hasMore: false });
  const [selected, setSelected] = useState<HistoryDetail | null>(null);
  const [type, setType] = useState("");
  const [summary, setSummary] = useState("");
  const [dispositionFilter, setDispositionFilter] = useState("");
  const [reviewDisposition, setReviewDisposition] = useState("");
  const [query, setQuery] = useState("");
  const [note, setNote] = useState("");
  const [message, setMessage] = useState("");
  const [evidenceRef, setEvidenceRef] = useState<string | null | undefined>(null);

  async function load(offset = 0) {
    const params = new URLSearchParams({ pageSize: "25", offset: String(offset) });
    if (type) params.set("beverageType", type);
    if (summary) params.set("summary", summary);
    if (dispositionFilter) params.set("disposition", dispositionFilter);
    if (query.trim()) params.set("q", query.trim());
    const response = await fetch(`/api/v1/history?${params}`);
    if (!response.ok) { setMessage("History could not be loaded."); return; }
    const value = await response.json() as HistoryResponse;
    setData(value);
    onCountChange(value.total);
    setMessage("");
    if (selected && !value.items.some((item) => item.id === selected.id)) setSelected(null);
  }

  async function open(id: string) {
    const response = await fetch(`/api/v1/history/${id}`);
    if (!response.ok) { setMessage("The selected result is no longer available."); return; }
    const detail = await response.json() as HistoryDetail;
    setSelected(detail);
    setReviewDisposition(detail.disposition ?? "");
    setNote(detail.reviewerNote);
    setEvidenceRef(null);
  }

  async function saveDisposition() {
    if (!selected) return;
    const response = await fetch(`/api/v1/history/${selected.id}/disposition`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ disposition: reviewDisposition || null, reviewerNote: note }) });
    setMessage(response.ok ? "Disposition saved." : "Disposition could not be saved.");
    if (response.ok) { await load(data.offset); await open(selected.id); }
  }

  async function remove(id: string) {
    if (!window.confirm("Delete this completed result and its retained images?")) return;
    const response = await fetch(`/api/v1/history/${id}`, { method: "DELETE" });
    if (response.ok) { if (selected?.id === id) setSelected(null); await load(data.offset); }
  }

  async function clearAll() {
    if (!window.confirm(`Delete all ${data.total} completed results and retained images?`)) return;
    const response = await fetch("/api/v1/history", { method: "DELETE" });
    if (response.ok) { setSelected(null); await load(0); }
  }

  useEffect(() => {
    const loadTimer = window.setTimeout(() => void load(0), 0);
    return () => window.clearTimeout(loadTimer);
    // Filters are applied explicitly with the Apply button.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectedEvidence = selected?.result.evidence.find(
    (evidence) => evidence.evidenceId === evidenceRef,
  ) ?? null;

  return (
    <section className="history-page">
      <div className="history-list-pane">
        <div className="page-heading"><div><p className="kicker">History</p><h1>Completed checks</h1><p>{data.total} of {data.cap} kept. The oldest records drop off first.</p></div><button className="btn ghost" disabled={!data.total} onClick={() => void clearAll()} type="button">Clear all {data.total}</button></div>
        <div className="history-filters"><select aria-label="Filter beverage type" onChange={(event) => setType(event.target.value)} value={type}><option value="">All types</option><option value="malt_beverage">Beer / malt</option><option value="wine">Wine</option><option value="distilled_spirits">Distilled spirits</option><option value="unresolved">Type uncertain</option></select><select aria-label="Filter machine result" onChange={(event) => setSummary(event.target.value)} value={summary}><option value="">All machine results</option><option>No differences found in checked fields</option><option>Review needed</option><option>Differences detected</option></select><select aria-label="Filter disposition" onChange={(event) => setDispositionFilter(event.target.value)} value={dispositionFilter}><option value="">All dispositions</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="more_info_requested">More info requested</option></select><input aria-label="Search history" onChange={(event) => setQuery(event.target.value)} placeholder="Date or text" value={query} /><button className="btn secondary" onClick={() => void load(0)} type="button">Apply</button></div>
        <p aria-live="polite" className="micro">{message}</p>
        <div className="table-wrap"><table><thead><tr><th>When</th><th>Product</th><th>Type</th><th>Panels</th><th>Machine result</th><th>Your disposition</th><th>Actions</th></tr></thead><tbody>{data.items.map((item) => <tr className={selected?.id === item.id ? "selected" : ""} key={item.id}><td>{new Date(item.createdAt).toLocaleString()}</td><th scope="row">{item.displayName}</th><td>{typeLabel(item.beverageType)}</td><td>{item.panelCount}</td><td><span className={`status-tag ${statusClass(item.summary)}`}>{item.summary}</span></td><td>{item.disposition?.replaceAll("_", " ") ?? "Undecided"}</td><td><button className="show-btn" onClick={() => void open(item.id)} type="button">Open</button><button className="delete-btn" onClick={() => void remove(item.id)} type="button">Delete</button></td></tr>)}</tbody></table></div>
        <div className="pager"><span>Showing {data.total ? data.offset + 1 : 0} to {Math.min(data.total, data.offset + data.items.length)} of {data.total}</span><button className="btn ghost" disabled={!data.offset} onClick={() => void load(Math.max(0, data.offset - data.pageSize))} type="button">Newer</button><button className="btn ghost" disabled={!data.hasMore} onClick={() => void load(data.offset + data.pageSize)} type="button">Older</button></div>
      </div>
      <aside className="blueprint history-drawer">
        {selected ? <><p className="kicker">Stored result</p><h2>{selected.displayName}</h2><p>{new Date(selected.createdAt).toLocaleString()} | {selected.requestId}</p><div className="drawer-status"><div><small>Machine result</small><span className={`status-tag ${statusClass(selected.summary)}`}>{selected.summary}</span></div><div><small>Your disposition</small><strong>{selected.disposition?.replaceAll("_", " ") ?? "Undecided"}</strong></div></div><div className="stored-images">{selected.panels.map((panel) => { const dimensions = selected.result.panels.find((item) => item.panelId === panel.panelId)?.originalDimensions; const highlighted = selectedEvidence?.panelId === panel.panelId; return <figure className={highlighted ? "highlighted" : ""} key={panel.panelId}><div><img alt={`Stored ${panel.fileName}`} src={panel.imageUrl} />{highlighted && dimensions ? <svg aria-label="Selected evidence location" role="img" viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}><polygon points={polygonPoints(selectedEvidence)} /></svg> : null}</div><figcaption>{panel.fileName}</figcaption></figure>; })}</div><div className="stored-checks">{selected.result.checks.map((check) => <div className={statusClass(check.state)} key={check.checkId}><strong>{check.label}</strong><span>{check.state}</span><small>{check.reasonText}</small>{check.evidenceRef ? <button className="show-btn" onClick={() => setEvidenceRef(check.evidenceRef)} type="button">Show on label</button> : null}</div>)}</div><p>Your judgment stays separate from the machine findings and can be changed.</p><div className="button-row"><button aria-pressed={reviewDisposition === "approved"} className="btn disposition approve" onClick={() => setReviewDisposition("approved")} type="button">Approve</button><button aria-pressed={reviewDisposition === "rejected"} className="btn disposition reject" onClick={() => setReviewDisposition("rejected")} type="button">Reject</button><button aria-pressed={reviewDisposition === "more_info_requested"} className="btn disposition more" onClick={() => setReviewDisposition("more_info_requested")} type="button">Request more info</button></div><label className="note-field">Reviewer note<input maxLength={1000} onChange={(event) => setNote(event.target.value)} value={note} /></label><button className="btn primary" onClick={() => void saveDisposition()} type="button">Save changes</button><button className="btn ghost" onClick={() => void remove(selected.id)} type="button">Delete this record</button><p className="micro">History uses the application database. Container replacement can clear this prototype environment.</p></> : <div className="drawer-empty"><h2>Select a result</h2><p>Stored images, evidence, checks, and reviewer disposition will appear here.</p></div>}
      </aside>
    </section>
  );
}
