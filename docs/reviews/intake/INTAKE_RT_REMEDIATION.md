# Intake Red-Team Remediation Ledger

**Review set:** RT1 requirements fidelity, RT2 UX/stakeholder fidelity, RT3 delivery/traceability  
**Initial verdicts:** 3 of 3 REWORK_REQUIRED  
**Remediation state:** CLOSED, three independent CLEAR verdicts

## Cross-review decision summary

The three reviewers independently agreed on the material defects. The remediation makes five foundational corrections:

1. Valid supported input must return a complete result within the five-second benchmark. Failure recovery is measured separately.
2. The product is a selected-check distilled-spirits demo profile, not complete label or legal compliance verification.
3. A submission accepts 1 to 6 label-panel images and reports coverage. Missing panels cannot yield a clean summary.
4. The assignment has a durable sanitized source baseline, per-requirement locators, and hashes for every external design artifact.
5. Scope, batch priority, and success are closed decisions under the requester's bounded authorization.

## RT1 findings

| Finding | Severity | Remediation | Evidence | State |
|---|---|---|---|---|
| `RT1-F001` Fast failure can satisfy five-second success | High | Separated valid complete-result latency from invalid/degraded failure timing; defined runs, percentile, measurement boundary, and cold behavior. | `success-definition.md`, Latency contract | REMEDIATED |
| `RT1-F002` Complete distilled-spirits wording overclaims coverage | High | Replaced completeness language with selected-check demo profile; enumerated included and excluded checks; separated comparison, presentation, and legal sufficiency. | `scope-boundary.md`, `INTAKE_DOCUMENT.md` | REMEDIATED |
| `RT1-F003` Source traceability is not reconstructable | Medium | Added durable sanitized baseline, source locators for all 58 rows, per-artifact hashes, and explicit omission policy. A re-review correction restored the exact apostrophes and limited STATED provenance to capitalization; punctuation remains reconstructed. | `assignment-source-baseline.md`, `source-requirements.md`, `source-context.md`, `RT1-RR-F001` | REMEDIATED |
| `RT1-F004` DEC-001/002/003 remain open | High | Recorded requester authorization, selected exact outcomes, attested scope/success, and closed all three decisions. | `clarification-log.md`, `open-questions.md`, `EVT-011` | REMEDIATED |

## RT2 findings

| Finding | Severity | Remediation | Evidence | State |
|---|---|---|---|---|
| `RT2-001` Valid-request latency can pass by failing quickly | High | Same corrected valid-result contract as `RT1-F001`; failure runs cannot count. | `success-definition.md` | REMEDIATED |
| `RT2-002` One image conflicts with supported field coverage | High | Accept 1 to 6 panels, show coverage, and prevent clean summary when applicable evidence is absent. | `scope-boundary.md`, `SRC-010`, aggregation contract | REMEDIATED |
| `RT2-003` Evaluator lacks self-starting path | Medium | Made Try sample a Must with a complete synthetic reference record and panel set. | `scope-boundary.md`, `success-definition.md`, `SRC-013` | REMEDIATED |
| `RT2-004` Public-demo data handling is incomplete | Medium | Defined synthetic-only notice, no raw logs, cleanup, third-party disclosure, honest retention copy, and threat/data-flow gate. | `scope-boundary.md`, `success-definition.md`, `SRC-045` through `SRC-047` | REMEDIATED |
| `RT2-005` Accessibility is not testable | Medium | Added supported desktop envelope, keyboard, focus, names/errors, WCAG 2.2 AA contrast, 200 percent zoom, axe, and NVDA criteria. | `scope-boundary.md`, `success-definition.md`, `SRC-015`, `SRC-016` | REMEDIATED |
| `RT2-006` Design dispositions are only pattern-level | Medium | Added one disposition and quarantine record for every PDF/image, including known generated-content defects. | `design-reference-analysis.md` | REMEDIATED |
| `RT2-007` Responsive scope is ambiguous | Low | Selected desktop-first viewports and zoom; deferred mobile-specific layout. | `scope-boundary.md` | REMEDIATED |

## RT3 findings

