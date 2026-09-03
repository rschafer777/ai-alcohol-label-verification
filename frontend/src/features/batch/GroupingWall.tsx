import { useState, type DragEvent, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import type { BatchGroup, BatchImage } from "./batch-state";
import { DRAG_TYPE, GroupCard } from "./GroupCard";

export function GroupingWall({ groups, images, analyzed, failed, analysisMs, canUndo, onUndo, onMerge, onSplit, onMove, onDropImage, onConfirm, onConfirmAll, onRename, onRun }: {
  groups: BatchGroup[];
  images: Map<string, BatchImage>;
  analyzed: number;
  failed: number;
  analysisMs: number;
  canUndo: boolean;
  onUndo: () => void;
  onMerge: (ids: string[]) => void;
  onSplit: (id: string) => void;
  onMove: (imageId: string, targetId: string | null) => void;
  onDropImage: (imageId: string, targetId: string | null) => void;
  onConfirm: (id: string) => void;
  onConfirmAll: () => void;
  onRename: (id: string, name: string) => void;
  onRun: () => void;
}): ReactElement {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [droppingNew, setDroppingNew] = useState(false);
  const pending = groups.filter((group) => !group.confirmed).length;
  const ready = groups.filter((group) => group.status === "ready" && !group.confirmed).length;
  const total = analyzed + failed;
  const avg = analyzed ? analysisMs / analyzed / 1000 : 0;
  const selectedGroups = groups.filter((group) => selected.has(group.id));
  const canMerge = selectedGroups.length >= 2 && selectedGroups.reduce((sum, group) => sum + group.imageIds.length, 0) <= 3;
  const canSplit = selectedGroups.some((group) => group.imageIds.length > 1);
  const overCap = groups.length > 300;

  function toggle(id: string) {
    setSelected((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id); else next.add(id);
      return next;
    });
  }

  function dropNew(event: DragEvent<HTMLButtonElement>) {
    event.preventDefault();
    setDroppingNew(false);
    const imageId = event.dataTransfer.getData(DRAG_TYPE);
    if (imageId) onDropImage(imageId, null);
  }

  return (
    <main className="grouping" data-screen-label="Batch grouping">
      <header className="grouping-header">
        <div><h6 className="kicker">Check a batch · step 2 of 3</h6><h2>Confirm how the images group into products</h2></div>
        <div className="grouping-stats">
          <span><span className="text-muted">Images</span><strong>{analyzed} analyzed · {failed} failed</strong></span>
          <span><span className="text-muted">Suggested products</span><strong>{groups.length}</strong></span>
          <span><span className="text-muted">Need your confirmation</span><strong className="attention">{pending}</strong></span>
          <span><span className="text-muted">Analysis time</span><strong>{(analysisMs / 1000).toFixed(1)} s · {avg.toFixed(1)} s avg</strong></span>
        </div>
      </header>
      <div aria-label="Grouping actions" className="grouping-toolbar" role="toolbar">
        <span className="hint text-muted">Drag a thumbnail between cards, or select and use:</span>
        <button className="btn btn-secondary" disabled={!canMerge} onClick={() => { onMerge([...selected]); setSelected(new Set()); }} type="button">Merge selected</button>
        <button className="btn btn-secondary" disabled={!canSplit} onClick={() => { selectedGroups.forEach((group) => onSplit(group.id)); setSelected(new Set()); }} type="button">Split into separate products</button>
        <button className="btn btn-secondary" disabled={!selectedImage} onClick={() => { if (selectedImage) { onMove(selectedImage, null); setSelectedImage(null); } }} type="button">Move to…</button>
        <button className="btn btn-ghost" disabled={!canUndo} onClick={onUndo} type="button">{icons.undo()} Undo</button>
        <span className="spacer" />
        <button className="btn btn-secondary btn-hit" disabled={!ready} onClick={onConfirmAll} type="button">Confirm all ready ({ready})</button>
        <span title={pending ? `${pending} group${pending === 1 ? "" : "s"} still need confirmation` : overCap ? "Merge related images until there are no more than 300 products" : undefined}>
          <button className="btn btn-primary blueprint btn-hit" disabled={pending > 0 || overCap || !groups.length} onClick={onRun} type="button"><Corners />Run {groups.length} product{groups.length === 1 ? "" : "s"} {icons.arrow()}</button>
        </span>
      </div>
      <p className="grouping-helper text-muted">Run unlocks when every group is confirmed. Groups can hold 1-3 images. Any edit returns a group to "needs confirmation" until you confirm it again.{total ? "" : " No images could be analyzed."}</p>
      {overCap ? <p className="form-error" role="alert">This batch has {groups.length} product groups. Merge related images until there are no more than 300 products.</p> : null}
      <div className="group-wall">
        {groups.map((group, index) => (
          <GroupCard group={group} images={images} key={group.id} onConfirm={() => onConfirm(group.id)} onDropImage={(imageId, target) => onDropImage(imageId, target)} onMove={(target) => { if (selectedImage) { onMove(selectedImage, target); setSelectedImage(null); } }} onRename={(name) => onRename(group.id, name)} onSelectImage={(imageId) => setSelectedImage((current) => current === imageId ? null : imageId)} onSplit={() => onSplit(group.id)} onToggleSelect={() => toggle(group.id)} ordinal={index + 1} otherGroups={groups.filter((other) => other.id !== group.id)} selected={selected.has(group.id)} selectedImageId={selectedImage} />
        ))}
        <button className={`card group-new-drop${droppingNew ? " dropping" : ""}`} disabled={!selectedImage && !droppingNew} onClick={() => { if (selectedImage) { onMove(selectedImage, null); setSelectedImage(null); } }} onDragLeave={() => setDroppingNew(false)} onDragOver={(event) => { if (event.dataTransfer.types.includes(DRAG_TYPE)) { event.preventDefault(); setDroppingNew(true); } }} onDrop={dropNew} type="button">
          <span>{icons.arrow()}</span>
          <strong>Drop a thumbnail here to start a new product</strong>
          <span className="text-muted">or select a thumbnail and press this button</span>
        </button>
      </div>
    </main>
  );
}
