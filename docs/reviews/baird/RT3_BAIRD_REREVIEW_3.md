REWORK_REQUIRED

# RT3 BAIRD Security, Delivery, and Traceability Rereview 3

Review date: 2026-08-31

## Reviewed sealed snapshot

- Manifest: `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V3.sha256`
- Expected and observed manifest SHA-256: `97707b49f130d37b1fc5303abb3f3fa87502efe23000f8f73089f79aa01277bc`
- Expected and observed entries: 119
- Missing files: 0
- Hash mismatches: 0

The manifest hash and every listed file hash were verified before review. They were verified again after this report was written and immediately before the gate decision was finalized. This report is outside the sealed manifest. No snapshotted file was modified.

## 1. Binary decision

The V3 package materially improves the retained feasibility proof and closes the four V2 findings at the code and evidence level that they were designed to address. In particular, the 17-check registry, separate field oracle, proof and warning-applicability cases, readiness hash enforcement, forced timeout recovery, bounded admission state, and honest Fly port-policy wording are all present and internally consistent.

BAIRD still cannot advance to I2R on this snapshot. Two material delivery defects remain:

1. the public upload design names a body/read timeout and a 9.0-second Fly request timeout without selecting or proving a total request-body deadline that can stop two admitted slow-drip uploads; and
2. the authoritative Intake assumptions register still records superseded BAIRD evidence counts and timings, contradicting the V3 evidence and traceability record for both load-bearing assumptions.

These defects are narrow, but they affect a public availability control and the source-of-truth chain into I2R. CLEAR requires no material unresolved issue.

## 2. Review method

I reviewed the complete sealed Intake and BAIRD package, all prior RT1, RT2, and RT3 reports, the remediation record, source coverage, control handoff, retained research source, model and registry provenance, fixture images, and raw evidence. I also:

1. reran `scripts/validate_baird_traceability.ps1` and confirmed 58 source rows, 12 ADRs, 8 BAIRD gates, 18 threats, `R-001` through `R-096`, `T-001` through `T-096`, 30 fixture IDs, and zero prohibited Unicode dash characters;
2. independently parsed all 54 direct architecture results and recomputed every result against the separate 27-case, 17-row oracle;
3. independently checked all 54 browser attempts, registry and DOM row counts, summaries, error counts, evidence counts, false-clean counts, and false-mismatch counts;
4. traced proof, warning applicability, country evidence, warning heading punctuation, heading emphasis, body weight, producer case/punctuation, panel coverage, and image quality through source, oracle, result, and aggregation;
5. inspected worker startup hashes, bad-hash probes, readiness, forced hang, 504 response, PID change, asynchronous recovery, and one-child evidence;
6. inspected pre-body admission, client/global start buckets, limiter bounds, multipart/spool design, cleanup ownership, Origin/Host, trusted client identity, no-store, logging, container, network, release tuple, and batch boundaries; and
7. rechecked current primary Fly, RapidOCR, TTB, and eCFR sources where the package makes current technical or regulatory claims.

## 3. Independent evidence results

### 3.1 Snapshot and traceability

| Check | Result |
|---|---|
| V3 manifest SHA-256 | PASS |
| All 119 entry hashes | PASS |
| Traceability validator | PASS |
| 58 `SRC` ownership chains | PASS structurally and by sampled semantic review |
| 12 ADR, 8 BG, and 18 THR ownership chains | PASS structurally and by sampled semantic review |
| Required repository, README, documentation, public URL, and deployment provenance chains | PASS as I2R and release obligations |
| Current load-bearing assumption record agrees with V3 | FAIL, finding `RT3-V3-F002` |

### 3.2 Field oracle and browser evidence

| Check | Observed result |
|---|---:|
| Selected registry rows | 17 |
| Oracle cases | 27 |
| Direct architecture runs | 54 |
| Direct field rows | 918 |
| Independently recomputed direct oracle errors | 0 |
| Missing required evidence | 0 |
| False clean | 0 |
| False mismatch | 0 |
| Browser attempts | 54 |
| Complete browser results | 54 |
| Browser registry or DOM omissions | 0 |
| Browser p95 | 3,730.50 ms |

Proof executes independently of ABV. Warning applicability executes below, at, and above the 0.5-percent boundary plus the unparseable path. Country Match retains panel and polygon evidence. The prior S02 false emphasis/body result is gone. Missing colon, altered heading, title case, regular heading, bold body, producer case, producer punctuation, and missing producer all produce their oracle-defined non-clean results.

### 3.3 Runtime and delivery evidence

