import { useCallback, useEffect, useRef, useState, type ReactElement } from "react";

import { createHistoryClient, type HistoryClient } from "../../api/history-client";
import { icons } from "../../components/icons";
import { summaryColor, type Disposition } from "../../components/status";
import { DispositionTag, SummaryTag } from "../../components/StatusTag";
import type { HistoryDetail, HistoryPage } from "../../contracts/types";
import { whenLabel } from "../home/format";
import { beverageTypeLabel } from "../verification/check-view";
import { StoredResultDrawer } from "./StoredResultDrawer";

const EMPTY_PAGE: HistoryPage = { items: [], total: 0, cap: 500, offset: 0, pageSize: 25, hasMore: false };

export function ConfirmDialog({ title, body, confirmLabel, onConfirm, onCancel }: { title: string; body: string; confirmLabel: string; onConfirm: () => void; onCancel: () => void }): ReactElement {
  const first = useRef<HTMLButtonElement>(null);
  useEffect(() => { first.current?.focus(); }, []);
  return (
    <div className="dialog-backdrop" onClick={onCancel}>
      <div aria-label={title} className="dialog" onClick={(event) => event.stopPropagation()} role="dialog">
        <div className="dialog-title">{title}</div>
        <p className="dialog-body">{body}</p>
        <div className="dialog-actions"><button className="btn btn-ghost" onClick={onCancel} ref={first} type="button">Cancel</button><button className="btn btn-secondary btn-reject" onClick={onConfirm} type="button">{icons.trash()} {confirmLabel}</button></div>
      </div>
    </div>
  );
}

