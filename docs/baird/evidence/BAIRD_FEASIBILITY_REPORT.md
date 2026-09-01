# BAIRD Feasibility Report

**Run date:** 2026-08-31  
**Evidence status:** Historical I2R research evidence, not current requirements or architecture authority.  
**Current authority:** LV-I2R-001 through LV-I2R-008, `docs/04-i2r-ae/selected-check-registry-v1.json`, and LV-FRD-001.  
**Purpose:** Preserve the early architecture-hypothesis test record produced before the process-stage correction.  
**Result:** Warm architecture path PASS. Runtime controls PASS. Cold path NOT CLOSED LOCALLY. Deployed proof remains a hard stop.

This report describes the exact historical research envelope. Where its 17-check registry, 3.0 second body deadline, Tesseract observations, metrics, or preliminary direction differ from current authority, they are retained only as historical test facts and do not control product implementation or release claims.

## 1. What was tested

The retained research slice exercised the proposed boundaries, not OCR in isolation:

1. synthetic full-panel image creation;
2. image decode, sequential panel normalization, and bounded contact sheet;
3. local OCR with boxes and text;
4. reference-blind candidate location and primary selection;
5. deterministic field comparison, applicability, and aggregation;
6. all 17 selected-check rows and field-level JSON serialization;
7. multipart browser upload through a local FastAPI parent process;
8. one spawned, killable OCR child with request/response IPC;
9. complete result, evidence, coverage, and limitations rendered in Chrome;
10. exact model, selected-check registry, and regulatory-rules registry hashes and versions plus non-writable governed assets before readiness;
11. forced worker timeout, result-free 504, readiness 503, asynchronous child replacement, and recovered complete result;
12. pre-body admission, real-endpoint multipart limits, partial disk-spool timeout, two-copy spool reservation, total upload deadline, client/global start limits, and unauthorized benchmark-header rejection;
13. worker-lock queue deadline, repeated-cancellation supervisor ownership, abort storm, active/waiter shutdown, cleanup, worker replacement, and recovery through the actual ASGI stack;
14. process-spawn timing through readiness and the first complete browser result.

The 37-case architecture slice covers clean, mismatch, and uncertainty outcomes across 1, 2, 3, and 6 panels. It includes a 12 MP source, imported and domestic references, producer exact/case/punctuation/missing/mismatch states, proof match/missing/mismatch/ambiguity, reference-blind ABV decoy selection, warning absence, 0.4/0.5/unparseable applicability boundaries, exact warning punctuation mutations, heading capitalization and colon exactness, altered heading text, independent heading/body weight, continuity, separation, contrast, image quality, duplicate identical country evidence, conflicting country candidates, country absence, unreadability, decoy text, and mismatch. Every result emits every registry row exactly once. Non-applicable rows remain explicit and do not aggregate.

The Grok and Gemini files informed scenario and interaction analysis only. They were not used as expected-outcome truth. The retained source, lock, and raw results are in `research/baird-spike`.

## 2. Exact environment

| Item | Value |
|---|---|
| Host | Windows x64 workstation, Intel Core i9-12900KF |
| CPU constraint | Process affinity limited to logical CPUs 0 and 1 |
| Python | 3.12.10 |
| Dependency resolution | `uv` with hash-pinned `requirements-research.lock` |
| RapidOCR | 3.4.2 |
| ONNX Runtime | 1.22.1, CPU provider selected |
| OCR threads | 2 intra-op, 1 inter-op |
| Browser | Google Chrome stable, headless through Playwright 1.55.0 |
| Browser viewport | 1440 by 1000 |
| OCR working canvas | 0.99 MP for one panel, 3.96 MP for three panels, 5.94 MP for six panels |
| Readiness | Exact selected model hashes, exact selected-check registry hash/version, exact regulatory-rules registry hash/version, non-writable governed assets, model load, and one representative inference |

