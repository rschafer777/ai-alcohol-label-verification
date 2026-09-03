import type { Disposition, MachineSummary } from "../../components/status";
import type { AnalysisResult, BeverageType, GroupSuggestion, PublicError, VerificationResult } from "../../contracts/types";

/* Batch state is client-orchestrated (one product at a time through the same analysis endpoint
   the single flow uses). The BatchProgress shape mirrors the handoff's REQ-16 object so the run
   screen displays counts and timing rather than deriving them in the render path. */

export type BatchStage = "selecting" | "analyzing" | "grouping" | "confirmation" | "queued" | "running" | "completed" | "completed_with_errors" | "cancelled";
export type GroupStatus = "ready" | "needs_confirmation" | "conflict";
export type RunStatus = "idle" | "queued" | "running" | "complete" | "failed" | "cancelled";

export interface BatchImage {
  id: string;
  file: File;
  url: string;
  path: string;
}

export interface BatchGroup {
  id: string;
  name: string;
  imageIds: string[];
  status: GroupStatus;
  confirmed: boolean;
  reasons: string[];
  inferredType: BeverageType | null;
  confidence: "high" | "medium" | "low";
  runStatus: RunStatus;
  analysis: AnalysisResult | null;
  result: VerificationResult | null;
  error: PublicError | null;
  attempts: number;
  durationMs: number | null;
  disposition: Disposition;
  note: string;
}

export interface BatchProgress {
  state: BatchStage;
  counts: { total: number; remaining: number; queued: number; running: number; complete: number; review: number; difference: number; badImage: number; failed: number; cancelled: number; images: number };
  current: { productId: string; stage: string } | null;
  timing: { activeMs: number; lastProductMs: number | null; averageMs: number | null; etaMs: number | null };
  retries: number;
}

export function groupFromSuggestion(suggestion: GroupSuggestion): BatchGroup {
  const status: GroupStatus = suggestion.conflict ? "conflict" : suggestion.status === "ready_to_confirm" ? "ready" : "needs_confirmation";
  return {
    id: suggestion.groupId,
    name: suggestion.suggestedName,
    imageIds: [...suggestion.panelIds],
    status,
    confirmed: false,
    reasons: suggestion.reasons,
    inferredType: suggestion.inferredType ?? null,
    confidence: suggestion.confidence,
    runStatus: "idle",
    analysis: null,
    result: null,
    error: null,
    attempts: 0,
    durationMs: null,
    disposition: null,
    note: "",
  };
}

let ordinal = 0;
export function newGroupId(): string {
  ordinal += 1;
  return `group-local-${ordinal}`;
}

function touched(group: BatchGroup, reason: string): BatchGroup {
  return { ...group, confirmed: false, status: group.imageIds.length > 3 ? "conflict" : "needs_confirmation", reasons: [reason] };
}

/** Move one image into another group (or a new group when target is null). Empty groups vanish. */
export function moveImage(groups: BatchGroup[], imageId: string, targetId: string | null): BatchGroup[] {
  const source = groups.find((group) => group.imageIds.includes(imageId));
  if (!source) return groups;
  if (targetId === source.id) return groups;
  const target = targetId ? groups.find((group) => group.id === targetId) : null;
  if (targetId && !target) return groups;
  if (target && target.imageIds.length >= 3) return groups;
  let next = groups.map((group) => {
    if (group.id === source.id) return touched({ ...group, imageIds: group.imageIds.filter((id) => id !== imageId) }, "Edited: confirm this product again");
    if (target && group.id === target.id) return touched({ ...group, imageIds: [...group.imageIds, imageId] }, "Edited: confirm this product again");
    return group;
  }).filter((group) => group.imageIds.length > 0);
  if (!target) {
    next = [...next, { ...touched({ ...source, id: newGroupId(), imageIds: [imageId], name: `Product ${next.length + 1}` }, "Split out: confirm as a separate product") }];
  }
  return next;
}

