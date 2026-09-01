# Intake Red Team 1 - Requirements Fidelity

## Verdict

**REWORK_REQUIRED**

The Intake is materially stronger than the assignment minimum and captures nearly every explicit requirement, stakeholder constraint, delivery obligation, and major failure mode. It does not yet qualify as CLEAR because four material issues remain:

1. the proposed five-second pass condition can be satisfied by a fast failure on a valid supported input;
2. the phrase "complete distilled-spirits verification" overstates the listed regulatory coverage;
3. source traceability is not independently reconstructable from the local package; and
4. the three load-bearing scope and success decisions remain open and unsigned.

These are correctable Intake defects. They do not invalidate the overall direction.

## Reviewed evidence

### Authoritative requester evidence

- The complete take-home assignment in the initiating conversation, including all four stakeholder interviews, Technical Requirements, Additional Context, sample distilled-spirits fields, Deliverables, Evaluation Criteria, and the instruction to fill gaps independently.
- The requester's follow-up requiring the repository to include all source code, README setup and run instructions, and brief documentation of approach, tools, and assumptions.
- The requester's instruction prohibiting em dashes.
- The requester's instruction to consider the Grok and Gemini materials as design input.
- The current request authorizing staged Red Team review and advancement only after review agreement.

### Local project evidence

Every file present under the project root at review time was read in full:

- `AGENTS.md`
- `README.md`
- `docs/PROCESS.md`
- `docs/intake/INTAKE_DOCUMENT.md`
- `docs/intake/assumptions.md`
- `docs/intake/clarification-log.md`
- `docs/intake/design-reference-analysis.md`
- `docs/intake/ingest-summary.md`
- `docs/intake/initial-risk-notes.md`
- `docs/intake/known-facts.md`
- `docs/intake/open-questions.md`
- `docs/intake/regulatory-source-register.md`
- `docs/intake/scope-boundary.md`
- `docs/intake/source-context.md`
- `docs/intake/source-requirements.md`
- `docs/intake/success-definition.md`

### Inspirational design evidence

Both PDFs were text-extracted and every rendered page was visually reviewed:

- Requester-provided `LabelVerify_UIUX_Design.pdf`, 10 pages, identified by the requester as Grok output.
- Requester-provided `TTB_Label_Verification_Design.pdf`, 4 pages, identified by the requester as Gemini output.

All seven supplied images were visually reviewed at original resolution:

- `Gemini_Generated_Image_r2ikjer2ikjer2ik.jpeg`
- `KqeWZ.jpg`
- `UNnON.jpg`
- `FgLtZ.jpg`
- `unDHl.jpg`
- `Gemini_Generated_Image_r2ikjer2ikjer2ik (1).jpeg`
- `Gemini_Generated_Image_r2ikjer2ikjer2ik (2).jpeg`

### Official primary-source validation

The following current official TTB pages were checked on 2026-08-31:

- [Distilled Spirits Labeling: Health Warning Statement](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning)
- [Distilled Spirits Labeling: Mandatory Label Information](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label)
- [Distilled Spirits Labeling: Alcohol Content](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-alcohol-content)
- [Distilled Spirits Labeling](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling)
- [Wine Labeling: Alcohol Content](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/labeling-wine/wine-labeling-alcohol-content)
- [Malt Beverage Labeling: Mandatory Label Information](https://www.ttb.gov/regulated-commodities/beverage-alcohol/beer/labeling/malt-beverage-mandatory-label-information)

## Method

1. Classified the assignment and requester follow-ups as authoritative for product intent, stakeholder constraints, evaluator expectations, and deliverables.
2. Classified official TTB sources as authoritative only for the specific regulatory facts cited.
3. Classified the Argus process as method only and the Grok and Gemini artifacts as inspirational only.
4. Decomposed the assignment into atomic source expectations.
5. Mapped each expectation to Intake documents and `SRC-NNN` entries.
6. Tested each Intake statement for omission, unsupported promotion, scope drift, and acceptance ambiguity.
7. Rechecked regulatory claims against current official TTB pages.
8. Compared adopted, modified, conditional, deferred, and rejected Grok and Gemini proposals against the assignment.
9. Applied the binary rule required by this review: CLEAR only if no material finding remains.

## Authority model validation

| Source | Correct role | Intake treatment | Result |
|---|---|---|---|
| Take-home assignment | Product brief and submission authority | `S-001`, AUTHORITATIVE / REQUIRED | Correct |
| Requester follow-ups | Additional project requirements and approvals | Recorded in the clarification log, but not assigned distinct source IDs | Partial |
| Official TTB pages | Regulatory fact authority for cited checks | `S-002` through `S-005`, plus `REG-NNN` | Correct |
| Argus documents | Process method only | `S-006`, no product dependency | Correct |
| Grok PDF and images | Inspirational design proposals | `S-007`, `S-009`, `DR-NNN` dispositions | Correct |
| Gemini PDF and images | Inspirational design and stack proposals | `S-008`, `S-009`, `DR-NNN` dispositions | Correct |

The Intake correctly resists prompt or instruction drift from attached design documents. It does not adopt their stack, official-looking branding, agent identities, legal approval language, uncalibrated confidence, decorative scanning animation, or batch implementation merely because those ideas appear in generated content.

## Requirement coverage matrix

| Assignment expectation | Authority and strength | Intake evidence | Coverage | Red Team judgment |
|---|---|---|---|---|
| Build an AI-powered alcohol-label verification prototype | Explicit project title and ask | `source-requirements.md:9`, `INTAKE_DOCUMENT.md:20-31` | Complete at Intake | Correctly leaves engine selection to BAIRD/I2R. |
| Compare label artwork with application data | Explicit stakeholder workflow | `source-requirements.md:10`, `INTAKE_DOCUMENT.md:23-38` | Complete | Core objective is accurately centered on evidence-backed comparison. |
| Check brand name | Explicit | `source-requirements.md:11` | Complete | Correct. |
| Check alcohol content | Explicit | `source-requirements.md:12` | Complete | Correct, but FRD must preserve that proof is not a substitute for the mandatory ABV statement. |
| Check government warning | Explicit | `source-requirements.md:13`, `source-requirements.md:48-53` | Complete and expanded | Expansion is justified by official TTB evidence and capability limits. |
| Consider class/type, net contents, name/address, and country of origin | Assignment context and sample, not equally strong for every field | `source-requirements.md:14`, `scope-boundary.md:15` | Captured, scope dependent | Reasonable, but provenance should distinguish required sample fields from contextual common fields. |
| Return useful results in about five seconds | Explicit adoption constraint | `source-requirements.md:24`, `success-definition.md:41,64` | Partial | Material flaw: current pass wording allows a fast failure for a valid supported input. See `RT1-F001`. |
| Be clean, obvious, and suitable for mixed technical comfort | Explicit stakeholder need | `source-requirements.md:25-32`, `success-definition.md:15-22` | Complete and expanded | Plain-language, accessibility, keyboard, and evidence controls are appropriate reconstructions. |
| Preserve human judgment for nuanced differences | Explicit | `source-requirements.md:16,37-42`, `INTAKE_DOCUMENT.md:40-58` | Complete | Strong treatment. Case-only variation is captured; punctuation is promoted too strongly as STATED. See `RT1-F003`. |
| Support batch uploads if feasible | Strong stakeholder request, not a formal deliverable | `source-requirements.md:73-77`, `open-questions.md:8` | Complete as a scope decision | Gated extension is the correct default recommendation for a time-constrained take-home. Decision is still open. |
| Handle angled, dark, glared, or poor images if feasible | Explicitly described as possibly out of prototype scope | `source-requirements.md:62-67`, `scope-boundary.md:20,50` | Complete as bounded Should behavior | Correctly avoids promising impossible recovery. |
| Standalone prototype, no direct COLA integration | Explicit | `source-requirements.md:15`, `scope-boundary.md:43` | Complete | Correct. |
| Account for blocked outbound domains | Explicit technical constraint | `source-requirements.md:65-67`, `initial-risk-notes.md:7` | Complete | Correctly makes egress and fallback an architecture decision. |
| Avoid sensitive-data misuse in the exercise | Explicit context | `source-requirements.md:83-87`, `scope-boundary.md:24,47` | Complete and conservatively expanded | Ephemeral processing is reasonable if documented as a project constraint, not a claim copied from a mockup. |
| Freedom to choose language, framework, and libraries | Explicit | `README.md:47`, `open-questions.md:29-31` | Complete | Correctly deferred from Intake. |
| Review TTB guidance for context | Explicit encouragement | `regulatory-source-register.md`, `known-facts.md:33-40` | Exceeds | Research is focused and current. |
| Handle the supplied distilled-spirits example fields | Explicit example expectation | `scope-boundary.md:11-18`, `source-requirements.md:9-18` | Complete | Correct core direction, but "complete verification" overclaims actual coverage. See `RT1-F002`. |
| Create or source additional test labels | Encouraged | `scope-boundary.md:21`, `success-definition.md:24-32` | Partial | Curated fixtures are planned, but the source register does not separately capture this assignment opportunity. Nonblocking by itself. |
| Submit a source repository | Explicit deliverable | `source-requirements.md:93`, `README.md:34-41` | Complete | Correct release requirement. |
| Include all source code | Explicit deliverable | `source-requirements.md:94` | Complete | Correct. |
| Include README setup and run instructions | Explicit deliverable | `source-requirements.md:95` | Complete | Correct. |
| Briefly document approach, tools, assumptions, and trade-offs or limitations | Explicit deliverable and evaluation note | `source-requirements.md:96,100`, `success-definition.md:31` | Complete | Correct. |
| Provide a deployed application URL | Explicit deliverable | `source-requirements.md:97`, `success-definition.md:42` | Complete | Correct. |
| Optimize for correctness, clean code, technical judgment, UX, error handling, and attention to requirements | Explicit evaluation criteria | `known-facts.md:12-13`, `PROCESS.md:15-21` | Complete and expanded | Correct. |
| Prefer working core over ambitious incomplete scope | Explicit | `source-requirements.md:98`, `scope-boundary.md:70-72` | Complete | Correct and central to the recommended sequencing. |
| Document trade-offs and limitations | Explicit | `source-requirements.md:96,100` | Complete | Correct. |
| Fill gaps independently while allowing clarification | Explicit evaluator expectation | `open-questions.md`, `assumptions.md` | Complete in process | Technical questions are correctly kept for research; only scope and success decisions go to the requester. |
| Do not use em dashes | Explicit requester follow-up | `source-requirements.md:101`, `AGENTS.md:15-17` | Complete | Correct project-wide control. |

## Grok and Gemini comparison

### Ideas correctly adopted

- A checklist-centered interface rather than a chatbot or generic AI dashboard.
- A flat intake flow and a side-by-side image and result workspace.
- Image evidence regions or crops linked to each extracted field.
- A dedicated warning-detail surface because warning text and presentation are separate checks.
- Human review for case differences, partial matches, poor evidence, and low confidence.
- Zoom and rotate, with enhancement evaluated as an aid while preserving the original.
- Visible progress and elapsed time.
- Exception-first batch review, but only if batch is approved.
- Status conveyed with text and icon in addition to color.

These decisions are well supported by the assignment and are accurately documented in `design-reference-analysis.md:25-79`.

### Ideas correctly modified

- Three visual states became Match, Review, Mismatch, and Not verified so missing evidence cannot look like a regulatory defect or a pass.
- "Bad image" became an input-quality state rather than a legal outcome.
- Confidence became supporting evidence instead of a verdict.
- The Grok five-second hard stop became an actionable degraded state rather than forced abandonment of partial evidence.
- The Gemini warning module was expanded beyond three checks using official TTB guidance, while physical size and some typography checks remain uncertain.

### Ideas correctly rejected or deferred

- Official seals, agency-identical styling, realistic staff identities, and generated avatars.
- Blanket Approve and Reject actions that imply legal authority.
- "Override compliant" as a way to erase a deterministic system finding.
- Decorative AI scanning effects that obscure the evidence.
- Auto-collapsing match rows before usability validation.
- Claims that the warning check works perfectly.
- React, Tailwind, FastAPI, Tesseract, Azure Document Intelligence, or an LLM merely because Gemini proposed them.
- Batch infrastructure before the core single-label path is proven.

### Generated-content defects correctly kept out of the Intake

- Mockup spelling and data inconsistencies, including malformed warning text and inconsistent net-content/application cells.
- Unsupported throughput claims such as 1.8 seconds per batch item.
- A visual ruler that implies a photograph can certify physical millimeters.
- A batch queue that mixes distilled spirits, wine, and beer while the product rule scope remains unresolved.
- A generated browser and official-system appearance that could imply TTB endorsement.

The comparison work is one of the strongest parts of the Intake. No material Grok or Gemini proposal was silently promoted into an authoritative requirement.

## Findings

### RT1-F001 - HIGH - Five-second success can be met by a fast failure

**Evidence**

- `docs/intake/success-definition.md:41` passes when the journey returns "a complete result or actionable failure" within five seconds.
- `docs/intake/success-definition.md:64` repeats the same criterion for one supported image.
- `docs/intake/INTAKE_DOCUMENT.md:150` asks the requester to approve that wording.
- The assignment says agents need results back in about five seconds because the previous scanner was slower than manual review. It does not say that a valid label may count as successful merely because the application fails quickly and explains why.

**Impact**

A system that times out on every valid image in 4.9 seconds could satisfy the written latency criterion while failing the central assignment outcome. This weakens the primary acceptance contract and could carry into FRD tests.

**Required correction**

Split latency criteria by input class:

1. valid supported fixtures must return a complete field-level result within the confirmed threshold;
2. invalid, unreadable, oversize, corrupt, blocked-service, and timeout fixtures must return an actionable non-clean state within their own bounded threshold; and
3. cold-start behavior on the deployed evaluator path must have an explicit release treatment, not measurement only.

The five-second statement can remain an approximate stakeholder target, but the pass condition must not equate useful completion with failure recovery.

### RT1-F002 - HIGH - "Complete distilled-spirits verification" overstates the committed field and rule coverage

**Evidence**

- `docs/intake/INTAKE_DOCUMENT.md:14,77,130` uses "complete distilled-spirits reference path" or "complete distilled-spirits verification."
- `docs/intake/scope-boundary.md:11,15` calls the path fully supported but lists brand, class/type, alcohol content, net contents, name/address, import origin, and warning checks.
- `docs/intake/regulatory-source-register.md:9` says official distilled-spirits mandatory and conditional information defines the "complete reference path."
- The current official TTB mandatory-information page also lists conditional items such as age statement, coloring disclosures, commodity statement, sulfites, state of distillation, and other circumstances not included in the committed core.
- The scope expressly excludes standards-of-identity analysis and exhaustive legal coverage at `docs/intake/scope-boundary.md:53-54`.

**Impact**

The wording creates an evaluator-facing contradiction: the Intake correctly disclaims complete TTB coverage while repeatedly calling a subset "complete verification." A straight bourbon example can itself trigger age-statement rules depending on product facts, so the distinction is not academic.

**Required correction**

Rename the recommendation to an accurate bounded term, such as "assignment-aligned distilled-spirits core comparison path" or "attested distilled-spirits field set." Then define exactly what "fully supported" means:

- application-versus-label comparison for the selected fields;
- deterministic warning-text checks where evidence is readable;
- bounded presentation checks with Not verified states; and
- no claim that all mandatory or conditional distilled-spirits requirements are evaluated.

Alternatively, expand the rule and evidence matrix to truly cover all applicable mandatory and conditional requirements, but that would conflict with the assignment's preference for a complete small core and is not recommended.

### RT1-F003 - MEDIUM - Source traceability is not independently reconstructable

**Evidence**

- `docs/intake/ingest-summary.md:11` says the source remains in the initiating conversation and will not be duplicated.
- `docs/intake/source-context.md:25` intentionally removes anecdotes and identities, which is sound, but the local package also lacks a sanitized atomic source baseline with assignment section locators.
- Every table in `docs/intake/source-requirements.md`, beginning at line 7, has a `Source ID` column that actually contains the new `SRC-NNN` identifier. It does not identify `S-001`, `REG-NNN`, a requester event, an assignment heading, or a source paragraph.
- `docs/intake/source-requirements.md:37` marks both case and punctuation differences as STATED, although the assignment example directly establishes capitalization variation, not a general punctuation-normalization rule.
- `SRC-058` is a requester follow-up, but `source-context.md` has no distinct requester-follow-up source entry.

**Impact**

The package promises `source -> decision -> requirement -> component -> test -> evidence`, but a later reviewer cannot independently trace many `SRC-NNN` rows to an exact authoritative statement without access to this conversation. Reconstructed and stated requirements can therefore be confused, especially after handoff to BAIRD or a public repository.

**Required correction**

- Add a sanitized assignment baseline or atomic source-statement register that preserves every relevant statement with stable locators such as `S-001 Deliverables`, `S-001 Deputy-Director/latency`, and `S-001 Junior-Agent/image-quality`.
- Add explicit source locator columns to every `SRC-NNN` row.
- Add source records for requester follow-ups, including repository contents, generated-design treatment, and the no-em-dash rule.
- Split `SRC-019`: capitalization variation is STATED; punctuation normalization is a reconstructed comparison-policy candidate pending field-specific validation.
- Keep personal anecdotes excluded. Exact traceability does not require publishing irrelevant identities or family details.

### RT1-F004 - HIGH - The Intake has no signed scope or success decision

**Evidence**

- `docs/intake/open-questions.md:7-9` leaves `DEC-001`, `DEC-002`, and `DEC-003` OPEN and NON-DEFAULTABLE.
- `docs/intake/scope-boundary.md:82-83` leaves beverage scope and batch treatment open.
- `docs/intake/success-definition.md:72-74` leaves the success contract unsigned and prohibits implementation from treating it as signed.
- `docs/intake/INTAKE_DOCUMENT.md:206` says the package cannot advance while those decisions remain open.
- `README.md:8-12` still reports CLARIFICATION REQUESTED.
- The current requester instruction authorizes the process to move forward after Red Team agreement, but the package does not yet record which exact option values that authorization selects.

**Impact**

BAIRD cannot have a stable scope basis while the Intake itself says no downstream stage may proceed. Different agents could assume different beverage breadth, batch commitment, or latency contract.

**Required correction**

Before BAIRD begins, append a decision event that records explicit values for all three decisions and update the attested scope and success documents consistently. If the current authorization is interpreted as approval of the recommended values, record those exact values rather than merely changing OPEN to CLOSED:

- distilled-spirits assignment-aligned core field set, with precise limits;
- batch as gated post-core extension or another explicit treatment; and
- corrected success contract after `RT1-F001` is resolved.

## Strengths

1. The Intake identifies the actual product value: routine evidence comparison, not generic image recognition.
2. It preserves human judgment and prevents low-confidence or missing evidence from becoming a clean pass.
3. It handles the five-second constraint as a product requirement rather than cosmetic performance work.
4. It captures every explicit release deliverable, including repository, all source code, README, documentation, and deployed URL.
5. It correctly excludes direct COLA integration, federal production authorization, identity management, retention infrastructure, and broad modernization work.
6. It distinguishes application-versus-label matching from label-only regulatory checks.
7. It recognizes that arbitrary photographs cannot reliably certify physical type size, contrast, or font weight.
8. It recognizes beverage-specific rules and avoids pretending one generic rule set covers spirits, wine, and malt beverages.
9. It treats poor-image behavior, blocked inference, corrupt files, and timeouts as first-class failure paths.
10. It documents evaluator reproducibility, clean-checkout rehearsal, deployed smoke testing, and secret scanning.
11. It uses Grok and Gemini selectively and skeptically, preserving strong workflow ideas without adopting unsupported product or stack decisions.
12. It is substantially more rigorous than the take-home requires while staying focused on a working core.

## Unresolved decisions

| Decision | Current state | Red Team recommendation |
|---|---|---|
| Beverage breadth | OPEN | Commit an assignment-aligned distilled-spirits core comparison path. Do not call it complete regulatory verification. |
| Batch treatment | OPEN | Keep as a gated extension after the single-label release gate. Architect for it, but do not let it weaken the core. |
| Success evidence | OPEN | Approve only after separating successful valid-input latency from bounded failure latency and setting a minimum fixture coverage matrix in the FRD. |
| Manual reference input | Load-bearing assumption | Accept for the single-label prototype unless the evaluator supplied another application schema. Document exact field types in the FRD. |
| Deployed cold start | Not dispositioned | Define a release threshold or explicit evaluator-facing warm-up strategy. Measurement alone is not a pass rule. |
| Additional label fixtures | Planned, not sourced | Create clearly synthetic fixtures with positive, mismatch, ambiguous, missing, and degraded variants. Do not imply production accuracy. |

## Final assessment

### Did the Intake meet or exceed the assignment requirements?

It exceeds the assignment in research depth, safety framing, failure-path planning, regulatory nuance, traceability intent, design analysis, and release discipline. It meets nearly all explicit assignment requirements at the Intake level.

It does not yet meet the process standard required to advance because the success contract contains a material loophole, the selected scope uses an overbroad label, the source chain cannot be independently reconstructed, and the load-bearing decisions are still open.

### Are the objectives and product direction correct?

Yes. The core objective, target user, human-in-the-loop posture, single-label priority, evidence-first UX, standalone boundary, and gated batch recommendation are the right direction for this homework assignment.

### Is the Intake ready for BAIRD?

No. Resolve `RT1-F001` through `RT1-F004`, update the affected documents consistently, and rerun the Intake Red Team gate. BAIRD should begin only after the corrected Intake receives a CLEAR verdict and the selected decisions are recorded.

## Binary verdict

**REWORK_REQUIRED**
