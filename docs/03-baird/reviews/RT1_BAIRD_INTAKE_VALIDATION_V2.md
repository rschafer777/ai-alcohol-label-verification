REWORK_REQUIRED

# RT1 BAIRD Intake Validation V2

Review date: 2026-08-31

Role: Independent requirements-fidelity reviewer

## Sealed snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V2.sha256`
- Observed manifest SHA-256: `480036814fe952f6111dc434311d4052c8cb318a0692eb07b62e2805165b90fa`
- Expected and observed entries: 29
- Missing entries: 0
- Hash mismatches: 0
- `BR-001` through `BR-024`: 24 unique contiguous IDs
- Prohibited characters U+2010 through U+2015 in sealed files: 0

The review used only the 29 files named by the V2 manifest. The prior architecture contamination is removed from the active BAIRD baseline. No OCR engine, framework, host, or deployment architecture is selected by the corrected BR requirements. The following material requirements-fidelity findings remain.

## Material findings

### `RT1-BV2-F001` - HIGH - The BR baseline has no durable source mapping

`docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:79-104` gives each BR only a broad source class of STATED, DECIDED, or DERIVED. It does not identify the controlling `SRC-NNN`, `DEC-NNN`, `ASG-NNN`, `USR-NNN`, or `REG-NNN` records. This conflicts with the required chain in `docs/PROCESS.md:23-25`, which requires `source -> decision -> BAIRD requirement -> architecture decision -> feature requirement -> component -> test -> evidence`.

This is material because the 24 BRs aggregate 58 Intake source requirements, including conditional and proposed batch rows. I2R and the FRD cannot determine from the BAIRD baseline which exact source statements a BR carries, which accepted source rows were intentionally combined, and which conditional rows remain excluded without reconstructing that authority themselves. That creates the invention and drift risk the BAIRD stage is meant to remove.

Required remediation:

1. Add durable source and decision locators to every `BR-001` through `BR-024` row.
2. Add a source disposition map showing every active `SRC-001` through `SRC-058` as carried by a BR, conditional on a named decision, or excluded with an authorized reason.
3. Recheck source-class labels after the exact mappings are present. Mixed stated, decided, and derived requirements must not be labeled only STATED or DECIDED.

### `RT1-BV2-F002` - HIGH - Required delivery, quality, and public-upload obligations drop out of the BR baseline

The corrected BAIRD calls its 24 BRs the complete requirements baseline, but several accepted Must rows have no equivalent BR outcome:

- `BR-023` at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:103` requires approach, tools, and assumptions documentation but drops the required trade-offs and limitations content. Its acceptance outcome checks only clean checkout and deployed revision identity. The assignment requires trade-offs and limitations at `docs/intake/assignment-source-baseline.md:86`; `SRC-053` and `SRC-057` preserve that obligation at `docs/intake/source-requirements.md:96,100`; and the approved Intake repeats it at `docs/intake/INTAKE_DOCUMENT.md:207`.
- No BR carries the evaluator's code-quality and organization criterion from `ASG-036` at `docs/intake/assignment-source-baseline.md:80` or the accepted clean-organization and separable-test outcome in `SRC-056` at `docs/intake/source-requirements.md:99`. Architecture questions do not substitute for a required delivered quality outcome.
- `BR-016` requires no intentional persistence, but no BR requires the visible synthetic-only notice or truthful UI and README disclosure of actual data flow, provider use, logging, temporary handling, and retention. Those release obligations are explicit in `SRC-045` and `SRC-047` at `docs/intake/source-requirements.md:83,85` and in `docs/intake/INTAKE_DOCUMENT.md:146`.

These are not optional implementation details. They are assignment delivery criteria and approved Intake safety requirements. If they are absent from BAIRD, I2R and the FRD can satisfy every BR while still submitting incomplete documentation, weakly organized code, or misleading public-upload privacy copy.

Required remediation:

1. Expand `BR-023` and its acceptance outcome to verify approach, tools, assumptions, trade-offs, limitations, clean-checkout reproducibility, repository completeness, and deployed revision identity.
2. Add a testable delivered-code quality and organization requirement that preserves `SRC-056` without selecting a stack or component topology.
3. Add a user-facing privacy and data-handling honesty requirement that carries `SRC-045` and `SRC-047`, while leaving the actual data flow and provider choices to I2R A&E.

## Gate decision

The corrected V2 package is free of the earlier architecture selection and captures the core verification experience well. It cannot advance because its declared complete BR baseline breaks the required source chain and omits assignment-level delivery and public-upload obligations. Correct the two findings, reseal one revision, and rerun the three BAIRD reviews.
