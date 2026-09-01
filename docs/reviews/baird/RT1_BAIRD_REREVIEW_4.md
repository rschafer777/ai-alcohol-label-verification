REWORK_REQUIRED

# RT1 BAIRD Architecture and Requirements Fidelity Rereview 4

Review date: 2026-08-31

Role: Independent requirements-fidelity and architecture red team

## Reviewed sealed snapshot

- Manifest: `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V4.sha256`
- Expected and observed manifest SHA-256: `8e2b88b12699f8192bc1b66637885ac9c8fbc1f72cd4158604775d0d2f80932b`
- Expected and observed hashed entries: 144
- Missing files: 0
- Hash mismatches: 0

I verified the manifest hash and every listed file before review. This report is outside the sealed manifest. I did not modify any snapshotted file.

## Gate decision

V4 closes the prior warning punctuation, country ambiguity, worker queue, cancellation ownership, two-copy reservation arithmetic, regulatory registry, governed-asset readiness, and stale Intake evidence defects at the documented design level. The independent field oracle and retained valid-result evidence reconcile exactly.

One material upload-control defect remains. The retained V4 deadline and storage probes do not exercise the actual FastAPI multipart dependency path. In the full ASGI app, the framework converts the custom body-deadline and raw-overflow exceptions into generic 400 responses before the outer middleware can return the selected 408 or 413. A partially rolled multipart spool file is not explicitly closed on that exceptional path. The full app also parses a seventh file part before the route-level six-file check. This contradicts the selected pre-route limit, status, cleanup, and evidence claims. It reopens a load-bearing public upload control and must be corrected before I2R.

## Review method and independent checks

I reviewed the complete sealed Intake and BAIRD package, including all Intake source and gate artifacts, every BAIRD decision and handoff artifact, retained source and evidence, all earlier RT1, RT2, and RT3 reports, and `BAIRD_RT_REMEDIATION.md`. Grok and Gemini materials were treated only as non-authoritative design evidence.

I independently performed these checks:

1. Verified the V4 manifest and all 144 entries.
2. Reran `scripts/validate_baird_traceability.ps1`.
3. Parsed all seven retained Python sources with the Python AST parser.
4. Joined the 17-check registry, 37-case independent oracle, 74 direct results, and 74 browser records without using implementation comparison functions.
5. Recomputed applicability, state, reason code, required evidence, summary, denominator, registry membership, and country ambiguity evidence.
6. Confirmed the research and evidence copies of the check registry, regulatory rules, and expected-field oracle are byte-identical.
7. Reran the two-client 3.0-second deadline primitive and two-copy multipart storage probe without writing retained result files.
8. Attacked the full FastAPI ASGI stack with a real partial multipart timeout, a missing-length chunked raw overflow, and seven file parts. Temporary files were tracked so explicit close behavior could be distinguished from later object destruction.

| Check | Independent result |
|---|---:|
| Traceability validator | PASS |
| Source rows | 58 |
| Requirement and test IDs | `R-001` through `R-096`; `T-001` through `T-096` |
| Allocated implementation fixtures | 30, including 6 holdouts |
| Prohibited Unicode dash count | 0 |
| Selected checks | 17 unique |
| Architecture cases | 37 |
| Direct results and field rows | 74 and 1,258 |
| Browser results | 74 |
| Independent retained-case oracle errors | 0 |
| S33 conflicting-country results | 2 Review results with all alternative evidence refs |
| Rerun slow-client deadline primitive | PASS, 408 at 3,009.31 and 3,009.16 ms |
| Rerun two-copy multipart peak | PASS, 100,651,008 bytes, then zero |
| Full-app partial multipart deadline | FAIL, generic 400 instead of 408; rolled file not explicitly closed |
| Full-app missing-length raw overflow | FAIL, generic 400 instead of 413; rolled file not explicitly closed |
| Full-app seven-file request | FAIL for pre-route bound; parser created all 7 parts before route returned 422 |

## Blocking finding

### `RT1-B-RR4-F001` - HIGH - The real multipart path bypasses the selected deadline, overflow-status, parser-limit, and explicit-cleanup contracts

**Selected contract**

- `docs/baird/SECURITY_DATA_FLOW.md:67` requires a 3.0-second total body deadline to return 408 `upload_timeout`, clean partial artifacts, and release reservations.
- `docs/baird/SECURITY_DATA_FLOW.md:85` requires exact multipart limits and 413 before handler or decode.
- `docs/baird/TECHNICAL_SOURCE_REGISTER.md:73` says multipart counts and field sizes are bounded and spooling is cleaned on every terminal path.
- `docs/baird/ENGINEERING_BLUEPRINT.md:77,251` assigns these controls to the upload guard before candidate extraction.
- `docs/baird/BAIRD_CONTROL_HANDOFF_MATRIX.md:39,47` requires fixed, chunked, missing, and understated body tests, part-limit tests, partial-artifact cleanup, exact terminal behavior, and capacity recovery.
- `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:93,95` claims the actual multipart and upload-lifetime defects are closed for V4 rereview.

