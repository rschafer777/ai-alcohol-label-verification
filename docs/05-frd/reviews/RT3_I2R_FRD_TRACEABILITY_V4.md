REWORK_REQUIRED

# RT3 I2R and FRD Delivery and Traceability Review V4

## Seal and chain verification

- Snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V4.sha256`
- Expected and observed SHA-256: `828fa0b9bf42e2add1054a67106f706be73065cb5d56e4ec0ab80fa95141ad91`
- Entries: 54
- First verification missing entries: 0
- First verification hash mismatches: 0
- Required second verification hash mismatches: 2
- Changed after sealing: `docs/05-frd/I2R_FRD_RT_REMEDIATION.md`, expected `8d6ec4cc2a4598b547cfc7ae795b316819a004c5ed1fdcc28757da054645a167`, observed `edc98783cf316b315f4d1cad608e02035b51142b76fc8e88b1853b3cfb8b845b`
- Changed after sealing: `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md`, expected `f15549085b0a571f8e1c1f183d326a2a3f2a168a20eea651435e52958c44d46a`, observed `7e24fe7f7b00d1df1a7dd2f77a15080946b67790e4c8e243af04c153419de9b9`
- Prohibited U+2010 through U+2015 characters: 0
- BAIRD requirements: 31 of 31 reach I2R and FRD
- BAIRD questions: 14 of 14 have I2R decisions
- Components: 16 of 16 reach the FRD
- Feature and test pairs: 41 unique contiguous FRs and 41 unique contiguous tests
- Product registry: 19 unique checks

The V3 deadline and FRD-authority corrections remain closed. Evidence, raw-request, cancellation, public-edge, error, delivery, exclusion, and release-gate chains show no material regression.

## Material finding

### RT3-I2R-V4-F000: The V4 review target changed between required seal verifications

Severity: HIGH

The manifest and all 54 entries matched at the start of review. The required second verification found the two mismatches listed above. Neither file was edited by RT3. V4 therefore no longer identifies the current package, and reviewers cannot issue a shared decision on one immutable revision.

Required remediation:

Do not rewrite the V4 manifest. Finish the corrections, create a new versioned snapshot, and have all three reviewers validate that same immutable revision twice.

### RT3-I2R-V4-F001: The V3 OCR correction is not fully auditable in the sealed evidence chain

Severity: HIGH

Evidence:

- LV-I2R-008 states at `docs/04-i2r-ae/08_I2R_OCR_CANDIDATE_COMPARISON.md:39` that the historical Tesseract inputs and runtime assets were not retained, so no field-miss or timing claim from those runs is reproducible or decisional.
- LV-I2R-008 states at line 44 that Tesseract is not rejected on an unsupported field-miss claim and is instead not qualified because it lacks a controlled full result-contract proof.
- The corrected model BOM now follows that rule at `docs/baird/evidence/MODEL_BOM.md:43`.
- The sealed legacy feasibility report still states that Tesseract missed the clean brand and three-panel ABV, corrupted the warning and six-panel brand, and was `Rejected as primary` at `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:193-197`.
- The next paragraph at line 199 says those exact historical field and timing claims are not reproducible or decisional.
- The remediation record claims the stale rejection statement was replaced in both the BOM and feasibility report at `docs/05-frd/I2R_FRD_RT_REMEDIATION.md:47`, but the report still contains the stale disposition and unsupported field claims.

Impact:

The same sealed evidence file both asserts and disclaims the unsupported comparison. The remediation record therefore overstates what changed, and BI or later README documentation can still inherit an invalid candidate-selection rationale from a file named as controlled evidence. This fails the requested V3 correction-auditability check even though RapidOCR remains a supportable choice on its positive controlled evidence.

Required remediation:

Remove or replace the unsupported Tesseract field/timing rows and `Rejected as primary` disposition in the feasibility report. The controlled record should say only that Tesseract was explored and remains not qualified because no reproducible full result-contract proof was retained. Then verify the remediation statement against the exact file, reseal, and rerun the gate.

## Gate decision

BI decomposition is not authorized on V4. Its sealed contents retained one controlled-evidence contradiction, and its review target then changed before the second integrity check. The corrected package requires a new immutable snapshot and review.
