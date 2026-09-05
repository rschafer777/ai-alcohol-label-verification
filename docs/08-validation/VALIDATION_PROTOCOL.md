# Validation Protocol

Document ID: LV-VP-001  
Status: Active CR-002 corrective release protocol

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-01 | Initial integrated release gates | LV-FRD-001 revision 1.0 |
| 1.1 | 2026-09-04 | Added cause attribution, correction integrity, numeric and producer truth, model bakeoff, and representative Azure gates | CR-002 |
| 1.2 | 2026-09-04 | Added final-review integrity regressions and canonical staged-source evidence binding | CR-002 |
| 1.3 | 2026-09-05 | Separated the time-boxed demo-UAT deployment gate from production-scale Azure load qualification | Product-owner release direction |

## Purpose

This protocol determines whether the delivered application matches the Intake, BAIRD, I2R, FRD, and Build Instructions. It tests behavior, safety, performance, deployment, and documentation without substituting a mock or visual design for working integration.

## Gates

| Gate | Procedure | Pass rule |
| --- | --- | --- |
| VP-01 Contract integrity | Load registries, verify hashes, compare generated TypeScript and deployment assertions | Exact agreement |
| VP-02 Backend static quality | Ruff and strict mypy | Zero errors |
| VP-03 Backend behavior | Pytest backend and validation suites | All tests pass |
| VP-04 Frontend static quality | ESLint and TypeScript | Zero errors |
| VP-05 Frontend behavior | Vitest and Testing Library | All tests pass |
| VP-06 Production build | Vite production build | Successful artifact |
| VP-07 Browser and accessibility | Playwright flows, keyboard, responsive, automated accessibility | All blocking assertions pass |
| VP-08 Beverage profiles | Beer or malt, wine, spirits, unknown, conflict, and rule activation | Expected 24-row outcomes |
| VP-09 History | Create, browse, filter, update, reopen evidence, delete, scope isolation, bounded mutation, FIFO 501, injected rollback during deletion, and startup orphan reconciliation | All expected operations pass; rollback cannot leave a retained record without its image and post-commit cleanup remains recoverable |
| VP-10 Batch | Group, confirm, process, isolate failure, retry, cancel, export, 300-product capacity | All expected operations pass |
| VP-11 Image and OCR | Valid formats, bad signatures, orientation, recovery, evidence inversion, unknown content | No false deterministic clearance |
| VP-12 Private UAT image corpus | Normalize non-destructively, skip non-images, run every current image through the production multipart API, group without a manifest, rerun every suggested product, and report every file | Every supported image returns a valid result, every result has 24 checks and valid evidence references, every successful image appears in exactly one group, and no group exceeds three images |
| VP-13 Image oracle and pixel ground truth | Process every current image, compare the 42 covered images with the disposition oracle (`test-oracle-v1.json`), and score the 70 covered images against the field-level pixel ground truth (`pixel-ground-truth-v1.json`) using `scripts/score_ground_truth.py` | Field accuracy, warning-wording outcomes, false-clean and false-reject counts, coverage, and timing are reported per run; the evaluation files are never read by the runtime; a TTB reviewer determination remains a requester UAT item |
| VP-14 Performance | Warm normal, difficult, cold, equivalent cross-format multi-panel, individual private images, grouped products, and sequential batch runs | All declared latency bands pass; a multi-panel request must complete without a worker-generation restart; a miss blocks release until corrected or explicitly accepted by the product owner |
| VP-15 Azure resource contract | Effective Container Apps template and post-deployment readback | One Consumption replica is allocated 4 vCPU and 8 GiB; any lower or different allocation blocks release |
| VP-16 Security | Static security scan, dependency audit, history isolation, body bounds, CSV neutralization, rate fairness, abuse cases, container and workflow review | No unresolved critical or high release finding |
| VP-17 Documentation | Trace every INT and FR item, scan claims and paths | Complete and current |
| VP-18 Independent RT | Three frozen-baseline reviews | Three Clear decisions |
| VP-19 Public deployment | Build exact commit, digest deploy, metadata and live UI smoke | Exact SHA and 24-check profile live |
| VP-20 Review-cause baseline | Report every blocking check and normalized cause for the 221-image baseline; classify processing, routing, field accuracy, and disposition accuracy separately | Counts reconcile exactly to each result and no routing percentage is labelled as accuracy |
| VP-21 Corrective truth | Validate annotated numeric positives and negatives, all producer miss or wrong cases, a sealed product-separated 24-product holdout, and 30 to 50 unique difficult text regions | Independent annotations are hash-governed, unavailable to runtime logic, and complete; the holdout records one exact normalized score per product and eligible field family, while regions are diagnostic only |
| VP-22 Revision lineage and correction | Correct every allowlisted field with verbatim statements plus multiple fields; exercise OCR evidence and reviewer-drawn original-pixel regions; immutable source image hash, panel, polygon, and retained original snippet; two corrections to one field followed by add-panel replay; server parsing of abbreviations, precision, ranges, units, positive sulfite wording, and producer blocks; reject typed sulfite absence; every FR-053 dependency including class-driven type inference and an ABV-only correction that reruns proof relation, same-field-of-vision placement, and visual distinction or adjacency; closed-set beverage selection; unresolved-type correction and add-panel behavior; resolved-to-unresolved transition under fresh conflicting label evidence; reviewer-corrected family followed by class correction; fresh label-derived baseline merge with explicit provenance for every field including malt alcohol source; resolved and unresolved mixed field provenance with response-to-history value-source comparison; strictly in-bounds positive-area manual polygons; fresh add-panel timing and limitations; race add-panel and correction; revision 10 and attempted 11; third and attempted fourth panel; missing evidence; prohibited fields; stale versions; invalid normalized-only payloads; oversized body and wrong Origin using valid and invalid history IDs; mutation rate; FIFO; deletion rollback; and cross-scope access while instrumenting image and OCR calls | Zero image or OCR calls for correction; raw, verbatim, and derived forms preserved with field provenance; latest immutable locator replayed; every returned revision value agrees with its declared source and persisted reference; fresh label-derived type may resolve or unresolve while reviewer-corrected type remains authoritative; invalid boundary or zero-area polygons are rejected; sulfite absence and printed defects not cleared by typed normalization; immutable self-contained revisions; child Pending; fresh add-panel baseline and telemetry; one atomic shared head; complete recomputation; bounded metadata and registered errors; unchanged FIFO age; whole-lineage deletion; no bearer disclosure; abuse paths rejected safely |
| VP-23 Deterministic corrections | Exercise neutral image roles, reversed order, numeric brands, presentation, sulfite applicability, import status, producer blocks, warning recovery, independent warning rows, and all-Match summary wording | Expected paired outcomes, measured FR-054 utility or an approved evidence-backed variance, no product-specific or upload-order behavior, zero lost correct protected fields, zero new false clean, and no protected-field regression |
| VP-24 OCR bakeoff | Compare current PP-OCRv4 and PP-OCRv5 with the same detector model and configuration, preprocessing, rules, hardware, and cases; require frozen-box replay before any promotion and test a detector only if region truth proves misses | Five net sealed-holdout product-field gains across at least two eligible families and every FR-061 gate pass, or the current model is retained with a recorded no-change decision; a candidate that already fails protected-field gates may be rejected before box replay when that limitation is explicit |
| VP-25 Demo deployed performance | Bind the local 221-image, grouped-product, 20-product timing, and 300-product browser-capacity evidence to an exact-build Azure deployment; run public workflow checks plus distinct difficult malt, wine, and spirits smoke inputs on the governed revision | Local mean no more than 5 seconds, local difficult maximum below 9 seconds, 20-product wall time no more than 100 seconds, 300-product browser capacity succeeds, Azure returns the exact build and 24-check profile, every selected Azure difficult product stays below 9 seconds, and no restart, timeout, drop, or memory failure occurs; a 30-product or 300-product distinct Azure load campaign and a 100-fingerprint deployed p95 remain pre-production operational qualification, not demo-UAT entry |
| VP-26 Corrective change control | Reconcile CR-002, lifecycle revisions, implementation record, results, QA/QC, release notes, canonical staged-source hashes, manifest, and three identical-snapshot independent reviews | Every corrective requirement is implemented or explicitly accepted, every evidence source hash matches the staged LF bytes, and all three reviews return Clear |

