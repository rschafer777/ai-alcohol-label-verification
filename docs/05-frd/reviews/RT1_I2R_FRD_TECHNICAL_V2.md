REWORK_REQUIRED

# RT1 I2R and FRD Technical Review V2

Reviewed snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V2.sha256`  
Expected and observed manifest SHA-256: `5d2fe2e62c5052bbb10f1e263946383c2674546e108dbdbb605586ba3c34c938`  
Manifest entries: 44  
Hash verification: 44 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015 scan: 0 findings

## Material findings

### RT1-I2R-FRD-V2-F001 - HIGH - The active upload deadline still has two normative values

LV-I2R-002 selects a non-resetting 20.0 second request-body deadline at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:157`, nests that value inside the 30 second server deadline at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:191-196`, and carries it into `FR-008`, `FR-031`, and `FR-041` at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:30`, `:53`, and `:63`. The same active security specification still requires a non-resetting 3 second total body deadline in the slow-request threat control at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:208`.

This is not a legacy-evidence conflict. Both values are in the current normative I2R security contract. A correct implementation of one value necessarily violates the other, so `T-008`, `T-031`, and `T-041` do not have one oracle. This leaves the prior upload and network feasibility finding open despite the otherwise coherent reduced 8 MiB payload, exact 8,650,752-byte raw ceiling, and 20/30/35 second composition.

Required remediation:

1. Replace the stale 3 second value with the selected 20 second value everywhere in the active I2R and FRD package.
2. Re-run the exact-ceiling, slow-drip, shaped-network, and composed-deadline consistency checks against one normative value.

### RT1-I2R-FRD-V2-F002 - HIGH - The validation and decode deadline is specified but not technically enforceable from the selected ownership model

LV-I2R-002 requires validation and decode to finish within 2.0 seconds or return `request_deadline_exceeded` at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:193`. It also requires controlled validation/decode stalls to reach a bounded terminal state at `:201`, and `FR-041` requires safe ownership and zero cleanup after that stall at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:63`.

The architecture defines only the OCR child as killable at `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:22`, assigns worker ownership after the controlled request reaches the worker at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:141`, and leaves decoded arrays in unspecified process or child memory at `:142`. It never decides whether decode runs inside the supervised child, another killable process, or a non-killable parent thread. A timeout around a blocking Pillow or OpenCV call does not terminate that work. The server could emit a 504 while decode still holds files, memory, or execution capacity, contradicting the cleanup and cancellation contract.

This is a load-bearing architecture gap, not a BI coding detail. The selected 30 second server deadline cannot be proven for adversarial or stalled decode until execution and termination ownership are explicit.

Required remediation:

1. Place full decode and preprocessing inside a named killable ownership boundary, or define an equally enforceable bounded mechanism.
2. Define when the 2.0 second clock starts, which supervisor owns files and capacity, and when cleanup may occur after timeout, disconnect, cancellation, and shutdown.
3. Extend `T-029` and `T-041` to force a real decoder stall and prove process or task termination, response behavior, recovery, and zero final handles, directories, reservations, and capacity.

### RT1-I2R-FRD-V2-F003 - HIGH - The sealed OCR candidate comparison is not a controlled, auditable comparison

LV-I2R-008 calls the Tesseract evidence ten normalized contact sheets at `docs/04-i2r-ae/08_I2R_OCR_CANDIDATE_COMPARISON.md:18` and uses their field misses to reject that candidate at `:20-25` and `:38`. The sealed benchmark script reads `research/baird-spike/sheets` at `research/baird-spike/tesseract_benchmark.mjs:8-17`, but the 44-entry snapshot contains no sheet, sheet hash manifest, or generator that writes that directory. The script cannot reproduce the sealed run from the sealed evidence. The seal also omits the Node lockfile and any Tesseract worker, core, or language-data identity, while the script uses default `createWorker('eng')` resolution at `research/baird-spike/tesseract_benchmark.mjs:11`.

The supporting legacy report is also not tied to the same raw run set. It reports RapidOCR direct p95 4,062.84 ms and browser p95 4,213.30 ms at `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:70` and `:89`, while the sealed CSV and browser JSON recompute to 3,994.82 ms and 3,963.00 ms, the values used in LV-I2R-001 at `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:154-155`. Its cold p95 11,557.18 ms at `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:171` also conflicts with the sealed `cold-start-runs.json` value 10,949.98 ms used at `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:159`.

RapidOCR remains a plausible selection, and the cold-start gap is honestly kept open. However, prior finding `RT1-I2R-F004` is not closed by a comparison whose exact inputs and dependency assets are absent and whose supporting report describes a different run set.

Required remediation:

1. Seal the exact common comparison inputs or a deterministic generator plus input hashes, the Node lockfile, and the Tesseract core, worker, and language-data identities and licenses.
2. Tie both candidate outputs to the same case and input hashes, record preprocessing and configuration per candidate, and preserve field-level output sufficient to verify each claimed miss.
3. Regenerate or explicitly supersede the stale feasibility report so every cited metric names one immutable run set.

## Prior-finding disposition

- `RT1-I2R-F001`: Partially remediated. The reduced envelope and shaped-network profile are coherent, but finding F001 above leaves the active deadline contradictory.
- `RT1-I2R-F002`: Closed. Fly client identity, direct-mode isolation, Host, Origin, response headers, no-store behavior, and a binary test matrix are now specified in LV-I2R-002 Section 10 and `FR-040`.
- `RT1-I2R-F003`: Closed. `FR-038` provides regulatory release re-verification and `FR-039` provides browser storage and cache inspection across terminal paths.
- `RT1-I2R-F004`: Open. Finding F003 above prevents the sealed comparison from being independently audited as the controlled evidence claimed.

## Gate decision

The 41 FR/T pairs, 19-check product registry, evidence reference contract, public error registry, raw request arithmetic, cold-start disclosure, BAIRD coverage, and architecture proportionality are otherwise sound. I2R and FRD cannot advance to BI until the three findings above are corrected, the package is resealed, and the independent review is rerun on that exact revision.
