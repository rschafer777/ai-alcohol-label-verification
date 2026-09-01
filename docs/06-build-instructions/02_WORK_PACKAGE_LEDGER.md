# Build Work Package Ledger

Document control ID: LV-BI-002  
Revision: 1.0  
Date: 2026-09-01  
Status: Candidate for BI review

## 1. Sizing scale

Sizes are relative delivery risk, not calendar promises:

- `S`: focused change with one primary layer and limited integration;
- `M`: several modules or one meaningful integration boundary;
- `L`: cross-module feature set with substantial negative testing;
- `XL`: critical cross-process or cross-layer work requiring staged integration and failure-path proof.

## 2. Epic summary

| Epic | Outcome | Work packages |
|---|---|---|
| `E-001` Product foundation | Reproducible project, contracts, dependency direction, and local quality commands | `WP-001` |
| `E-002` Verification engine | Reference-blind extraction plus deterministic evidence-linked checks | `WP-002`, `WP-003` |
| `E-003` Secure runtime | Bounded API, child supervision, privacy, security, health, and container behavior | `WP-004`, `WP-009` |
| `E-004` Guided reviewer experience | Obvious intake, processing, result, evidence, recovery, and reset journeys | `WP-005`, `WP-006` |
| `E-005` Verification and acceptance | Independent fixtures, automated proof, accessibility, UAT, and full validation loop | `WP-007`, `WP-008`, `WP-011`, `WP-012` |
| `E-006` Submission package | Evaluator-ready README, approach, assumptions, limitations, and release records | `WP-010` |

## 3. Stories and tasks

