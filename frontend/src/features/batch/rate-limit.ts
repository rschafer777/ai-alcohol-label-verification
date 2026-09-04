/* The API meters verification starts per client and per minute. A large batch of products,
   each answered in well under a second, reaches that limit; the run waits and tries the same
   product again rather than recording the metered refusal as a failure. */
export const RATE_LIMIT_CODES = new Set(["client_rate_limited", "global_start_rate_limited"]);
export const RATE_LIMIT_WAIT_MS = 2000;
export const RATE_LIMIT_MAX_WAITS = 45;

function rateLimitCode(error: unknown): boolean {
  if (typeof error !== "object" || error === null || !("detail" in error)) return false;
  const detail = (error as { detail?: { code?: unknown } }).detail;
  return typeof detail?.code === "string" && RATE_LIMIT_CODES.has(detail.code);
}

export async function analyzeWithinRateLimit<T>(attempt: () => Promise<T>, signal: AbortSignal, waitMs = RATE_LIMIT_WAIT_MS, maxWaits = RATE_LIMIT_MAX_WAITS): Promise<T> {
  for (let waits = 0; ; waits += 1) {
    try {
      return await attempt();
    } catch (error) {
      if (!rateLimitCode(error) || signal.aborted || waits >= maxWaits) throw error;
      await new Promise<void>((resolve) => {
        const timer = window.setTimeout(() => { signal.removeEventListener("abort", onAbort); resolve(); }, waitMs);
        const onAbort = () => { window.clearTimeout(timer); resolve(); };
        signal.addEventListener("abort", onAbort, { once: true });
      });
      if (signal.aborted) throw error;
    }
  }
}
