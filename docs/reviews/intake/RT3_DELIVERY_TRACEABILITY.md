# Intake Red Team 3: Delivery and Traceability Review

## Review identity

| Field | Value |
|---|---|
| Review | Independent Red Team 3 |
| Perspective | Senior engineer, delivery owner, and take-home hiring evaluator |
| Date | 2026-08-31 |
| Stage tested | Intake readiness for BAIRD handoff |
| Required verdict | `CLEAR` or `REWORK_REQUIRED` |
| Verdict | **REWORK_REQUIRED** |

## Executive verdict

The intake identifies the right central objective: build a fast, obvious, human-in-the-loop verification assistant that compares application/reference values with visible label evidence and sends uncertainty to the reviewer. It also correctly treats the Grok and Gemini proposals as design input rather than authority. The selected side-by-side review workspace, evidence linkage, warning detail, plain status vocabulary, and conditional exception-first batch concept are defensible choices.

The package does not yet clear Intake. It captures the assignment deliverables and exceeds the brief in process discipline, risk awareness, and regulatory caution, but it is not yet a closed or reproducible contract. Three owner decisions remain open. The authoritative assignment is not stored in a durable project artifact. "Complete distilled-spirits" conflicts with the explicitly excluded mandatory or conditional checks. A one-image contract cannot reliably cover information distributed across container panels. The five-second gate can be satisfied by returning an actionable failure instead of a useful result. The fixture contract has no minimum size, coverage model, independence rule, or holdout rule. Security and privacy claims are not yet backed by a concrete public-upload threat boundary.

Advancing this version to BAIRD would cause architecture and engineering to optimize against an ambiguous target. The package requires focused corrections, not a rewrite.

## Direct answer to the assignment-readiness questions

| Question | Result | Assessment |
|---|---|---|
| Did the intake meet the explicit submission requirements? | **PASS** | Repository, all source code, README setup/run instructions, approach/tools/assumptions documentation, and a deployed URL are all recorded as required release outputs. |
| Did it identify the correct product objective? | **PASS** | The routine matching problem, five-second adoption constraint, mixed technical comfort, human judgment, image quality, and lack of direct COLA integration are correctly centered. |
| Did it correctly use the Grok and Gemini material? | **PASS** | Strong patterns were adopted, risky patterns were rejected, and suggested technology choices were not treated as instructions. |
| Did it choose a reasonable core? | **PARTIAL** | A distilled-spirits demo profile is a reasonable narrow core, but the word "complete" overclaims the checks that are actually in scope. |
| Is correctness measurable enough to drive implementation? | **FAIL** | Fixture and latency gates are gameable and do not yet prove extraction quality or useful response time. |
| Are the input and evidence boundaries closed? | **FAIL** | One image versus multiple label panels, artwork versus bottle photo, supported file types, required reference fields, and result aggregation remain insufficiently defined. |
| Are privacy and deployment risks controlled? | **PARTIAL** | Intent is sound, but public upload, logs, temporary storage, third-party retention, malicious files, and resource abuse lack binding acceptance gates. |
| Is the package genuinely ready for BAIRD? | **FAIL** | Open decisions and the material findings below must be closed first. |

## Review coverage

### Project files read in full

| File | Coverage | Main review purpose |
|---|---|---|
| `AGENTS.md` | Complete | Authority, stop rules, product separation, writing, and delivery controls |
| `README.md` | Complete | Stage status and release deliverables |
| `docs/PROCESS.md` | Complete | Stage gates and traceability claims |
| `docs/intake/INTAKE_DOCUMENT.md` | Complete | Main scope, success, questions, findings, and attestation |
| `docs/intake/ingest-summary.md` | Complete | Request capture and problem thesis |
| `docs/intake/source-context.md` | Complete | Source authority and source handling |
| `docs/intake/known-facts.md` | Complete | Stated, verified, derived, and unknown facts |
| `docs/intake/assumptions.md` | Complete | Load-bearing assumptions and falsification paths |
| `docs/intake/open-questions.md` | Complete | Human decisions and downstream research |
| `docs/intake/clarification-log.md` | Complete | Decision state and attestation history |
| `docs/intake/success-definition.md` | Complete | Observable evidence and release pass/fail contract |
| `docs/intake/scope-boundary.md` | Complete | Committed, conditional, excluded, and deferred scope |
| `docs/intake/source-requirements.md` | Complete | Source statement inventory and downstream acceptance direction |
| `docs/intake/regulatory-source-register.md` | Complete | Regulatory sources and capability guardrails |
| `docs/intake/initial-risk-notes.md` | Complete | Risk coverage and mitigation direction |
| `docs/intake/design-reference-analysis.md` | Complete | Grok/Gemini comparison and design dispositions |