| WP | Epic and story | Size | Owner | Depends on | Tasks | Primary FRs | Exit evidence |
|---|---|---|---|---|---|---|---|
| `WP-001` | `E-001/S-001` Establish the governed monorepo foundation | M | `INT-LEAD` | BI CLEAR | `TASK-001` scaffold production/test folders; `TASK-002` pin Python/npm dependencies; `TASK-003` configure lint, format, type, test, and all-check commands; `TASK-004` install governed registry/error/contract sources; `TASK-005` enforce dependency boundaries and Unicode scan | `FR-034` | Clean local commands, dependency-boundary test, zero prohibited imports |
| `WP-002` | `E-002/S-002` Implement deterministic comparison and aggregation | L | `ENG-BE` | `WP-001`, `CG-001`, `CG-003` | `TASK-006` define states/reason types; `TASK-007` implement brand/class policies; `TASK-008` implement ABV/proof/net policies; `TASK-009` implement producer/country policies; `TASK-010` implement the exact 10 `warning_*` policies; `TASK-011` implement complete-check aggregation; `TASK-012` add exhaustive unit/mutation and registry-to-policy completeness tests | `FR-013` to `FR-020`, `FR-022` | Pure-function tests, 100 percent aggregator branches, exact 19-row registry/policy coverage, zero false clean |
| `WP-003` | `E-002/S-003` Implement bounded imaging, OCR, candidates, and evidence | XL | `ENG-BE` | `WP-001`, `WP-002`, `CG-001`, `CG-003` | `TASK-013` implement child-side decode/pixel limits/EXIF; `TASK-014` implement bounded transforms and inverse polygons; `TASK-015` implement RapidOCR adapter/readiness; `TASK-016` implement reference-blind candidate locators; `TASK-017` implement ambiguity and evidence contract; `TASK-018` implement panel coverage and quality; `TASK-019` add corruption/stall/coordinate tests | `FR-009` to `FR-012`, `FR-021` | Real OCR result, exact evidence polygons, corrupt/stall recovery, no reference leakage |
| `WP-004` | `E-003/S-004` Implement secure API, orchestrator, and supervisor lifecycle | XL | `ENG-BE` | `WP-001` to `WP-003`, `CG-001` | `TASK-020` implement health/meta/sample/versioned routes; `TASK-021` implement pre-body admission and raw byte guard; `TASK-022` implement multipart/signature/schema controls; `TASK-023` implement child supervisor/deadlines/restart; `TASK-024` implement rates/client identity/Host/Origin; `TASK-025` implement headers/errors/content-free logs; `TASK-026` prove cleanup across all terminal paths; `TASK-078` implement `C-008` ordered orchestration, typed completion/error transfer, all-or-nothing delivery, cancellation ownership, stage timings, and route-bypass boundary tests | `FR-008`, `FR-025`, `FR-028`, `FR-029`, `FR-040`, `FR-041` | Boundary matrix, orchestrator completeness/bypass tests, lifecycle counters at zero, exact error map, security tests |
| `WP-005` | `E-004/S-005` Build intake and sample journey | L | `ENG-FE` | `WP-001`; `CG-002` before `TASK-032` | `TASK-027` build neutral shell and notice; `TASK-028` build typed reference form; `TASK-029` implement imported-origin behavior; `TASK-030` build file add/preview/reorder/remove; `TASK-031` add client validation/focus; `TASK-032` consume the accepted sample contract and implement Try sample and guarded Start over | `FR-001`, `FR-003` to `FR-006`, `FR-027` | Keyboard-complete intake, valid 1/6 panel flows, deterministic sample load |
| `WP-006` | `E-004/S-006` Build processing, result, evidence, and recovery journey | XL | `ENG-FE` | `WP-003` to `WP-005`, `CG-001`, `CG-004` | `TASK-033` consume generated types and implement exhaustive error mapping; `TASK-034` implement elapsed state/cancel/deadline; `TASK-035` render summary and all check rows; `TASK-036` implement panel viewer/evidence polygons/alternatives; `TASK-037` implement limitations and retry preservation; `TASK-038` implement session-only note/disposition; `TASK-039` add focus/live-region/responsive tests | `FR-007`, `FR-023`, `FR-024`, `FR-026` | No duplicate request, exact server rendering, evidence focus, stale-result suppression |
| `WP-007` | `E-005/S-007` Build independent fixture, oracle, sample, and holdout corpus | L | `VV-LEAD` | `WP-001`, cleared FRD only | `TASK-040` define manifest/oracle schema; `TASK-041` create at least 18 development fixtures; `TASK-042` seal at least 6 holdouts; `TASK-043` cover every selected check and required negative scenario; `TASK-044` create deterministic sample assets; `TASK-045` add anti-hard-coding and mutation controls | `FR-002`, `FR-032` | 24 or more deterministic cases, 6 or more sealed holdouts, independent expected states |
| `WP-008` | `E-005/S-008` Build automated validation harness | XL | `VV-LEAD` | `WP-002` to `WP-007`, `CG-001` to `CG-004` | `TASK-046` map every `T` to local assertions and the exact 12 requester-gated assertions; `TASK-047` implement backend unit/contract suites; `TASK-048` implement browser E2E and axe; `TASK-049` implement security/privacy/lifecycle probes; `TASK-050` implement field/summary oracle validator; `TASK-051` produce assertion-level machine-readable evidence that enumerates and cross-validates all 12 external gates; `TASK-052` enforce zero false-clean and no prohibited content | `FR-039`; supports validation of all 41 | One command runs all local suites; exact assertion/evidence ledger; deterministic repeatability |
| `WP-009` | `E-003/S-009` Package and prove runtime characteristics | L | `INT-LEAD`, supported by `ENG-BE` | `WP-004`, `WP-006`, `WP-008` | `TASK-053` perform a clean multi-stage non-root OCI build and clean rebuild; `TASK-054` record image digest, runtime identity, governed-asset hashes, non-root state, and readiness smoke; `TASK-055` optimize cold readiness; `TASK-056` run local warm/cold/load/memory tests; `TASK-057` prepare Fly configuration without deployment; `TASK-058` record the exact six deployment-controlled assertions without promoting them to PASS | `FR-031`; supports `FR-011`, `FR-028`, `FR-040` runtime evidence | Successful hash-recorded OCI build and clean rebuild, non-root/readiness smoke, local performance report, and exact external checklist. If no OCI builder is available, status is BLOCKED and local readiness cannot pass. |
| `WP-010` | `E-006/S-010` Complete submission and compliance documentation | M | `INT-LEAD` | All implementation packages | `TASK-059` write setup/run README; `TASK-060` document approach/tools/assumptions/trade-offs/limitations; `TASK-061` add notices/SBOM/model BOM; `TASK-062` document implemented session-only batch behavior and exclusions; `TASK-063` run source/privacy/Unicode scans; `TASK-064` prepare release provenance and local regulatory-source inventory while individually tracking repository checkout, release recheck, requester code review, requester functional test, requester UAT, and final approval | `FR-033`, `FR-035`, `FR-036`, `FR-038` | A new evaluator can run locally from README; claims match evidence; local deliverables present; six named non-deployment external assertions remain individually visible |
| `WP-011` | `E-005/S-011` Execute accessibility and first-time UAT | M | `VV-LEAD`, supported by `ENG-FE` | `WP-005`, `WP-006`, `WP-008` | `TASK-065` run keyboard/focus/zoom scripts; `TASK-066` run Chrome/Edge/NVDA/axe checks; `TASK-067` run two independent Try sample sessions; `TASK-068` run two independent manual sessions; `TASK-069` record timings/help/errors; `TASK-070` remediate and regress blockers | `FR-030`, `FR-037` | No serious/critical axe issue, all manual scripts pass, binary first-time UAT passes |
| `WP-012` | `E-005/S-012` Run end-to-end Validation Protocol and QA/QC loop | L | `INT-LEAD` with `VV-LEAD` verification | `WP-001` to `WP-011` | `TASK-071` verify source-to-evidence matrix; `TASK-072` run full clean local build; `TASK-073` run every local assertion across all 41 tests and classify only the enumerated external assertions as `PENDING_REQUESTER_GATE`; `TASK-074` create complete defect records and return failures to owners; `TASK-075` rerun focused plus full regression and cross-validate ledgers; `TASK-076` assemble local release candidate; `TASK-077` obtain three final RT verdicts | No primary FR; validates all 41 | Local readiness pass, no open stop-ship/high/medium defect, zero unclassified gaps, requester-controlled assertions isolated without false PASS |