**Why the retained proof does not exercise that contract**

- `research/baird-spike/security_control_benchmark.py:128-136` tests the 3.0-second deadline against a dummy `body_consumer`, not FastAPI form parsing or the verification route.
- `security_control_benchmark.py:222-244` creates a standalone Starlette `MultiPartParser`, manually supplies `max_files`, `max_fields`, and `max_part_size`, manually copies files, and explicitly closes them. The actual app does not invoke the parser with those selected limits.
- `research/baird-spike/server.py:479-480` declares FastAPI `Form` and `File` dependencies. Framework multipart parsing therefore occurs before the route body.
- The actual six-file and 32 KiB reference checks occur only at `server.py:487-490`, after parsing.
- `server.py:299-325` raises and catches custom deadline and raw-limit exceptions around the downstream app. The full framework path converts those exceptions into a generic body-parsing response before the outer catch can produce the selected response.

**Independent full-stack observations**

I invoked `server.app` through its actual ASGI middleware stack. No retained evidence file was written.

1. A valid multipart start created one file, supplied more than 2 MiB so the Starlette spool rolled to disk, then continued one small chunk every 250 ms. At the selected total deadline the app returned HTTP 400 with `{"detail":"There was an error parsing the body"}`. It did not return 408 `upload_timeout`. The tracked rolled spool file remained open after response construction. I manually closed it after recording the result.
2. A missing-length multipart stream crossed the 25,296,896-byte raw cap after 13 chunks totaling approximately 27.26 MiB. The app again returned the same generic 400 instead of 413 `request_too_large`. The tracked rolled spool file remained open until manual cleanup.
3. A multipart request with seven file parts was fully parsed. The parser created all seven file objects before the route-level check returned 422 `invalid_panel_count`. This proves the retained app does not enforce the selected six-file parser bound before routing.

Holding a tracking reference prevents object finalization and shows whether the exceptional path explicitly closes the spool file. The required control is explicit cleanup on every terminal path, not eventual cleanup that depends on interpreter object destruction.

**Impact**

- The documented API status and actionable error contract is false for two required failure classes.
- Partial multipart cleanup is not owned explicitly on deadline and overflow.
- Admission and reservation counters can return to zero while a rolled spool handle still exists, so the counter is not sufficient proof that storage ownership ended.
- Part-count and field-size checks occur after the parser has accepted more than the selected bounds.
- The retained V4 evidence overstates closure of `BAIRD-RT3-F001`, `RT3-V2-F001`, and `RT3-V3-F001`.

**Required remediation**

1. Exercise the full FastAPI ASGI app for deadline, overflow, part-count, field-count, field-size, and cleanup evidence. Do not substitute a dummy consumer or standalone parser for the production request path.
2. Select and implement a mechanism that preserves typed upload exceptions through framework parsing, or performs bounded multipart parsing in an owned pre-route component. The response must be the selected result-free 408 for total deadline and 413 for actual-byte overflow.
3. Enforce at parser entry: at most 6 files, the selected field count, 32 KiB reference data, per-file and aggregate byte limits, and actual raw bytes for fixed, chunked, missing, and understated length.
4. Explicitly close every partially created `UploadFile` or spool handle on timeout, overflow, malformed multipart, part-limit, disconnect, and internal-error paths before releasing storage reservation.
5. Prove two concurrent slow multipart clients, a rejected third body, non-resetting 3.0-second deadline, exact 408 responses, partial-spool cleanup, zero final storage, and a successful recovery request through the full app.
6. Prove fixed-length and missing or understated-length overflow through the full app with exact 413 behavior and no handler or decoder invocation.
7. Regenerate affected security evidence, validation, remediation, traceability, and the sealed manifest, then repeat all three independent BAIRD reviews.

## Retest of prior V3 findings

