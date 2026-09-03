# Validation Results

Document ID: LV-VP-RESULT-001  
Execution date: 2026-09-03  
Status: Engineering, independent RT, and immutable Azure deployment gates passed; requester UAT pending

## Automated code and interface gates

| Check | Result |
| --- | --- |
| Ruff | PASS, zero findings |
| Strict mypy | PASS, source package |
| Pytest | PASS, 262 tests |
| ESLint | PASS, zero findings |
| TypeScript | PASS, zero errors |
| Vitest and Testing Library | PASS, 24 tests in 5 files |
| Vite production build | PASS, 129 modules |
| Browser and accessibility workflows | PASS |

One third-party Starlette TestClient deprecation warning is non-blocking and does not occur in the production Uvicorn path.

## Governed product validation

The governed product corpus passed 30 of 30 cases, including 24 development cases and 6 sealed holdout cases. All 576 expected check rows were observed, all 8 mutation controls passed, and no false clean result occurred. The corpus covers malt beverages, wine, distilled spirits, unknown type, conflicting evidence, warning defects, reference comparison, and degraded-image review paths.

## Private current-image API and batch validation

The private UAT folder contained 71 selected files. The browser and server admission rule accepted 70 JPEG or PNG images and skipped the JSON oracle without failing the selection. The production multipart API then produced:

- 70 of 70 successful individual image analyses
- 24 ordered checks and valid original-pixel evidence references in every successful result
- 50 server-suggested product groups
- 36 groups ready to confirm and 14 groups requiring confirmation review
- no group above the three-image product limit
- 50 of 50 successful grouped-product analyses
- no filename, product-name, or expected-value override in the runtime or validator

Individual analysis averaged 3.559 seconds, with a 3.378-second median, 5.943-second p95, and 6.449-second maximum. Grouped-product reruns averaged 0.546 seconds, with a 0.469-second median, 0.892-second p95, and 1.359-second maximum. The 5-second arithmetic-mean target and 9-second hard-case ceiling both passed.

The detailed per-file report is `PRIVATE_UAT_CORPUS_REPORT.md`, and machine-readable evidence is `evidence/private-uat-corpus-e2e.json`. Raw images are excluded from the public repository because public redistribution rights were not established.

## Difficult-image validation scenarios

The current difficult-image cases were exercised through the production multipart API to verify generic OCR and inference behavior:

| Product | Observed result |
| --- | --- |
| Jack Daniel's front and back | Distilled spirits, `JACK DANIEL'S`, `WHISKEY`, 40 percent ABV, 80 proof, 375 mL, and producer/location read |
| Organic Vodka front and back | Distilled spirits, `OrganicVodka`, neutral spirits, 40 percent ABV, 80 proof, 750 mL, and Hawaii producer/location read; country correctly remains not applicable for a domestic address |
| Cascade Light | Wine, `CASCADE LIGHT`, `RIESLING`, 11.5 percent ABV, 750 mL, producer/location, appellation, and sulfite evidence read |
| Peak Farm | Malt beverage, `PEAK FARM`, `DOUBLE PALE ALE`, 7.2 percent ABV, 16 fl oz, and producer/address read |
| Blood & Honey | Malt beverage, `BLOOD & HONEY`, `TEXAS STYLE ALE`, and producer/location read; the supplied image does not visibly include a reliable ABV or net-contents statement |

The machine-readable private-corpus evidence records a content-only cross-format equivalence test. The first analysis request after fresh application readiness returned HTTP 200 in 6.015 seconds, retained both submitted panel records, marked panel 2 with `duplicateOfPanelId: panel-1`, and kept the OCR worker at generation 1 with zero restarts. The evidence binds the result to SHA-256 hashes of the validator, pipeline, supervisor, and submitted files. Product names, filenames, and expected values do not participate in runtime selection or extraction.

The processing behavior uses generic OCR layout, semantic-noise exclusion, token-boundary beverage inference, and context ranking. Production logic contains no list of these products and does not read expected values from filenames or test manifests.

## Accuracy boundary

The private API gate proves processing, contract, evidence, grouping, and timing behavior. It does not prove that every OCR field is semantically correct or that a label is legally compliant. The local visual oracle contains 50 cases, but only 42 exact filenames remain in the current 70-image folder. Twenty-eight current images have no oracle row, and eight oracle filenames are absent. A complete current-corpus human oracle is required before claiming 70-image field-level or legal-label accuracy.

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

## Release-bound checks

Three independent RT reviewers returned Clear decisions for requirements fidelity, architecture and security, and delivery and UAT readiness against the same 346-entry frozen manifest. The release manifest SHA-256 is `6C3E824D9E2B174B20A65DD650FAD23EE03B9EF1F3113BC2D70EC91BAB01AD57`.

## Public Azure deployment validation

GitHub Actions run `33746505754` validated and deployed application commit `6863ea8eaa4074ba209cc273f79db19f84917641`. The immutable image digest is `sha256:9ab566a7a604dd558c8aefbe19af75edddc4b57165054a200b6a3698b6d8fd41`. GitHub deployment `6242353833` reports success for environment `demo`. The rollback job was not invoked.

The workflow read back 4 vCPU and 8 GiB before public verification. The live service returned HTTPS 200, liveness true, readiness true at worker generation 1, exact build metadata, profile `all_beverages_demo_v2`, RapidOCR 3.4.2, 24 selected checks, three panels per product, and a 500-record history cap. Its protected sample gate required three complete public results with a server-duration mean below 5 seconds and maximum below 9 seconds, and passed.

Nine additional fresh difficult-image analyses were then submitted through the public production-mode demo API with the required Origin control. Every request returned HTTP 200, 24 checks, and the correct beverage family. Server duration averaged 7.148 seconds and never exceeded 8.752 seconds.

| Public case | Type | Core extraction | Server duration |
| --- | --- | --- | --- |
| Tuscan wine | Wine | `Tuscan`, `Sangiovese`, 13.5 percent, 750 mL | 8.093 seconds |
| Valle di Pietra wine | Wine | `VALLE DI PIETRA`, `Sangiovese`, 13.5 percent, 750 mL | 7.019 seconds |
| Northveil Vodka | Distilled spirits | `NORTHVEIL`, `VODKA`, 40 percent, 80 proof, 750 mL | 7.623 seconds |
| Jack Daniel's, two panels | Distilled spirits | `JACK DANIEL'S`, `WHISKEY`, 40 percent, 80 proof, 375 mL, producer/location | 5.973 seconds |
| Organic Vodka, two panels | Distilled spirits | `OrganicVodka`, neutral spirits, 40 percent, 80 proof, 750 mL, Hawaii producer/location | 6.474 seconds |
| Cascade Light | Wine | `CASCADE LIGHT`, `RIESLING`, 11.5 percent, 750 mL, producer/location | 8.752 seconds |
| Peak Farm | Malt beverage | `PEAK FARM`, `DOUBLE PALE ALE`, 7.2 percent, 16 fl oz, producer/address | 6.388 seconds |
| Blood & Honey equivalent pair | Malt beverage | `BLOOD & HONEY`, `TEXAS STYLE ALE`; both panels retained with one duplicate link | 7.428 seconds |
| XXL, two panels | Wine | `STRAWBERRY`, grape wine with natural flavor, 16 percent, 750 mL | 6.586 seconds |

Missing or unreadable source fields remain Review or Not verified. Domestic Hawaii and Tennessee addresses correctly do not create a foreign country-of-origin value. These public checks prove technical processing and the recorded extraction results, not final legal compliance or agreement with an independent COLA application.
