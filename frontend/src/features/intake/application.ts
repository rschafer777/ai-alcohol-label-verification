import type { AnalysisResult, BeverageType, ReferenceRecord } from "../../contracts/types";

/**
 * Application (COLA form) values a reviewer types before the label is read. Every field is
 * optional: whatever is entered is compared with the label, and whatever is left blank is
 * taken from the label read itself so the profile-specific rules still run.
 */
export interface ApplicationInput {
  beverageType: BeverageType | null;
  brandName: string;
  classType: string;
  abv: string;
  proof: string;
  netContents: string;
  producer: string;
  imported: boolean;
  country: string;
}

export const EMPTY_APPLICATION: ApplicationInput = {
  beverageType: null,
  brandName: "",
  classType: "",
  abv: "",
  proof: "",
  netContents: "",
  producer: "",
  imported: false,
  country: "",
};

export function hasApplicationValues(input: ApplicationInput | null | undefined): boolean {
  if (!input) return false;
  return Boolean(
    input.beverageType || input.brandName.trim() || input.classType.trim() || input.abv.trim() || input.proof.trim() || input.netContents.trim() || input.producer.trim() || input.country.trim(),
  );
}

/** Field names of the entered values, used to tell the reviewer what was compared. */
export function enteredFields(input: ApplicationInput): string[] {
  const names: string[] = [];
  if (input.brandName.trim()) names.push("brand");
  if (input.classType.trim()) names.push("class/type");
  if (input.abv.trim()) names.push("alcohol content");
  if (input.proof.trim()) names.push("proof");
  if (input.netContents.trim()) names.push("net contents");
  if (input.producer.trim()) names.push("producer");
  if (input.country.trim()) names.push("country");
  return names;
}

function parseNumber(value: string): number | null {
  const match = value.replace(",", ".").match(/\d+(?:\.\d+)?/);
  return match ? Number(match[0]) : null;
}

const UNITS: Array<[RegExp, ReferenceRecord["netContentsUnit"]]> = [
  [/\bml\b|millilit/i, "mL"],
  [/fl\.?\s*oz|fluid|\boz\b/i, "fl oz"],
  [/\bpt\b|pint/i, "pt"],
  [/\bqt\b|quart/i, "qt"],
  [/gal/i, "gal"],
  [/\bl\b|lit(?:er|re)/i, "L"],
];

export function parseNetContents(value: string): { value: number | null; unit: ReferenceRecord["netContentsUnit"] | null } {
  const amount = parseNumber(value);
  const unit = UNITS.find(([pattern]) => pattern.test(value))?.[1] ?? null;
  return { value: amount, unit };
}

/**
 * Build the reference record for POST /api/v1/verifications from the entered application
 * values, falling back to the label-derived draft for anything left blank.
 */
export function referenceFromApplication(input: ApplicationInput, analysis: AnalysisResult): ReferenceRecord | null {
  const draft = analysis.draft;
  const type = input.beverageType ?? draft.beverageType;
  if (!type) return null;
  const abv = input.abv.trim() ? parseNumber(input.abv) : draft.abvPercent;
  const proof = input.proof.trim() ? parseNumber(input.proof) : draft.proof;
  const net = input.netContents.trim() ? parseNetContents(input.netContents) : { value: draft.netContentsValue, unit: draft.netContentsUnit };
  const country = input.country.trim();
  const imported = input.imported || Boolean(country) || (!input.country.trim() && !input.imported && draft.isImported);
  const countryOfOrigin = country || draft.countryOfOrigin || null;
  return {
    profileId: "all_beverages_demo_v2",
    beverageType: type,
    referenceProvenance: "manual",
    fieldProvenance: {
      beverage_type: input.beverageType ? "trusted_application" : "label_ocr",
      brand_name: input.brandName.trim() ? "trusted_application" : "label_ocr",
      class_type: input.classType.trim() ? "trusted_application" : "label_ocr",
      alcohol_content: input.abv.trim() ? "trusted_application" : "label_ocr",
      proof: input.proof.trim() ? "trusted_application" : "label_ocr",
      net_contents: input.netContents.trim() ? "trusted_application" : "label_ocr",
      producer_name_address: input.producer.trim() ? "trusted_application" : "label_ocr",
      country_of_origin: input.imported || input.country.trim() ? "trusted_application" : "label_ocr",
      wine_appellation: "label_ocr",
      wine_sulfite_declaration: "label_ocr",
      malt_alcohol_source: "label_ocr",
    },
    caseLabel: null,
    brandName: (input.brandName.trim() || draft.brandName || "Brand not stated").slice(0, 160),
    classType: (input.classType.trim() || draft.classType || "Class or type not stated").slice(0, 240),
    abvPercent: abv ?? null,
    proof: proof ?? null,
    netContentsValue: net.value ?? 1,
    netContentsUnit: net.unit ?? "mL",
    producerNameAddress: (input.producer.trim() || draft.producerNameAddress || "Producer not stated").slice(0, 1000),
    isImported: imported,
    countryOfOrigin: imported ? (countryOfOrigin ?? "Not stated") : null,
    wineAppellation: draft.wineAppellation,
    wineSulfiteStatus: draft.wineSulfiteStatus,
    maltAlcoholSource: draft.maltAlcoholSource,
  };
}
