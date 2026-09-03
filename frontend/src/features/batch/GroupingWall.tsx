import { useState, type DragEvent, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import type { BatchGroup, BatchImage } from "./batch-state";
import { DRAG_TYPE, GroupCard } from "./GroupCard";

export function GroupingWall({ groups, images, analyzed, failed, analysisMs, canUndo, onUndo, onMerge, onSplit, onMove, onDropImage, onConfirm, onConfirmAll, onConfirmPending, onRename, onRun }: {
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
  onConfirmPending: () => void;
  onRename: (id: string, name: string) => void;
  onRun: () => void;
}): ReactElement {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [droppingNew, setDroppingNew] = useState(false);
  const [pendingOnly, setPendingOnly] = useState(false);
  const pending = groups.filter((group) => !group.confirmed).length;
  const confirmedCount = groups.length - pending;
  const ready = groups.filter((group) => group.status === "ready" && !group.confirmed).length;
  const conflicts = groups.filter((group) => !group.confirmed && group.status === "conflict").length;
  const confirmable = groups.filter((group) => !group.confirmed && group.status !== "conflict" && group.imageIds.length <= 3).length;
  const total = analyzed + failed;
  const avg = analyzed ? analysisMs / analyzed / 1000 : 0;
  const selectedGroups = groups.filter((group) => selected.has(group.id));
  const canMerge = selectedGroups.length >= 2 && selectedGroups.reduce((sum, group) => sum + group.imageIds.length, 0) <= 3;
  const canSplit = selectedGroups.some((group) => group.imageIds.length > 1);
  const overCap = groups.length > 300;
  // The filter only makes sense while something is left to confirm; it clears itself after.
  const filtering = pendingOnly && pending > 0;
  const visible = filtering ? groups.filter((group) => !group.confirmed) : groups;
  const products = (count: number) => `${count} product${count === 1 ? "" : "s"}`;
  const runReason = !groups.length
    ? "There are no products to run."
    : overCap
      ? "Merge related images until there are no more than 300 products."
      : pending > 0
        ? `Confirm ${pending} more product${pending === 1 ? "" : "s"} to unlock the run.`
        : "";

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
          <span><span className="text-muted">Confirmed</span><strong>{confirmedCount} of {groups.length}</strong></span>
          <span><span className="text-muted">Need your confirmation</span><strong className={pending ? "attention" : ""}>{pending}</strong></span>
          <span><span className="text-muted">Analysis time</span><strong>{(analysisMs / 1000).toFixed(1)} s · {avg.toFixed(1)} s avg</strong></span>
        </div>
      </header>

      <section aria-label="Next step" aria-live="polite" className={`grouping-next${pending || !groups.length ? "" : " done"}`}>
        <p className="grouping-next-text">
          {pending ? (
            <>
              <strong>{confirmedCount} of {products(groups.length)} confirmed.</strong>{" "}
              {pending === 1 ? "One product still needs" : `${pending} products still need`} your confirmation: check the images on each card marked
              {" "}<em>Needs confirmation</em>, then press its Confirm button. If the suggested grouping looks right for all of them, confirm them in one step.
              {conflicts ? (
                <>
                  {" "}{conflicts === 1 ? "One card shows a" : `${conflicts} cards show a`} <em>Conflict</em>: its images may belong to different products, so open it and choose Split or Confirm anyway; conflicts are never confirmed in bulk.
                </>
              ) : null}
              {" "}The run unlocks once every product is confirmed.
            </>
          ) : groups.length ? (
            <>
              <strong>All {products(groups.length)} are confirmed.</strong>{" "}
              Run the batch to read each product against its checks. The results screen then lists every product and walks you through the ones that need a human, one at a time.
            </>
          ) : (
            <strong>No products to confirm.</strong>
          )}
        </p>
        <div className="grouping-next-actions">
          {pending ? (
            <>
              <button aria-pressed={filtering} className="btn btn-secondary btn-hit" onClick={() => setPendingOnly((value) => !value)} title="Hide the confirmed products so only the cards that still need a decision are shown" type="button">
                {filtering ? `Show all ${products(groups.length)}` : `Show the ${pending} that still need confirmation`}
              </button>
              {confirmable ? (
                <button className="btn btn-secondary btn-hit" onClick={onConfirmPending} title="Accept the suggested grouping of every product marked Needs confirmation; conflicts and over-full products are left for you" type="button">
                  Confirm the remaining {confirmable} as suggested
                </button>
              ) : null}
            </>
          ) : null}
          <button aria-describedby={runReason ? "grouping-run-reason" : undefined} className="btn btn-primary blueprint btn-hit" disabled={!!runReason} onClick={onRun} title={runReason || `Read each of the ${products(groups.length)} and open the results`} type="button">
            <Corners />Run {products(groups.length)} {icons.arrow()}
          </button>
          {runReason ? <span className="grouping-run-reason" id="grouping-run-reason">{runReason}</span> : null}
        </div>
      </section>

      <div aria-label="Grouping actions" className="grouping-toolbar" role="toolbar">
        <span className="hint text-muted">Fix a grouping: tick the cards involved, then</span>
        <button className="btn btn-secondary" disabled={!canMerge} onClick={() => { onMerge([...selected]); setSelected(new Set()); }} title="Tick two or three cards that show the same product, then merge them into one product of up to three images" type="button">Merge selected</button>
        <button className="btn btn-secondary" disabled={!canSplit} onClick={() => { selectedGroups.forEach((group) => onSplit(group.id)); setSelected(new Set()); }} title="Tick a card that holds several images to make each image its own product" type="button">Split into separate products</button>
        <button className="btn btn-secondary" disabled={!selectedImage} onClick={() => { if (selectedImage) { onMove(selectedImage, null); setSelectedImage(null); } }} title="Click a thumbnail to select it, then move it into a new product; use the Move button on its card to pick another product" type="button">Move to…</button>
        <button className="btn btn-ghost" disabled={!canUndo} onClick={onUndo} title="Undo the last grouping edit" type="button">{icons.undo()} Undo</button>
        <span className="spacer" />
        <button className="btn btn-secondary btn-hit" disabled={!ready} onClick={onConfirmAll} title={ready ? "Confirm every product the machine grouped confidently (the cards marked Ready)" : "Every product marked Ready is already confirmed"} type="button">Confirm all ready ({ready})</button>
      </div>
      <p className="grouping-helper text-muted">You can also drag a thumbnail between cards. A product holds 1 to 3 images. Any edit returns that product to <em>Needs confirmation</em> until you confirm it again.{total ? "" : " No images could be analyzed."}</p>
      {overCap ? <p className="form-error" role="alert">This batch has {groups.length} product groups. Merge related images until there are no more than 300 products.</p> : null}

      <div className="group-wall">
        {visible.map((group) => (
          <GroupCard group={group} images={images} key={group.id} onConfirm={() => onConfirm(group.id)} onDropImage={(imageId, target) => onDropImage(imageId, target)} onMove={(target) => { if (selectedImage) { onMove(selectedImage, target); setSelectedImage(null); } }} onRename={(name) => onRename(group.id, name)} onSelectImage={(imageId) => setSelectedImage((current) => current === imageId ? null : imageId)} onSplit={() => onSplit(group.id)} onToggleSelect={() => toggle(group.id)} ordinal={groups.indexOf(group) + 1} otherGroups={groups.filter((other) => other.id !== group.id)} selected={selected.has(group.id)} selectedImageId={selectedImage} />
        ))}
        {filtering ? null : (
          <button className={`card group-new-drop${droppingNew ? " dropping" : ""}`} disabled={!selectedImage && !droppingNew} onClick={() => { if (selectedImage) { onMove(selectedImage, null); setSelectedImage(null); } }} onDragLeave={() => setDroppingNew(false)} onDragOver={(event) => { if (event.dataTransfer.types.includes(DRAG_TYPE)) { event.preventDefault(); setDroppingNew(true); } }} onDrop={dropNew} type="button">
            <span>{icons.arrow()}</span>
            <strong>Drop a thumbnail here to start a new product</strong>
            <span className="text-muted">or select a thumbnail and press this button</span>
          </button>
        )}
      </div>
    </main>
  );
}
