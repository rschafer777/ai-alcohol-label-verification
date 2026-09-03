import type { AnalysisResult, BeverageType, ReferenceRecord } from "../../contracts/types";
import { slotTitle, type ReviewImage } from "./review-images";

/** Build the reviewer-corrected reference for REQ-8 from the label-derived draft. */
export function referenceFromAnalysis(analysis: AnalysisResult, overrides: Partial<Record<string, string>>, beverageType?: BeverageType | null): ReferenceRecord | null {
  const draft = analysis.draft;
  const type = beverageType ?? draft.beverageType;
  if (!type) return null;
  const abv = overrides.abv !== undefined ? parseNumber(overrides.abv) : draft.abvPercent;
  const proof = overrides.proof !== undefined ? parseNumber(overrides.proof) : draft.proof;
  const net = overrides.net_contents !== undefined ? parseVolume(overrides.net_contents) : { value: draft.netContentsValue, unit: draft.netContentsUnit };
  const imported = overrides.country !== undefined ? !!overrides.country.trim() : draft.isImported;
  const country = overrides.country !== undefined ? overrides.country.trim() || null : draft.countryOfOrigin;
  return {
    profileId: "all_beverages_demo_v2",
    beverageType: type,
    referenceProvenance: "manual",
    caseLabel: null,
    brandName: (overrides.brand ?? draft.brandName ?? "Brand not detected").slice(0, 160),
    classType: (overrides.class_type ?? draft.classType ?? "Class or type not detected").slice(0, 240),
    abvPercent: abv ?? null,
    proof: proof ?? null,
    netContentsValue: net.value ?? 1,
    netContentsUnit: net.unit ?? "mL",
    producerNameAddress: (overrides.producer ?? draft.producerNameAddress ?? "Producer not detected").slice(0, 500),
    isImported: imported,
    countryOfOrigin: imported ? (country ?? "Not stated") : null,
    wineAppellation: overrides.wine_appellation ?? draft.wineAppellation,
    wineSulfiteStatus: draft.wineSulfiteStatus,
    maltAlcoholSource: draft.maltAlcoholSource,
  };
}

function parseNumber(value: string): number | null {
  const match = value.replace(",", ".").match(/\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
}

const UNITS: Array<[RegExp, ReferenceRecord["netContentsUnit"]]> = [
  [/\bml\b|millilit/i, "mL"], [/\bl\b|lit(?:er|re)/i, "L"], [/fl\.?\s*oz|fluid/i, "fl oz"], [/\bpt|pint/i, "pt"], [/\bqt|quart/i, "qt"], [/gal/i, "gal"],
];

function parseVolume(value: string): { value: number | null; unit: ReferenceRecord["netContentsUnit"] | null } {
  const amount = parseNumber(value);
  const unit = UNITS.find(([pattern]) => pattern.test(value))?.[1] ?? null;
  return { value: amount, unit };
}

/** Object URLs for the files in memory; the caller revokes them when the record changes. */
export function imagesForFiles(files: File[], addedFrom = files.length): ReviewImage[] {
  return files.map((file, index) => ({
    src: URL.createObjectURL(file),
    name: file.name,
    alt: `${file.name} label image`,
    title: slotTitle(index, files.length, index >= addedFrom),
  }));
}

export function revokeImages(images: ReviewImage[]): void {
  images.forEach((image) => { if (image.src.startsWith("blob:")) URL.revokeObjectURL(image.src); });
}

/** Map a corrected check id to the reference field it edits (REQ-8). */
export const CORRECTION_FIELDS: Record<string, string> = {
  beverage_type: "beverage_type", brand: "brand", class_type: "class_type", abv: "abv", proof: "proof",
  net_contents: "net_contents", producer: "producer", country: "country", wine_appellation: "wine_appellation",
};