export function mergeGroups(groups: BatchGroup[], ids: string[]): BatchGroup[] {
  const selected = groups.filter((group) => ids.includes(group.id));
  if (selected.length < 2) return groups;
  const imageIds = selected.flatMap((group) => group.imageIds);
  if (imageIds.length > 3) return groups;
  const first = selected[0];
  if (!first) return groups;
  const merged = touched({ ...first, imageIds }, "Merged: confirm this product again");
  return groups.flatMap((group) => group.id === first.id ? [merged] : ids.includes(group.id) ? [] : [group]);
}

export function splitGroup(groups: BatchGroup[], id: string): BatchGroup[] {
  const group = groups.find((item) => item.id === id);
  if (!group || group.imageIds.length < 2) return groups;
  const parts = group.imageIds.map((imageId, index) => touched({ ...group, id: index === 0 ? group.id : newGroupId(), imageIds: [imageId], name: index === 0 ? group.name : `${group.name} ${index + 1}` }, "Split: confirm as a separate product"));
  return groups.flatMap((item) => item.id === id ? parts : [item]);
}

export function confirmGroup(groups: BatchGroup[], id: string): BatchGroup[] {
  return groups.map((group) => group.id === id && group.imageIds.length <= 3 ? { ...group, confirmed: true, status: "ready" } : group);
}

export function confirmAllReady(groups: BatchGroup[]): BatchGroup[] {
  return groups.map((group) => group.status === "ready" ? { ...group, confirmed: true } : group);
}

/** Accept the suggested grouping of every unconfirmed product except conflicts, which need a
    person to split them or confirm them anyway on the card, and over-full groups. */
export function confirmAllPending(groups: BatchGroup[]): BatchGroup[] {
  return groups.map((group) => !group.confirmed && group.status !== "conflict" && group.imageIds.length <= 3 ? { ...group, confirmed: true, status: "ready" } : group);
}

export function renameGroup(groups: BatchGroup[], id: string, name: string): BatchGroup[] {
  return groups.map((group) => group.id === id ? { ...group, name } : group);
}

export function summaryOf(group: BatchGroup): MachineSummary | null {
  if (group.runStatus === "running") return "Running";
  if (group.runStatus === "queued") return "Queued";
  if (group.runStatus === "failed") return "Failed";
  if (group.runStatus === "cancelled") return "Cancelled";
  if (group.result?.badImage) return "Bad image";
  return group.result?.summary ?? null;
}

export function isException(group: BatchGroup): boolean {
  if (group.runStatus === "failed") return true;
  if (!group.result) return false;
  return group.result.badImage === true || group.result.summary !== "No differences found in checked fields";
}

export function batchProgress(groups: BatchGroup[], images: number, stage: BatchStage, activeMs: number, retries: number): BatchProgress {
  const counts = { total: groups.length, remaining: 0, queued: 0, running: 0, complete: 0, review: 0, difference: 0, badImage: 0, failed: 0, cancelled: 0, images };
  let current: BatchProgress["current"] = null;
  const durations: number[] = [];
  for (const group of groups) {
    if (group.runStatus === "queued") { counts.queued += 1; counts.remaining += 1; }
    else if (group.runStatus === "running") { counts.running += 1; counts.remaining += 1; current = { productId: group.id, stage: "Reading label" }; }
    else if (group.runStatus === "failed") counts.failed += 1;
    else if (group.runStatus === "cancelled") counts.cancelled += 1;
    else if (group.runStatus === "complete") {
      counts.complete += 1;
      if (group.result?.badImage) counts.badImage += 1;
      else if (group.result?.summary === "Review needed") counts.review += 1;
      else if (group.result?.summary === "Differences detected") counts.difference += 1;
    }
    if (group.durationMs != null && group.runStatus === "complete") durations.push(group.durationMs);
  }
  const averageMs = durations.length ? durations.reduce((sum, value) => sum + value, 0) / durations.length : null;
  const etaMs = durations.length >= 3 && averageMs !== null ? counts.remaining * averageMs : null;
  return { state: stage, counts, current, timing: { activeMs, lastProductMs: durations.at(-1) ?? null, averageMs, etaMs }, retries };
}
