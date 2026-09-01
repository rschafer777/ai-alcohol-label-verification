REWORK_REQUIRED

# BAIRD V4 Security, Delivery, and Traceability Re-review

**Reviewer:** Independent Red Team 3, security, delivery, and traceability  
**Review date:** 2026-08-31  
**Reviewed snapshot:** `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V4.sha256`  
**Expected and observed manifest SHA-256:** `8e2b88b12699f8192bc1b66637885ac9c8fbc1f72cd4158604775d0d2f80932b`  
**Manifest entries:** 144  
**Initial hash verification:** 144 matched, 0 missing, 0 mismatched  
**Material findings:** 3 Medium

## 1. Binary decision

The V4 package is not ready to advance to I2R. The architecture, selected OCR path, regulatory scope, field oracle, warm evidence, readiness asset checks, two-copy arithmetic, bounded Fly egress claim, release provenance contract, and traceability structure are substantially sound. The local cold result also remains honestly open.

Three security evidence gaps remain in the upload and cancellation boundary:

1. the six-file and one-field multipart limits are proven only on a separately constructed parser, not on the retained FastAPI application path;
2. the slow-drip deadline probe uses a body consumer that creates no multipart spool files, so it does not prove the claimed cleanup of partial parser artifacts; and
3. the cancellation harness issues one cancellation, while the retained handler can leave its shielded ownership wait on a second cancellation and execute cleanup while the worker thread still uses request paths.

These are not product polish issues. They concern the public unauthenticated upload surface and the rule that request artifacts must remain owned until work has truly ended. The package labels the affected controls closed and cites retained execution as proof. That proof is incomplete, so the BAIRD gate cannot be CLEAR.

## 2. Review method

I reviewed the complete sealed Intake and BAIRD package, all prior RT1, RT2, and RT3 reports, the remediation record, source coverage, control handoff, retained research source, generated fixtures, dependency locks, model and regulatory provenance, and raw evidence. I also performed these independent checks:

1. verified the V4 manifest SHA-256 and all 144 listed file hashes before review;
2. reran `scripts/validate_baird_traceability.ps1`;
3. parsed all seven retained Python sources through the Python AST without writing bytecode;
4. independently expanded the 37-case oracle, reconciled all 74 direct results and 1,258 field rows, and recomputed summaries, evidence requirements, false-clean results, and false-mismatch results;
5. independently recomputed the 74 browser-attempt counts, rendered row coverage, cache headers, errors, timeouts, and nearest-rank p95;
6. independently checked the five cold runs and six fail-closed readiness results;
7. reconciled every retained research result with its governed evidence copy;
8. inspected the application middleware order, parser entry point, worker queue, termination, restart, cancellation, upload cleanup, and admission accounting source;
9. recomputed the two-request parser plus controlled-copy peak against the reservation and quota;
10. semantically sampled source, ADR, BG, THR, R, and T ownership chains, including all prior RT3 findings; and
11. rechecked current primary Fly, RapidOCR, Starlette, and TTB sources where the selected decisions depend on current behavior.

## 3. Integrity, traceability, and evidence recomputation

### 3.1 Seal and source checks

| Check | Result |
|---|---|
| Manifest SHA-256 | PASS |
| Manifest entry count | PASS, 144 |
| Missing or mismatched entries | PASS, 0 |
| Traceability validator | PASS |
| Source rows | PASS, 58 |
| Control rows | PASS, 12 ADR, 8 BG, 18 THR |
| Requirement IDs | PASS, `R-001` through `R-096` |
| Test IDs | PASS, `T-001` through `T-096` |
| Fixture allocation IDs | PASS, `FX-001` through `FX-030` |
| Python AST parse | PASS, 7 files |
| Prohibited Unicode dash scan before report | PASS, 0 |

### 3.2 Result evidence

| Check | Independent result |
|---|---|
| Selected checks | 17 unique IDs |
| Architecture cases | 37 |
| Direct runs | 74 |
| Direct field rows | 1,258 |
| Applicability, state, reason, or summary errors | 0 |
| Missing required evidence | 0 |
| False clean | 0 |
| False mismatch | 0 |
| Direct p95 | 4,062.84 ms |
| Browser attempts and complete results | 74 and 74 |
| Browser errors and timeouts | 0 and 0 |
| Browser field and DOM rows | 17 on every attempt |
| Browser success cache header | `no-store, private` on every attempt |
| Browser p95 | 4,213.30 ms |
| Cold runs | 5 |
| Cold conservative p95 | 11,557.18 ms, correctly NOT CLOSED |
| Research/evidence copy equality | PASS for details, fixtures, metadata, browser, cold, security-control, and runtime-control files |

