CLEAR

# BAIRD RT3 Intake Validation V4

## Snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V4.sha256`
- Expected manifest SHA-256: `0369475a6f451ef739cdf53d7831542a90398b1d6c7b0813dbdd707481a3d9f6`
- Observed manifest SHA-256: `0369475a6f451ef739cdf53d7831542a90398b1d6c7b0813dbdd707481a3d9f6`
- Expected entries: 38
- Observed entries: 38
- Missing entries: 0
- Hash mismatches: 0
- Files containing U+2010 through U+2015: 0

## Targeted acceptance-detail retest

The three V3 acceptance-detail corrections are complete and introduce no material regression:

1. `BR-013` now requires a first-time evaluator to complete both Try sample and the supported manual reference-entry, upload, validation-correction, verification, evidence-review, and start-over journeys without external instruction. Exact interaction design remains an I2R A&E decision.
2. `BR-009` now preserves prescribed warning text, heading capitalization, heading emphasis, remaining-text emphasis, continuity, separation, contrast, and legibility as independent evidence-backed checks. Unsupported physical-format properties remain Not verified or require human confirmation.
3. `BR-010` now preserves the at-least-30-attempt warmed benchmark, its required fixture and browser-session composition, p95 target, and 100 percent complete-result rule. `BR-021` now preserves at least 24 end-to-end submissions, at least 6 sealed holdouts, required scenario coverage, independent expected outcomes, and anti-hard-coding behavior.

## Regression result

- All 58 `SRC-NNN` rows and all 3 `DEC-NNN` rows remain uniquely dispositioned.
- `BR-001` through `BR-031` and `BQ-001` through `BQ-014` remain unique and contiguous.
- Warmed verification, public load, cold start, and hard failure timing remain separate and internally consistent.
- Restricted-network behavior remains architecture-neutral and fails safely without false-clean results.
- BAIRD defines outcomes and bounded questions without selecting an OCR engine, model, framework, API shape, host, runtime topology, resource limit, or work package.
- Repository, all-source, README, documentation, deployment, provenance, code-quality, privacy-disclosure, limitation, data-minimization, branding, and writing obligations remain traceable.
- Historical process wording remains explicitly superseded by the active process and `EVT-014`.

## Material findings

None.

## Gate decision

CLEAR