| Check | Result |
|---|---|
| Exact detector, recognizer, classifier, and registry hashes before readiness | PASS |
| Wrong model hash blocks readiness | PASS |
| Wrong registry hash blocks readiness | PASS |
| Forced worker hang returns result-free 504 | PASS at 6,325.75 ms |
| Readiness becomes 503 during replacement | PASS |
| Worker PID changes and one child recovers | PASS |
| Two POSTs admitted, third rejected before receive | PASS as component evidence |
| 4,096-key cap and 900-second inactive TTL | PASS as selected bounds, release proof retained |
| Actual public slow-upload total deadline | FAIL, finding `RT3-V3-F001` |
| Current local cold path below 10 seconds | NOT CLOSED, honestly retained as deployed stop |
| Fly common-port egress claim matches port semantics | PASS |
| Full public no-store/log/cleanup proof | Correctly retained as implementation and release stop |
| Immutable OCI promotion and release tuple | PASS as an implementation-ready contract |

## 4. Attack cases

| Attack | Required safe behavior | V3 result |
|---|---|---|
| Three clients start verification bodies concurrently | At most two bodies admitted; third rejected before receive | PASS in retained component probe |
| Two admitted clients send one body byte often enough to avoid an idle timeout | Both connections terminate at one selected total deadline and capacity returns | FAIL, no total body clock is selected or owned |
| Client omits or understates `Content-Length` | Actual byte count still stops at the raw cap | PASS by design; implementation test retained |
| Rotating client identities fill limiter state | Key table remains capped and inactive state expires | PASS as selected bounds; public-edge proof retained |
| Client supplies, duplicates, joins, or malforms `Fly-Client-IP` | Exact trusted value only, ambiguous input fails closed | PASS by design and reserved public-edge test |
| Cross-site form or fetch POST | Wrong, missing, or null Origin fails before mutation | PASS by exact decision table and reserved test |
| Label has matching ABV but wrong proof | Proof Mismatch controls the aggregate | PASS in S15 |
| Warning heading lacks the colon | Heading Mismatch controls the aggregate | PASS in S21 |
| Warning applicability is unknown | Applicability Review prevents clean | PASS in S20 |
| Import origin matches | Match carries panel and polygon evidence | PASS in S10 |
| Worker hangs after owning request artifacts | No partial result, true child exit, 504, readiness 503, one replacement | PASS in retained forced-hang result |
| Model or registry hash changes | Process never becomes ready | PASS in two independent bad-hash probes |
| Deployed process sends conventional DNS, HTTP, or HTTPS traffic | Ports 53, 80, and 443 denied; TCP 65535 limitation disclosed | PASS at decision level, deployed proof retained |
| Public success or error is cacheable | `no-store, private` and `no-cache` on all covered classes | PASS at contract level, deployed proof retained |
| Mutable tag or wrong image is promoted | Deployment stops on immutable tuple or readback mismatch | PASS at contract level |
| Batch or ZIP code appears before core clearance | Core gate blocks batch and archive paths | PASS |
| I2R reads the current load-bearing evidence from Intake | Intake and BAIRD must agree on counts and timings | FAIL, finding `RT3-V3-F002` |

## 5. Material findings

### `RT3-V3-F001`: Slow uploads remain unbounded and the 9.0-second Fly request deadline has no enforceable owner

**Severity:** Medium  
**Reopens:** `BAIRD-RT3-F001`, `RT3-V2-F001`, and the timeout portion of `RT1-B-F003` and `RT1-B-F004`  
**Files:** `docs/baird/SECURITY_DATA_FLOW.md:92,124-154`, `docs/baird/ARCHITECTURE_DECISIONS.md:70-74`, `docs/baird/ENGINEERING_BLUEPRINT.md:250-259`, `docs/baird/BAIRD_CONTROL_HANDOFF_MATRIX.md:47`, `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:118-128,198-201`, `research/baird-spike/server.py:231-265,333-368,416-491`

The new process-global gate fixes the V2 fan-out problem: only two verification POSTs enter, each reserves the full raw envelope, and a third is rejected before body consumption. That does not bound the lifetime of either admitted body.

`THR-009` names a body/read timeout, but no document selects its duration, clock start, reset behavior, cancellation mechanism, or relationship to the 7.5-second browser clock. `T-029` says only `client timeout`. The retained server counts bytes but has no total body-read deadline. Its 6.75-second application deadline starts inside the route after multipart parsing, so it cannot stop a slow body. The feasibility report correctly says public-edge slow upload remains unproven.

