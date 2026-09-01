REWORK_REQUIRED

# RT1 BAIRD Architecture and Requirements Fidelity Rereview 3

Review date: 2026-08-31

Role: Independent architecture and requirements fidelity reviewer

## Reviewed snapshot

- Manifest: `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V3.sha256`
- Expected and observed manifest SHA-256: `97707b49f130d37b1fc5303abb3f3fa87502efe23000f8f73089f79aa01277bc`
- Expected and observed entries: 119
- Missing files: 0
- Hash mismatches: 0

I verified the manifest hash and every listed file before substantive review. I repeated the complete verification immediately before writing this report. This report is outside the manifest. I did not modify any snapshotted file.

## Gate basis

The V3 package is substantially stronger than V2. It now has a 17-check registry, a separate 27-case expected-field oracle, 54 direct runs, 54 real-browser runs, exact field-level reconciliation, proof and warning-applicability branches, forced worker timeout and recovery evidence, startup hash-failure probes, and honest cold-start disposition. The React, FastAPI, RapidOCR, ONNX, single-container, always-on Fly architecture still fits the assignment and the attested network and delivery boundaries.

BAIRD cannot advance to I2R on this snapshot. Retained code can still produce a clean result for a readable warning punctuation mutation and for conflicting import-origin candidates. The selected two-request worker and temporary-storage contracts are also not realized by the retained runtime evidence: a queued request can outlive its route deadline while its request directory is deleted, and the 64 MiB spool calculation omits the already-spooled multipart copy. The package additionally lacks an owned total upload deadline and has stale load-bearing Intake evidence. These are architecture and requirements-fidelity defects, not I2R detail choices.

## Evidence reviewed and method

I treated the original assignment, stakeholder notes, and attested Intake sources as requirements evidence. I treated the Grok and Gemini documents and images as non-authoritative design inspiration. I reviewed:

- the complete Intake, including source register, source requirements, scope, success definition, assumptions, decision log, regulatory register, design-reference analysis, and Intake exit record;
- every file in `docs/baird`, including ADRs, architecture, UX, warning, security, performance, deployment, control handoff, source coverage, traceability, feasibility evidence, model BOM, fixture allocation, and I2R handoff;
- every snapshotted prior RT1, RT2, and RT3 report and `BAIRD_RT_REMEDIATION.md`;
- the retained RapidOCR spike, server, browser and cold benchmarks, security-control probe, 30 fixtures, 17-check registry, independent expected-field manifest, and all raw result files;
- current official TTB warning and distilled-spirits labeling sources, current eCFR Part 16 and section 5.63, and current Fly configuration, network-policy, pricing, request-header, and CPU guidance where those sources affect the selected design.

Independent checks produced the following results:

| Check | Result |
|---|---:|
| Traceability validator | PASS |
| Attested source rows | 58 |
| ADR, BAIRD gate, and threat rows | 12, 8, and 18 |
| Requirement and test IDs | `R-001` through `R-096`; `T-001` through `T-096` |
| Fixture IDs | `FX-001` through `FX-030` |
| Selected registry rows | 17 unique checks |
| Independent oracle cases | 27 |
| Direct runs and field rows | 54 and 918 |
| Browser runs | 54 |
| Independent retained-case field errors | 0 |
| Missing required retained-case evidence | 0 |
| Retained-case false clean or false mismatch | 0 |
| Warm direct p95 | 3,802.40 ms |
| Warm browser p95 | 3,730.50 ms |
| Forced worker-hang response | Result-free 504 at 6,325.75 ms, then one-child recovery |
| Cold p95 | 10,845.35 ms, honestly NOT CLOSED LOCALLY |

The retained evidence is internally correct for its enumerated cases. The blocking findings below arise from uncovered executable paths and contradictions in the selected runtime and evidence contracts.

## Material findings

### `RT1-B-RR3-F001` - HIGH - Warning punctuation reconstruction can manufacture an exact Match and a clean aggregate

**Requirements and design contract**