The current field and latency evidence is internally consistent. The emitted field order places `warning_heading_uppercase` before `warning_wording`, while the registry lists those two in the opposite order. This does not affect membership, uniqueness, aggregation, or the current browser contract and is not material at BAIRD.

### 3.3 Storage arithmetic

The retained numbers reconcile:

- raw envelope per request: 25,296,896 bytes;
- reservation per request at copy factor 2: 50,593,792 bytes;
- two-request reservation: 101,187,584 bytes;
- application quota: 134,217,728 bytes;
- independently checked retained visible peak: 100,651,008 bytes;
- margin between reservation and observed peak: 536,576 bytes; and
- final retained visible bytes: 0.

The arithmetic and successful near-limit two-copy probe pass. Finding `RT3-V4-F001` concerns which parser configuration the real application uses, not this arithmetic.

## 4. Attack cases

| Attack case | Required property | Result |
|---|---|---|
| Two slow clients send a chunk every 250 ms | One 3.0 second clock from pre-body admission, no activity reset | PASS for the receive wrapper |
| Third request arrives while two bodies are admitted | Reject before any body read | PASS |
| Two near-limit multipart bodies exist in parser and controlled copies | Peak stays below reservation and 128 MiB quota, then returns to baseline | PASS in standalone parser probe |
| Seven or hundreds of small files hit the real FastAPI endpoint | Six-file parser limit applies before route logic and cleanup is bounded | FAIL, see `RT3-V4-F001` |
| Slow multipart body crosses the 1 MiB spool threshold and then times out | Partial parser file is closed and removed before 408 and reservation release | NOT PROVEN, see `RT3-V4-F002` |
| One request runs and one waits for the worker | Waiter returns 503 near 200 ms | PASS, 219.73 ms observed |
| Forced worker hang reaches 6.25 second child deadline | Result-free 504, old child joined, readiness 503, one warmed replacement | PASS |
| One caller cancellation occurs during a worker hang | Request waits through worker termination before cleanup | PASS for one cancellation |
| Cancellation repeats during shielded ownership wait or shutdown | No finalizer runs before worker completion or termination | FAIL by source path and untested, see `RT3-V4-F003` |
| Wrong or writable governed runtime asset | Readiness fails closed | PASS for the retained probes |
| Common outbound ports are tested under selected Fly policy | Only the bounded 53, 80, and 443 denial is claimed; TCP 65535 remains disclosed | PASS at BAIRD contract level, deployed proof remains open |
| Public edge supplies malformed or duplicate client identity | Exact Fly identity policy fails closed | PASS at BAIRD contract level, deployed proof remains open |
| Public success or error response is cacheable | `no-store, private` plus `no-cache` on every class | PASS at BAIRD contract level, deployed full-class proof remains open |
| Running deployment differs from submitted source or image | Immutable release tuple and Machine image readback stop release | PASS at BAIRD contract level |
| Batch code begins before core gates | Batch remains absent and gated | PASS |

## 5. Material findings

### `RT3-V4-F001`: The actual FastAPI upload path does not apply the multipart limits proven by the standalone parser

**Severity:** Medium  
**Affected controls:** `BAIRD-RT3-F001`, `RT3-V2-F001`, `THR-001`, `R-021`, `T-021`  
**Files:** `research/baird-spike/server.py:31`, `server.py:480-488`, `research/baird-spike/security_control_benchmark.py:197-247`, `docs/baird/SECURITY_DATA_FLOW.md:58-71`, `docs/baird/BAIRD_CONTROL_HANDOFF_MATRIX.md:39`, `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:46,81,93`

The retained application declares `MAX_FILES = 6`, but its FastAPI route accepts `files: list[UploadFile] = File(...)`. The six-file check runs inside the route after framework multipart parsing has completed. The route does not pass `max_files=6`, `max_fields=1`, or the selected part limits to the parser.