The package also says `The Fly request timeout is 9.0 s`, but it does not name a Fly configuration field, middleware, or test that creates that total request deadline. Current official Fly configuration documents a connection `idle_timeout` and request concurrency limits. An idle timeout is not a total request-body deadline because a client can continue sending small chunks before the idle interval expires. The selected two-request gate therefore allows two slow-drip clients to hold all verification admission indefinitely while staying below every byte limit.

This is not cured by hard concurrency 4. That setting limits routed concurrent requests, but it does not make the two admitted requests end. It is also not cured by the normal browser abort because a hostile client does not use that browser code.

**Required remediation:**

1. Select an exact total upload/body deadline with an unambiguous start point, preferably admission or first body byte, and make it independent of chunk activity.
2. Assign it to an application or platform control that actually enforces total elapsed time. If Fly `idle_timeout` is also used, name it separately and do not call it a total request timeout.
3. Define status, cleanup, limiter, admission, and logging behavior when the total body deadline fires.
4. Make `R-029/T-029` prove two slow-drip clients, a waiting third client, chunk activity below any idle threshold, bounded open connections and spool bytes, cleanup, and restored capacity.
5. Remove or correct the unsupported `9.0 s Fly request timeout` claim throughout remediation and timing records.

**Closure proof:** Two admitted public-edge clients continuously drip valid-size multipart data. Both terminate at the selected total deadline even though neither is idle. No handler, decoder, or OCR work starts, temporary use returns to baseline, limiter/admission state is released exactly once, and a subsequent valid request succeeds.

### `RT3-V3-F002`: The Intake source of truth records superseded load-bearing BAIRD evidence

**Severity:** Medium  
**Files:** `docs/intake/assumptions.md:13,18,23`, `docs/baird/BAIRD_TRACEABILITY.md:43-49`, `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:55-96,130-146`, `docs/baird/evidence/FIXTURE_ALLOCATION.md:1-39`, `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:31-35,54-62,69-81`

`ASM-007` and `ASM-012` are the two explicitly load-bearing Intake assumptions. Their `Current treatment` cells are no longer current:

- `ASM-007` says 42 fixed browser attempts, p95 3.5805 seconds, and cold p95 10.28761 seconds. V3 records 54 browser attempts, p95 3.7305 seconds, and cold p95 10.84535 seconds.
- `ASM-012` says a 25-fixture allocation. V3 records 30 fixtures with 6 holdouts.

The V3 BAIRD traceability file has the correct values, and the raw evidence supports those values. The problem is not the V3 evidence. The problem is that the sealed, supposedly complete Intake and the BAIRD handoff disagree about the current disposition of the exact assumptions BAIRD exists to resolve.

This is material source drift. An I2R author following the complete Intake can cite the wrong benchmark denominator, timings, fixture count, and cold miss. It also prevents a reviewer from identifying one authoritative current record without knowing the package history.

**Required remediation:**

1. Update the `Current treatment` for `ASM-007` and `ASM-012` to the exact V3 evidence, or replace volatile numbers with a clear pointer to the versioned BAIRD evidence authority.
2. Preserve the cold result as NOT CLOSED LOCALLY and the deployed restart stop. Do not turn it into a pass.
3. Preserve the 30-fixture allocation and 6 holdouts as design evidence, with construction and holdout integrity still pending release proof.
4. Rerun the traceability and Unicode gates and seal one corrected snapshot for all three reviewers.

**Closure proof:** A repository-wide search finds one current set of BAIRD evidence values, with any older values explicitly labeled historical and excluded from the active handoff.

## 6. Retest of prior RT1 findings

