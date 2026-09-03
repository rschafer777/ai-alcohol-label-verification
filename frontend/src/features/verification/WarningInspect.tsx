import { useEffect, useMemo, useRef, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import { evidenceColors } from "../../components/status";
import { Badge, SemTag } from "../../components/StatusTag";
import type { Evidence, VerificationResult } from "../../contracts/types";
import { displayLabel, observedDisplay, panelIndexOf, polygonPoints, reasonShort, ruleExpectation, WARNING_IDS } from "./check-view";
import type { ReviewImage } from "./review-images";
import { byId, CROP_H, CROP_W, STATUTORY_BODY, STATUTORY_HEADING, warningEvidencePair } from "./warning-view";

export function WarningInspect({ result, images, onBack }: { result: VerificationResult; images: ReviewImage[]; onBack: () => void }): ReactElement {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus();
  }, []);
  const rows = result.checks.filter((check) => WARNING_IDS.has(check.checkId));
  const applicable = rows.filter((check) => check.applicable);
  const mismatch = applicable.filter((check) => check.state === "Mismatch").length;
  const review = applicable.filter((check) => check.state === "Review").length;
  const match = applicable.filter((check) => check.state === "Match").length;
  const caps = byId(rows, "warning_heading_uppercase");
  const bold = byId(rows, "warning_heading_emphasis");
  const bodyBold = byId(rows, "warning_body_not_bold");
  const contrast = byId(rows, "warning_contrast");
  const legible = byId(rows, "warning_legibility");
  const wording = byId(rows, "warning_wording");
  const headColor = caps?.state === "Match" && bold?.state === "Match" ? evidenceColors.pass : caps?.state === "Mismatch" ? evidenceColors.fail : evidenceColors.warn;
  const bodyColor = contrast?.state === "Mismatch" || bodyBold?.state === "Mismatch" || wording?.state === "Mismatch" ? evidenceColors.fail : legible?.state === "Review" || wording?.state === "Review" ? evidenceColors.warn : evidenceColors.pass;
  const worst = applicable.find((check) => check.state === "Mismatch") ?? applicable.find((check) => check.state === "Review") ?? applicable.find((check) => check.state === "Not verified") ?? rows[0];

  const groupTag = mismatch
    ? <SemTag icon={icons.x()} kind="fail">Mismatch · {mismatch} of 10</SemTag>
    : review
      ? <SemTag icon={icons.help()} kind="warn">Review · {review} of 10</SemTag>
      : <SemTag icon={icons.check()} kind="pass">Match · {match} of 10{applicable.length - match > 0 ? " (size not verifiable)" : ""}</SemTag>;

  const { heading: headEv, body: bodyEv } = warningEvidencePair(result);
  const crop = useMemo(() => {
    const evidence = headEv ?? bodyEv;
    if (!evidence) return null;
    const panelIndex = panelIndexOf(result, evidence.panelId);
    const panel = result.panels[panelIndex];
    const image = images[panelIndex];
    if (!panel || !image) return null;
    const points = [headEv, bodyEv].filter((item): item is Evidence => !!item && item.panelId === evidence.panelId).flatMap((item) => item.polygonOriginalPixels);
    const xs = points.map((point) => point.x);
    const ys = points.map((point) => point.y);
    let x = Math.min(...xs);
    let y = Math.min(...ys);
    let w = Math.max(...xs) - x;
    let h = Math.max(...ys) - y;
    const pad = Math.max(w, h) * 0.08;
    x -= pad; y -= pad; w += 2 * pad; h += 2 * pad;
    const scale = Math.min(CROP_W / w, CROP_H / h);
    return { image, panel, panelIndex, transform: `scale(${scale.toFixed(4)}) translate(${(-x).toFixed(0)}px, ${(-y).toFixed(0)}px)` };
  }, [headEv, bodyEv, result, images]);

  const tokens = wording?.wordingDiff ?? null;
  const statutoryTokens = `${STATUTORY_HEADING} ${STATUTORY_BODY}`.split(" ");
  const matched = wording?.matchedWords ?? null;
  const total = wording?.totalWords ?? statutoryTokens.length;

  return (
    <main className="warning" data-screen-label="Government warning">
      <header className="warning-header">
        <button className="btn btn-ghost" onClick={onBack} type="button">{icons.back()} All 24 checks</button>
        <h2 ref={heading} tabIndex={-1}>Government warning statement</h2>
        <span className="tag tag-neutral">27 CFR Part 16 · exact text required</span>
        <span className="group-result"><span className="text-muted">Group result</span>{groupTag}</span>
      </header>
      <div className="warning-grid">
        <section className="card blueprint warning-crop-card">
          <Corners />
          <div className="crop-head"><h6>{crop ? `${images.length > 1 ? `${crop.image.title} · panel ${crop.panelIndex + 1}` : crop.image.name}: warning region` : "Warning region"}</h6><span className="text-muted">{crop ? "Auto-cropped to the evidence polygons" : "No warning region was located"}</span></div>
          <div aria-label="Warning region crop" className="crop-stage" tabIndex={0}>
            {crop ? (
              <div className="crop-inner" style={{ transform: crop.transform }}>
                <img alt={crop.image.alt} src={crop.image.src} style={{ width: crop.panel.originalDimensions.width, height: crop.panel.originalDimensions.height }} />
                <svg aria-hidden="true" height={crop.panel.originalDimensions.height} viewBox={`0 0 ${crop.panel.originalDimensions.width} ${crop.panel.originalDimensions.height}`} width={crop.panel.originalDimensions.width}>
                  {bodyEv && bodyEv.panelId === crop.panel.panelId ? <polygon points={polygonPoints(bodyEv)} style={{ fill: "none", stroke: bodyColor, strokeWidth: 2, strokeDasharray: "6 6", vectorEffect: "non-scaling-stroke" }} /> : null}
                  {headEv && headEv.panelId === crop.panel.panelId ? <polygon points={polygonPoints(headEv)} style={{ fill: `color-mix(in srgb, ${headColor} 16%, transparent)`, stroke: headColor, strokeWidth: 3, vectorEffect: "non-scaling-stroke" }} /> : null}
                </svg>
              </div>
            ) : <p className="text-muted" style={{ padding: 16, fontSize: 13 }}>The warning statement was not located on the submitted images, so there is nothing to crop. Check the label by eye.</p>}
          </div>
          <div className="crop-legend text-muted"><span>Solid: heading</span><span>Dashed: body</span><span className="legend"><span><i className="pass" />Passes</span><span><i className="warn" />Questionable</span><span><i className="fail" />Rejected</span></span></div>
        </section>

        <section className="warning-right">
          <div className="card blueprint warning-text-card">
            <Corners />
            <h6>Required text: what the rule expects</h6>
            <p><strong>{STATUTORY_HEADING}</strong> {STATUTORY_BODY}</p>
            <div className="hr" />
            <h6>Read on label: word by word</h6>
            <p>
              {tokens
                ? tokens.map((token, index) => {
                  const different = token.status !== "match";
                  const shown = token.observed ?? (token.status === "missing" ? `[${token.expected}]` : token.expected ?? "");
                  return <span className={`diff-token ${token.status}${index < 2 ? " head" : ""}`} key={index} title={different && token.expected ? `Expected “${token.expected}”` : undefined}>{shown} </span>;
                })
                : <span className="text-muted">{wording?.observedDisplay ?? "The warning text was not read from the submitted images."}</span>}
            </p>
            <span className="summary text-muted">{matched !== null ? `${matched} of ${total} words match.${matched < total ? " Underlined words differ from the statute." : ""}` : "Word-level comparison is not available for this record."}</span>
          </div>
          <div className="table-wrap">
            <table className="table warning-table">
              <thead><tr><th>Check</th><th>Read on label</th><th>Result</th></tr></thead>
              <tbody>
                {rows.map((check) => (
                  <tr className={check.applicable ? "" : "na"} key={check.checkId}>
                    <td className="check-name">{displayLabel(check)}<br /><span className="expects text-muted">{ruleExpectation(check)}</span></td>
                    <td className="small">{observedDisplay(check, result)}</td>
                    <td><span className="result-cell"><Badge applicable={check.applicable} state={check.state} /><span className="reason text-muted">{reasonShort(check)}</span></span></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
      <footer className="warning-footer">
        <span className="note text-muted">{worst?.reasonText ?? "Everything the image can show is in order. Physical type size still needs a ruler."}</span>
        <span className="spacer" />
        <button className="btn btn-secondary" onClick={onBack} type="button">Back to all checks</button>
        <button className="btn btn-primary blueprint" onClick={onBack} type="button"><Corners />{icons.check()} Warning looks compliant: continue</button>
      </footer>
    </main>
  );
}