### External and original sources inspected

| Source | Coverage | Finding |
|---|---|---|
| Original take-home assignment and stakeholder notes in the initiating conversation | Complete | Product need and required submission outputs are represented, but the source itself is not durably retrievable from the project. |
| `LabelVerify_UIUX_Design.pdf` | All 10 pages, text and rendered pages | Strong workflow concept, warning detail, and batch design. Contains official-style branding, named identities, legal action wording, unsupported certainty, and a hard five-second stop that must not be copied as requirements. |
| `TTB_Label_Verification_Design.pdf` | All 4 pages, text and rendered pages | Strong split workspace and evidence concept. Contains automatic Approve/Reject, unproven perfect warning claims, a copied stack, and cloud/LLM assumptions. |
| `Gemini_Generated_Image_r2ikjer2ikjer2ik.jpeg` | Full image | Empty workspace reference; official identity and named-user concepts are unsuitable for the public demo. |
| `KqeWZ.jpg` | Full image | Clear intake pattern; equal batch prominence is not justified until batch scope closes. |
| `UNnON.jpg` | Full image | Strong side-by-side result layout and evidence links; raw confidence and pass/return language need constraints. |
| `FgLtZ.jpg` | Full image | Strong warning decomposition; official seal, named staff rule, and compliance override wording are unsafe. |
| `unDHl.jpg` | Full image | Strong exception-first batch pattern; counts and 247-label performance are conceptual, not evidence. |
| `Gemini_Generated_Image_r2ikjer2ikjer2ik (1).jpeg` | Full image | Useful bounding-box concept; generated warning text is nonsensical and proves the asset cannot be a correctness fixture. |
| `Gemini_Generated_Image_r2ikjer2ikjer2ik (2).jpeg` | Full image | Flashy overlay obscures evidence and should remain rejected. |
| Current official TTB distilled-spirits labeling, mandatory information, alcohol content, and health warning pages | Verified during review | The intake's core regulatory facts are directionally correct, but the word "complete" is not supported by the selected field set. |

## Grok and Gemini decision comparison

| Design topic | Grok | Gemini | Intake disposition | RT3 judgment |
|---|---|---|---|---|
| Primary workflow | Home, review, warning detail, batch | Batch inbox plus split review workspace | Three core surfaces plus conditional batch | Correct |
| Human authority | Pass/return/override language | Approve/reject and field override | Human judgment with no legal approval language | Correct, but final reviewer action still needs a contract |
| Evidence | Source image, bounding regions, confidence | Bounding boxes and matched values | Region, crop, snippet, or explicit unavailable state | Correct |
| Warning | Independent wording and presentation checks | Three warning checks | Dedicated detail plus capability matrix | Correct |
| Speed | Hard stop at 5.0 seconds | Background preprocessing and prefetch | Useful result or degraded state near five seconds | Directionally correct, acceptance definition is weak |
| Batch | First-class 200 to 300 item workflow | Default queue and prefetch | Conditional after core | Correct for take-home risk control |
| Image assistance | Zoom, rotate, brighten, original/enhanced | Zoom, rotate, enhance | Zoom/rotate adopted, enhancement benchmarked | Correct |
| Status model | Match, needs review, fail, bad image | Green/yellow/red | Match, Review, Mismatch, Not verified; quality separate | Correct and safer |
| Technology | Mostly design-level | React, Tailwind, FastAPI, Tesseract/Azure, LLM | Deferred to evidence-based analysis | Correct |
| Branding | Official-style TTB seal and employee identity | Government-style system identity | Neutral original brand and no personal identities | Correct |
| Processing visual | Simple timer and fallback | Theatrical scanning overlay | Simple progress and recovery | Correct |

