REWORK_REQUIRED

# RT1 BAIRD Architecture and Requirements Fidelity Rereview 2

Review date: 2026-08-31

## Reviewed sealed snapshot

- Manifest: `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V2.sha256`
- Expected and observed manifest SHA-256: `0d80c9ffa7bb2e7d23d550b1639d7e9dc2c520b8e8500e264c71ecf1c0e1e29d`
- Expected and observed entries: 95
- Missing files: 0
- Hash mismatches: 0

The manifest hash and every listed file hash were verified before review and verified again immediately before this report was written. This report is outside the sealed manifest and no snapshotted file was modified.

## Review method

I independently reviewed the complete Intake, BAIRD package, retained research source, raw architecture and browser evidence, fixture images and manifests, all prior BAIRD red-team reports, and `BAIRD_RT_REMEDIATION.md`. I also:

1. reran the BAIRD traceability validator and confirmed 58 source rows, 12 ADR rows, 8 BG rows, 18 THR rows, 96 requirement IDs, 96 test IDs, and 25 fixture IDs with no structural relation error;
2. independently parsed all 42 architecture runs, 42 browser runs, and five cold-start runs;
3. inspected representative clean, warning, capitalization, import, multi-panel, and degraded-evidence payloads;
4. traced the executable check inventory and aggregation code against the Intake selected checks, `BAIRD_ASSESSMENT.md`, `WARNING_CAPABILITY_MATRIX.md`, `ENGINEERING_BLUEPRINT.md`, and `SOURCE_COVERAGE.csv`;
5. traced timeout control flow against the selected child, app, browser, and Fly deadlines; and
6. rechecked the current official TTB distilled-spirits health-warning and alcohol-content guidance, plus 27 CFR Part 16. The current primary sources continue to support the Intake and BAIRD rules for warning applicability, the exact heading and colon, heading emphasis, a non-bold remainder, and proof as an additional alcohol-content statement.

## Binary verdict basis

The technology direction is reasonable for the assignment, and most earlier architecture, deployment, evidence-durability, security, cold-start, and fixture-truth defects were corrected. BAIRD cannot advance to I2R yet because the retained executable evidence still omits selected active checks, contains uncovered false-clean paths, contradicts the attested result vocabulary, and does not implement the selected timeout recovery order. Those are material architecture and requirements-fidelity issues, not I2R wording details.

## Prior finding retest

| Prior finding | Result on V2 | Evidence |
|---|---|---|
| `RT1-B-F001` load-bearing assumptions | NOT CLOSED | The retained slice now exercises the real parent-child and browser path, but its self-declared active inventory omits proof and warning applicability while the report claims zero omitted active checks. See `RT1-B-RR2-F001`. |
| `RT1-B-F002` warning capability and aggregation | NOT CLOSED | The written matrix is strong, but the executable slice omits applicability and can issue Match for a missing colon and for body-weight evidence that does not independently prove a non-bold remainder. See `RT1-B-RR2-F001` and `RT1-B-RR2-F002`. |
| `RT1-B-F003` resource envelope | CLOSED | Byte, pixel, canvas, memory, concurrency, host, region, and cost boundaries are selected and retained. Parent-child memory evidence is now durable. |
| `RT1-B-F004` performance and timeout contract | PARTIALLY CLOSED | The hard five-second cancellation is gone and the metric semantics are correct. Timeout recovery still synchronously performs a four-second worker replacement inside a remaining 0.5-second app window. See `RT1-B-RR2-F004`. |
| `RT1-B-F005` options and fallbacks | CLOSED | Alternatives are now separated into measured, documented, and unknown evidence; failure paths reopen BAIRD instead of silently narrowing scope. |
| `RT1-B-RR-F001` five-second browser cancellation | CLOSED | Five seconds is now only the warmed p95 target. Independent hard bounds are documented at 6.25, 6.75, 7.5, and 9.0 seconds. |
| `RT1-B-RR-F002` incomplete retained result | NOT CLOSED | The browser renders the returned rows, but the authoritative inventory itself is incomplete and therefore cannot prove zero omitted active checks or zero false clean. See `RT1-B-RR2-F001` and `RT1-B-RR2-F002`. |
| `RT1-B-RR-F003` brand capitalization and punctuation | CLOSED | Brand case-only and punctuation-only paths now return Review, with `S14_brand_case` and `FX-025` aligned. A separate producer normalization drift remains in `RT1-B-RR2-F002`. |
| `RT1-B-RR-F004` source-coverage locators | PARTIALLY CLOSED | `SOURCE_COVERAGE.csv` is structurally complete and its named locators are valid, but `I2R_HANDOFF.md` still directs all SRC mappings to a different file. See `RT1-B-RR2-F005`. |

