# BAIRD Red Team 1: Architecture and Requirements Fidelity

## Verdict

**REWORK_REQUIRED**

The modular monolith, deterministic rule engine, evidence-first UI, no-database boundary, and no-external-inference direction are reasonable candidates. They cannot advance to I2R on this revision because five material findings remain.

## Review basis

Reviewed the complete CLEAR Intake, `README.md`, `AGENTS.md`, `docs/PROCESS.md`, and every file in `docs/baird`. Rechecked material platform and library claims against current primary sources, including the RapidOCR repository and documentation, PaddleOCR pipeline documentation, ONNX Runtime API documentation, FastAPI concurrency and deployment documentation, and Railway pricing, Serverless, and healthcheck documentation.

## Findings

### RT1-B-F001 - HIGH - Load-bearing Intake assumptions remain open after BAIRD

**Evidence**

- `docs/intake/assumptions.md:13-18` identifies `ASM-007` and `ASM-012` as load-bearing. Line 25 requires BAIRD to confirm or falsify both before architecture approval.
- `docs/PROCESS.md:12` requires BAIRD to benchmark load-bearing choices before the three CLEAR reviews.
- `docs/baird/BAIRD_ASSESSMENT.md:78-85` explicitly says the only OCR evidence is not an acceptance benchmark and is not representative of the deployment tier. It covers two very small crops on an Intel i9 workstation, not a complete 1-to-6-panel request, the maximum input envelope, a container, a target host, or the browser-visible path.
- The feasibility record does not identify the exact RapidOCR version, ONNX Runtime version, model names, model hashes, thread settings, peak RAM, or container resource limits, even though those values can materially change the result.
- `docs/baird/BAIRD_TRACEABILITY.md:42-45` moves `ASM-007` closure to a later release point and `ASM-012` closure to a later validation-plan point.
- At the same time, `docs/baird/I2R_HANDOFF.md:7-16` directs I2R to formalize RapidOCR/ONNX, the synchronous container, and Railway as the selected baseline.

**Impact**

BAIRD has selected an architecture before completing the evidence gate that the attested Intake and process require. A red team cannot determine that this architecture is feasible for the core five-second result or that the minimum fixture design is sufficient. I2R would turn provisional hypotheses into requirements.

**Required remediation**

1. Run a reproducible BAIRD feasibility spike before another BAIRD review. Record exact library versions, model IDs and hashes, container digest, CPU/RAM limits, preprocessing parameters, thread settings, input bytes/pixels/panel count, stage timings, peak RAM, and result coverage.
2. Exercise the selected OCR path on a deterministic representative set that includes single-panel, multi-panel, warning text, small label text, controlled degradation, and the proposed boundary envelope. Do not use the Grok/Gemini images as expected-outcome truth.
3. Run the resource-capped container on the proposed deployment class, or on an equivalent measured resource envelope, and establish a component budget that leaves explicit headroom for upload, transfer, render, and announcement inside the user-visible target.
4. Complete an independent fixture coverage and mutation review for the 24-submission minimum and six holdouts, then mark `ASM-012` confirmed or increase the corpus.
5. Record each load-bearing gate as PASS or FAIL. If a gate fails, select and test the fallback before I2R. Do not hand I2R a provisional technology baseline.

### RT1-B-F002 - HIGH - Warning capability and aggregation drift from the attested state machine

**Evidence**

- `docs/intake/source-requirements.md` defines warning emphasis as `SRC-028`, a Must with a capability limit and one of the four field states. `SRC-029` requires independent evaluation of the other supported presentation checks. `SRC-021` and `SRC-022` prohibit insufficient applicable evidence from becoming a clean result.
- `docs/intake/success-definition.md:17-19` requires each selected check to expose its state and states that insufficient format evidence produces Review or Not verified, never a clean result. Lines 46-49 require any applicable Review or Not verified to aggregate to Review needed.
- `docs/baird/BAIRD_ASSESSMENT.md:100-105` demotes heading emphasis, remaining-text emphasis, separation, and continuity to advisory observations and delegates the decision about which observations elevate the summary to the FRD.
- `docs/baird/ENGINEERING_BLUEPRINT.md:189-217` separates `advisory_observations[]` from `fields[]` without defining their state-machine or aggregation contract.
- `docs/baird/I2R_HANDOFF.md:49-60` explicitly lets I2R decide whether warning advisory observations elevate Review. That is decision authority the attested Intake has already resolved.