## Execution commands

`scripts/check.ps1` runs static analysis, typed checks, unit and integration tests, frontend tests, the production build, browser tests, and the tracked-source Unicode dash scan. `scripts/release-check.ps1` runs that code-quality gate and then executes the governed product corpus, warm and cold OCR performance, a 20-product sequential batch, the private current-image API and grouping corpus when at least 50 local images are installed, Python and production npm dependency audits, and exact Git-index release-manifest verification. The Azure workflow repeats the source gates and binds deployment evidence to the commit and immutable container digest.

## Private-image interpretation

The current private corpus measures file admission, decode, preprocessing, OCR, candidate presence, warning evidence, 24-check aggregation, server grouping, grouped-product reruns, and latency through the production API. The corpus has no independent COLA data, formula data, chemistry, or reliable physical scale. Its prior visual oracle also does not cover the complete current inventory. Therefore the evidence reports these distinct facts:

1. Technical processing: whether every supported image and grouped product completes through the production API with valid contracts and evidence.
2. Machine finding: the conservative result produced from label-derived evidence.
3. Oracle coverage: the count of current filenames with an independent expected result and the exact coverage gaps.
4. Accuracy status: field-level or legal-label accuracy is not claimed until a complete current oracle and requester review exist.

The raw corpus is not published because public redistribution rights were not established. Hash-governed oracle and non-sensitive result evidence may be published.

