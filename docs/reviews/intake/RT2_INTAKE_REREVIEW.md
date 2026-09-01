# Intake Red Team 2 Re-Review: UX and Stakeholder Fidelity

**Reviewer role:** Independent UX and stakeholder red team  
**Review date:** 2026-08-31  
**Revision reviewed:** Remediated Intake after RT1, RT2, and RT3  
**Verdict:** **CLEAR**

## Executive verdict

The remediated Intake closes every material RT2 finding. It now states the right product objective, gives a first-time evaluator a safe self-starting path, makes valid-result latency resistant to fast-failure gaming, resolves multi-panel evidence, defines testable accessibility and public-demo honesty, constrains responsive work to a desktop-first envelope, and records an explicit disposition for every supplied Grok/Gemini artifact.

The Intake now meets the original assignment at the requirements-definition level and exceeds it in traceability, result integrity, accessibility evidence, privacy controls, and validation discipline. Technical feasibility is intentionally not claimed. The remaining OCR, hosting, egress, normalization, schema, and batch questions are correctly routed to BAIRD and I2R with falsifiable outputs.

No material UX, stakeholder-fidelity, assignment-fidelity, scope, or success-contract finding remains in this review.

## Evidence re-reviewed

This re-review read every current file under `docs/intake/`, including the new durable assignment baseline, all scope and success artifacts, source and regulatory registers, risks, assumptions, decisions, and the complete human review document.

It also read:

- `docs/reviews/intake/INTAKE_RT_REMEDIATION.md`;
- the prior `docs/reviews/intake/RT2_UX_STAKEHOLDER.md`;
- current `AGENTS.md`, `README.md`, and `docs/PROCESS.md` for boundary consistency.

The design-source hashes were checked against the nine supplied files. They identify the same two PDFs and seven JPEGs reviewed in the first RT2 pass. A project-wide scan found no Unicode dash characters.

## Prior RT2 finding closure

| Finding | Original concern | Remediated evidence | Re-review result |
|---|---|---|---|
| `RT2-001` | A valid request could satisfy the five-second contract by failing quickly, and cold behavior had no gate. | `success-definition.md:56-76` requires a complete result, warmed p95 at or below 5.0 seconds over at least 30 runs, separate invalid/degraded timing, reported cold runs, and a cold-start failure gate above 10 seconds. `INTAKE_DOCUMENT.md:130` repeats that timeout, error, and degraded fallback do not count. | CLOSED |
| `RT2-002` | A one-image contract conflicted with fully supported distilled-spirits wording. | `scope-boundary.md:18-25` accepts 1 to 6 panels and requires explicit coverage. `INTAKE_DOCUMENT.md:97` makes one image valid only when all applicable evidence is visible. `success-definition.md:45-50` prevents a clean summary for missing panels. The product is now a selected-check profile, not comprehensive verification. | CLOSED |
| `RT2-003` | The evaluator had no guaranteed self-starting path. | `scope-boundary.md:56` makes Try sample part of committed UX. `success-definition.md:15` requires a complete synthetic reference record and panel set without prepared data. `source-requirements.md:25-26` makes both sample and manual journeys testable Must behavior. | CLOSED |
| `RT2-004` | Public-demo retention and third-party handling were too vague. | `scope-boundary.md:74-81` defines synthetic/sanitized-only use, no raw-content logs, cleanup, third-party disclosure, and truthful copy. `success-definition.md:90-99` makes the threat boundary, resource controls, transfer/retention behavior, cleanup, and privacy text release evidence. | CLOSED |
| `RT2-005` | Accessibility was named but not binary. | `scope-boundary.md:54-62` defines supported browsers/viewports, 200 percent zoom, keyboard completion, focus, names/errors, no color-only meaning, WCAG 2.2 AA contrast, axe, and NVDA review. `success-definition.md:79-88` carries these into release evidence. | CLOSED |
| `RT2-006` | Design dispositions were pattern-level and known mockup defects remained implicit. | `design-reference-analysis.md:81-95` now has one Adopt/Modify/Reject/Quarantine row for each `DR-001` through `DR-009`, including the wrong net-contents value, nonsensical warning text, mixed beverage categories, official-looking identity, and decorative scan. Provenance uncertainty is disclosed and hashes identify the bytes. | CLOSED |
| `RT2-007` | Responsive scope was ambiguous and could become unplanned mobile work. | `scope-boundary.md:59-62` defines desktop support from 1024 by 768 through 1920 by 1080 plus 200 percent zoom. Mobile-specific layout is explicitly out of scope/deferred. | CLOSED |

## Stakeholder scenario replay

| Scenario | Required behavior now stated | Intake assessment |
|---|---|---|
| First-time evaluator has no data | One obvious path plus Try sample loads a complete synthetic record and necessary panels. | PASS |
| Low-comfort user enters a real demo record | Plain fields, direct validation, large/obvious flow, direct recovery, and no hidden primary action. Exact schema usability is assigned to I2R. | PASS AT INTAKE |
| Valid supported warmed request | Complete field-level result at warmed p95 at or below 5.0 seconds. Failure cannot count. | PASS AT INTAKE, BAIRD PROOF REQUIRED |
| First valid request encounters a cold process | Cold p95 is measured, published, and fails release above 10 seconds. The 30 to 40 second prior-pilot behavior is prohibited. | PASS AT INTAKE, BAIRD PROOF REQUIRED |
| `STONE'S THROW` differs only by capitalization | Exact versus normalized behavior is visible and routes to Review with a reason. | PASS |
| Warning wording or heading is wrong | Wording, capitalization, and supported presentation checks remain separate. Deterministic evidence cannot be erased by reviewer disposition. | PASS |
| Warning or address is on another panel | Up to six panels are accepted. Missing or wrong coverage forces Review needed and cannot produce a clean summary. | PASS |
| Image is glared, angled, blurred, spoofed, corrupt, or too large | Original evidence is preserved, quality is separate from mismatch, and bounded actionable states are required. | PASS |
| Inference endpoint is blocked | Failure is bounded and non-clean, never counted as valid success. Egress and fallback selection are BAIRD questions. | PASS AT INTAKE |
| Public evaluator considers uploading private material | Synthetic/sanitized-only notice appears before upload and the deployed data flow must match retention and provider disclosures. | PASS |
| Keyboard, low-vision, or screen-reader user completes the core flow | Keyboard, focus, labels/errors, contrast, non-color status, 200 percent zoom, axe, and manual NVDA evidence are release gates. | PASS |
| Peak batch arrives | Batch remains a gated Should objective after all single-submission gates, with a bounded synthetic proof and no unsupported category claims. | PASS |

