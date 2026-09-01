# Final Red-Team Signoff

Document control ID: LV-REL-003  
Revision: 2.5  
Date: 2026-09-01  
Status: Unanimous APPROVED_WITH_KNOWN_GATE; composite INCOMPLETE

## 1. Candidate under review

This record supersedes the pre-batch signoff. The current candidate includes single-label verification, client-managed batch verification for 1 to 300 applications, conservative warning analysis, bounded image recovery, current federal-readiness starter documents, and updated validation evidence.

The release manifest was regenerated from the exact staged Git tree after every actionable finding from the three independent RT reviews was corrected and regressed. Automatic-clear recognition remains failed and prevents corpus-UAT completion.

## 2. Current evidence baseline

- Root gate: PASS.
- Public seal: all 561 staged files represented by the manifest match the normalized Git index bytes; the manifest is the 562nd staged file and is excluded from its own contents.
- Python: 182 tests pass; Ruff and strict MyPy pass.
- Frontend: 46 tests pass; ESLint, strict TypeScript, and production build pass.
- Browser: Chrome core, Chrome privacy, and Edge core pass; the intentional duplicate Edge privacy run is skipped.
- Product corpus: 30 of 30 cases, 456 of 456 expected check rows, and 8 of 8 mutations pass with zero false-clean outcomes.
- Warm performance: 2.374-second p95 across 30 runs, 3.204-second maximum, and 1,466,724,352-byte peak combined parent and worker RSS.
- Cold readiness through first result: 7.532-second p95 across 5 runs and 1,578,123,264-byte peak combined parent and worker RSS.
- Batch performance: 10 applications in 18.665 seconds, 20 in 36.301 seconds, and 300 in 521.963 seconds, averaging 1.740 seconds per application with zero false-clean results and 847,986,688-byte peak combined parent and worker RSS.
- User-supplied image diagnostic: human oracle 33 pass and 17 do not pass; harness 0 pass, 45 review, and 5 do not pass; all 17 defects contained; zero false clearances; zero false deterministic rejections; automatic-clear recognition gate FAIL.

## 3. Independent verdicts

| Review | Scope | Verdict |
|---|---|---|
| Current requirements RT | Assignment, Intake, BAIRD, I2R, FRD, BI, source, README, corpus behavior, and validation traceability | APPROVED_WITH_KNOWN_GATE |
| Current technical and security RT | Architecture, runtime locality, security, privacy, warning logic, batch isolation, startup, performance, and evidence | APPROVED_WITH_KNOWN_GATE |
| Current evidence and hidden-test RT | Source bindings, manifest integrity, counts, regression, anti-overfitting controls, and active documentation | APPROVED_WITH_KNOWN_GATE |

## 4. Controlled disposition

The current frozen snapshot has unanimous internal approval with one known gate. It is not corpus-UAT complete because the automatic-clear recognition gate remains failed at 0 of 14 selected-profile visual passes. The package must not be represented as fully validated, release-complete, or ready for final requester acceptance until that gate is resolved or the requester explicitly accepts the documented human-review limitation. Source publication is authorized. Public deployment remains a later requester-controlled step.