The intake captures every material idea worth retaining from the additional design material. The problem is not design omission. The problem is that several adopted ideas do not yet have closed, measurable delivery contracts.

## Attack cases

| Attack ID | Scenario | Expected safe behavior | Current coverage | Result |
|---|---|---|---|---|
| `ATK-001` | The conversation is unavailable when a future engineer or evaluator audits `SRC-003`. | A durable project source excerpt and exact locator prove what the assignment stated. | `source-context.md:7`, `ingest-summary.md:11`, `INTAKE_DOCUMENT.md:212` | **FAIL** |
| `ATK-002` | All selected fields match, but an applicable age statement or conditional distilled-spirits disclosure is missing. | Product copy says only which checks were performed and never claims a complete distilled-spirits verification. | `scope-boundary.md:11-16`, `scope-boundary.md:52`, `regulatory-source-register.md:9-12` | **FAIL** |
| `ATK-003` | The front image has brand/class/ABV while the warning and producer address are on the back. | The case accepts a documented image set or reports required panel coverage as missing. | `scope-boundary.md:12-16`, `INTAKE_DOCUMENT.md:34-39`, `regulatory-source-register.md:10` | **FAIL** |
| `ATK-004` | The system always returns "Verification timed out, inspect manually" at 4.9 seconds. | Supported valid benchmark inputs must return a complete useful result inside the threshold. | `success-definition.md:41`, `success-definition.md:64` | **FAIL** |
| `ATK-005` | The fixture suite contains only one clean generated bottle and one mismatch. | Minimum independent fixture coverage and difficulty strata prevent cherry-picking. | `success-definition.md:26`, `success-definition.md:39`, `open-questions.md:26` | **FAIL** |
| `ATK-006` | OCR reads the wrong text region but happens to produce the expected field value. | Evidence-region correctness and extraction correctness are tested separately from comparison logic. | `source-requirements.md:18`, `success-definition.md:28` | **PARTIAL** |
| `ATK-007` | OCR/model confidence is low but normalization produces the expected value. | Low-confidence evidence routes to Review or Not verified and cannot aggregate clean. | `source-requirements.md:39-42`, `success-definition.md:40` | **PASS, contract needs thresholds** |
| `ATK-008` | The cloud inference endpoint is blocked or times out. | Bounded timeout, explicit degraded state, and no false result are tested. | `source-requirements.md:65-67`, `open-questions.md:19,25` | **PARTIAL** |
| `ATK-009` | A public user uploads a decompression bomb, malformed image, or huge pixel-dimension file. | Decode limits, byte limits, pixel limits, time limits, and resource isolation reject it safely. | `source-requirements.md:63`, `initial-risk-notes.md` | **FAIL** |
| `ATK-010` | A batch ZIP contains path traversal, duplicate names, unsupported files, or an archive bomb. | Safe extraction, manifest uniqueness, total-size limits, and row-level error isolation hold. | `source-requirements.md:74-77`, `scope-boundary.md:34` | **FAIL if batch is selected** |
| `ATK-011` | Hosting logs, analytics, crash reports, temporary files, or a model provider retain uploaded content. | A data-flow and retention test proves what "ephemeral" means across every component. | `scope-boundary.md:24`, `assumptions.md:14`, `source-requirements.md:83-85` | **FAIL** |
| `ATK-012` | A valid warmed run is fast, but public cold starts or uncached runs take 20 seconds. | Warm and cold distributions are reported with a defined sample count, cache state, and environment. | `success-definition.md:64`, `initial-risk-notes.md:7,16` | **PARTIAL** |
| `ATK-013` | `STONE'S THROW` and `Stone's Throw` are treated as exact without showing normalization. | Exact and normalized-equivalent states remain distinguishable and reviewable. | `source-requirements.md:37-40`, `success-definition.md:19` | **PASS** |
| `ATK-014` | A warning has readable correct text but boldness and physical size cannot be proven. | Text can match while presentation checks remain Review or Not verified; overall cannot be clean. | `regulatory-source-register.md:30-40`, `success-definition.md:55` | **PASS in concept** |
| `ATK-015` | Every implemented check passes, but four applicable checks were out of scope. | Result copy shows checked, not checked, and not verified counts and limits the summary to checked fields. | `INTAKE_DOCUMENT.md:50`, `source-requirements.md:85` | **FAIL** |
| `ATK-016` | A keyboard-only user reaches the review workspace at 200 percent zoom. | Focus order, visible focus, target size, reflow, errors, and all core actions remain usable. | `scope-boundary.md:20`, `source-requirements.md:25-31` | **PARTIAL** |
| `ATK-017` | The deployed URL runs code or configuration different from the submitted revision. | Release evidence records the deployed revision and smoke-tests that exact build. | `success-definition.md:31,42`, `docs/PROCESS.md:17` | **PARTIAL** |

