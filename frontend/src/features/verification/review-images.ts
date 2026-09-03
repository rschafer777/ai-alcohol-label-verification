export interface ReviewImage {
  src: string;
  name: string;
  alt: string;
  title: string;
}

export interface SlotUpload {
  slot: number;
  name: string;
  pct: number;
  stage: "Uploading…" | "Reading label…" | "Checking rules…";
}

export function slotTitle(index: number, count: number, added = false): string {
  if (added) return "Added evidence";
  if (count === 1) return "Front";
  return index === 0 ? "Front" : index === 1 ? "Back" : "Added evidence";
}
