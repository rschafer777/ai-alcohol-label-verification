import { useEffect, useMemo, useRef, useState, type DragEvent, type ReactElement } from "react";

import { icons } from "../../components/icons";
import { evidenceColors, stateColor } from "../../components/status";
import type { CheckResult, Evidence, VerificationResult } from "../../contracts/types";
import { coverageText, displayLabel, evidenceFor, polygonPoints, provenanceLabel, qualityText } from "./check-view";
import type { ReviewImage, SlotUpload } from "./review-images";

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
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [enhanced, setEnhanced] = useState(false);
  const [dragSlot, setDragSlot] = useState<number | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const pendingSlot = useRef<number>(0);
  const caption = useRef<HTMLDivElement>(null);
  const image = images[Math.min(panelIndex, images.length - 1)];
  const panel = result.panels[panelIndex];
  const regionsOnPanel = useMemo(() => result.evidence.filter((item) => item.panelId === panel?.panelId).length, [result, panel]);
  const selectedEvidence: Evidence | null = evidenceFor(result, selected);

  useEffect(() => {
    if (selected) caption.current?.focus();
  }, [selected]);

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

  return (
    <section aria-labelledby="viewer-h" className="viewer">
      <div className="viewer-tools">
        <h6 id="viewer-h">Label images <span className="text-muted">· {images.length} of 3</span></h6>
        <span className="spacer" />
        <button aria-label="Zoom out" className="btn btn-icon btn-secondary" onClick={() => setZoom((value) => Math.max(0.5, +(value - 0.25).toFixed(2)))} type="button">{icons.zoomOut()}</button>
        <span className="zoom">{Math.round(zoom * 100)}%</span>
        <button aria-label="Zoom in" className="btn btn-icon btn-secondary" onClick={() => setZoom((value) => Math.min(2.5, +(value + 0.25).toFixed(2)))} type="button">{icons.zoomIn()}</button>
        <button aria-label="Rotate 90 degrees" className="btn btn-icon btn-secondary" onClick={() => setRotation((value) => (value + 90) % 360)} type="button">{icons.rotate()}</button>
        <button aria-pressed={enhanced} className="btn btn-secondary" onClick={() => setEnhanced((value) => !value)} type="button">{icons.sun()} Enhance</button>
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
            <button aria-label={`Add image ${slot + 1}: click to choose a file or drop a photo here`} className={`slot-empty${dragSlot === slot ? " dragging" : ""}`} disabled={!onAddImage} key={slot} onClick={() => openPicker(slot)} onDragLeave={() => setDragSlot(null)} onDragOver={(event) => { event.preventDefault(); setDragSlot(slot); }} onDrop={dropOn(slot)} type="button">
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
      </div>

      <div aria-label="Label image with evidence regions" className="stage" tabIndex={0}>
        <div className="stage-inner" style={{ transform: `scale(${zoom}) rotate(${rotation}deg)`, filter: enhanced ? "contrast(1.25) brightness(1.08) saturate(0.8)" : "none" }}>
          {image ? <img alt={image.alt} src={image.src} /> : null}
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
