REWORK_REQUIRED

# RT3 BI Delivery, Traceability, QA/QC, and UAT Readiness Review V1

Reviewed snapshot: `docs/06-build-instructions/BI_SNAPSHOT_V1.sha256`  
Expected and observed manifest SHA-256: `d11c35cab49b4f557aff81c99825e9e5297c7c3248da67c549e41a754661f357`  
Manifest entries: 68  
Integrity result: two complete passes, 68 matched, 0 missing, 0 mismatched  
Unicode result: zero U+2010 through U+2015 characters across all 68 sealed files

## Coverage recomputation

- Structure is complete and contiguous: 6 Epics, 12 stories, 12 work packages, and 77 tasks. No identifier gap or unexpected identifier was found.
- The canonical ownership matrix contains each `FR-001` through `FR-041` exactly once and pairs it with the matching `T-001` through `T-041`.
- Joining the FRD upstream column to that canonical matrix reaches all 31 `BR` requirements. No BR is orphaned.
- All 14 `BQ` decision topics have planned work: OCR and preprocessing in `WP-003`; contracts and limits in `WP-001`, `WP-004`, and `WP-005`; policies and warning boundaries in `WP-002`; UX in `WP-005`, `WP-006`, and `WP-011`; data lifecycle and operations in `WP-004` and `WP-009`; dependency and deployment controls in `WP-001`, `WP-009`, and `WP-010`; validation in `WP-007` and `WP-008`; and batch NO-GO in `WP-010`. The component-boundary topic is not fully executable because of finding RT3-BI-V1-F003.
- All 16 component IDs are reachable through the FRD. Fifteen have identifiable production or validation tasks. `C-008` does not have an explicit implementation task.
- The work-package dependency graph has no cycle. Its declared topological sequence is broadly viable, subject to the parallel contract handoff gap in RT3-BI-V1-F004.
- QA/QC includes static, unit, contract, integration, E2E, non-functional, UAT, and release layers. UAT has binary scenarios, independent witnesses, timing bounds, accessibility coverage, retry, cancellation, reset, ambiguity, and bad-image behavior.
- The package preserves the release boundary: Git initialization, repository publication, deployment, public URL, deployed probes, final regulatory recheck, and requester acceptance remain requester-controlled.

## Material findings

### RT3-BI-V1-F001 - HIGH - Local completion requires final tests that the same package keeps pending

The mandatory protocol requires every `T-001` through `T-041` to be PASS and says NOT RUN or BLOCKED cannot satisfy DoD at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:25-35`. The local DoD repeats 41 of 41 PASS at `:70-75`. `TASK-073` and the `WP-012` exit also require all 41 tests and the local DoD at `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md:43`.

The same QA document correctly keeps repository clean-checkout proof, public deployment, deployed performance and public-edge probes, the final regulatory recheck, and requester acceptance pending until authorization at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:94-105`. Those are required assertions within `T-031`, `T-033`, `T-038`, and `T-040`, not optional enhancements. The local candidate therefore cannot truthfully satisfy its own 41-PASS rule.

Required remediation:

1. Define separate local-readiness and final-release states without weakening any FR or test.
2. Permit only named external assertions to use a status such as `PENDING_REQUESTER_GATE`; the composite `T` remains not finally PASS until those assertions pass.
3. Update `TASK-073`, `WP-009`, `WP-010`, `WP-012`, the evidence schema, and the release rule so local evidence cannot be promoted into a deployed or repository PASS claim.

### RT3-BI-V1-F002 - HIGH - Primary FR ownership contradicts the canonical matrix

The ledger labels its column `Primary FRs` at `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md:30`, but several work-package rows conflict with the exact ownership table at `:45-71`:

- `WP-005` claims `FR-001` through `FR-006`, although the matrix assigns `FR-002` to `WP-007`.
- `WP-009` claims `FR-011`, `FR-028`, and `FR-031`, although the matrix assigns the first two to `WP-003` and `WP-004`.
- `WP-012` claims all 41, although it is the validation and release-candidate package rather than the primary implementation owner.

In the same ledger, `TASK-010` says it implements 11 warning-related policies at line 33. The sealed 19-check registry has exactly 10 `warning_*` rows. These discrepancies violate the one-primary-owner exit rule in `docs/06-build-instructions/01_BUILD_INSTRUCTIONS.md:141-149` and can produce duplicate completion evidence or a nonexistent policy.