## Findings

### `RT3-F001` - Open owner decisions prohibit handoff

**Severity:** HIGH  
**Evidence:** `README.md:7-14`, `AGENTS.md:9-10`, `assumptions.md:21-23`, `open-questions.md:7-9`, `clarification-log.md:15-31`, `INTAKE_DOCUMENT.md:204-227`

`DEC-001`, `DEC-002`, and `DEC-003` are still open and the project instructions explicitly prohibit advancement before the solution boundary is confirmed. The present intake calls its scope and success documents draft and unsigned. No red team can convert those open owner decisions into approval by consensus.

**Remediation:** Record the owner's current authorization as a new clarification event, explicitly accept or revise each recommended decision, update the attestation state, and change the Intake verdict only after the resulting text is reviewed. If the owner selects the recommendations, state the exact decision: distilled-spirits demo profile, batch gated after core, and a corrected measurable success contract.

### `RT3-F002` - Source-to-requirement traceability is not durable

**Severity:** HIGH  
**Evidence:** `ingest-summary.md:10-12`, `source-context.md:7`, `source-requirements.md:7-101`, `INTAKE_DOCUMENT.md:212-214`

The assignment is classified as authoritative but exists only in the initiating conversation. The intake attestation says it is captured and retrievable, which will not be true for an engineer, reviewer, or GitHub evaluator who receives only the repository. `SRC-NNN` rows contain a provenance class but no `S-NNN` source ID and no section or quotation locator. This breaks the package's claimed source-to-decision-to-requirement chain at its first link.

**Remediation:** Add a durable, sanitized assignment source record inside the project. Preserve every product statement, stakeholder constraint, deliverable, and evaluation criterion needed for traceability while excluding irrelevant personal anecdotes. Give each `SRC-NNN` row a source ID and exact locator such as section plus paragraph or source statement ID. Record hashes for the two external PDFs and seven images if they remain outside the repository. Do not publish the external assets unless reuse rights are confirmed.

### `RT3-F003` - "Complete distilled-spirits" overstates the selected rules

**Severity:** HIGH  
**Evidence:** `INTAKE_DOCUMENT.md:14,77-80,102-116`, `scope-boundary.md:11,15-16,45,52`, `regulatory-source-register.md:9-16`, `known-facts.md:35-40`

The proposed scope calls the path "complete" and "fully supported" while explicitly excluding age claims, standards-of-identity analysis, and other conditionally mandatory distilled-spirits information. Official TTB guidance lists additional mandatory and conditional information beyond the proposed field set. Matching class/type text to application data also does not establish that the designation itself legally satisfies a standard of identity.

This is not a reason to expand the take-home. It is a reason to narrow the claim.

**Remediation:** Rename the scope to a "distilled-spirits demo profile" or "selected distilled-spirits checks." Enumerate every included check. Enumerate applicable checks not evaluated. Separate application-to-label equality from label-only presentation checks and from legal sufficiency. Remove "complete" and "fully supported" anywhere they can be read as comprehensive TTB coverage.

### `RT3-F004` - The single-image contract cannot prove the committed field set

**Severity:** HIGH  
**Evidence:** `INTAKE_DOCUMENT.md:34-39,78-80`, `scope-boundary.md:12-16,28`, `regulatory-source-register.md:10-11`, `source-context.md:33`

The primary journey and committed scope use one uploaded image, yet the intended field set can be distributed across front, back, and side labels. The package recognizes that one panel may be insufficient but does not resolve the contradiction. A prototype that asks for one front image and then reports producer address or warning as missing can confuse missing evidence with a label defect.