| Prior finding | V4 result | Evidence |
|---|---|---|
| `RT1-B-RR3-F001` warning punctuation false clean | CLOSED | No punctuation is deleted before exact comparison. S28 through S30 are readable Mismatch cases and S31 is low-evidence Review. All direct and browser rows match the separate oracle. |
| `RT1-B-RR3-F002` conflicting country candidates | CLOSED | Distinct candidates produce `country_ambiguous` Review with all alternative evidence refs. S32 through S37 cover duplicate, conflict, missing, unreadable, decoy, and mismatch behavior. |
| `RT1-B-RR3-F003` 200 ms queue and ownership | CLOSED | Bounded lock acquisition, shielded cancellation ownership, timeout, replacement, empty request directories, zero reservations, and recovery are present in the actual ASGI control evidence. |
| `RT1-B-RR3-F004` two-copy arithmetic | CLOSED FOR ARITHMETIC; UPLOAD LIFECYCLE REOPENED | The 101,187,584-byte reservation correctly covers the measured 100,651,008-byte two-request peak within 128 MiB. Exceptional full-app multipart ownership fails F001. |
| `RT1-B-RR3-F005` regulatory-rule and read-only readiness | CLOSED | Exact model, check-registry, and regulatory-registry hashes and versions plus non-writable assets precede readiness. Six negative startup probes fail closed. |
| `RT1-B-RR3-F006` total upload deadline | REOPENED | The primitive works, but the real FastAPI multipart path returns generic 400 and does not explicitly close the partial rolled file. See F001. |
| `RT1-B-RR3-F007` stale Intake values | CLOSED | `ASM-007` points to the sealed evidence authority and preserves the cold miss. `ASM-012` states 30 allocated implementation fixtures, 6 holdouts, and distinguishes the 37-case feasibility corpus. |
| `RT2-BAIRD-RR3-001` warning punctuation repair | CLOSED | Exact readable mutations cannot become Match; uncertain punctuation remains Review. |
| `RT3-V3-F001` slow upload and unsupported Fly deadline | REOPENED IN IMPLEMENTATION | Unsupported Fly total-request wording is removed and the application clock is selected, but the real multipart terminal path fails F001. |
| `RT3-V3-F002` stale Intake evidence | CLOSED | The active Intake and sealed BAIRD authority no longer contain competing current counts or timings. |

## Retest of earlier RT1 findings

| Finding family | V4 result | Disposition |
|---|---|---|
| `RT1-B-F001` load-bearing feasibility | CLOSED FOR BAIRD DIRECTION | Warm evidence supports selection. Cold remains honestly NOT CLOSED LOCALLY and is a deployed hard stop. |
| `RT1-B-F002` warning states and aggregation | CLOSED | All 17 rows are explicit, fail closed, and oracle checked. |
| `RT1-B-F003` resource envelope | REOPENED IN PART | Memory, pixels, two-copy arithmetic, and concurrency are selected. Exceptional multipart lifecycle remains false in the retained app. |
| `RT1-B-F004` performance and timeout contracts | REOPENED IN PART | User, worker, queue, and cold clocks are coherent. The real upload deadline does not deliver its selected terminal contract. |
| `RT1-B-F005` alternatives and fallbacks | CLOSED | Options, evidence classes, reopen rules, and no-cloud-fallback boundary remain explicit. |
| `RT1-B-RR-F001` five-second hard cancellation | CLOSED | Five seconds is only the warmed p95 objective. |
| `RT1-B-RR-F002` incomplete result and false clean | CLOSED | Every retained result has 17 rows; newly attacked warning and country cases prevent clean results. |
| `RT1-B-RR-F003` capitalization and punctuation | CLOSED | Brand and producer case or punctuation variations remain Review, not silent Match. |
| `RT1-B-RR-F004` source locators | CLOSED | All selected source rows have valid control and test ownership. |
| `RT1-B-RR2-F001` proof and warning applicability omission | CLOSED | Both are independent active checks with retained branch evidence. |
| `RT1-B-RR2-F002` uncovered false-clean rules | CLOSED FOR SELECTED FIELD CASES | Warning punctuation and country ambiguity gaps are corrected. |
| `RT1-B-RR2-F003` incompatible result contracts | CLOSED | Internal states and three exact summaries are consistent. |
| `RT1-B-RR2-F004` timeout recovery ordering | CLOSED FOR OCR WORK | Worker timeout, ownership, asynchronous replacement, readiness, and recovery are demonstrated. |
| `RT1-B-RR2-F005` wrong I2R mapping authority | CLOSED | Both source coverage and control handoff are named. |

## Retest of earlier RT2 findings

