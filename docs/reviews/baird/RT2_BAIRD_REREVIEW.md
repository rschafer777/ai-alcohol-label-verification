REWORK_REQUIRED

# BAIRD Red Team 2 Re-review

**Reviewer role:** Stakeholder UX, extraction feasibility, and assignment-fit skeptic  
**Review date:** 2026-08-31  
**Reviewed snapshot manifest SHA-256:** `02b68ffb8148f0880fa70b51135b062238a196eab8739894e141f66083381d71`  
**Snapshot integrity:** PASS, all 45 listed file hashes matched  
**Verdict:** **REWORK_REQUIRED**

## 1. Executive result

The corrected BAIRD package is substantially stronger and most prior RT2 findings are closed at the contract level. The following are now clear:

- Try sample is a one-activation first-time path with explicit focus movement.
- The manual path is plain, low-jargon, and appropriate for mixed technical comfort.
- The 1, 3, and 6-panel interaction model is coherent.
- OCR candidate generation and primary selection are reference-blind.
- Multiple plausible candidates cannot become Match.
- The warning capability and aggregation matrix is now explicit.
- Accessibility acceptance is binary and testable.
- Batch remains absent until every single-submission gate passes.
- Grok and Gemini remain inspirational inputs rather than product authority.
- The selected stack remains proportionate to the homework assignment.

BAIRD is not yet clear because the retained feasibility evidence does not execute the corrected warning contract it is cited to prove, can produce a producer Match without comparing an observed producer value, and excludes OCR engine construction from the claimed cold-process measurement. A separate timeout decision also reintroduces the exact five-second hard cancellation that the attested design disposition rejected.

These are evidence and runtime-behavior defects in the architecture approval record. They are not requests to build the full product before I2R.

## 2. Review scope and integrity

I verified the exact hash of `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT.sha256` first. It matched the instructed value. I then recomputed every listed file hash. All 45 files matched their manifest entries.

I reviewed:

- the complete current Intake;
- every current BAIRD artifact;
- `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md`;
- `docs/baird/evidence/FIXTURE_ALLOCATION.md`;
- `docs/baird/evidence/MODEL_BOM.md`;
- the retained CSV and JSON benchmark evidence;
- every source file under `research/baird-spike` included in the snapshot;
- the Grok and Gemini per-source dispositions in `docs/intake/design-reference-analysis.md`;
- the three initial BAIRD red-team reports;
- `docs/reviews/baird/BAIRD_RT_REMEDIATION.md`;
- the corrected BAIRD handoff and control matrix.

I independently recomputed the retained warm metrics:

| Evidence set | Recorded count | Recomputed p95 | Recomputed maximum | Integrity result |
|---|---:|---:|---:|---|
| Server pipeline CSV | 30 | 3,751.97 ms | 4,011.54 ms | Matches report |
| Browser JSON | 20 | 3,830.40 ms | 3,981.20 ms | Matches report |

The timing arithmetic is accurate for the operations actually measured. The material issue is that those operations are not the complete corrected BAIRD result contract.

## 3. Prior RT2 finding retest

| Prior finding | Re-review state | Evidence |
|---|---|---|
| `RT2-BAIRD-001` load-bearing feasibility deferred | PARTIALLY CLOSED | Representative 1, 3, 6-panel and 12 MP timing now exists, and the 24-fixture allocation is explicit. The retained slice omits active warning rows and the cold metric omits OCR construction, so the claimed full-path and cold closure is incomplete. |
| `RT2-BAIRD-002` reference-conditioned candidate selection | CLOSED | `ENGINEERING_BLUEPRINT.md:162-164` makes observation and primary selection reference-blind. Ambiguity caps the result below Match. Decoy fixtures are reserved. |
| `RT2-BAIRD-003` warning capability and aggregation | CLOSED AS A CONTRACT, OPEN AS FEASIBILITY EVIDENCE | `WARNING_CAPABILITY_MATRIX.md` now gives every active row prerequisites, states, and aggregation. The retained feasibility code does not evaluate most of those rows. |
| `RT2-BAIRD-004` fallback silently weakens the core | CLOSED | `ADR-004`, `BAIRD_ASSESSMENT.md`, and `FIXTURE_ALLOCATION.md` require BAIRD reopening or requester-approved scope change after systematic field-family failure. |
| `RT2-BAIRD-005` Try sample behavior ambiguous | CLOSED | `UX_PRODUCT_SPEC.md:21-24` defines one activation that loads data, starts verification, announces processing, and moves focus to the result heading. |

## 4. Scenario retest

