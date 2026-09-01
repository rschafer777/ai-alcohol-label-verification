# Final RT1 Requirements Fidelity and Traceability Review

Document control ID: LV-FINAL-RT1-001  
Revision: 1.0  
Date: 2026-09-01  
Reviewer role: RT1 requirements fidelity and traceability  
Review mode: Read-only review of the sealed local candidate  
Verdict: REWORK_REQUIRED

## 1. Reviewed snapshot

- Release manifest: `docs/10-release/RELEASE_MANIFEST.sha256`
- Required manifest SHA-256: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Observed manifest SHA-256: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Manifest entries checked: 489
- Missing entries: 0
- Hash mismatches: 0

The snapshot is internally intact. This review report is created after the freeze and is not represented as part of that sealed snapshot.

## 2. Review scope

The review compared the complete candidate against:

- the sanitized take-home assignment and stakeholder discovery;
- the requester process and writing instructions;
- Intake, BAIRD, I2R Architecture and Engineering, FRD, and Build Instructions;
- source, contracts, fixtures, tests, and implementation records;
- Validation Protocol results and machine-readable evidence;
- QA, QC, UAT, defect, README, dependency, release, and provenance records; and
- the exact external-gate treatment authorized for Git, OCI, deployment, final official-source recheck, and requester acceptance.

## 3. Requirements fidelity result

The product scope is faithful to the take-home assignment:

- The source baseline preserves the working prototype, matching workflow, five-second adoption need, simple UX, human judgment, warning exactness, degraded-image need, blocked-egress constraint, required repository contents, deployed URL, and evaluation criteria in `docs/intake/assignment-source-baseline.md`.
- The process carries 58 source requirements and 3 requester decisions into 31 BAIRD requirements, 14 architecture questions, 41 feature requirements, 41 test identifiers, and the Build Instructions work packages.
- The implementation remains a standalone distilled-spirits selected-check prototype with no COLAs Online integration, no legal approval behavior, no official TTB branding, no database, no durable queue, and no required runtime inference egress.
- Batch is explicitly documented as a valuable future enhancement and excluded from the time-boxed core. This is consistent with the assignment preference for a complete working core over incomplete ambition.
- The Grok and Gemini material is treated as non-authoritative design input. Useful side-by-side comparison, evidence focus, concise status, and warning-detail patterns were retained, while official seals, approval controls, decorative scanning, and generated regulatory text were rejected.
- README contains setup and run instructions, approach, technology choices, assumptions, trade-offs, limitations, validation commands, and the exact pending publication and deployment posture.
- The decisive corpus evidence records 30 of 30 cases, 456 of 456 expected result rows, 8 of 8 mutation controls, zero failures, and zero false-clean outcomes.
- Local performance evidence records warmed p95 of 1,978.469 ms over 30 complete runs and cold readiness through first result below 10,000 ms over 5 complete runs.
- The prohibited U+2010 through U+2015 scan is clean.

No product-scope drift, missing core source code, batch overreach, false legal authority, or false public deployment claim was found.

## 4. Blocking findings

### RT1-F001 - HIGH - The mandatory assertion-level validation ledger is absent

`docs/06-build-instructions/03_QA_QC_UAT_DOD.md:23-45` requires assertion-level status for every `T-001` through `T-041`, requires every local assertion to pass, and defines exact composite states. Lines 125-142 require each record to contain the mapped FR, stable assertion ID, scope, snapshot, time, command, inputs, expected and observed outcome, status, composite state, counters, artifact hashes, executor, reviewer, and defect linkage. Line 161 prevents `WP-012` closure until that ledger cross-validates with the defect ledger.

The candidate contains aggregate summaries, corpus evidence, performance evidence, test outputs summarized in prose, and a defect ledger. It does not contain the required assertion ledger for `T-001` through `T-041`. A repository search found no complete set of stable `T-NNN-A-*` assertion records or composite `FINAL_PASS` and `LOCAL_READY` states. `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md` therefore cannot substantiate its blanket local PASS at the granularity required by the approved BI.

Required closure:

1. Produce the complete assertion evidence ledger for all 41 tests.
2. Classify every local assertion as PASS, FAIL, NOT_RUN, or BLOCKED and every exact external assertion as `PENDING_REQUESTER_GATE` where applicable.
3. Include the mandatory evidence metadata and artifact hashes.
4. Cross-validate every failed and corrected assertion with `docs/09-qa-qc-uat/DEFECT_LEDGER.md`.
5. Reconcile the composite state of every test and the local candidate.

### RT1-F002 - HIGH - Mandatory independent first-time UAT is not evidenced

`FR-037` requires two independent reviewers who did not implement the UI to complete the Try sample journey within 3 minutes and the manual entry, upload, error correction, verification, evidence, and Start over journey within 7 minutes without facilitator help. `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:64-77` makes those sessions binary local UAT, and line 99 makes both independent reviewers a Local Definition of Done condition.

`docs/09-qa-qc-uat/UAT_RESULTS.md` records a general internal rehearsal and two automated Playwright journeys. It does not identify two independent non-implementers, record the two required manual sessions for each reviewer, provide elapsed times, record help or critical errors, or provide signed observation evidence. Requester UAT is a valid later external gate, but it does not replace this separate local `FR-037` evidence.

