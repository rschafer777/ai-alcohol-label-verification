# Beginning Assessment Intake Requirements Document

Document control ID: LV-BRD-001  
Revision: 2.2  
Date: 2026-08-31  
Status: Pending independent red-team confirmation  
Project: AI-Powered Alcohol Label Verification App take-home assignment

## 1. Purpose

BAIRD converts the approved Intake into the complete requirements baseline that I2R Architecture and Engineering will design against. It answers four questions:

1. What did discovery and the Intake define?
2. What was not defined?
3. What additional requirements are necessary for the stated experience to work safely and seamlessly?
4. Which bounded technical questions must I2R A&E answer before the FRD and Build Instructions can be approved?

BAIRD defines what the solution must accomplish, the boundaries it must respect, and the evidence needed to prove it. It does not select the frontend, backend, OCR engine, API design, hosting platform, data structures, or work packages. Those are I2R A&E and BI decisions.

## 2. Material assessed

- the sanitized assignment source baseline;
- stakeholder discovery notes for Compliance, IT, senior-agent, and junior-agent perspectives;
- technical requirements, deliverables, and evaluation criteria;
- official TTB sources recorded in the Intake source register;
- Grok and Gemini PDFs and images as non-authoritative design references;
- requester decisions and process clarifications;
- every canonical Intake artifact;
- all three Intake review reports and remediation history.

## 3. Requirements baseline summary

TTB compliance agents need a simple standalone prototype that compares information visible on alcohol label images with application values entered for the review. It must produce understandable, evidence-linked field results in about five seconds for the normal warmed path, expose uncertainty instead of creating a false clean result, and keep the compliance agent in control of the final disposition.

The take-home implementation will demonstrate a bounded distilled-spirits profile. It will not integrate with COLAs Online, retain production records, issue legal approval, replace human judgment, claim official TTB affiliation, or claim comprehensive compliance coverage.

## 4. What discovery and Intake defined

| Area | Defined baseline | Authority |
|---|---|---|
| Primary user | Compliance agent with widely varying technical comfort | Stakeholder discovery |
| Primary job | Compare application values with label content faster while preserving judgment | Stakeholder discovery |
| Core workflow | Enter reference values, supply label image evidence, run verification, inspect field results | Assignment plus Intake decision |
| Demonstration scope | Selected-check distilled-spirits profile | Assignment example plus `DEC-001` |
| Input coverage | One structured record and 1 to 6 label-panel images | `DEC-001` |
| Core fields | Brand, class/type, alcohol content and proof, net contents, producer/bottler and address, origin when imported, warning, image and panel sufficiency | Assignment context plus bounded Intake scope |
| Result safety | Missing, unreadable, low-confidence, or conflicting evidence cannot produce a clean result | Stakeholder nuance plus Intake safety decision |
| Human authority | Tool assists comparison and never approves or rejects as a legal authority | Stakeholder discovery plus scope boundary |
| Performance | Normal warmed browser-visible p95 target at or below 5 seconds | Stakeholder discovery plus `DEC-003` |
| Ease of use | Clean, obvious, low-training interaction with visible status and recovery | Stakeholder discovery |
| Network | Restricted outbound access may block external ML endpoints | IT stakeholder discovery |
| Data handling | Prototype uses synthetic or sanitized inputs and avoids intentional persistence | Assignment prototype boundary plus Intake decision |
| Batch | Valuable for 200 to 300 item peaks, but secondary to the required working core | Stakeholder discovery plus `DEC-002` |
| Delivery | All source, README, setup and run instructions, approach/tools/assumptions documentation, repository, and deployed URL | Assignment deliverables |

## 5. What discovery did not define