The retained multipart probe does pass `max_files=server.MAX_FILES`, but it constructs `MultiPartParser` directly and never sends the body through `server.app`. It therefore proves the desired parser configuration, not the parser configuration used by the retained application. Starlette 0.47.3 defaults `max_files` and `max_fields` to 1,000 in the parser used by the selected FastAPI version. The official source is [Starlette 0.47.3 formparsers.py](https://github.com/encode/starlette/blob/0.47.3/starlette/formparsers.py#L120-L144).

An attacker can make the retained app parse far more than six small file parts before the route returns `invalid_panel_count`. The raw-byte and two-admission caps limit total bytes, but they do not enforce the selected file-count, field-count, or handler-before-limit property. This also means the V4 proof cannot support the statement that exact multipart limits apply on the application path.

**Required remediation:**

1. Put the six-file, one-field, seven-part, 32 KiB field, and per-part controls on the actual application parser path before route business logic.
2. Exercise the complete `server.app` stack with 0, 6, 7, and many tiny files, extra fields, a field above 32 KiB, and malformed boundaries.
3. Assert body reads, route/decoder entry, open-file and directory counts, response code, reservation release, and post-request baseline.
4. Ensure the standalone benchmark cannot pass unless the real application configuration passes.

**Closure proof:** The real FastAPI endpoint rejects every above-limit part and field case under the selected limits, before route or decoder work, and restores the filesystem, handle, admission, and reservation baseline.

### `RT3-V4-F002`: The slow-drip probe bypasses multipart parsing and cannot prove partial spool cleanup

**Severity:** Medium  
**Affected controls:** `RT3-V3-F001`, `THR-009`, `R-029`, `T-029`, `BG-006`, `R-018`, `T-018`  
**Files:** `research/baird-spike/security_control_benchmark.py:123-193`, `docs/baird/SECURITY_DATA_FLOW.md:67,93,156`, `docs/baird/BAIRD_CONTROL_HANDOFF_MATRIX.md:47`, `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:118-136`, `docs/baird/evidence/EVIDENCE_VALIDATION.md:28`, `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:95`

The fixed 3.0 second clock is implemented correctly in the receive wrapper and the two slow receive functions demonstrate that chunk activity does not reset it. However, the benchmark installs a custom `body_consumer` that only drains receive messages. It does not invoke `MultiPartParser`, create an `UploadFile`, cross the 1 MiB spool threshold, or create a controlled request copy.

The package then states that the slow-drip timeout cleans partial request artifacts. That conclusion does not follow from the probe. The separate multipart probe tests only successful, fully delivered bodies. It never combines partial multipart state with `UploadBodyDeadlineExceeded`.

This distinction matters for the selected dependency. Starlette 0.47.3 explicitly closes its parser files in the `MultiPartException` path. The application deadline raises a different exception from the wrapped ASGI receive. Cleanup may occur through object finalization in a particular interpreter run, but the V4 evidence does not establish the selected explicit lifecycle guarantee.

**Required remediation:**

1. Send two real multipart requests through the complete application stack.
2. Deliver enough valid file content to force disk spooling, then continue valid boundary-aware chunks every 250 ms past the fixed deadline.
3. Prove both responses are result-free 408 values and that all parser files, request directories, handles, admission counters, and reservations return to the exact baseline before recovery is accepted.
4. Add fixed-length, understated-length, absent-length, and streamed-overflow variants through the same real parser path.
5. If framework cleanup is not explicit for the deadline exception, add application-owned parser cleanup rather than relying on garbage collection.

**Closure proof:** A full-stack partial multipart slow-drip test observes nonzero spool use before timeout, then zero bytes and zero open request artifacts after both 408 responses, followed by a successful request.

### `RT3-V4-F003`: Cancellation ownership is not robust to repeated cancellation and the abort-storm proof is absent

**Severity:** Medium  
**Affected controls:** `BAIRD-RT3-F002`, `RT1-B-RR3-F003`, `THR-008`, `THR-011`, `R-007`, `T-007`, `R-028`, `T-028`, `R-031`, `T-031`  
**Files:** `research/baird-spike/server.py:525-534`, `server.py:558-562`, `research/baird-spike/runtime_control_benchmark.py:136-150`, `runtime_control_benchmark.py:173-191`, `docs/baird/SECURITY_DATA_FLOW.md:77,92,95,132-139`, `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:47,66,77,92`

The retained source protects the worker task from the first cancellation, catches one `asyncio.CancelledError`, and awaits the same task again under `asyncio.shield`. The inner wait catches only `Exception`. A second cancellation is another `CancelledError`, which is not caught there. It can leave the wait and reach the route finalizer while the `to_thread` worker still owns and uses the request paths.

The retained runtime harness calls `disconnected.cancel()` once. It proves one-cancellation behavior and the forced child timeout path. It does not execute a repeated cancellation, shutdown cancellation, or abort storm despite `T-028` and the remediation record claiming abort-storm ownership and recovery.

**Required remediation:**

1. Make work and artifact ownership independent of the number of caller cancellations. A worker-owned request directory, a separate supervisor task that cannot be cancelled by the request, or an explicit cancellation-deferral loop are viable patterns.
2. Test a second cancellation during the ownership wait, repeated start-and-abort traffic, and shutdown while a worker and waiter exist.
3. Assert that no request path is removed until the worker has returned or the child has been terminated and joined.
4. Assert one OCR child, bounded waiters, readiness 503 during replacement, zero final counters, empty request directories, and complete recovery.

**Closure proof:** Repeated cancellation and forced shutdown cannot trigger cleanup or capacity release before true worker exit, and the post-storm process has exactly one ready child and no retained request content.

## 6. Retest of prior findings

| Prior finding | V4 result |
|---|---|
| `BAIRD-RT3-F001`, pre-parser limits | REOPENED IN PART by `RT3-V4-F001` and `RT3-V4-F002` |
| `BAIRD-RT3-F002`, killable work ownership | REOPENED IN PART by `RT3-V4-F003` |
| `BAIRD-RT3-F003`, client identity and Origin/Host | CLOSED AT BAIRD LEVEL, exact Fly and same-origin tests remain release gates |
| `BAIRD-RT3-F004`, Fly egress semantics | CLOSED, only conventional 53/80/443 denial is claimed and TCP 65535 is disclosed |
| `BAIRD-RT3-F005`, model rights and provenance | CLOSED, exact artifacts, hashes, sources, attribution, notices, and stop-on-change remain selected |
| `BAIRD-RT3-F006`, platform metadata and no-store | CLOSED AT BAIRD LEVEL, public full-response-class proof remains a release gate |
| `BAIRD-RT3-F007`, immutable OCI promotion | CLOSED, complete release tuple and Machine image readback remain mandatory |
| `BAIRD-RT3-F008`, source/control ownership | CLOSED structurally and by semantic sampling |
| `RT3-RR1`, trusted client identity proof | CLOSED AT BAIRD LEVEL |
| `RT3-RR2`, no-store proof ownership | CLOSED AT BAIRD LEVEL |
| `RT3-RR3`, semantic traceability | CLOSED |
| `RT3-V2-F001`, global admission and spool quota | CLOSED for count and arithmetic, actual parser-limit proof reopened by `RT3-V4-F001` |
| `RT3-V2-F002`, field oracle and country/proof completeness | CLOSED |
| `RT3-V2-F003`, runtime readiness assets | CLOSED |
| `RT3-V2-F004`, bounded port-level egress wording | CLOSED |
| `RT3-V3-F001`, total upload deadline | CLOSED for clock ownership and no-reset behavior, partial-parser cleanup proof reopened by `RT3-V4-F002` |
| `RT3-V3-F002`, stale Intake assumptions | CLOSED |
| `RT1-B-RR3-F001`, warning punctuation false clean | CLOSED |
| `RT1-B-RR3-F002`, conflicting country candidates | CLOSED |
| `RT1-B-RR3-F003`, queued/cancelled worker ownership | REOPENED IN PART by `RT3-V4-F003` |
| `RT1-B-RR3-F004`, two-copy spool accounting | CLOSED for arithmetic and successful-body peak |
| `RT1-B-RR3-F005`, regulatory rules and read-only readiness | CLOSED |
| `RT1-B-RR3-F006`, admitted body lifetime | CLOSED for deadline, reopened only for partial-parser cleanup proof |
| `RT1-B-RR3-F007`, evidence and fixture authority | CLOSED |
| `RT2-BAIRD-RR3-001`, exact warning punctuation | CLOSED |

## 7. Current-source checks

- [Fly Network Policies](https://fly.io/docs/machines/guides-examples/network-policies/) still documents directional allow rules, default denial for the covered direction, and the limitation that policies do not affect Fly Proxy traffic. The package preserves that bounded meaning.
- [Fly request headers](https://fly.io/docs/networking/request-headers/) still defines `Fly-Client-IP` as the client address from Fly Proxy's perspective and warns that added proxy topology changes trust handling. The selected one-proxy profile remains defensible.
- [Fly application configuration](https://fly.io/docs/reference/configuration/) still documents request concurrency and connection `idle_timeout`. It does not establish a total request-body deadline. V4 correctly assigns the 3.0 second total body clock to the application and does not restore the old Fly 9.0 second claim.
- [RapidOCR releases](https://github.com/RapidAI/RapidOCR/releases/tag/v3.4.2) and the pinned source remain consistent with the selected 3.4.2 evidence. A newer upstream release does not invalidate a deliberately locked version.
- [TTB distilled-spirits health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) continues to support the exact warning text, 0.5 percent applicability boundary, uppercase and bold heading, non-bold remainder, continuity, separation, contrast, legibility, and physical-size limitation.
- [TTB distilled-spirits labeling](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling) continues to support the selected field families and the imported-only country rule. The package correctly avoids a comprehensive-compliance claim.

## 8. Controls that pass and must not regress

The following decisions are fit to carry into the corrected snapshot:

- one same-origin React, FastAPI, and local RapidOCR modular monolith;
- no LLM or external service in the authoritative decision path;
- exact selected model, selected-check registry, and regulatory-rules registry hashes and versions;
- fail-closed readiness, representative warmup, and non-writable governed assets;
- 17 deterministic result rows with explicit applicability, state, reason, evidence, capability, and aggregation;
- exact warning punctuation behavior with uncertainty routed to Review;
- all alternative country evidence retained when candidates conflict;
- zero false clean across the 37-case architecture corpus;
- warm browser feasibility under the equivalent local envelope;
- honest local cold failure and deployed restart stop;
- two admitted POSTs, 200 ms worker acquisition, one killable OCR child, and asynchronous replacement;
- two-copy reservation arithmetic within the 128 MiB application envelope;
- no database, persistent volume, raw-content logs, remote input URLs, runtime downloader, or external inference dependency;
- exact public identity, Host, Origin, CORS, CSRF, error, no-store, privacy, and log obligations;
- Fly policy wording limited to the tested conventional ports, with TCP 65535 disclosed;
- immutable OCI build and promotion tuple with deployed digest readback and rollback;
- a separate 30-fixture implementation corpus with 6 sealed holdouts;
- batch deferred until every core gate passes; and
- source repository, all source, README, approach/tools/assumptions documentation, public URL, and same-revision deployment deliverables.

## 9. Honest open release stops

The V4 package correctly keeps these as implementation or deployment stops rather than claiming local closure:

- constructed 30-fixture corpus and sealed holdouts;
- public Fly client-identity behavior;
- deployed no-store behavior across every response class;
- application and platform log inspection;
- Fly network-policy readback and denied 53/80/443 probes;
- current `iad` class, price, sleep, concurrency, readiness, and image readback;
- deployed warmed p95 at or below 5.0 seconds with 100 percent complete valid results;
- five deployed restart trials below 10 seconds with no traffic before readiness;
- deployed peak memory and cleanup behavior;
- clean-checkout build, notices, SBOM, immutable release manifest, public smoke, rollback digest, and GitHub/deployment equality; and
- batch omission unless the separate core-first gate later authorizes it.

Historical reports contain measurements from their own sealed V2 and V3 snapshots. They are clearly versioned review records, not current evidence authority. The active Intake and BAIRD documents point to the V4 evidence and preserve the current warm, cold, fixture, and release interpretation. No additional active-document drift was found outside the three evidence overclaims above.

## 10. Required gate for another review

Before another V4 successor review:

1. enforce the exact selected multipart limits on the real application parser path;
2. replace the surrogate part-count and slow-drip proofs with complete application-stack probes;
3. prove partial spool cleanup after an actual multipart body timeout;
4. make cancellation ownership robust to repeated cancellation and shutdown;
5. execute the abort-storm, handle, directory, child-count, counter, readiness, and recovery assertions already reserved by `T-007`, `T-018`, `T-021`, `T-028`, `T-029`, and `T-031`;
6. regenerate affected evidence and all active claims from the same execution;
7. preserve every passing V4 field, performance, readiness, security, provenance, regulatory, traceability, and release-stop decision;
8. seal one corrected manifest and have all three reviewers inspect that identical snapshot.

Until those conditions are met, BAIRD remains open and I2R must not begin.