The three selected model hashes in `architecture-metadata.json` match `MODEL_BOM.md`. The selected-check registry hash is `f1b357c1ebcc261d6b37cf187e44e8501acda31f397d9414101b0cbb8e89adf1`. The regulatory-rules registry hash is `8c7051123f958997781999042efd2d3090f17fa60f39bdf54fee58d811c11c45`. Five separate server starts reported those exact values and non-writable governed assets. This is a measured two-CPU equivalent envelope. It is not evidence about sustained Fly shared-CPU scheduling or public-network latency.

## 3. Field-level oracle

`selected-check-registry.json` is the executable 17-check registry for this historical research slice. It is not the current product scope authority. `regulatory-rules.json` is the research source/value registry. `expected-field-manifest.json` is a separate expected-outcome oracle. It declares applicability, state, exact reason code, and evidence requirement per check and case. Application comparison functions do not supply oracle values.

The 74 direct runs produced 1,258 field rows. Validation failed a run if any field had the wrong applicability, state, reason code, required evidence, registry membership, or aggregate summary.

| Measure | Result |
|---|---:|
| cases | 37 |
| runs | 74 |
| field rows | 1,258 |
| exact field-oracle results | 74 of 74 |
| field validation errors | 0 |
| missing required evidence | 0 |
| false clean | 0 |
| false mismatch | 0 |

## 4. Direct architecture result

| Measure | Result |
|---|---:|
| p50 | 2,712.76 ms |
| p95 | 4,062.84 ms |
| maximum | 4,521.24 ms |
| direct process peak RSS | 1,230,151,680 bytes, 1.15 GiB |

Raw runs are in `rapidocr-server-runs.csv`. Full per-field payloads are in `architecture-details.json`. Environment and model hashes are in `architecture-metadata.json`.

## 5. Browser-visible result

Seventy-four fixed valid attempts covered all 37 cases twice. Every clock started at Verify activation and ended after the complete heading, all 17 rows, limitations, focus target, and live status were rendered across two animation frames. The harness started and stopped its own managed server and retained the startup asset attestation.

| Measure | Result |
|---|---:|
| attempts | 74 |
| complete results | 74 |
| completion rate | 100 percent |
| timeouts | 0 |
| errors | 0 |
| exact field-oracle results | 74 of 74 |
| p50 complete | 2,815.20 ms |
| p95 complete | 4,213.30 ms |
| maximum complete | 4,480.40 ms |
| registry or DOM row omissions | 0 |
| missing required evidence | 0 |
| false clean | 0 |
| false mismatch | 0 |
| maximum OCR-worker peak RSS | 1,244,172,288 bytes, 1.16 GiB |
| response size range | 7,912 to 9,436 bytes |

No attempt was retried out of the denominator. Each response carried `Cache-Control: no-store, private`. The controlled local timing harness used a test-only matching environment secret and header to bypass start-rate accounting while retaining admission controls. A separate negative control proved the header cannot bypass limits when the environment secret is absent. The product release must not configure a public bypass.

Raw attempts are in `browser-runs.json`.

## 6. Timeout and recovery result

A forced child hang exercised the actual browser, API, parent, and worker path:

| Measure | Result |
|---|---:|
| HTTP result | 504 `inference_timeout` |
| user-visible duration | 6,318.53 ms |
| partial field rows | 0 |
| readiness 503 externally observed | Yes |
| worker PID changed | Yes |
| recovered direct child count | 1 |
| next clean verification | 200, all 17 rows |

The failed child was terminated and joined before artifact cleanup. A replacement warmed asynchronously while readiness remained unavailable.

## 7. Admission, upload, and storage controls

`security-control-evidence.json` records executable control probes:

- two clients were admitted and a third was rejected with 503 before any body read;
- the third rejection made zero receive and downstream calls;
- every admission reserved 50,593,792 bytes for two file copies;
- two admissions reserved 101,187,584 bytes inside a 134,217,728-byte, 128 MiB quota;
- two actual near-limit multipart requests, with three files each, reached 100,651,008 visible spool bytes and returned to a zero-byte baseline;
- two admitted slow-drip clients sent chunks every 250 ms and both received 408 near the 3.0 second total deadline;
- the total deadline started at pre-body admission and chunk activity did not reset it;
- a third request during the slow uploads received 503 before body receipt;
- admission and storage reservations returned to zero and a recovery request succeeded;
- 20 client starts were allowed in 10 minutes, then 429;
- 30 global starts were allowed in one minute, then 503;
- an unauthorized benchmark header did not bypass the client limit;
- limiter table cap 4,096 and inactive TTL 900 seconds were configured.