- `docs/baird/WARNING_CAPABILITY_MATRIX.md:8-9` allows warning Match only for exact prescribed characters after whitespace and line-wrap normalization, and requires readable punctuation mutation to be Mismatch.
- `docs/baird/ENGINEERING_BLUEPRINT.md:189` repeats that only OCR line wrapping and repeated whitespace may be ignored.
- `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:72` claims no readable negative warning case can remain clean.

**Executable evidence**

- `research/baird-spike/spike.py:277-280` removes a final period from an observed warning-body row whenever the next OCR row begins with a lowercase character. This is not whitespace or line-wrap normalization. It changes observed punctuation.
- `research/baird-spike/spike.py:588-589` then compares the altered body and can return `warning_wording_exact`.
- `research/baird-spike/spike.py:574-578` also strips a period from an observed `GOVERNMENT WARNING:.` heading before returning `warning_heading_exact`. The separate emphasis row prevents a fully clean result for that heading in the current slice, but the exactness row is still false.

I exercised the warning comparator in memory, without editing project files. The observed body contained an added period at an OCR row boundary. The post-reconstruction body equaled the canonical string, every applicable warning row returned Match, and the aggregate was `No differences found in checked fields`.

S21 covers a missing colon and S22 covers an added word. Neither case covers the period-deletion branches. This directly reopens `RT1-B-F002`, `RT1-B-RR-F002`, `RT1-B-RR2-F002`, `RT2-BAIRD-003`, `RT2-BAIRD-RR-001`, and `RT2-BAIRD-RR2-002`.

**Required remediation**

1. Remove punctuation-deleting repair from the exact warning path. Only whitespace and line wrapping may normalize away.
2. If OCR punctuation evidence is uncertain, emit Review or Not verified. Do not transform it into Match.
3. Add independent-oracle fixtures for uppercase `GOVERNMENT WARNING:.`, an added body period at a row boundary, duplicated punctuation, and a low-evidence punctuation artifact.
4. Require readable mutations to be Mismatch and low-evidence cases to be Review, then rerun direct, browser, oracle, and zero-false-clean validation.

### `RT1-B-RR3-F002` - HIGH - Conflicting country candidates can be hidden behind the first matching candidate

**Requirements and design contract**

- `docs/baird/ENGINEERING_BLUEPRINT.md:151-164` requires candidate generation before comparison and requires multiple independently plausible candidates to be Ambiguous. An ambiguous field cannot be Match, and expected data cannot resolve the ambiguity.
- Country of origin is an active, aggregating check for imported references in the 17-check registry.

**Executable evidence**

- `research/baird-spike/spike.py:255-268` retains every observed `PRODUCT OF` country candidate.
- `research/baird-spike/spike.py:544-552` evaluates only `countries[0]`. It never checks whether a second distinct candidate exists.

I exercised this path in memory with two independently observed candidates, `USA` and `CANADA`, and an imported reference of `USA`. The country row returned Match using only the first candidate, and an otherwise matching result aggregated to `No differences found in checked fields`.

The retained oracle has one matching import case but no competing-country case. This reopens the false-clean portion of `RT1-B-RR2-F002` and `RT3-V2-F002`. It also shows that the written reference-blind candidate policy is not fully implemented by the retained feasibility proof.

**Required remediation**

1. Deduplicate and evaluate all independently plausible country candidates before comparison.
2. Emit Review with all material alternatives and their panel/polygon evidence when distinct candidates remain.
3. Add imported fixtures for duplicate-same, conflicting, missing, unreadable, and decoy origin candidates.
4. Extend the independent oracle so no conflicting-country case can aggregate clean.

### `RT1-B-RR3-F003` - HIGH - The selected 200 ms queue and true-ownership timeout model is not implemented by the retained runtime slice

**Selected architecture**

- `docs/baird/ARCHITECTURE_DECISIONS.md:74` selects one active OCR request and at most one request pending for 200 ms.
- `docs/baird/ENGINEERING_BLUEPRINT.md:247-260` requires the parent to retain the worker slot, handles, and request directory until actual child completion or exit. It also requires one pending request to wait no more than 200 ms.
- `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:74` claims timeout ordering and ownership are closed for V3 rereview.

**Retained runtime**