| Finding family | V4 result | Disposition |
|---|---|---|
| `RT2-BAIRD-001` extraction and latency feasibility | CLOSED FOR BAIRD DIRECTION | 37 cases and 74 browser attempts support the selected architecture; deployed and cold gates remain. |
| `RT2-BAIRD-002` reference-conditioned candidate selection | CLOSED | Extraction remains reference-blind and ambiguity is preserved. |
| `RT2-BAIRD-003` warning presentation and aggregation | CLOSED | One matrix, registry, rules artifact, oracle, and execution contract agree. |
| `RT2-BAIRD-004` weak fallback | CLOSED | Systematic field-family failure reopens BAIRD or requires requester-approved scope change. |
| `RT2-BAIRD-005` Try sample ambiguity | CLOSED | One activation has one deterministic complete-sample behavior. |
| `RT2-BAIRD-RR-001` active warning rows omitted | CLOSED | Every applicable warning row executes and aggregates. |
| `RT2-BAIRD-RR-002` cold clock omission | CLOSED BY HONEST DISPOSITION | Process start includes assets, OCR construction, warmup, and first browser result. The 11,557.18 ms miss remains open. |
| `RT2-BAIRD-RR-003` biased timeout denominator | CLOSED | All 74 valid browser attempts remain in one fixed denominator. |
| `RT2-BAIRD-RR2-001` proof/applicability denominator | CLOSED | All 17 rows are reconciled in every retained case. |
| `RT2-BAIRD-RR2-002` heading exactness | CLOSED | Missing, altered, and extra punctuation are distinct non-Match branches. |

## Retest of earlier RT3 findings

| Finding family | V4 result | Disposition |
|---|---|---|
| `BAIRD-RT3-F001` pre-parser upload limits | REOPENED | The real multipart path does not preserve selected errors, parser limits, or explicit exceptional cleanup. See F001. |
| `BAIRD-RT3-F002` blocking-work ownership | CLOSED | One child, bounded queue, cancellation shield, true completion, cleanup, replacement, and recovery are proven. |
| `BAIRD-RT3-F003` client identity and Origin | CLOSED AT BAIRD LEVEL | Exact Fly client identity and Host/Origin decisions plus public tests are owned. |
| `BAIRD-RT3-F004` runtime-egress overclaim | CLOSED | Only the bounded port property is claimed and TCP 65535 remains disclosed. |
| `BAIRD-RT3-F005` model rights and provenance | CLOSED | Exact artifacts, hashes, notices, paths, and build-only acquisition remain selected. |
| `BAIRD-RT3-F006` hosting privacy and caching | CLOSED AT BAIRD LEVEL | Public notice, data inventory, log allowlist, and no-store test matrix remain explicit. |
| `BAIRD-RT3-F007` immutable promotion | CLOSED | Release tuple, digest promotion, readback, evidence, and rollback are explicit. |
| `BAIRD-RT3-F008` executable traceability | CLOSED | The current 58-source and 96-requirement/test chains validate. |
| `RT3-RR1` trusted client identity | CLOSED AT BAIRD LEVEL | Spoof, duplicate, forwarding, limiter, abort, and recovery tests are owned. |
| `RT3-RR2` no-store responses | CLOSED AT BAIRD LEVEL | Success and all named error classes are assigned to public proof. |
| `RT3-RR3` semantic source and finding traceability | CLOSED | Active source values and current finding mappings agree. |
| `RT3-V2-F001` global admission and temporary storage | REOPENED IN PART | Admission and arithmetic pass; real exceptional multipart cleanup and parser limits do not. |
| `RT3-V2-F002` field-level correctness evidence | CLOSED | The independent oracle covers all 17 rows in 37 cases with zero retained-case error. |
| `RT3-V2-F003` readiness omitted governed assets | CLOSED | Both registries, three model files, versions, hashes, and read-only state are checked before readiness. |
| `RT3-V2-F004` Fly egress wording | CLOSED | Port-level semantics remain accurate and bounded. |

## Assignment, scope, and deliverable fidelity

No additional assignment drift was found:

- The product remains a standalone proof-of-concept with no COLA integration or government decision authority.
- Core scope remains one submission with 1 to 6 label panels, application values, evidence-first field comparison, warning checks, uncertainty, and human judgment.
- Batch remains conditional and blocked behind the complete single-submission gate.
- Local packaged OCR with no runtime model download still fits the blocked-outbound stakeholder constraint.
- The visible latency measure remains Verify activation through complete rendered and announced results. Server timing is diagnostic only.
- Physical warning type size remains human-only because reliable scale evidence is absent.
- Grok and Gemini proposals remain inspiration only. Their official identity, named staff, legal pass/return actions, generated text errors, confidence theater, and proposed stacks are not requirements authority.
- Repository source, README setup/run instructions, brief approach/tools/assumptions documentation, deployed URL, clean-checkout proof, and immutable deployment provenance remain explicit deliverables.
- React, FastAPI, RapidOCR, ONNX, one same-origin container, one always-on Fly Machine, no database, and deterministic comparison remain coherent selections for the time-constrained prototype.

## Advancement condition

Correct `RT1-B-RR4-F001` in one governed revision. Regenerate the affected security, validation, remediation, traceability, and snapshot artifacts. Then rerun all three independent BAIRD reviews on the same sealed revision.

I2R must not begin from V4 because it would inherit a claimed upload contract that the retained framework path demonstrably does not satisfy.