Required remediation:

1. Make every work-package row agree with the canonical matrix on exactly one primary WP per FR.
2. Mark cross-cutting packages as supporting and identify the exact supporting assertion or artifact they own.
3. Correct `TASK-010` to the exact 10 warning checks and require an executable registry-to-policy completeness test.

### RT3-BI-V1-F003 - HIGH - The central orchestrator component has no implementation task

`C-008` owns ordered pipeline execution and all-or-nothing result delivery at `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:71`. The planned repository even reserves `backend/labelverify/orchestration` at `docs/06-build-instructions/01_BUILD_INSTRUCTIONS.md:42-53`. No task in `WP-002`, `WP-003`, or `WP-004` explicitly implements this component, wires the ordered child-side decode through aggregation path, or proves that only a complete result crosses the parent boundary. `FR-036`, which names `C-008`, is assigned to documentation package `WP-010` and cannot fill that production gap.

The Wave 3 exit statement says the real pipeline integrates, but an exit statement is not an owned implementation task. This leaves the central integration responsibility implicit and makes component, task, owner, and evidence traceability incomplete.

Required remediation:

1. Add an explicit task under the appropriate backend package to implement `C-008`, including ordered stages, typed completion/error transfer, all-or-nothing delivery, cancellation ownership, and stage timing.
2. Name its owner, dependent contracts, focused tests, FR/T mappings, and integration evidence.
3. Add an architecture-boundary test proving routes and UI cannot bypass the orchestrator or recompute its result.

### RT3-BI-V1-F004 - HIGH - Parallel delivery lacks shared-source ownership and contract handoff gates

The role table assigns broad responsibilities at `docs/06-build-instructions/01_BUILD_INSTRUCTIONS.md:29-38`, but it does not assign writable roots, governed shared files, a primary editor, or an integrator. Parallel work is authorized at `:80-92`. Shared contract schemas, the error registry, selected-check registry, fixture/sample manifests, root lockfiles, generated client types, cross-layer tests, operations files, and evidence indexes can therefore receive conflicting edits.

The dependency detail is also underspecified. Wave 2 lists `WP-005` and `WP-007` in parallel, while `WP-005` depends on the `WP-007` sample contract at `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md:36-38`. The general instruction to use committed contracts or generated mocks does not say which revision is approved, who publishes it, or which task cannot proceed before the handoff.

Required remediation:

1. Add a directory and governed-file ownership matrix covering every planned root and every shared contract, registry, configuration, lockfile, fixture, test, and evidence location.
2. Define a primary editor, integration owner, required reviewer, and cross-owner change rule for each shared source.
3. Add task-level contract-first handoff gates for the sample, request, result, evidence, and error contracts before dependent parallel implementation proceeds.

### RT3-BI-V1-F005 - MEDIUM - The defect record and composite evidence contracts are not audit-complete

The defect loop at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:38-53` defines severities and regression stages, but it never defines the required defect record. The evidence minimum at `:107-121` includes a linked defect and regression ID only when applicable. It does not define assertion-level identity or status for composite tests, nor require a defect's reproduction fixture/steps, source FR/T, severity rationale, owner, affected build, fix revision, closure reviewer, and state timestamps.

Without those fields, `TASK-074` and `TASK-075` cannot prove that the same failure was reproduced, corrected, independently reviewed, and closed. The omission is especially material for the split local/final assertions in finding RT3-BI-V1-F001.

Required remediation:

1. Define a versioned defect schema with a stable ID, FR/T/assertion links, severity and rationale, environment/build, reproduction input or fixture, expected and observed behavior, owner, lifecycle timestamps/status, fix revision, regression test, evidence hashes, and independent closer.
2. Extend the evidence schema with `assertionId`, execution scope such as local or deployed, and an explicit `PENDING_REQUESTER_GATE` status permitted only for the enumerated external assertions.
3. Require the defect ledger and test evidence ledger to cross-validate before `WP-012` closes.

## Gate decision

The sealed BI V1 package has strong end-to-end requirement coverage and a sound overall decomposition, but it is not yet safe to execute. The impossible local/final gate, contradictory primary ownership, missing orchestrator task, unresolved shared-source handoffs, and incomplete defect/evidence contracts must be corrected and sealed for three independent re-reviews before Development begins.
