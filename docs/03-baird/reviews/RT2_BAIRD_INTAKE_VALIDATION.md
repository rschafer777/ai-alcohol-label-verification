REWORK_REQUIRED

# BAIRD RT2 Intake Validation

Review date: 2026-08-31

Role: Independent stakeholder, UX, usability, ambiguity, scope, and evaluator-fidelity reviewer

## Snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V1.sha256`
- Expected and observed SHA-256: `3327ecc8cb790eaf36155eb94a57a243cf8dff5182417281429fb484355bbf4e`
- Expected and observed hashed entries: 23
- Missing files: 0
- Hash mismatches: 0

The snapshot passed integrity verification before review. This report is outside the manifest, and no snapshotted file was modified.

## Decision basis

The Intake remains materially faithful to the take-home discovery in its product requirements. It correctly captures the fast routine-comparison need, broad technical-comfort range, human judgment, exact warning nuance, poor-image uncertainty, restricted-network context, future batch value, standalone prototype boundary, evaluator deliverables, and preference for a clean working core.

The corrected BAIRD definition is not consistently applied across the sealed package. The new governing document says BAIRD validates Intake against discovery only and does not select or prove architecture. Multiple active Intake artifacts still define BAIRD as the product and technical architecture stage, assign architecture research to it, and record completed architecture conclusions inside the Intake source of truth. The BAIRD validation document itself also promotes local OCR as committed scope. This contradiction makes the stage gate inaccurate and risks authorizing I2R from a mixed requirements and architecture baseline.

## Requirements-domain assessment

| Domain | Result | Material evidence |
|---|---|---|
| Stakeholder fidelity | PASS | `assignment-source-baseline.md` preserves the routine comparison burden, five-second adoption expectation, low-tech usability, human judgment, warning exactness, poor-image challenge, blocked outbound access, and batch demand without unnecessary personal details. |
| Primary workflow | PASS | `success-definition.md:14-21` defines an obvious first path, one-click sample, manual reference plus 1 to 6 panels, complete field evidence, uncertainty, actionable errors, and clean-checkout use. |
| Low-tech usability | PASS | Plain language, obvious actions, no hidden primary control, direct recovery, and no required OCR terminology are carried consistently into Intake scope and design disposition. |
| Accessibility | PASS | `scope-boundary.md:54-63` and `success-definition.md:81-90` define keyboard completion, visible focus, accessible names and errors, text plus icon status, AA contrast, 200 percent zoom, automated checks, and manual NVDA review. |
| Human judgment | PASS | Match, Review, Mismatch, and Not verified are distinct. Capitalization nuance routes to Review, system findings stay separate from human disposition, and approval or compliance language is prohibited. |
| Ambiguity and missing evidence | PASS | A clean summary requires every applicable selected check to have sufficient Match evidence. Missing panels, low confidence, unreadable regions, conflicting candidates, and unsupported physical checks cannot become clean. |
| Warning nuance | PASS | Exact wording, heading capitalization, bounded presentation checks, and physical-size limitation are separately expressed without claiming arbitrary photos prove every property. |
| Grok and Gemini disposition | PASS | `design-reference-analysis.md` classifies all nine references as inspiration, adopts useful checklist and evidence patterns, and rejects or quarantines official branding, named staff, legal actions, generated text, mockup data errors, copied stack choices, and decorative AI treatment. |
| Scope discipline | PASS WITH PROCESS EXCEPTION | The selected distilled-spirits profile, multi-panel input, legal non-authority, no COLA integration, and post-core batch gate fit the assignment. The local-OCR commitment and downstream architecture conclusions do not belong in this BAIRD gate. |
| Evaluator-facing deliverables | PASS | Repository, all source, README setup/run instructions, approach/tools/assumptions documentation, limitations, and a deployed URL remain explicit acceptance requirements. |
| Stage and authority consistency | FAIL | The corrected Intake-only BAIRD definition conflicts with current Intake and review artifacts that still make BAIRD responsible for architecture selection and feasibility evidence. See `RT2-BI-F001` and `RT2-BI-F002`. |

## Material findings

### `RT2-BI-F001` - HIGH - The sealed package uses two incompatible definitions of BAIRD