- `research/baird-spike/server.py:190-203` acquires `verify_lock` with an unbounded blocking context. There is no 200 ms acquisition bound.
- `research/baird-spike/server.py:463-466` runs that blocking method in `asyncio.to_thread` under a 6.75-second `wait_for`.
- Canceling the await does not stop the underlying thread. A second request can spend part of the 6.75 seconds waiting on the lock, begin worker activity later, and then have the outer route timeout while the thread remains active.
- `research/baird-spike/server.py:488-491` closes uploads and deletes `request_dir` as soon as the route exits, even if the background thread still owns those paths.

The forced-hang evidence proves one dispatched request can kill and replace the OCR child. It does not test two admitted requests, the 200 ms pending contract, outer-await cancellation during lock wait, or artifact ownership after route timeout. `security_control_benchmark.py` exercises controller tokens only. It does not send concurrent valid multipart requests.

This reopens the ownership portion of `BAIRD-RT3-F002`, the resource and timeout portions of `RT1-B-F003` and `RT1-B-F004`, and `RT1-B-RR2-F004`.

**Required remediation**

1. Implement an explicit bounded worker admission primitive with a 200 ms pending deadline.
2. Start each deadline at its selected event and ensure an outer timeout cannot orphan a running thread.
3. Retain paths and capacity until the actual job has completed or the child has been terminated and joined.
4. Add concurrent integration cases for one active request, one 200 ms waiter, a third pre-body rejection, waiter expiry, active-worker hang, client disconnect, cleanup, and successful recovery.

### `RT1-B-RR3-F004` - HIGH - The 64 MiB spool proof counts raw reservations but omits duplicate multipart storage

**Selected architecture claim**

- `docs/baird/ARCHITECTURE_DECISIONS.md:74`, `docs/baird/SECURITY_DATA_FLOW.md:66`, and `docs/baird/ENGINEERING_BLUEPRINT.md:250` calculate two raw envelopes as 50,593,792 bytes and claim that this fits a 64 MiB application spool quota.
- `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:78` marks the global admission and temporary-storage finding closed for V3 rereview.

**Retained runtime and evidence**

- `research/baird-spike/server.py:416-417` receives FastAPI `UploadFile` values. Multipart parsing and Starlette spooling occur before the route body executes. `docs/baird/TECHNICAL_SOURCE_REGISTER.md:73` records this behavior.
- `research/baird-spike/server.py:433-445` then copies every upload into a new request-directory file. A large upload therefore has the multipart spool copy plus the application copy.
- The selected maximum file payload is 24 MiB per request at `server.py:27`, so two near-limit admitted requests can approach roughly 96 MiB of upload file storage before metadata and overhead. The exact peak depends on per-file spool thresholds, but the stated 50,593,792-byte upper bound is not valid for this implementation.
- `research/baird-spike/security_control_benchmark.py:119-137` proves only `2 * RAW_REQUEST_LIMIT <= 64 MiB`. It sends no multipart uploads, measures no temporary storage, and enforces no 64 MiB quota.

This is not merely deferred public proof. The selected architecture arithmetic omits an owned copy and the retained server has no application spool-quota enforcer. It reopens `RT1-B-F003`, `BAIRD-RT3-F001`, and `RT3-V2-F001`.

**Required remediation**

1. Select a one-copy upload ownership design or account for every simultaneous multipart and request-directory copy.
2. Define and enforce an aggregate quota using actual storage ownership, not raw-envelope reservation alone.
3. Test two near-limit multipart requests, baseline and peak disk use, third-request rejection before receive, every error path, disconnect, timeout, and return to baseline.
4. Reconcile the quota with the worker-ownership correction in `RT1-B-RR3-F003`.

### `RT1-B-RR3-F005` - MEDIUM - Asset readiness does not attest the selected regulatory rule set or read-only state

**Selected contract**

- `docs/baird/evidence/MODEL_BOM.md:32-38` requires readiness to fail when a selected file is absent, hash-wrong, or writable by the runtime user.
- `docs/baird/ARCHITECTURE_DECISIONS.md:82` requires a regulatory registry version and digest in the immutable release tuple.
- `docs/baird/UX_PRODUCT_SPEC.md:129` and `docs/baird/ENGINEERING_BLUEPRINT.md:108` say the canonical warning comes from a versioned regulatory registry.

