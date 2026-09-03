import type { ReactElement } from "react";

import { icons } from "../components/icons";

export type TrayDestination = "home" | "batch" | "history";

export function LeftTray({ open, current, historyTotal, historyCap, agentName, onNavigate, onHelp }: {
  open: boolean;
  current: TrayDestination | null;
  historyTotal: number;
  historyCap: number;
  agentName: string;
  onNavigate: (destination: TrayDestination) => void;
  onHelp: () => void;
}): ReactElement {
  const item = (key: TrayDestination, icon: ReactElement, label: string, sub: string) => (
    <li>
      <button aria-current={current === key ? "page" : undefined} className="tray-link" onClick={() => onNavigate(key)} tabIndex={open ? 0 : -1} type="button">
        {icon}
        <span><span className="tray-label">{label}</span><span className="tray-sub text-muted">{sub}</span></span>
      </button>
    </li>
  );
  return (
    <nav aria-hidden={!open} aria-label="Primary" className="tray" id="lv-tray">
      <ol>
        {item("home", icons.image(28), "Check one label", "1-3 images of one product")}
        {item("batch", icons.folder(28), "Check a batch", "Up to 300 products")}
        {item("history", icons.clock(16), "History", `${historyTotal} of ${historyCap} kept`)}
      </ol>
      <div className="tray-foot text-muted">
        <span>Signed in as <strong>{agentName}</strong></span>
        <button className="btn btn-ghost" onClick={onHelp} tabIndex={open ? 0 : -1} type="button">{icons.keyboard()} Shortcuts &amp; help</button>
      </div>
    </nav>
  );
}