## End-to-end assignment fidelity

| Assignment expectation | Intake response | Result |
|---|---|---|
| AI-powered label verification prototype | End-to-end extraction, evidence, comparison, rule, aggregation, UI, and deployment contracts are defined without prematurely selecting a provider. | MEETS |
| Compare application data with label artwork | Structured reference record plus 1 to 6 panel images and field-level expected-versus-found evidence. | MEETS |
| Brand and alcohol comparison | Must requirements with documented normalization and fixtures. | MEETS |
| Common label fields | Selected spirits profile includes class/type, net contents, name/address, conditional origin, and the warning, with explicit limits. | MEETS |
| About five-second results | Valid complete-result p95 contract, separate cold and failure evidence, and no fast-failure loophole. | MEETS |
| Clean and obvious for varied technical comfort | One primary path, Try sample, plain reasons, large/simple concept, direct recovery, and binary usability/accessibility evidence. | EXCEEDS |
| Preserve human judgment | Four field states, exact versus normalized distinction, immutable evidence, and no legal-decision wording. | EXCEEDS |
| Exact warning nuance | Independent text, heading, and bounded presentation checks with Not verified where pixels cannot prove a property. | EXCEEDS |
| Handle difficult images where feasible | Bounded degradation fixtures, original-image preservation, quality state, resource controls, and re-upload behavior. | MEETS |
| Batch value | Gated exception-first Should objective preserves the stakeholder opportunity without risking the required core. | MEETS |
| Standalone and network-aware | No COLA dependency; blocked-egress, adapter, fallback, and deployment choices are BAIRD obligations. | MEETS |
| Source, README, documentation, and deployed URL | All submission items and clean-checkout/deployment provenance gates are explicit. | MEETS |
| Working core over ambitious incomplete features | Selected spirits checks are Must; batch and additional categories cannot weaken the core. | MEETS |

## Decisions confirmed as correct

1. Use a selected-check distilled-spirits profile rather than shallow all-category coverage.
2. Accept multiple label panels and expose coverage instead of pretending one image proves the container.
3. Keep manual structured entry for the prototype, paired with a zero-preparation Try sample path.
4. Keep final judgment with the human and preserve system findings independently.
5. Use Match, Review, Mismatch, and Not verified with deterministic summary precedence.
6. Make the side-by-side checklist and evidence location the leading desktop concept.
7. Keep warning detail separate and label heuristic or unprovable properties honestly.
8. Treat image quality as evidence quality, not as a regulatory defect.
9. Reject official seals, named employees, legal approval wording, decorative AI effects, and mockup values as fixture truth.
10. Gate batch after the single-submission release gate and restrict any claim to tested capacity.
11. Defer stack, model, host, egress, and preprocessing choices until BAIRD evidence exists.

## Remaining work that does not reopen Intake

The following are controlled downstream questions, not Intake defects:

- prove the valid-result and cold-start targets on candidate architectures;
- choose the exact reference schema and reduce manual-entry burden through I2R usability work;
- classify each warning check as deterministic, heuristic, or not provable;
- select and benchmark extraction, preprocessing, deployment, and egress behavior;
- define the adapter evidence contract and blocked-network fallback;
- compose the fixture/holdout corpus and keep expected outcomes independent;
- decide the gated batch go/no-go only after the core passes.

## Final revision confirmation

The final revision corrects the previously noted doubled-apostrophe typography in `AGENTS.md`, `assignment-source-baseline.md`, `design-reference-analysis.md`, and `INTAKE_RT_REMEDIATION.md`. I verified the corrected assignment example, requester-authority wording, design-provenance caveat, and remediation decisions. The changes are editorial only and do not alter authority, scope, success criteria, stakeholder fidelity, or any RT2 closure. The final revision still merits **CLEAR**.

## Final snapshot confirmation

I inspected the additional current-snapshot corrections. The latency clock now starts when the user activates Verify with locally valid inputs and ends only when the complete result is rendered and announced. It includes client preprocessing, upload, server work, response transfer, and browser rendering, while server-only timing is diagnostic. This is a stronger and more faithful measure of the stakeholder's five-second experience.

`docs/PROCESS.md` now distinguishes unresolved human-owned assumptions from named technical hypotheses that BAIRD must falsify before architecture approval. This removes the stage-gate ambiguity without treating unproven feasibility as settled. The assignment provenance now states only the supplied capitalization example. Any punctuation normalization is correctly labeled as reconstructed policy and remains Review unless later evidence supports a safer rule.

These corrections reduce ambiguity and do not reopen any RT2 finding. The exact final snapshot remains **CLEAR**.

## Binary verdict

**CLEAR**

Every material RT2 finding is closed in source, scope, success, and design-disposition evidence. The remediated Intake is fit to advance to BAIRD once the other two independent re-reviews also return CLEAR on this same revision.
