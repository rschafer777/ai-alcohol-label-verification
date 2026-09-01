# Success Definition

**Status:** ATTESTED through `DEC-003`  
**Human outcome:** A compliance agent can complete routine first-pass comparison materially faster, inspect the evidence, and reserve judgment for genuine ambiguity or unsupported checks.

## Who experiences the outcome

- Primary: label-compliance agent with any level of technical comfort.
- Secondary: team lead evaluating whether the prototype could reduce routine review burden.
- Take-home evaluator: reviewer assessing correctness, code quality, technical judgment, UX, error handling, and attention to requirements.

## Observable user evidence

1. A first-time evaluator reaches one obvious verification path from the landing page.
2. The evaluator can choose Try sample and receive a complete synthetic reference record and label-panel set without preparing test data.
3. The evaluator can instead enter a supported reference record and upload 1 to 6 panel images without external instructions.
4. Each selected check shows the expected value when applicable, extracted evidence, evidence location or explicit unavailability, state, and plain reason.
5. Capitalization variation is distinguished from exact match and definite mismatch. Any field-specific punctuation handling is documented as a reconstructed policy and remains Review unless evidence supports a safer rule.
6. Missing panels, unreadable regions, insufficient format evidence, and low-confidence extraction produce Review or Not verified, never a clean result.
7. Invalid or unsupported input produces an actionable error without a crash or blank screen.
8. The repository runs from a clean checkout using only the README.

## Fixture and correctness contract

The committed validation corpus contains at least 24 end-to-end synthetic submissions. At least 6 are holdout fixtures that are not used while tuning extraction, normalization, or rules. Scenario categories may overlap, but the manifest must include all of the following:

- clean exact matches;
- safe normalized variations;
- deterministic mismatches for each core comparison family;
- missing required value;
- missing or wrong panel evidence;
- unreadable region and bounded blur, glare, lighting, rotation, or perspective degradation;
- prescribed warning text mutation;
- warning heading capitalization failure;
- warning typography or physical-size uncertainty;
- 1-image and multi-panel submissions;
- invalid file, spoofed type, corrupt image, oversize image, and decompression/resource-boundary failures;
- inference timeout or failure when an inference adapter exists.

Canonical label text is authored deterministically before visual rendering or controlled degradation. Generated images are never trusted as the source of expected text. Expected outcomes live in a versioned manifest separate from implementation constants. The validation report shows every fixture and field outcome without claiming production accuracy.

Deterministic comparison logic also has independent unit tests for each normalization rule and aggregation branch. Extraction tests and comparison tests are separate so a hard-coded fixture map cannot satisfy the release gate.

## Submission aggregation contract

1. Any field-level Mismatch yields Differences detected.
2. Otherwise, any Review or Not verified yields Review needed.
3. No differences found in checked fields is allowed only when every applicable selected check has sufficient evidence and resolves to Match.
4. A missing panel or unperformed applicable check prevents a clean summary.
5. A reviewer may add a separate session-only disposition or note, but the original system evidence and states remain unchanged.

## Latency contract

### Valid supported submissions

Valid benchmark submissions must return a complete field-level result. A timeout or actionable failure never counts as successful completion.

- Primary user-perceived measurement begins when the user activates Verify with locally valid inputs and ends when the complete field-level result is rendered and announced in the browser. It includes client preprocessing, upload, server validation, extraction, comparison, response transfer, and result rendering.
- Server acceptance-to-response timing is recorded as a diagnostic sub-measurement and cannot replace the user-perceived release metric.
- The deployed warmed-path p95 must be at or below 5.0 seconds over at least 30 runs.
- The 30-run set includes every benchmark fixture at least once, at least one multi-panel fixture, and at least 5 fresh browser sessions.
- The benchmark is one predeclared set of at least 30 valid attempts. It reports attempt count, complete-result count, completion rate, timeout count, error count, each duration, and p95 over complete results. Release requires 100 percent complete results on that fixed set. Timed-out attempts cannot be retried out of the denominator.
- Benchmark fixtures stay within the published byte, pixel, panel-count, and field envelope.
- Server region, client region, hardware tier, model/provider version, cache state, concurrency, bytes, pixels, panel count, and each run duration are recorded.
- No fixture-specific result cache or hard-coded expected result may satisfy the measurement.

