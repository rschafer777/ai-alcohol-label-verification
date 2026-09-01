REWORK_REQUIRED

# RT2 I2R and FRD UX Review V4

Reviewed snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V4.sha256`  
Expected and observed manifest SHA-256: `828fa0b9bf42e2add1054a67106f706be73065cb5d56e4ec0ab80fa95141ad91`  
Entries: 54  
Hash result: 54 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015: 0 findings

## Material finding

### RT2-I2R-FRD-V4-F001 - HIGH - The corrected legacy feasibility report still presents unsupported and obsolete claims as current evidence

The governing OCR rationale is appropriately cautious. LV-I2R-008 says the historical Tesseract inputs and runtime assets were not retained, no historical field-miss or timing claim controls selection, and Tesseract is not qualified because it lacks a reproducible full result-contract proof at `docs/04-i2r-ae/08_I2R_OCR_CANDIDATE_COMPARISON.md:37-46`. The model BOM now uses the same honest rationale.

However, the sealed `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md` still presents the opposite claims in its comparison table:

- Tesseract missed the clean one-panel brand and three-panel ABV at lines 193-194;
- it materially corrupted the warning and split the six-panel brand at lines 195-196; and
- it was rejected as primary at line 197.

The following paragraph says those exact field-coverage observations are not reproducible or decisional. The same report also labels an obsolete 3.0 second upload deadline and deterministic 17-check aggregation as the selected direction at lines 201-217, despite the current 20-second deadline and authoritative 19-check registry.

This is material to stakeholder and evaluator trust. The submitted documentation can repeat unsupported comparative claims and contradictory product limits even if the UI is correct. It violates the requirement that limitations and validation claims agree across documentation and evidence, and it can misrepresent why the OCR choice was made.

Required remediation:

1. Remove the unsupported field-miss, corruption, and rejected-as-primary statements from the comparison table, or label each only as an unverifiable historical observation that cannot support selection.
2. Replace the primary disposition with the governing result: Tesseract was explored but not qualified because no reproducible full result-contract proof was retained.
3. Mark the report prominently as legacy, non-authoritative evidence and identify LV-I2R-001, LV-I2R-008, the current raw run files, and `selected-check-registry-v1.json` as the governing sources.
4. Remove or explicitly quarantine the obsolete 3.0 second, 17-check, old-resource, and old-metric architecture conclusions so an evaluator cannot read them as current product claims.
5. Re-run the cross-artifact claim-consistency review before resealing.

## Targeted regression result

- Retryable failure and cancellation preserve editable form values and selected files through binary `FR-025` and `FR-041` acceptance.
- Start over confirmation, Cancel unchanged, Confirm clear, and clean-state behavior remain binary in `FR-027`.
- First-time Try sample and complete manual usability remain binary in `FR-037` and `T-037`.
- The authoritative registry still has 19 unique checks with separate warning contrast, legibility, and physical-size limitation rows.
- All active I2R and FRD contracts use the 20-second request-body deadline. The obsolete three-second value survives only in the misleading legacy report identified above and historical review records.
- No material UX, accessibility, privacy, cancellation, evidence, recovery, scope, or architecture-overbuild regression was found.

## Gate decision

BI is not ready on this seal because the controlled evidence package still exposes contradictory and unsupported evaluator-facing claims. Correct the one finding, reseal, and rerun the independent reviews.