**Retained implementation**

- `research/baird-spike/server.py:58-74` checks hashes for three model files and `selected-check-registry.json`, but checks no read-only or writability property.
- The selected-check registry contains IDs, activation expressions, and aggregation flags only. The prescribed warning text remains a code constant at `research/baird-spike/spike.py:29`, and the 0.5-percent rule remains a code constant at `spike.py:558`.
- The wrong-hash cold probes are valuable, but they do not prove a versioned regulatory rule registry or the required non-writable runtime state.

This partially reopens `RT3-V2-F003`. I2R may translate a selected asset contract into binary requirements, but it should not invent which artifact is the authoritative regulatory rules registry.

**Required remediation**

1. Select and define the regulatory rule artifact that owns canonical warning text, applicability threshold, citations, policy versions, and digest.
2. Include that artifact in readiness and release provenance.
3. Enforce and test absence, wrong hash, wrong version, and writable-by-runtime-user failures for every governed model and rule artifact.

### `RT1-B-RR3-F006` - MEDIUM - Admitted slow uploads have no selected total deadline and the 9.0-second Fly timeout has no owner

- `docs/baird/SECURITY_DATA_FLOW.md:92` names a body/read timeout, but gives no duration, start event, reset semantics, or enforcement owner.
- `docs/baird/SECURITY_DATA_FLOW.md:154` calls 9.0 seconds a Fly request timeout without naming a Fly control that creates a total elapsed request deadline.
- `research/baird-spike/server.py:231-265` counts received bytes but has no total body timer. The 6.75-second application deadline begins only after FastAPI multipart parsing and route validation.

Two admitted clients can therefore drip valid-size body chunks without becoming idle, occupy both admission reservations, and prevent valid work indefinitely. Concurrency and byte caps limit fan-out and size, but not lifetime. Current Fly configuration guidance documents connection idle timeout, which is not a total body deadline when traffic continues.

This reopens the lifetime portion of `BAIRD-RT3-F001`, `RT1-B-F003`, `RT1-B-F004`, and `RT3-V2-F001`.

**Required remediation**

1. Select an exact total body deadline with an unambiguous start event and no activity-based reset.
2. Assign it to a real application or platform control. Name idle timeout separately if used.
3. Define terminal status, cleanup, limiter release, admission release, and safe logging.
4. Prove two continuous slow-drip uploads terminate on schedule, a waiting or later valid request succeeds, and storage and capacity return to baseline.

### `RT1-B-RR3-F007` - MEDIUM - The active Intake assumptions record contradicts the V3 BAIRD evidence

- `docs/intake/assumptions.md:13` still records 42 browser attempts, 3.5805-second warm p95, and 10.28761-second cold p95 for `ASM-007`.
- V3 `docs/baird/BAIRD_TRACEABILITY.md:45` records 54 browser attempts, 3,730.50 ms warm browser p95, 3,802.40 ms direct p95, and 10,845.35 ms cold p95.
- `docs/intake/assumptions.md:18` still records a 25-fixture allocation for `ASM-012`.
- V3 `docs/baird/BAIRD_TRACEABILITY.md:46` and `docs/baird/evidence/FIXTURE_ALLOCATION.md` record 30 fixtures, including 6 holdouts.

The V3 raw evidence supports the BAIRD values. The defect is that the complete Intake and BAIRD handoff expose two current treatments for the exact load-bearing assumptions BAIRD was required to resolve. I2R could cite a stale denominator, timing, or fixture allocation.

This reopens the authoritative-handoff portion of `RT1-B-F001`, `BAIRD-RT3-F008`, and `RT3-RR3`.

**Required remediation**

1. Update the active Intake treatments to the exact V3 evidence or replace volatile numbers with a durable pointer to the sealed BAIRD evidence authority.
2. Preserve cold p95 as NOT CLOSED LOCALLY and preserve deployed warm/restart gates.
3. Preserve the 30-fixture allocation and 6 holdouts while keeping construction and holdout integrity as release gates.

## Retest of prior RT1 findings

