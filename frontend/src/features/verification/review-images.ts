import type { Point } from "../../contracts/types";

export interface ReviewImage {
  src: string;
  name: string;
  alt: string;
  title: string;
}

export interface ManualEvidenceSelection {
  panelId: string;
  polygon: [Point, Point, Point, Point];
}

export interface SlotUpload {
  slot: number;
  name: string;
  pct: number;
  stage: "Uploading…" | "Reading label…" | "Checking rules…";
}

export function slotTitle(index: number, count: number, added = false): string {
  void count;
  void added;
  return `Image ${index + 1}`;
}
