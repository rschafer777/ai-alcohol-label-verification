import { useEffect, useMemo, useState, type RefObject } from "react";

import type { CheckResult, Evidence, VerificationResult } from "../../api/generated-contract";

interface ResultWorkspaceProps {
  result: VerificationResult;
  sourcePanels: File[];
  selectedEvidenceId: string | null;
  note: string;
  disposition: string;
  summaryRef: RefObject<HTMLHeadingElement | null>;
  onSelectEvidence: (evidenceId: string) => void;
  onNoteChange: (note: string) => void;
  onDispositionChange: (disposition: string) => void;
  onStartOver: () => void;
}

function useObjectUrl(file?: File): string {
  const url = useMemo(
    () => file && typeof URL.createObjectURL === "function" ? URL.createObjectURL(file) : "",
    [file],
  );
  useEffect(() => {
    return () => {
      if (url && typeof URL.revokeObjectURL === "function") URL.revokeObjectURL(url);
    };
  }, [url]);
  return url;
}

function stateClass(state: CheckResult["state"]): string {
  if (state === "Match") return "state-match";
  if (state === "Mismatch") return "state-difference";
  if (state === "Review") return "state-review";
  return "state-unverified";
}

function stateLabel(state: CheckResult["state"]): string {
  return state === "Mismatch" ? "Difference" : state;
}

function fallbackComparisonValue(check: CheckResult, side: "reference" | "observed"): string {
  if (!check.applicable) return "Not applicable";
  if (side === "reference") return "Rule-based requirement";
  if (check.state === "Match") return "Condition satisfied";
  if (check.state === "Mismatch") return "Condition not satisfied";
  if (check.state === "Review") return "Review required";
  return "Not verified";
}

function summaryClass(summary: VerificationResult["summary"]): string {
  if (summary === "No differences found in checked fields") return "summary-clear";
  if (summary === "Differences detected") return "summary-difference";
  return "summary-review";
}

function CheckRow({
  check,
  evidenceById,
  selectedEvidenceId,
  onSelectEvidence,
}: {
  check: CheckResult;
  evidenceById: Map<string, Evidence>;
  selectedEvidenceId: string | null;
  onSelectEvidence: (evidenceId: string) => void;
}) {
  const evidence = check.evidenceRef ? evidenceById.get(check.evidenceRef) : undefined;
  return (
    <article className={`check-row ${stateClass(check.state)}`} aria-labelledby={`check-${check.checkId}`}>
      <div className="check-title">
        <span className="state-symbol" aria-hidden="true">
          {check.state === "Match" ? "OK" : check.state === "Mismatch" ? "!" : "?"}
        </span>
        <div>
          <h3 id={`check-${check.checkId}`}>{check.label}</h3>
          <span className="state-label">{check.applicable ? stateLabel(check.state) : "Not applicable"}</span>
        </div>
      </div>
      <dl className="comparison-values">
        <div><dt>Application</dt><dd>{check.referenceDisplay ?? fallbackComparisonValue(check, "reference")}</dd></div>
        <div><dt>Label</dt><dd>{check.observedDisplay ?? fallbackComparisonValue(check, "observed")}</dd></div>
      </dl>
      <p className="reason-text">{check.reasonText}</p>
      <p className="capability-text">Check capability: {check.capability.replaceAll("_", " ")}</p>
      <div className="evidence-actions">
        {evidence ? (
          <button
            aria-pressed={selectedEvidenceId === evidence.evidenceId}
            className="evidence-button"
            onClick={() => onSelectEvidence(evidence.evidenceId)}
            type="button"
          >
            Show on label
          </button>
        ) : (
          <span className="no-evidence">No visual evidence is available for this check.</span>
        )}
        {check.alternatives.map((alternative) => (
          <button
            aria-pressed={selectedEvidenceId === alternative.evidenceRef}
            className="evidence-button alternative-button"
            key={`${alternative.value}-${alternative.evidenceRef}`}
            onClick={() => onSelectEvidence(alternative.evidenceRef)}
            type="button"
          >
            Show {alternative.value}
          </button>
        ))}
      </div>
    </article>
  );
}

