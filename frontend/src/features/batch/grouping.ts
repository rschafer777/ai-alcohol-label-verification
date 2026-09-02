import type { AnalysisResult, VerificationResult } from "../../contracts/types";
import { limits } from "../../api/generated-contract";

export interface SuggestedGroup {
  id: string;
  name: string;
  files: File[];
  confirmed: boolean;
  reason: string;
  analysis: AnalysisResult | null;
  result: VerificationResult | null;
  status: "needs_confirmation" | "ready" | "queued" | "running" | "complete" | "failed" | "cancelled";
  durationMs: number | null;
  attempts: number;
  error: string | null;
}

const ROLE_WORDS = /(?:^|[-_.\s])(front|back|rear|neck|side|panel|label|left|right|photo|image|img)(?:[-_.\s]|$)/gi;
const SUPPORTED_IMAGE_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

export function imageSelectionIssue(files: File[], maximumCount: number): string | null {
  if (files.length > maximumCount) return `Choose no more than ${maximumCount} images.`;
  const unsupported = files.find((file) => !SUPPORTED_IMAGE_TYPES.has(file.type));
  if (unsupported) return `${unsupported.name} is not a JPEG, PNG, or WebP image.`;
  const oversized = files.find((file) => file.size > limits.fileBytes);
  if (oversized) return `${oversized.name} is larger than 4 MB.`;
  return null;
}

export function spreadsheetSafeCsvCell(value: unknown): string {
  const plain = String(value);
  const protectedValue = /^[\t\r\n ]*[=+\-@]/.test(plain) || /^[\t\r\n]/.test(plain)
    ? `'${plain}`
    : plain;
  return `"${protectedValue.replaceAll('"', '""')}"`;
}

export function canonicalPath(file: File): string {
  return ((file as File & { webkitRelativePath?: string }).webkitRelativePath || file.name).replaceAll("\\", "/");
}

function groupKey(file: File): string {
  const path = canonicalPath(file);
  const parts = path.split("/");
  if (parts.length > 2) return parts.slice(0, -1).join("/").toLocaleLowerCase("en-US");
  const stem = (parts.at(-1) ?? file.name).replace(/\.[^.]+$/, "");
  const normalized = stem.replace(ROLE_WORDS, " ").replace(/[-_.\s]+/g, " ").trim().toLocaleLowerCase("en-US");
  return normalized || stem.toLocaleLowerCase("en-US");
}

export function suggestProductGroups(files: File[]): SuggestedGroup[] {
  const buckets = new Map<string, File[]>();
  [...files]
    .sort((a, b) => canonicalPath(a).localeCompare(canonicalPath(b), "en-US"))
    .forEach((file) => {
      const key = groupKey(file);
      buckets.set(key, [...(buckets.get(key) ?? []), file]);
    });
  const groups: SuggestedGroup[] = [];
  let ordinal = 1;
  for (const [key, bucket] of buckets) {
    for (let offset = 0; offset < bucket.length; offset += 3) {
      const chunk = bucket.slice(offset, offset + 3);
      groups.push({
        id: `group-${ordinal}`,
        name: key.replace(/\b\w/g, (value) => value.toUpperCase()) || `Product ${ordinal}`,
        files: chunk,
        confirmed: false,
        reason: chunk.length > 1
          ? "Filename or folder cues suggest these images belong together."
          : "No safe matching image cue was found. Confirm this as a separate product.",
        analysis: null,
        result: null,
        status: "needs_confirmation",
        durationMs: null,
        attempts: 0,
        error: null,
      });
      ordinal += 1;
    }
  }
  return groups;
}
