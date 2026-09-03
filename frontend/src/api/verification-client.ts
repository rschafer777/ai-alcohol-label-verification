import { internalError, parseAnalysisResult, parseGroupingResult, parsePublicError, parseVerificationResult, ResponseContractError } from "../contracts/runtime";
import type {
  AddPanelRequest,
  AnalysisRequest,
  GroupingRequest,
  GroupingResult,
  PublicError,
  UploadProgress,
  VerificationClient,
  VerificationRequest,
} from "../contracts/types";

export class VerificationClientError extends Error {
  readonly detail: PublicError;

  constructor(detail: PublicError) {
    super(detail.message);
    this.name = "VerificationClientError";
    this.detail = detail;
  }
}

function networkError(): VerificationClientError {
  return new VerificationClientError({
    requestId: "unavailable",
    code: "network_unavailable",
    message: "The verifier could not be reached.",
    retryable: true,
    nextAction: "Check your connection and retry",
    fieldOrPanel: null,
  });
}

function contractError(error: unknown, subject: string): VerificationClientError {
  if (error instanceof ResponseContractError) {
    return new VerificationClientError({
      requestId: error.requestId,
      code: error.code,
      message: `No ${subject} were shown because the response could not be verified.`,
      retryable: true,
      nextAction: "Retry and report the request ID if repeated",
      fieldOrPanel: null,
    });
  }
  return new VerificationClientError(internalError());
}

interface RawResponse {
  ok: boolean;
  payload: unknown;
}

/** Multipart POST through XMLHttpRequest so the UI can show real upload progress (REQ-2). */
function postMultipart(url: string, body: FormData, signal: AbortSignal, onUploadProgress?: (progress: UploadProgress) => void): Promise<RawResponse> {
  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", url);
    request.responseType = "text";
    request.setRequestHeader("Accept", "application/json");
    const abort = () => {
      request.abort();
      reject(signal.reason instanceof Error ? signal.reason : new DOMException("Aborted", "AbortError"));
    };
    if (signal.aborted) {
      abort();
      return;
    }
    signal.addEventListener("abort", abort, { once: true });
    request.upload.onprogress = (event) => {
      if (onUploadProgress && event.lengthComputable) onUploadProgress({ loaded: event.loaded, total: event.total });
    };
    request.onerror = () => {
      signal.removeEventListener("abort", abort);
      reject(networkError());
    };
    request.onload = () => {
      signal.removeEventListener("abort", abort);
      let payload: unknown;
      try {
        payload = JSON.parse(request.responseText);
      } catch {
        reject(new VerificationClientError(internalError()));
        return;
      }
      resolve({ ok: request.status >= 200 && request.status < 300, payload });
    };
    request.send(body);
  });
}

async function postMultipartWithFetch(fetcher: typeof fetch, url: string, body: FormData, signal: AbortSignal): Promise<RawResponse> {
  let response: Response;
  try {
    response = await fetcher(url, { method: "POST", body, signal, headers: { Accept: "application/json" } });
  } catch (error) {
    if (signal.aborted) throw error;
    throw networkError();
  }
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new VerificationClientError(internalError());
  }
  return { ok: response.ok, payload };
}

export function createVerificationClient(fetcher: typeof fetch = fetch, transport: "xhr" | "fetch" = typeof XMLHttpRequest === "undefined" ? "fetch" : "xhr"): VerificationClient {
  async function post(url: string, body: FormData, signal: AbortSignal, onUploadProgress?: (progress: UploadProgress) => void): Promise<RawResponse> {
    if (transport === "xhr") return postMultipart(url, body, signal, onUploadProgress);
    return postMultipartWithFetch(fetcher, url, body, signal);
  }

  return {
    async analyze(request: AnalysisRequest) {
      const body = new FormData();
      request.panels.forEach((panel) => body.append("panels", panel, panel.name));
      const url = request.persist === false ? "/api/v1/analyses?persist=false" : "/api/v1/analyses";
      const response = await post(url, body, request.signal, request.onUploadProgress);
      if (!response.ok) throw new VerificationClientError(parsePublicError(response.payload) ?? internalError());
      try {
        return parseAnalysisResult(response.payload);
      } catch (error) {
        throw contractError(error, "detected values");
      }
    },
    async addPanel(request: AddPanelRequest) {
      const body = new FormData();
      body.append("panels", request.panel, request.panel.name);
      const response = await post(`/api/v1/history/${encodeURIComponent(request.historyId)}/panels`, body, request.signal, request.onUploadProgress);
      if (!response.ok) throw new VerificationClientError(parsePublicError(response.payload) ?? internalError());
      try {
        return parseAnalysisResult(response.payload);
      } catch (error) {
        throw contractError(error, "detected values");
      }
    },
    async verify(request: VerificationRequest) {
      const body = new FormData();
      body.append("reference", JSON.stringify(request.reference));
      request.panels.forEach((panel) => body.append("panels", panel, panel.name));
      const response = await postMultipartWithFetch(fetcher, "/api/v1/verifications", body, request.signal);
      if (!response.ok) throw new VerificationClientError(parsePublicError(response.payload) ?? internalError());
      try {
        return parseVerificationResult(response.payload);
      } catch (error) {
        throw contractError(error, "results");
      }
    },
    async suggestGroups(request: GroupingRequest): Promise<GroupingResult> {
      let response: Response;
      try {
        response = await fetcher("/api/v1/grouping-suggestions", {
          method: "POST",
          body: JSON.stringify({ images: request.images }),
          signal: request.signal,
          headers: { Accept: "application/json", "Content-Type": "application/json" },
        });
      } catch (error) {
        if (request.signal?.aborted) throw error;
        throw networkError();
      }
      let payload: unknown;
      try {
        payload = await response.json();
      } catch {
        throw new VerificationClientError(internalError());
      }
      if (!response.ok) throw new VerificationClientError(parsePublicError(payload) ?? internalError());
      try {
        return parseGroupingResult(payload);
      } catch (error) {
        throw contractError(error, "grouping suggestions");
      }
    },
  };
}
