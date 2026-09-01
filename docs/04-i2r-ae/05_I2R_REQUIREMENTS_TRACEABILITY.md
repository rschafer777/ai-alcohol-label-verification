# I2R Requirements to Component Traceability

Document control ID: LV-I2R-005  
Revision: 1.0  
Date: 2026-08-31  
Status: Draft for combined I2R and FRD review

| BAIRD requirement | Architecture components | Engineering verification |
|---|---|---|
| `BR-001` | `C-001`, `C-006`, deployment | Public smoke and core E2E |
| `BR-002` | `C-002`, `C-003`, `C-006` | Request schema and 1/6-panel tests |
| `BR-003` | `C-009` through `C-011` | Extraction contract and missing-evidence tests |
| `BR-004` | `C-011` through `C-014` | Registry completeness and per-field fixtures |
| `BR-005` | `C-012`, `C-014`, `C-004` | State and aggregation branch tests |
| `BR-006` | `C-011`, `C-014`, `C-016` | Negative fixture invariant and holdout |
| `BR-007` | `C-004`, `C-010`, `C-011` | Result schema and evidence-focus E2E |
| `BR-008` | `C-012`, `C-004` | Case/punctuation Review fixtures |
| `BR-009` | `C-012`, `C-013`, `C-004` | Independent warning-check fixtures and UI rows |
| `BR-010` | All request-path components | 30-attempt deployed browser benchmark |
| `BR-011` | `C-005` through `C-010`, `C-015` | `FR-011`, `FR-025`, `FR-031`, and `FR-041` prove separate performance, composed deadlines, cancellation, and failure timing |
| `BR-012` | `C-010`, `C-015`, deployment | Blocked-egress complete or bounded non-clean test |
| `BR-013` | `C-001` through `C-004` | `FR-002`, `FR-003`, `FR-013`, and `FR-037` include two independent no-instruction sessions |
| `BR-014` | `C-001` through `C-004` | Axe, keyboard, NVDA, contrast, zoom |
| `BR-015` | `C-006`, `C-007`, `C-009`, `C-015` | `FR-008`, `FR-009`, `FR-029`, `FR-040`, and `FR-041` cover boundary, edge identity, abuse, timing, memory, rate, and cleanup |
| `BR-016` | `C-001` through `C-010`, `C-015` | `FR-026`, `FR-027`, `FR-029`, `FR-039`, and `FR-040` prove server and browser non-persistence |
| `BR-017` | `C-004` through `C-010` | `FR-025` and `FR-041` use the normative error registry and total deadline/cancel contract |
| `BR-018` | `C-003`, `C-004`, `C-009` | Original/derived view and coordinate tests |
| `BR-019` | `C-001` through `C-004`, `C-016` | Built-in sample E2E and deterministic result |
| `BR-020` | Domain contracts only | No batch route/UI in core; post-core gate record |
| `BR-021` | `C-016` | 24 fixtures, 6 holdouts, mutation and anti-hard-coding evidence |
| `BR-022` | `C-013`, `C-015` | `FR-019`, `FR-020`, `FR-028`, and `FR-038` prove registry behavior, integrity, and release source re-verification |
| `BR-023` | Repository and deployment | Clean-checkout rehearsal, documentation audit, revision readback |
| `BR-024` | `C-001`, public documentation | Branding and forbidden-claim scan |
| `BR-025` | `C-001`, deployment | 5 clean-browser load tests, p95 at or below 3 seconds |
| `BR-026` | `C-010`, `C-015`, deployment | 5 cold starts, p95 below 10 seconds |
| `BR-027` | `C-001`, `C-015`, README | `FR-001`, `FR-027`, `FR-039`, and `FR-040` prove truthful disclosure and actual browser/server privacy controls |
| `BR-028` | All code components | Static analysis, code review, module and test separation |
| `BR-029` | Public artifacts | Personal-detail and private-source scan |
| `BR-030` | UI, README, validation report, deployment | Cross-artifact limitation consistency review |
| `BR-031` | All project artifacts | Automated U+2010 through U+2015 scan |

## Coverage result

- BAIRD requirements mapped: 31 of 31
- Unmapped requirements: 0
- Components with no requirement: 0
- Requirements relying only on manual assertion: 0
- Open technical release gates: cold start, deployed performance/configuration, final accessibility and security evidence

## V1 review remediation trace

| Finding area | Controlled resolution |
|---|---|
| Evidence references | LV-I2R-006 plus `FR-023`, `FR-024`, `T-023`, `T-024` |
| Total timeout and cancellation | LV-I2R-002 Section 8 plus `FR-041`, `T-041` |
| Exact raw request ceiling | LV-I2R-002 Sections 1 and 6 plus `FR-008`, `T-008` |
| Public edge and response privacy | LV-I2R-002 Section 10 plus `FR-040`, `T-040` |
| Normative errors | LV-I2R-007 plus `FR-025`, `T-025` |
| First-time usability | `FR-037`, `T-037` |
| Final warning registry | `selected-check-registry-v1.json`, `FR-019`, `FR-020` |
| Regulatory release recheck | `FR-038`, `T-038` |
| Browser non-persistence | `FR-039`, `T-039` |
| OCR comparison | LV-I2R-008 and sealed raw candidate evidence |
