# QA, QC, UAT, and Definition of Done

Document control ID: LV-BI-003  
Revision: 1.0  
Date: 2026-09-01  
Status: Candidate for BI review

## 1. Quality model

QA verifies the process, contracts, prevention controls, and traceability. QC verifies the built behavior and evidence. UAT verifies that first-time users can complete the intended journeys. None can replace another.

| Layer | Required proof | Owner |
|---|---|---|
| Static quality | Formatting, lint, strict typing, dependency boundaries, secret/license/Unicode scans | Package owner, reviewed by `INT-LEAD` |
| Unit | Parsers, comparison, warning checks, aggregation, error mapping, UI reducers | Package owner |
| Contract | Request, result, evidence, error, registry, and frontend/backend schema parity | `ENG-BE`, `ENG-FE`, verified by `VV-LEAD` |
| Integration | Upload guard, child process, OCR, cleanup, API, and UI wiring | `ENG-BE`, `INT-LEAD` |
| E2E | Sample, manual, invalid, cancel, timeout, evidence, reset, and recovery journeys | `VV-LEAD` |
| Non-functional | Accessibility, privacy, security, performance, cold start, memory, and shaped-network behavior | `VV-LEAD`, `INT-LEAD` |
| UAT | Two independent first-time Try sample and manual sessions | `VV-LEAD` |
| Release | Clean setup, docs, provenance, regulatory recheck, public deployment checks | `INT-LEAD`, requester-controlled external actions |

## 2. Mandatory Validation Protocol

1. Verify the immutable authority and product-source snapshot.
2. Join every `SRC/DEC` to `BR`, architecture decision, `FR`, component, `T`, and evidence record.
3. Run all static, unit, contract, integration, E2E, security, privacy, accessibility, and performance suites.
4. Validate every applicable 19-check row exactly once in the response and browser.
5. Independently compare fixture results against the oracle at field and summary levels.
6. Inspect evidence IDs, panels, polygons, transforms, ambiguity alternatives, and focus behavior.
7. Exercise every terminal path: success, invalid input, busy, rate limit, upload timeout, decode stall, inference timeout, cancellation, disconnect, shutdown, and internal error.
8. Confirm zero final handles, files, directories, reservations, jobs, and child leaks.
9. Inspect browser storage and cache after success, error, cancel, refresh, reopen, and Start over.
10. Record assertion-level status for every `T-001` through `T-041`. Locally executable assertions use PASS, FAIL, NOT_RUN, or BLOCKED. Only the enumerated external assertions in Section 6 may use `PENDING_REQUESTER_GATE`.
11. Return every failure to development with a regression-test requirement.
12. Rerun the focused test, affected suite, and full regression before closure.

Composite test state:

- `LOCAL_READY`: every locally executable assertion is PASS, every external assertion is one of the exact requester-gated assertions in Section 6, and there is no unclassified gap;
- `FINAL_PASS`: every local and external assertion is PASS;
- `FAIL`: at least one required assertion is FAIL;
- `INCOMPLETE`: any required assertion is NOT_RUN, BLOCKED, missing, or pending without being explicitly enumerated.

A `T-NNN` with requester-gated assertions may be `LOCAL_READY`, but it is not `FINAL_PASS`. All other `T-NNN` tests must reach `FINAL_PASS` during local validation.

## 3. Defect classes and return loop

| Severity | Definition | Gate effect |
|---|---|---|
| Stop-ship | False clean, user-content retention/leak, contract corruption, security boundary bypass, missing selected check, unkillable worker, or misleading official/legal claim | Immediate development return; all downstream gates invalidated |
| High | Core journey failure, inaccessible required action, repeatable crash, wrong result/evidence, cleanup leak, deadline failure, or missing required deliverable | Development return; full affected regression required |
| Medium | Non-core usability, recoverability, documentation, or visual issue that does not change the result | Must close before local release candidate unless explicitly excluded by the cleared scope |
| Low | Cosmetic issue with no accessibility, clarity, correctness, or delivery effect | May remain only when documented and all higher gates pass |

Correction loop:

```text
FAIL -> defect record -> owner fix -> focused regression -> affected suite -> full suite -> evidence review -> close or repeat
```

No issue closes on code inspection alone when executable proof is possible.

## 4. UAT scenarios

| UAT | Scenario | Binary pass |
|---|---|---|
| `UAT-001` | First-time Try sample | Reviewer completes from first load to evidence focus in at most 3 minutes with no help or critical error |
| `UAT-002` | First-time manual exact record | Reviewer enters reference, adds panels, corrects one induced error, verifies, inspects evidence, and starts over in at most 7 minutes with no help or critical error |
| `UAT-003` | Brand case variation | STONE'S THROW versus Stone's Throw is Review, not automatic Mismatch or Match |
| `UAT-004` | Warning exactness | Title-case heading and altered punctuation are exposed as separate non-Match checks with evidence |
| `UAT-005` | Imperfect image | Angle, curvature, low light, glare, or partial framing does not create a label failure by itself. Recoverable evidence is evaluated normally. Unreadable mandatory evidence produces Review, Not verified, or an additional-image request, while a visible deterministic defect remains Mismatch. |
| `UAT-006` | Cancel and retry | Cancel reaches terminal state within 1 second, preserves editable work, ignores late response, and allows successful retry |
| `UAT-007` | Destructive reset | Cancel confirmation preserves all work; Confirm clears all session state without server deletion |
| `UAT-008` | Ambiguous evidence | Each material alternative has a distinct name, evidence ID, polygon, and focus action |

Two independent non-implementers must pass `UAT-001` and `UAT-002`. Other scenarios require at least one independent witness plus automated evidence.

## 5. Local Definition of Done