## Findings

### RT1-B-RR2-F001 - HIGH - The retained active-check inventory omits proof and warning applicability

The selected scope is unambiguous:

- `docs/intake/INTAKE_DOCUMENT.md:63` selects `ABV/proof`.
- `docs/intake/scope-boundary.md:33` selects alcohol-content comparison with ABV/proof normalization where defensible.
- `docs/intake/source-requirements.md:12` requires ABV/proof fixtures under documented normalization.
- `docs/baird/BAIRD_ASSESSMENT.md:91` makes proof Active whenever the reference or label presents it.
- `docs/baird/ENGINEERING_BLUEPRINT.md:187` requires reference comparison plus the two-times-ABV relationship.
- `docs/baird/WARNING_CAPABILITY_MATRIX.md:3-7` makes warning applicability an Active, aggregating row.
- `docs/baird/SOURCE_COVERAGE.csv` assigns proof to `SRC-004` and warning applicability to `SRC-025` with explicit tests and stop gates.

The retained slice does not implement those decisions:

- `research/baird-spike/spike.py:35-39` declares the inventory used by the omission assertion. It includes ABV but not proof or warning applicability.
- `research/baird-spike/spike.py:386-477` never extracts, compares, returns, or aggregates either omitted check.
- The retained `S01_clean_one` reference contains `"proof":"90"`, but its 13 result rows contain neither proof nor warning applicability and still return `No differences found`.
- `research/baird-spike/spike.py:461-470` can only detect omissions from its own incomplete `ACTIVE_CHECKS` set.
- `docs/baird/BAIRD_ASSESSMENT.md:78` and the remediation ledger consequently overstate `zero omitted active checks` and `zero false clean`.

Impact: a label can match 45 percent ABV, present an inconsistent proof value, and still receive a clean result. The architecture evidence also cannot prove the applicability rule that BAIRD marked Active. I2R would have to decide whether the executable inventory or the authoritative BAIRD decisions are real.

Required remediation:

1. Put proof into the executable selected-check registry whenever the label or reference presents it. Whether it is displayed as a row or an ABV sub-check may remain the documented I2R choice, but it must return a state and aggregate.
2. Put warning applicability into the executable registry with its own sufficient-evidence and uncertainty behavior.
3. Add fixed expected-outcome fixtures for matching, mismatching, missing, and ambiguous proof, including an ABV/proof relationship mismatch.
4. Add applicability fixtures immediately below, at, and above 0.5 percent ABV, plus an unparseable-applicability case.
5. Generate the omission assertion from the authoritative selected-check registry rather than a manually reduced set.
6. Rerun architecture and browser evidence and correct the zero-omission and zero-false-clean claims.

### RT1-B-RR2-F002 - HIGH - Selected comparison rules still contain uncovered false-clean paths

Three selected policies differ from the retained implementation.

First, `WARNING_CAPABILITY_MATRIX.md:9` requires the exact uppercase `GOVERNMENT WARNING:` heading and colon. `spike.py:418-419` returns Match for any readable heading containing `GOVERNMENT WARNING`, even when the colon is missing. The reason text then asserts that the colon was observed. `SOURCE_COVERAGE.csv` assigns title, lowercase, and missing-colon coverage to `T-065`, but the retained fixture set has no missing-colon architecture or browser case.