| Prior finding | V3 result | Evidence and disposition |
|---|---|---|
| `RT1-B-F001` load-bearing assumptions | REOPENED FOR TRACEABILITY | The V3 evidence is strong, but Intake still records superseded closure values. See `RT3-V3-F002`. |
| `RT1-B-F002` warning capability and aggregation | CLOSED | All active warning rows have explicit prerequisites, states, aggregation, registry rows, oracle branches, and retained results. |
| `RT1-B-F003` resource envelope | REOPENED IN PART | Bytes, pixels, memory, spool reservation, rate, and concurrency are selected. Total body lifetime is not. See `RT3-V3-F001`. |
| `RT1-B-F004` performance and timeout contract | REOPENED IN PART | Browser, app, child, and recovery clocks are otherwise correct. The 9.0-second Fly claim and unbounded body clock remain. |
| `RT1-B-F005` option comparison and fallback | CLOSED | Evidence classes, selected adapter, rejected options, host choice, and reopen rules are explicit. |
| `RT1-B-RR-F001` five-second browser cancellation | CLOSED | Five seconds is only p95. The 7.5-second browser safety bound is separate. |
| `RT1-B-RR-F002` incomplete retained result | CLOSED | All 17 rows are emitted and independently oracle-checked in direct and browser paths. |
| `RT1-B-RR-F003` brand capitalization and punctuation | CLOSED | Case-only and punctuation-only paths produce Review. |
| `RT1-B-RR-F004` source-coverage locators | CLOSED | All 58 source rows have named controls, R/T pairs, components, gates, and owners. |
| `RT1-B-RR2-F001` omitted proof/applicability | CLOSED | Proof and warning applicability are versioned active rows with independent cases. |
| `RT1-B-RR2-F002` uncovered false-clean rules | CLOSED | Heading colon/alteration and producer exact/case/punctuation/missing/mismatch branches are covered. |
| `RT1-B-RR2-F003` incompatible result contracts | CLOSED | One four-state internal contract and three exact summaries are used. |
| `RT1-B-RR2-F004` impossible timeout recovery order | CLOSED FOR OCR WORK | The forced hang returns before 6.75 seconds and rewarms asynchronously. The request-body clock is a separate reopened issue. |
| `RT1-B-RR2-F005` wrong I2R traceability authority | CLOSED | I2R names both `SOURCE_COVERAGE.csv` and `BAIRD_CONTROL_HANDOFF_MATRIX.md` correctly. |

## 7. Retest of prior RT2 findings

| Prior finding | V3 result | Evidence and disposition |
|---|---|---|
| `RT2-BAIRD-001` unproven performance and quality | CLOSED FOR ARCHITECTURE DIRECTION | 54 direct and 54 browser runs pass the complete field oracle; deployed warm and cold gates remain honest stops. |
| `RT2-BAIRD-002` reference leakage into extraction | CLOSED | Candidate generation and primary selection remain reference-blind, with decoy cases and release mutation tests. |
| `RT2-BAIRD-003` incomplete warning matrix | CLOSED | One matrix, one registry, independent rows, and deterministic aggregation agree. |
| `RT2-BAIRD-004` weak field-family gate | CLOSED | The 30-fixture allocation preserves family minimums, zero false clean, and BAIRD reopen behavior. |
| `RT2-BAIRD-005` ambiguous Try sample | CLOSED | One activation loads and verifies a complete synthetic case with focus/status behavior. |
| `RT2-BAIRD-RR-001` advisory warning rows | CLOSED | Every applicable active row executes and aggregates. |
| `RT2-BAIRD-RR-002` unmeasured cold path | CLOSED BY HONEST DISPOSITION | Five process starts include hashes and warmup; p95 10.84535 seconds remains a failed local hypothesis and deployed stop. |
| `RT2-BAIRD-RR-003` biased fixed denominator | CLOSED | All 54 attempts remain in one fixed denominator with no retry removal. |
| `RT2-BAIRD-RR2-001` omitted proof and applicability | CLOSED | Both are present in registry, source, oracle, direct results, and browser results. |
| `RT2-BAIRD-RR2-002` warning heading exactness | CLOSED | Missing colon and altered heading are distinct Mismatch branches with evidence. |

## 8. Retest of prior RT3 findings

| Prior finding | V3 result | Evidence and disposition |
|---|---|---|
| `BAIRD-RT3-F001` pre-parser upload limits | REOPENED IN PART | Global pre-body admission and byte/spool reservations are fixed. Total admitted-body lifetime is not. See `RT3-V3-F001`. |
| `BAIRD-RT3-F002` killable work ownership | CLOSED | Child ownership, true exit, result-free timeout, readiness, and one-child recovery are explicit and exercised. |
| `BAIRD-RT3-F003` client identity and Origin/Host | CLOSED AT BAIRD LEVEL | Exact Fly identity and Origin/Host tables plus public-edge tests are owned. |
| `BAIRD-RT3-F004` Fly egress semantics | CLOSED | Only TCP 65535 is allowed, 53/80/443 denial is the bounded claim, and arbitrary 65535 traffic is disclosed. |
| `BAIRD-RT3-F005` model rights and provenance | CLOSED | Exact three-file lineage, hashes, sizes, paths, notices, build-only fetch, and stop-on-change rule agree with current primary sources. |
| `BAIRD-RT3-F006` platform metadata and no-store | CLOSED AT BAIRD LEVEL | Data inventory, public copy, log allowlist, cache headers, and public response-class proof are assigned. |
| `BAIRD-RT3-F007` immutable OCI promotion | CLOSED | Complete source/build/model/rule/fixture/deployment/readback/rollback tuple is required. |
| `BAIRD-RT3-F008` source/control ownership | CLOSED | All 58 SRC and 38 ADR/BG/THR controls have complete I2R ownership chains. |
| `RT3-RR1` trusted client identity proof | CLOSED AT BAIRD LEVEL | Spoof, duplicate, malformed, forwarding, limiter, burst, abort, and recovery cases are explicit. |
| `RT3-RR2` no-store proof | CLOSED AT BAIRD LEVEL | Public success and all named error classes are covered by `R-030/T-030`. |
| `RT3-RR3` semantic source and finding traceability | CLOSED | The validator passes and current finding citations are semantically aligned. |
| `RT3-V2-F001` global admission and temp storage | REOPENED IN PART | Fan-out, reservation, rate, and key bounds are fixed. Slow-drip lifetime is still open. |
| `RT3-V2-F002` incomplete field correctness evidence | CLOSED | Separate 27-case oracle covers all 17 rows, exact reasons, applicability, evidence, and summaries. |
| `RT3-V2-F003` readiness omitted claimed hashes | CLOSED | Runtime readiness verifies exact model and registry hashes; bad hashes block readiness. |
| `RT3-V2-F004` Fly egress overclaim | CLOSED | Port-only semantics and the TCP 65535 limitation are consistently disclosed. |