**Remediation:** Choose and document one of two contracts before BAIRD:

1. Accept one or more images as a case-level label set, with panel coverage, per-image limits, deduplication, and evidence linkage; or
2. Accept exactly one image and explicitly verify only content visible in that image, with all absent-panel checks reported as Not verified rather than missing.

The first option is stronger for the stated field set. The second is smaller but requires narrower product claims.

### `RT3-F005` - The five-second acceptance gate can be satisfied without useful verification

**Severity:** HIGH  
**Evidence:** `source-requirements.md:24`, `success-definition.md:41,56,62-66`, `design-reference-analysis.md:75-79`, `initial-risk-notes.md:7`

The proposed gate accepts a "complete result or actionable failure" within five seconds for a supported image. An implementation that always times out and sends the user back to manual review could pass. One observed run also does not establish latency reliability. The benchmark lacks sample count, percentile, client/server measurement boundary, deployment region, cache state, dimensions, file bytes, concurrency, and field-completeness criteria.

**Remediation:** For supported valid benchmark fixtures, require a complete useful result within the threshold, not a timeout fallback. Define start and stop events, maximum bytes and pixels, fixture mix, deployment environment, warm/cold/cache state, run count, and percentile. A defensible take-home target is warmed deployed p95 at or below five seconds for valid supported single-label fixtures, with cold-start results reported separately. Invalid and unreadable inputs may satisfy the threshold with actionable failure. Record partial-result behavior separately and never call it a successful verification.

### `RT3-F006` - Correctness evidence is too easy to cherry-pick or hard-code

**Severity:** HIGH  
**Evidence:** `success-definition.md:26-31,38-40`, `open-questions.md:26`, `assumptions.md:12`, `initial-risk-notes.md:12`, `source-requirements.md:98-100`

"Every curated fixture passes" is not meaningful without a minimum corpus, scenario matrix, independent expected outcomes, and separation of extraction tests from deterministic comparison tests. The package has no holdout rule and no protection against fixture-specific mappings. Generated labels can also contain visual nonsense while looking realistic, as the supplied mockups demonstrate.

**Remediation:** Before FRD sign-off, define a fixture manifest schema and coverage matrix. It must include at least clean match, exact mismatch, normalized variation, missing required field, unreadable region, wrong evidence region, warning text mutation, heading-case failure, typography uncertainty, multi-panel or absent-panel evidence, invalid file, and external inference failure. Keep expected outcomes independent of implementation code. Add a small holdout set not used while tuning. Report per-fixture results and field-level errors without claiming production accuracy. For generated labels, author canonical text deterministically and then apply controlled image degradation rather than trusting text rendered by image generation.

### `RT3-F007` - Public upload security and ephemeral privacy are assertions, not acceptance gates

**Severity:** HIGH  
**Evidence:** `scope-boundary.md:23-24,47-49`, `assumptions.md:8,14,16`, `source-requirements.md:63-67,83-87,93-97`, `initial-risk-notes.md:16-18`

The planned public URL accepts untrusted files. File type validation alone does not cover decompression bombs, oversized dimensions, malformed decoder input, batch archive traversal, resource exhaustion, third-party upload retention, logs, crash telemetry, EXIF metadata, temporary storage, or cleanup. "No intentional persistence" is weaker than the visible claim that nothing is stored.

**Remediation:** Add a prototype threat/data-flow gate for BAIRD. It must identify every process, network hop, temporary location, log, analytics/crash service, and third-party inference provider. Define accepted MIME types, content sniffing, byte and pixel limits, decoder time/memory bounds, request rate/concurrency bounds, timeout, cleanup, metadata handling, log redaction, retention policy, CORS/CSRF posture as applicable, and secret handling. If batch ZIP is selected, include traversal, archive bomb, duplicate-name, and total-uncompressed-size controls. Change UI claims to what the implementation can prove.

### `RT3-F008` - The end-user decision and aggregation contracts are incomplete

**Severity:** MEDIUM  
**Evidence:** `INTAKE_DOCUMENT.md:41-50`, `design-reference-analysis.md:81-93,107-116`, `scope-boundary.md:17-19`, `source-requirements.md:17,40-42`