export function ResultWorkspace({
  result,
  sourcePanels,
  selectedEvidenceId,
  note,
  disposition,
  summaryRef,
  onSelectEvidence,
  onNoteChange,
  onDispositionChange,
  onStartOver,
}: ResultWorkspaceProps) {
  const [viewMode, setViewMode] = useState<"original" | "enhanced">("original");
  const [zoom, setZoom] = useState(1);
  const [rotation, setRotation] = useState(0);
  const selectedEvidence = result.evidence.find((item) => item.evidenceId === selectedEvidenceId) ?? null;
  const selectedPanelId = selectedEvidence?.panelId ?? result.panels[0]?.panelId ?? "panel-1";
  const selectedPanelIndex = Math.max(0, Number(selectedPanelId.replace("panel-", "")) - 1);
  const selectedFile = sourcePanels[selectedPanelIndex];
  const imageUrl = useObjectUrl(selectedFile);
  const panelResult = result.panels.find((panel) => panel.panelId === selectedPanelId);
  const evidenceById = useMemo(() => new Map(result.evidence.map((item) => [item.evidenceId, item])), [result.evidence]);
  const viewerTransformClass = `zoom-${Math.round(zoom * 100)} rotate-${rotation}`;
  const polygon = selectedEvidence?.polygonOriginalPixels.map((point) => `${point.x},${point.y}`).join(" ");

  function resetViewer() {
    setViewMode("original");
    setZoom(1);
    setRotation(0);
  }

  return (
    <div className="result-page">
      <section className={`summary-card ${summaryClass(result.summary)}`} aria-live="polite">
        <div>
          <p className="eyebrow">Verification complete</p>
          <h1 ref={summaryRef} tabIndex={-1}>{result.summary}</h1>
          <p>Review the system findings and source evidence. You make the final decision.</p>
        </div>
        <div className="summary-meta">
          <span>Server work: {(result.serverDurationMs / 1000).toFixed(1)}s</span>
          <span>Request: {result.requestId}</span>
        </div>
      </section>

      <div className="workspace-grid">
        <section className="card viewer-card" aria-labelledby="viewer-heading">
          <div className="section-heading compact-heading">
            <div><p className="step-label">Source evidence</p><h2 id="viewer-heading">Label view</h2></div>
            <span className="panel-count">{selectedPanelId}</span>
          </div>
          <div className="viewer-toolbar" aria-label="Label view controls">
            <div className="segmented-control" aria-label="Image view">
              <button aria-pressed={viewMode === "original"} onClick={() => setViewMode("original")} type="button">Original</button>
              <button aria-pressed={viewMode === "enhanced"} onClick={() => setViewMode("enhanced")} type="button">Enhanced display</button>
            </div>
            <button aria-label="Zoom out" disabled={zoom <= 0.75} onClick={() => setZoom((value) => Math.max(0.75, value - 0.25))} type="button">Zoom out</button>
            <button aria-label="Zoom in" disabled={zoom >= 2} onClick={() => setZoom((value) => Math.min(2, value + 0.25))} type="button">Zoom in</button>
            <button onClick={() => setRotation((value) => (value + 90) % 360)} type="button">Rotate</button>
            <button onClick={resetViewer} type="button">Fit and reset</button>
          </div>
          <p className="view-explanation">
            {viewMode === "original" ? "Original uploaded image" : "Display-only contrast enhancement. Findings do not change."}
          </p>
          <div className="image-stage">
            {imageUrl && panelResult ? (
              <div className={`image-transform ${viewMode === "enhanced" ? "enhanced" : ""} ${viewerTransformClass}`}>
                <img alt={`Original label ${selectedPanelId}`} src={imageUrl} />
                {polygon ? (
                  <svg aria-hidden="true" className="evidence-overlay" preserveAspectRatio="none" viewBox={`0 0 ${panelResult.originalDimensions.width} ${panelResult.originalDimensions.height}`}>
                    <polygon points={polygon} />
                  </svg>
                ) : null}
              </div>
            ) : (
              <div className="viewer-empty">Original panel preview is unavailable. The result remains unchanged.</div>
            )}
          </div>
          {selectedEvidence ? (
            <div className="selected-evidence" aria-live="polite">
              <strong>Focused evidence</strong>
              <span>{selectedEvidence.textSnippet || "Visual presentation evidence"}</span>
              <span>Source: {selectedEvidence.sourceView}; confidence is an extraction signal, not an approval score.</span>
            </div>
          ) : <p className="selected-evidence">Choose Show on label to focus a source region.</p>}
        </section>

        <section className="card checks-card" aria-labelledby="checks-heading">
          <div className="section-heading compact-heading">
            <div><p className="step-label">Application compared with label</p><h2 id="checks-heading">Checked details</h2></div>
            <span className="panel-count">{result.checks.filter((check) => check.applicable).length} applicable</span>
          </div>
          <div className="check-list">
            {result.checks.map((check) => (
              <CheckRow
                check={check}
                evidenceById={evidenceById}
                key={check.checkId}
                onSelectEvidence={onSelectEvidence}
                selectedEvidenceId={selectedEvidenceId}
              />
            ))}
          </div>
        </section>
      </div>

      <section className="card limitations-card" aria-labelledby="limitations-heading">
        <h2 id="limitations-heading">Limits and reviewer notes</h2>
        {result.limitations.length ? <ul>{result.limitations.map((item) => <li key={item}>{item}</li>)}</ul> : <p>No additional result limitations were reported.</p>}
        <div className="review-fields">
          <div className="field">
            <label htmlFor="reviewer-disposition">Session disposition (optional)</label>
            <select id="reviewer-disposition" onChange={(event) => onDispositionChange(event.target.value)} value={disposition}>
              <option value="">No disposition selected</option>
              <option value="reviewed">Reviewed</option>
              <option value="follow-up">Follow-up needed</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="reviewer-note">Reviewer note (optional)</label>
            <textarea id="reviewer-note" maxLength={1000} onChange={(event) => onNoteChange(event.target.value)} rows={3} value={note} />
          </div>
        </div>
        <p className="session-note">Notes and disposition stay only in this browser tab and never change the system findings.</p>
        <button className="button secondary" onClick={onStartOver} type="button">Start over</button>
      </section>
    </div>
  );
}
