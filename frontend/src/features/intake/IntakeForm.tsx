import { useEffect, useMemo, useRef, type ChangeEvent, type DragEvent } from "react";

import type { DraftErrors, DraftField, ReferenceDraft } from "./model";

interface IntakeFormProps {
  draft: ReferenceDraft;
  errors: DraftErrors;
  panels: File[];
  disabled: boolean;
  sampleLoading: boolean;
  onFieldChange: <K extends DraftField>(field: K, value: ReferenceDraft[K]) => void;
  onAddPanels: (files: File[]) => void;
  onMovePanel: (index: number, direction: -1 | 1) => void;
  onRemovePanel: (index: number) => void;
  onTrySample: () => void;
  onVerify: () => void;
  onStartOver: () => void;
}

function ErrorText({ id, message }: { id: string; message?: string }) {
  if (!message) return null;
  return (
    <p className="field-error" id={id} role="alert">
      {message}
    </p>
  );
}

function PanelPreview({ file }: { file: File }) {
  const previewUrl = useMemo(
    () => typeof URL.createObjectURL === "function" ? URL.createObjectURL(file) : "",
    [file],
  );

  useEffect(() => {
    return () => {
      if (previewUrl && typeof URL.revokeObjectURL === "function") URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  return previewUrl ? <img alt={`Preview of ${file.name}`} src={previewUrl} /> : <span aria-hidden="true">Image</span>;
}

function TextField({
  field,
  label,
  draft,
  errors,
  disabled,
  onFieldChange,
  type = "text",
  inputMode,
  help,
}: {
  field: DraftField;
  label: string;
  draft: ReferenceDraft;
  errors: DraftErrors;
  disabled: boolean;
  onFieldChange: IntakeFormProps["onFieldChange"];
  type?: "text" | "number";
  inputMode?: "decimal";
  help?: string;
}) {
  const errorId = `error-${field}`;
  const helpId = `help-${field}`;
  return (
    <div className="field">
      <label htmlFor={`field-${field}`}>{label}</label>
      {help ? <p className="field-help" id={helpId}>{help}</p> : null}
      <input
        aria-describedby={[help ? helpId : "", errors[field] ? errorId : ""].filter(Boolean).join(" ") || undefined}
        aria-invalid={Boolean(errors[field])}
        disabled={disabled}
        id={`field-${field}`}
        inputMode={inputMode}
        onChange={(event) => onFieldChange(field, event.target.value as never)}
        type={type}
        value={String(draft[field])}
      />
      <ErrorText id={errorId} message={errors[field]} />
    </div>
  );
}

export function IntakeForm({
  draft,
  errors,
  panels,
  disabled,
  sampleLoading,
  onFieldChange,
  onAddPanels,
  onMovePanel,
  onRemovePanel,
  onTrySample,
  onVerify,
  onStartOver,
}: IntakeFormProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleFiles(event: ChangeEvent<HTMLInputElement>) {
    onAddPanels(Array.from(event.target.files ?? []));
    event.target.value = "";
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    if (!disabled) onAddPanels(Array.from(event.dataTransfer.files));
  }

  return (
    <div className="intake-layout">
      <section className="card intro-card" aria-labelledby="start-heading">
        <p className="eyebrow">Distilled spirits label review</p>
        <h1 id="start-heading" tabIndex={-1}>Check label details against an application</h1>
        <p className="lede">
          Enter the application values and add clear images of every label panel. LabelVerify points to the evidence and leaves the final decision to you.
        </p>
        <button className="button secondary sample-button" disabled={disabled || sampleLoading} onClick={onTrySample} type="button">
          {sampleLoading ? "Loading sample..." : "Try the built-in sample"}
        </button>
        <p className="field-help">Loads one complete synthetic example. No external service is needed.</p>
      </section>

      <form className="card form-card" noValidate onSubmit={(event) => { event.preventDefault(); onVerify(); }}>
        <div className="section-heading">
          <div>
            <p className="step-label">Step 1</p>
            <h2>Application values</h2>
          </div>
          <span className="required-note">All fields required unless marked optional</span>
        </div>

        <div className="field-grid">
          <TextField field="caseLabel" label="Case label (optional)" draft={draft} errors={errors} disabled={disabled} onFieldChange={onFieldChange} help="For display in this browser session only." />
          <TextField field="brandName" label="Brand name" draft={draft} errors={errors} disabled={disabled} onFieldChange={onFieldChange} />
          <TextField field="classType" label="Class or type" draft={draft} errors={errors} disabled={disabled} onFieldChange={onFieldChange} />
          <TextField field="abvPercent" label="Alcohol by volume (%)" draft={draft} errors={errors} disabled={disabled} onFieldChange={onFieldChange} type="number" inputMode="decimal" />
          <TextField field="proof" label="Proof (optional)" draft={draft} errors={errors} disabled={disabled} onFieldChange={onFieldChange} type="number" inputMode="decimal" />
          <div className="field net-contents-field">
            <label htmlFor="field-netContentsValue">Net contents</label>
            <div className="input-pair">
              <input
                aria-describedby={errors.netContentsValue ? "error-netContentsValue" : undefined}
                aria-invalid={Boolean(errors.netContentsValue)}
                disabled={disabled}
                id="field-netContentsValue"
                inputMode="decimal"
                onChange={(event) => onFieldChange("netContentsValue", event.target.value)}
                type="number"
                value={draft.netContentsValue}
              />
              <select
                aria-label="Net contents unit"
                disabled={disabled}
                id="field-netContentsUnit"
                onChange={(event) => onFieldChange("netContentsUnit", event.target.value as "mL" | "L")}
                value={draft.netContentsUnit}
              >
                <option value="mL">mL</option>
                <option value="L">L</option>
              </select>
            </div>
            <ErrorText id="error-netContentsValue" message={errors.netContentsValue} />
          </div>
          <div className="field full-width">
            <label htmlFor="field-producerNameAddress">Producer or bottler name and address</label>
            <textarea
              aria-describedby={errors.producerNameAddress ? "error-producerNameAddress" : undefined}
              aria-invalid={Boolean(errors.producerNameAddress)}
              disabled={disabled}
              id="field-producerNameAddress"
              maxLength={500}
              onChange={(event) => onFieldChange("producerNameAddress", event.target.value)}
              rows={3}
              value={draft.producerNameAddress}
            />
            <ErrorText id="error-producerNameAddress" message={errors.producerNameAddress} />
          </div>
          <div className="field full-width checkbox-field">
            <input
              checked={draft.isImported}
              disabled={disabled}
              id="field-isImported"
              onChange={(event) => onFieldChange("isImported", event.target.checked)}
              type="checkbox"
            />
            <label htmlFor="field-isImported">This product is imported</label>
          </div>
          {draft.isImported ? (
            <TextField field="countryOfOrigin" label="Country of origin" draft={draft} errors={errors} disabled={disabled} onFieldChange={onFieldChange} />
          ) : null}
        </div>

        <div className="section-heading panel-heading">
          <div>
            <p className="step-label">Step 2</p>
            <h2>Label panels</h2>
          </div>
          <span className="panel-count" aria-live="polite">{panels.length} of 6 added</span>
        </div>

        <div
          aria-describedby={`panel-help${errors.panels ? " error-panels" : ""}`}
          className={`drop-zone${errors.panels ? " has-error" : ""}`}
          onDragOver={(event) => event.preventDefault()}
          onDrop={handleDrop}
        >
          <strong>Drop label images here</strong>
          <span id="panel-help">JPEG, PNG, or WebP. Up to 4 MiB each and 8 MiB total.</span>
          <button className="button tertiary" disabled={disabled || panels.length >= 6} id="choose-panels" onClick={() => fileInputRef.current?.click()} type="button">
            Choose images
          </button>
          <input
            accept="image/jpeg,image/png,image/webp"
            aria-describedby="panel-help error-panels"
            aria-label="Label panel images"
            className="visually-hidden"
            disabled={disabled || panels.length >= 6}
            id="field-panels"
            multiple
            onChange={handleFiles}
            ref={fileInputRef}
            tabIndex={-1}
            type="file"
          />
        </div>
        <ErrorText id="error-panels" message={errors.panels} />

        {panels.length ? (
          <ol className="panel-list" aria-label="Selected label panels">
            {panels.map((file, index) => (
              <li key={`${file.name}-${file.size}-${file.lastModified}`}>
                <div className="panel-thumb"><PanelPreview file={file} /></div>
                <div className="panel-meta">
                  <strong>Panel {index + 1}</strong>
                  <span>{file.name}</span>
                  <span>{(file.size / 1_048_576).toFixed(2)} MiB</span>
                </div>
                <div className="panel-actions">
                  <button aria-label={`Move ${file.name} up`} disabled={disabled || index === 0} onClick={() => onMovePanel(index, -1)} type="button">Up</button>
                  <button aria-label={`Move ${file.name} down`} disabled={disabled || index === panels.length - 1} onClick={() => onMovePanel(index, 1)} type="button">Down</button>
                  <button aria-label={`Remove ${file.name}`} disabled={disabled} onClick={() => onRemovePanel(index)} type="button">Remove</button>
                </div>
              </li>
            ))}
          </ol>
        ) : null}

        <div className="form-actions">
          <button className="button primary" disabled={disabled} type="submit">Verify label</button>
          <button className="button quiet" disabled={disabled} onClick={onStartOver} type="button">Start over</button>
        </div>
        <p className="session-note">Your form and images stay only in this browser tab. Refreshing or closing this page clears them.</p>
      </form>
    </div>
  );
}
