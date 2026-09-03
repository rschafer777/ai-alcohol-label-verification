import type { ReactElement } from "react";

import type { PublicError } from "../contracts/types";
import { Corners } from "./Blueprint";
import { stateCopy } from "./state-copy";
import { SemTag } from "./StatusTag";

export function StateCard({ error, onPrimary, onSecondary, standalone = false }: { error: PublicError; onPrimary?: () => void; onSecondary?: () => void; standalone?: boolean }): ReactElement {
  const copy = stateCopy(error);
  return (
    <article className={`card blueprint state-card${standalone ? " standalone" : ""}`} role={copy.role} tabIndex={-1}>
      <Corners />
      <div className="state-head"><span className="card-kicker">{copy.code}</span><SemTag icon={copy.icon} kind={copy.kind}>{copy.tag}</SemTag></div>
      <div className="state-body"><span>{copy.icon}</span><div><span className="card-title">{copy.title}</span><p className="card-body">{copy.body}</p>{error.nextAction ? <p className="card-body"><strong>Next:</strong> {error.nextAction}</p> : null}</div></div>
      <div className="card-meta state-meta"><span>{copy.meta} · Request {error.requestId}</span><span>{onSecondary ? <button className="btn btn-ghost" onClick={onSecondary} type="button">{copy.secondary}</button> : null}{onPrimary ? <button className="btn btn-secondary" onClick={onPrimary} type="button">{copy.primary}</button> : null}</span></div>
    </article>
  );
}