### Initial-load and cold-start behavior

- Public load-to-interactive p95 target is at or below 3.0 seconds over at least 5 clean-browser loads in the documented evaluator region.
- Process cold-start submission performance is measured separately over at least 5 runs and must be visible in the validation report.
- I2R A&E must select a deployment strategy that does not routinely expose the user to the previously rejected 30 to 40 second wait. Cold-start submission p95 must remain below 10 seconds. If that threshold cannot be met, the architecture or deployment configuration must change before release.

### Invalid and degraded submissions

- Client-detectable invalid input returns an actionable validation error within 1.0 second.
- Server-side decode, resource-boundary, or inference failures return an actionable non-clean state within a bounded deadline. A still-running valid request is not converted into a failure merely to satisfy the p95 target. I2R A&E must define and justify the hard safety deadline separately from the five-second success measure.
- Failure timing is reported separately and never included in the valid-result success rate.

Batch timing, if delivered, has a separate FRD threshold. Batch averages cannot dilute the single-submission target.

## Accessibility and usability evidence

- keyboard-only completion of Try sample, manual entry/upload, result inspection, and start-over;
- visible focus and logical focus order;
- accessible names for controls and programmatic association of errors;
- status meaning conveyed by text and icon, not color alone;
- WCAG 2.2 AA contrast for core content and controls;
- usable core journey at 200 percent zoom within the supported desktop viewport;
- no serious or critical axe findings in committed pages;
- manual keyboard and NVDA smoke review recorded before release.

## Public-demo privacy and security evidence

- visible synthetic-data-only and unofficial-prototype notice before upload;
- documented data-flow and threat-boundary review;
- content sniffing plus byte, pixel, panel, decoder, time, memory, rate, and concurrency limits;
- no raw image or extracted text in logs, analytics, or crash payloads;
- verified temporary-file cleanup on success and every failure path;
- documented third-party transfer and retention behavior, or proof that core inference has no external egress;
- secret scan, dependency scan, and public-route abuse checks;
- truthful retention copy verified against the deployed architecture.

## Release pass conditions

The release passes only when all of the following are true:

1. All committed automated tests pass in the documented local and CI environments.
2. Every development and holdout fixture produces its independently expected field states and submission summary.
3. No known mismatch, missing applicable evidence, or unreadable applicable field receives No differences found in checked fields.
4. Valid supported benchmark submissions meet the complete-result latency contract.
5. Invalid and degraded inputs meet their separate actionable-failure contracts.
6. The public URL opens without evaluator credentials and completes Try sample plus manual upload paths.
7. UI and documentation never claim legal approval, full TTB compliance, COLA approval, or official affiliation.
8. Accessibility acceptance passes.
9. Public-demo privacy and security acceptance passes.
10. README setup succeeds from a clean checkout.
11. All source code and required documentation are present in the submitted revision.
12. The deployment is built from that same revision and passes a post-deploy smoke test.
13. Known limitations agree across the UI, README, validation report, and implemented behavior.

## Failure conditions

The release fails if any pass condition fails, if a fast failure is counted as a valid result, if fixture outcomes can be satisfied by a hard-coded map, if an absent panel is treated as evidence, if private input reaches logs or undeclared third parties, or if committed behavior exists only as a placeholder.

## Attestation record

| Decision | State | Actor | Selected outcome |
|---|---|---|---|
| `DEC-003` | CLOSED | Requester through bounded decision delegation in `USR-008` and `EVT-011` | Corrected fixture, latency, aggregation, accessibility, privacy, and release contract in this document. |
