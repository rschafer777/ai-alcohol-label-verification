# AI-Powered Alcohol Label Verification

## Full Intake Document

**Project type:** Job-application take-home prototype  
**Stage:** Intake complete  
**Verdict:** CLEAR, 3 of 3 independent reviewers  
**Decision state:** `DEC-001`, `DEC-002`, and `DEC-003` closed  
**Implementation state:** Not started  
**Repository/deployment state:** Not created

## 1. Executive restatement

Build a standalone, browser-based AI-assisted comparison tool for routine alcohol-label review. A user provides structured application/reference data and 1 to 6 images representing the relevant label panels. The tool extracts candidate evidence, compares only the selected distilled-spirits demo checks, and returns an explainable field-level result in about five seconds for valid supported submissions. It preserves human judgment, exposes ambiguity and missing evidence, and never claims TTB approval or comprehensive legal compliance.

The core must be immediately understandable to a first-time evaluator, including an in-product Try sample path. It must handle invalid and poor-quality images safely, work without direct COLA integration, remain credible when outbound ML endpoints are blocked, and be reproducible from the submitted source repository. A batch workflow is a gated secondary objective only after the single-submission release gate passes.

This restatement reflects the assignment, official regulatory context, requester instructions, and three independent Intake reviews. The durable assignment reconstruction is in `assignment-source-baseline.md`.

## 2. Problem and opportunity

Agents reportedly review about 150,000 applications per year and spend substantial time comparing values that should be the same. The current routine process takes about 5 to 10 minutes for a simple application. A previous scanner reportedly took 30 to 40 seconds and was abandoned because users could work faster by eye. The opportunity is not autonomous compliance approval. It is faster evidence gathering and comparison so agents can focus on actual judgment.

The prototype must address four adoption constraints:

1. valid supported results need to arrive in about five seconds;
2. the main flow must be clean and obvious for mixed technical comfort;
3. the stated capitalization example needs a Review state rather than naive rejection, while any punctuation normalization requires a separately justified field policy;
4. unreadable or absent evidence must never become a clean result.

## 3. Users and stakeholders

| Role | Need | Intake response |
|---|---|---|
| Compliance agent | Faster routine comparison without loss of judgment | Checklist interface, evidence links, plain reasons, four field states |
| Low-comfort or infrequent user | No hunting, jargon, or hidden flow | One primary action, Try sample, large controls, keyboard support, direct recovery |
| Experienced reviewer | Nuance and source visibility | Exact versus normalized comparison, immutable system finding, original image access |
| Team lead | Evidence that the prototype improves workflow | Fixture report, latency report, limitations, exception-first batch concept |
| IT/security reviewer | Standalone, bounded, honest data flow | No COLA integration, synthetic-only notice, public-upload threat gate, egress decision |
| Take-home evaluator | Working, reproducible, thoughtful submission | Repository, all source, README, approach/tools/assumptions, deployment, validation traceability |

## 4. Authoritative objective

A user can submit a structured distilled-spirits reference record and the label panels needed for the selected checks, receive an evidence-backed field comparison, and understand:

- what matched exactly;
- what matched only after documented normalization and needs review;
- what differs deterministically;
- what cannot be verified from the supplied evidence;
- where the extracted evidence came from;
- what action to take next.

The system supports review. It does not approve, reject, or certify a label.

## 5. Selected product boundary

### 5.1 Core Must scope

- browser-based standalone proof of concept;
- selected-check distilled-spirits demo profile;
- manual structured reference record plus Try sample;
- 1 to 6 JPEG, PNG, or WebP panel images per submission;
- brand, class/type, ABV/proof, net contents, producer/bottler name/address, and conditional import-origin comparison;
- warning text, heading case, and separately supported presentation checks;
- evidence region/crop/snippet or explicit unavailable state;
- Match, Review, Mismatch, and Not verified field states;
- deterministic submission aggregation;
- image-quality and panel-coverage diagnostics;
- original image preserved when preprocessing is displayed;
- accessible desktop-first UX;
- no intentional persistent submission storage;
- local setup, automated validation, public deployment, and required documentation.

### 5.2 Gated Should scope

