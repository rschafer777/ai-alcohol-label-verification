# Feature Requirements Document

Document control ID: LV-FRD-001  
Revision: 1.1  
Date: 2026-08-31  
Status: Controlled as-built baseline  
Architecture authority: LV-I2R-001 through LV-I2R-008 plus `selected-check-registry-v1.json`

## 1. Purpose

This FRD defines the exact features required to implement the BAIRD baseline using the selected I2R Architecture and Engineering. Every requirement has upstream traceability, an owning component, binary acceptance, failure behavior, and a test identifier.

Priority values:

- Must: required for development DoD and take-home submission;
- Should: implemented only if it cannot threaten a Must;
- Conditional: active only after an explicit gate.

## 2. Feature requirements

| ID | Priority | Upstream | Feature requirement | Component | Binary acceptance and failure behavior | Test |
|---|---|---|---|---|---|---|
| `FR-001` | Must | `BR-001`, `BR-024`, `BR-027` | Show LabelVerify as an unofficial prototype with a synthetic/sanitized-data-only notice before upload. | `C-001` | PASS when notice is visible on first load, has no official seal or approval language, and agrees with actual data flow; FAIL otherwise. | `T-001` |
| `FR-002` | Must | `BR-019`, `BR-013` | Provide Try sample that loads a complete synthetic distilled-spirits record and required panels. | `C-001` to `C-004`, `C-016` | PASS when one action loads all required values/panels and completes the deterministic sample journey; FAIL on missing data, external dependency, or differing expected result. | `T-002` |
| `FR-003` | Must | `BR-002`, `BQ-003` | Provide typed manual reference fields for brand, class/type, ABV, optional proof, net contents value/unit, producer name/address, imported status, and conditional origin. | `C-002` | PASS when the schema, labels, required states, max lengths, numeric ranges, and accessible errors match LV-I2R-002; FAIL on silent coercion or ambiguous blank handling. | `T-003` |
| `FR-004` | Must | `BR-002`, `BR-013` | Show and require country of origin only when imported is selected. | `C-002` | PASS when toggling imported deterministically changes applicability, validation, and result coverage without losing an entered value during the current session; FAIL otherwise. | `T-004` |
| `FR-005` | Must | `BR-002`, `BR-018` | Accept, preview, reorder, and remove 1 to 6 JPEG, PNG, or WebP panels. | `C-003` | PASS for valid 1-panel and 6-panel journeys with labeled previews and originals retained; FAIL when 0 or more than 6 proceeds to verification. | `T-005` |
| `FR-006` | Must | `BR-013`, `BR-017` | Validate required reference fields and obvious client-side file errors before network submission. | `C-002`, `C-003` | PASS when Verify moves focus to the first error, associates text with its control, and preserves valid work; FAIL on color-only, hidden, or crash behavior. | `T-006` |
| `FR-007` | Must | `BR-010`, `BR-011`, `BR-013` | Submit one verification, show current processing state and elapsed time, and prevent duplicate activation. | `C-004`, `C-005` | PASS when one request is sent, status is announced, elapsed time is honest, and controls reflect busy state; FAIL on indefinite spinner or duplicate request. | `T-007` |
| `FR-008` | Must | `BR-015`, `BR-017` | Enforce 8,650,752 complete raw request bytes, 32 KiB reference JSON, 4 MiB per file, 8 MiB aggregate files, 1 to 6 panels, and the 20 second body deadline before decode. | `C-006`, `C-007`, `C-015` | PASS when missing/duplicate/invalid/conflicting/understated/oversized Content-Length and streaming overflow follow LV-I2R-002 and every limit returns its registry-defined result-free error, consumes no OCR capacity when pre-route, closes partial files, and returns counters to zero; FAIL otherwise. | `T-008` |
| `FR-009` | Must | `BR-015`, `BR-017` | Verify signatures in the parent, then fully decode and enforce per-image and cumulative pixel limits only inside the supervised child. | `C-007`, `C-009`, `C-010` | PASS when spoofed, corrupt, unsupported, oversize, decompression-boundary, and forced decoder-stall inputs return actionable result-free errors, the child is terminated/joined when needed, readiness recovers, and no handle, directory, reservation, capacity, job, or child leak remains; FAIL otherwise. | `T-009` |
| `FR-010` | Must | `BR-018`, `BQ-002` | Normalize EXIF orientation and create only bounded non-generative OCR views while preserving original evidence coordinates. | `C-009` | PASS when transformed polygons map to the correct original region and original/derived views remain distinguishable; FAIL if glyphs are invented or original evidence is replaced. | `T-010` |
| `FR-011` | Must | `BR-003`, `BR-012`, `BQ-001` | Run bundled hash-verified RapidOCR through one supervised child worker and return tokens, lines, polygons, reading order, confidence provenance, duration, and typed errors. | `C-010` | PASS when correct assets and warmup enable readiness, wrong assets block readiness, no runtime download occurs, and extraction is reference-blind; FAIL otherwise. | `T-011` |
| `FR-012` | Must | `BR-003`, `BR-006`, `BR-007` | Locate typed observed candidates for every selected field before reference comparison. | `C-011` | PASS when each field returns Found, Ambiguous, Not found, or Unreadable with evidence/alternatives and no expected-value shortcut; FAIL when reference text is copied into an observed value. | `T-012` |
| `FR-013` | Must | `BR-004`, `BR-008` | Compare brand using exact Match, case-only Review, punctuation Review, definite Mismatch, and missing/unreadable Not verified behavior. | `C-012` | PASS for the supplied STONE'S THROW case variation and independent mutation fixtures; FAIL if case-only becomes automatic Mismatch or semantic fuzzy Match. | `T-013` |
| `FR-014` | Must | `BR-004`, `BR-008` | Compare class/type with exact and explicitly safe representation rules; otherwise route variation to Review. | `C-012` | PASS when documented fixtures hit all states and no universal fuzzy threshold creates Match; FAIL otherwise. | `T-014` |
| `FR-015` | Must | `BR-004` | Parse and compare ABV and proof and check their documented relationship when both exist. | `C-012` | PASS for supported notation, equivalent representation, numeric difference, missing value, and inconsistent ABV/proof fixtures; FAIL on string-only comparison or invented tolerance. | `T-015` |
| `FR-016` | Must | `BR-004` | Parse net contents and normalize exact `mL`/`L` quantities. | `C-012` | PASS when 750 mL equals 0.75 L and a numeric quantity difference is Mismatch; FAIL when unsupported units silently Match. | `T-016` |
| `FR-017` | Must | `BR-004`, `BR-008` | Compare producer/bottler name and address with explicit whitespace/line handling and Review for material formatting ambiguity. | `C-012` | PASS for exact, safe line/space, ambiguous, definite difference, and missing fixtures; FAIL on broad fuzzy Match. | `T-017` |
| `FR-018` | Must | `BR-004`, `BR-006` | Compare country of origin only when imported and preserve every plausible conflicting candidate. | `C-011`, `C-012` | PASS when domestic is not applicable, one clear imported origin compares normally, and two plausible origins produce Review with distinct evidence actions; FAIL if expected value chooses the candidate. | `T-018` |
| `FR-019` | Must | `BR-009`, `BR-022` | Compare warning applicability, exact prescribed wording, punctuation, heading capitalization, heading emphasis, and remaining-text emphasis as separate checks in `selected-check-registry-v1.json`. | `C-012`, `C-013` | PASS when each registry check has an independent state/reason/evidence and title-case heading is not Match; FAIL if checks are collapsed or physical certainty is invented. | `T-019` |
| `FR-020` | Must | `BR-009`, `BR-022` | Render and evaluate warning continuity, separation, contrast, legibility, and physical-size limitation as five independent registry rows. | `C-004`, `C-012`, `C-013` | PASS when each row has independent state/reason/evidence, contrast and legibility are not combined, and physical size defaults to Not verified/human confirmation without reliable scale; FAIL when any row is missing or unavailable evidence becomes Match. | `T-020` |
| `FR-021` | Must | `BR-004`, `BR-006` | Report panel coverage and image quality separately from detected field differences. | `C-009`, `C-014` | PASS when absent or unreadable applicable evidence prevents a clean summary and requests better evidence; FAIL if quality failure becomes a field Mismatch or clean result. | `T-021` |
| `FR-022` | Must | `BR-005`, `BR-006` | Aggregate all applicable checks using deterministic precedence. | `C-014` | PASS with 100 percent branch tests proving Mismatch first, then Review/Not verified, then all-Match clean; FAIL if any applicable check is omitted or a partial result is reused. | `T-022` |
| `FR-023` | Must | `BR-007`, `BR-013`, `BR-018` | Render the summary, all applicable check rows, reference and observed values, reason, capability, and evidence action in a side-by-side workspace using LV-I2R-006. | `C-004` | PASS when response count equals rendered count, evidence IDs are unique/resolvable, polygons are valid original-image coordinates, derived mapping is correct, and every action focuses the exact region; any schema/reference failure suppresses the full result; FAIL otherwise. | `T-023` |
| `FR-024` | Must | `BR-007`, `BR-006` | Render each material ambiguity alternative as a separately named evidence action under LV-I2R-006. | `C-004` | PASS when the conflicting-country fixture shows exact distinct values, unique evidence IDs, and distinct source polygons, and invalid/duplicate references produce `response_contract_invalid`; FAIL on generic Candidate 1 labels, one reused region, or guessed focus. | `T-024` |
| `FR-025` | Must | `BR-011`, `BR-012`, `BR-017` | Implement every server and browser error in LV-I2R-007 with its fixed status, code, retryability, locator rule, next-action class, result-free invariant, and safe fallback. | `C-004` through `C-010`, `C-015` | PASS when contract tests cover every registry row, UI mapping is exhaustive, unknown failures become `internal_error`, no stale result remains, retryable failure preserves current reference values and selected browser file objects, and retry recovery succeeds without re-entry; FAIL otherwise. | `T-025` |
| `FR-026` | Must | `BR-008`, `BR-016` | Allow an optional session-only reviewer note and disposition separate from immutable system findings. | `C-004` | PASS when note/disposition never changes machine states, is never sent to the server, and disappears on refresh/start-over; FAIL otherwise. | `T-026` |
| `FR-027` | Must | `BR-013`, `BR-016` | Provide Start over that confirms before clearing non-empty browser work and returns to a clean Intake state. | `C-001`, `C-004` | PASS when non-empty form, files, result, evidence selection, or note triggers confirmation; Cancel leaves all work unchanged; Confirm clears all browser state without a server deletion call; an already clean state needs no confirmation; FAIL otherwise. | `T-027` |
| `FR-028` | Must | `BR-012`, `BR-016`, `BR-022` | Provide liveness, fail-closed readiness, and safe metadata endpoints. | `C-006`, `C-010`, `C-013`, `C-015` | PASS when liveness is process-only, readiness requires exact assets and warmup, and metadata exposes safe release identity only; FAIL on false readiness or secret/path exposure. | `T-028` |
| `FR-029` | Must | `BR-015`, `BR-016`, `BR-027` | Use allowlisted content-free logs and enforce supervisor-owned cleanup on success, validation error, upload timeout, child decode stall, worker timeout, cancellation, disconnect, and shutdown. | `C-007`, `C-010`, `C-015` | PASS when content-canary scans find no user data, cleanup occurs only after child exit/termination, and final handles, directories, reservations, capacity, owned jobs, and children are zero for every path; FAIL otherwise. | `T-029` |
| `FR-030` | Must | `BR-014` | Meet the defined keyboard, focus, live-region, label/error, non-color, contrast, zoom, Chrome, Edge, and NVDA accessibility contract. | `C-001` through `C-004` | PASS when automated axe has no serious/critical findings and all manual scripts pass; FAIL on any required-path blocker. | `T-030` |
| `FR-031` | Must | `BR-010`, `BR-025`, `BR-026` | Meet public load, warmed verification, and cold-start performance as three separate metrics under the declared network profiles. | All request-path components and deployment | PASS when load p95 is at most 3 seconds over 5 loads, warmed result p95 is at most 5 seconds with 30 of 30 complete normal-profile attempts and required composition, cold p95 is below 10 seconds over 5 runs, and representative/max shaped-network requests meet the 20/30/35 second terminal budgets; FAIL if any threshold or completeness gate fails. | `T-031` |
| `FR-032` | Must | `BR-021` | Deliver at least 24 deterministic end-to-end fixtures with at least 6 sealed holdouts and the approved scenario coverage. | `C-016` | PASS when independent oracle, mutation, holdout, anti-hard-coding, field-level, and summary evidence all pass; FAIL on fixture-specific production branching or an untested selected check. | `T-032` |
| `FR-033` | Must | `BR-023`, `BR-030` | Deliver all source, README, clean setup/run path, approach, tools, assumptions, trade-offs, limitations, validation results, and revision/deployment provenance. | Repository and deployment | PASS when clean checkout works using only README and all claims match UI, tests, and deployment; FAIL on missing source, undocumented prerequisite, or claim conflict. | `T-033` |
| `FR-034` | Must | `BR-028` | Keep extraction, candidate location, normalization, comparison, rules, aggregation, UI, and fixtures separated and reviewable. | All components | PASS when dependency rules, static checks, focused tests, naming, and code review pass; FAIL on circular architecture, business logic in UI/routes, or expected-fixture imports in production. | `T-034` |
| `FR-035` | Must | `BR-029`, `BR-031` | Exclude unnecessary personal details/private design sources and all U+2010 through U+2015 characters from deliverables. | Repository | PASS when automated and manual scans return zero prohibited findings; FAIL otherwise. | `T-035` |
| `FR-036` | Must | `BR-020` | Provide a bounded 1 to 300 application batch workflow that reuses the complete single-verification contract. | `C-001`, `C-004`, `C-008`, `C-009` | PASS when manifest intake, row accounting, sequential execution, progress, cancellation, retry, exception review, CSV and detailed JSON exports, input safety, and the 10/20/300 capacity model in the batch FRD addendum pass; FAIL on a missing row, duplicate execution, false clean result, unsafe path, formula-capable CSV cell, or batch failure that aborts later valid rows. | `T-036` |
| `FR-037` | Must | `BR-013` | Prove first-time no-instruction usability for both the complete Try sample and manual journeys. | `C-001` through `C-004` | PASS when two independent reviewers who did not implement the UI each complete Try sample in at most 3 minutes and manual entry/upload/error-correction/verification/evidence/start-over in at most 7 minutes, with no facilitator help, no critical error, and every required step observed; FAIL otherwise. | `T-037` |
| `FR-038` | Must | `BR-022` | Re-verify every implemented TTB/eCFR regulatory source immediately before release. | `C-013`, release process | PASS when each rule records authority URL, retrieval date, compared version/content, reviewer, change result, and release decision; any material unincorporated change blocks release; FAIL otherwise. | `T-038` |
| `FR-039` | Must | `BR-016`, `BR-027` | Prove that browser storage and caching never persist reference values, files, extracted text, evidence, results, or reviewer notes. | `C-001` through `C-005` | PASS when localStorage, sessionStorage, IndexedDB, Cache Storage, service workers, history state, and browser cache inspection remain content-free after success, error, cancel, refresh, close/reopen, and Start over; verification/API responses are no-store; FAIL otherwise. | `T-039` |
| `FR-040` | Must | `BR-015`, `BR-016`, `BR-027` | Enforce the LV-I2R-002 explicitly selected edge client identity, Host, Origin, secure response-header, no-store, and privacy-safe digest contracts. | `C-006`, `C-015`, deployment | PASS when direct, Azure rightmost forwarded, and Fly portability identity paths plus spoofed/duplicate/malformed/missing headers, identity/rate isolation, Host/Origin matrix, CSP/HSTS/anti-framing/referrer/permissions headers, and no-store behavior all pass; FAIL otherwise. | `T-040` |
| `FR-041` | Must | `BR-011`, `BR-012`, `BR-017` | Enforce the composed 20 second upload, 30 second server, and 35 second browser terminal deadlines and user cancellation race rules. | `C-004` through `C-010`, `C-015` | PASS when controlled stalls at every asynchronous wait boundary reach the exact terminal state: upload, parent validation, worker queue, the single supervised child job containing decode through inference, response transfer, and the browser request deadline. Client validation must reject locally within 1 second without transport. A complete response must render all rows, move focus, and expose the required live-region content in one deterministic commit. Cancel must enter Cancelled within 1 second while preserving editable form/file work; server ownership must remain safe after disconnect; late responses must be ignored; child termination/recovery must pass; and cleanup must reach zero; FAIL otherwise. | `T-041` |