## 9. Current primary-source verification

- [Fly app configuration](https://fly.io/docs/reference/configuration/) supports request concurrency soft and hard limits and documents connection `idle_timeout`. The BAIRD hard-4 concurrency decision is supported. That source does not, as cited in this package, establish the claimed 9.0-second total request deadline.
- [Fly network policies](https://fly.io/docs/machines/guides-examples/network-policies/) confirms directional port/protocol allowlists and default deny after a rule exists. The narrowed 53/80/443 denial plus TCP 65535 disclosure is accurate.
- [Fly request headers](https://fly.io/docs/networking/request-headers/) confirms `Fly-Client-IP` is the client address from Fly Proxy's perspective. The no-additional-proxy trust decision is coherent.
- [Fly CPU performance](https://fly.io/docs/machines/cpu-performance/) confirms shared CPUs burst but have a lower baseline quota than performance CPUs. The package correctly treats local two-CPU affinity as an equivalent architecture probe, not deployed performance proof.
- [RapidOCR 3.4.2 default models](https://raw.githubusercontent.com/RapidAI/RapidOCR/v3.4.2/python/rapidocr/default_models.yaml) lists the exact detector, recognizer, classifier URLs and hashes in `MODEL_BOM.md`.
- [TTB distilled-spirits health warning](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) currently supports the 0.5-percent threshold, prescribed warning, uppercase/bold heading, non-bold remainder, continuity, separation, contrast, and size limitation.
- [27 CFR 5.63](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-5/subpart-E/section-5.63) remains consistent with the selected distilled-spirits field subset and the package's non-comprehensive authority wording.

## 10. Confirmed controls that should not regress

- same-origin modular monolith with no COLA integration;
- local RapidOCR inference with exact versioned model artifacts and no runtime download;
- reference-blind candidates and deterministic comparison;
- 17 explicit rows, including proof and warning applicability;
- fail-closed aggregation and zero false-clean release tolerance;
- one killable OCR child with true-exit ownership and asynchronous replacement;
- exact public identity, Host, Origin, rate, concurrency, and bounded limiter decisions;
- no database, no persistent volume, no raw-content logging, and truthful public notice;
- response no-store requirements across success and error classes;
- honest Fly port-level egress claim with TCP 65535 disclosed;
- immutable OCI digest promotion and complete release provenance;
- 30-fixture allocation with 6 holdouts and anti-hard-coding requirements;
- batch held behind all core release gates;
- repository, all source, README, brief documentation, public URL, clean-checkout, and same-revision deployment deliverables.

## 11. Gate requirements

RT3 can return CLEAR only on a new sealed snapshot that:

1. selects and owns an exact total upload/body deadline that slow chunk activity cannot extend;
2. removes or correctly implements and names the 9.0-second Fly request claim;
3. extends `R-029/T-029` with a measurable public slow-drip proof and cleanup/recovery evidence contract;
4. synchronizes `ASM-007` and `ASM-012` with the current V3 evidence authority;
5. preserves every confirmed V3 field, runtime, security, provenance, and traceability closure;
6. passes the snapshot hash, traceability, evidence-integrity, link, and Unicode gates; and
7. receives CLEAR from all three independent reviewers on the identical corrected snapshot.

Until then, BAIRD remains open and I2R must not begin.
