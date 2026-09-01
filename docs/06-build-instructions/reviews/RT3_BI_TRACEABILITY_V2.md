REWORK_REQUIRED

# RT3 BI Delivery, Traceability, QA/QC, and UAT Readiness Review V2

Reviewed snapshot: `docs/06-build-instructions/BI_SNAPSHOT_V2.sha256`  
Expected and observed manifest SHA-256: `c0b46218e2490faedb7ea17be96ce2175a3dbaa1ce62b836082c2d7432791c3f`  
Manifest entries: 73  
Integrity: two valid complete passes, 73 matched, 0 missing, 0 mismatched  
Unicode scan: zero U+2010 through U+2015 characters in the 73 sealed files

## Recomputed coverage

- Structure is complete and contiguous: 6 Epics, 12 stories, 12 work packages, and 78 tasks.
- The canonical ledger maps each `FR-001` through `FR-041` exactly once to one primary WP and the matching `T-001` through `T-041`.
- Joining the FRD upstream column to the canonical ledger reaches all 31 BRs. The 14 BQ decisions have planned implementation or validation work. All 16 components are covered, including the corrected `C-008` task.
- The WP dependency graph remains acyclic. Contract-first gates now make the Wave 2 and Wave 3 handoffs executable.
- Scope, requester authority, batch NO-GO, clean delivery obligations, final RT, UAT, and release limitations remain aligned with the cleared I2R/FRD.

## V1 finding closure

| Prior finding | Result | Evidence |
|---|---|---|
| `RT3-BI-V1-F001` local/final status conflict | CLOSED | LV-BI-003 lines 34 through 45 defines assertion and composite states; lines 83 through 86 define honest local readiness; lines 109 through 119 enumerate the only pending external assertions. |
| `RT3-BI-V1-F002` primary ownership and warning count | CLOSED | LV-BI-002 lines 33 through 43 now agrees with the exact ownership matrix at lines 45 through 71, labels support separately, and assigns exactly 10 warning policies plus registry completeness proof. |
| `RT3-BI-V1-F003` missing `C-008` task | CLOSED | LV-BI-002 line 35 adds owned `TASK-078` with dependencies, ordered orchestration, typed transfer, all-or-nothing delivery, cancellation, timing, and bypass evidence. |
| `RT3-BI-V1-F004` shared-source and contract handoffs | CLOSED | LV-BI-001 lines 40 through 65 defines writable roots, primary editors, integrators, reviewers, four contract gates, hash handoff, and change control. |
| `RT3-BI-V1-F005` defect/evidence contract | CLOSED | LV-BI-003 lines 121 through 156 defines assertion-level evidence, complete defect fields, independent closure, and ledger cross-validation. |

## Material findings

### RT3-BI-V2-F001 - HIGH - `WP-009` can exit without a proven container image

`TASK-053` requires a multi-stage non-root image, but the `WP-009` exit at `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md:40` weakens the required artifact to a reproducible local image only "when a local builder is available." The local DoD does not separately require a successful OCI build. The exact external assertion list at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:105-119` does not identify image construction as requester-gated and explicitly says every other assertion remains required locally.

This creates an unclassified path where `WP-009` and the local release candidate can be called ready without ever building the deployment artifact selected by ADR-008. A missing builder is a blocked prerequisite, not evidence that the image is reproducible.

Required remediation:

1. Require one clean, successful, hash-recorded OCI build and non-root/readiness smoke before `WP-009` and local readiness can pass.
2. If no builder is available, record BLOCKED or INCOMPLETE. Do not silently omit the proof.
3. Add the image build, image digest, runtime identity, readiness, and clean rebuild evidence to the local assertion ledger and local DoD.

### RT3-BI-V2-F002 - MEDIUM - One requester assertion overloads four independent acceptance gates

`T-033-A-REQUESTER-ACCEPTANCE` at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:117` combines requester code review, functional test, UAT acceptance, and final submission approval into one status. These are different decisions with different evidence and can complete at different times. A single assertion record cannot represent partial completion without either losing audit detail or leaving the whole gate semantically ambiguous.

Required remediation:

1. Give requester code review, functional test, UAT acceptance, and final submission approval separate stable assertion IDs, or define mandatory child assertions whose conjunction controls the parent.
2. Update the exact requester-gate count, `TASK-046`, `TASK-051`, `TASK-058`, `TASK-064`, and the evidence schema references so none of the four can be skipped or implicitly inferred.

## Decision

All five V1 RT3 findings are closed, and the V2 decomposition is materially stronger. Development is not yet authorized because the local package gate can omit the deployable OCI artifact and the requester acceptance evidence is not atomic. Correct these two delivery controls, reseal the package, and rerun the three BI reviews.