**Impact**

The current design can produce a clean submission while a committed warning-presentation check lacks sufficient evidence, depending on a later I2R choice. This violates the no-false-clean invariant and forces I2R to invent product behavior.

**Required remediation**

1. Define applicability, sufficient evidence, capability, state, reason, and aggregation treatment for every committed warning check in BAIRD.
2. For an applicable committed check, insufficient image evidence must produce Not verified or Review and therefore Review needed. A heuristic cannot issue Match unless its evidence standard is explicitly supported and tested.
3. If an observation is intentionally informational and non-aggregating, distinguish it from the committed selected checks and obtain scope change authority where required. Do not silently relabel a committed check as advisory.
4. Keep physical type-size automation outside scope as already attested, but disclose the limitation separately and do not let that limitation obscure the active state of the checks that are in scope.
5. Remove the aggregation decision from the list of matters I2R may refine.

### RT1-B-F003 - HIGH - The image, memory, concurrency, and host envelope is not finalized

**Evidence**

- `docs/intake/scope-boundary.md:18-24` makes the 8 MB, 24 megapixel, 24 MB submission envelope provisional and assigns final verification to BAIRD.
- `docs/baird/SECURITY_DATA_FLOW.md:51-58` carries the per-image and encoded limits forward but leaves the cumulative decoded-pixel cap undefined.
- `docs/baird/SECURITY_DATA_FLOW.md:100-111` labels concurrency and resource values provisional and sends exact values to I2R after load testing.
- `docs/baird/ENGINEERING_BLUEPRINT.md:244-265` does not specify whether panels are decoded and processed sequentially, how long decoded and derived buffers remain resident, or how per-request memory is released between panels.
- At 24 million pixels, one 3-channel 8-bit decoded image is about 72 MB before decoder overhead, preprocessing copies, OCR tensors, evidence crops, and the model. Six such panels are about 432 MB if resident together. Two concurrent jobs can exceed about 864 MB before the model and intermediate arrays. The current package contains no measured peak or safe bound.
- `docs/baird/ARCHITECTURE_DECISIONS.md:84-90` selects Railway while deferring the exact resource tier, region, memory, CPU, cost, and measured p95.

**Impact**

I2R cannot write binary upload, memory, overload, timeout, or deployment requirements without inventing critical values. The unresolved envelope also prevents meaningful latency, abuse-resistance, and cost conclusions.

**Required remediation**

1. Set a final cumulative decoded-pixel limit and a per-request working-memory budget based on measured peak use.
2. Specify panel decode/OCR ordering, buffer lifetime, downscale behavior, and the exact point at which an oversized request is rejected.
3. Set the measured global and per-request concurrency for the selected model and resource class. Account for ONNX Runtime intra-op and inter-op threads to avoid CPU oversubscription.
4. Select a minimum host CPU/RAM envelope, region, and cost ceiling for the preferred deployment. Record the corresponding fallback envelopes.
5. Boundary-test one-panel, six-panel, and concurrent requests. If the Intake envelope is not safe or cannot meet latency, reduce the provisional byte/pixel envelope now and update all affected BAIRD documents before I2R.

### RT1-B-F004 - HIGH - The performance and timeout contracts conflict

**Evidence**