| Unknown area | Why it matters | BAIRD treatment |
|---|---|---|
| Exact reference-data schema | Verification cannot run without unambiguous expected values and applicability | Define required outcome and route exact schema to I2R A&E |
| Image packaging and technical limits | Public uploads require safe and predictable bounds | Define bounded-input requirement and route exact limits to I2R A&E |
| OCR or vision implementation | Extraction quality, latency, cost, egress, and reproducibility depend on it | Route compared selection and benchmark to I2R A&E |
| Image preprocessing | Rotation, perspective, lighting, and glare affect readability | Require bounded enhancement with original evidence preserved |
| Comparison rules | Case, punctuation, units, ABV/proof, and address variation need field-specific handling | Require explicit policy and Review fallback |
| Warning-check feasibility | Exact text can be compared, but typography and physical size may not be provable | Separate deterministic, heuristic, and human-only checks |
| Exact user interface | Discovery defines ease, evidence, and speed, not page structure | Define UX outcomes and route interaction design to I2R A&E |
| Data flow and temporary storage | Privacy and cleanup claims depend on actual runtime behavior | Require explicit data-flow and lifecycle design |
| API and component boundaries | Needed for maintainable implementation and testing | Route to I2R A&E |
| Hard timeout and cancellation | Five-second success is not itself a safe cancellation policy | Require a separately justified bounded-failure contract |
| Hosting platform and cold start | Public access and latency depend on deployment behavior | Require platform selection and deployed proof |
| Validation corpus | Correctness claims need independent expected outcomes | Require synthetic corpus, holdout, and anti-hard-coding controls |
| Batch implementation | Stakeholder value is clear, but schedule and complexity were initially open | The single-submission core passed its gate and the requester directed a bounded 1 to 300 application batch release; details are governed by the batch reassessment addendum |
| Supported browser and assistive technology matrix | Ease of use must be demonstrable | Require a bounded compatibility and accessibility test matrix |

## 6. Validated and derived requirements

Source class values are STATED, DECIDED, or DERIVED. DERIVED requirements are necessary to make a stated user expectation testable, safe, or complete. They do not select implementation technology.