## 3. Field comparison policy

| Field | Match | Review | Mismatch | Not verified |
|---|---|---|---|---|
| Brand | Exact text | Case-only, punctuation, ambiguous candidate | Definite readable different name | Missing or unreadable |
| Class/type | Exact or explicitly enumerated safe representation | Formatting or incomplete but plausible observed designation | Definite readable different designation | Missing or unreadable |
| ABV | Equal parsed decimal | Ambiguous parse or inconsistent precision representation | Definite different parsed value | Missing or unreadable |
| Proof | Equal parsed decimal and consistent with ABV | Ambiguous parse or relationship uncertainty | Definite different value or documented inconsistency | Not present when optional, or unreadable when expected |
| Net contents | Equal exact quantity after L/mL conversion | Ambiguous parse | Definite different quantity | Missing or unreadable |
| Producer/address | Exact or safe whitespace/line equivalence | Material formatting or candidate ambiguity | Definite readable difference | Missing or unreadable |
| Country | Equal when imported | Conflicting plausible countries or formatting ambiguity | Definite different country | Required but absent/unreadable; not applicable for domestic |
| Warning wording | Exact prescribed tokens after line-wrap/whitespace handling | Readability uncertainty | Readable word or punctuation mutation | Missing/unreadable |
| Warning presentation | Supported property visibly satisfied | Heuristic evidence requires judgment | Supported property visibly fails | Image cannot support the property |
| Physical warning size | Never automatic from unscaled photo | Human confirmation with sufficient context | Only when reliable scale supports it | Default for unscaled image |

