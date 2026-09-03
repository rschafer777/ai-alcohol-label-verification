import { useState, type ReactElement } from "react";

import { summaryColor } from "../../components/status";
import { SummaryTag } from "../../components/StatusTag";
import type { BatchGroup, BatchImage } from "./batch-state";
import { isException, summaryOf } from "./batch-state";

export function BatchRail({ groups, images, currentId, onOpen }: { groups: BatchGroup[]; images: Map<string, BatchImage>; currentId: string | null; onOpen: (id: string) => void }): ReactElement {
  const [filter, setFilter] = useState<"attention" | "all">("attention");
  const attention = groups.filter((group) => isException(group));
  const shown = filter === "attention" ? attention : groups;
  return (
    <aside aria-label="Batch products" className="batch-rail">
      <div className="batch-rail-filters">
        <button aria-pressed={filter === "attention"} className={`btn ${filter === "attention" ? "btn-secondary" : "btn-ghost"}`} onClick={() => setFilter("attention")} type="button">Needs attention · {attention.length}</button>
        <button aria-pressed={filter === "all"} className={`btn ${filter === "all" ? "btn-secondary" : "btn-ghost"}`} onClick={() => setFilter("all")} type="button">All · {groups.length}</button>
      </div>
      <ol aria-label="Products" tabIndex={0}>
        {shown.map((group) => {
          const summary = summaryOf(group);
          const thumb = images.get(group.imageIds[0] ?? "");
          return (
            <li key={group.id}>
              <button aria-current={currentId === group.id ? "true" : undefined} className="rail-row" disabled={!group.result} onClick={() => onOpen(group.id)} style={{ borderLeftColor: summaryColor(summary) }} type="button">
                {thumb ? <img alt="" src={thumb.url} /> : <span />}
                <span><span className="rail-name">{group.name}</span><span className="rail-meta">{summary ? <SummaryTag summary={summary} /> : null}<span className="text-muted">{group.imageIds.length} img · {group.durationMs == null ? "-" : `${(group.durationMs / 1000).toFixed(1)} s`}</span></span></span>
              </button>
            </li>
          );
        })}
      </ol>
    </aside>
  );
}