export function History({ historyClient, initialRecordId, onCountChange, onScreenTitle }: { historyClient?: HistoryClient; initialRecordId?: string | null; onCountChange: (total: number, cap: number) => void; onScreenTitle?: (title: string) => void }): ReactElement {
  const client = useRef(historyClient ?? createHistoryClient()).current;
  const [page, setPage] = useState<HistoryPage>(EMPTY_PAGE);
  const [selected, setSelected] = useState<HistoryDetail | null>(null);
  const [type, setType] = useState("");
  const [summary, setSummary] = useState("");
  const [dispositionFilter, setDispositionFilter] = useState("");
  const [query, setQuery] = useState("");
  const [message, setMessage] = useState("");
  const [confirm, setConfirm] = useState<{ kind: "one"; id: string; name: string } | { kind: "all" } | null>(null);

  const load = useCallback(async (offset = 0, filters = { type, summary, dispositionFilter, query }) => {
    try {
      const value = await client.list({ offset, pageSize: 25, beverageType: filters.type, summary: filters.summary, disposition: filters.dispositionFilter, q: filters.query });
      setPage(value);
      onCountChange(value.total, value.cap);
      setMessage("");
      setSelected((current) => current && !value.items.some((item) => item.id === current.id) && offset === 0 && !filters.query && !filters.type && !filters.summary && !filters.dispositionFilter ? null : current);
    } catch {
      setMessage("History could not be loaded.");
    }
  }, [client, onCountChange, type, summary, dispositionFilter, query]);

  const open = useCallback(async (id: string) => {
    const detail = await client.get(id);
    if (!detail) { setMessage("The selected result is no longer available."); return; }
    setSelected(detail);
  }, [client]);

  useEffect(() => {
    onScreenTitle?.("History");
    const handle = window.setTimeout(() => { void load(0); if (initialRecordId) void open(initialRecordId); }, 0);
    return () => window.clearTimeout(handle);
    // Initial load only; filters trigger their own loads below.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handle = window.setTimeout(() => void load(0, { type, summary, dispositionFilter, query }), query ? 300 : 0);
    return () => window.clearTimeout(handle);
  }, [type, summary, dispositionFilter, query, load]);

  async function saveDisposition(disposition: Disposition, note: string) {
    if (!selected) return false;
    const ok = await client.setDisposition(selected.id, disposition, note);
    if (ok) {
      setSelected({ ...selected, disposition, reviewerNote: note });
      await load(page.offset);
    }
    return ok;
  }

  async function removeOne(id: string) {
    setConfirm(null);
    const ok = await client.remove(id);
    if (ok) {
      if (selected?.id === id) setSelected(null);
      await load(page.offset);
    } else setMessage("The record could not be deleted.");
  }

  async function clearAll() {
    setConfirm(null);
    await client.clear();
    setSelected(null);
    await load(0);
  }

  return (
    <main className="history" data-screen-label="History">
      <section className="history-list">
        <header className="history-header">
          <div><h6 className="kicker">History</h6><h2>Completed checks</h2></div>
          <span className="kept text-muted">{page.total} of {page.cap} kept · oldest drop off first</span>
          <button className="btn btn-ghost" disabled={!page.total} onClick={() => setConfirm({ kind: "all" })} type="button">{icons.trash()} Clear all {page.total}…</button>
        </header>
        <div className="history-filters">
          <select aria-label="Type" className="input" onChange={(event) => setType(event.target.value)} value={type}><option value="">All types</option><option value="malt_beverage">Beer / malt</option><option value="wine">Wine</option><option value="distilled_spirits">Distilled spirits</option><option value="unresolved">Type unresolved</option></select>
          <select aria-label="Machine result" className="input" onChange={(event) => setSummary(event.target.value)} value={summary}><option value="">Any machine result</option><option value="No differences found in checked fields">No differences found</option><option value="Review needed">Review needed</option><option value="Differences detected">Differences detected</option></select>
          <select aria-label="Disposition" className="input" onChange={(event) => setDispositionFilter(event.target.value)} value={dispositionFilter}><option value="">Any disposition</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="more_info_requested">More info requested</option></select>
          <input aria-label="Date or text" className="input search" onChange={(event) => setQuery(event.target.value)} placeholder="Date or text…" value={query} />
        </div>
        {message ? <p aria-live="polite" className="form-error">{message}</p> : null}
        <div className="table-wrap">
          <table className="table history-table reflow">
            <thead><tr><th>When</th><th>Product</th><th>Type</th><th>Panels</th><th>Machine result</th><th>Your disposition</th><th /></tr></thead>
            <tbody>
              {page.items.map((item) => (
                <tr aria-selected={selected?.id === item.id} key={item.id} style={{ boxShadow: `inset 3px 0 0 ${summaryColor(item.summary)}` }}>
                  <td className="text-muted nowrap" data-label="When">{whenLabel(item.createdAt)}</td>
                  <td className="w500" data-label="Product">{item.displayName}</td>
                  <td data-label="Type">{beverageTypeLabel(item.beverageType, true)}</td>
                  <td data-label="Panels">{item.panelCount}</td>
                  <td data-label="Machine result"><SummaryTag summary={item.summary} /></td>
                  <td data-label="Your disposition"><DispositionTag value={item.disposition} /></td>
                  <td className="actions"><button className="btn btn-ghost" onClick={() => void open(item.id)} type="button">Open</button><button aria-label={`Delete ${item.displayName}`} className="btn btn-ghost btn-icon" onClick={() => setConfirm({ kind: "one", id: item.id, name: item.displayName })} type="button">{icons.trash()}</button></td>
                </tr>
              ))}
              {!page.items.length ? <tr><td className="text-muted" colSpan={7}>No completed checks yet. When you finish a check it appears here: the images, every finding with its evidence region, and your disposition.</td></tr> : null}
            </tbody>
          </table>
        </div>
        <div className="pager text-muted">
          <span>Showing {page.total ? page.offset + 1 : 0}-{Math.min(page.total, page.offset + page.items.length)} of {page.total}</span>
          <span><button className="btn btn-ghost" disabled={!page.offset} onClick={() => void load(Math.max(0, page.offset - page.pageSize))} type="button">Newer</button><button className="btn btn-ghost" disabled={!page.hasMore} onClick={() => void load(page.offset + page.pageSize)} type="button">Older</button></span>
        </div>
      </section>
      <StoredResultDrawer detail={selected} key={selected?.id ?? "none"} onDelete={() => selected && setConfirm({ kind: "one", id: selected.id, name: selected.displayName })} onSave={saveDisposition} />
      {confirm?.kind === "one" ? <ConfirmDialog body={`Delete ${confirm.name} and its retained images? This cannot be undone.`} confirmLabel="Delete record" onCancel={() => setConfirm(null)} onConfirm={() => void removeOne(confirm.id)} title="Delete this record?" /> : null}
      {confirm?.kind === "all" ? <ConfirmDialog body={`Delete all ${page.total} completed results and their retained images? This cannot be undone.`} confirmLabel={`Delete all ${page.total}`} onCancel={() => setConfirm(null)} onConfirm={() => void clearAll()} title="Clear history?" /> : null}
    </main>
  );
}
