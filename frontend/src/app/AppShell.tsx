import { useEffect, useRef, type ReactElement, type ReactNode } from "react";

import { Corners } from "../components/Blueprint";
import { icons } from "../components/icons";
import { LeftTray, type TrayDestination } from "./LeftTray";

import { AGENT_NAME } from "./agent";

export function HelpDialog({ onClose }: { onClose: () => void }): ReactElement {
  const closeButton = useRef<HTMLButtonElement>(null);
  useEffect(() => {
    closeButton.current?.focus();
  }, []);
  return (
    <div className="dialog-backdrop" onClick={onClose}>
      <div aria-label="Keyboard shortcuts" className="dialog blueprint" onClick={(event) => event.stopPropagation()} role="dialog" style={{ width: "min(560px,100%)" }}>
        <Corners />
        <div className="dialog-title">Shortcuts: optional, never required</div>
        <dl className="shortcuts-list">
          <dt><kbd>A</kbd></dt><dd>Approve</dd>
          <dt><kbd>R</kbd></dt><dd>Reject</dd>
          <dt><kbd>M</kbd></dt><dd>Request more info (better image, records, etc.)</dd>
          <dt><kbd>E</kbd></dt><dd>Open next exception (batch)</dd>
          <dt><kbd>&uarr; &darr;</kbd></dt><dd>Move through checks; Enter shows evidence</dd>
          <dt><kbd>1 / 2 / 3</kbd></dt><dd>Switch panel</dd>
          <dt><kbd>W</kbd></dt><dd>Inspect government warning</dd>
          <dt><kbd>Esc</kbd></dt><dd>Close / back</dd>
        </dl>
        <div className="dialog-actions"><button className="btn btn-secondary" onClick={onClose} ref={closeButton} type="button">Close</button></div>
      </div>
    </div>
  );
}

export function AppShell({ screenTitle, current, trayOpen, onToggleTray, helpOpen, onToggleHelp, historyTotal, historyCap, onNavigate, children }: {
  screenTitle: string;
  current: TrayDestination | null;
  trayOpen: boolean;
  onToggleTray: () => void;
  helpOpen: boolean;
  onToggleHelp: () => void;
  historyTotal: number;
  historyCap: number;
  onNavigate: (destination: TrayDestination) => void;
  children: ReactNode;
}): ReactElement {
  return (
    <div className="shell">
      <header aria-label="Application bar" className="topbar">
        <button aria-controls="lv-tray" aria-expanded={trayOpen} aria-label={trayOpen ? "Close navigation" : "Open navigation"} className="btn btn-icon" onClick={onToggleTray} type="button">{icons.menu()}</button>
        <a className="topbar-agency" href="#/" onClick={(event) => { event.preventDefault(); onNavigate("home"); }}>
          <img alt="Alcohol and Tobacco Tax and Trade Bureau seal" src="/ttb-seal.png" />
          <span><span className="agency">TTB</span><span className="agency-sub">Alcohol and Tobacco Tax and Trade Bureau<br />U.S. Department of the Treasury</span></span>
        </a>
        <span className="topbar-rule" />
        <span className="topbar-brand"><span>LabelVerify</span><span className="brand-sub">Alcohol label evidence assistant</span></span>
        <span className="topbar-title">{screenTitle}</span>
        <span className="topbar-rule short" />
        <span className="topbar-agent">{AGENT_NAME}</span>
        <span className="tag tag-white">Unofficial prototype</span>
        <button aria-label="Keyboard shortcuts and help" className="btn btn-icon" onClick={onToggleHelp} type="button">{icons.keyboard()}</button>
      </header>
      <div className="notice-band" role="note">
        <span>Synthetic or sanitized data only</span><span>·</span><span>Not connected to COLA: no legal decisions are issued</span><span>·</span><span>Values read from the label are not independent application data</span><span>·</span><span>Images are kept with each result so evidence can be re-checked</span>
      </div>
      <div className={`shell-body ${trayOpen ? "tray-open" : "tray-closed"}`}>
        <LeftTray agentName={AGENT_NAME} current={current} historyCap={historyCap} historyTotal={historyTotal} onHelp={onToggleHelp} onNavigate={onNavigate} open={trayOpen} />
        <div className="shell-content">{children}</div>
      </div>
      <footer className="shell-footer text-muted"><span>Evidence support for human review · history capped at {historyCap}</span></footer>
      {helpOpen ? <HelpDialog onClose={onToggleHelp} /> : null}
    </div>
  );
}