The package defines field states and submission summaries, but not the aggregation truth table or the user's permitted actions after reviewing a result. It rejects Approve/Reject wording but proposes "Complete review" and "Needs correction" without stating whether these are ephemeral UI actions, whether the user can disagree with a field result, or whether the original system finding remains visible.

**Remediation:** Define the case aggregation rule. At minimum: any deterministic mismatch yields Differences detected; otherwise any Review or Not verified yields Review needed; only all in-scope checks with sufficient evidence can yield No differences found in checked fields. Define whether reviewer actions are included, whether changes are session-only, and how system findings remain immutable when a reviewer disagrees.

### `RT3-F009` - AI/OCR degradation is researched but not yet bound to release behavior

**Severity:** MEDIUM  
**Evidence:** `open-questions.md:19-25`, `source-requirements.md:39-42,65-67`, `initial-risk-notes.md:8,13,20`

The intake correctly defers OCR/model selection and rejects confidence as truth. It does not yet state the minimum evidence contract an extraction adapter must return, or whether the released demo must function when external inference is blocked. A "credible fallback" can range from local OCR to an empty checklist and therefore changes the product outcome materially.

**Remediation:** BAIRD entry must require an extraction adapter contract containing raw text, field candidate, region/crop when available, confidence provenance, error class, duration, and provider/model version. The architecture decision must choose either a self-contained core, an external service with tested degraded behavior, or a deterministic demo fallback. State whether blocked egress is a release acceptance test or only a documented limitation.

### `RT3-F010` - The application/reference input contract is still load-bearing

**Severity:** MEDIUM  
**Evidence:** `assumptions.md:9`, `INTAKE_DOCUMENT.md:106-109`, `scope-boundary.md:26-28`, `open-questions.md:23`

Manual structured entry is recommended but unsigned. Exact required fields, optionality, imported status, beverage category, units, validation, and how blank reference data differs from a missing label field are deferred. This is acceptable during Intake only if the scope decision closes and BAIRD has a mandatory contract work item. The current primary journey also says the user selects beverage type while the recommended core supports only distilled spirits.

**Remediation:** After `DEC-001`, align the journey with the selected scope. For a distilled-spirits-only demo, remove a meaningless category selector or show a fixed profile. Define the minimum reference record, required/conditional fields, canonical units, imported flag, validation errors, and missing-value semantics before architecture is approved.

### `RT3-F011` - Accessibility and "obvious" usability are not binary yet

**Severity:** MEDIUM  
**Evidence:** `success-definition.md:16-22`, `scope-boundary.md:20`, `source-requirements.md:25-31`, `design-reference-analysis.md:95-105`

"Without instructions," "responsive," and "keyboard-usable" are good goals but not sufficient acceptance criteria. The design references are desktop-oriented and visually dense at smaller widths.

**Remediation:** Define supported browsers and viewport range, keyboard-only completion, visible focus, no color-only status, accessible names, error association, text zoom/reflow target, contrast target, and automated accessibility scan policy. Keep the core desktop-first if that protects schedule. Do not promise broad responsive behavior without a tested breakpoint contract.

### `RT3-F012` - Conditional batch scope lacks a bounded proof target

**Severity:** MEDIUM  
**Evidence:** `scope-boundary.md:30-38,49,62`, `source-requirements.md:69-77`, `success-definition.md:66`, `initial-risk-notes.md:11`

The decision to gate batch after the core is correct. If selected, the intake does not define the demo batch size or what success means while explicitly excluding production-scale 200 to 300 item processing. The Grok/Gemini mockups visually imply 247-label support that the project will not prove.

**Remediation:** If batch is selected, state a bounded demonstration size, manifest schema, mapping rules, progress semantics, row-level isolation, cancellation/retry, export schema, and performance threshold. Keep all UI and README claims within the tested size. If the mandatory repository and deployment work is at risk, defer batch rather than ship a partial queue.

### `RT3-F013` - Release provenance needs one additional gate

**Severity:** MEDIUM  
**Evidence:** `success-definition.md:31,42-46,58-60`, `docs/PROCESS.md:15-17`, `source-requirements.md:93-100`

The release criteria correctly require a deployed smoke test, clean checkout, README rehearsal, and no secrets. They do not prove that the public deployment corresponds to the submitted revision or that required runtime assets and configuration are present in the repository.

