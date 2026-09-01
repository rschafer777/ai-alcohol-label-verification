REWORK_REQUIRED

# BAIRD Red Team 3 Intake Validation

## Review boundary

This review tested only whether the sealed Intake faithfully, completely, and testably represents the take-home discovery and requester decisions. It did not require or evaluate architecture, engineering implementation, security implementation, model selection, deployment feasibility, or benchmark proof. Those subjects belong to later stages under the corrected process definition.

## Sealed snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V1.sha256`
- Expected manifest SHA-256: `3327ecc8cb790eaf36155eb94a57a243cf8dff5182417281429fb484355bbf4e`
- Observed manifest SHA-256: `3327ecc8cb790eaf36155eb94a57a243cf8dff5182417281429fb484355bbf4e`
- Expected entries: 23
- Observed entries: 23
- Missing entries: 0
- Hash mismatches: 0

## Material findings

### RT3-BRD-F001 - HIGH - The BAIRD determination promotes architecture choices into validated discovery requirements

`docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:11` correctly states that BAIRD does not select architecture, hosting, languages, or engineering patterns. The same document then validates "no required external inference service" at line 39, makes an outbound-cloud-independent path a non-functional requirement at line 69, declares "local OCR and deterministic comparison" in scope at line 79, excludes external AI as a required dependency at line 90, and marks that network interpretation PASS at line 118.

The discovery says the government network blocks outbound traffic to many domains and instructs the designer to keep that constraint in mind. It does not require local OCR, prohibit an external inference design, or decide a fallback architecture. `DEC-001` through `DEC-003` do not authorize local OCR. The sealed Intake itself still treats local versus external inference as an unresolved technical question in `docs/intake/open-questions.md:17` and `docs/intake/open-questions.md:23`.

This is material because a CLEAR verdict would make an unselected implementation strategy appear to be a discovery-backed product requirement while the corrected BAIRD definition expressly forbids that decision.

Required remediation:

1. Remove local OCR and no-required-external-inference assertions from the validated requirements and boundaries.
2. Preserve the discovery-level outcome only: the standalone prototype must account for restricted outbound access and must fail safely and honestly if a selected dependency is unavailable.
3. Leave inference location, provider, fallback, egress, and deployment choices to the named later-stage owner.

### RT3-BRD-F002 - HIGH - The sealed Intake is not a discovery-only, self-contained handoff under the corrected stage model

The BAIRD document says it assessed every current Intake artifact at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:21`, but current governing Intake files contain results from a different, architecture-oriented meaning of BAIRD:

- `docs/intake/assumptions.md:13` claims warm architecture support, cites `docs/baird/evidence/EVIDENCE_VALIDATION.md`, and requires an always-running Machine. That cited evidence is outside this 23-entry seal.
- `docs/intake/assumptions.md:18` claims closure from a 30-fixture implementation allocation and a 37-case BAIRD architecture benchmark.
- `docs/intake/assumptions.md:25` summarizes retained BAIRD feasibility evidence as an Intake result.
- `docs/intake/scope-boundary.md:23` replaces the provisional Intake envelope with exact byte, pixel, multipart, and working-canvas limits said to have been resolved by BAIRD.
- `docs/intake/clarification-log.md:19` records a BAIRD author changing the attested Intake latency contract.

The active handoff also assigns technical analysis to BAIRD even though the corrected definition assigns it to I2R A&E, FRD, and BI. Examples include `docs/intake/ingest-summary.md:46`, `docs/intake/open-questions.md:17-29`, `docs/intake/source-requirements.md:66`, `docs/intake/success-definition.md:71`, and `docs/reviews/intake/INTAKE_GATE_RESULT.md:28`.

This is material for source traceability and advancement readiness. A reviewer cannot determine from the sealed discovery package which requirements were authorized during Intake, which were later technical findings, and which downstream stage now owns unresolved work. The package also depends on an out-of-snapshot evidence file while claiming exact sealed validation.

Required remediation:

1. Restore the active Intake source of truth to discovery, requester decisions, product boundaries, measurable outcomes, and unresolved technical questions only.
2. Move exact implementation envelopes, benchmark results, Machine policy, and architecture evidence to later-stage records without back-writing them as Intake facts.
3. Retarget active technical research and decision ownership from BAIRD to I2R A&E, FRD, or BI under the corrected process.
4. Treat earlier review reports as historical evidence, or mark their old BAIRD terminology superseded, without rewriting the historical verdicts as if they used the corrected definition.
5. Reseal the corrected Intake and BAIRD document, then rerun all three BAIRD reviews against that one snapshot.

## Checks that passed

- The 58 `SRC-NNN` rows are unique and contiguous.
- The stated provenance totals reconcile: 21 STATED, 8 VERIFIED, 25 RECONSTRUCTED, and 4 PROPOSED.
- All referenced `ASG`, `USR`, `REG`, and `DEC` identifiers resolve to definitions in the sealed package.
- The required repository, all-source, README, approach/tools/assumptions documentation, and deployed-URL obligations are present in `SRC-050` through `SRC-054`.
- The selected-check distilled-spirits scope, multi-panel input, human judgment, warning-check limits, Try sample, batch boundary, accessibility outcomes, uncertainty behavior, and working-core priority are testable at the Intake level.
- Grok and Gemini material remains classified as non-authoritative design evidence.
- No missing assignment deliverable was found.
- No prohibited Unicode dash character was found in the 23 sealed entries.

## Gate decision

The source inventory and assignment coverage are strong, but the sealed package cannot advance while it both forbids architecture decisions in BAIRD and validates or imports those decisions as Intake truth. Correct the stage authority and discovery boundary, reseal, and rereview.

REWORK_REQUIRED