Batch is valuable because the assignment describes 200 to 300 item peak submissions. It is sequenced after the entire core release gate. If delivered, the maximum claim is based on a tested proof up to 250 synthetic rows and includes a manifest, row isolation, progress, cancellation/retry, exception-first review, and export. Batch does not justify weakening core correctness, accessibility, security, deployment, or documentation.

### 5.3 Out of scope

- comprehensive distilled-spirits legal review;
- wine and malt-beverage rule packs;
- direct COLA integration or real COLA PDF parsing;
- autonomous approval/rejection;
- production federal authorization and identity/audit systems;
- real sensitive data;
- persistent cases;
- production-scale annual throughput;
- definitive physical print-size checks without reliable scale evidence;
- unsupported marketing, formula, age, geography, or standards-of-identity analysis;
- mobile-specific layout;
- Argus code, services, branding, or runtime.

The complete boundary is in `scope-boundary.md`.

## 6. Input and evidence contract

One submission contains one reference record and 1 to 6 panel images. This corrects the original one-image assumption. A single image can be enough only when it visibly contains all evidence needed for every applicable selected check. Missing or wrong panel evidence forces Review needed.

The provisional envelope is:

- JPEG, PNG, or WebP after content sniffing;
- at most 8 MB and 24 decoded megapixels per image;
- at most 24 MB total;
- at most 6 images;
- bounded decode time, memory, processing time, request rate, and concurrency to be finalized in I2R A&E.

The reference schema will define required and conditional values, canonical units, imported status, and missing-value semantics. The UI will use a fixed distilled-spirits profile rather than a misleading beverage selector.

## 7. Decision and result integrity

### 7.1 Field states

- **Match:** sufficient evidence and the selected comparison rule matches.
- **Review:** evidence exists but a normalized variation, heuristic, ambiguity, or human judgment remains.
- **Mismatch:** sufficient evidence proves a deterministic difference under the selected rule.
- **Not verified:** evidence is missing, unreadable, unsupported, or outside prototype capability.

### 7.2 Submission summaries

1. Any Mismatch yields **Differences detected**.
2. Otherwise, any Review or Not verified yields **Review needed**.
3. **No differences found in checked fields** is permitted only when every applicable selected check has sufficient evidence and resolves to Match.

Reviewer notes or disposition are session-only and never erase system evidence.

## 8. Success and validation

### 8.1 Valid-result latency

The deployed warmed-path p95 must be at or below 5.0 seconds over one predeclared set of at least 30 valid supported attempts. The clock starts when the user activates Verify with locally valid inputs and ends when the complete result is rendered and announced. It includes client preprocessing, upload, server validation, extraction, comparison, transfer, and rendering. Server timing is diagnostic only. Each attempt must end in a complete field result for release to pass. The report includes attempt count, complete-result count, completion rate, timeouts, errors, and every duration. A timed-out attempt remains in the denominator and cannot be replaced. A timeout, error, or degraded fallback does not count as success. The 5.0-second value is not a hard cancellation. I2R A&E must define and justify an independent hard safety deadline. The benchmark records input dimensions, bytes, panels, model/provider, deployment tier and region, client region, cache state, concurrency, and every run duration.

Public load-to-interactive p95 target is 3.0 seconds. Cold-start submission p95 must remain below 10 seconds and be reported separately. Invalid and degraded inputs have separate bounded failure thresholds.

### 8.2 Fixture evidence

At least 24 end-to-end synthetic submissions are required, including at least 6 holdouts not used during tuning. The set covers exact matches, normalized variations, mismatches, missing values, absent panels, warning mutations, heading case, typography uncertainty, bounded image degradation, invalid/spoofed/corrupt/oversize inputs, and inference failure if applicable.

Expected outcomes live outside implementation constants. Canonical text is authored deterministically before controlled rendering and degradation. Grok/Gemini mockups and image-generated text are not correctness fixtures.

### 8.3 Accessibility

Core acceptance includes keyboard-only completion, visible focus, accessible names and associated errors, no color-only state, WCAG 2.2 AA contrast, usable 200 percent zoom, zero serious or critical axe findings, and recorded manual keyboard/NVDA smoke review.

### 8.4 Public-demo security and privacy

Release requires a visible synthetic-data-only notice, a documented threat and data flow, content sniffing, resource/rate limits, raw-content log exclusion, temporary-file cleanup, declared provider/retention behavior, secret/dependency checks, and UI privacy wording that matches the deployed system.

