import { z } from "zod";

import errorRegistryJson from "../../../contracts/error-registry-v1.json";
import { checkIds, profileId } from "../api/generated-contract";

import type { PublicError, VerificationResult } from "./types";

const pointSchema = z.object({ x: z.number().int().nonnegative(), y: z.number().int().nonnegative() }).strict();

const evidenceSchema = z
  .object({
    evidenceId: z.string().regex(/^ev_[a-z0-9_-]+$/),
    panelId: z.string().regex(/^panel-[1-6]$/),
    polygonOriginalPixels: z.array(pointSchema).length(4),
    sourceView: z.enum(["original", "derived"]),
    transformId: z.string().min(1),
    textSnippet: z.string().nullable().optional(),
    confidenceProvenance: z
      .object({
        source: z.string().min(1),
        signal: z.number().nullable(),
        calibratedProbability: z.literal(false),
      })
      .passthrough(),
  })
  .strict();

const checkSchema = z
  .object({
    checkId: z.enum(checkIds),
    label: z.string().min(1),
    applicable: z.boolean(),
    referenceDisplay: z.string().nullable().optional(),
    observedDisplay: z.string().nullable().optional(),
    state: z.enum(["Match", "Mismatch", "Review", "Not verified"]),
    reasonCode: z.string().min(1),
    reasonText: z.string().min(1),
    evidenceRef: z.string().nullable().optional(),
    alternatives: z.array(
      z.object({ value: z.string().min(1), evidenceRef: z.string().min(1) }).strict(),
    ),
    capability: z.string().min(1),
    policyVersion: z.string().min(1),
  })
  .strict();

const resultSchema = z
  .object({
    requestId: z.string().min(1),
    buildId: z.string().min(1),
    profileId: z.literal(profileId),
    profileVersion: z.string().min(1),
    modelIdentity: z.string().min(1),
    ruleSources: z.array(z.string()),
    serverDurationMs: z.number().nonnegative(),
    stageTimings: z.record(z.string(), z.number().nonnegative()),
    panels: z.array(
      z
        .object({
          panelId: z.string().regex(/^panel-[1-6]$/),
          originalDimensions: z
            .object({ width: z.number().int().positive(), height: z.number().int().positive() })
            .strict(),
          qualitySignals: z.record(
            z.string(),
            z.union([z.number(), z.boolean(), z.string(), z.null()]),
          ),
          coverageState: z.string(),
        })
        .passthrough(),
    ),
    evidence: z.array(evidenceSchema),
    checks: z.array(checkSchema),
    limitations: z.array(z.string()),
    summary: z.enum([
      "No differences found in checked fields",
      "Review needed",
      "Differences detected",
    ]),
  })
  .passthrough();

const publicErrorSchema = z
  .object({
    requestId: z.string().min(1),
    code: z.string().min(1),
    message: z.string().min(1),
    fieldOrPanel: z.string().nullable().optional(),
    retryable: z.boolean(),
    nextAction: z.string().min(1),
  })
  .strict();

const errorRegistrySchema = z.object({
  errors: z.array(
    z.object({
      code: z.string(),
      retryable: z.boolean(),
      action: z.string(),
      locatorAllowed: z.boolean().optional(),
    }),
  ),
  browserOnly: z.array(z.string()),
});

const errorRegistry = errorRegistrySchema.parse(errorRegistryJson);

export const SELECTED_CHECK_IDS = [...checkIds];
export const KNOWN_ERROR_CODES = [
  ...errorRegistry.errors.map((error) => error.code),
  ...errorRegistry.browserOnly,
] as const;

const errorByCode = new Map(errorRegistry.errors.map((error) => [error.code, error]));

function hasDuplicates(values: string[]): boolean {
  return new Set(values).size !== values.length;
}

function polygonKey(evidence: { panelId: string; polygonOriginalPixels: Array<{ x: number; y: number }> }): string {
  return `${evidence.panelId}:${evidence.polygonOriginalPixels.map((point) => `${point.x},${point.y}`).join(";")}`;
}

