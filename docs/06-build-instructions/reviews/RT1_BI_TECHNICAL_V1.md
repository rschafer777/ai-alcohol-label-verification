REWORK_REQUIRED

# RT1 BI Technical Build-Readiness Review V1

Reviewed snapshot: `docs/06-build-instructions/BI_SNAPSHOT_V1.sha256`  
Expected and observed manifest SHA-256: `d11c35cab49b4f557aff81c99825e9e5297c7c3248da67c549e41a754661f357`  
Manifest entries: 68  
Seal verification: two complete passes, 68 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015 scan: 0 findings

## Material findings

### RT1-BI-V1-F001 - HIGH - The local Definition of Done cannot coexist with the requester-controlled release gates

The mandatory protocol says every `T-001` through `T-041` must be PASS and that NOT RUN or BLOCKED cannot satisfy DoD at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:25-35`. The local DoD repeats that all 41 feature requirements and tests must be PASS at `:70-75`, and `WP-012` requires all 41 tests plus local DoD at `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md:43`.

The same QA document correctly says GitHub and deployment authorization are requester-controlled and keeps repository clean-checkout proof, public deployment, deployed warm/cold/network/edge tests, and the final regulatory recheck pending at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:94-105`. Those are not optional details. They are required portions of `T-031`, `T-033`, `T-038`, and `T-040`. Therefore the local candidate cannot truthfully record all 41 tests PASS while those portions are still PENDING, yet NOT RUN and BLOCKED are forbidden by the local DoD.

This makes `WP-012` impossible to complete without either making a false PASS claim or performing actions the requester has not authorized.

Required remediation:

1. Define separate local-development and final-release gate states without weakening any FR. A composite test may record all local assertions PASS and named external assertions `PENDING_REQUESTER_GATE`; the complete `T-NNN` remains not finally PASS until all required assertions pass.
2. Replace the local 41-of-41 PASS statement with a binary local-readiness rule that requires every locally executable assertion to pass, zero unclassified gaps, and only the enumerated requester-controlled assertions to remain pending.
3. Update `TASK-073`, `WP-009`, `WP-010`, `WP-012`, the evidence schema, and the final release rule so no agent can convert a pending deployed or repository assertion into PASS.

### RT1-BI-V1-F002 - HIGH - Parallel implementation has no directory ownership or shared-file mutation contract

LV-BI-001 assigns broad responsibilities at `docs/06-build-instructions/01_BUILD_INSTRUCTIONS.md:29-38` and lists the repository tree at `:40-76`, but it does not assign writable roots or shared-file ownership to the four roles. Wave 2 explicitly runs three packages in parallel at `:82-92`. Contract, registry, fixture, test, documentation, configuration, and generated-client changes can therefore overlap without a defined author, integrator, or merge order.

Work-package ownership is not enough to resolve shared paths such as `backend/labelverify/contracts`, frontend API contracts, `fixtures`, root lockfiles, `scripts`, cross-layer `tests`, `ops`, and development evidence. The package requires cross-role review but does not say who may edit each shared source of truth or how a dependent agent receives an approved contract revision.

Required remediation:

1. Add a directory and governed-file ownership matrix covering every planned root and each shared contract, registry, error, lockfile, configuration, test, and evidence location.
2. Give every shared source one primary editor and one integrator, with explicit review and handoff rules for cross-owner changes.
3. Add contract-first subgates for parallel work so `WP-005` receives the approved `WP-007` sample contract and backend/frontend work consumes the same versioned request, result, evidence, and error contracts.

### RT1-BI-V1-F003 - MEDIUM - The work-package ledger contradicts its own primary ownership and registry count

The ledger column is named `Primary FRs` at `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md:30`. `WP-009` claims primary ownership of `FR-011`, `FR-028`, and `FR-031` at line 40, while the canonical ownership matrix assigns `FR-011` to `WP-003`, `FR-028` to `WP-004`, and only `FR-031` to `WP-009` at lines 49 through 69. BI exit criteria require one primary work package and test owner for each FR at `docs/06-build-instructions/01_BUILD_INSTRUCTIONS.md:143-149`.

The same ledger tells `TASK-010` to implement 11 warning-related policies at `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md:33`, but the authoritative 19-check registry contains 10 `warning_*` checks. The remaining 9 checks are 7 selected fields plus panel coverage and image quality.

These contradictions can produce duplicate ownership, a nonexistent warning policy, and divergent completion evidence.

Required remediation:

1. Make the work-package rows and the ownership matrix agree on exactly one primary WP per FR. Label other packages as supporting and name their required sub-evidence.
2. Change the warning task to the exact 10 registry checks and require a generated or tested registry-to-policy completeness assertion.

## Verified strengths

- All 12 work packages and all 77 tasks are unique and contiguous.
- All 41 FRs map exactly once to a primary WP and matching `T-NNN` in the ownership matrix.
- Dependencies preserve the cleared modular monolith, reference-blind extraction, killable child boundary, evidence contract, security controls, privacy posture, and no-false-clean rule.
- The fixture and holdout owner is independent from production comparison and aggregation.
- Release limitations, cold-start work, deployed proof, documentation, accessibility, and security evidence are identified rather than claimed complete.
- Scope excludes batch, accounts, persistence, COLA integration, required external inference, and legal disposition behavior.

## Gate decision

BI is not build-ready on V1. Correct the impossible local/final gate model, define directory and shared-source ownership, reconcile primary ownership, and fix the warning-policy count before implementation begins.
