import { useState, type DragEvent, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { GroupStatusTag } from "../../components/StatusTag";
import { beverageTypeLabel } from "../verification/check-view";
import type { BatchGroup, BatchImage } from "./batch-state";

export const DRAG_TYPE = "application/x-labelverify-image";

export function GroupCard({ group, ordinal, images, selected, selectedImageId, otherGroups, onToggleSelect, onSelectImage, onDropImage, onSplit, onMove, onConfirm, onRename }: {
  group: BatchGroup;
  ordinal: number;
  images: Map<string, BatchImage>;
  selected: boolean;
  selectedImageId: string | null;
  otherGroups: BatchGroup[];
  onToggleSelect: () => void;
  onSelectImage: (imageId: string) => void;
  onDropImage: (imageId: string, targetGroupId: string) => void;
  onSplit: () => void;
  onMove: (targetGroupId: string | null) => void;
  onConfirm: () => void;
  onRename: (name: string) => void;
}): ReactElement {
  const [dropping, setDropping] = useState(false);
  const [menu, setMenu] = useState(false);
  const status = group.status === "ready" ? "ready" : group.status === "conflict" ? "conflict" : "confirm";
  const cta = group.confirmed ? "Confirmed" : group.status === "conflict" ? "Confirm anyway" : group.imageIds.length === 1 && group.reasons.some((reason) => /separate|not read/i.test(reason)) ? "Confirm as separate" : group.confidence === "low" ? "Confirm type" : "Confirm";
  const typeText = `${beverageTypeLabel(group.inferredType, true)} · ${group.confidence}`;
  const note = group.reasons.slice(1).join(" ") || (group.confirmed ? "Confirmed. Any edit will need confirmation again." : "Confirm this product before the run unlocks.");

  function onDrop(event: DragEvent<HTMLElement>) {
    event.preventDefault();
    setDropping(false);
    const imageId = event.dataTransfer.getData(DRAG_TYPE);
    if (imageId) onDropImage(imageId, group.id);
  }

  return (
    <article aria-labelledby={`g-${group.id}`} className={`card blueprint group-card ${status}${selected ? " selected" : ""}${dropping ? " dropping" : ""}`} onDragLeave={() => setDropping(false)} onDragOver={(event) => { if (event.dataTransfer.types.includes(DRAG_TYPE) && group.imageIds.length < 3) { event.preventDefault(); setDropping(true); } }} onDrop={onDrop}>
      <Corners />
      <div className="group-head">
        <label className="card-kicker" style={{ display: "flex", gap: 6, alignItems: "center", cursor: "pointer" }}><input aria-label={`Select product ${ordinal}`} checked={selected} onChange={onToggleSelect} type="checkbox" />Product {ordinal}</label>
        <GroupStatusTag status={status} />
      </div>
      <div className="thumbs">
        {group.imageIds.map((imageId) => {
          const image = images.get(imageId);
          if (!image) return null;
          return (
            <figure aria-label={`${image.file.name}: drag to another product or select and use Move`} className={`group-thumb${selectedImageId === imageId ? " selected" : ""}`} draggable key={imageId} onClick={() => onSelectImage(imageId)} onDragStart={(event) => { event.dataTransfer.setData(DRAG_TYPE, imageId); event.dataTransfer.effectAllowed = "move"; }} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onSelectImage(imageId); } }} tabIndex={0}>
              <img alt="" src={image.url} />
              <figcaption>{image.file.name.replace(/\.[^.]+$/, "")}</figcaption>
            </figure>
          );
        })}
        {group.imageIds.length < 3 ? <div aria-hidden="true" className="group-drop">drop another panel</div> : null}
      </div>
      <div className="group-name">
        <input aria-label={`Product ${ordinal} name`} className="name-input" id={`g-${group.id}`} maxLength={80} onChange={(event) => onRename(event.target.value)} value={group.name} />
        <span className="group-type"><span className="tag tag-neutral">{typeText}</span><span className="text-muted">{group.reasons[0] ?? ""}</span></span>
      </div>
      <p className="card-body">{note}</p>
      <div className="card-meta" style={{ position: "relative" }}>
        <span>{group.imageIds.length} of 3 images</span>
        <span>
          <button className="btn btn-ghost" disabled={group.imageIds.length < 2} onClick={onSplit} title="Make each image of this product its own product" type="button">Split</button>
          <button aria-expanded={menu} aria-haspopup="menu" className="btn btn-ghost" disabled={!selectedImageId || !group.imageIds.includes(selectedImageId)} onClick={() => setMenu((value) => !value)} type="button">Move…</button>
          <button className="btn btn-secondary" disabled={group.confirmed || !group.name.trim() || group.imageIds.length > 3} onClick={onConfirm} type="button">{cta}</button>
        </span>
        {menu ? (
          <div className="move-menu" role="menu" style={{ right: 0, top: "100%" }}>
            {otherGroups.filter((other) => other.imageIds.length < 3).map((other) => <button key={other.id} onClick={() => { setMenu(false); onMove(other.id); }} role="menuitem" type="button">{other.name}</button>)}
            <button onClick={() => { setMenu(false); onMove(null); }} role="menuitem" type="button">New product</button>
          </div>
        ) : null}
      </div>
    </article>
  );
}