| Prior finding | V3 result | Disposition |
|---|---|---|
| `RT1-B-F001` load-bearing assumptions | REOPENED IN PART | Retained feasibility is strong, but active Intake values are stale. See F007. |
| `RT1-B-F002` warning capability and aggregation | REOPENED | A readable punctuation mutation can become exact Match and clean. See F001. |
| `RT1-B-F003` resource envelope | REOPENED | Queue ownership, duplicate spool use, and upload lifetime remain unresolved. See F003, F004, F006. |
| `RT1-B-F004` performance and timeout contracts | REOPENED IN PART | OCR hang ordering passes, but pending-request and upload clocks do not. See F003 and F006. |
| `RT1-B-F005` architecture alternatives and fallbacks | CLOSED | Alternatives, reopen rules, and core fallback boundaries are explicit and evidence-backed. |
| `RT1-B-RR-F001` five-second hard cancellation | CLOSED | Five seconds is a warmed p95 objective, not the hard cancellation. |
| `RT1-B-RR-F002` incomplete result and false-clean claim | REOPENED IN PART | All 17 rows emit, but uncovered warning and country paths can be false clean. |
| `RT1-B-RR-F003` capitalization and punctuation policy | CLOSED FOR BRAND AND PRODUCER | Case and punctuation variants do not auto-Match for those fields. Warning punctuation is separately reopened by F001. |
| `RT1-B-RR-F004` source coverage locators | CLOSED | All 58 sources have complete current R/T ownership in BAIRD. |
| `RT1-B-RR2-F001` proof and warning applicability omitted | CLOSED | Both are active registry rows with independent retained cases. |
| `RT1-B-RR2-F002` uncovered false-clean paths | REOPENED | Warning punctuation and country ambiguity remain uncovered. |
| `RT1-B-RR2-F003` incompatible result vocabulary | CLOSED | One four-state internal contract and three exact summaries are used. |
| `RT1-B-RR2-F004` impossible timeout recovery order | REOPENED IN PART | Single forced hang passes; queued request cancellation can violate true ownership. |
| `RT1-B-RR2-F005` wrong I2R traceability authority | CLOSED | I2R names both source coverage and control handoff authorities. |

## Retest of prior RT2 findings

| Prior finding | V3 result | Disposition |
|---|---|---|
| `RT2-BAIRD-001` unproved performance and quality | CLOSED FOR BAIRD DIRECTION | Warm proof is sufficient for selection; cold and deployed proof remain honest stops. |
| `RT2-BAIRD-002` reference-conditioned candidate selection | CLOSED AS ORIGINALLY STATED | Selection remains reference-blind. F002 is a separate failure to preserve ambiguity. |
| `RT2-BAIRD-003` warning capability unresolved | REOPENED IN EXECUTION | Written policy is complete; executable punctuation repair violates it. |
| `RT2-BAIRD-004` fallback weakens core | CLOSED | Systematic failure reopens BAIRD or requires approved scope change. |
| `RT2-BAIRD-005` ambiguous Try sample | CLOSED | One activation has one defined sample and focus/status path. |
| `RT2-BAIRD-RR-001` warning rows advisory or omitted | REOPENED IN PART | Rows execute and aggregate, but exact-warning state can be false. |
| `RT2-BAIRD-RR-002` cold timing excludes construction | CLOSED BY HONEST DISPOSITION | Five runs include process start, hash checks, construction, warmup, and first result. |
| `RT2-BAIRD-RR-003` biased timeout denominator | CLOSED | All 54 fixed browser attempts remain in the denominator. |
| `RT2-BAIRD-RR2-001` proof and applicability absent from denominator | CLOSED | All 17 registry rows are oracle-checked in retained runs. |
| `RT2-BAIRD-RR2-002` heading exactness | REOPENED AT ADDED-PUNCTUATION EDGE | Missing colon and added word pass their negative cases; added terminal punctuation is repaired. |

## Retest of prior RT3 findings

