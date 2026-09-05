# Validation Results

Document ID: LV-VP-RESULT-001  
Execution date: 2026-09-04 to 2026-09-05  
Status: CR-002 validation, exact-candidate reviews, commit-bound deployment, and engineering pre-UAT complete; requester UAT ready

## Automated code and interface gates

| Check | Result |
| --- | --- |
| Ruff | PASS, zero findings |
| Strict mypy | PASS, source package |
| Pytest | PASS, 412 tests (backend and validation suites) |
| ESLint | PASS, zero findings |
| TypeScript | PASS, zero errors |
| Vitest and Testing Library | PASS, 38 tests in 7 files |
| Vite production build | PASS, 134 modules |
| Browser and accessibility workflows | PASS, 3 applicable tests and 3 declared browser-matrix skips |

One third-party Starlette TestClient deprecation warning is non-blocking and does not occur in the production Uvicorn path.

## Governed product validation

The governed product corpus passed 30 of 30 cases, including 24 development cases and 6 sealed holdout cases. All 576 expected check rows were observed, all 8 mutation controls passed, and no false clean result occurred. The corpus covers malt beverages, wine, distilled spirits, unknown type, conflicting evidence, warning defects, reference comparison, and degraded-image review paths. The synthetic labels now set the warning statement apart with visibly more space than their line spacing, as a printed label does, and the uncertain-separation case places a neighbouring line at about a third of a line height above the heading.

## Private current-image API and batch validation

The private UAT folder contained 223 selected files. The browser and server admission rule accepted 221 JPEG or PNG images and skipped the 2 JSON files (the disposition oracle and the pixel ground truth) without failing the selection. The production multipart API then produced:

- 221 of 221 successful individual image analyses
- 24 ordered checks and valid original-pixel evidence references in every successful result
- 155 server-suggested product groups
- no group above the three-image product limit
- 155 of 155 successful grouped-product analyses
- no filename, product-name, or expected-value override in the runtime or validator

Individual analysis averaged 3.840 seconds, with a 3.681-second median, 6.138-second p95, and 7.237-second maximum. Grouped-product reruns averaged 0.935 seconds, with a 0.525-second median, 2.830-second p95, and 5.764-second maximum. The 5-second arithmetic-mean target and 9-second hard-case ceiling both passed.

The detailed per-case technical report is `PRIVATE_UAT_CORPUS_REPORT.md`, and machine-readable evidence is `evidence/private-uat-corpus-e2e.json`. Public evidence uses case identifiers, image basenames required to join the local oracle, content hashes, outcomes, field-read flags, counts, and timing. Raw images, machine-specific paths, and raw OCR strings are excluded because public redistribution and disclosure rights were not established. Basenames are evidence keys only and do not participate in runtime selection or extraction.

## Difficult-image validation scenarios

The current difficult-image cases were exercised through the production multipart API to verify generic OCR and inference behavior:

| Product | Observed result |
| --- | --- |
| Jack Daniel's front and back | Distilled spirits, `JACK DANIEL'S`, `WHISKEY`, 40 percent ABV, 80 proof, 375 mL, and producer/location read |
| Organic Vodka front and back | Distilled spirits, `OrganicVodka`, neutral spirits, 40 percent ABV, 80 proof, 750 mL, and Hawaii producer/location read; country correctly remains not applicable for a domestic address |
| Cascade Light | Wine, `CASCADE LIGHT`, `RIESLING`, 11.5 percent ABV, 750 mL, producer/location, appellation, and sulfite evidence read |
| Peak Farm | Malt beverage, `PEAK FARM`, `DOUBLE PALE ALE`, 7.2 percent ABV, 16 fl oz, and producer/address read |
| Blood & Honey | Malt beverage, `BLOOD & HONEY`, `TEXAS STYLE ALE`, and producer/location read; the supplied image does not visibly include a reliable ABV or net-contents statement |

The machine-readable private-corpus evidence records a content-only cross-format equivalence test. The first analysis request after fresh application readiness returned HTTP 200 in 5.751 seconds, retained both submitted panel records, marked panel 2 with `duplicateOfPanelId: panel-1`, and kept the OCR worker at generation 1 with zero restarts. The evidence binds the result to SHA-256 hashes of the validator, pipeline, supervisor, and submitted files. Product names, filenames, and expected values do not participate in runtime selection or extraction.

The processing behavior uses generic OCR layout, semantic-noise exclusion, token-boundary beverage inference, and context ranking. Production logic contains no list of these products and does not read expected values from filenames or test manifests.

## Accuracy evaluation against the pixel ground truth

`scripts/score_ground_truth.py` ran every image in the private folder through the production
analysis path and scored it against two files that the runtime never reads: the disposition
oracle (`test-oracle-v1.json`, 42 matching images) and a field-level
ground truth read from the pixels of every image (`pixel-ground-truth-v1.json`). The evidence
is `evidence/ground-truth-scores.json`.

| Measure | Result |
| --- | --- |
| Images processed | 221 |
| Oracle conflicts excluded and reported separately | 6 of 42 |
| Non-conflicting oracle images reported clean that the oracle rejects (false clean) | 0 |
| Oracle images reported as a difference that the oracle passes (false reject) | 0 |
| Non-conflicting oracle images with the same disposition | 5 of 36 |
| Non-conflicting oracle images routed to review | 31 of 36 |
| Beverage type exact | 68 of 70 |
| Brand name exact, or contained in a longer read | 47 exact and 12 contained of 70 |
| Class or type exact, contained, or partial | 52 exact, 5 contained, 2 partial of 67 |
| Alcohol content exact | 65 of 65 |
| Proof exact | 28 of 28 |
| Net contents exact | 64 of 64 |
| Producer exact, contained, or partial | 35 exact, 6 contained, 9 partial of 65 |
| Country of origin exact or contained | 9 exact and 2 contained of 19 |
| Warning located when present | 64 of 70 |
| Warning wording | 20 exact, 38 Review, 5 missing, and 7 not applicable of 70 |
| Mean time per image | 3.843 s (median 3.669 s, p95 6.182 s, maximum 7.393 s, 45 over 5 s) |

Six oracle rows directly contradict the corresponding pixel annotations: missing-versus-present
warning statements, title-case-versus-uppercase headings, or bold-versus-regular warning bodies.
The harness identifies and excludes those rows from disposition-confusion counts while preserving
them in the evidence. This prevents a disputed annotation from being relabeled as either a false
clean or a false reject. Across the 36 non-conflicting oracle cases, no expected failure was
reported clean and no expected pass was reported as a difference. Thirty-one uncertain cases were
conservatively routed to Review. Most review routing comes from warning punctuation and typography
that cannot be resolved safely from the photograph.

Images that read wrongly or not at all are the known limitations: an embossed brand on a clear
bottle, the tiny warning on a curved side panel, a stylized can where the brand is decorative
type, and a heavily stylized graphic label; each is reported as review with the fields it
could not read marked as not verified.

151 photographs without ground truth were also processed, 145 of them the operator's store photographs (taken on a phone and normalized to 300 pixels per inch, mostly 2400 by 3200 or 4139 by 2778 pixels, 2 of them above the pixel limit and prepared the way the browser prepares them) and 6 earlier images outside the ground-truth set: 151 needs review. None was reported as a difference, and none as clean. Their timing on the development workstation was a 4.30-second mean, 4.09-second median, 6.81-second p95, and 7.57-second maximum, with 45 over 5 seconds. Dense back labels on curved glass carry thirty or more small lines, and their first recognition pass alone takes about five seconds; on those images the second, closer read is skipped under the time budget and the result says so, which is what keeps them inside the 9-second hard-case bound.

## Sealed product holdout

The sealed holdout contains 24 products, with eight malt beverages, eight wines, and eight distilled
spirits. Its manifest hash is `9fb850adfec0ff286405b42c0cc79d65402a680429b3d52fd07a534149cd1f2a`.
The corrective candidate produced 137 exact normalized field results across 195 eligible product
fields, for a 70.26 percent exact rate, with zero false clean against annotated deterministic defects.
All 23 applicable ABV statements were exact. Producer results were 8 exact, 3 contained, 4 partial,
3 wrong, and 2 missed. Review attribution reconciled to 71 missing-evidence, 49 presentation,
26 policy, 13 OCR, 7 trusted-context, and 2 conflicting-evidence causes. Mean product time was
4.628 seconds, median was 4.671 seconds, p95 was 5.868 seconds, and the maximum was 7.831 seconds.

The provisional four-exact producer-and-warning utility target was not achieved. General producer
parsing improved full-corpus exact producer results from 31 to 35 and sealed-holdout exact producer
results from 7 to 8 without a protected-field loss or false clean. Remaining misses are dominated by
damaged recognition, absent readable pixels, and disputed truth rows. Variance `LV-VAR-002` accepts
that measured result rather than adding product-specific rules, weakening warning policy, or adding
a second runtime recognizer.

## OCR model decision

The governed bakeoff compared the current PP-OCRv4 English recognizer with PP-OCRv5 English mobile
and PP-OCRv5 Latin under the same detector, preprocessing, rules, hardware, and sealed products.
Both candidates were faster and neither created a false clean, but each regressed previously correct
protected ABV or warning-wording fields. Neither passed the promotion gate. PP-OCRv4 English remains
the single production recognizer. Exact frozen-box replay remains mandatory before any later model
promotion; it was not used to rescue candidates that had already failed protected-field gates.

## Accuracy boundary

The private API gate proves processing, contract, evidence, grouping, and timing behavior. Field-level accuracy is measured separately against the pixel ground truth above; the ground truth was read by people from the pixels and is not an independent COLA record.

Label-derived values also cannot prove agreement with an independent COLA application. Formula, chemistry, permit, state-law, production-record, and trustworthy physical-size facts require additional evidence.

## Security and dependency validation

The security review covers the public HTTP boundary, uploads, image decoding, worker lifecycle, history, browser resources, exports, container, deployment workflow, and dependency acquisition. The regression evidence verifies:

- opaque HttpOnly browser-scope authorization on every history operation;
- an 8 KiB streamed JSON limit on history mutations;
- exact production Origin enforcement for state changes;
- per-client minute rate fairness below the global allowance;
- formula-safe CSV cells;
- lifecycle-managed batch preview URLs;
- bounded upload, decoded-pixel, timeout, worker, cache, and history capacity controls;
- non-root container execution and pinned GitHub Actions;
- no content logging or runtime cloud inference.

Python and production npm dependency audits are part of the complete release gate. No critical or high security finding may remain unresolved.

The final independent security diff review examined all 46 changed executable and contract surfaces in the corrective integration range. Coverage was complete, no surface was deferred, and no reportable security finding remained after upload, decode, OCR supervision, correction, immutable-revision, history-isolation, rendering, model-acquisition, and validation-tool traces.

## Release-bound checks

The frozen manifest, three independent RT decisions, final application commit, protected deployment, immutable image digest, live contract checks, and browser pre-UAT are recorded in `../10-release/FINAL_RT_SIGNOFF.md`, `../10-release/DEPLOYMENT_EVIDENCE.json`, and `evidence/live-browser-uat.json`.

The first CR-002 final-review snapshot was not released. Architecture and delivery review found mutation-boundary, unresolved-type, per-field provenance, correction-replay, add-panel telemetry, deletion-order, public-error-name, and staged-source-hash gaps. A second architecture review found stale add-panel baseline, split replay lineage, class-inference, sulfite-absence, numeric-audit, and browser-evidence gaps. A third architecture challenge found incomplete merge provenance, reviewer-corrected family precedence, stale resolved-family state after conflicting added evidence, and invalid right/bottom-boundary manual polygons. A fourth frozen-candidate review found that mixed-source add-panel responses could disagree with their declared provenance or the reference stored in history. Response reconciliation and resolved and unresolved integration regressions close that gap. A later requirements review found duplicate BAIRD identifiers that made downstream citations ambiguous; BAIRD requirements are now uniquely numbered 1 through 42, affected feature citations are exact, and a sequential-ID regression prevents recurrence. The implementation and dedicated regressions close all recorded findings, tracked corpus evidence has been regenerated from the corrected sources, and the complete release gate passed before the documentation-only numbering correction. The affected regression and full source gate then passed with 412 tests. Three identical-snapshot reviews returned Clear before publication. The exact candidate was committed, deployed, and verified as recorded below.

## Public Azure deployment validation

The protected workflow deployed CR-002 application commit `0e9e79f37b074ba2f432ec7f6cf3e99495a4f007` in GitHub Actions run `33942995735`, attempt 1. The deployed image digest is `sha256:fddb9af98443e3206abc9af44ef15072308bbf05bb2b4374ab3262dc2d4f260d`. Azure readback confirmed 4 vCPU, 8 GiB, and the zero-to-one replica contract. Public liveness, readiness, exact build metadata, HSTS, history creation, and application checks passed. Three public sample analyses completed in 2,958.387, 338.846, and 343.406 milliseconds, for a 1,213.546-millisecond mean and 2,958.387-millisecond maximum. Each returned all 24 checks with no mismatch, conservative warning handling, and physical warning size correctly left Not verified from a photograph.

## Live-browser UAT execution

Engineering browser pre-UAT passed against the exact CR-002 Azure build. It directly covered the home, three advertised beverage families, label-first two-panel sample, all 24 checks, evidence selection, warning inspection, Table, Cards, and Image first views, and creation of a reopenable history record under the 500-record boundary. The protected workflow separately exercised public history and three complete verification requests. Automated release tests cover batch progress and grouping, folder admission, unsupported-file skipping, decoded-pixel guidance, failure isolation, retry, cancel, export, accessibility, keyboard use, and responsive behavior. The detailed result is `evidence/live-browser-uat.json`. Requester acceptance remains open.