function validatePolygon(
  polygon: Array<{ x: number; y: number }>,
  width: number,
  height: number,
): boolean {
  if (polygon.some((point) => point.x >= width || point.y >= height)) return false;

  const first = polygon[0];
  if (!first) return false;
  const expectedFirst = [...polygon].sort((a, b) => a.y - b.y || a.x - b.x)[0];
  if (!expectedFirst || expectedFirst.x !== first.x || expectedFirst.y !== first.y) return false;

  let signedArea = 0;
  for (let index = 0; index < polygon.length; index += 1) {
    const current = polygon[index];
    const next = polygon[(index + 1) % polygon.length];
    if (!current || !next) return false;
    signedArea += current.x * next.y - next.x * current.y;
  }
  return signedArea > 0;
}

export class ResponseContractError extends Error {
  readonly code = "response_contract_invalid";
  readonly requestId: string;

  constructor(message: string, requestId = "unavailable") {
    super(message);
    this.name = "ResponseContractError";
    this.requestId = requestId;
  }
}

export function parseVerificationResult(value: unknown): VerificationResult {
  const parsed = resultSchema.safeParse(value);
  if (!parsed.success) throw new ResponseContractError("The verification response was incomplete or invalid.");

  const result = parsed.data;
  const panelIds = result.panels.map((panel) => panel.panelId);
  const evidenceIds = result.evidence.map((evidence) => evidence.evidenceId);
  const checkIds = result.checks.map((check) => check.checkId);

  if (hasDuplicates(panelIds) || hasDuplicates(evidenceIds) || hasDuplicates(checkIds)) {
    throw new ResponseContractError("The verification response contained duplicate identifiers.", result.requestId);
  }

  if (
    checkIds.length !== SELECTED_CHECK_IDS.length ||
    SELECTED_CHECK_IDS.some((checkId) => !checkIds.includes(checkId))
  ) {
    throw new ResponseContractError("The verification response did not contain every selected check.", result.requestId);
  }

  const panels = new Map(result.panels.map((panel) => [panel.panelId, panel]));
  const evidence = new Map(result.evidence.map((item) => [item.evidenceId, item]));

  for (const item of result.evidence) {
    const panel = panels.get(item.panelId);
    if (
      !panel ||
      !validatePolygon(
        item.polygonOriginalPixels,
        panel.originalDimensions.width,
        panel.originalDimensions.height,
      )
    ) {
      throw new ResponseContractError("The verification response contained invalid evidence coordinates.", result.requestId);
    }
  }

  for (const check of result.checks) {
    if (check.evidenceRef && !evidence.has(check.evidenceRef)) {
      throw new ResponseContractError("The verification response referenced missing evidence.", result.requestId);
    }

    const alternativeRefs = check.alternatives.map((alternative) => alternative.evidenceRef);
    if (hasDuplicates(alternativeRefs)) {
      throw new ResponseContractError("An ambiguous result reused the same evidence.", result.requestId);
    }
    const alternativePolygons = alternativeRefs.map((reference) => {
      const item = evidence.get(reference);
      if (!item) {
        throw new ResponseContractError("An ambiguous result referenced missing evidence.", result.requestId);
      }
      return polygonKey(item);
    });
    if (hasDuplicates(alternativePolygons)) {
      throw new ResponseContractError("Ambiguous values did not have distinct source regions.", result.requestId);
    }
  }

  return result as unknown as VerificationResult;
}

export function parsePublicError(value: unknown): PublicError | null {
  const parsed = publicErrorSchema.safeParse(value);
  if (!parsed.success) return null;
  const registered = errorByCode.get(parsed.data.code);
  if (!registered) return null;
  return {
    ...parsed.data,
    retryable: registered.retryable,
    nextAction: registered.action,
    fieldOrPanel: registered.locatorAllowed ? parsed.data.fieldOrPanel : null,
  };
}

export function internalError(requestId = "unavailable"): PublicError {
  const registered = errorByCode.get("internal_error");
  return {
    requestId,
    code: "internal_error",
    message: "We could not complete this verification.",
    retryable: true,
    nextAction: registered?.action ?? "Retry and report the request ID if repeated",
    fieldOrPanel: null,
  };
}