| Scenario | Re-review result | Reason |
|---|---|---|
| First-time evaluator | PASS | One-click sample, honest notice, processing focus, and result focus are explicit. |
| Low-tech manual user | PASS | Two clear entry actions, grouped fields, one Verify action, plain states, and actionable errors avoid hunting. |
| 1-panel evidence | PASS AT DESIGN, PARTIAL AT FEASIBILITY | Warm timing exists, but current active warning presentation checks are not executed by the slice. |
| 3-panel evidence | PASS AT DESIGN, PARTIAL AT FEASIBILITY | Panel timing and ordering were measured. Full corrected active-check results were not. |
| 6-panel evidence | PASS AT DESIGN, PARTIAL AT FEASIBILITY | Six panels completed below five seconds locally, but the benchmark result omits active warning presentation rows. |
| Expected value appears as a decoy | PASS | Reference-blind field-role selection is explicit and the ABV decoy produced Differences found. |
| Multiple net or ABV candidates | PASS AT CONTRACT | Ambiguous candidates cannot be resolved by the reference and cannot become Match. |
| Exact warning with uncertain emphasis | PASS AT CONTRACT | It must become Review or Not verified and aggregate to Review needed. |
| Clean warning with all active rows | NOT PROVEN | The retained slice never evaluates emphasis, remainder weight, separation, continuity, or contrast and legibility as active rows. |
| Producer value differs from reference | NOT PROVEN, FALSE-CLEAN PATH EXISTS IN SPIKE | The retained slice checks only producer anchors and can issue Match without comparing an extracted producer value to the reference. |
| Warm local complete result | PARTIAL PASS | The measured p95 is real for the reduced spike result, not for the corrected full field-level result. |
| Forced process restart | FAIL AS RECORDED | The timer starts after `RapidOCR(...)` construction, so the reported total is not process-start-to-ready or cold-submission time. |
| Keyboard, zoom, and screen-reader behavior | PASS AT DESIGN GATE | The contract specifies semantic structure, focus, live status, 200 percent reflow, axe, keyboard, and NVDA evidence. |
| Batch omission | PASS | Batch remains a post-core Should objective with no core endpoint, parser, or UI commitment. |
| Homework assignment fit | PASS IN DIRECTION | The architecture is bounded, explainable, deployable in shape, and emphasizes working core quality. The evidence claims below must be corrected before I2R. |

## 5. Material findings

### `RT2-BAIRD-RR-001`: The feasibility slice issues clean results without executing the active warning contract

**Severity:** HIGH  
**Status:** OPEN

#### Concrete evidence

- `docs/baird/WARNING_CAPABILITY_MATRIX.md:10-14` makes heading emphasis, remaining-text weight, separation, continuity, and contrast and legibility active aggregating checks.
- `docs/baird/WARNING_CAPABILITY_MATRIX.md:21` permits `No differences found` only when every applicable active warning check is Match.
- `docs/baird/WARNING_CAPABILITY_MATRIX.md:29` says the clean sample requires proven presentation checks.
- `research/baird-spike/spike.py:238-303` builds results for brand, class/type, ABV, net contents, warning heading, warning wording, producer, country, and image quality. It contains no result row for heading emphasis, remaining-text weight, separation, continuity, or warning contrast and legibility.
- `research/baird-spike/spike.py:302` can still return `No differences found` after evaluating only that reduced set.
- `docs/baird/evidence/rapidocr-server-runs.csv` records clean results for `S01`, `S07`, `S08`, `S09`, and `S10` under the reduced result contract.
- `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:43-56` labels those runs a full pipeline and reports zero false clean.

The corrected warning matrix is good. The retained evidence predates or bypasses it. The package therefore cites a reduced checker as proof of the current architecture's complete field-level result and false-clean resistance.

There is a second field-family proof gap in the same slice. `research/baird-spike/spike.py:222` reduces producer evidence to a boolean anchor check. At `spike.py:284`, any observed `BOTTLED BY` plus `FRANKFORT` anchor becomes producer Match. The reference producer value is never compared. A case with the same anchors and a different application producer can therefore become Match in the spike. The future fixture plan reserves a producer mismatch, but the current claim that the slice exercised the proposed comparison boundary is overstated.

#### Impact

This invalidates the strongest BAIRD claim: that the selected full pipeline already demonstrated a complete clean result and zero false clean on a representative architecture slice. It also leaves the feasibility of the hardest warning presentation checks unknown. The user asked for evidence-driven architecture with minimal slop, and these rows are central to the stakeholder's exact-warning concern.