Second, the current official TTB rule and `WARNING_CAPABILITY_MATRIX.md:10-11` make heading emphasis and the non-bold remainder separate checks. `spike.py:324-341` derives both states from the same heading-to-body stroke ratio and always gives them the same state. A heavier heading can make the body row Match even if the body itself is still bold. `S12_warning_typography` proves only the opposite extreme, regular heading with bold body, so it cannot validate independent body-weight behavior.

Third, `BAIRD_ASSESSMENT.md:93` and `ENGINEERING_BLUEPRINT.md:185-189` route unproven punctuation variation to Review. `spike.py:438-445` removes all producer punctuation and capitalization and then returns Match. The retained producer fixture tests a different name, not punctuation-only or case-only variation.

Impact: readable nonconforming evidence can be reported as Match, and an otherwise clean submission can reach a clean summary. This violates the Intake no-false-clean invariant and the field-specific normalization policy.

Required remediation:

1. Require an exact readable uppercase heading plus colon for heading Match. Add missing-colon and altered-heading fixtures.
2. Implement independent evidence and calibrated decisions for heading emphasis and body non-boldness. If body weight cannot be independently proven, return Review or Not verified rather than Match.
3. Add at least these warning combinations: bold heading with regular body, bold heading with bold body, regular heading with regular body, and regular heading with bold body.
4. Apply the selected producer exact, case, whitespace, and punctuation policy. Case or punctuation variation that lacks an approved equivalence rule must return Review.
5. Add producer case-only, punctuation-only, missing, and true-difference fixtures.
6. Rerun the full retained evidence and demonstrate that each readable negative case prevents a clean summary.

### RT1-B-RR2-F003 - MEDIUM - BAIRD has two incompatible result contracts

The CLEAR Intake contract uses internal states `Match`, `Review`, `Mismatch`, and `Not verified`, with exact summaries `No differences found in checked fields`, `Review needed`, and `Differences detected` in:

- `docs/intake/INTAKE_DOCUMENT.md:66` and `:111-122`;
- `docs/intake/scope-boundary.md:44-52`;
- `docs/intake/success-definition.md:44-50`; and
- `docs/intake/source-requirements.md:40`.

`docs/baird/UX_PRODUCT_SPEC.md:97-109` correctly maps internal `Mismatch` to the user label `Difference` and preserves the Intake summary wording. In contrast, `WARNING_CAPABILITY_MATRIX.md:3` defines `Difference` as a state, `:19-21` defines `Differences found` and `No differences found`, and `spike.py:386-477` plus all retained evidence use those alternate internal and summary values.

Impact: I2R cannot derive one binary state machine without choosing which authority to override. The retained browser evidence also does not prove the user-visible wording that Intake selected.

Required remediation:

1. Select one canonical internal enum and one canonical display mapping across every BAIRD artifact. The existing Intake and UX contract supports internal `Mismatch` with user label `Difference`.
2. Use the exact Intake submission summaries everywhere, including evidence fixtures and browser assertions.
3. Update the warning matrix, result schema examples, feasibility slice, expected manifests, raw evidence, and traceability tests together.

### RT1-B-RR2-F004 - MEDIUM - Timeout recovery cannot satisfy the selected deadline order

`SECURITY_DATA_FLOW.md:149` selects a 6.25-second child deadline, a 6.75-second app deadline after body completion, and a 7.5-second browser deadline from Verify activation. `ENGINEERING_BLUEPRINT.md:253` requires the timed-out child to be terminated and joined before a new child is warmed.

The retained topology implements replacement synchronously inside the request:

- `research/baird-spike/server.py:102-104` calls `self.replace()` before raising the timeout.
- `server.py:93-95` stops and then starts the worker.
- Startup performs model initialization and a representative OCR warmup.
- The retained five cold trials report worker warmup between 4,111.54 ms and 4,260.35 ms.

