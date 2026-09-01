# Build Instructions

Document control ID: LV-BI-001  
Revision: 1.0  
Date: 2026-09-01  
Status: Candidate for BI review  
Authority: `I2R_FRD_SNAPSHOT_V5.sha256`, LV-I2R-001 through LV-I2R-008, LV-FRD-001, and the 19-check registry

## 1. Build objective

Build one complete, locally runnable LabelVerify take-home prototype that implements all core Must requirements and the bounded 1 to 300 application batch extension without adding COLA integration, persistence, official TTB branding, legal approval language, or a required external inference service.

The implementation target is a same-origin modular monolith:

- React 19.2 and strict TypeScript frontend;
- Python 3.12, FastAPI, Pydantic, and Uvicorn backend;
- RapidOCR 3.4.2 and ONNX Runtime 1.22.1 CPU behind an extraction port;
- deterministic comparison, warning, and aggregation modules;
- one killable supervised child job for full decode through aggregation;
- no application database, durable queue, account, or server session;
- one multi-stage OCI image for the eventual public deployment.

## 2. Development authority and boundary

Local implementation may start only after this BI package receives three CLEAR verdicts on one immutable snapshot. No Git initialization, GitHub repository, publication, or deployment is authorized by this document. Those actions remain requester-controlled release steps.

Implementation must not alter the cleared requirements or architecture to make tests pass. A discovered conflict follows change control in Section 9.

## 3. Delivery roles

| Role ID | Assigned agent | Primary responsibility | Independence rule |
|---|---|---|---|
| `INT-LEAD` | Root agent | Shared contracts, integration, runtime packaging, documentation, gate control | Cannot self-clear the final product without all required RT and QA evidence |
| `ENG-BE` | Russell | Deterministic domain, imaging, OCR adapter, API, security, lifecycle | Does not author holdout expected outcomes |
| `ENG-FE` | Beauvoir | Intake, processing, result, evidence, accessibility implementation | Does not redefine server aggregation or comparison policy |
| `VV-LEAD` | James | Independent fixtures, oracle, automated validation, QA/QC, UAT evidence | Does not implement production comparison or aggregation logic |

Every production change receives cross-role review. The owning agent supplies focused tests and evidence. The reviewer checks behavior, dependency direction, requirement mapping, error paths, and documentation.

## 4. Writable-root and shared-source ownership

Only the primary editor may change a governed path during a parallel wave. Another role proposes the change to the primary editor. The integrator applies cross-owner changes only after the required reviewer accepts the contract and all affected contract tests pass.

| Path or governed source | Primary editor | Integrator | Required reviewer |
|---|---|---|---|
| Root project files, Python/npm lockfiles, all-check entrypoints | `INT-LEAD` | `INT-LEAD` | `VV-LEAD` |
| `backend/labelverify` except published governed contract copies | `ENG-BE` | `INT-LEAD` | `VV-LEAD` |
| `backend/tests` | `ENG-BE` | `INT-LEAD` | `VV-LEAD` |
| `frontend/src` and `frontend/tests` | `ENG-FE` | `INT-LEAD` | `VV-LEAD` |
| `fixtures`, sample manifest/assets, holdouts, and oracle | `VV-LEAD` | `INT-LEAD` | `ENG-BE` for schema only; holdout outcomes remain hidden from implementers |
| Cross-layer `tests/contract`, `tests/e2e`, `tests/performance`, and `tests/security` | `VV-LEAD` | `INT-LEAD` | Relevant non-owning engineer |
| `ops` and release configuration | `INT-LEAD` | `INT-LEAD` | `ENG-BE` and `VV-LEAD` |
| `scripts` and machine-readable evidence indexes | `VV-LEAD` | `INT-LEAD` | Relevant package owner |
| `docs/07-development` through `docs/10-release` | `INT-LEAD` | `INT-LEAD` | `VV-LEAD` |
| Selected-check registry, error registry, rule registry, and request/result/evidence schemas | `INT-LEAD` publishes controlled copies; source authority remains read-only | `INT-LEAD` | `ENG-BE`, `ENG-FE`, and `VV-LEAD` |
| Generated frontend API types | Generated only by `INT-LEAD` from the accepted schema | `INT-LEAD` | `ENG-FE` and `ENG-BE` |

Contract-first gates:

1. `CG-001`: `INT-LEAD` publishes and hashes request, result, evidence, error, limit, and 19-check contracts. `ENG-BE`, `ENG-FE`, and `VV-LEAD` accept them before `WP-003`, `WP-004`, or `WP-006` implementation.
2. `CG-002`: `VV-LEAD` publishes and hashes the sample manifest and assets. `INT-LEAD` and `ENG-FE` accept them before `TASK-032`.
3. `CG-003`: `VV-LEAD` publishes the fixture/oracle schema. `INT-LEAD` and `ENG-BE` accept the schema before policy fixture tests or `WP-008` integration.
4. `CG-004`: `INT-LEAD` generates and hashes frontend API types from the accepted schema. `ENG-FE` must not hand-edit the generated types.

