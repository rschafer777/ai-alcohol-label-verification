# Validation Protocol

Document ID: LV-VP-001  
Status: Active release protocol

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
| VP-09 History | Create, browse, filter, update, reopen evidence, delete, scope isolation, bounded mutation, FIFO 501 | All expected operations pass |
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
- Report each case, arithmetic mean, p95 where sample size permits, maximum, and target achievement.
- Normal readable target is about 5 seconds. At least 75 percent of the selected normal sample must complete within 5 seconds and the full-corpus arithmetic mean must be no more than 5 seconds.
- Difficult recoverable target is no more than 9 seconds per selected case.
- Sequential warm batch target is about 5 seconds mean per product.
- Cold readiness and first request are reported separately.
- Equivalent cross-format panels are tested as one product. The request must preserve every submitted panel, mark the duplicate relationship, finish within the difficult-image band, and leave the worker generation unchanged.
- A partial image harness is never presented as browser round-trip or production API timing.

## Defect loop

Any failure is assigned to requirements, contract, backend, frontend, data, test, documentation, deployment, or environment. The owner corrects the cause, adds or updates regression coverage, reruns the affected gate, then reruns the full gate. Expected results are not changed to match code unless the source requirement or independent oracle is demonstrably wrong and the reason is recorded.

## UAT entry rule

Requester UAT begins when the engineering gates and VP-19 deployment are complete. The 76-image technical-processing claim is supported because every admitted image completed. Field-accuracy claims are limited to the 70 images with human ground truth; a complete oracle is required before extending those rates to all 76 images. UAT is performed against the public commit-bound deployment and repeats the core single, evidence, beverage, warning, batch, history, keyboard, error, and difficult-image flows.
