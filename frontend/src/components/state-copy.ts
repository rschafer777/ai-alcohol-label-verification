import type { ReactNode } from "react";

import type { PublicError } from "../contracts/types";
import { icons } from "./icons";
import type { SemanticKind } from "./status";

/* One card per governed error code. Wording says what happened and the one next thing to do.
   Terminal errors use alert semantics; progress and status use polite live regions. */

export interface StateCardCopy {
  code: string;
  tag: string;
  kind: SemanticKind;
  title: string;
  body: string;
  meta: string;
  primary: string;
  secondary: string;
  role: "alert" | "status";
  icon: ReactNode;
}

const FAIL_TAGS = new Set(["Timed out", "Offline", "Rejected"]);

const CATALOG: Record<string, Omit<StateCardCopy, "code" | "kind" | "icon"> & { icon: keyof typeof icons }> = {
  image_unreadable: { tag: "Bad image", title: "We could not read this label", body: "Glare or blur covers the text we needed. Nothing was invented for the parts we could not read.", primary: "Retry with a clearer photo", secondary: "Open image", meta: "Result: Bad image · kept in history", role: "alert", icon: "imageOff" },
  type_low_confidence: { tag: "Ask", title: "Which type is this?", body: "We read the type with low confidence. The checks change with the type, so we ask instead of guessing.", primary: "Confirm type", secondary: "Show why", meta: "Blocks Verify until answered", role: "status", icon: "help" },
  client_deadline_exceeded: { tag: "Timed out", title: "This took longer than 35 seconds", body: "We stopped so you are not waiting on a spinner. Your images are still selected.", primary: "Try again", secondary: "Check by eye", meta: "No result was issued", role: "alert", icon: "clock" },
  request_deadline_exceeded: { tag: "Timed out", title: "The verifier stopped at its deadline", body: "The read did not finish in time. Your images are still selected.", primary: "Try again", secondary: "Check by eye", meta: "No result was issued", role: "alert", icon: "clock" },
  inference_timeout: { tag: "Timed out", title: "Reading the label took too long", body: "OCR did not finish within its budget. A tighter crop or a smaller image usually helps.", primary: "Try again", secondary: "Check by eye", meta: "No result was issued", role: "alert", icon: "clock" },
  verification_capacity_busy: { tag: "Busy", title: "Another label is being read", body: "The prototype reads one label at a time. Yours will start as soon as it is free, usually a few seconds.", primary: "Wait in line", secondary: "Cancel", meta: "Auto-retries; no action needed", role: "status", icon: "clock" },
  worker_queue_busy: { tag: "Busy", title: "Another label is being read", body: "The prototype reads one label at a time. Yours will start as soon as it is free, usually a few seconds.", primary: "Wait in line", secondary: "Cancel", meta: "Auto-retries; no action needed", role: "status", icon: "clock" },
  network_unavailable: { tag: "Offline", title: "The verifier cannot be reached", body: "Nothing was sent. Check the connection, then retry. You can still open the image and check by eye.", primary: "Retry", secondary: "Open image", meta: "Degraded: lightbox and empty checklist", role: "alert", icon: "alert" },
  request_too_large: { tag: "Rejected", title: "One image is over 4 MB", body: "Shrink it or take a smaller photo; three images together must stay under 12 MB.", primary: "Choose another image", secondary: "Remove it", meta: "Points at the exact file", role: "alert", icon: "image" },
  payload_too_large: { tag: "Rejected", title: "One image is over 4 MB", body: "Shrink it or take a smaller photo; three images together must stay under 12 MB.", primary: "Choose another image", secondary: "Remove it", meta: "Points at the exact file", role: "alert", icon: "image" },
  unsupported_media_type: { tag: "Rejected", title: "That file is not a supported image", body: "Use a JPEG, PNG or WebP photo of the label.", primary: "Choose another image", secondary: "Remove it", meta: "Points at the exact file", role: "alert", icon: "image" },
  invalid_image: { tag: "Rejected", title: "That image could not be decoded", body: "The file is damaged or is not really an image. Re-export it and try again.", primary: "Choose another image", secondary: "Remove it", meta: "Points at the exact file", role: "alert", icon: "image" },
  decoded_pixel_limit: { tag: "Rejected", title: "This image has too many decoded pixels", body: "The table shows the submitted dimensions, supported limit and exact resize target.", primary: "Choose resized image", secondary: "Start over", meta: "No result was issued", role: "alert", icon: "image" },
  batch_partial_failure: { tag: "Isolated", title: "Some products failed", body: "The other products finished and are already in History. Retry makes a new attempt and keeps the old one.", primary: "Retry failed", secondary: "Export anyway", meta: "Batch: completed with errors", role: "status", icon: "alert" },
  history_empty: { tag: "Empty", title: "No completed checks yet", body: "When you finish a check it appears here: the images, every finding with its evidence region, and your disposition.", primary: "Check one label", secondary: "Check a batch", meta: "0 of 500", role: "status", icon: "clock" },
  not_ready: { tag: "Busy", title: "The verifier is still starting", body: "The OCR worker is warming up. This usually takes a few seconds.", primary: "Try again", secondary: "Cancel", meta: "Auto-retries; no action needed", role: "status", icon: "clock" },
  cancelled: { tag: "Cancelled", title: "You stopped this read", body: "Nothing was recorded. Your images are still selected.", primary: "Read again", secondary: "Start over", meta: "No result was issued", role: "status", icon: "clock" },
};

export function stateCopy(error: PublicError): StateCardCopy {
  const entry = CATALOG[error.code];
  if (!entry) {
    return { code: error.code, tag: "Error", kind: "warn", title: "We could not finish this label", body: error.message, meta: `Request ${error.requestId}`, primary: error.retryable ? "Try again" : "Start over", secondary: "Start over", role: "alert", icon: icons.alert() };
  }
  const kind: SemanticKind = entry.role === "alert" ? (FAIL_TAGS.has(entry.tag) ? "fail" : "warn") : "info";
  const body = error.fieldOrPanel && (error.code === "request_too_large" || error.code === "unsupported_media_type" || error.code === "invalid_image") ? `${error.fieldOrPanel}: ${entry.body}` : entry.body;
  return { code: error.code, kind, title: entry.title, body, tag: entry.tag, meta: entry.meta, primary: entry.primary, secondary: entry.secondary, role: entry.role, icon: icons[entry.icon]() };
}
