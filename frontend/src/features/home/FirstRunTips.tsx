import { useEffect, useRef, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";

export function FirstRunTips({ onClose, onDismissForever }: { onClose: () => void; onDismissForever: () => void }): ReactElement {
  const first = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    first.current?.focus();
  }, []);
  return (
    <div aria-label="First-time tips" className="first-run" role="dialog">
      <div className="dialog blueprint">
        <Corners />
        <h6 className="kicker">First time here</h6>
        <div className="dialog-title">Three things, then we get out of your way</div>
        <ol className="tips">
          <li><span className="num">1</span><strong>Drop photos, nothing to type</strong><span className="text-muted">We read the brand, type, alcohol, contents, and the warning from the label itself.</span></li>
          <li><span className="num">2</span><strong>Every finding points at the label</strong><span className="text-muted">Select any row to see exactly where on the image it came from: green passes, amber questionable, red rejected.</span></li>
          <li><span className="num">3</span><strong>You decide</strong><span className="text-muted">The machine result and your Approve / Reject stay separate. Nothing here is a legal decision.</span></li>
        </ol>
        <div className="dialog-actions">
          <button className="btn btn-ghost" onClick={onDismissForever} ref={first} type="button">Don't show again</button>
          <button className="btn btn-primary blueprint btn-hit" onClick={onClose} type="button"><Corners />Got it</button>
        </div>
      </div>
    </div>
  );
}
