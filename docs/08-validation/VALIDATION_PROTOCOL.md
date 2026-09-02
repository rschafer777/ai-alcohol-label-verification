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
| VP-12 Governed 50 images | Verify inventory and oracle, run local diagnostic, report every file | Complete evidence, zero false clearances, zero false deterministic rejections, 100 percent expected-defect containment, and usable positive evidence on at least 90 percent of oracle-pass images |
| VP-13 Performance | Warm normal, difficult, cold, and sequential batch runs | All declared latency bands pass; a miss blocks release until corrected or explicitly accepted by the product owner |
| VP-14 Security | Static security scan, dependency audit, history isolation, body bounds, CSV neutralization, rate fairness, abuse cases, container and workflow review | No unresolved critical or high release finding |
| VP-15 Documentation | Trace every INT and FR item, scan claims and paths | Complete and current |
| VP-16 Independent RT | Three frozen-baseline reviews | Three Clear decisions |
| VP-17 Public deployment | Build exact commit, digest deploy, metadata and live UI smoke | Exact SHA and 24-check profile live |

## Execution commands

`scripts/check.ps1` runs static analysis, typed checks, unit and integration tests, frontend tests, the production build, browser tests, and the tracked-source Unicode dash scan. `scripts/release-check.ps1` runs that code-quality gate and then executes the governed product corpus, warm and cold OCR performance, a 20-product sequential batch, the governed 50-image diagnostic when its local images are installed, Python and production npm dependency audits, and exact Git-index release-manifest verification. The Azure workflow repeats the source gates and binds deployment evidence to the commit and immutable container digest.

## 50-image interpretation

The visual oracle answers whether a human reviewer identified a visible image-supported defect. The local diagnostic measures file admission, decode, preprocessing, OCR, candidate presence, and warning evidence. The corpus has no independent COLA data, formula data, chemistry, or reliable physical scale. Therefore the diagnostic must report three distinct facts:

1. Oracle disposition: the independent expected visual decision.
2. Machine disposition: what the partial image diagnostic produced.
3. Comparison: true defect, conservative hold, conservative non-clear, false clear, or false deterministic rejection.
4. Positive evidence effectiveness: at least four core candidates plus warning heading and body are detected on at least 90 percent of oracle-pass images.

The raw corpus is not published because public redistribution rights were not established. Hash-governed oracle and non-sensitive result evidence may be published.

## Performance protocol

- Preload governed models before warm measurements.
- Report each case, arithmetic mean, p95 where sample size permits, maximum, and target achievement.
- Normal readable target is about 5 seconds. At least 75 percent of the selected normal sample must complete within 5 seconds and the full-corpus arithmetic mean must be no more than 5 seconds.
- Difficult recoverable target is no more than 9 seconds per selected case.
- Sequential warm batch target is about 5 seconds mean per product.
- Cold readiness and first request are reported separately.
- A partial image harness is never presented as browser round-trip or production API timing.

## Defect loop

Any failure is assigned to requirements, contract, backend, frontend, data, test, documentation, deployment, or environment. The owner corrects the cause, adds or updates regression coverage, reruns the affected gate, then reruns the full gate. Expected results are not changed to match code unless the source requirement or independent oracle is demonstrably wrong and the reason is recorded.

## UAT entry rule

UAT begins when VP-01 through VP-17 are complete or a non-blocking limitation is explicitly listed in the release record. UAT is performed against the public commit-bound deployment and repeats the core single, evidence, beverage, warning, batch, history, keyboard, and error flows.
