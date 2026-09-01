# Batch and Federal Readiness Build Instructions

Document control ID: LV-BI-005  
Revision: 1.0  
Date: 2026-09-01  
Status: Active correction wave  
Authority: LV-BRD-002, LV-I2R-010, and LV-FRD-003

## 1. Work packages

| Package | Size | Owner role | Build output | Exit gate |
|---|---:|---|---|---|
| `WP-013 Batch model` | M | Frontend engineer | Strict CSV parser, manifest validation, ordered row model, path and ownership controls, formula-safe CSV, detailed JSON | `T-043` through `T-045`, `T-049` |
| `WP-014 Batch experience` | M | Frontend engineer | Workspace switch, folder intake, demo batch, sequential runner, progress, cancel, retry, filters, details, exports, responsive and accessible states | `T-042`, `T-046` through `T-048` |
| `WP-015 Warning correction` | S | Backend engineer | Exact punctuation preservation, volume-tier size/density policy, unscaled-photo handling | `T-051`, `T-052` |
| `WP-016 Image recovery` | M | Backend engineer | Skew signals, bounded deskew, conservative perspective correction, CLAHE recovery, inverse evidence mapping | `T-053` |
| `WP-017 Capacity validation` | M | Validation engineer | 10, 20, and 300 row scenarios, timing, completeness, row isolation, memory, false-clean, cancel, retry, and export evidence | `T-050` |
| `WP-018 Federal starter package` | M | Security architecture | Current official-source path analysis and starter document set | `T-056` |
| `WP-019 Documentation correction` | S | Integration lead | Canonical addenda, README, traceability, change record, and limitation reconciliation | `T-057` |
| `WP-020 Regression and RT` | M | Independent validation | Full quality gate, live UAT, security, accessibility, Validation Protocol, three independent RT verdicts | Corrected DoD |

## 2. Task sequence

1. Update BAIRD and record batch GO after the passed core gate.
2. Publish the batch architecture, manifest contract, state model, and 300-row boundary.
3. Supersede `FR-036` and publish binary batch features and tests.
4. Implement the batch model before the UI runner.
5. Correct warning punctuation and container-volume tiers.
6. Implement one bounded recovery view and original-coordinate mapping.
7. Add focused unit and component tests before running regression.
8. Build the production frontend and test 10 and 20 rows against the local API.
9. Execute the 300-row deterministic capacity protocol or record a blocking defect.
10. Complete the federal authorization-start package and README.
11. Run lint, strict typing, all automated tests, product corpus, lifecycle, security, accessibility, performance, and live browser UAT.
12. Run three independent RTs against the same final candidate. Return any material finding to its owning work package and repeat the affected gates plus full regression.

## 3. Coding and documentation standards

- TypeScript uses strict mode, explicit exported types, stable row keys, plain status names, and no business-rule recomputation.
- Python uses strict typing, Ruff, MyPy, small pure policy functions, bounded OpenCV transforms, and no expected-fixture imports in production.
- The existing request, response, error, evidence, check, and rule contracts remain authoritative.
- Batch uses the existing single-verification endpoint and never bypasses its input or lifecycle controls.
- CSV output neutralizes spreadsheet formulas. JSON output preserves the full validated result.
- Every corrected defect receives a focused regression test and requirement mapping.
- Code comments explain security boundaries, non-obvious transforms, and policy decisions. They do not narrate obvious syntax.
- Documents use controlled IDs, revision, date, status, authority, explicit acceptance, and source links.
- U+2010 through U+2015 characters are prohibited.

## 4. QA and QC gates

| Gate | Pass condition |
|---|---|
| Functional | Single and batch journeys complete; all batch rows are accounted for; one error does not abort later rows |
| Correctness | Product corpus and batch oracle have zero false clean results; `STONE'S THROW` routes to Review; warning mutations route correctly |
| Security | Manifest traversal, path ambiguity, shared panels, hostile MIME, resource limits, formula injection, Host, Origin, rate, cleanup, and log-canary tests pass |
| Performance | Warm single p95 remains at most five seconds and batch 10/20/300 limits pass |
| Resource | Server RSS remains below 2 GiB and supervisor counters return to zero |
| Accessibility | Keyboard, focus, live progress, non-color states, labels, table semantics, zoom, and automated serious/critical checks pass |
| Privacy | No application content persists in server or browser storage after the documented lifecycle |
| Documentation | README and numbered process artifacts agree with the as-built behavior and measured evidence |
| Federal readiness | Starter inventory is complete and every pending production input has a decision owner |

## 5. UAT

UAT includes:

- a first-time single-label journey;
- a first-time batch demo journey;
- a low-technical-comfort participant for both journeys;
- a `STONE'S THROW` harmless-variation review;
- a title-case government-warning difference;
- a missing or unreadable warning;
- a difficult skewed or low-light image that does not become falsely clean;
- a 10-row batch with mixed outcomes, detail inspection, and both exports;
- cancel during an active row and retry a Cancelled row;
- invalid manifest row isolation;
- refresh and Start over privacy checks.

The human participant records time, assistance, errors, comprehension of statuses, recovery, and final comments. Automated tests do not substitute for the required participant evidence.

## 6. Corrected Definition of Done

Done requires all original single-submission gates plus `FR-042` through `FR-057`, 10/20/300 batch evidence, accurate README limitations, federal starter documents, zero open Severity 1 or Severity 2 defects, no unresolved false-clean defect, current regulatory-source verification, and three CLEAR RT verdicts on one candidate. GitHub publication and public deployment remain requester-controlled steps after local UAT.
