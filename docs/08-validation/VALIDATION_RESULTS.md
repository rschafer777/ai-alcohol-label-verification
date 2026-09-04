# Validation Results

Document ID: LV-VP-RESULT-001  
Execution date: 2026-09-03  
Status: Engineering, governed-corpus, private-corpus, performance, protected Azure deployment, and engineering browser pre-UAT gates passed; requester UAT pending

## Automated code and interface gates

| Check | Result |
| --- | --- |
| Ruff | PASS, zero findings |
| Strict mypy | PASS, source package |
| Pytest | PASS, 372 tests (backend and validation suites) |
| ESLint | PASS, zero findings |
| TypeScript | PASS, zero errors |
| Vitest and Testing Library | PASS, 35 tests in 6 files |
| Vite production build | PASS, 131 modules |
| Browser and accessibility workflows | PASS, 3 applicable tests and 3 declared browser-matrix skips |

One third-party Starlette TestClient deprecation warning is non-blocking and does not occur in the production Uvicorn path.

## Governed product validation

The governed product corpus passed 30 of 30 cases, including 24 development cases and 6 sealed holdout cases. All 576 expected check rows were observed, all 8 mutation controls passed, and no false clean result occurred. The corpus covers malt beverages, wine, distilled spirits, unknown type, conflicting evidence, warning defects, reference comparison, and degraded-image review paths. The synthetic labels now set the warning statement apart with visibly more space than their line spacing, as a printed label does, and the uncertain-separation case places a neighbouring line at about a third of a line height above the heading.

## Private current-image API and batch validation

The private UAT folder contained 223 selected files. The browser and server admission rule accepted 221 JPEG or PNG images and skipped the 2 JSON files (the disposition oracle and the pixel ground truth) without failing the selection. The production multipart API then produced:

- 221 of 221 successful individual image analyses
- 24 ordered checks and valid original-pixel evidence references in every successful result
- 152 server-suggested product groups
- no group above the three-image product limit
- 152 of 152 successful grouped-product analyses
- no filename, product-name, or expected-value override in the runtime or validator

Individual analysis averaged 3.997 seconds, with a 3.895-second median, 6.748-second p95, and 7.874-second maximum. Grouped-product reruns averaged 1.014 seconds, with a 0.629-second median, 2.693-second p95, and 6.607-second maximum. The 5-second arithmetic-mean target and 9-second hard-case ceiling both passed.

The detailed per-case technical report is `PRIVATE_UAT_CORPUS_REPORT.md`, and machine-readable evidence is `evidence/private-uat-corpus-e2e.json`. Public evidence uses case identifiers, content hashes, outcomes, field-read flags, counts, and timing. Raw images, private filenames, and raw OCR strings are excluded because public redistribution and disclosure rights were not established.

## Difficult-image validation scenarios

The current difficult-image cases were exercised through the production multipart API to verify generic OCR and inference behavior:

| Product | Observed result |
| --- | --- |
| Jack Daniel's front and back | Distilled spirits, `JACK DANIEL'S`, `WHISKEY`, 40 percent ABV, 80 proof, 375 mL, and producer/location read |
| Organic Vodka front and back | Distilled spirits, `OrganicVodka`, neutral spirits, 40 percent ABV, 80 proof, 750 mL, and Hawaii producer/location read; country correctly remains not applicable for a domestic address |
| Cascade Light | Wine, `CASCADE LIGHT`, `RIESLING`, 11.5 percent ABV, 750 mL, producer/location, appellation, and sulfite evidence read |
| Peak Farm | Malt beverage, `PEAK FARM`, `DOUBLE PALE ALE`, 7.2 percent ABV, 16 fl oz, and producer/address read |
| Blood & Honey | Malt beverage, `BLOOD & HONEY`, `TEXAS STYLE ALE`, and producer/location read; the supplied image does not visibly include a reliable ABV or net-contents statement |

The machine-readable private-corpus evidence records a content-only cross-format equivalence test. The first analysis request after fresh application readiness returned HTTP 200 in 6.086 seconds, retained both submitted panel records, marked panel 2 with `duplicateOfPanelId: panel-1`, and kept the OCR worker at generation 1 with zero restarts. The evidence binds the result to SHA-256 hashes of the validator, pipeline, supervisor, and submitted files. Product names, filenames, and expected values do not participate in runtime selection or extraction.

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
| Oracle images reported clean that the oracle rejects (false clean) | 1 |
| Oracle images reported as a difference that the oracle passes (false reject) | 0 |
| Oracle images with the same disposition as the oracle | 6 of 42 |
| Oracle images routed to review | 35 of 42 |
| Beverage type exact | 68 of 70 |
| Brand name exact, or contained in a longer read | 53 exact and 8 contained of 70 |
| Class or type exact, contained, or partial | 54 exact, 5 contained, 1 partial of 67 |
| Alcohol content exact | 65 of 65 |
| Proof exact | 28 of 28 |
| Net contents exact | 64 of 64 |
| Producer exact, contained, or partial | 31 exact, 9 contained, 10 partial of 65 |
| Country of origin exact or contained | 9 exact and 2 contained of 19 |
| Warning located when present | 64 of 70 |
| Warning wording (labels whose wording is exact) | 22 confirmed, 36 routed to review, 0 rejected in error of 63 |
| Mean time per image | 4.06 s (median 3.91 s, p95 6.70 s, maximum 7.57 s, 53 over 5 s) |

The one false clean is `Test_TTB_Image_0031.jpg`, whose oracle row records a bold warning body;
visual inspection of the pixels shows the body in regular weight and the label compliant, so
the oracle row is disputed rather than the result. Every other oracle image that the machine
does not decide is routed to review, never reported clean; most review routings come from the
warning punctuation policy (a photograph cannot settle commas and periods) and from typography
that the stroke measurement could not call decisively. `Test_TTB_Image_0025.jpg` is scored as
exact wording even though its ground-truth row records the body in capital letters, because
27 CFR 16.22 fixes the case of the heading only.

Images that read wrongly or not at all are the known limitations: an embossed brand on a clear
bottle, the tiny warning on a curved side panel, a stylized can where the brand is decorative
type, and a heavily stylized graphic label; each is reported as review with the fields it
could not read marked as not verified.

151 photographs without ground truth were also processed, 145 of them the operator's store photographs (taken on a phone and normalized to 300 pixels per inch, mostly 2400 by 3200 or 4139 by 2778 pixels, 2 of them above the pixel limit and prepared the way the browser prepares them) and 6 earlier images outside the ground-truth set: 151 needs review. None was reported as a difference, and none as clean. Their timing on the development workstation was a 4.30-second mean, 4.09-second median, 6.81-second p95, and 7.57-second maximum, with 45 over 5 seconds. Dense back labels on curved glass carry thirty or more small lines, and their first recognition pass alone takes about five seconds; on those images the second, closer read is skipped under the time budget and the result says so, which is what keeps them inside the 9-second hard-case bound.

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

The completed security diff scan `b8501684-ed2e-4d83-8fe9-5775bc5f81d7` reviewed all 34 changed source and validation surfaces in its fixed integration range. Coverage was complete, no surface was deferred, and no plausible security finding remained after upload, decode, OCR supervision, history, rendering, export, and deployment-control traces.

## Release-bound checks

The frozen manifest, three independent RT decisions, final application commit, protected deployment, immutable image digest, live contract checks, and browser pre-UAT are recorded in `../10-release/FINAL_RT_SIGNOFF.md`, `../10-release/DEPLOYMENT_EVIDENCE.json`, and `evidence/live-browser-uat.json`.

## Public Azure deployment validation

The protected workflow deployed application commit `4a31e1a95cf6b2ec8dac5c8bc8f5763ffa7f3961` in GitHub Actions run `33815343738`, attempt 2. The deployed image digest is `sha256:c439dea1a608b4e1ba08d364eabee979d20a388c3a44fae2187c9da8dc208d9c`. Azure readback confirmed 4 vCPU, 8 GiB, and the zero-to-one replica contract. Public liveness, readiness, metadata, HSTS, and application checks passed. Three public sample analyses completed in 282.147, 302.252, and 294.255 milliseconds, for a 292.885-millisecond mean and 302.252-millisecond maximum. Each returned all 24 checks with no mismatches, an exact government-warning wording match, and physical warning size correctly marked Not verified from a photograph.

## Live-browser UAT execution

Engineering browser pre-UAT passed against the commit-bound Azure deployment. It covered the home and three beverage families, label-first two-panel analysis, all 24 checks, original-pixel evidence selection, warning inspection, Table, Cards, and Image first views, keyboard help, 500-record FIFO history, live batch progress, and grouping confirmation controls. The detailed result is `evidence/live-browser-uat.json`. Automated release tests cover folder admission, unsupported-file skipping, decoded-pixel guidance, failure isolation, retry, cancel, export, accessibility, and responsive behavior. Requester acceptance remains open.
