REWORK_REQUIRED

# RT2 I2R and FRD UX Review V2

Review role: stakeholder, user experience, and evaluator-fit red team  
Reviewed snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V2.sha256`  
Expected and observed manifest SHA-256: `5d2fe2e62c5052bbb10f1e263946383c2674546e108dbdbb605586ba3c34c938`  
Manifest entries: 44  
Hash verification: 44 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015 scan: 0 findings in the sealed snapshot

## Prior RT2 finding retest

`RT2-I2R-FRD-V1-F001` is CLOSED. `FR-037` and `T-037` now require two independent no-instruction sessions covering both Try sample and the complete manual entry, upload, correction, verification, evidence, and start-over journeys.

`RT2-I2R-FRD-V1-F002` is CLOSED. The authoritative `docs/04-i2r-ae/selected-check-registry-v1.json` contains 19 unique checks. Contrast and legibility are separate. Physical size is a separate human-confirmation check. `FR-019`, `FR-020`, `FR-023`, `T-019`, `T-020`, and `T-023` require independent rows, states, reasons, evidence behavior, and full rendering.

## Material findings

### RT2-I2R-FRD-V2-F001 - HIGH - Recovery can discard unsaved work because preservation and reset confirmation are not binary FRD outcomes

The I2R UX contract says an inference timeout preserves the form and selected browser files when safe at `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:51`. It also says Start over asks for confirmation when work exists at `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:121-123`.

Those user protections are not preserved in binary FRD acceptance:

- `FR-025` requires exhaustive error mapping and successful retry recovery, but does not require valid reference values and selected panels to remain available after a retryable result-free error at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:47`.
- `FR-027` requires Start over to clear everything, but does not require confirmation when work exists or require a cancelled confirmation to leave state unchanged at line 49.
- `FR-041` requires cancellation timing and safe server ownership, but does not require cancellation to return to the still-populated editable Intake state at line 63.
- The browser error registry says cancellation returns to editable Intake with no result at `docs/04-i2r-ae/07_I2R_ERROR_REGISTRY.md:40`, but does not say whether the form and file selection survive.

This is material because the prototype intentionally has no saved history. A user who waits through an upload or OCR failure, or accidentally activates Start over, can otherwise lose all manually entered reference data and panel selection. That conflicts with the low-tech, low-friction recovery objective and makes Retry misleading.

Required remediation:

1. Amend `FR-025` and `FR-041` so retryable result-free errors and user cancellation preserve valid form values and selected browser files when the browser still owns safe handles, while clearing any prior result as current.
2. Define the cases where preservation is unsafe or impossible and give those cases an explicit plain-language warning before destructive loss where the user can still choose.
3. Amend `FR-027` so Start over requires an accessible confirmation when work exists, Cancel leaves all state unchanged, and Confirm performs the current complete clear.
4. Extend `T-025`, `T-027`, `T-037`, and `T-041` with state-preservation and destructive-confirmation assertions.

### RT2-I2R-FRD-V2-F002 - HIGH - The revised upload deadline still has a contradictory 3-second normative control

The corrected ingress, runtime, and FRD contracts consistently select a non-resetting 20 second body deadline:

- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:149-176` defines the 20 second deadline, reduced 8 MiB aggregate profile, and shaped-network proof.
- The composed timing contract repeats 20 seconds at lines 189-201.
- `FR-008`, `FR-031`, and `FR-041` require 20 second upload behavior at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:30,53,63`.

However, the normative threat-control table still specifies a non-resetting 3 second total body deadline at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:203-208`.

This is material because 3 seconds is the rejected deadline that made the accepted upload envelope infeasible. A developer or test author following the threat table can build behavior that contradicts the ingress contract, shaped-network acceptance, error timing, and recovery copy.

Required remediation:

1. Replace the stale 3 second value with the selected 20 second body deadline everywhere in the controlled specification.
2. Run an exact-value consistency check across LV-I2R-001, LV-I2R-002, LV-I2R-007, the FRD, and test trace before resealing.

## Unaffected review areas

The revised evidence contract, exhaustive error registry, cancellation race ownership, browser non-persistence, public disclosure, separate normal and maximum performance profiles, blocked-egress operation, accessibility contract, Grok/Gemini disposition, and honest capability boundaries are materially sound.

All 19 registry checks are unique, aggregating, and covered by field, warning, panel, image-quality, rendering, evidence, and aggregation requirements. The old 17-check spike registry is explicitly legacy evidence and no longer controls the product contract.

The architecture remains a core-first modular monolith. Batch is excluded, external inference is not required, no persistence layer or user-account system is added, and the added safety controls remain bounded to the public upload surface. No material architecture overbuild was found.

The FRD contains 41 contiguous `FR-NNN` requirements and 41 contiguous `T-NNN` identifiers. All 31 BAIRD requirements remain represented. These structural passes do not resolve the two contradictory user-facing contracts above.

## Gate decision

The combined I2R and FRD package cannot advance on RT2 until recovery preserves in-browser work and confirms destructive reset through binary acceptance, and the obsolete 3 second upload deadline is removed. Correct both findings, reseal the complete package, and rerun the three independent reviews on the same revision.