- `docs/intake/success-definition.md:56-64` defines the primary metric from Verify activation through complete render and browser announcement, including client preprocessing, upload, server work, response transfer, and rendering. Warmed p95 must be at or below 5.0 seconds.
- `docs/baird/SECURITY_DATA_FLOW.md:100-111` gives the server a 5-second budget "inside the larger user-visible metric," but the user-visible metric has the same 5-second threshold and includes more work.
- `docs/baird/UX_PRODUCT_SPEC.md:35-47` says not to cancel a valid request at five seconds solely to satisfy the clock.
- `docs/baird/ENGINEERING_BLUEPRINT.md:191-217` defines only `total_duration_ms` and `stage_timings` in the server result, without identifying the clock domain. It cannot represent browser render and announcement that occur after the response.
- Proxy, application, inference, client abort, and valid-slow-outlier behavior are not assigned exact ordering or semantics.

**Impact**

I2R cannot derive one coherent binary performance contract. A literal implementation can either exceed the attested end-to-end target, cancel valid work contrary to the UX contract, or misreport server time as user-visible time.

**Required remediation**

1. Publish a latency budget across client validation/preprocessing, upload, queue, decode/OCR/rules, response transfer, render, and announcement. The sum must fit the 5.0-second warmed p95 target.
2. Name the clocks separately, such as server processing duration and browser user-visible duration. State that only the browser clock decides the release metric.
3. Define proxy, request, queue, OCR, and client timeouts in a consistent order and distinguish a p95 target from a hard timeout.
4. Define what happens to a valid request that exceeds five seconds and how that differs from a bounded inference failure. Preserve the separate Intake contract for degraded failures.
5. Update the API/result contract, UX text, security envelope, and benchmark method to use the same definitions.

### RT1-B-F005 - MEDIUM - The option comparison and fallbacks are not evidence-backed or fully executable

**Evidence**

- `docs/baird/BAIRD_ASSESSMENT.md:58-70` presents precise weighted scores without scoring anchors, uncertainty, measured resource data, or the same-workload comparison across candidates.
- Only RapidOCR was exercised, and only on the two small generated-image crops at lines 78-85. Full PaddleOCR, browser ONNX, Tesseract.js, and the deployment fallbacks were not measured on the same workload.
- `docs/baird/BAIRD_ASSESSMENT.md:174` and `docs/baird/ARCHITECTURE_DECISIONS.md:46-52` allow the fallback to "reduce claims" or narrow scope if OCR fails. The selected checks are attested scope, so narrowing them requires scope change control rather than an engineering fallback.
- `docs/baird/BAIRD_ASSESSMENT.md:109-117` labels Railway preferred before resource/cost proof. Current Railway documentation confirms that Serverless is optional and may return a 502 on wake when enabled, so disabling it is appropriate. Current Railway healthcheck documentation also states that the healthcheck is used at deployment start, not for continuous monitoring. The current deployment comparison does not record that limitation or define runtime monitoring and rollback triggers for the single-replica service.

**Impact**

The matrix communicates more certainty than its evidence supports, and some fallback paths cannot be taken without either new benchmarks or a scope decision. The deployment path also lacks an operationally explicit failure and rollback contract.

**Required remediation**

1. Define score anchors and minimum pass criteria, then run the plausible OCR candidates on the same versioned inputs and resource envelope. Report raw measurements and uncertainty before weighted scores.
2. Explain what additional accuracy is expected from full PaddleOCR versus the selected RapidOCR model family, then prove it on the same errors before naming it the accuracy fallback.
3. Replace "reduce claims" with an explicit stop: choose a tested alternative, or open scope change control with the requester. Core selected checks cannot be silently narrowed.
4. For Railway, Fly, and Azure, define trigger, configuration, minimum resources, cost estimate, readiness behavior, smoke test, rollback trigger, and rollback action. Note that Railway's deployment healthcheck is not continuous monitoring and provide a proportionate take-home runtime health strategy.
5. Update `BAIRD_TRACEABILITY.md` so every fallback has evidence, authority, and a closure point before I2R.

## Gate result

BAIRD remains open. I2R must not start until these findings are remediated and all three BAIRD reviewers return CLEAR on the same revision.
