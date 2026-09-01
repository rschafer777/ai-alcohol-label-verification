CLEAR

# RT1 BAIRD Intake Validation V4

Review date: 2026-08-31

Role: Independent requirements-fidelity reviewer

## Sealed snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V4.sha256`
- Expected and observed manifest SHA-256: `0369475a6f451ef739cdf53d7831542a90398b1d6c7b0813dbdd707481a3d9f6`
- Expected and observed entries: 38
- Missing entries: 0
- Hash mismatches: 0
- Source dispositions: 58 unique contiguous rows from `SRC-001` through `SRC-058`
- Requester decision dispositions: 3 unique contiguous rows from `DEC-001` through `DEC-003`
- BAIRD requirements: 31 unique contiguous rows from `BR-001` through `BR-031`
- I2R A&E questions: 14 unique contiguous rows from `BQ-001` through `BQ-014`
- Prohibited characters U+2010 through U+2015 in sealed files: 0

## Prior finding retest

`RT1-BV3-F001` is closed.

- `BR-010` now requires one predeclared set of at least 30 valid warmed attempts, every benchmark fixture at least once, at least one multi-panel fixture, at least 5 fresh browser sessions, p95 at or below 5.0 seconds, and 100 percent complete valid results.
- `BR-021` now requires at least 24 deterministic end-to-end submissions, at least 6 sealed holdouts, independently authored expected outcomes, the attested scenario families, per-field reporting, and anti-hard-coding protection.

The V2 closures remain intact. Every BR has upstream lineage, every SRC and DEC has an explicit disposition, and the delivery, code-quality, privacy, public-artifact minimization, limitation, and writing requirements remain active. `BR-009` now carries the independent warning-presentation checks, and `BR-013` now tests both Try sample and the complete manual workflow.

The BAIRD requirements state product and evidence outcomes only. OCR, preprocessing, schema, normalization, UX design, component boundaries, data movement, limits, languages, frameworks, hosting, validation implementation, batch selection, and observability remain bounded I2R A&E questions. No implementation architecture is selected.

## Material findings

None.

## Gate decision

CLEAR