| ID | Source class | Upstream locator | Requirement | Acceptance outcome |
|---|---|---|---|---|
| `BR-001` | STATED | `SRC-001`, `SRC-007`, `SRC-050`, `SRC-054` | Provide a standalone browser-based proof of concept with a public evaluator path. | Evaluator opens the URL without agency credentials and completes the core flow. |
| `BR-002` | RECONSTRUCTED and DECIDED | `SRC-008`, `SRC-010`, `DEC-001` | Support one structured distilled-spirits reference record and 1 to 6 label-panel images per submission. | Valid single-panel and multi-panel fixtures complete successfully. |
| `BR-003` | STATED and DERIVED | `SRC-001`, `SRC-002`, `SRC-024`, `SRC-036` | Extract label evidence needed for the selected fields using an AI-assisted capability. | Each selected field returns observed evidence or an explicit unavailable state. |
| `BR-004` | STATED and DECIDED | `SRC-003` through `SRC-006`, `SRC-025`, `SRC-031`, `SRC-032`, `DEC-001` | Compare brand, class/type, alcohol content and proof, net contents, producer/bottler and address, origin when applicable, warning, image quality, and panel coverage. | Every applicable selected check appears exactly once in the result. |
| `BR-005` | DERIVED and DECIDED | `SRC-022`, `DEC-003` | Use explicit field states: Match, Mismatch, Review, and Not verified. | Every field and submission summary follows the documented aggregation rules. |
| `BR-006` | DERIVED and DECIDED | `SRC-021`, `SRC-023`, `SRC-024`, `SRC-036`, `DEC-003` | Never report a clean result when applicable evidence is missing, unreadable, low-confidence, or conflicting. | Controlled validation produces zero false clean outcomes. |
| `BR-007` | STATED and DERIVED | `SRC-002`, `SRC-010`, `SRC-018`, `SRC-024` | Show reference value, observed value, state, reason, and inspectable evidence when evidence exists. | Reviewer can trace each machine finding to the relevant label region or explicit unavailability reason. |
| `BR-008` | STATED and RECONSTRUCTED | `SRC-009`, `SRC-019`, `SRC-020` | Preserve human judgment for harmless presentation differences and nuanced cases. | Ambiguous case, punctuation, or extraction outcomes route to Review rather than automatic legal disposition. |
| `BR-009` | STATED and VERIFIED | `SRC-005`, `SRC-025` through `SRC-030`, `SRC-033` | Evaluate the prescribed government warning text, heading capitalization, heading emphasis, remaining-text emphasis, continuity, separation, contrast, and legibility as independent checks. | Each supported check has its own state and evidence; unsupported physical-format checks are Not verified or require human confirmation. |
| `BR-010` | STATED and DECIDED | `SRC-011`, `DEC-003` | Return the complete normal warmed result in about five seconds. | Deployed browser-visible warmed p95 is at or below 5.0 seconds over one predeclared set of at least 30 valid attempts, including every benchmark fixture at least once, at least one multi-panel fixture, and at least 5 fresh browser sessions, with 100 percent complete valid results. |
| `BR-011` | DERIVED and DECIDED | `SRC-017`, `SRC-039`, `DEC-003` | Separate successful-result latency from hard timeout and failure timing. | No timeout or fast failure counts as a successful valid result; hard limits are reported separately. |
| `BR-012` | STATED constraint plus DERIVED behavior | `SRC-037`, `SRC-038` | Explicitly support the restricted-network scenario without assuming local, external, or hybrid inference. | With inference egress blocked, the system either completes verification through its supported path or returns a bounded actionable non-clean state. It never hangs, crashes, or reports a false clean result. |
| `BR-013` | STATED and RECONSTRUCTED | `SRC-012` through `SRC-014` | Make the workflow usable by agents with low technical comfort. | A first-time evaluator completes both Try sample and manual reference-entry, upload, validation-correction, verification, evidence-review, and start-over journeys without external instruction. |
| `BR-014` | DERIVED and DECIDED | `SRC-015`, `SRC-016`, `DEC-003` | Meet core accessibility outcomes for keyboard operation, focus, announcements, contrast, labels, errors, and 200 percent zoom. | Automated and manual accessibility evidence passes the documented supported matrix. |
| `BR-015` | DERIVED and DECIDED | `SRC-035`, `SRC-046`, `DEC-003` | Validate file identity and enforce bounded bytes, decoded pixels, panels, memory, time, rate, and concurrency. | Invalid and malicious boundary tests fail safely without partial clean results or leaked resources. |
| `BR-016` | STATED and DECIDED | `SRC-045`, `DEC-003` | Do not intentionally persist uploaded images, extracted text, or reference values in the core prototype. | Storage and log inspection confirm request-scoped lifecycle and content-free operational logs. |
| `BR-017` | DERIVED | `SRC-014`, `SRC-017`, `SRC-023`, `SRC-037`, `SRC-039` | Provide actionable states for validation, unsupported input, unreadable image, timeout, capacity, and recovery. | Every documented failure path renders a plain-language next action and the app remains usable. |
| `BR-018` | STATED and DERIVED | `SRC-010`, `SRC-018`, `SRC-034` | Preserve the original image as review evidence when enhancement or cropping is shown. | Reviewer can return to the original panel and see how derived evidence relates to it; unsupported degradation remains explicit. |
| `BR-019` | RECONSTRUCTED | `SRC-013` | Include a complete built-in synthetic sample. | Try sample populates reference data and all required panels and produces a deterministic result. |
| `BR-020` | STATED and DECIDED | `SRC-040` through `SRC-044`, `SRC-055`, `DEC-002`, post-core requester direction | Provide a bounded 1 to 300 application batch workflow after preserving the complete single-submission core. | Manifest intake, row isolation, sequential processing, progress, cancellation, retry, exception review, and complete exports pass the batch acceptance model in the reassessment addendum. |
| `BR-021` | DERIVED and DECIDED | `SRC-021`, `SRC-035`, `SRC-036`, `SRC-055`, `SRC-056`, `DEC-003` | Use at least 24 deterministic synthetic end-to-end submissions with independently authored expected outcomes, including at least 6 sealed holdouts. | The manifest covers exact and normalized matches, each mismatch family, missing values and panels, warning mutations, typography uncertainty, bounded image degradation, invalid and resource-boundary inputs, and inference failure when applicable; validation cannot pass through fixture-name hard-coding and reports each field outcome. |
| `BR-022` | VERIFIED and DERIVED | `SRC-025` through `SRC-033` | Centralize regulatory text and rule provenance used by the prototype. | Rule source, retrieval date, version, and release re-verification are documented. |
| `BR-023` | STATED and RECONSTRUCTED | `SRC-050` through `SRC-054`, `SRC-057` | Deliver the repository, all source, README setup and run instructions, and concise documentation of approach, tools, assumptions, trade-offs, and limitations. | Clean-checkout setup succeeds using only the README; repository contents are complete; limitations are accurate; deployed revision identity is recorded. |
| `BR-024` | RECONSTRUCTED | `SRC-048` | Use original neutral branding and clearly identify the product as an unofficial prototype. | UI and documentation contain no official seal, false affiliation, approval, or comprehensive-compliance claim. |
| `BR-025` | DERIVED and DECIDED | `DEC-003`, `success-definition.md` | Keep public load-to-interactive performance separate from verification latency. | Clean-browser load-to-interactive p95 is at or below 3.0 seconds over at least 5 documented loads. |
| `BR-026` | DERIVED and DECIDED | `DEC-003`, `success-definition.md` | Keep process cold-start submission behavior separate from the warmed result target. | Cold-start submission p95 is below 10 seconds over at least 5 documented runs and is not included in the warmed metric. |
| `BR-027` | STATED and RECONSTRUCTED | `SRC-045`, `SRC-047` | Display truthful synthetic-data, privacy, transfer, logging, temporary-handling, retention, and limitation disclosures. | UI and README agree with the implemented and tested data flow before any upload occurs. |
| `BR-028` | RECONSTRUCTED | `SRC-056` | Deliver cleanly organized, documented, reviewable code with separable extraction, normalization, rules, aggregation, and UI contracts. | Code review and tests demonstrate separation, consistent naming, focused modules, and no fixture-specific production logic. |
| `BR-029` | RECONSTRUCTED | `SRC-049` | Exclude unnecessary personal anecdotes and identities from public artifacts. | Public-artifact data-minimization review finds no unnecessary personal detail. |
| `BR-030` | STATED and RECONSTRUCTED | `SRC-053`, `SRC-057` | Keep limitations consistent across the UI, README, fixture report, and deployed behavior. | Cross-artifact review finds no hidden, conflicting, or overstated capability claim. |
| `BR-031` | STATED process constraint | `SRC-058` | Use no em dashes or Unicode dash characters in project deliverables. | Automated scan finds no U+2010 through U+2015 characters. |