The 3.0 second deadline was application-owned in this historical research harness. It is not the product contract. Current authority sets the non-resetting total request-body deadline to 20 seconds. A Fly connection idle timeout, if configured, is separate and is not represented as a total request-body deadline.

## 8. Worker queue, cancellation, and cleanup controls

`runtime-control-evidence.json` uses the actual FastAPI ASGI stack and real worker process:

| Control | Result |
|---|---|
| one active request plus one admitted waiter | 2 in flight |
| waiter acquisition deadline | 200 ms configured, 219.73 ms observed response |
| waiter result | 503 `worker_queue_busy` |
| third request | 503 in 0.10 ms, zero body receive |
| forced active hang | 504 in 6,281.95 ms |
| timeout worker replacement | Passed |
| first recovery | 200 in 2,507.18 ms, all 17 rows |
| client cancellation | Propagated only after 6,272.28 ms worker termination ownership |
| cancellation worker replacement | Passed |
| final recovery | 200 in 2,622.41 ms, all 17 rows |
| request directories after each sequence | Empty |
| final admission count | 0 |
| final spool reservation | 0 |

This closes the V3 orphaned-work and premature-cleanup concern at the architecture-slice level. Product and deployed tests must reproduce the same ownership property.

## 9. Cold and readiness result

Five separate server processes were spawned before Python imports. Readiness required worker creation, exact runtime asset hashes and versions, read-only governed assets, model load, and representative inference. A clean result was then submitted and rendered in Chrome.

| Measure | Result |
|---|---:|
| runs | 5 |
| complete clean results | 5 of 5 |
| exact runtime hashes and versions | 5 of 5 |
| read-only governed assets | 5 of 5 |
| maximum process spawn to ready | 8,681.95 ms |
| p95 conservative submission wait plus browser-visible result | 11,557.18 ms |
| maximum process spawn to first complete result including page setup | 12,359.71 ms |
| maximum parent plus child peak RSS | 801,607,680 bytes, 0.75 GiB |
| invalid selected-check registry hash blocked readiness | Yes |
| invalid model hash blocked readiness | Yes |
| invalid regulatory-rules hash blocked readiness | Yes |
| missing regulatory-rules registry blocked readiness | Yes |
| wrong regulatory-rules version blocked readiness | Yes |
| writable governed assets blocked readiness | Yes |

`BG-003` is not closed by local evidence because the conservative p95 is 1,557.18 ms above the Intake threshold. The architecture keeps one Fly Machine running and prevents traffic before readiness. Five forced restarts on the deployed immutable image remain a hard release stop. A deployed p95 at or above 10 seconds reopens the architecture decision and blocks release.

Raw runs are in `cold-start-runs.json`.

## 10. Historical OCR candidate exploration

Tesseract.js 6.0.1 was run earlier on ten normalized contact sheets, three times each.

| Candidate | Controlled result-contract evidence retained | Current qualification disposition |
|---|---|---|
| RapidOCR 3.4.2 | Yes. Exact input/output evidence, runtime identities, full pipeline, and browser evidence are retained. | Selected behind the extraction port, subject to all product and deployed gates. |
| Tesseract.js 6.0.1 | No. Exact historical contact sheets and resolved runtime assets were not retained. | Explored but not qualified as primary. Historical field and timing observations are non-decisional. |
| Full PaddleOCR | No product-workload measurement. | Not an automatic fallback. |

The historical Tesseract.js exploration is preserved only as evidence that an alternative was considered. Its exact comparison inputs and resolved runtime assets were not retained, so no field-coverage or timing claim from those runs is reproducible or decisional. Tesseract.js is not qualified as the primary adapter because it lacks a controlled full result-contract proof. Full PaddleOCR is not an automatic fallback because it was not measured on this workload. Failure of the selected adapter reopens the architecture decision or requires requester-approved scope change.

