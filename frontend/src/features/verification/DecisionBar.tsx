import type { ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { icons } from "../../components/icons";
import { dispositionLabel, type Disposition } from "../../components/status";

export function DecisionButtons({ value, onChange, withKeys = true }: { value: Disposition; onChange: (value: Disposition) => void; withKeys?: boolean }): ReactElement {
  return (
    <>
      <button aria-pressed={value === "approved"} className="btn btn-primary blueprint btn-approve btn-decide" onClick={() => onChange("approved")} type="button"><Corners />{icons.check()} Approve {withKeys ? <kbd>A</kbd> : null}</button>
      <button aria-pressed={value === "rejected"} className="btn btn-secondary btn-reject btn-decide" onClick={() => onChange("rejected")} type="button">{icons.x()} Reject {withKeys ? <kbd>R</kbd> : null}</button>
      <button aria-pressed={value === "more_info_requested"} className="btn btn-secondary btn-more btn-decide" onClick={() => onChange("more_info_requested")} type="button">{icons.help()} Request more info {withKeys ? <kbd>M</kbd> : null}</button>
    </>
  );
}

export function DecisionBar({ disposition, note, onDisposition, onNote, saveState, inBatch, onNext, onSave }: {
  disposition: Disposition;
  note: string;
  onDisposition: (value: Disposition) => void;
  onNote: (value: string) => void;
  saveState: string;
  inBatch: boolean;
  onNext: () => void;
  onSave: () => void;
}): ReactElement {
  return (
    <footer className="decision-bar">
      <div className="disposition"><span className="text-muted">Your disposition</span><span className={`disposition-value ${disposition ?? ""}`}>{dispositionLabel(disposition)}</span></div>
      <span className="vrule" />
      <DecisionButtons onChange={onDisposition} value={disposition} />
      <input aria-label="Reviewer note" className="input" maxLength={1000} onChange={(event) => onNote(event.target.value)} placeholder="Note (optional): stays with this record, never changes the findings" value={note} />
      {saveState ? <span aria-live="polite" className="save-state text-muted">{saveState}</span> : null}
      {inBatch
        ? <button className="btn btn-secondary" onClick={onNext} type="button">Next exception {icons.arrow()} <kbd>E</kbd></button>
        : <button className="btn btn-secondary" onClick={onSave} type="button">Save &amp; check another {icons.arrow()}</button>}
    </footer>
  );
}
