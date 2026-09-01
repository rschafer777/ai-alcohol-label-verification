import { limits, profileId, type ReferenceRecord } from "../../api/generated-contract";

export const MAX_FILE_BYTES = limits.fileBytes;
export const MAX_AGGREGATE_BYTES = limits.aggregateFileBytes;
export const MAX_PANELS = limits.panelCountMax;
export const ACCEPTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"] as const;
type NetContentsUnit = ReferenceRecord["netContentsUnit"];

export interface ReferenceDraft {
  caseLabel: string;
  brandName: string;
  classType: string;
  abvPercent: string;
  proof: string;
  netContentsValue: string;
  netContentsUnit: NetContentsUnit;
  producerNameAddress: string;
  isImported: boolean;
  countryOfOrigin: string;
}

export type DraftField = keyof ReferenceDraft;
export type DraftErrors = Partial<Record<DraftField | "panels", string>>;

export const EMPTY_DRAFT: ReferenceDraft = {
  caseLabel: "",
  brandName: "",
  classType: "",
  abvPercent: "",
  proof: "",
  netContentsValue: "",
  netContentsUnit: "mL",
  producerNameAddress: "",
  isImported: false,
  countryOfOrigin: "",
};

export function referenceToDraft(reference: ReferenceRecord): ReferenceDraft {
  return {
    caseLabel: reference.caseLabel ?? "",
    brandName: reference.brandName,
    classType: reference.classType,
    abvPercent: String(reference.abvPercent),
    proof: reference.proof == null ? "" : String(reference.proof),
    netContentsValue: String(reference.netContentsValue),
    netContentsUnit: reference.netContentsUnit,
    producerNameAddress: reference.producerNameAddress,
    isImported: reference.isImported,
    countryOfOrigin: reference.countryOfOrigin ?? "",
  };
}

function required(value: string, label: string, maxLength: number): string | undefined {
  const trimmed = value.trim();
  if (!trimmed) return `${label} is required.`;
  if (trimmed.length > maxLength) return `${label} must be ${maxLength} characters or fewer.`;
  return undefined;
}

function positiveDecimal(value: string, label: string, maximum?: number): string | undefined {
  if (!value.trim()) return `${label} is required.`;
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0) return `${label} must be a number greater than 0.`;
  if (maximum !== undefined && number > maximum) return `${label} must be ${maximum} or less.`;
  return undefined;
}

export function validateDraft(draft: ReferenceDraft, panels: File[]): DraftErrors {
  const errors: DraftErrors = {};
  errors.brandName = required(draft.brandName, "Brand name", 160);
  errors.classType = required(draft.classType, "Class or type", 240);
  errors.abvPercent = positiveDecimal(draft.abvPercent, "Alcohol by volume", 100);
  if (draft.proof.trim()) {
    const proof = Number(draft.proof);
    if (!Number.isFinite(proof) || proof < 0) errors.proof = "Proof must be 0 or greater.";
  }
  errors.netContentsValue = positiveDecimal(draft.netContentsValue, "Net contents");
  errors.producerNameAddress = required(draft.producerNameAddress, "Producer name and address", 500);
  if (draft.caseLabel.length > 80) errors.caseLabel = "Case label must be 80 characters or fewer.";
  if (draft.isImported) errors.countryOfOrigin = required(draft.countryOfOrigin, "Country of origin", 80);

  if (panels.length < 1 || panels.length > MAX_PANELS) {
    errors.panels = "Add 1 to 6 label panels.";
  } else if (panels.some((file) => !ACCEPTED_IMAGE_TYPES.includes(file.type as (typeof ACCEPTED_IMAGE_TYPES)[number]))) {
    errors.panels = "Use JPEG, PNG, or WebP images only.";
  } else if (panels.some((file) => file.size > MAX_FILE_BYTES)) {
    errors.panels = "Each image must be 4 MiB or smaller.";
  } else if (panels.reduce((total, file) => total + file.size, 0) > MAX_AGGREGATE_BYTES) {
    errors.panels = "All images together must be 8 MiB or smaller.";
  }

  return Object.fromEntries(Object.entries(errors).filter(([, value]) => Boolean(value))) as DraftErrors;
}

export function toReference(draft: ReferenceDraft): ReferenceRecord {
  return {
    profileId,
    caseLabel: draft.caseLabel.trim() || null,
    brandName: draft.brandName.trim(),
    classType: draft.classType.trim(),
    abvPercent: Number(draft.abvPercent),
    proof: draft.proof.trim() ? Number(draft.proof) : null,
    netContentsValue: Number(draft.netContentsValue),
    netContentsUnit: draft.netContentsUnit,
    producerNameAddress: draft.producerNameAddress.trim(),
    isImported: draft.isImported,
    countryOfOrigin: draft.isImported ? draft.countryOfOrigin.trim() : null,
  };
}

export function draftHasContent(draft: ReferenceDraft): boolean {
  return Object.entries(draft).some(([key, value]) => {
    if (key === "netContentsUnit") return value !== "mL";
    if (key === "isImported") return value === true;
    return typeof value === "string" && value.length > 0;
  });
}