| Prior finding | V3 result | Disposition |
|---|---|---|
| `BAIRD-RT3-F001` pre-parser upload limit | REOPENED | Admission count is bounded, but spool duplication and total body lifetime are not. |
| `BAIRD-RT3-F002` timeout and disconnect work ownership | REOPENED IN PART | Dispatched forced-hang recovery passes; queued-thread ownership does not. |
| `BAIRD-RT3-F003` portable client identity and origin | CLOSED AT BAIRD LEVEL | Exact Fly identity and Host/Origin rules plus public tests are owned. |
| `BAIRD-RT3-F004` no-runtime-egress overclaim | CLOSED | The package now makes only the bounded port-level claim and discloses TCP 65535. |
| `BAIRD-RT3-F005` model rights and provenance | CLOSED | Exact artifacts, hashes, paths, notices, and build-only fetch are selected. |
| `BAIRD-RT3-F006` hosting metadata and caching | CLOSED AT BAIRD LEVEL | Public notice, data inventory, log allowlist, and no-store tests are owned. |
| `BAIRD-RT3-F007` immutable promotion | CLOSED | Release tuple, digest promotion, readback, evidence, and rollback are explicit. |
| `BAIRD-RT3-F008` executable source/control ownership | REOPENED IN PART | BAIRD coverage is complete, but the active Intake load-bearing treatments are stale. |
| `RT3-RR1` trusted-client identity proof | CLOSED AT BAIRD LEVEL | Spoof, duplicate, malformed, forwarding, limiter, abort, and recovery cases are specified. |
| `RT3-RR2` no-store response proof | CLOSED AT BAIRD LEVEL | Success and named error classes are assigned to public release proof. |
| `RT3-RR3` semantic traceability | REOPENED IN PART | Machine traceability passes, but the active Intake evidence values conflict with V3. |
| `RT3-V2-F001` global upload admission and storage | REOPENED | Two-request admission is present; actual aggregate storage and body lifetime are not bounded. |
| `RT3-V2-F002` field-level correctness and coverage | REOPENED | Retained enumerated cases reconcile, but uncovered warning and country paths can be false clean. |
| `RT3-V2-F003` readiness clock and hashes | REOPENED IN PART | Model and selected-check hashes run before readiness; rule registry and writability do not. |
| `RT3-V2-F004` Fly egress wording | CLOSED | Port-policy semantics and the TCP 65535 limitation are stated consistently. |

## Requirements, scope, and design-reference fidelity that passed

- The primary job remains a standalone proof-of-concept. No COLA integration, legal approval authority, sensitive-data storage, or official TTB identity was introduced.
- The core journey stays single-submission first with 1 to 6 panel images, explicit application values, evidence-first results, human judgment, uncertainty, and no false precision.
- Brand nuance remains Review rather than a naive case-sensitive rejection. Warning checks remain independently visible. Physical type size remains human-only.
- Batch remains a post-core Should objective behind explicit single-submission and capacity gates, preserving the assignment preference for a clean working core.
- Local packaged inference, no runtime model download, one same-origin container, no database, and one always-on Machine fit the blocked-outbound stakeholder evidence and public prototype risk envelope.
- The user-visible latency clock runs from Verify activation through complete rendered and announced results. Server timing is diagnostic only.
- The selected hosting direction, immutable OCI delivery, repository deliverables, README, approach/tools/assumptions documentation, deployed URL, and clean-checkout proof cover the assignment submissions.
- Grok and Gemini proposals remain scenario and layout input only. Their official-looking identity, named staff, legal pass/return authority, generated label errors, confidence theater, unproved batch behavior, and proposed implementation stacks were not promoted into requirements truth.
- Current official TTB and eCFR sources still support the warning applicability and exactness boundaries. Current Fly primary sources still support the selected topology and bounded port-policy claim, subject to the unresolved total-upload deadline and final region/cost deployment stops.

## Advancement condition

Correct F001 through F007 in one governed revision. Regenerate all affected fixtures, oracle rows, direct/browser/security/cold evidence, traceability, remediation, and the sealed manifest. Preserve every V3 strength listed above. Then run all three independent BAIRD reviews against the exact same snapshot.

I2R must not begin from this revision because it would have to invent or repair load-bearing comparison, queue, storage, rule-registry, and upload-lifetime decisions that BAIRD is required to settle.