The governing definition at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:11` says BAIRD only validates whether Intake faithfully and completely represents discovery. It expressly excludes architecture, engineering patterns, languages, hosting, and build work packages.

Active snapshot artifacts still assign those excluded activities to BAIRD:

- `docs/intake/ingest-summary.md:46` says BAIRD must test latency, extraction, deployment, egress, licensing, regulatory capability, data flow, security, and batch feasibility before selecting the stack, OCR engine, rule architecture, or host.
- `docs/intake/open-questions.md:11-30` assigns OCR selection, preprocessing, normalization, deployment platform, self-contained inference, regulatory registry, threat model, batch feasibility, and extraction adapter contracts to BAIRD.
- `docs/intake/success-definition.md:71` requires BAIRD to select a deployment strategy and change architecture when the cold target is missed.
- `docs/reviews/intake/INTAKE_GATE_RESULT.md:28` authorizes `BAIRD product and technical analysis`.
- `docs/reviews/intake/RT3_INTAKE_REREVIEW.md:116` says BAIRD must benchmark architectures, choose extraction, produce a threat model, and define capability limits.
- Multiple Intake rereview and remediation rows use the same superseded architecture-stage meaning.

Impact: a reviewer cannot determine whether this BAIRD gate is evaluating discovery fidelity or approving technical feasibility. The mixed definition also makes research ownership, advancement conditions, and later I2R inputs ambiguous.

Required correction:

1. Make Beginning Assessment Intake Requirements Document the only current BAIRD definition across active Intake, gate, handoff, and process artifacts.
2. Reassign architecture, extraction, deployment, egress, security design, performance feasibility, and adapter research to I2R A&E or the appropriate later stage.
3. Preserve older reports as historical evidence if desired, but mark their former BAIRD stage terminology as superseded and non-authoritative for current stage ownership.
4. Regenerate the sealed Intake validation snapshot after the active authority and handoff surfaces agree.

### `RT2-BI-F002` - HIGH - Architecture conclusions are embedded in the Intake baseline being validated against discovery

The new BAIRD document says it does not select implementation architecture, but the snapshot includes post-Intake architecture conclusions as though they were Intake requirements:

- `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:77-82` puts `local OCR` into validated in-scope product requirements. The discovery only establishes that cloud endpoints may be blocked and that the prototype must work credibly in that context. It does not choose local OCR.
- `docs/intake/scope-boundary.md:23` replaces the provisional Intake bounds with exact values said to have been resolved by a prior technical BAIRD stage, including raw multipart bytes, cumulative pixels, and working-canvas size.
- `docs/intake/assumptions.md:13` records an equivalent-envelope warm architecture result, a selected always-running Machine, and downstream evidence paths instead of leaving the feasibility hypothesis open for I2R A&E.
- `docs/intake/assumptions.md:18` records a completed 30-fixture allocation and 37-case architecture benchmark.
- `docs/intake/assumptions.md:25` concludes that BAIRD supports warm-path feasibility and validation design.

These are not stakeholder or evaluator requirements derived from the assignment. Their technical merit is outside this review. Their presence in the active Intake source of truth violates the corrected stage boundary and can cause later stages to mistake prior implementation findings for discovery authority.

Required correction:

1. Restate network behavior as an outcome requirement, such as no unbounded or unusable failure when stakeholder egress blocks a dependency. Leave local versus external inference to I2R A&E.
2. Restore active Intake assumptions to discovery-level hypotheses and falsification needs. Move completed benchmarks, machine choices, byte arithmetic, and implementation-corpus conclusions to the appropriate later-stage records.
3. Keep only requester-approved product scope and acceptance outcomes in the active Intake boundary. Mark exact technical envelopes as downstream decisions with their own authority rather than retroactively attributing them to discovery.
4. Update `01_BAIRD_INTAKE_VALIDATION.md` so its in-scope list does not select local OCR or any other architecture.

## Confirmed strengths to preserve

- One obvious evaluator path plus a complete built-in sample.
- Structured reference values and 1 to 6 label panels.
- Evidence-linked, field-by-field review rather than a chatbot or opaque score.
- Safe distinction among exact Match, human Review, definite Mismatch, and Not verified.
- Exact warning wording and heading treatment with honest capability limits.
- Separate image-quality handling and actionable re-upload behavior.
- Neutral public branding and no official seal, employee identity, or legal approval action.
- Desktop-first accessibility with keyboard, focus, semantics, contrast, zoom, axe, and NVDA evidence.
- Batch preserved as valuable but unable to delay the required working core.
- Complete take-home repository, documentation, and deployed URL requirements.

## Advancement condition

Reconcile the stage definition across the active 23-file package, remove or relocate architecture conclusions from the Intake authority, and reseal the corrected snapshot. This review does not reject any architecture choice. It requires BAIRD to perform the Intake-only validation defined by the corrected process without silently approving downstream technical work.