An accepted contract change records its prior hash, new hash, affected `FR/T/WP`, owner, reviewers, and regression commands in `docs/07-development/contract-change-ledger.md`. Dependent work pauses until the new gate is accepted.

## 5. Planned repository shape

```text
backend/
  labelverify/
    api/
    contracts/
    domain/
    extraction/
    imaging/
    orchestration/
    security/
    settings/
  tests/
frontend/
  src/
    api/
    app/
    components/
    features/intake/
    features/verification/
    styles/
  tests/
fixtures/
  development/
  holdout/
  oracle/
ops/
scripts/
tests/
  contract/
  e2e/
  performance/
  security/
docs/
  01-discovery/ through 10-release/
```

Research under `research/baird-spike` is evidence only. Production code must never import it or its expected results.

## 6. Build sequence

| Wave | Work | Exit gate |
|---|---|---|
| 0 | Freeze BI authority and verify toolchains | BI snapshot has 3 CLEAR reviews; required runtimes are available |
| 1 | `WP-001` foundation and `CG-001` governed contracts | Lint, type-check, unit-test, all-check, and accepted contract commands run from documented entrypoints |
| 2 | `WP-002`, non-sample portions of `WP-005`, and `WP-007` in parallel | `CG-002` and `CG-003` are accepted; domain policies, intake UI, and independent fixture/oracle contracts pass focused tests |
| 3 | `WP-003`, `WP-004`, and `WP-006` | Real backend pipeline and frontend workspace integrate through the versioned contract |
| 4 | `WP-008` full automated validation | Unit, contract, integration, E2E, negative, mutation, privacy, and lifecycle suites pass |
| 5 | `WP-009`, `WP-010`, and `WP-011` | Container, performance, documentation, accessibility, and first-time UAT gates pass locally |
| 6 | `WP-012` Validation Protocol and QA/QC loop | All local DoD items pass or are recorded as requester-controlled deployment gates |

No later wave may hide or waive a failed earlier gate. Parallel work must use committed contracts or mocks generated from those contracts.

## 7. Integration rules

1. The server owns result states and summary. The browser renders them without recomputation.
2. Extraction and candidate generation remain reference-blind.
3. Every applicable selected check appears exactly once.
4. Missing, ambiguous, unreadable, or unsupported evidence can never become Match.
5. All result and error payloads validate against one versioned contract on both sides.
6. Full image decode and every expensive step run only inside the killable supervised child.
7. Request files remain owned until child completion or confirmed termination.
8. User content is not logged, persisted, cached, or sent to analytics.
9. Static UI and API share one origin.
10. Production modules never import fixtures, oracle data, or research code.

## 8. Required implementation evidence

Each work package must deliver:

- source files;
- focused automated tests;
- mapping to its `FR` and `T` identifiers;
- commands executed and machine-readable results;
- documented limitations or open release gates;
- cross-role review result;
- regression tests for every corrected defect.

Evidence is stored under `docs/07-development/evidence` during development and promoted into `docs/08-validation/evidence` only by the validation process. Large transient outputs stay outside Documents and are never part of the submission.

## 9. Proportionality controls

- Build only the distilled-spirits single-verification release and its bounded client-managed batch extension.
- Do not implement accounts, databases, saved history, ZIP ingestion, server-side batch queues, dashboards, or admin screens. Batch exports are required and remain local to the browser.
- Prefer pure functions and small modules over framework abstraction layers.
- Reuse one contract, one registry, one error map, and one fixture manifest rather than duplicate sources of truth.
- Meet every Must before considering visual polish beyond the cleared UX.
- Stop polishing documents once their binary gate is satisfied and move effort to executable proof.

## 10. Change control

| Discovery during build | Required action |
|---|---|
| Code defect or missing test within current requirement | Fix in development and add regression evidence |
| Ambiguous implementation detail already bounded by I2R | `INT-LEAD` records the choice in development notes and continues |
| Architecture cannot satisfy a cleared `FR` | Stop affected package, document impact, reopen I2R/FRD review |
| New feature or scope expansion | Do not implement without requester authorization and updated BAIRD/FRD |
| Regulatory source materially changed | Block release, update registry and affected requirements, rerun impacted gates |
| Performance, security, or false-clean gate fails | No waiver by implementation agent; return to development and rerun full regression |

## 11. BI exit criteria

BI is complete only when:

1. every `FR-001` through `FR-041` has a primary work package and test owner;
2. every package has size, dependency, outputs, acceptance, and review ownership;
3. coding and documentation standards are explicit;
4. QA/QC, UAT, evidence, and DoD are binary;
5. three independent reviewers return CLEAR on the same BI snapshot.
