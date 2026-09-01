REWORK_REQUIRED

# RT1 BAIRD Intake Validation

Review date: 2026-08-31

Role: Independent assignment and requirements-fidelity reviewer

## Snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V1.sha256`
- Expected and observed manifest SHA-256: `3327ecc8cb790eaf36155eb94a57a243cf8dff5182417281429fb484355bbf4e`
- Expected and observed hashed entries: 23
- Missing files: 0
- Hash mismatches: 0

The manifest and all 23 listed files passed verification before review. This report is outside the snapshot. No snapshotted file was modified.

## Review boundary

This review tests only whether the Beginning Assessment Intake Requirements Document accurately validates the Intake against the take-home discovery, requester decisions, and submission instructions. It does not assess or require a stack, OCR engine, model, host, benchmark result, resource envelope, security implementation, or other I2R A&E evidence.

## Material findings

### `RT1-BAIRD-F001` - HIGH - BAIRD selects an inference architecture while declaring architecture out of scope

`docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:11` correctly states that BAIRD does not select implementation architecture and that those decisions belong to I2R A&E. The same document then makes an architecture selection:

- line 39 says there is no required external inference service;
- line 69 says the authoritative path does not depend on outbound cloud inference;
- line 79 puts local OCR in scope;
- line 90 excludes external AI as a required dependency;
- line 118 treats the no-external-inference path as a passed Intake fact.

Those statements are not established discovery requirements. The stakeholder said outbound domains and cloud ML endpoints may be blocked. That creates a required constraint and failure scenario, but it does not itself choose local OCR or prohibit a bounded external path.

The active Intake confirms the decision is still open:

- `docs/intake/known-facts.md:44-48` says no OCR, model, library, or host is selected;
- `docs/intake/open-questions.md:17` asks I2R analysis to compare OCR or vision candidates;
- `docs/intake/open-questions.md:23` asks whether a self-contained or no-external-inference core can meet the contract;
- `docs/intake/source-requirements.md:65` explicitly permits an external inference service if its failure degrades safely;
- `docs/intake/initial-risk-notes.md:8` calls for local-first or bounded fallback analysis, not a preselected local implementation.

This is a substantive contradiction, not a preference disagreement. BAIRD cannot both defer architecture and validate one architecture as a requirement.

Required remediation:

1. Remove `local OCR`, `no required external inference service`, and equivalent implementation selections from the BAIRD determination.
2. Preserve the discovery-level requirement: restricted or blocked outbound access must not produce an unsafe, false-clean, indefinite, or unexplained result.
3. State that I2R A&E must compare and select local, external, or hybrid inference and prove latency, blocked-egress behavior, privacy, licensing, reproducibility, and deployment feasibility.
4. Keep the result and evidence contract independent of the selected extraction adapter.

### `RT1-BAIRD-F002` - HIGH - The active Intake and ownership map contain downstream technical conclusions from the superseded BAIRD process

The corrected BAIRD boundary is discovery-only, but current governing Intake files contain old architecture and research conclusions:

- `docs/intake/scope-boundary.md:22` labels the image envelope provisional, while line 23 immediately says BAIRD resolved exact raw-request, pixel, and working-canvas limits. Those are I2R A&E engineering decisions under the corrected process.
- `docs/intake/assumptions.md:13` says a warm architecture path is supported, cites `docs/baird/evidence/EVIDENCE_VALIDATION.md` outside this 23-file snapshot, selects one always-running Machine, and retains deployment proof gates.
- `docs/intake/assumptions.md:18` cites a 37-case BAIRD architecture benchmark as current treatment.
- `docs/intake/assumptions.md:25` says BAIRD supports warm-path feasibility and validation design.
- `docs/intake/ingest-summary.md:46` assigns latency, extraction, deployment, egress, licensing, data-flow, security, and stack selection to BAIRD.
- `docs/intake/open-questions.md:17-30` assigns multiple implementation research outputs to BAIRD even though `01_BAIRD_INTAKE_VALIDATION.md:11,122,130` assigns remaining engineering choices to I2R A&E.
- `docs/intake/INTAKE_DOCUMENT.md:193` still names a BAIRD egress decision.
- `docs/reviews/intake/INTAKE_GATE_RESULT.md:28` authorizes BAIRD product and technical analysis under the previous process definition.

The issue is not whether the old technical conclusions were good. They are outside this review. The issue is that BAIRD is claiming to validate a discovery-only Intake that is no longer discovery-only and is not self-contained within its sealed evidence set.

This creates three practical failures:

1. the same snapshot assigns technical decision authority to both BAIRD and I2R A&E;
2. load-bearing current treatments depend on evidence not included in the 23-entry seal;
3. I2R A&E could treat prior implementation choices as requirements instead of independently deriving the solution from the validated Intake.

Required remediation:

1. Remove downstream architecture measurements, platform choices, and old BAIRD evidence conclusions from the active Intake requirements surfaces.
2. Restore `ASM-007` as an unresolved, load-bearing technical hypothesis for I2R A&E to falsify before architecture approval.
3. Preserve the fixture and holdout requirement in `ASM-012`, but remove old architecture-benchmark closure claims from the discovery record.
4. Keep the image envelope provisional or express it as a requirement boundary to be finalized in I2R A&E. Do not retain an unreviewed implementation limit as Intake truth.
5. Reassign `RQ-001` through `RQ-014` according to the corrected process. Technical architecture, engineering, research, UX design, and security implementation outputs belong to I2R A&E or later governed stages, not BAIRD.
6. Update Intake gate and transition wording so BAIRD authorizes only three independent Intake-validation reviews. A unanimous CLEAR then authorizes I2R A&E.
7. Seal the corrected discovery-only Intake and BAIRD document together and rerun all three BAIRD reviews on that exact revision.

## Confirmed assignment fidelity that should not regress

No other material assignment omission was found. The corrected revision should preserve these strengths:

- The prototype is standalone and does not integrate with COLAs Online.
- Core scope is a selected-check distilled-spirits demonstration, not comprehensive TTB compliance.
- One verification accepts one structured reference record and 1 to 6 JPEG, PNG, or WebP panel images.
- Selected checks include brand, class or type, alcohol content, optional proof behavior, net contents, producer or bottler, conditional country of origin, government warning, panel coverage, and image quality.
- Missing, unreadable, weak, or conflicting evidence cannot produce a clean result.
- Match, Mismatch, Review, and Not verified preserve nuance and human judgment.
- The warning is decomposed into exact text and supportable presentation checks, while physical size remains limited by available evidence.
- The primary evaluator journey includes a complete built-in sample, obvious actions, evidence-linked results, plain reasons, and actionable error behavior.
- Browser-visible warmed p95 at or below 5.0 seconds is measurable and cannot be satisfied by a fast failure.
- Batch remains a gated Should objective that cannot delay or weaken the working single-submission core.
- Grok and Gemini artifacts remain non-authoritative inspiration and do not supply legal truth, fixture truth, branding, scope, or implementation decisions.
- Required submission deliverables remain complete: evaluator-accessible source repository, all source code, README setup and run instructions, brief approach/tools/assumptions/trade-offs/limitations documentation, and a deployed application URL.
- The requester keeps GitHub publication local until solution agreement.

## Gate conclusion

The product requirements are strong and cover the assignment. The BAIRD package is not yet coherent with the corrected process boundary. It must remove architecture selections and old downstream evidence from the active discovery-only record before I2R A&E can receive an authoritative requirements baseline.
