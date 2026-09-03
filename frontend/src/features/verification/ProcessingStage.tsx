import { useEffect, useRef, type ReactElement } from "react";

import { Corners } from "../../components/Blueprint";
import { FilePreview } from "../../components/FilePreview";
import { icons } from "../../components/icons";
import { Spinner } from "../../components/Spinner";

export type ProcessingPhase = "uploading" | "reading" | "checking";

export function ProcessingStage({ files, elapsedSeconds, phase, uploadSeconds, deadlineSeconds, onCancel, kicker = "Check one label", title = "Reading the label" }: {
  files: File[];
  elapsedSeconds: number;
  phase: ProcessingPhase;
  uploadSeconds: number | null;
  deadlineSeconds: number;
  onCancel: () => void;
  kicker?: string;
  title?: string;
}): ReactElement {
  const heading = useRef<HTMLHeadingElement>(null);
  useEffect(() => {
    heading.current?.focus();
  }, []);
  const count = files.length;
  const reached = { uploading: 0, reading: 1, checking: 2 }[phase];
  const stages = [
    { label: "Uploaded", detail: `${count} image${count === 1 ? "" : "s"}${uploadSeconds !== null ? ` · ${uploadSeconds.toFixed(1)} s` : ""}`, icon: reached > 0 ? icons.check() : <Spinner /> },
    { label: "Reading label", detail: `OCR on image 1 of ${count}`, icon: reached === 1 ? <Spinner /> : reached > 1 ? icons.check() : icons.clock() },
    { label: "Checking rules", detail: "Waits for the read: type decides which 24 checks apply", icon: reached === 2 ? <Spinner /> : icons.clock() },
  ];
  return (
    <main aria-live="polite" className="processing" data-screen-label="Processing">
      <div className="processing-head"><h6 className="kicker">{kicker}</h6><button className="btn btn-ghost" onClick={onCancel} type="button">Cancel</button></div>
      <section className="card blueprint processing-card">
        <Corners />
        <div className="processing-thumbs">
          {files.map((file, index) => <div className="scan-thumb" key={`${file.name}-${index}`}><FilePreview alt={file.name} file={file} /><div aria-hidden="true" className="scan-sweep" /></div>)}
        </div>
        <div className="processing-main">
          <div className="processing-title"><h2 id="processing-heading" ref={heading} tabIndex={-1}>{title}</h2><span className="elapsed">{elapsedSeconds.toFixed(1)} s</span></div>
          <ol className="stages">
            {stages.map((stage, index) => <li className={index <= reached ? "reached" : ""} key={stage.label}><span className="stage-label">{stage.icon} {stage.label}</span><span className="stage-detail text-muted">{stage.detail}</span></li>)}
          </ol>
          <p className="processing-note text-muted">Most labels finish in about 5 seconds. If it passes {deadlineSeconds} seconds we stop, keep your images selected, and tell you what to try.</p>
        </div>
      </section>
    </main>
  );
}