## Performance protocol

- Preload governed models before warm measurements.
- Report each case or product fingerprint, arithmetic mean, p95 where sample size permits, maximum, and target achievement. Publish beverage-family, panel-count, normal-versus-difficult, and admitted-dimension distributions.
- Normal readable target is about 5 seconds. At least 75 percent of the selected normal sample must complete within 5 seconds and the full-corpus arithmetic mean must be no more than 5 seconds.
- Difficult recoverable target is no more than 9 seconds per selected case.
- Sequential warm active-processing target is about 5 seconds mean per product. Total wall time includes queueing, retry, capacity, and rate-limit waits and must remain within 100 seconds for 20 products and 1,500 seconds for 300 products.
- Cold scale-to-zero activation is measured from request start through readiness and first result, reported separately, and excluded from the post-ready 5-second and 9-second bands.
- Equivalent cross-format panels are tested as one product. The request must preserve every submitted panel, mark the duplicate relationship, finish within the difficult-image band, and leave the worker generation unchanged.
- A partial image harness is never presented as browser round-trip or production API timing.
- Formal representative products have distinct admitted pixel hashes. Repeated images, re-encodings, metadata-only changes, cache-busted duplicates, warm caches, and governed samples are reported as smoke, cache, queue, or diagnostic evidence, not representative latency.
- A production-scale Azure performance claim requires a separate 30-distinct-product quick gate and at least 100 distinct product request fingerprints for a formal deployed p95. Repeated images can test queue capacity but cannot establish representative latency. The demo release makes no such production-scale claim.
- Stage timings report detection, recognition, recovery-skip, candidates, rules, persistence, and total request duration sufficiently to explain a regression.

## Defect loop

Any failure is assigned to requirements, contract, backend, frontend, data, test, documentation, deployment, or environment. The owner corrects the cause, adds or updates regression coverage, reruns the affected gate, then reruns the full gate. Expected results are not changed to match code unless the source requirement or independent oracle is demonstrably wrong and the reason is recorded.

## UAT entry rule

Requester UAT for CR-002 begins when VP-01 through VP-26 and the corrective deployment are complete. The 221-image technical-processing claim means every admitted image completed; it is not an accuracy claim. Field-accuracy claims remain limited to independently annotated cases. UAT is performed against the public commit-bound deployment and repeats the core single, evidence, beverage, warning, correction, batch, history, keyboard, error, difficult-image, and provenance flows.