## 11. Historical research conclusions and current overrides

The research supported the modular, local-OCR direction. Current implementation controls are governed only by LV-I2R-001 through LV-I2R-008 and the 19-check product registry. The following current controls supersede preliminary values used by this harness:

- RapidOCR 3.4.2 with the exact detector, recognizer, and orientation classifier in `MODEL_BOM.md`;
- hash-pinned dependencies, exact model hashes, exact selected-check registry hash/version, exact regulatory-rules registry hash/version, and non-writable governed assets;
- sequential bounded source decode and derived OCR views inside the killable supervised child, with original-coordinate evidence mapping;
- one FastAPI parent, one killable OCR child, one OCR job, and at most two pre-body admissions;
- 20 second non-resetting body deadline, 30 second server deadline, and 35 second browser terminal deadline;
- exact 8,650,752 raw request ceiling and two-admission reservation inside a 50,331,648-byte application spool quota;
- 200 ms worker acquisition deadline plus supervisor-owned cancellation and disconnect handling;
- reference-blind extraction and candidate selection;
- expected values introduced only at comparison;
- deterministic 19-check product aggregation with zero false-clean tolerance;
- Fly.io `shared-cpu-2x`, 2 GiB, `iad`, and one Machine kept running;
- an outbound policy allowing TCP 65535 while denying conventional 53, 80, and 443, with no broader no-egress claim;
- deployed warm, cold, cost, policy, cleanup, public-edge, and smoke acceptance before release.

## 12. Gate disposition

| Gate | Historical evidence status | Evidence | Remaining release obligation |
|---|---|---|---|
| `BG-001` selected OCR feasibility | PASS ON HISTORICAL EQUIVALENT ENVELOPE | 74 direct runs, 37 cases, 17 research rows each, zero oracle errors, zero false clean | Execute the product fixture corpus and sealed holdouts against all 19 product checks |
| `BG-002` five-second architecture feasibility | PASS ON EQUIVALENT ENVELOPE | 74 fixed Chrome attempts, 100 percent complete, p95 4.2133 s | Repeat the fixed set on the deployed `iad` URL |
| `BG-003` cold/restart feasibility | NOT CLOSED LOCALLY | Five starts, p95 11.55718 s | One always-running Machine plus five deployed forced restarts below 10 s |
| `BG-004` fixture sufficiency | PASS FOR DESIGN | 30 allocated implementation fixtures, including 6 sealed holdouts | Construct and execute all 30 independently |
| `BG-005` offline dependency and common-port property | PASS FOR ARCHITECTURE DIRECTION | Bundled hashes and versions, read-only assets, six failed readiness probes, no declared external runtime service, selected port policy | Deployment inventory, policy readback, and denied 53/80/443 probes; disclose allowed TCP 65535 |
| `BG-006` request cleanup | PASS FOR ARCHITECTURE DIRECTION | Actual ASGI timeout, cancellation, queue, multipart, cleanup, reservation, worker replacement, and recovery proofs | Repeat every-exit filesystem, multipart spool, disconnect storm, and public-edge tests in the product artifact |
| `BG-007` host resource and cost | PASS FOR ARCHITECTURE DIRECTION | Maximum measured browser worker peak 1.16 GiB; 2 GiB selected | Confirm current `iad` quote and deployed peak |
| `BG-008` batch | DEFERRED BY SCOPE | Core-first gate preserved | Omit unless all core release gates pass first |

## 13. Limits of this evidence

- Synthetic typography is cleaner than many bottle photos.
- Windows CPU affinity is not identical to Fly shared-CPU scheduling.
- Browser timing used loopback networking and a disclosed test-only rate-accounting bypass.
- The local cold path missed the selected threshold and remains open.
- The 30-fixture implementation corpus is allocated but not yet constructed or executed because product implementation has not started.
- Public-edge identity and Fly policy behavior are not local architecture-slice proofs.
- The selected Fly policy is port-level and leaves TCP 65535 allowed.
- Physical warning type size is not automated.

These limits are explicit implementation and release tests. They do not authorize weakening the Intake or silently changing the architecture.