## 4. Submission state machine

```text
INTAKE
  -> CLIENT_INVALID -> INTAKE
  -> SUBMITTING
      -> API_ERROR -> RECOVERABLE_ERROR -> SUBMITTING or INTAKE
      -> PROCESSING
          -> COMPLETE_RESULT -> REVIEWING -> INTAKE
          -> RESULT_FREE_ERROR -> RECOVERABLE_ERROR
```

No partial field response becomes COMPLETE_RESULT. No prior result remains current after a new verification starts or fails.

## 5. Release exclusions

The FRD does not authorize:

- COLA integration or PDF parsing;
- accounts, persistence, saved history, or durable audit records;
- wine or malt-beverage rule packs;
- legal approval or rejection;
- external AI as a required runtime dependency;
- ZIP ingestion, server-side batch routes, durable queues, or capacity claims beyond 300 applications;
- physical type-size certification without reliable scale;
- mobile-specific release claims.

## 6. FRD completeness result

- Active feature requirements: 41 Must plus the batch and readiness requirements in the current addendum
- Conditional batch implementation requirements: 0; bounded batch is active
- BAIRD requirements covered: 31 of 31
- I2R components covered: 16 of 16
- Features without binary acceptance: 0
- Features without test IDs: 0
- Known open release gate: cold-start p95 below 10 seconds
