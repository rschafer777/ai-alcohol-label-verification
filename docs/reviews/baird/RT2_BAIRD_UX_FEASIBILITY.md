# BAIRD Red Team 2: Stakeholder UX and Feasibility

**Reviewer role:** Independent stakeholder UX, extraction feasibility, and performance skeptic  
**Review date:** 2026-08-31  
**Revision reviewed:** Current local BAIRD snapshot at review time  
**Verdict:** **REWORK_REQUIRED**

## 1. Executive finding

The product direction is strong. It preserves the assignment's human-in-the-loop intent, gives a first-time evaluator a clear sample path, keeps batch behind the correct gate, defines a practical multi-panel workspace, treats warning wording separately from presentation, and specifies unusually good accessibility and public-demo honesty for a take-home prototype.

The BAIRD stage is not yet clear because three material architecture risks remain unresolved:

1. the selected OCR and hosting path can advance to I2R even though the only timing evidence is explicitly non-representative and the two Intake load-bearing hypotheses remain open;
2. expected application values are allowed to influence evidence-candidate selection, which can create a false clean result;
3. warning presentation checks do not yet have a coherent capability and aggregation contract, so the same case can become either permanently Review or incorrectly clean depending on an I2R choice that BAIRD should make.

These are architecture and trust-boundary issues, not document polish. BAIRD should not advance until they are closed and independently re-reviewed.

## 2. Evidence reviewed

### 2.1 Attested Intake

I reviewed the complete current Intake set:

- `docs/intake/assignment-source-baseline.md`
- `docs/intake/assumptions.md`
- `docs/intake/clarification-log.md`
- `docs/intake/design-reference-analysis.md`
- `docs/intake/ingest-summary.md`
- `docs/intake/initial-risk-notes.md`
- `docs/intake/INTAKE_DOCUMENT.md`
- `docs/intake/known-facts.md`
- `docs/intake/open-questions.md`
- `docs/intake/regulatory-source-register.md`
- `docs/intake/scope-boundary.md`
- `docs/intake/source-context.md`
- `docs/intake/source-requirements.md`
- `docs/intake/success-definition.md`
- the Intake remediation, gate, and three final re-review records in `docs/reviews/intake`

### 2.2 BAIRD package

I reviewed every current BAIRD artifact:

- `docs/baird/ARCHITECTURE_DECISIONS.md`
- `docs/baird/BAIRD_ASSESSMENT.md`
- `docs/baird/BAIRD_TRACEABILITY.md`
- `docs/baird/ENGINEERING_BLUEPRINT.md`
- `docs/baird/I2R_HANDOFF.md`
- `docs/baird/SECURITY_DATA_FLOW.md`
- `docs/baird/TECHNICAL_SOURCE_REGISTER.md`
- `docs/baird/UX_PRODUCT_SPEC.md`

### 2.3 Current primary-source verification

I rechecked the load-bearing technology and hosting claims against current primary sources:

- [RapidOCR quick start](https://rapidai.github.io/RapidOCRDocs/main/quickstart/) confirms the local `rapidocr` plus `onnxruntime` path and exposes boxes and recognized text.
- [RapidOCR usage documentation](https://rapidai.github.io/RapidOCRDocs/main/install_usage/rapidocr/usage/) confirms boxes, text, scores, and elapsed-time output. It also shows that default model families change by package version. This supports the adapter choice but reinforces the need to pin the exact package, model identifiers, and model hashes.
- [RapidOCR repository](https://github.com/RapidAI/RapidOCR) confirms Apache 2.0 for project code and separately identifies Baidu model copyright. Release notices still need to cover the actual bundled model files.
- [Railway pricing plans](https://docs.railway.com/pricing/plans) currently lists Hobby at 5 USD per month, plus measured resource usage. It provides resource ceilings, not a latency guarantee.
- [Railway Serverless](https://docs.railway.com/deployments/serverless) confirms that sleep behavior is optional and based on inactivity. Disabling it is directionally correct but does not prove a warm OCR result target.
- [Fly autostop and autostart](https://fly.io/docs/launch/autostop-autostart/) confirms that one machine can be kept running in the primary region with the stated settings.
- [Azure Container Apps scaling](https://learn.microsoft.com/en-us/azure/container-apps/scale-app) confirms that `minReplicas` of 1 or more keeps an instance running.
- [Render free services](https://render.com/docs/free) confirms idle spin-down and an approximately one-minute wake, so rejecting that tier for the evaluator URL is correct.

The primary sources validate component capabilities and hosting mechanics. None validates OCR accuracy on alcohol labels or the five-second user-visible result. Those claims still require project evidence.

## 3. Scenario attacks

| Scenario | Expected behavior | BAIRD result | Assessment |
|---|---|---|---|
| First-time evaluator opens the public URL | Sees honest prototype notice, selects Try sample, receives an inspectable result without instructions | Landing and review surfaces are clearly specified | PASS, with a minor behavior ambiguity noted below |
| Low-tech agent checks one label | Uses plain form groups, one Verify action, visible evidence, and plain state language | UX avoids dashboard clutter and legal-decision wording | PASS |
| Submission has 1, 3, or 6 panels | Progress and evidence identify the correct panel; missing panels cannot become clean | Panel selector, progress, coverage, and evidence switching are specified | DESIGN PASS, PERFORMANCE UNPROVEN |
| Label contains glare, angle, blur, or tiny warning text | Tool either extracts defensibly or requests better evidence without invention | Preprocessing and uncertainty states exist, but the selected OCR has not been tested on a representative full-panel set | REWORK |
| Label contains the expected number in an unrelated region and a different number in the true field | Candidate selection must not use the expectation to manufacture a Match | Expected values may rank candidates | REWORK |
| Warning wording is exact but boldness cannot be established | Result must follow one documented capability and aggregation rule | BAIRD defers whether advisory warning observations elevate Review | REWORK |
| Warm public evaluator run | Complete rendered and announced result has p95 <= 5.0 seconds | Only small crops on a high-end workstation were timed | REWORK |
| Cold process start | p95 stays below 10 seconds and readiness prevents early traffic | Host settings are plausible, but no selected-tier process measurement exists | REWORK |
| Keyboard and 200 percent zoom review | Full core path remains operable and findings are announced | Testable keyboard, focus, zoom, axe, and NVDA contracts are present | PASS AT DESIGN GATE |
| Batch is omitted | Core remains complete and architecture preserves a later seam | Batch is hidden until the single-submission gate passes | PASS |

## 4. Findings

### RT2-BAIRD-001: Load-bearing feasibility is deferred past architecture approval

**Severity:** HIGH  
**Status:** OPEN

#### Evidence

- `docs/intake/assumptions.md:13` defines latency feasibility as load-bearing and requires a BAIRD spike plus deployed benchmark.
- `docs/intake/assumptions.md:18` defines the 24-submission corpus and six-submission holdout as load-bearing.
- `docs/intake/assumptions.md:25` says BAIRD must falsify or confirm both load-bearing hypotheses before architecture approval.
- `docs/PROCESS.md:12` says BAIRD must benchmark load-bearing choices before its three CLEAR reviews.
- `docs/baird/BAIRD_ASSESSMENT.md:78` explicitly says the benchmark is not an acceptance benchmark and does not represent the deployment tier.
- `docs/baird/BAIRD_ASSESSMENT.md:82` times a 480 by 470 warning crop on an Intel i9 workstation. It does not exercise upload, full-panel detection, multiple panels, field location, rule execution, response transfer, browser rendering, or the selected hosting tier.
- `docs/baird/BAIRD_ASSESSMENT.md:174-177` leaves OCR, five-second, cold-start, and fixture gates open.
- `docs/baird/BAIRD_TRACEABILITY.md:42` defers latency closure until before the release architecture is final.
- `docs/baird/I2R_HANDOFF.md:89-95` permits BAIRD exit based on review reports and document checks without requiring the load-bearing feasibility evidence.
- `docs/baird/SECURITY_DATA_FLOW.md:106-107` gives decode/preprocess up to two seconds and the server up to five seconds even though the complete user-visible path must itself be at or below five seconds. That is not a closed latency budget.

#### Why this is material

The prior pilot failed precisely because it took 30 to 40 seconds. A small-crop OCR time on a high-end workstation cannot justify a one-container, one-worker, 1-to-6-panel design on a low-cost public host. Six full panels can multiply OCR work, and small warning text is likely to require more resolution or targeted crops. If this assumption fails during build, the team may need to change the image envelope, model, extraction pipeline, concurrency, host, or even the demonstrable field set. Those are BAIRD decisions.

The fixture plan is thoughtfully described but not allocated. With overlapping categories, 24 submissions can technically satisfy the list while giving little evidence for six-panel processing, warning mutations, decoys, and poor-image behavior. The architecture currently treats the count as sufficient without showing that the planned corpus can challenge the model and rules independently.

#### Required remediation

1. Build a disposable BAIRD feasibility slice before I2R. It may be minimal, but it must use the same decode, preprocess, OCR, candidate, comparison, serialization, upload, and render boundaries proposed for the product.
2. Run it in a resource-capped Linux container matching the proposed Railway tier. Record CPU allocation, RAM peak, image bytes, decoded pixels, panel count, exact RapidOCR version, exact ONNX Runtime version, model IDs, and model hashes.
3. Use full submission images, not only hand-cropped regions. The set must include at least one each of 1, 3, and 6 panels; a high-resolution case near the input envelope; small warning text; capitalization review; deterministic mismatch; missing expected evidence; glare or blur; and a decoy field value.
4. Measure the Intake boundary from Verify activation through complete rendered and announced results. Use enough warm and forced-process-start runs to close `BG-002` and `BG-003`, or explicitly revise the architecture before handoff. Server-only timing remains diagnostic.
5. Allocate all 24 planned submissions and six holdouts in a manifest design table. Show field-family coverage, panel-count coverage, degradation coverage, warning coverage, negative invariants, development versus holdout assignment, and which categories overlap. Add decoy and competing-candidate cases.
6. If RapidOCR fails, compare the fully specified fallback on the same cases. Update `ADR-004`, `ADR-007`, `ADR-009`, `BAIRD_TRACEABILITY.md`, and the I2R baseline from measured evidence.
7. Make BAIRD exit require closure of `BG-001` through `BG-004`, not merely three review verdicts.

#### Closure proof

- representative feasibility report and raw timing table;
- exact environment and model provenance;
- fixture allocation table;
- resolved gate outcomes;
- ADR statuses that match the result;
- I2R handoff that cannot bypass the evidence.

### RT2-BAIRD-002: Reference-conditioned candidate selection can produce a false clean result

**Severity:** HIGH  
**Status:** OPEN

#### Evidence

- `docs/baird/ENGINEERING_BLUEPRINT.md:162` permits the candidate locator to use expected reference values to rank possible evidence.
- `docs/intake/success-definition.md:47-49` permits a clean summary only when every applicable selected check has sufficient evidence and resolves to Match.
- `docs/intake/source-requirements.md`, `SRC-021`, `SRC-023`, `SRC-024`, and `SRC-036`, prohibit missing, poor, low-confidence, or unreadable evidence from becoming clean or invented.

#### Attack

Consider an image with `45% Alc./Vol.` in an unrelated promotional sentence and `40% Alc./Vol.` in the actual alcohol-content field, or two net-content-looking numbers on different panels. A locator that knows the application expects 45 can rank the unrelated 45 as the candidate and the comparator can then report Match. The rule has not copied the expected value, but it has still used that value to select confirming evidence.

The same risk applies when the expected brand appears in producer copy, the expected country appears in an address, or `750 mL` appears more than once. Bounding boxes and confidence do not remove confirmation bias.

#### Required remediation

1. Make OCR and primary candidate generation reference-blind. Observed tokens, layout roles, lexical labels, panel hints, and quality evidence must be produced before expected values enter the pipeline.
2. Use expected values only in the comparison stage after an observed field candidate is selected independently.
3. If reference-aware logic is retained solely to disambiguate multiple independently plausible candidates, cap that field at Review. Show all material candidates and explain that the application value influenced ranking.
4. Require field-location evidence such as nearby lexical anchors and panel/region semantics for Match. Text equality anywhere on the submission is insufficient.
5. Add adversarial fixtures for competing ABV values, repeated net contents, expected brand in producer text, expected country in an address, missing expected value plus a close decoy, and expected warning fragments outside the warning block.

#### Closure proof

- revised extraction and comparison contract;
- sequence diagram showing where expected data first enters;
- tests proving each decoy case cannot become Match;
- evidence UI that exposes ambiguity when more than one candidate remains plausible.

### RT2-BAIRD-003: Warning presentation capability and aggregation are unresolved

**Severity:** HIGH  
**Status:** OPEN

#### Evidence

- `docs/intake/scope-boundary.md:36-39` includes warning wording, heading capitalization, and conditional presentation checks in the selected profile.
- `docs/intake/scope-boundary.md:45-49` requires any Review or Not verified to produce Review needed and permits a clean summary only when every applicable selected check has sufficient evidence and is Match.
- `docs/baird/BAIRD_ASSESSMENT.md:100` says boldness cannot be established reliably, that suspicious evidence may trigger Review, and that absence of proof cannot become Match.
- `docs/baird/BAIRD_ASSESSMENT.md:105` says the FRD will decide which advisory observations elevate the submission.
- `docs/baird/I2R_HANDOFF.md:60` explicitly leaves that decision to I2R.
- `docs/baird/UX_PRODUCT_SPEC.md:63-74` displays heading appearance, remainder appearance, separation, continuity, contrast, legibility, and physical-size limitation as independent warning details, but it does not identify which rows aggregate.

#### Why this is material

There are two incompatible outcomes under the current documents:

- If boldness and related observations remain applicable selected checks, lack of reliable proof must be Not verified and every otherwise clean submission becomes Review needed.
- If they are shown only as non-aggregating observations, the app can produce a clean summary while a user may reasonably think the displayed warning-format requirement was checked.

Leaving this to I2R changes core product behavior, the value proposition, the clean sample, the state machine, and the test oracle. BAIRD must choose the capability boundary.

#### Required remediation

1. Add a per-warning-check contract with columns for selected check, evidence prerequisites, possible states, Match proof, Mismatch proof, uncertainty state, aggregation effect, and user-facing limitation.
2. Decide whether heading emphasis, remainder emphasis, separation, continuity, contrast, and legibility are automatic selected checks or non-aggregating observations. Do not mix the two categories in one table or summary.
3. If a check can never produce a defensible Match from the accepted images, do not imply it was automatically verified. Either keep it as a clearly labeled human-only limitation outside the checked-field summary or change the selected-check scope through documented control.
4. Define readable-evidence thresholds for warning wording and capitalization. OCR disagreement or low signal must be Review or Not verified, not a definite Difference.
5. Make the clean sample, title-case sample, altered-wording sample, glare sample, and typography-uncertain sample each have one unambiguous expected warning row and submission summary.

#### Closure proof

- completed warning capability matrix;
- one authoritative aggregation rule used by Intake traceability, UX, API schema, and fixture manifest;
- scenario outcomes for every warning sample;
- no clean result that implies an unsupported presentation check passed.

### RT2-BAIRD-004: OCR failure fallback can silently weaken the committed core

**Severity:** MEDIUM  
**Status:** OPEN

#### Evidence

- `docs/baird/BAIRD_ASSESSMENT.md:174` says that if RapidOCR and PaddleOCR fail, the product may reduce claims and route unsupported fields to Review.
- `docs/intake/scope-boundary.md:26-39` defines the committed selected checks.
- `docs/baird/I2R_HANDOFF.md:62-72` correctly says changes to selected scope and the no-false-clean invariant require change control, but it does not classify widespread OCR non-performance as such a change.

#### Why this is material

Uncertainty on an individual label should route to Review. Systematic inability to automate one or more committed field families is different. A product that sends every warning, producer address, or six-panel case to Review may remain safe but no longer demonstrates the working comparison core the assignment asks evaluators to assess.

#### Required remediation

1. Define a minimum useful capability gate by active field family. At minimum, state the fixture outcomes that must succeed and the false-clean ceiling of zero on the committed corpus.
2. Distinguish case-level uncertainty from system-level unsupported capability.
3. If no self-contained candidate meets the minimum gate, require BAIRD architecture reconsideration or documented scope change. Do not call a systematic capability removal a normal fallback.
4. Make validation evidence report extraction failures, candidate-location failures, rule mismatches, and safe uncertainty separately so a high Review rate cannot hide a non-working feature.

#### Closure proof

- field-family minimum capability table;
- fallback decision tree;
- explicit scope-change trigger;
- validation report schema that exposes safe but unusable behavior.

### RT2-BAIRD-005: Try sample has two permitted behaviors instead of one

**Severity:** LOW  
**Status:** OPEN, non-blocking by itself

#### Evidence

- `docs/baird/UX_PRODUCT_SPEC.md:23` says Try sample either starts verification or prepares verification.
- `docs/baird/UX_PRODUCT_SPEC.md:187-198` expects a first-time evaluator to select Try sample and then observe a result.

#### Recommended remediation

Choose one behavior. The lower-friction evaluator path is one activation that loads the synthetic data, starts verification, focuses the processing status, and then focuses the result heading. If a preview step is intentionally preferred, say why and define the second action explicitly. The README and E2E test must use the same path.

## 5. Design-source disposition check

The BAIRD direction preserves the correct parts of the supplied Grok and Gemini material without treating those files as requirements:

| Supplied concept | BAIRD disposition | RT2 assessment |
|---|---|---|
| Simple single-label landing action | Adopted through Try sample and Check another label | Correct |
| First-class batch landing card | Deferred and hidden until the core gate | Correct |
| Split image and checklist workspace | Adopted with panel selector and evidence actions | Correct |
| Warning-focused detail surface | Adopted without legal approval or applicant-return authority | Correct, subject to RT2-BAIRD-003 |
| Exception-first batch queue | Preserved only as a gated future UX | Correct |
| Official seal, staff identity, queue count, and official IDs | Rejected | Correct |
| Decorative AI scanning overlay | Rejected | Correct |
| Confidence as an answer | Rejected in favor of evidence and uncertainty | Correct, subject to RT2-BAIRD-002 |

There is no design drift toward a chatbot, official TTB branding, autonomous approval, or an oversized dashboard.

## 6. What is already strong

The following areas should be preserved through remediation:

- React plus FastAPI as a small modular monolith is proportionate to the assignment.
- A local OCR adapter and deterministic comparison core fit the blocked-egress context.
- One public origin, no database, no accounts, and no analytics reduce demo risk.
- The original image remains primary evidence and processed views stay labeled.
- Match, Review, Difference, and Not verified language supports human judgment.
- The UX avoids employee impersonation, official case IDs, official seals, and legal action controls.
- Multi-panel navigation, evidence crops, panel progress, and missing-region explanations are explicit.
- The accessibility plan is testable and includes keyboard, focus, zoom, axe, and NVDA evidence.
- Failure states are actionable and distinct from successful five-second results.
- Security controls cover byte, pixel, panel, decoder, rate, concurrency, cleanup, logs, and runtime egress.
- Batch remains a Should-level feature behind a complete single-submission gate.
- Railway, Fly, Azure, and Render were compared using current official behavior rather than assumed free-tier claims.

## 7. Re-review gate

RT2 can return CLEAR only after all of the following are true on the same revision:

1. `RT2-BAIRD-001` through `RT2-BAIRD-004` have documented closure evidence.
2. The selected OCR, model, resource tier, and hosting choice are supported by a representative full-path feasibility result.
3. The candidate-selection contract cannot use expected values to create Match.
4. Every warning check has one capability, state, and aggregation rule.
5. Systematic OCR inability triggers architecture or scope change rather than silent claim reduction.
6. The I2R handoff lists the same measured gates and cannot advance around them.
7. The three BAIRD reviewers evaluate the same final snapshot.

## 8. Binary verdict

**REWORK_REQUIRED**

The proposed product is aligned with the stakeholder and assignment. The BAIRD evidence does not yet justify architecture approval because the five-second and corpus assumptions remain unclosed, and two comparison-design choices can still create misleading clean results. Close the four material findings before I2R.
