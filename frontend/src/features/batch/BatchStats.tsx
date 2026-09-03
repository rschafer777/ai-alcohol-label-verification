import type { ReactElement } from "react";

import type { BatchProgress } from "./batch-state";

function seconds(ms: number | null): string {
  return ms === null ? "-" : `${(ms / 1000).toFixed(1)} s`;
}

export function BatchStats({ progress }: { progress: BatchProgress }): ReactElement {
  const { counts, timing } = progress;
  const cells: Array<[string, string, "pass" | "warn" | "fail" | ""]> = [
    ["Products", String(counts.total), ""],
    ["Images", String(counts.images), ""],
    ["Processed", String(counts.complete + counts.failed), counts.complete + counts.failed ? "pass" : ""],
    ["Remaining", String(counts.remaining), ""],
    ["Running", String(counts.running), ""],
    ["Queued", String(counts.queued), ""],
    ["Review", String(counts.review), counts.review ? "warn" : ""],
    ["Differences", String(counts.difference), counts.difference ? "fail" : ""],
    ["Bad image", String(counts.badImage), counts.badImage ? "warn" : ""],
    ["Failed", String(counts.failed), counts.failed ? "fail" : ""],
    ["Active time", `${(timing.activeMs / 1000).toFixed(1)} s`, ""],
    ["Avg · ETA", timing.averageMs === null ? "- until 3 done" : `${seconds(timing.averageMs)} · ${counts.remaining === 0 ? "done" : timing.etaMs === null ? "- until 3 done" : `~${Math.ceil(timing.etaMs / 1000)} s`}`, ""],
  ];
  return (
    <div aria-label="Batch progress" aria-live="polite" className="stats-strip" role="status" tabIndex={0}>
      {cells.map(([label, value, tone]) => <div key={label}><span className="stat-label text-muted">{label}</span><span className={`stat-value ${tone}`}>{value}</span></div>)}
    </div>
  );
}