**Remediation:** Record the submitted commit/revision, deployment identifier, runtime configuration contract, and post-deploy smoke evidence. Build deployment from the same repository revision. Verify the clean setup and deployed journey after the final revision, not before it.

### `RT3-F014` - Regulatory versioning should cite the actual rule authority as well as guidance

**Severity:** LOW  
**Evidence:** `regulatory-source-register.md:7-16`, `source-context.md:29-37`, `source-requirements.md:48-56`

The source register uses current official TTB guidance and appropriately avoids legal claims. For exact warning text and deterministic formatting rules, guidance pages alone are a weaker long-term anchor than the referenced CFR sections.

**Remediation:** In BAIRD/FRD, record both the TTB guidance page and the applicable eCFR section, retrieval date, and canonical text/rule version. Centralize regulatory constants. Re-verify them immediately before release.

## Strengths that should not be lost during remediation

1. The package correctly makes the checklist and evidence the interface rather than centering a chatbot or AI spectacle.
2. Missing or low-confidence evidence is prohibited from becoming a clean result.
3. Exact, normalized, mismatched, and not-verifiable states are separated.
4. Image quality is separated from legal or field mismatch.
5. Government warning checks are decomposed by evidence capability.
6. The intake rejects official TTB seals, real employee identities, and misleading approval language.
7. Technology and hosting choices are deferred until latency, egress, license, and deployment evidence exist.
8. Batch is correctly sequenced behind a trustworthy single-label path.
9. Required repository, documentation, deployment, and reproducibility outputs are explicit.
10. The process protects a complete small core over an ambitious incomplete build.

## Missing gates before BAIRD

| Gate ID | Required proof | Exit condition |
|---|---|---|
| `A-GATE-01` | Owner decision closure | `DEC-001`, `DEC-002`, and corrected `DEC-003` are recorded and attested. |
| `A-GATE-02` | Durable source baseline | Sanitized assignment source exists; every `SRC-NNN` has `S-NNN` plus an exact locator. |
| `A-GATE-03` | Honest scope name | No use of "complete" or "fully supported" implies checks beyond the enumerated demo profile. |
| `A-GATE-04` | Evidence input boundary | One-image versus image-set contract, artwork/photo formats, panel coverage, and reference record semantics are closed. |
| `A-GATE-05` | Useful latency contract | Supported valid inputs must return a complete result within a documented repeated benchmark envelope. |
| `A-GATE-06` | Fixture quality contract | Minimum scenario matrix, manifest schema, independent expected outcomes, degradation strata, and holdout rule exist. |
| `A-GATE-07` | Result aggregation contract | Field statuses, evidence thresholds, case summary, unsupported checks, and reviewer action semantics are deterministic. |
| `A-GATE-08` | Security/privacy boundary | Public upload data flow and malicious-file controls are mandatory BAIRD inputs. |
| `A-GATE-09` | Batch proof boundary | If selected, batch demo scale and success conditions are bounded; otherwise batch is absent from the core UI. |
| `A-GATE-10` | Independent re-review | All material findings are closed and the three Intake red teams return `CLEAR` on the same revision. |

## Recommended remediation sequence

1. Freeze a durable sanitized assignment source and repair source locators.
2. Record the owner's decisions and align every status/attestation file.
3. Rename and enumerate the distilled-spirits demo profile.
4. Close the image-set and reference-data contracts.
5. Rewrite the five-second and fixture acceptance gates so they cannot be gamed.
6. Add public-upload data-flow and threat controls as mandatory BAIRD inputs.
7. Define aggregation, unsupported-check copy, and any reviewer action.
8. Bound or defer batch.
9. Run all three Intake red teams again against the same updated revision.
10. Move to BAIRD only after all three return `CLEAR` and `A-GATE-01` through `A-GATE-10` pass.

## Final binary verdict

**REWORK_REQUIRED**

The intake is strong in intent and direction, and it captures the assignment better than a typical take-home plan. It does not yet meet the user's required standard of low slop, reproducible traceability, measurable correctness, and deployable end-to-end control. The findings are bounded and remediable. BAIRD should not begin from this revision.
