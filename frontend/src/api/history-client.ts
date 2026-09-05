import { parseVerificationResult } from "../contracts/runtime";
import type { CorrectionRequest, HistoryDetail, HistoryPage, MetaResponse, VerificationResult } from "../contracts/types";

export type CorrectionPayload = CorrectionRequest;

export interface HistoryFilters {
  beverageType?: string;
  summary?: string;
  disposition?: string;
  q?: string;
}

export interface HistoryClient {
  meta(): Promise<MetaResponse | null>;
  list(options: HistoryFilters & { offset?: number; pageSize?: number }): Promise<HistoryPage>;
  get(id: string): Promise<HistoryDetail | null>;
  setDisposition(id: string, disposition: string | null, reviewerNote: string): Promise<boolean>;
  correct?(id: string, payload: CorrectionPayload): Promise<VerificationResult>;
  remove(id: string): Promise<boolean>;
  clear(): Promise<number>;
}

export function createHistoryClient(fetcher: typeof fetch = fetch): HistoryClient {
  const json = { Accept: "application/json" };
  return {
    async meta() {
      try {
        const response = await fetcher("/api/v1/meta", { headers: json });
        if (!response.ok) return null;
        return (await response.json()) as MetaResponse;
      } catch {
        return null;
      }
    },
    async list(options) {
      const params = new URLSearchParams({ pageSize: String(options.pageSize ?? 25), offset: String(options.offset ?? 0) });
      if (options.beverageType) params.set("beverageType", options.beverageType);
      if (options.summary) params.set("summary", options.summary);
      if (options.disposition) params.set("disposition", options.disposition);
      if (options.q?.trim()) params.set("q", options.q.trim());
      const response = await fetcher(`/api/v1/history?${params}`, { headers: json });
      if (!response.ok) throw new Error("History could not be loaded.");
      return (await response.json()) as HistoryPage;
    },
    async get(id) {
      const response = await fetcher(`/api/v1/history/${encodeURIComponent(id)}`, { headers: json });
      if (!response.ok) return null;
      return (await response.json()) as HistoryDetail;
    },
    async setDisposition(id, disposition, reviewerNote) {
      const response = await fetcher(`/api/v1/history/${encodeURIComponent(id)}/disposition`, {
        method: "PATCH",
        headers: { ...json, "Content-Type": "application/json" },
        body: JSON.stringify({ disposition, reviewerNote }),
      });
      return response.ok;
    },
    async correct(id, payload) {
      const response = await fetcher(`/api/v1/history/${encodeURIComponent(id)}/corrections`, {
        method: "POST",
        headers: { ...json, "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        const error = (await response.json().catch(() => null)) as { message?: string; nextAction?: string } | null;
        throw new Error([error?.message, error?.nextAction].filter(Boolean).join(" ") || "The correction could not be saved.");
      }
      const envelope = (await response.json()) as { result?: unknown };
      return parseVerificationResult(envelope.result);
    },
    async remove(id) {
      const response = await fetcher(`/api/v1/history/${encodeURIComponent(id)}`, { method: "DELETE", headers: json });
      return response.ok;
    },
    async clear() {
      const response = await fetcher("/api/v1/history", { method: "DELETE", headers: json });
      if (!response.ok) return 0;
      const payload = (await response.json()) as { deleted?: number };
      return payload.deleted ?? 0;
    },
  };
}