## 4. FR-to-work-package ownership

| FR | Primary WP | Test | FR | Primary WP | Test |
|---|---|---|---|---|---|
| `FR-001` | `WP-005` | `T-001` | `FR-022` | `WP-002` | `T-022` |
| `FR-002` | `WP-007` | `T-002` | `FR-023` | `WP-006` | `T-023` |
| `FR-003` | `WP-005` | `T-003` | `FR-024` | `WP-006` | `T-024` |
| `FR-004` | `WP-005` | `T-004` | `FR-025` | `WP-004` | `T-025` |
| `FR-005` | `WP-005` | `T-005` | `FR-026` | `WP-006` | `T-026` |
| `FR-006` | `WP-005` | `T-006` | `FR-027` | `WP-005` | `T-027` |
| `FR-007` | `WP-006` | `T-007` | `FR-028` | `WP-004` | `T-028` |
| `FR-008` | `WP-004` | `T-008` | `FR-029` | `WP-004` | `T-029` |
| `FR-009` | `WP-003` | `T-009` | `FR-030` | `WP-011` | `T-030` |
| `FR-010` | `WP-003` | `T-010` | `FR-031` | `WP-009` | `T-031` |
| `FR-011` | `WP-003` | `T-011` | `FR-032` | `WP-007` | `T-032` |
| `FR-012` | `WP-003` | `T-012` | `FR-033` | `WP-010` | `T-033` |
| `FR-013` | `WP-002` | `T-013` | `FR-034` | `WP-001` | `T-034` |
| `FR-014` | `WP-002` | `T-014` | `FR-035` | `WP-010` | `T-035` |
| `FR-015` | `WP-002` | `T-015` | `FR-036` | `WP-010` | `T-036` |
| `FR-016` | `WP-002` | `T-016` | `FR-037` | `WP-011` | `T-037` |
| `FR-017` | `WP-002` | `T-017` | `FR-038` | `WP-010` | `T-038` |
| `FR-018` | `WP-002` | `T-018` | `FR-039` | `WP-008` | `T-039` |
| `FR-019` | `WP-002` | `T-019` | `FR-040` | `WP-004` | `T-040` |
| `FR-020` | `WP-002` | `T-020` | `FR-041` | `WP-004` | `T-041` |
| `FR-021` | `WP-003` | `T-021` |  |  |  |

Coverage result: 41 of 41 feature requirements have one primary owner and one test identifier.
