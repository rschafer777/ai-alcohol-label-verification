# Final RT3 Evaluator UX, UAT, and Take-Home Quality Review

Document control ID: LV-FINAL-RT3-001  
Revision: 1.0  
Date: 2026-09-01  
Reviewer role: RT3 evaluator UX, UAT, and take-home quality  
Review mode: Read-only review of the sealed local candidate  
Verdict: REWORK_REQUIRED

## 1. Reviewed snapshot

- Release manifest: `docs/10-release/RELEASE_MANIFEST.sha256`
- Required manifest SHA-256: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Observed manifest SHA-256: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Manifest entries checked: 489
- Missing entries: 0
- Hash mismatches: 0

The sealed snapshot is internally intact. This review report was created after the freeze and is not represented as an entry in that snapshot.

## 2. Review coverage

The review compared the complete local candidate against:

- the sanitized assignment, stakeholder needs, deliverables, and evaluation criteria;
- the Grok and Gemini design-reference analysis and its recorded dispositions;
- the approved I2R evaluator workflow and accessibility contract;
- the FRD, test traceability, QA, QC, UAT, and Local Definition of Done;
- the implemented frontend, styles, component tests, Playwright tests, and error behavior;
- the README first-run path, approach, limitations, and pending delivery statements; and
- the validation and release-candidate summaries.

Git publication, public deployment, and requester UAT were treated as permitted pending gates when they were stated accurately. No deployment or external runtime was evaluated.

## 3. Evidence-backed UX and take-home assessment

### 3.1 First-time and older-user workflow

The implemented interface is materially aligned with the stakeholder need for a clean and obvious workflow for users with varied technical comfort in `docs/intake/assignment-source-baseline.md:21-23` and the approved first-time experience in `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:10`.

Positive implementation evidence includes:

- a prominent `Try the built-in sample` action and plain explanation of the human review role in `frontend/src/features/intake/IntakeForm.tsx:118-121`;
- two visible intake steps, explicit panel count, file guidance, preview controls, Verify, and Start over in `frontend/src/features/intake/IntakeForm.tsx:129-254`;
- minimum 44 pixel form controls and a strong visible focus treatment in `frontend/src/app/styles.css:13-16`;
- focus movement to validation errors and the result summary in `frontend/src/app/App.tsx:109,173,261`;
- elapsed time, cancellation, typed retry, and safe error actions in `frontend/src/app/App.tsx:73-100,280-297`; and
- eight component tests covering first-error focus, conditional fields, the complete sample, cancellation, retry, six panels, evidence ambiguity, and truthful fallback text in `frontend/tests/app.test.tsx:25-210`.

No source-level blocker was found that would obviously prevent an older or low-technical-comfort evaluator from completing the core workflow. The required independent user evidence needed to prove that conclusion is absent, as described in RT3-F001.

### 3.2 Evidence and human judgment

The result workspace keeps system findings separate from the human decision and makes evidence inspectable:

- the UI says `You make the final decision` in `frontend/src/features/verification/ResultWorkspace.tsx:152`;
- each check exposes a textual state, reason, capability, and evidence action, with separately named alternatives in `frontend/src/features/verification/ResultWorkspace.tsx:32-104`;
- the viewer supports original evidence, reversible zoom and rotation, focused polygons, and a clearly labeled display-only enhancement in `frontend/src/features/verification/ResultWorkspace.tsx:163-199`;
- session notes and disposition are explicitly separate from immutable system findings in `frontend/src/features/verification/ResultWorkspace.tsx:221-239`; and
- the shell states that the prototype is not connected to COLA, does not issue legal decisions, and does not save the session in `frontend/src/app/App.tsx:351-357`.

This is consistent with the design-reference decisions to use side-by-side evidence, four textual states, and human review while rejecting official identity, legal approve or reject authority, hidden matches, and decorative scan behavior in `docs/intake/design-reference-analysis.md:29-67,85-108`.

### 3.3 Batch scope and limitations

Batch is not falsely implied complete. The README explicitly excludes batch from the time-boxed core in `README.md:18`, the FRD requires no batch route, UI, or claim in `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:58`, and the release status records no batch upload or persistent queue in `docs/10-release/RELEASE_CANDIDATE_STATUS.md:27,38`.

The product instead delivers the complete single-submission core preferred by `ASG-041`. The README also states the important OCR, physical measurement, legal-authority, persistence, and scope limitations in `README.md:128-147`.

### 3.4 Local evaluator materials

The README provides prerequisites, exact PowerShell setup and run commands, the fastest sample path, quality commands, architecture, assumptions, limitations, and honest pending Git and deployment statements in `README.md:20-48,63-102,104-168`. The decisive evidence reports 30 of 30 corpus cases, 456 of 456 expected rows, 8 of 8 mutation controls, zero false-clean results, and warm p95 of 1.98 seconds in `README.md:87` and `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md:28-33`.

The local take-home materials are substantial and navigable. They are not yet evaluator-ready under their own UAT and accessibility acceptance rules because required execution evidence is missing and the aggregate status documents currently overstate those gates.

## 4. Blocking findings

### RT3-F001 - HIGH - Required independent first-time UAT is not evidenced