## 7. User experience requirements baseline

The following experience is required, while exact page layout remains an I2R A&E decision:

1. Start with one obvious choice between Try sample and manual verification.
2. Make required reference fields and applicable imported-product fields clear before verification.
3. Accept label panels through a familiar file picker and drag-and-drop where supported.
4. Show upload coverage, validation, and processing state without decorative animation that obscures progress.
5. Present the label and field results together so evidence inspection does not require hunting between pages.
6. Use plain result wording: No differences found in checked fields, Review needed, or Differences detected.
7. Let the reviewer inspect each evidence region, conflicting candidate, and original panel.
8. Keep machine findings immutable while allowing a separate session-only reviewer note or disposition.
9. Provide clear start-over and recovery actions.
10. Use the useful Grok and Gemini patterns only as inspiration: side-by-side review, concise status rows, focused warning review, and exception-first batch review. Do not copy their official-looking seals, approval language, synthetic OCR text, or mandatory scope assumptions.

## 8. I2R A&E decision questions

Each question must produce a documented decision, rationale, interfaces, failure behavior, and verification evidence.

| ID | Required decision | Required evidence |
|---|---|---|
| `BQ-001` | Select the OCR or vision approach and fallback behavior. | Candidate comparison, license and egress review, benchmark, adapter contract |
| `BQ-002` | Define image preprocessing and evidence preservation. | Pipeline, limits, before/after behavior, degradation tests |
| `BQ-003` | Define the exact reference record and upload contracts. | Schema, validation, applicability, examples, error cases |
| `BQ-004` | Define field extraction and normalization policies. | Per-field rules, confidence handling, ambiguity boundaries, unit tests |
| `BQ-005` | Define warning capabilities and human-only boundaries. | Capability matrix, regulatory provenance, permitted result wording |
| `BQ-006` | Define end-to-end UX, navigation, state, and accessibility behavior. | Wireflow, state model, keyboard and screen-reader acceptance |
| `BQ-007` | Define frontend, middleware, backend, API, and component boundaries. | Architecture diagrams, interface contracts, error model |
| `BQ-008` | Define data movement, temporary storage, cleanup, logging, and egress. | Data-flow diagram, lifecycle table, threat model, tests |
| `BQ-009` | Define exact input, resource, concurrency, timeout, and cancellation limits. | Limit rationale, full-stack boundary tests, recovery proof |
| `BQ-010` | Select languages, frameworks, libraries, and dependency controls. | ADRs, compatibility, licensing, reproducible setup |
| `BQ-011` | Select deployment topology and public hosting path. | Platform ADR, cost/limit evidence, cold/warm tests, rollback plan |
| `BQ-012` | Define the validation corpus and independent oracle. | Fixture manifest, holdout controls, mutation and anti-hard-coding tests |
| `BQ-013` | Decide whether batch fits after the core passes. | Schedule and risk assessment, bounded contract, go/no-go record |
| `BQ-014` | Define observability and operational readiness without content leakage. | Health/readiness behavior, metrics, redaction, recovery and smoke tests |

