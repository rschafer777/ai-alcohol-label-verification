import { useCallback, useEffect, useMemo, useRef, useState, type DragEvent, type KeyboardEvent, type PointerEvent, type ReactElement } from "react";

import { icons } from "../../components/icons";
import { evidenceColors, stateColor } from "../../components/status";
import type { CheckResult, Evidence, VerificationResult } from "../../contracts/types";
import { coverageText, displayLabel, evidenceFor, polygonPoints, provenanceLabel, qualityText } from "./check-view";
import type { ReviewImage, SlotUpload } from "./review-images";

const MIN_ZOOM = 0.5;
const MAX_ZOOM = 4;
const BUTTON_STEP = 0.25;
const WHEEL_FACTOR = 1.1;
const KEY_PAN_PX = 40;
/* How far the enlarged image may be dragged past the edge of the stage. */
const PAN_SLACK_PX = 40;

interface View {
  zoom: number;
  x: number;
  y: number;
}

export function EvidencePolygons({ result, panelIndex, selected }: { result: VerificationResult; panelIndex: number; selected: CheckResult | null }): ReactElement | null {
  const panel = result.panels[panelIndex];
  if (!panel) return null;
  const { width, height } = panel.originalDimensions;
  const selectedEvidence = evidenceFor(result, selected);
  const polygons: Array<{ key: string; points: string; stroke: string; width: number; dash: string; fill: string }> = [];
  if (selected && selectedEvidence) {
    if (selectedEvidence.panelId === panel.panelId) {
      const color = selected.applicable ? stateColor(selected.state) : evidenceColors.none;
      polygons.push({ key: selectedEvidence.evidenceId, points: polygonPoints(selectedEvidence), stroke: color === "transparent" ? evidenceColors.none : color, width: 4, dash: selected.state === "Not verified" ? "6 5" : "none", fill: `color-mix(in srgb, ${color === "transparent" ? evidenceColors.none : color} 18%, transparent)` });
    }
  } else if (!selected) {
    for (const evidence of result.evidence) {
      if (evidence.panelId !== panel.panelId) continue;
      polygons.push({ key: evidence.evidenceId, points: polygonPoints(evidence), stroke: "var(--lv-accent-400)", width: 1.5, dash: "4 4", fill: "none" });
    }
  }
  return (
    <svg aria-hidden="true" preserveAspectRatio="none" viewBox={`0 0 ${width} ${height}`}>
      {polygons.map((polygon) => <polygon key={polygon.key} points={polygon.points} style={{ fill: polygon.fill, stroke: polygon.stroke, strokeWidth: polygon.width, strokeDasharray: polygon.dash }} />)}
    </svg>
  );
}

function clampZoom(value: number): number {
  return Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, +value.toFixed(3)));
}