Required closure:

1. Run `UAT-001` and `UAT-002` with two independent non-implementers.
2. Record reviewer role, date, snapshot, elapsed time, help, errors, observed steps, and binary result.
3. Link the signed records to `T-037` in the assertion ledger.

### RT1-F003 - HIGH - Manual NVDA accessibility proof is not present

`FR-030` requires the keyboard, focus, live-region, labels and errors, non-color, contrast, zoom, Chrome, Edge, and NVDA contract. `docs/05-frd/02_FRD_TEST_TRACEABILITY.md` requires an automated report and signed manual checklist for `T-030`. `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:98` requires all manual scripts, including NVDA, to pass.

The candidate has Playwright, axe, Chrome, and Edge evidence. `docs/09-qa-qc-uat/UAT_RESULTS.md` gives a generic screen-reader PASS but provides no NVDA execution record, checklist, reviewer, date, environment, observed announcements, focus sequence, or defect disposition. Repository-wide NVDA references occur in requirements and planning documents, not in execution evidence.

Required closure:

1. Execute and record the manual NVDA smoke script on the frozen candidate.
2. Record browser, NVDA version, steps, expected and observed announcements, focus behavior, result, reviewer, and date.
3. Link the signed checklist to `T-030` in the assertion ledger.

### RT1-F004 - MEDIUM - The accepted fixture baseline records obsolete hashes

`docs/07-development/CONTRACT_BASELINE.md:63-65` identifies the accepted CG-003 fixture baseline with these hashes:

- corpus manifest: `cf55ca7c637c2e86ca23f7da19034edaaa906fb438b27b579e718941d2f87bb3`
- holdout seal: `7dc3c01e10ff2272da05229cdaba8ee0a81f61f94daf3842263858990f3d7bb0`
- mutation plan: `12bc5b89317a4d398cf336f682f4c1c71f0475c10abd7f5aa117a0d88d6f3e06`

The sealed release candidate contains:

- corpus manifest: `c7ba0668714867274de73cdf4828eaf2dbabc20f22e2339520783fdfae5810a6`
- holdout seal: `fa43f21aeaca64ce955970c6e03fc06a2fa4ddec08a2d7fa963d6c6af3f32830`
- mutation plan: `7b35bf40cb411443a49893ddd4eb5847d4e67d3d0c78d35f7414afa4b606e314`

The later `VAL-004` record honestly explains the oracle correction and reseal, but the contract baseline is not marked historical or superseded and contains no linked accepted change record. This creates conflicting provenance in a release package whose stated strength is exact traceability.

Required closure:

1. Mark the original hashes as historical and link them to the governed correction, or update the accepted baseline through the documented change process.
2. Record the final fixture, oracle-index, mutation-plan, and holdout-seal hashes in one authoritative final baseline.
3. Verify consumer acceptance and include the corrected record in the next release manifest.

### RT1-F005 - MEDIUM - Public documentation exposes unnecessary local filesystem identity

`BR-029` and `FR-035` require public-artifact data minimization and exclusion of unnecessary personal or private source details. The sealed package includes local absolute paths containing the workstation username and private Downloads location in:

- `docs/intake/design-reference-analysis.md:13-14`
- `docs/reviews/intake/RT1_REQUIREMENTS_FIDELITY.md:28,51-52`
- `docs/reviews/intake/RT2_UX_STAKEHOLDER.md:44-45`

Those paths are not needed to prove which Grok and Gemini references were reviewed. Stable artifact IDs, sanitized filenames, and hashes are sufficient.

Required closure:

1. Replace local absolute paths with sanitized artifact identifiers or repository-neutral filenames.
2. Repeat the public-artifact privacy and path-leak scan.
3. Regenerate the release manifest after correction.

## 5. External gates accepted as honestly pending

The following do not cause this REWORK_REQUIRED verdict because the final-review instruction explicitly permits them as external gates when honestly recorded:

- Git repository creation and clean-checkout replay;
- OCI clean build, rebuild, non-root identity, governed-asset, and readiness proof;
- public deployment URL and deployed edge, load, warm, cold, and shaped-network proof;
- final official TTB source recheck immediately before public release; and
- requester code review, functional testing, UAT, and final submission approval.

The candidate consistently labels these as BLOCKED or `PENDING_REQUESTER_GATE` and does not present them as passed.

## 6. Advisory observations

- The numbered lifecycle map is usable. The `docs/01-discovery` and `docs/02-intake` indexes correctly explain why approved historical source files remain under `docs/intake`.
- The legacy `docs/baird` package is clearly marked superseded and directs readers to the current numbered BAIRD and I2R authorities.
- Several historical stage documents retain pre-gate status labels such as Draft, Candidate, Pending review, or Active. Gate-result documents provide the current authority, so this is not independently blocking, but a concise status index would reduce evaluator confusion.
- The final candidate is substantially more complete than the assignment minimum. Before submission, the requester should consider whether all retained historical review iterations improve evaluator comprehension or create avoidable review volume.

## 7. Verdict and re-review entry condition

Verdict: REWORK_REQUIRED

Re-review may begin only after RT1-F001 through RT1-F005 are corrected, all affected validation and documentation checks pass, a new release manifest is generated, and every final reviewer evaluates the same corrected snapshot.