| Finding | Severity | Remediation | Evidence | State |
|---|---|---|---|---|
| `RT3-F001` Open owner decisions prohibit handoff | High | Closed all decisions and attested exact selections. | `clarification-log.md`, `open-questions.md` | REMEDIATED |
| `RT3-F002` Traceability is not durable | High | Added sanitized baseline, statement IDs, all-row locators, hashes, and redistribution boundary. | `assignment-source-baseline.md`, `source-requirements.md`, `source-context.md` | REMEDIATED |
| `RT3-F003` Scope overclaims selected rules | High | Selected-check profile, enumerated capabilities/exclusions, no comprehensive claim. | `scope-boundary.md` | REMEDIATED |
| `RT3-F004` Single image cannot prove field set | High | Multi-panel submission and coverage state. | `scope-boundary.md`, `SRC-010` | REMEDIATED |
| `RT3-F005` Five-second gate lacks useful completion and envelope | High | Valid result only, p95/30 runs, user activation through rendered result, server diagnostic sub-timing, input/environment metadata, cold and invalid separation. | `success-definition.md` | REMEDIATED |
| `RT3-F006` Fixtures can be cherry-picked or hard-coded | High | Minimum 24, 6 holdouts, scenario matrix, external manifest, deterministic text source, separate extraction/comparison tests. | `success-definition.md` | REMEDIATED |
| `RT3-F007` Public upload security/privacy is assertion-only | High | Added data-flow and threat-model gate, type/resource/rate limits, cleanup, logging, provider, secret, and truthful-copy requirements. | `scope-boundary.md`, `success-definition.md`, `RQ-011` | REMEDIATED |
| `RT3-F008` Result aggregation and human disposition are incomplete | Medium | Defined field-to-submission precedence and immutable system findings with separate session-only disposition. | `success-definition.md`, `scope-boundary.md` | REMEDIATED |
| `RT3-F009` Extraction degradation lacks a release contract | Medium | Added BAIRD extraction-adapter contract and blocked-egress research requirements. | `RQ-001`, `RQ-007`, `RQ-013`, `SRC-037`, `SRC-038` | REMEDIATED AT INTAKE ENTRY LEVEL |
| `RT3-F010` Reference input contract is load-bearing | Medium | Fixed beverage profile, enumerated checks, multi-panel envelope, and required BAIRD/I2R schema outputs. | `scope-boundary.md`, `RQ-005`, `SRC-006`, `SRC-008` | REMEDIATED AT INTAKE ENTRY LEVEL |
| `RT3-F011` Accessibility and obvious usability are not binary | Medium | Added exact browser, viewport, keyboard, focus, semantics, zoom, contrast, axe, and NVDA gates. | `scope-boundary.md`, `success-definition.md` | REMEDIATED |
| `RT3-F012` Batch has no bounded proof target | Medium | Defined gated Should status, up to 250 synthetic rows, and required manifest/progress/isolation/cancel/retry/export evidence if shipped. | `scope-boundary.md`, `RQ-012`, `SRC-040` through `SRC-044` | REMEDIATED AT INTAKE ENTRY LEVEL |
| `RT3-F013` Release provenance lacks a gate | Medium | Required submitted revision, matching deployment, runtime contract, and post-deploy smoke evidence. | `success-definition.md`, release pass conditions | REMEDIATED |
| `RT3-F014` Regulatory versioning needs rule authority | Low | BAIRD must record guidance plus eCFR authority, dates, centralized constants, and pre-release re-verification. | `SRC-033`, `RQ-010`, `regulatory-source-register.md` | REMEDIATED AT INTAKE ENTRY LEVEL |

## Re-review rule

Each original reviewer must inspect the complete remediated Intake and this ledger. CLEAR is allowed only when no material finding remains and all three decisions, sources, boundaries, and success gates are mutually consistent. Any reviewer finding keeps Intake open and triggers another documented remediation cycle.

## Re-review cycle 1 corrections

| Finding | Correction | State |
|---|---|---|
| `RT1-RR-F001` Exact brand example and punctuation provenance | Restored `STONE'S THROW` and `Stone's Throw`; limited STATED requirement/fact to capitalization; kept punctuation under reconstructed field-specific policy. | REMEDIATED |
| `RT1-RR-F002` Intake exit rule conflicts with BAIRD hypotheses | Clarified that human-owned load-bearing assumptions block Intake, while named technical hypotheses advance to BAIRD only with falsification methods and downstream stop gates. | REMEDIATED |
| `RT3-RR-F001` Latency clock omitted client/upload/render time | Changed the primary release metric to user Verify activation through complete rendered and announced result; server timing is diagnostic only. | REMEDIATED |
| `RT3-RR-F002` Intake exit rule conflicts with BAIRD hypotheses | Closed by the same process correction as `RT1-RR-F002`. | REMEDIATED |
