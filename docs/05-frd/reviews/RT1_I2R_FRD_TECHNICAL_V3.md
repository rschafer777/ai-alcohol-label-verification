REWORK_REQUIRED

# RT1 I2R and FRD Technical Review V3

Reviewed snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V3.sha256`  
Expected and observed manifest SHA-256: `d86756843c9414978ad2e7cf995be72e4abbbf7b1ba2e2d4a416810a52155722`  
Manifest entries: 50  
Hash verification: 50 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015 scan: 0 findings

## Material finding

### RT1-I2R-FRD-V3-F001 - HIGH - The controlled model BOM still rejects Tesseract using the evidence that V3 declares non-decisional

LV-I2R-008 correctly states that the unsealed historical Tesseract contact sheets and runtime assets make its field-miss and timing claims non-decisional at `docs/04-i2r-ae/08_I2R_OCR_CANDIDATE_COMPARISON.md:39`. It further says Tesseract is not rejected on the unsupported field-miss claim and selects RapidOCR only because RapidOCR is the sole candidate with controlled positive full-contract evidence at `:44`.

However, the same document lists `docs/baird/evidence/MODEL_BOM.md` as controlled decision evidence at `docs/04-i2r-ae/08_I2R_OCR_CANDIDATE_COMPARISON.md:30-36`. That BOM still says Tesseract failed the required field-coverage comparison in the superseded feasibility report and uses that failure to dispose of it as the primary adapter at `docs/baird/evidence/MODEL_BOM.md:41-43`.

These are incompatible selection rationales inside the same sealed authority chain. The unsupported historical field-miss claim remains decisional in a document V3 explicitly retains as controlled evidence. This leaves the V2 OCR-evidence finding partially open and allows BI or delivery documentation to repeat a claim that LV-I2R-008 now rejects.

Required remediation:

1. Replace the BOM alternative disposition with the V3 qualification result: Tesseract was explored but is not qualified because no reproducible full result-contract proof was retained; no historical field-miss or timing claim controls selection.
2. Scan every V3 controlled authority and evidence file for any other active Tesseract disposition based on the superseded report, then reseal.

## Gate decision

The other targeted checks pass. All active request-body controls use 20 seconds. Full decode and preprocessing run inside the supervised killable child with safe timeout, cancellation, shutdown, and cleanup ownership. The 41 FR and 41 test identifiers are unique and contiguous, all 31 BAIRD requirements remain represented, the registry has 19 unique aggregating checks, prior edge, regulatory, browser, evidence, and error-contract closures remain intact, and the cold-start miss remains an honest release stop. Architecture scope remains proportionate to the take-home.

BI cannot begin until the one contradictory controlled OCR disposition is corrected and the package is resealed.