#### Required remediation

1. Update the disposable slice to emit every applicable active warning row from `WARNING_CAPABILITY_MATRIX.md`.
2. Implement a bounded preliminary evidence rule for each presentation row, or return Review or Not verified when the spike cannot establish Match. Do not manufacture a clean result merely because the synthetic font was authored bold or regular.
3. Extract and compare an observed producer name/address candidate. An anchor-presence boolean cannot create Match.
4. Retain per-field output and expected per-field states for each architecture case, not only the submission summary.
5. Re-run at least the clean one-panel, 3-panel, 6-panel, title-case, warning mutation, poor-image, producer mismatch, and warning-uncertainty cases.
6. Recompute warm browser and server timing using the corrected full result contract. The full 24-case release corpus can remain a release gate.
7. Update every PASS and zero-false-clean statement to match the corrected evidence.

#### Closure proof

- per-run field results containing every active warning row;
- producer observed and reference values kept distinct;
- no applicable omitted row in a clean aggregate;
- corrected raw evidence and feasibility report;
- measured p95 still inside the selected architecture envelope or a revised architecture decision.

### `RT2-BAIRD-RR-002`: The claimed forced-process timing excludes OCR engine construction

**Severity:** MEDIUM  
**Status:** OPEN

#### Concrete evidence

- `research/baird-spike/server.py:20` constructs `RapidOCR(...)`.
- `research/baird-spike/server.py:32` starts `warmup_started` only after that construction has completed.
- `research/baird-spike/server.py:33-36` times only the first representative inference.
- `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:76` adds that warmup value to the first post-readiness browser result and calls 6,305.69 ms a conservative forced-process total.
- `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:117`, `docs/baird/BAIRD_TRACEABILITY.md`, and `docs/intake/assumptions.md` use that value to mark cold or restart feasibility closed for architecture design.

Python startup, module imports, OCR object construction, model loading performed during construction, application initialization, listener startup, hash checks, and readiness transition are outside the recorded clock. The sum is therefore not a forced-process total and is not conservative.

#### Impact

The always-running Fly choice reduces routine exposure but does not remove restarts, deploys, or host maintenance. A missing initialization segment could move the cold path above ten seconds. That would affect readiness, evaluator recovery, and the selected resource class.

#### Required remediation

1. Measure from process spawn before Python imports through listener start, model/hash initialization, representative warmup, and readiness success.
2. Measure the first complete browser result after readiness separately.
3. If cold-submission time is reported, define when a request begins relative to readiness and include all waiting or routing time.
4. Record at least five local equivalent-envelope process starts for BAIRD direction, or change the architecture claim to unproven and explain why the selected always-ready host plus mandatory deployed gate is sufficient.
5. Keep the five deployed forced-restart trials as a release stop.

#### Closure proof

- process-spawn-to-ready raw durations;
- first-result raw durations;
- exact clock definitions;
- revised `BG-003`, traceability, assumptions, and feasibility language.

### `RT2-BAIRD-RR-003`: The exact five-second hard cancellation reappears after being rejected

**Severity:** MEDIUM  
**Status:** OPEN

#### Concrete evidence

- `docs/intake/design-reference-analysis.md:85` explicitly rejects a hard five-second cancellation from the supplied Grok design.
- The same Intake analysis says the five-second target must not be satisfied by a fast failure and rejects a theatrical hard stop.
- `docs/baird/SECURITY_DATA_FLOW.md:148` gives the browser a hard abort at exactly 5.0 seconds from Verify activation and the OCR child a 4.4-second deadline.
- The same sentence says these are independent safety bounds, but their values are derived directly inside the five-second result boundary.
- `docs/baird/UX_PRODUCT_SPEC.md` correctly says the p95 target is not satisfied by hiding or replacing a result. The exact 5.0-second abort can still turn a slow but otherwise valid supported result into a timeout.

#### Impact

This can reproduce the wrong lesson from the failed scanner pilot: optimize the clock rather than the useful result. It can also game warm-result reporting if repeated timeouts are reported separately while only successful completions populate the 30-run p95 set. For a public shared-CPU host, scheduler variance near the 4.4-second child limit is plausible.

#### Required remediation

1. Keep the five-second value as the warmed p95 success target.
2. Select a separately justified hard safety timeout above the target and below the proxy bound, with enough room for a valid slow outlier and cleanup.
3. Define the valid-run success denominator. The deployed benchmark must report all attempted valid runs, completion rate, timeout rate, p95 over complete results, and failures separately. A release cannot pass by retrying timed-out valid inputs until 30 successes exist.
4. Keep invalid and known failure-path response bounds separate from valid supported work.
5. Align `SECURITY_DATA_FLOW.md`, `UX_PRODUCT_SPEC.md`, `ENGINEERING_BLUEPRINT.md`, the browser harness, and the original design disposition.