The local release candidate is ready only when all statements are true:

- 31 of 31 BAIRD requirements remain represented.
- Every locally executable assertion for all 41 feature requirements is PASS.
- Every test without an external assertion is `FINAL_PASS`; `T-031`, `T-033`, `T-037`, `T-038`, and `T-040` may be `LOCAL_READY` only when their exact Section 6 external assertions are `PENDING_REQUESTER_GATE`.
- There are zero NOT_RUN, BLOCKED, missing, or unclassified local assertions.
- All 19 product checks execute with complete-check aggregation.
- At least 24 deterministic E2E fixtures and at least 6 sealed holdouts pass.
- False-clean count is zero. Field/summary oracle errors and missing required evidence are zero.
- Warm local verification has 30 of 30 complete normal-profile attempts and p95 at or below 5 seconds.
- Normal readable images target less than 5 seconds, difficult recoverable images may take up to 9 seconds, and sequential batch mean targets at most 5 seconds per image. Each class is reported separately.
- Local cold start has 5 runs with p95 below 10 seconds.
- Local page-load p95 is at most 3 seconds over 5 loads.
- `T-033-A-OCI-CLEAN-BUILD`, `T-033-A-OCI-CLEAN-REBUILD`, `T-028-A-OCI-NONROOT`, and `T-028-A-OCI-READINESS` are PASS with image digests, runtime identity, governed-asset hashes, non-root identity, and readiness evidence. A missing OCI builder is BLOCKED and makes local readiness INCOMPLETE.
- Max accepted inputs reach a safe terminal result within documented server/browser limits.
- Real decode stall, inference stall, cancellation, disconnect, and shutdown recover with zero leaks.
- Security, Host/Origin, identity, rate, response-header, no-store, and content-log tests pass.
- Browser persistence inspections are clean.
- Automated axe has no serious or critical issue, and all keyboard, focus, zoom, Chrome, Edge, and NVDA scripts pass.
- Both independent first-time UAT reviewers pass.
- README setup/run, approach, tools, assumptions, trade-offs, limitations, and validation records are complete and consistent.
- Batch, COLA, account, persistence, legal decision, external-runtime-API, and mobile claims are absent.
- Source, secrets, personal/private content, licenses, and Unicode dash scans pass.
- No stop-ship, high, or medium defect remains open.
- Three final RT reviewers return CLEAR on the same local release-candidate snapshot.

## 6. Requester-controlled release gates

These cannot be claimed complete before requester authorization permits GitHub and deployment:

- `T-033-A-REPO-CHECKOUT`: source repository creation and clean checkout proof;
- `T-033-A-PUBLIC-URL`: public deployment URL and release provenance;
- `T-031-A-DEPLOYED-LOAD`: deployed page-load p95 proof;
- `T-031-A-DEPLOYED-WARM`: deployed 30-run warmed verification proof;
- `T-031-A-DEPLOYED-COLD`: deployed 5-run cold/restart proof;
- `T-031-A-SHAPED-NETWORK`: deployed representative and near-maximum shaped-network proof;
- `T-040-A-PUBLIC-EDGE`: deployed Fly identity, Host, Origin, security-header, no-store, and clean-browser smoke;
- `T-038-A-RELEASE-RECHECK`: final regulatory source recheck immediately before release;
- `T-033-A-REQUESTER-CODE-REVIEW`: requester code review result;
- `T-033-A-REQUESTER-FUNCTIONAL-TEST`: requester functional test result;
- `T-037-A-REQUESTER-UAT`: requester UAT acceptance;
- `T-033-A-FINAL-SUBMISSION-APPROVAL`: requester final submission approval.

Only these 12 assertions may use `PENDING_REQUESTER_GATE`. Local simulations, configuration validation, OCI construction, source inventory, documentation, and all other assertions remain required locally. The local release candidate may be internally CLEAR while the 12 assertions are pending. It may not be called the final assignment submission, and the composite tests are not `FINAL_PASS`, until all 12 pass.

## 7. Evidence record minimum

Every test record contains:

- `testId` and mapped `FR`;
- stable `assertionId` and execution scope of `local`, `repository`, `deployed`, `regulatory_release`, or `requester_acceptance`;
- product snapshot/build ID;
- UTC execution time;
- environment and command;
- inputs or fixture IDs without private content;
- expected and observed outcome;
- assertion status of PASS, FAIL, NOT_RUN, BLOCKED, or `PENDING_REQUESTER_GATE`;
- composite state of `LOCAL_READY`, `FINAL_PASS`, FAIL, or INCOMPLETE;
- duration and relevant counters;
- artifact digest, runtime identity, and governed-asset hashes when the assertion builds or executes an OCI image;
- artifact paths and hashes;
- executor and reviewer role;
- linked defect and regression ID when applicable.

## 8. Defect record contract

The versioned defect ledger uses one record per defect with:

- stable `defectId`;
- linked `FR`, `T`, and `assertionId` values;
- severity and written rationale;
- lifecycle status of OPEN, IN_FIX, READY_FOR_RETEST, CLOSED, or REOPENED;
- environment, product snapshot/build, and discovery timestamp;
- reproduction steps plus non-private fixture/input ID;
- expected and observed behavior;
- owner and affected component/work package;
- fix revision or product snapshot;
- regression test ID and evidence hashes;
- independent closure reviewer;
- opened, assigned, fixed, retested, closed, and reopened timestamps as applicable.

`WP-012` cannot close until the defect ledger and assertion evidence ledger cross-validate: every failed assertion links to an open or closed defect, every fixed defect links to a passing regression assertion on the corrected snapshot, no closed defect lacks an independent closer, and no open stop-ship, high, or medium defect remains.