The binary release contract is in `success-definition.md`.

## 9. Grok and Gemini comparison

The supplied references converge on useful patterns:

- checklist as the primary interface;
- side-by-side source and result;
- evidence highlighting;
- dedicated warning detail;
- plain multi-state feedback;
- visible timing and progress;
- exception-first batch review.

They also contain ideas that must not become requirements:

- official seals and agency-identical branding;
- named employee identities;
- Approve/Reject or compliance-override authority;
- uncalibrated confidence as verdict;
- decorative AI scanning effects;
- hard cancellation at five seconds;
- copied stack recommendations;
- generated or internally inconsistent values used as fixture truth.

Every PDF and image has an explicit Adopt/Modify/Reject/Quarantine disposition in `design-reference-analysis.md`, and the reviewed bytes are identified by SHA-256 in `source-context.md`.

## 10. Selected decisions

| Decision | Selection | Reason |
|---|---|---|
| `DEC-001` | Selected-check distilled-spirits demo profile with 1 to 6 panels | Best fit to the supplied example and time-constrained working-core preference without overstating legal coverage |
| `DEC-002` | Batch is a gated Should objective after core | Preserves high stakeholder value without risking required correctness and deployment |
| `DEC-003` | Corrected valid-result latency, 24-fixture/6-holdout, aggregation, accessibility, privacy, and release contract | Makes success measurable and resistant to fast-failure or cherry-picked-fixture gaming |

The requester authorized bounded solution decisions and progression through all pre-development stages while maintaining assignment fidelity. This closes the prior human decision blockers. The event is recorded as `EVT-011`.

## 11. Main risks and controls

| Risk | Control |
|---|---|
| False clean result | Fail closed, deterministic aggregation, negative fixtures, holdouts |
| Missing panel | Multi-panel contract, coverage state, clean-summary prohibition |
| OCR hallucination | Raw evidence, region/crop, confidence provenance, Not verified |
| Five-second target missed | Early benchmark, bounded inputs, stable host, separate cold reporting |
| Blocked outbound endpoint | I2R A&E egress decision, adapter boundary, blocked-egress test |
| Warning format overclaim | Per-check capability matrix and physical-size limitation |
| Fixture hard-coding | Separate expected manifest, holdouts, extraction/comparison separation, mutations |
| Public upload abuse/privacy | Threat model, limits, no raw logs, cleanup, honest notice |
| Dense or inaccessible UI | One path, Try sample, accessibility acceptance, plain reasons |
| Batch scope erosion | Should-level gate after core and no untested capacity claims |

## 12. Required final submission

The submitted package must include:

- evaluator-accessible source repository such as GitHub;
- all source code;
- README setup and run instructions;
- brief approach, tools, assumptions, trade-offs, and limitations documentation;
- deployed application URL;
- validation evidence tied to the submitted revision and deployment.

The requester will create the GitHub setup after solution agreement. No repository publication is part of Intake.

## 13. Intake gate status

| Gate | Status | Evidence |
|---|---|---|
| Durable source reconstruction | PASS | `assignment-source-baseline.md`, source locators, design hashes |
| Scope boundary selected | PASS | `DEC-001`, `DEC-002`, `scope-boundary.md` |
| Success contract selected | PASS | `DEC-003`, `success-definition.md` |
| Scope claim bounded | PASS | Selected checks and exclusions; no comprehensive verification claim |
| Multi-panel evidence resolved | PASS | 1 to 6 panel contract and coverage aggregation |
| Valid-result latency ungameable | PASS | Complete result required; failures separate |
| Fixture rigor defined | PASS | 24 minimum, 6 holdouts, scenario and independence rules |
| Accessibility binary | PASS | WCAG/axe/keyboard/NVDA/zoom acceptance |
| Privacy/security entry gate | PASS | Public-upload requirements carried to I2R A&E after BAIRD validation |
| Design dispositions complete | PASS | One row per supplied artifact |
| Three independent re-reviews | PASS | RT1, RT2, and RT3 returned CLEAR after remediation |

## 14. Intake verdict

**CLEAR.** The material findings from RT1, RT2, and RT3 were remediated and traced in `docs/reviews/intake/INTAKE_RT_REMEDIATION.md`. All three independent reviewers returned CLEAR. BAIRD may begin.
