import type { CSSProperties, ReactElement, ReactNode } from "react";

import type { CheckState } from "../contracts/types";
import { icons } from "./icons";
import { Spinner } from "./Spinner";
import { stateKind, summaryKind, summaryLabel, type Disposition, type MachineSummary, type SemanticKind } from "./status";

export function SemTag({ kind, icon, children, style, title }: { kind: SemanticKind; icon?: ReactNode; children: ReactNode; style?: CSSProperties; title?: string }): ReactElement {
  return <span className={`tag tag-${kind}`} style={style} title={title}>{icon}{children}</span>;
}

export function Badge({ state, applicable = true, mini = false }: { state: CheckState; applicable?: boolean; mini?: boolean }): ReactElement {
  const text = !applicable ? "Not applicable" : state;
  const icon = !applicable ? icons.minus() : state === "Match" ? icons.check() : state === "Mismatch" ? icons.x() : state === "Review" ? icons.help() : icons.minus();
  const className = !applicable ? "tag tag-neutral tag-na" : state === "Not verified" ? "tag tag-neutral tag-nv" : `tag tag-${stateKind(state)}`;
  return <span className={className} title={text}>{icon}{mini ? <span className="sr-only">{text}</span> : text}</span>;
}

export function SummaryTag({ summary }: { summary: MachineSummary }): ReactElement {
  const kind = summaryKind(summary);
  const icon = summary === "Bad image" ? icons.imageOff() : summary === "Running" ? <Spinner /> : summary === "Queued" || summary === "Cancelled" ? icons.clock() : summary === "Failed" ? icons.alert() : kind === "pass" ? icons.check() : kind === "fail" ? icons.x() : icons.help();
  return <SemTag icon={icon} kind={kind} title={summary}>{summaryLabel(summary)}</SemTag>;
}

export function DispositionTag({ value }: { value: Disposition | string | null | undefined }): ReactElement {
  if (value === "approved") return <SemTag icon={icons.check()} kind="pass">Approved</SemTag>;
  if (value === "rejected") return <SemTag icon={icons.x()} kind="fail">Rejected</SemTag>;
  if (value === "more_info_requested") return <SemTag icon={icons.help()} kind="warn">More info requested</SemTag>;
  return <span className="text-muted" style={{ fontSize: 12 }}>- undecided</span>;
}

export function GroupStatusTag({ status }: { status: "ready" | "confirm" | "conflict" }): ReactElement {
  if (status === "ready") return <SemTag icon={icons.check()} kind="pass">Ready</SemTag>;
  if (status === "confirm") return <SemTag icon={icons.help()} kind="warn">Needs confirmation</SemTag>;
  return <SemTag icon={icons.alert()} kind="fail">Conflict</SemTag>;
}