## 9. Scope boundaries

In scope for the core:

- working single-submission, multi-panel distilled-spirits prototype;
- structured reference entry and built-in sample;
- AI-assisted extraction and explainable comparison;
- evidence-linked field results and uncertainty states;
- validation, accessibility, security, documentation, and public deployment.

Out of scope for the core:

- direct COLAs Online integration or COLA PDF parsing;
- user accounts, real PII, durable case history, or production retention;
- comprehensive beer, wine, or distilled-spirits certification;
- autonomous legal approval or rejection;
- physical type-size certification when reliable scale is absent;
- batch as a core release blocker;
- production federal authorization, FedRAMP certification, or ATO;
- Argus code, branding, runtime, services, or infrastructure.

## 10. BAIRD quality and completeness determination

| Assessment | Result | Basis |
|---|---|---|
| Discovery statements captured | PASS | Assignment, stakeholders, deliverables, and constraints map into the baseline |
| Undefined areas identified | PASS | Fourteen material unknown areas are explicit |
| Requirements gaps closed | PASS | Thirty-one testable requirements include stated, decided, verified, reconstructed, and necessary derived outcomes |
| Architecture boundary preserved | PASS | Technical selections are expressed as `BQ-NNN` questions, not assumed solutions |
| User experience sufficiently defined | PASS | End-to-end outcomes are fixed while exact interaction design remains open |
| Safety and uncertainty explicit | PASS | Missing or weak evidence cannot become clean |
| Network constraint represented | PASS | Restricted-network outcome is required without preselecting local or cloud architecture |
| Human authority preserved | PASS | Machine evidence and reviewer disposition remain separate |
| Assignment deliverables traceable | PASS | Source, README, documentation, repository, and deployed URL remain explicit |
| Open requester decision blocks I2R A&E | NO | Remaining unknowns are bounded engineering decisions |

## 11. Review remediation

The first corrected-process review found that earlier work had placed architecture conclusions inside the Intake and BAIRD layers. Revision 2.0:

- removes selected OCR, hosting, byte, pixel, canvas, and hard-timeout conclusions from the requirements baseline;
- reclassifies retained technical research as evidence for I2R A&E;
- preserves the five-second, restricted-network, safety, privacy, and evaluator outcomes as requirements;
- adds the missing BAIRD function requested by the requester: identify undefined areas and derive the requirements needed for the stated experience to work;
- defines a bounded I2R A&E question set without choosing implementation technology.

The V2 independent review found source-lineage and completeness gaps. Revision 2.1:

- adds durable upstream locators to every `BR-NNN`;
- adds `02_BAIRD_SOURCE_DISPOSITION_MATRIX.md` mapping all 58 source requirements and all 3 requester decisions;
- carries trade-offs, limitations, code organization, public-artifact minimization, privacy disclosure, and the writing convention into explicit requirements;
- reconciles initial-load, warmed verification, cold-start, and hard-failure timing as separate outcomes;
- defines blocked-egress behavior without requiring a local, external, or hybrid implementation.

The V3 independent review found three omitted acceptance details. Revision 2.2 restores the manual workflow usability journey, independent warning presentation checks, and the approved benchmark and validation-corpus counts and composition.

## 12. BAIRD determination

The Intake is faithful to the assignment, and this BAIRD now completes the requirements-level gaps needed to begin architecture and engineering. It defines what is known, what remains unknown, what the solution must accomplish, and what I2R A&E must decide and prove.

Disposition: READY FOR THREE INDEPENDENT BAIRD REVIEWS.

Advancement rule: Three CLEAR verdicts on the same corrected Intake and BAIRD snapshot authorize I2R A&E. A material finding must identify a missing, inaccurate, contradictory, untestable, or architecture-contaminated requirement.
