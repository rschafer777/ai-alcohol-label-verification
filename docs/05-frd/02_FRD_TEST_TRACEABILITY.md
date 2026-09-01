# FRD Test Traceability

Document control ID: LV-FRD-002  
Revision: 1.1  
Date: 2026-08-31  
Status: Controlled as-built baseline

| Test range | Layer | Tool direction | Evidence |
|---|---|---|---|
| `T-001` to `T-007` | UI and primary journeys | Vitest, Testing Library, Playwright | Screens, traces, accessibility tree, assertions |
| `T-008` to `T-012` | Boundary, imaging, extraction, candidates | pytest, raw ASGI/HTTP clients, real fixture images | Structured reports and cleanup counters |
| `T-013` to `T-022` | Deterministic field policies and aggregation | pytest unit, property, mutation, and fixture tests | Branch/mutation results and field oracle |
| `T-023` to `T-027` | Result/evidence/recovery/session UX | Playwright | DOM, focus, evidence polygons, recovery traces |
| `T-028` to `T-029` | Readiness, metadata, privacy, lifecycle | pytest integration and runtime harness | Hash/readiness probes, log canary, final zero counters |
| `T-030` | Accessibility | axe, Playwright, manual keyboard and NVDA | Automated report and signed checklist |
| `T-031` | Performance | Browser timing harness and deployment readback | Raw run records and percentile report |
| `T-032` | Validation corpus | Independent oracle and sealed holdout runner | Fixture manifest and result matrix |
| `T-033` to `T-036` | Delivery and architecture quality | Clean-checkout rehearsal, static analysis, review and scans | QA/QC report and release checklist |
| `T-037` | First-time usability | Two independent no-instruction observed sessions | Timed observation records and step checklist |
| `T-038` | Regulatory release control | Authority readback and content comparison | Signed source re-verification record |
| `T-039` | Browser privacy | Playwright plus browser storage/cache inspection | Storage, cache, refresh, close/reopen evidence |
| `T-040` | Public edge security | Direct and proxied HTTP matrices | Identity, Host, Origin, headers, no-store, rate isolation |
| `T-041` | Total timing and cancellation | Controlled asynchronous boundary stalls, synchronous browser commit tests, browser E2E, runtime harness | Exact terminal timing, complete render and announcement, race, ownership, and cleanup report |

## Required test properties

- Deterministic aggregation has 100 percent branch coverage.
- Comparison and regulatory policies have at least 90 percent branch coverage.
- Frontend and backend business modules have at least 80 percent line and branch coverage.
- Coverage percentages do not replace negative, mutation, boundary, E2E, accessibility, performance, or holdout tests.
- Every bug found after development receives a regression test before closure.
- Retries are disabled for release performance and correctness gates unless the test explicitly validates retry behavior.
