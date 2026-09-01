REWORK_REQUIRED

# RT1 BAIRD Intake Validation V3

Review date: 2026-08-31

Role: Independent requirements-fidelity reviewer

## Sealed snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V3.sha256`
- Expected and observed manifest SHA-256: `57f094518cbdf8c2680307623923464ec7ef4943189f5ff8ed020cb92019d8c8`
- Expected and observed entries: 34
- Missing entries: 0
- Hash mismatches: 0
- Source dispositions: 58 unique contiguous rows from `SRC-001` through `SRC-058`
- Requester decision dispositions: 3 unique contiguous rows from `DEC-001` through `DEC-003`
- BAIRD requirements: 31 unique contiguous rows from `BR-001` through `BR-031`
- Prohibited characters U+2010 through U+2015 in sealed files: 0

The two RT1 V2 findings are closed. Every BR now has upstream lineage, every SRC and DEC has an explicit disposition, and `BR-023`, `BR-027` through `BR-031` carry the previously omitted delivery, code-quality, privacy, data-minimization, limitation, and writing obligations. The active BAIRD baseline selects no OCR engine, framework, host, deployment topology, API shape, or other implementation architecture.

## Material finding

### `RT1-BV3-F001` - HIGH - The binary BR outcomes weaken the attested DEC-003 benchmark contract

`DEC-003` attests the complete fixture and success contract in `docs/intake/success-definition.md`. That contract requires at least 24 end-to-end synthetic submissions with at least 6 holdouts at `docs/intake/success-definition.md:23-40`, and at least 30 predeclared warmed verification attempts with fixed composition and 100 percent completion at `docs/intake/success-definition.md:54-65`. The approved Intake repeats the 24-submission and 6-holdout minimum at `docs/intake/INTAKE_DOCUMENT.md:134-138`.

The V3 disposition matrix maps `DEC-003` to `BR-010` and `BR-021` at `docs/03-baird/02_BAIRD_SOURCE_DISPOSITION_MATRIX.md:81`, but the mapped BR acceptance outcomes do not preserve those minimums:

- `BR-010` at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:91` requires p95 at or below 5.0 seconds on a predeclared benchmark with 100 percent complete valid results, but it omits the minimum 30 attempts and required benchmark composition.
- `BR-021` at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:102` requires a sealed holdout subset, but it omits the minimum 24 submissions, minimum 6 holdouts, and the attested scenario coverage.

This is material because I2R and the FRD can satisfy the stated BR acceptance outcomes with a much smaller benchmark and fixture set while violating the approved Intake contract. A source link does not make a weaker binary acceptance criterion equivalent to the attested requirement, especially when BAIRD declares itself the complete baseline I2R will design against.

Required remediation:

1. Amend `BR-010` to preserve the at-least-30-attempt warmed benchmark and its fixed composition, while retaining the current 100 percent completion and p95 rules.
2. Amend `BR-021` to preserve at least 24 end-to-end submissions, at least 6 sealed holdouts, the required scenario families, and the separate expected-outcome oracle.
3. Keep exact OCR, deployment, fixture rendering, and test implementation choices in I2R A&E.

## Gate decision

V3 closes the prior source-lineage, delivery, quality, privacy, process, cold-start, blocked-egress, and architecture-boundary findings. It cannot advance until the two weakened DEC-003 acceptance outcomes are restored to the BR baseline and the corrected revision is resealed.