#### Closure proof

- one coherent target and timeout table;
- no hard cancellation at the exact p95 target;
- benchmark reporting attempted runs and completion rate;
- timeout behavior that cannot substitute for a useful complete result.

## 6. Confirmed closures and strengths

The following corrections are sound and should be preserved:

### Stakeholder and evaluator journey

- `UX_PRODUCT_SPEC.md` now gives Try sample one exact behavior.
- Processing uses current step, elapsed time, panel progress, cancel, and a polite live region.
- The review surface keeps original evidence visible and maps `Show on label` to the correct panel.
- Plain Match, Review, Difference, and Not verified language preserves human judgment.
- No agency seal, named employee, queue theater, or legal approval action remains.

### Reference-blind and false-clean contract

- `ENGINEERING_BLUEPRINT.md:162-164` correctly separates observed evidence from expected application values.
- Ambiguous candidates expose alternatives and cannot become Match.
- Equality anywhere in a submission is explicitly insufficient.
- `FIXTURE_ALLOCATION.md` includes ABV, net-contents, and brand decoys plus sealed holdout controls.
- Systematic field-family failure reopens BAIRD rather than silently reducing scope.

### Warning contract

- `WARNING_CAPABILITY_MATRIX.md` now resolves the prior advisory ambiguity.
- Every active row aggregates.
- Insufficient evidence becomes Review or Not verified.
- Physical type size is shown as a human-only limitation and cannot appear passed.

The contract itself is CLEAR. Only its claimed feasibility proof requires rework.

### Accessibility and low-tech usability

- Semantic controls, error focus, result focus, keyboard operation, text plus icons, 200 percent reflow, reduced motion, axe, and NVDA evidence are all explicit.
- The form uses fixed field groups and conditional country input rather than a complex wizard.
- Exact OCR text remains visible while confidence is not presented as truth.

### Multi-panel and batch boundaries

- One, three, and six panels have explicit selection, progress, evidence, pixel, memory, and timing contracts.
- Missing panel evidence prevents a clean result.
- Batch remains a post-core Should objective, with no ZIP or partial feature commitment.

### Homework assignment fit

- React, FastAPI, local OCR, deterministic rules, no database, one OCI image, and one always-ready machine are proportionate choices.
- The design prioritizes a working core, clear evidence, error handling, public access, README reproducibility, and documented limitations.
- The product does not drift into COLA integration, broad legal compliance, wine/beer support, or production federal architecture.

## 7. Grok and Gemini disposition recheck

| Design input theme | Corrected BAIRD disposition | Re-review |
|---|---|---|
| Checklist as interface | Adopted | PASS |
| Split image and results workspace | Adopted | PASS |
| Evidence highlights and panel navigation | Adopted with OCR-region fallback | PASS |
| Dedicated warning detail | Adopted with neutral human-review wording | PASS AT CONTRACT |
| Official branding and named staff | Rejected | PASS |
| Approve, Reject, or compliance override | Rejected | PASS |
| Confidence as verdict | Rejected | PASS |
| Decorative AI scanning overlay | Rejected | PASS |
| Batch as equal landing priority | Deferred behind core | PASS |
| Generated text as fixture truth | Quarantined | PASS |
| Hard cancellation at exactly five seconds | Reintroduced in the security timeout table | FAIL |

## 8. Re-review gate

RT2 can return CLEAR after the same snapshot demonstrates all of the following:

1. The retained feasibility slice evaluates every applicable active warning row and an observed producer candidate before issuing clean results.
2. Per-field raw evidence replaces summary-only proof for the representative slice.
3. The corrected full result still fits the selected warm architecture envelope.
4. Cold timing includes process and OCR construction or is no longer claimed as measured closure.
5. The hard timeout is independently justified and is not the exact p95 target.
6. Valid-run completion and timeout rates are part of the deployed benchmark contract.
7. All three reviewers assess one new unchanged snapshot.

## 9. Binary verdict

**REWORK_REQUIRED**

The architecture and UX direction remain appropriate for the assignment. Reference bias, one-click sample behavior, warning state definitions, accessibility, batch control, and field-family fallback are corrected. The remaining work is narrow but material: make the retained evidence execute the corrected contract, repair the cold clock, and remove the exact five-second hard-stop drift before I2R.
