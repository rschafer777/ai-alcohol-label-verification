import type { ReactElement } from "react";

import type { BeverageType } from "../../contracts/types";
import type { ApplicationInput } from "./application";

/*
 * Optional application (COLA form) values. The assignment's core workflow is "does what is on
 * the label match what is in the application"; typing the application values here turns the
 * label read into that comparison. Everything left blank is still read from the label.
 */
export function ApplicationDetails({ value, onChange, open, onToggle }: {
  value: ApplicationInput;
  onChange: (next: ApplicationInput) => void;
  open: boolean;
  onToggle: (open: boolean) => void;
}): ReactElement {
  function set<K extends keyof ApplicationInput>(key: K, next: ApplicationInput[K]) {
    onChange({ ...value, [key]: next });
  }

  return (
    <details className="application-details" onToggle={(event) => onToggle((event.target as HTMLDetailsElement).open)} open={open}>
      <summary>
        <strong>Compare with the application</strong>
        <span className="text-muted"> (optional): type what the COLA application says and we check the label against it</span>
      </summary>
      {open ? <div className="application-grid">
        <label className="application-field">
          <span>Beverage type</span>
          <select className="input" onChange={(event) => set("beverageType", (event.target.value || null) as BeverageType | null)} value={value.beverageType ?? ""}>
            <option value="">Read it from the label</option>
            <option value="malt_beverage">Beer / malt beverage</option>
            <option value="wine">Wine</option>
            <option value="distilled_spirits">Distilled spirits</option>
          </select>
        </label>
        <label className="application-field">
          <span>Brand name</span>
          <input className="input" maxLength={160} onChange={(event) => set("brandName", event.target.value)} placeholder="OLD TOM DISTILLERY" value={value.brandName} />
        </label>
        <label className="application-field">
          <span>Class / type</span>
          <input className="input" maxLength={240} onChange={(event) => set("classType", event.target.value)} placeholder="Kentucky Straight Bourbon Whiskey" value={value.classType} />
        </label>
        <label className="application-field">
          <span>Alcohol content (% by volume)</span>
          <input className="input" inputMode="decimal" maxLength={8} onChange={(event) => set("abv", event.target.value)} placeholder="45" value={value.abv} />
        </label>
        <label className="application-field">
          <span>Proof (spirits, if stated)</span>
          <input className="input" inputMode="decimal" maxLength={8} onChange={(event) => set("proof", event.target.value)} placeholder="90" value={value.proof} />
        </label>
        <label className="application-field">
          <span>Net contents</span>
          <input className="input" maxLength={24} onChange={(event) => set("netContents", event.target.value)} placeholder="750 mL" value={value.netContents} />
        </label>
        <label className="application-field wide">
          <span>Producer or bottler name and address</span>
          <input className="input" maxLength={500} onChange={(event) => set("producer", event.target.value)} placeholder="Distilled and bottled by Old Tom Distillery, Frankfort, Kentucky" value={value.producer} />
        </label>
        <label className="application-field check">
          <input checked={value.imported} onChange={(event) => set("imported", event.target.checked)} type="checkbox" />
          <span>Imported product</span>
        </label>
        <label className="application-field">
          <span>Country of origin (imports)</span>
          <input className="input" maxLength={80} onChange={(event) => set("country", event.target.value)} placeholder="Mexico" value={value.country} />
        </label>
      </div> : null}
      {open ? <p className="text-muted small">Leave anything blank and it is read from the label instead. Capitalization-only differences are flagged for your judgment, never rejected automatically.</p> : null}
    </details>
  );
}
