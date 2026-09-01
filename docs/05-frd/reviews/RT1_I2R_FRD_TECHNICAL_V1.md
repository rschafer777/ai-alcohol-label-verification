REWORK_REQUIRED

# RT1 I2R A&E and FRD Technical Review V1

Review date: 2026-08-31

Role: Independent architecture, engineering, and feature-requirements reviewer

## Sealed snapshot verification

- Manifest: `docs/05-frd/I2R_FRD_SNAPSHOT_V1.sha256`
- Expected and observed manifest SHA-256: `d2203fcfc94fd469d2855f50d9af291780014c751ce7dcaf8c51f1144b6f81c4`
- Expected and observed entries: 32
- Missing entries: 0
- Hash mismatches: 0
- Answered BAIRD questions: 14 unique rows from `BQ-001` through `BQ-014`
- Feature requirements: 36 unique rows from `FR-001` through `FR-036`
- Test identifiers: 36 unique references from `T-001` through `T-036`
- BAIRD identifiers referenced by FRD: 31 of 31
- Prohibited characters U+2010 through U+2015 in sealed files: 0

The selected modular-monolith architecture is proportionate to the take-home. The warm local evidence, worker-lifecycle probes, upload-control probes, independent field oracle, false-clean controls, and all-check registry materially support the direction. The cold-start miss is reported honestly as an unresolved release gate. The following material findings remain.

## Material findings

### `RT1-I2R-F001` - HIGH - The accepted upload envelope and fixed body deadline are not jointly feasible under a declared public network envelope

The interface accepts 8 MiB per file and 24 MiB aggregate at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:15-16`, while the total request body has a non-resetting 3.0 second deadline at line 133. A near-limit request therefore needs more than 8 MiB per second, about 67 megabits per second of sustained upstream throughput, before network and multipart overhead.

The raw evidence does not close that feasibility gap:

- the 74 OCR benchmark rows in `docs/baird/evidence/rapidocr-server-runs.csv` contain at most 424,016 input bytes, far below the 24 MiB accepted envelope;
- the 23,053,216 byte full-stack spool probes in `docs/baird/evidence/security-control-evidence.json:237-270` completed in about 300 ms on the local harness;
- `research/baird-spike/security_control_benchmark.py:370-406` replaces real OCR with a held fake worker for that near-limit probe;
- no deployed or shaped-network test proves that a valid near-limit public upload can meet the selected deadline and then complete or fail for a reason other than ordinary uplink speed.

This is material because the product can advertise an input as valid while predictably rejecting it for many normal evaluator connections. `FR-008` tests that the timeout fires and cleans up, but it does not prove that the selected valid envelope is usable.

Required remediation:

1. Define the supported client-uplink and evaluator-region envelope, or revise the byte limits and upload deadline so the contract is internally attainable.
2. Add shaped-network and deployed tests at representative one-panel, multi-panel, and near-limit sizes.
3. Keep abuse protection non-resetting and bounded, but do not treat a loopback spool test as public upload feasibility evidence.

### `RT1-I2R-F002` - HIGH - Public client identity and cross-origin controls have no trusted-proxy contract or FRD test

The design relies on a per-client active-request and rate policy at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:136`, records only a non-reversible client digest at line 125, and claims strict Host/Origin enforcement at line 170. The selected host is Fly.io, so the application sits behind a public proxy.

The sealed architecture never defines which proxy-supplied client identity is trusted, how the immediate peer is validated, whether Uvicorn proxy-header handling is enabled, what happens when the header is absent or malformed, or how spoofed forwarding headers are rejected. The retained harness derives identity directly from ASGI `scope.client` at `research/baird-spike/server.py:510-512`, which does not prove the Fly deployment path. The FRD has no requirement or test for trusted proxy identity, Host validation, Origin validation, or the stated secure headers. `FR-008` covers numeric limits and `FR-029` covers logs and cleanup, but neither covers this boundary.

This is material because all public users can collapse to the proxy peer and share the one-active-request limit, or an incorrectly trusted forwarding header can make the limiter spoofable. The documented cross-origin control can also be omitted while all 36 current feature tests pass.

Required remediation:

1. Define the exact trusted client-identity chain for the selected host, including trusted peers, accepted header, fallback behavior, and privacy-safe digesting.
2. Add spoofed, duplicate, malformed, missing, and direct-client identity tests.
3. Add an FR and test for allowed Host/Origin behavior and the selected response security headers on all relevant UI, API, and error paths.

### `RT1-I2R-F003` - HIGH - BR-to-FR coverage is identifier-complete but drops two mandatory acceptance outcomes

The FRD references every `BR-NNN`, but two BAIRD outcomes can still be violated while every current FR passes:

1. `BR-022` requires rule source, retrieval date, version, and release re-verification at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:102`. `FR-019` and `FR-020` test warning behavior, and `FR-028` tests registry hash readiness, but no FR or `T-NNN` requires checking the governing TTB/eCFR sources again at release or recording that evidence. A hash proves internal immutability, not regulatory currency.
2. `BR-016` prohibits persistence of uploads, extracted text, and reference values at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:96`. The UX specification correctly prohibits local storage, IndexedDB, service-worker content caching, and analytics storage, but `FR-026` tests refresh loss only for reviewer notes, `FR-027` tests Start over, and `FR-029` tests server cleanup and logs. No FR test proves that the form, files, extracted result, and evidence are absent from browser persistence and caches after refresh or close.

This is material because the FRD declares exact, test-backed implementation requirements. A stale regulatory registry or browser-persisted label content would violate approved BAIRD requirements without failing the current FRD.

Required remediation:

1. Add a release-source re-verification feature/test that records authority URL, retrieval date, rule version, reviewed change result, and release stop behavior.
2. Add browser storage and cache inspection across verification, refresh, close/reopen, Start over, success, and failure paths.
3. Update the BR-to-FR trace so these acceptance outcomes map to the new tests, not only to component-level assertions.

### `RT1-I2R-F004` - MEDIUM - The sealed OCR selection lacks its required comparative evidence

`BQ-001` requires a candidate comparison, license and egress review, benchmark, and adapter contract at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:134`. The snapshot contains strong RapidOCR benchmark and asset evidence, but its only comparative conclusion says Tesseract.js failed field coverage and cites `BAIRD_FEASIBILITY_REPORT.md` at `docs/baird/evidence/MODEL_BOM.md:43`. That report is not one of the 32 sealed entries. No retained raw result in this snapshot shows the alternative's inputs, field coverage, timing, environment, or failure criteria.

This is material to the architecture gate because the selected OCR is the dominant latency, memory, startup, licensing, and deployment decision. A statement that an alternative failed is not independently reviewable when its cited evidence is outside the controlled package.

Required remediation:

1. Add the controlled candidate-comparison record and raw results to the next sealed snapshot, including environment, fixture subset, field coverage, latency, memory, egress, licensing, and decision thresholds.
2. If the old report is not reliable under the corrected process, rerun a bounded comparison and record it as I2R evidence.
3. Keep the adapter boundary and fallback stop gate so development evidence can replace the OCR choice without redesigning the product contract.

## Gate decision

The architecture and FRD are close, and the cold-start gap is handled honestly. The four findings above affect valid-input usability, public runtime controls, mandatory BAIRD acceptance, and independent support for the central OCR choice. They must be corrected and the combined I2R A&E and FRD package resealed before Build Instructions advance.
