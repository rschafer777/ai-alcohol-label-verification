import { useState, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import { Badge } from "../../components/StatusTag";
import type { CheckResult, VerificationResult } from "../../contracts/types";
import { checkGroup, displayLabel, EDITABLE_IDS, GROUP_ORDER, observedDisplay, reasonShort, ruleExpectation, shortLabel, tally, tallyText } from "./check-view";

export interface CheckListProps {
  result: VerificationResult;
  checks: CheckResult[];
  selectedId: string | null;
  correctedIds: ReadonlySet<string>;
  onSelect: (id: string) => void;
  onInspectWarning: () => void;
  onCorrect: ((check: CheckResult, value: string) => void) | null;
}

function CorrectionEditor({ check, onCancel, onSave }: { check: CheckResult; onCancel: () => void; onSave: (value: string) => void }): ReactElement {
  const initialType = check.observedDisplay === "malt_beverage" || check.observedDisplay === "Beer / malt"
    ? "malt_beverage"
    : check.observedDisplay === "wine" || check.observedDisplay === "Wine"
      ? "wine"
      : check.observedDisplay === "distilled_spirits" || check.observedDisplay === "Distilled spirits"
        ? "distilled_spirits"
        : "";
  const [value, setValue] = useState(check.checkId === "beverage_type" ? initialType : check.observedDisplay ?? "");
  const producer = check.checkId === "producer";
  return (
    <form aria-label={`Correct the read value for ${displayLabel(check)}`} onSubmit={(event) => { event.preventDefault(); if (value.trim()) onSave(value.trim()); }} style={{ display: "grid", gap: 6 }}>
      {check.checkId === "beverage_type"
        ? <select aria-label="Corrected value" autoFocus className="input" onChange={(event) => setValue(event.target.value)} value={value}><option value="">Choose type</option><option value="malt_beverage">Beer / malt</option><option value="wine">Wine</option><option value="distilled_spirits">Distilled spirits</option></select>
        : producer
        ? <textarea aria-label="Corrected value" autoFocus className="input" maxLength={1000} onChange={(event) => setValue(event.target.value)} rows={5} value={value} />
        : <input aria-label="Corrected value" autoFocus className="input" maxLength={500} onChange={(event) => setValue(event.target.value)} value={value} />}
      <span style={{ display: "flex", gap: 6 }}>
        <button className="btn btn-primary" style={{ fontSize: 12, padding: "4px 10px" }} type="submit">Save correction</button>
        <button className="btn btn-ghost" onClick={onCancel} style={{ fontSize: 12 }} type="button">Cancel</button>
      </span>
      <span className="text-muted" style={{ fontSize: 11 }}>The original OCR value and its evidence stay on record.</span>
    </form>
  );
}

export function CheckTable({ result, checks, selectedId, correctedIds, onSelect, onInspectWarning, onCorrect, warningExpanded, onToggleWarning }: CheckListProps & { warningExpanded: boolean; onToggleWarning: () => void }): ReactElement {
  const [editing, setEditing] = useState<string | null>(null);
  return (
    <>
      {GROUP_ORDER.map((group) => {
        const rows = checks.filter((check) => checkGroup(check) === group.id);
        if (!rows.length) return null;
        const isWarning = group.id === "warning";
        const open = !isWarning || warningExpanded;
        return (
          <div className="check-group" key={group.id}>
            <div className="group-head">
              <h5>{group.title}</h5><span className="tally text-muted">{tallyText(tally(rows))}</span>
              {isWarning ? <span className="actions"><button className="btn btn-ghost" onClick={onToggleWarning} type="button">{warningExpanded ? "Collapse 10 checks" : "Expand 10 checks"}</button><button className="btn btn-secondary" onClick={onInspectWarning} type="button">{icons.scan()} Inspect warning</button></span> : null}
            </div>
            {open ? (
              <div className="table-wrap">
                <table aria-label={`${group.title} checks`} className="table check-table">
                  <colgroup><col style={{ width: "22%" }} /><col style={{ width: "26%" }} /><col style={{ width: "26%" }} /><col style={{ width: "16%" }} /><col style={{ width: "10%" }} /></colgroup>
                  <thead><tr><th>Check</th><th>Rule expects</th><th>Read on label</th><th>Result</th><th /></tr></thead>
                  <tbody>
                    {rows.map((check) => {
                      const selected = selectedId === check.checkId;
                      const editable = !!onCorrect && check.applicable && EDITABLE_IDS.has(check.checkId);
                      const corrected = correctedIds.has(check.checkId) || check.observationProvenance === "reviewer_corrected";
                      return (
                        <tr aria-selected={selected} className={check.applicable ? "" : "na"} key={check.checkId}>
                          <td className="check-name">{displayLabel(check)}{corrected ? <><br /><span className="tag tag-outline" style={{ fontSize: 10 }}>Reviewer-corrected</span></> : null}</td>
                          <td className="small">{ruleExpectation(check)}</td>
                          <td className="small">
                            {editing === check.checkId && onCorrect ? <CorrectionEditor check={check} onCancel={() => setEditing(null)} onSave={(value) => { setEditing(null); onCorrect(check, value); }} /> : (
                              <span className="read-cell"><span>{observedDisplay(check, result)}</span>{editable ? <button aria-label={`Correct the read value for ${displayLabel(check)}`} className="btn btn-ghost btn-icon" onClick={() => { if (!selected) onSelect(check.checkId); setEditing(check.checkId); }} type="button">{icons.pencil(14)}</button> : null}</span>
                            )}
                          </td>
                          <td><span className="result-cell"><Badge applicable={check.applicable} state={check.state} /><span className="reason text-muted">{reasonShort(check)}</span></span></td>
                          <td className="right">{check.evidenceRef || editable ? <button aria-pressed={selected} className="btn btn-ghost show-btn" onClick={() => onSelect(check.checkId)} type="button">{icons.target(14)} {check.evidenceRef ? "Show" : "Select area"}</button> : null}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="warning-strip">
                {rows.map((check) => <span className={check.applicable ? "" : "na"} key={check.checkId}><Badge applicable={check.applicable} mini state={check.state} /><span>{shortLabel(check)}</span></span>)}
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}

export function CheckCards({ result, checks, selectedId, correctedIds, onSelect, onInspectWarning }: CheckListProps): ReactElement {
  return (
    <>
      {GROUP_ORDER.map((group) => {
        const rows = checks.filter((check) => checkGroup(check) === group.id);
        if (!rows.length) return null;
        return (
          <div className="check-group cards" key={group.id}>
            <div className="group-head"><h5>{group.title}</h5><span className="tally text-muted">{tallyText(tally(rows))}</span>{group.id === "warning" ? <button className="btn btn-secondary" onClick={onInspectWarning} style={{ marginLeft: "auto", fontSize: 13 }} type="button">{icons.scan()} Inspect warning</button> : null}</div>
            <div className="card-grid">
              {rows.map((check) => {
                const selected = selectedId === check.checkId;
                const corrected = correctedIds.has(check.checkId) || check.observationProvenance === "reviewer_corrected";
                return (
                  <article aria-selected={selected} className={`card check-card${check.applicable ? "" : " na"}`} key={check.checkId}>
                    <div className="card-head"><span className="card-title">{displayLabel(check)}{corrected ? <> <span className="tag tag-outline" style={{ fontSize: 10 }}>Reviewer-corrected</span></> : null}</span><Badge applicable={check.applicable} state={check.state} /></div>
                    <dl>
                      <div><dt className="dl-label text-muted">Rule expects</dt><dd>{ruleExpectation(check)}</dd></div>
                      <div><dt className="dl-label text-muted">Read on label</dt><dd>{observedDisplay(check, result)}</dd></div>
                    </dl>
                    <p className="card-body">{check.reasonText}</p>
                    <div className="card-meta"><span>{check.capability === "human_confirmation" ? "Needs human confirmation" : check.capability === "visual_heuristic" ? "Visual heuristic" : check.reasonCode === "label_value_readable" ? "Label-derived: not compared with a COLA record" : "OCR: original pixels"}</span>{check.evidenceRef ? <button aria-pressed={selected} className="btn btn-ghost" onClick={() => onSelect(check.checkId)} type="button">{icons.target(14)} Show on label</button> : null}</div>
                  </article>
                );
              })}
            </div>
          </div>
        );
      })}
    </>
  );
}

export function CheckRail({ result, checks, selectedId, onSelect, onInspectWarning }: CheckListProps): ReactElement {
  const active = checks.find((check) => check.checkId === selectedId) ?? checks[1] ?? checks[0];
  return (
    <>
      <ol className="check-rail">
        {checks.map((check) => (
          <li key={check.checkId}>
            <button aria-pressed={selectedId === check.checkId} className={check.applicable ? "" : "na"} onClick={() => onSelect(check.checkId)} type="button"><span>{displayLabel(check)}</span><Badge applicable={check.applicable} mini state={check.state} /></button>
          </li>
        ))}
      </ol>
      {active ? (
        <div className="card blueprint check-detail">
          <Corners />
          <div className="card-head"><span className="card-title">{displayLabel(active)}</span><Badge applicable={active.applicable} state={active.state} /></div>
          <dl>
            <div><dt className="dl-label text-muted">Rule expects</dt><dd>{ruleExpectation(active)}</dd></div>
            <div><dt className="dl-label text-muted">Read on label</dt><dd>{observedDisplay(active, result)}</dd></div>
          </dl>
          <p className="card-body">{active.reasonText}</p>
          <button className="btn btn-secondary" onClick={onInspectWarning} type="button">{icons.scan()} Inspect warning</button>
        </div>
      ) : null}
    </>
  );
}
