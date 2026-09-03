import { useState, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import { Spinner } from "../../components/Spinner";
import { summaryColor } from "../../components/status";
import { DispositionTag, SummaryTag } from "../../components/StatusTag";
import { beverageTypeLabel, firstException, reasonShort } from "../verification/check-view";
import type { BatchGroup, BatchImage, BatchProgress } from "./batch-state";
import { isException, summaryOf } from "./batch-state";
import { BatchStats } from "./BatchStats";

type Filter = "attention" | "all" | "clear" | "review" | "diff" | "bad" | "failed";

function matches(group: BatchGroup, filter: Filter): boolean {
  const summary = summaryOf(group);
  switch (filter) {
    case "all": return true;
    case "attention": return isException(group);
    case "clear": return summary === "No differences found in checked fields";
    case "review": return summary === "Review needed";
    case "diff": return summary === "Differences detected";
    case "bad": return summary === "Bad image";
    case "failed": return summary === "Failed";
  }
}

export function BatchRun({ batchName, groups, images, progress, onBack, onCancel, onRetryFailed, onRetry, onExportCsv, onExportJson, onOpen, onNextException }: {
  batchName: string;
  groups: BatchGroup[];
  images: Map<string, BatchImage>;
  progress: BatchProgress;
  onBack: () => void;
  onCancel: () => void;
  onRetryFailed: () => void;
  onRetry: (id: string) => void;
  onExportCsv: () => void;
  onExportJson: () => void;
  onOpen: (id: string) => void;
  onNextException: () => void;
}): ReactElement {
  const [filter, setFilter] = useState<Filter>("attention");
  const { counts } = progress;
  const imageCount = counts.images;
  const currentIndex = progress.current ? groups.findIndex((group) => group.id === progress.current?.productId) + 1 : 0;
  const stageText = progress.state === "running" && progress.current ? `${progress.current.stage} · product ${currentIndex} of ${groups.length}` : progress.state === "completed" ? "Completed" : progress.state === "completed_with_errors" ? "Completed with errors" : progress.state === "cancelled" ? "Cancelled" : "Queued";
  const filters: Array<[Filter, string, number]> = [
    ["attention", "Needs attention", groups.filter((group) => isException(group)).length],
    ["all", "All", groups.length],
    ["clear", "No differences", groups.filter((group) => matches(group, "clear")).length],
    ["review", "Review", counts.review],
    ["diff", "Differences", counts.difference],
    ["bad", "Bad image", counts.badImage],
    ["failed", "Failed", counts.failed],
  ];
  const rows = groups.filter((group) => matches(group, filter));
  const done = counts.complete + counts.failed + counts.cancelled;
  const running = progress.state === "running" || progress.state === "queued";

  return (
    <main className="batch-run" data-screen-label="Batch run">
      <header className="batch-run-header">
        <button className="btn btn-ghost" onClick={onBack} type="button">{icons.back()} Groups</button>
        <div><h6 className="kicker">Check a batch · step 3 of 3</h6><h2>{batchName}: {groups.length} product{groups.length === 1 ? "" : "s"}, {imageCount} image{imageCount === 1 ? "" : "s"}</h2></div>
        <span className="stage-tag"><span className="text-muted">Stage</span><span className="tag tag-info">{running ? <Spinner /> : null}{stageText}</span></span>
        <button className="btn btn-secondary" disabled={!running} onClick={onCancel} type="button">Cancel remaining</button>
        <button className="btn btn-secondary" disabled={!counts.failed || running} onClick={onRetryFailed} type="button">Retry failed ({counts.failed})</button>
        <button className="btn btn-secondary" disabled={!counts.complete} onClick={onExportCsv} type="button">{icons.download()} CSV</button>
        <button className="btn btn-secondary" disabled={!counts.complete} onClick={onExportJson} type="button">{icons.download()} Detailed JSON</button>
      </header>
      <BatchStats progress={progress} />
      <div className="batch-run-body">
        <div className="progress-track"><div style={{ width: `${groups.length ? (done / groups.length) * 100 : 0}%` }} /></div>
        <div className="batch-run-table">
          <div className="batch-filters">
            <span className="show text-muted">Show</span>
            {filters.map(([key, label, count]) => <button aria-pressed={filter === key} className={`btn chip ${filter === key ? "btn-secondary" : "btn-ghost"}`} key={key} onClick={() => setFilter(key)} type="button">{label} · {count}</button>)}
            <span className="spacer" />
            <button className="btn btn-primary blueprint" disabled={!groups.some((group) => isException(group) && group.result && group.disposition === null)} onClick={onNextException} type="button"><Corners />Open next exception {icons.arrow()} <kbd>E</kbd></button>
          </div>
          <div className="table-wrap">
            <table className="table batch-table">
              <thead><tr><th className="thumb-col" /><th>Product</th><th>Type</th><th>Images</th><th>Machine result</th><th>Why</th><th style={{ textAlign: "right" }}>Time</th><th>Attempts</th><th>Your disposition</th><th /></tr></thead>
              <tbody>
                {rows.map((group) => {
                  const summary = summaryOf(group);
                  const exception = group.result ? firstException(group.result) : null;
                  const why = group.error ? group.error.message : group.runStatus === "running" ? "Reading label…" : group.runStatus === "queued" ? "Waiting" : exception ? reasonShort(exception) : "-";
                  const thumb = images.get(group.imageIds[0] ?? "");
                  const type = group.analysis?.draft.beverageType ?? group.inferredType;
                  const imported = group.analysis?.draft.isImported;
                  return (
                    <tr className={group.runStatus === "queued" ? "queued" : ""} key={group.id} style={{ boxShadow: `inset 3px 0 0 ${summaryColor(summary)}` }}>
                      <td>{thumb ? <img alt="" src={thumb.url} /> : null}</td>
                      <td className="w500">{group.name}</td>
                      <td>{type ? `${beverageTypeLabel(type, true)}${imported ? " · imported" : ""}` : "-"}</td>
                      <td>{group.imageIds.length}</td>
                      <td>{summary ? <SummaryTag summary={summary} /> : <span className="text-muted">-</span>}</td>
                      <td className="why text-muted">{why}</td>
                      <td className="time">{group.durationMs == null ? "-" : `${(group.durationMs / 1000).toFixed(1)} s`}</td>
                      <td>{group.attempts}</td>
                      <td><DispositionTag value={group.disposition} /></td>
                      <td className="right">{group.result ? <button className="btn btn-ghost" onClick={() => onOpen(group.id)} type="button">Open</button> : group.runStatus === "failed" || group.runStatus === "cancelled" ? <button className="btn btn-ghost" disabled={running} onClick={() => onRetry(group.id)} type="button">Retry</button> : null}</td>
                    </tr>
                  );
                })}
                {!rows.length ? <tr><td className="text-muted" colSpan={10}>Nothing matches this filter.</td></tr> : null}
              </tbody>
            </table>
          </div>
          <p className="batch-run-note text-muted">Products run one at a time. A failure or cancellation on one product never touches the others; completed products are already in History. Retrying creates a new attempt and keeps the old one.</p>
        </div>
      </div>
    </main>
  );
}
