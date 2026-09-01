# BAIRD Evidence Validation

**Validation date:** 2026-08-31  
**Scope:** Retained architecture, browser, timeout/recovery, cold-start, upload/storage, queue/cancellation, environment, and fixture evidence

## Binary checks

| Check | Result |
|---|---|
| Python source parses | PASS, 7 retained research files |
| JSON evidence parses | PASS |
| Selected-check registry | PASS, 17 unique checks |
| Regulatory-rules registry | PASS, exact source/value version and hash used by runtime |
| Independent field oracle | PASS, all 37 cases define every registry check through base plus overrides |
| Direct architecture runs | PASS, 74 of 74 exact field-oracle results |
| Field validation errors | PASS, 0 |
| Required evidence omissions | PASS, 0 |
| False clean | PASS, 0 |
| False mismatch | PASS, 0 |
| Browser attempts | PASS, 74 of 74 complete |
| Browser timeouts/errors | PASS, 0 timeouts and 0 errors in the fixed valid set |
| Browser field rendering | PASS, 17 registry rows in response and DOM on every attempt |
| Browser cache header | PASS, every retained success is `no-store, private` |
| Forced timeout/recovery | PASS, result-free 504, readiness 503, PID change, one child, recovered complete result |
| Startup assets | PASS, exact model and both registry hashes and versions plus non-writable state on 5 of 5 starts |
| Fail-closed readiness probes | PASS, wrong model hash, wrong check-registry hash, wrong rules hash, missing rules, wrong rules version, and writable assets all blocked readiness |
| Admission and rate controls | PASS, pre-body third-client rejection and exact client/global limit probes |
| Total upload deadline | PASS, two 250 ms slow-drip clients received 408 near 3.0 seconds with no clock reset, third rejected pre-body, counters zero, recovery succeeded |
| Multipart spool accounting | PASS, two actual near-limit multipart flows stayed within two-copy reservation and 128 MiB quota, then returned to zero bytes |
| Worker queue | PASS, 200 ms acquisition bound and 503 `worker_queue_busy` |
| Cancellation ownership | PASS, cancellation propagated only after worker termination, replacement, cleanup, zero reservations, and complete recovery |
| Cold evidence | PASS as measurement, NOT CLOSED as target |
| Traceability validator | PASS on the reconciled V4 package |
| Unicode dash scan | PASS, zero U+2010 through U+2015 characters |
| Placeholder scan | PASS, no unfinished-work markers |

## Metric readback

```text
SELECTED_CHECKS=17
ARCHITECTURE_CASES=37
ARCHITECTURE_RUNS=74
ARCHITECTURE_FIELD_ROWS=1258
ARCHITECTURE_FIELD_ERRORS=0
ARCHITECTURE_MISSING_EVIDENCE=0
ARCHITECTURE_FALSE_CLEAN=0
ARCHITECTURE_FALSE_MISMATCH=0
ARCHITECTURE_P50_MS=2712.76
ARCHITECTURE_P95_MS=4062.84
ARCHITECTURE_MAX_MS=4521.24
BROWSER_ATTEMPTS=74
BROWSER_COMPLETE=74
BROWSER_TIMEOUTS=0
BROWSER_ERRORS=0
BROWSER_FIELD_ERRORS=0
BROWSER_MISSING_EVIDENCE=0
BROWSER_FALSE_CLEAN=0
BROWSER_FALSE_MISMATCH=0
BROWSER_P50_MS=2815.20
BROWSER_P95_MS=4213.30
BROWSER_MAX_MS=4480.40
FORCED_TIMEOUT_VISIBLE_MS=6318.53
FORCED_TIMEOUT_RECOVERY=PASS
UPLOAD_TOTAL_DEADLINE_SECONDS=3.0
UPLOAD_CLOCK_START=PRE_BODY_ADMISSION
UPLOAD_ACTIVITY_RESETS_CLOCK=FALSE
SPOOL_RESERVATION_PER_REQUEST_BYTES=50593792
SPOOL_TWO_REQUEST_RESERVATION_BYTES=101187584
SPOOL_QUOTA_BYTES=134217728
SPOOL_ACTUAL_MULTIPART_PEAK_BYTES=100651008
WORKER_QUEUE_DEADLINE_MS=200
RUNTIME_CONTROL_RECOVERY=PASS
COLD_RUNS=5
COLD_CONSERVATIVE_P95_MS=11557.18
INVALID_CHECK_REGISTRY_HASH_BLOCKS_READY=TRUE
INVALID_MODEL_HASH_BLOCKS_READY=TRUE
INVALID_RULES_HASH_BLOCKS_READY=TRUE
MISSING_RULES_BLOCKS_READY=TRUE
WRONG_RULES_VERSION_BLOCKS_READY=TRUE
WRITABLE_ASSETS_BLOCK_READY=TRUE
COLD_LOCAL_STATUS=NOT_CLOSED
```

## Retained evidence hashes

```text
e6d0a9efa00619f763b7c8903bf740fc25db5c243f6fdd846b410460830979a6  docs/baird/evidence/rapidocr-server-runs.csv
89fad8544268dfc8301289fade7069844bf1fda7fca2d81a772596d7b285d65b  docs/baird/evidence/browser-runs.json
29450560b0e64f61127db89f189bb7ba5e54b514bba9817e32a2033b2ae8b64d  docs/baird/evidence/cold-start-runs.json
281db2394810d79a05d2051988e18482bacd73361196b280e88e7d75f719b617  docs/baird/evidence/architecture-details.json
313ef5e779bb45a7519ff371975bef17bc7d725ca31c30d74cb1e81269ee9d61  docs/baird/evidence/architecture-metadata.json
aacc1e75829c4c150d7e968c574ce80a7c99339d2a9dd89f7e8a12838d594dde  docs/baird/evidence/architecture-fixture-manifest.json
92208a8d400ba07e57a63f345f8054b32cbf61d7ff6da493a675951cf42e267b  docs/baird/evidence/security-control-evidence.json
0e05b8a5123ea7c470dd9e4719cfeaad68e11de0ff65042390cef81026ba68b9  docs/baird/evidence/runtime-control-evidence.json
c25fdfc112df0d69827a822674a6791bef188294cab6ccfd73107351a901e4e5  docs/baird/evidence/expected-field-manifest.json
f1b357c1ebcc261d6b37cf187e44e8501acda31f397d9414101b0cbb8e89adf1  docs/baird/evidence/selected-check-registry.json
8c7051123f958997781999042efd2d3090f17fa60f39bdf54fee58d811c11c45  docs/baird/evidence/regulatory-rules.json
028a868eb104fd50942831aa575d3ee0448f88f3c947349b6053af3c8050f462  research/baird-spike/requirements-research.lock
```

## Interpretation

The warm local evidence supports the selected implementation direction and directly remediates the V3 warning-punctuation, conflicting-country, worker-ownership, two-copy storage, readiness-asset, and total-upload-deadline findings. It does not substitute for deployed Fly performance, public-edge identity, policy readback, cost, or restart evidence. The local cold measurement missed the Intake limit and is intentionally retained as an open gate. Release remains blocked unless the always-running deployed topology passes `BG-003`.