A timeout detected at 6.25 seconds cannot synchronously complete a roughly four-second replacement and return within the remaining 0.5-second app window or the 1.25-second browser window. The browser harness waits 12 seconds and the disposable UI has no 7.5-second abort path, so the selected timeout order and recovery behavior were not exercised.

Impact: a forced OCR hang can violate the published hard bounds, keep the request open beyond the user timeout, or expose inconsistent readiness and capacity behavior. The architecture currently leaves I2R to invent the recovery sequence.

Required remediation:

1. Select an explicit sequence that terminates and joins the failed child, returns the non-clean timeout before the outer deadline, marks readiness/capacity unavailable, and performs replacement warmup without holding the timed-out response open.
2. Define whether readiness returns 503 and how new work is rejected until the replacement worker is warm.
3. Add a deterministic forced-worker-hang fixture that verifies child termination, no partial result, response timing, readiness transition, replacement warmup, restored service, artifact cleanup, and single-child ownership.
4. Exercise the actual 6.25, 6.75, and 7.5-second controls in the retained app and browser path.

### RT1-B-RR2-F005 - MEDIUM - The I2R stop condition names the wrong traceability authority for SRC rows

The second-round remediation correctly placed each `SRC` requirement, test, stop gate, and owner in `SOURCE_COVERAGE.csv`. `BAIRD_TRACEABILITY.md` also treats `SOURCE_COVERAGE.csv` and `BAIRD_CONTROL_HANDOFF_MATRIX.md` as separate required authorities.

`docs/baird/I2R_HANDOFF.md:87` nevertheless says that every `SRC`, `ADR`, `BG`, and `THR` mapping must be in `BAIRD_CONTROL_HANDOFF_MATRIX.md`. That matrix contains ADR, BG, and THR rows, not SRC rows. The literal I2R stop condition therefore fails the corrected package or encourages duplicate and diverging SRC mappings.

Required remediation:

1. Change the stop condition to require SRC mappings in `SOURCE_COVERAGE.csv` and ADR, BG, and THR mappings in `BAIRD_CONTROL_HANDOFF_MATRIX.md`.
2. Name both files in the BAIRD exit evidence and I2R authoritative-input list.
3. Keep the existing executable relation validator and semantic citation review as the acceptance proof.

## Confirmed strengths

- React, FastAPI, local RapidOCR/ONNX, one long-lived OCR child, and a single container form a coherent standalone architecture for a time-constrained prototype.
- Local inference honors the firewall and outbound-dependency context better than a cloud OCR dependency.
- The single-worker 2 GiB envelope is supported by retained parent-child memory evidence and explicit concurrency controls.
- The option comparison now avoids unsupported scoring and gives architecture-reopening fallbacks rather than silent scope loss.
- The warmed browser path includes client, upload, server, transfer, render, and live-region completion. The 42-attempt distribution is complete and does not replace failures with retries.
- Cold performance is reported honestly as not closed locally. Always-on deployment, readiness, and deployed release gates prevent the local miss from being mislabeled as a pass.
- Brand capitalization and punctuation fixtures now preserve the senior agent's judgment example as Review.
- Batch remains gated after the core rather than becoming an unsupported assignment blocker.
- Input, memory, worker ownership, cleanup, proxy identity, no-store, egress, release tuple, model integrity, and accessibility responsibilities are substantially more precise than in the initial BAIRD draft.

## Advancement decision

Do not advance this snapshot to I2R. Correct `RT1-B-RR2-F001` through `RT1-B-RR2-F005`, regenerate the affected source, fixtures, raw evidence, reports, and manifest, then repeat all three independent BAIRD reviews against one new sealed revision. CLEAR requires one authoritative active-check inventory, no uncovered false-clean path, one result vocabulary, an executable timeout recovery order, and an unambiguous I2R traceability handoff.
