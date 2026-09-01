import { internalError, parsePublicError, parseVerificationResult, ResponseContractError } from "../contracts/runtime";
import type { PublicError, VerificationClient, VerificationRequest } from "../contracts/types";

export class VerificationClientError extends Error {
  readonly detail: PublicError;

  constructor(detail: PublicError) {
    super(detail.message);
    this.name = "VerificationClientError";
    this.detail = detail;
  }
}

export function createVerificationClient(fetcher: typeof fetch = fetch): VerificationClient {
  return {
    async verify(request: VerificationRequest) {
      const body = new FormData();
      body.append("reference", JSON.stringify(request.reference));
      request.panels.forEach((panel) => body.append("panels", panel, panel.name));

      let response: Response;
      try {
        response = await fetcher("/api/v1/verifications", {
          method: "POST",
          body,
          signal: request.signal,
          headers: { Accept: "application/json" },
        });
      } catch (error) {
        if (request.signal.aborted) throw error;
        throw new VerificationClientError({
          requestId: "unavailable",
          code: "network_unavailable",
          message: "The verifier could not be reached.",
          retryable: true,
          nextAction: "Check your connection and retry",
          fieldOrPanel: null,
        });
      }

      let payload: unknown;
      try {
        payload = await response.json();
      } catch {
        throw new VerificationClientError(internalError());
      }

      if (!response.ok) {
        throw new VerificationClientError(parsePublicError(payload) ?? internalError());
      }

      try {
        return parseVerificationResult(payload);
      } catch (error) {
        if (error instanceof ResponseContractError) {
          throw new VerificationClientError({
            requestId: error.requestId,
            code: error.code,
            message: "No result was shown because the response could not be verified.",
            retryable: true,
            nextAction: "Retry and report the request ID if repeated",
            fieldOrPanel: null,
          });
        }
        throw new VerificationClientError(internalError());
      }
    },
  };
}
