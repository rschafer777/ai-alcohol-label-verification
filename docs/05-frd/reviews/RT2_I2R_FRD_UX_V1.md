REWORK_REQUIRED

# RT2 I2R and FRD UX Review V1

Review role: stakeholder, user experience, and evaluator-fit red team  
Reviewed snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V1.sha256`  
Expected and observed manifest SHA-256: `d2203fcfc94fd469d2855f50d9af291780014c751ce7dcaf8c51f1144b6f81c4`  
Manifest entries: 32  
Hash verification: 32 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015 scan: 0 findings in the sealed snapshot

## Material findings

### RT2-I2R-FRD-V1-F001 - HIGH - The first-time manual usability outcome is not a binary FRD acceptance test

The approved BAIRD requires a first-time evaluator to complete both Try sample and the full manual reference-entry, upload, validation-correction, verification, evidence-review, and start-over journeys without external instruction in `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:93`. I2R preserves that objective in `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:8-10` and maps `BR-013` to first-time sample and manual usability scripts in `docs/04-i2r-ae/05_I2R_REQUIREMENTS_TRACEABILITY.md:22`.

The FRD decomposes the workflow into technical feature checks in `FR-002` through `FR-007`, `FR-023`, and `FR-027`, but none has binary acceptance for a first-time, low-tech evaluator completing the full manual journey without outside instruction. `FR-002` tests only Try sample. The remaining rows test schema, conditional fields, panel mechanics, error focus, request status, result rendering, and clearing state in isolation. `T-001` through `T-007` are described as UI and primary-journey tests at `docs/05-frd/02_FRD_TEST_TRACEABILITY.md:10`, but no feature acceptance requires the first-time usability script that the I2R trace promises.

This is material because an implementation can pass every current FRD row while remaining confusing in the actual agent workflow. Sarah's clean-and-obvious requirement and the V4 BAIRD correction are therefore not fully protected downstream.

Required remediation:

1. Add a Must FRD requirement, or amend an existing Must, with binary acceptance for first-time completion of both Try sample and the full supported manual journey without external instructions.
2. Assign a dedicated test that records the primary action, reference entry, conditional origin behavior, 1-panel and multi-panel upload, validation correction, verification, evidence inspection, error recovery, and start-over.
3. Preserve the current low-tech, keyboard, focus, and plain-language requirements without prescribing a different page architecture.

### RT2-I2R-FRD-V1-F002 - HIGH - The warning registry contradicts the independent warning-check contract

The governing BAIRD requires contrast and legibility as independent checks and requires unsupported physical-format checks to remain Not verified or require human confirmation at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:89`. I2R repeats independent contrast and legibility and says physical size is Not verified without reliable scale at `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:137`. The UX design requires separate contrast, legibility, and physical-size limitation rows at `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:71-78`. `FR-020` also says continuity, separation, contrast, and legibility are evaluated independently at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:42`.

However, the only sealed selected-check registry contains one combined `warning_contrast_legibility` check and no physical-size check. The retained expected-field manifest uses the same combined identifier. This conflicts with the result contract that every applicable registry check appears once at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:60-94` and with `FR-023`, which renders all applicable check rows at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:45`.

This is material because one combined state cannot show a case where contrast is sufficient but text remains unreadable, or the reverse. The missing physical-size entry also leaves no binary guarantee that the user sees the promised human-only or Not verified limitation row.

Required remediation:

1. Define the authoritative product selected-check registry for I2R and split `warning_contrast` and `warning_legibility` into separate applicable checks, states, reasons, evidence, and fixtures.
2. Add a `warning_physical_size` Not verified or human-confirmation check, or define an equally explicit non-registry limitation-row contract and binary UI test. Do not infer physical size from an unscaled image.
3. Update the result contract, expected-outcome manifest direction, `FR-020`, `FR-023`, and `T-020` or `T-023` so the specification has one consistent executable interpretation.
4. Keep the retained spike registry clearly classified as superseded evidence if it is not the implementation registry.

## Unaffected review areas

The selected architecture is a bounded modular monolith with batch excluded from the required release. No material architecture overbuild was found. The five-second warmed goal, cold-start limitation, blocked-egress behavior, privacy lifecycle, neutral branding, human authority, false-clean prevention, evidence focus, accessibility, plain recovery states, public evaluator path, and Grok/Gemini adopt-or-reject disposition remain aligned with Sarah, Dave, Jenny, IT, and the assignment.

The FRD contains 36 contiguous `FR-NNN` requirements and 36 contiguous `T-NNN` identifiers, and all 31 BAIRD requirements appear in FRD upstream mappings. Those structural counts do not close the two missing or contradictory user-visible acceptance contracts above.

## Gate decision

The combined I2R and FRD package cannot advance on RT2 until the first-time manual usability journey is binary-tested and the warning check registry is made consistent with the independent warning requirements. Correct both findings, reseal the complete package, and rerun all three independent reviews on the same revision.