`FR-037` requires two independent reviewers who did not implement the UI to complete both the Try sample journey within 3 minutes and the manual entry, upload, induced error correction, verification, evidence, and Start over journey within 7 minutes, with no facilitator help and no critical error. See `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:59`. The QA and UAT authority repeats the two independent first-time sessions at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:20,68-77` and makes both reviewer passes a Local Definition of Done condition at line 99.

`docs/09-qa-qc-uat/UAT_RESULTS.md:6-27` records an aggregate internal rehearsal and states that 2 of 2 Playwright journeys passed. It does not provide two independent non-implementer records, elapsed times, observed required steps, help received, critical errors, reviewer roles, or witnessed results. The Playwright suite contains one named sample journey at `frontend/e2e/labelverify.spec.ts:12-56`; running that test in Chrome and Edge does not create two independent human sessions and does not exercise the required first-time manual journey.

As a result, this review cannot source-validate that a nontechnical older agent can operate both required workflows without help. Favorable source design and automated tests reduce implementation risk, but do not satisfy the explicit UAT oracle.

Required closure:

1. Run `UAT-001` and `UAT-002` on this candidate with two independent non-implementers representative of the low-technical-comfort audience.
2. Record reviewer role, snapshot identity, environment, elapsed time, help, critical errors, every required observed step, and binary outcome.
3. Correct and regress any failure, then link the final records to `T-037` and the release evidence.

### RT3-F002 - HIGH - Required manual accessibility proof is absent

The approved UX contract requires complete keyboard operation, visible focus, a usable 200 percent zoom layout at 1024 by 768, controls suitable for older users and reduced precision, and automated axe plus manual keyboard and NVDA smoke checks in `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:84-92`. `FR-030` makes all manual scripts part of the binary pass condition in `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:52`. The Local Definition of Done repeats keyboard, focus, zoom, Chrome, Edge, and NVDA at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:98`.

The code contains favorable accessibility features, including semantic controls, live regions, visible focus, minimum control sizing, reduced-motion handling, responsive layout, 200 percent image zoom, and forced-color support in `frontend/src/app/styles.css:13-16,77-95,118-127,170-186`. The Playwright sample performs axe checks and runs in Chrome and Edge, but it does not execute NVDA, a manual keyboard script, or the required 200 percent page-zoom and 1024 by 768 inspection. `docs/09-qa-qc-uat/UAT_RESULTS.md:23-27` states a generic keyboard and screen-reader PASS without an execution record, operator, browser and NVDA versions, expected and observed announcements, focus sequence, zoom result, date, or signed checklist.

Required closure:

1. Execute the governed manual keyboard, focus, 200 percent zoom, and NVDA scripts against the frozen candidate.
2. Record environment and assistive-technology versions, reviewer role, required steps, expected and observed behavior, defects, disposition, date, and binary result.
3. Link the signed checklist and automated axe output to `T-030` and the release evidence.

### RT3-F003 - MEDIUM - Release summaries overstate UX and accessibility completion

`docs/10-release/RELEASE_CANDIDATE_STATUS.md:10,21` says local accessibility and test evidence are complete. `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md:10,30-32` says all locally executable stop-ship assertions passed and records integrated browser and accessibility PASS. `docs/09-qa-qc-uat/UAT_RESULTS.md:6,23-27` records internal rehearsal and screen-reader PASS.

Those claims are not supported by the independent UAT and manual accessibility artifacts required by `FR-037`, `FR-030`, and the Local Definition of Done. Requester UAT may remain pending, but it is separate from the missing local independent sessions and manual accessibility proof.

Required closure:

1. Add the missing execution evidence and preserve the PASS statements only if all required checks pass.
2. Otherwise change the affected local statuses to incomplete or blocked until the evidence exists.
3. Regenerate and verify the release manifest after the corrected package is frozen.

## 5. Advisory observations

- The current integrated Playwright suite is one complete sample test executed in Chrome and Edge. Adding live manual-upload, invalid-input correction, cancel, retry, timeout, and 200 percent page-zoom journeys would make regressions in the evaluator path easier to detect. Existing component tests cover many of these behaviors, so this is advisory once the required human UAT is recorded.
- `models/` is intentionally ignored, and the clean setup path runs `ops/fetch_models.py`. The README should state plainly that this one-time setup step requires network access, distinguish setup egress from restricted runtime egress, and provide actionable recovery guidance for a blocked model download.
- UAT records can identify independent reviewers by role or stable pseudonymous identifier. Personal names are not needed to prove independence, timing, observation, and outcome.
- Git publication, public deployment, and requester UAT are accurately presented as pending and do not independently cause this verdict.
- OCI proof is also honestly recorded as blocked. This review did not treat unavailable external runtime proof as evidence that the local UI itself is defective.

## 6. Verdict and re-review condition

Verdict: REWORK_REQUIRED

The implementation presents a strong, appropriately scoped evaluator experience, makes evidence and human judgment clear, and does not imply completed batch capability. CLEAR requires source-valid proof of the two independent first-time no-help UAT sessions, the governed manual accessibility checks, and reconciled release-status claims on one newly sealed snapshot.