export function EvidenceViewer({ result, images, panelIndex, selected, upload, onSelectPanel, onClearSelection, onAddImage, addedFrom = Number.POSITIVE_INFINITY }: {
  result: VerificationResult;
  images: ReviewImage[];
  panelIndex: number;
  selected: CheckResult | null;
  upload: SlotUpload | null;
  onSelectPanel: (index: number) => void;
  onClearSelection: () => void;
  onAddImage: ((file: File, slot: number) => void) | null;
  addedFrom?: number;
}): ReactElement {
  const [view, setView] = useState<View>({ zoom: 1, x: 0, y: 0 });
  const [rotation, setRotation] = useState(0);
  const [enhanced, setEnhanced] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [dragSlot, setDragSlot] = useState<number | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const pendingSlot = useRef<number>(0);
  const caption = useRef<HTMLDivElement>(null);
  const stage = useRef<HTMLDivElement>(null);
  const inner = useRef<HTMLDivElement>(null);
  const drag = useRef<{ pointerId: number; startX: number; startY: number; panX: number; panY: number } | null>(null);
  const image = images[Math.min(panelIndex, images.length - 1)];
  const panel = result.panels[panelIndex];
  const regionsOnPanel = useMemo(() => result.evidence.filter((item) => item.panelId === panel?.panelId).length, [result, panel]);
  const selectedEvidence: Evidence | null = evidenceFor(result, selected);
  const zoomed = view.zoom > 1;

  useEffect(() => {
    if (selected) caption.current?.focus();
  }, [selected]);

  /* Keep the enlarged image within reach: it may be dragged until its edge is a little way
     past the edge of the stage, never entirely out of sight. */
  const clampPan = useCallback((value: number, axis: "x" | "y", zoom: number) => {
    const stageSize = axis === "x" ? stage.current?.clientWidth ?? 0 : stage.current?.clientHeight ?? 0;
    const innerSize = axis === "x" ? inner.current?.offsetWidth ?? 0 : inner.current?.offsetHeight ?? 0;
    const limit = Math.max(0, (innerSize * zoom - stageSize) / 2) + PAN_SLACK_PX;
    return Math.min(limit, Math.max(-limit, value));
  }, []);

  /* Zoom about a point on the stage (offset from the image centre in stage pixels) so the
     detail under the cursor stays put; without an anchor the image zooms about its centre. */
  const applyZoom = useCallback((update: (current: number) => number, anchor?: { x: number; y: number }) => {
    setView((current) => {
      const zoom = clampZoom(update(current.zoom));
      if (zoom === current.zoom) return current;
      if (zoom <= 1) return { zoom, x: 0, y: 0 };
      const ratio = zoom / current.zoom;
      const x = anchor ? current.x + anchor.x * (1 - ratio) : current.x;
      const y = anchor ? current.y + anchor.y * (1 - ratio) : current.y;
      return { zoom, x: clampPan(x, "x", zoom), y: clampPan(y, "y", zoom) };
    });
  }, [clampPan]);

  /* The wheel zooms instead of scrolling while the pointer is over the image. React registers
     wheel listeners as passive, so the listener is attached directly to keep preventDefault. */
  useEffect(() => {
    const element = stage.current;
    if (!element) return undefined;
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      const rect = inner.current?.getBoundingClientRect();
      const anchor = rect ? { x: event.clientX - (rect.left + rect.width / 2), y: event.clientY - (rect.top + rect.height / 2) } : undefined;
      applyZoom((current) => current * (event.deltaY < 0 ? WHEEL_FACTOR : 1 / WHEEL_FACTOR), anchor);
    };
    element.addEventListener("wheel", onWheel, { passive: false });
    return () => element.removeEventListener("wheel", onWheel);
  }, [applyZoom]);

  function resetView() {
    setView({ zoom: 1, x: 0, y: 0 });
  }

  function onPointerDown(event: PointerEvent<HTMLDivElement>) {
    if (event.button !== 0 || !zoomed) return;
    drag.current = { pointerId: event.pointerId, startX: event.clientX, startY: event.clientY, panX: view.x, panY: view.y };
    if (typeof event.currentTarget.setPointerCapture === "function") event.currentTarget.setPointerCapture(event.pointerId);
    setDragging(true);
    event.preventDefault();
  }

  function onPointerMove(event: PointerEvent<HTMLDivElement>) {
    const state = drag.current;
    if (!state || state.pointerId !== event.pointerId) return;
    const dx = event.clientX - state.startX;
    const dy = event.clientY - state.startY;
    setView((current) => ({ ...current, x: clampPan(state.panX + dx, "x", current.zoom), y: clampPan(state.panY + dy, "y", current.zoom) }));
  }

  function endDrag(event: PointerEvent<HTMLDivElement>) {
    if (drag.current?.pointerId !== event.pointerId) return;
    drag.current = null;
    setDragging(false);
  }

  function onStageKey(event: KeyboardEvent<HTMLDivElement>) {
    const key = event.key;
    if (key === "+" || key === "=") applyZoom((current) => current + BUTTON_STEP);
    else if (key === "-" || key === "_") applyZoom((current) => current - BUTTON_STEP);
    else if (key === "0") resetView();
    else if (zoomed && (key === "ArrowLeft" || key === "ArrowRight" || key === "ArrowUp" || key === "ArrowDown")) {
      const dx = key === "ArrowLeft" ? KEY_PAN_PX : key === "ArrowRight" ? -KEY_PAN_PX : 0;
      const dy = key === "ArrowUp" ? KEY_PAN_PX : key === "ArrowDown" ? -KEY_PAN_PX : 0;
      setView((current) => ({ ...current, x: clampPan(current.x + dx, "x", current.zoom), y: clampPan(current.y + dy, "y", current.zoom) }));
    } else return;
    event.preventDefault();
  }

  function openPicker(slot: number) {
    pendingSlot.current = slot;
    fileInput.current?.click();
  }

  function dropOn(slot: number) {
    return (event: DragEvent<HTMLButtonElement>) => {
      event.preventDefault();
      setDragSlot(null);
      const file = event.dataTransfer.files[0];
      if (file && onAddImage) onAddImage(file, slot);
    };
  }

  const captionLabel = selected ? displayLabel(selected) : "All evidence regions";
  const captionSnippet = selected
    ? (selectedEvidence ? `“${selectedEvidence.textSnippet ?? selected.observedDisplay ?? "Region read on the label"}”` : "No visual evidence for this check")
    : `${regionsOnPanel} region${regionsOnPanel === 1 ? "" : "s"} read on this image: dotted outlines`;
  const captionMeta = selected
    ? (selectedEvidence ? `Panel ${selectedEvidence.panelId.replace("panel-", "")} · original-pixel polygon · ${provenanceLabel(selected)}` : selected.reasonText)
    : "Select Show on any check to focus its region in its result color";
  const zoomLabel = `${Math.round(view.zoom * 100)}%`;

  return (
    <section aria-labelledby="viewer-h" className="viewer">
      <div className="viewer-tools">
        <h6 id="viewer-h">Label images <span className="text-muted">· {images.length} of 3</span></h6>
        <span className="spacer" />
        <button aria-label="Zoom out" className="btn btn-icon btn-secondary" disabled={view.zoom <= MIN_ZOOM} onClick={() => applyZoom((current) => current - BUTTON_STEP)} title="Zoom out (or scroll down over the image)" type="button">{icons.zoomOut()}</button>
        <button aria-label="Reset zoom to 100%" className="btn btn-ghost zoom" onClick={resetView} title="Back to 100% and centred" type="button">{zoomLabel}</button>
        <button aria-label="Zoom in" className="btn btn-icon btn-secondary" disabled={view.zoom >= MAX_ZOOM} onClick={() => applyZoom((current) => current + BUTTON_STEP)} title="Zoom in (or scroll up over the image)" type="button">{icons.zoomIn()}</button>
        <button aria-label="Rotate 90 degrees" className="btn btn-icon btn-secondary" onClick={() => setRotation((value) => (value + 90) % 360)} title="Rotate the image a quarter turn" type="button">{icons.rotate()}</button>
        <button aria-pressed={enhanced} className="btn btn-secondary" onClick={() => setEnhanced((value) => !value)} title="Boost contrast and brightness to read faint print" type="button">{icons.sun()} Enhance</button>
      </div>

      <div aria-label="Label images" className="slots" role="group">
        {[0, 1, 2].map((slot) => {
          const item = images[slot];
          if (item) {
            const added = slot >= addedFrom;
            const quality = added ? "Read · added to this record" : qualityText(result.panels[slot]);
            const grade = result.panels[slot]?.qualitySummary?.grade ?? "good";
            return (
              <button aria-pressed={panelIndex === slot} className="slot" key={slot} onClick={() => onSelectPanel(slot)} type="button">
                <img alt={item.alt} src={item.src} />
                <span><span className="slot-title">{item.title}</span><span className="slot-name text-muted">{item.name}</span><span className={`slot-quality ${added ? "" : grade}`}>{quality}</span></span>
              </button>
            );
          }
          if (upload && upload.slot === slot) {
            return (
              <div aria-live="polite" className="slot-uploading" key={slot} role="status">
                <span className="row"><strong>{upload.stage}</strong><span className="pct text-muted">{upload.pct}%</span></span>
                <span className="bar"><span style={{ width: `${upload.pct}%` }} /></span>
                <span className="name text-muted">{upload.name}</span>
              </div>
            );
          }
          return (
            <button aria-label={`Add image ${slot + 1}: click to choose a file or drop a photo here`} className={`slot-empty${dragSlot === slot ? " dragging" : ""}`} disabled={!onAddImage} key={slot} onClick={() => openPicker(slot)} onDragLeave={() => setDragSlot(null)} onDragOver={(event) => { if (onAddImage) { event.preventDefault(); setDragSlot(slot); } }} onDrop={dropOn(slot)} type="button">
              <span>{icons.upload(20)}</span>
              <span className="slot-cta">Click here to add or drop photo here</span>
              <span className="slot-sub text-muted">Image {slot + 1} of 3 · read and added to this record</span>
            </button>
          );
        })}
        <input accept="image/jpeg,image/png,image/webp" aria-hidden="true" className="sr-only" onChange={(event) => { const file = event.target.files?.[0]; if (file && onAddImage) onAddImage(file, pendingSlot.current); event.target.value = ""; }} ref={fileInput} tabIndex={-1} type="file" />
      </div>

      <div className="viewer-meta text-muted">
        <span>Viewing <strong>{image?.name ?? "image"}</strong></span>
        <span>Image quality: <strong>{qualityText(panel)}</strong></span>
        <span>Coverage: {coverageText(result)}</span>
        <span className="legend"><span><i className="pass" />Passes</span><span><i className="warn" />Questionable</span><span><i className="fail" />Rejected</span></span>
        <span className="viewer-hint" title="With the image focused, + and - zoom, 0 resets, and the arrow keys pan">Wheel zooms · {zoomed ? "drag moves the image" : "drag moves it once enlarged"}</span>
      </div>

      <div
        aria-label="Label image with evidence regions"
        className={`stage${zoomed ? " zoomed" : ""}${dragging ? " dragging" : ""}`}
        onKeyDown={onStageKey}
        onPointerCancel={endDrag}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        ref={stage}
        tabIndex={0}
      >
        <div className="stage-inner" ref={inner} style={{ transform: `translate(${view.x}px, ${view.y}px) scale(${view.zoom}) rotate(${rotation}deg)`, transition: dragging ? "none" : undefined, filter: enhanced ? "contrast(1.25) brightness(1.08) saturate(0.8)" : "none" }}>
          {image ? <img alt={image.alt} draggable={false} src={image.src} /> : null}
          <EvidencePolygons panelIndex={panelIndex} result={result} selected={selected} />
        </div>
      </div>

      <div aria-live="polite" className="evidence-caption" ref={caption} tabIndex={-1}>
        <span>{icons.target(14)}</span>
        <div className="caption-text"><strong>{captionLabel}</strong><span>{captionSnippet}</span><span className="text-muted">{captionMeta}</span></div>
        {selected ? <button className="btn btn-ghost" onClick={onClearSelection} type="button">Show all regions</button> : null}
      </div>
    </section>
  );
}
