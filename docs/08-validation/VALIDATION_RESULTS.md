# Validation Results

Document ID: LV-VP-RESULT-001  
Execution date: 2026-09-02  
Status: Local release gates passed; immutable deployment verification follows commit

## Automated release gate

| Check | Result |
| --- | --- |
| Ruff | PASS, zero findings |
| Strict mypy | PASS, 36 source files |
| Pytest | PASS, 224 tests |
| ESLint | PASS, zero findings |
| TypeScript | PASS, zero errors |
| Vitest and Testing Library | PASS, 9 tests |
| Vite production build | PASS, 96 modules |
| Chrome primary workflow | PASS |
| Edge primary workflow | PASS |
| Chrome browser privacy matrix | PASS |
| Chrome 300-product capacity | PASS, 300 conservatively grouped products completed |

One third-party Starlette TestClient deprecation warning is non-blocking and does not occur in the production Uvicorn path.

## Product and image validation

The governed product corpus passed 30 of 30 cases, including 24 development cases and 6 sealed holdout cases. All 576 expected check rows were observed, all 8 mutation controls passed, and no false clean result occurred.

The governed 50-image diagnostic reported:

- 33 oracle PASS images and 17 oracle DO_NOT_PASS images
- 100 percent expected-defect containment
- zero false clearances
- zero false deterministic rejections
- 30 of 33 positive images meeting the evidence-recognition gate, or 90.909 percent
- all-image mean 3,358.920 ms
- 23 of 24 normal images within 5 seconds, or 95.833 percent
- all 13 difficult images within 9 seconds, with a maximum of 4,927.729 ms
- overall diagnostic result PASS

The diagnostic is intentionally conservative because the raw images do not contain independent COLA records, formula facts, chemistry, or trustworthy physical scale. Its detailed per-image report is `TEST_IMAGES_VALIDATION_REPORT.md`; raw images are not included in the public repository.

## Performance validation

The governed full-sample profile completed 30 warm runs with a p95 of 3,107.692 ms and a maximum of 4,006.515 ms. Five cold worker-readiness-through-first-result runs had a p95 and maximum of 6,846.503 ms, below the separate 10-second cold threshold. The 20-product sequential batch completed in 58.137 seconds with a 2,903.200 ms arithmetic mean and a 4,390.521 ms maximum. Every run returned the expected summary and all 24 checks. The warm, cold, and batch performance gates passed.

## Security and dependency validation

The security review covered the public HTTP boundary, uploads, image decoding, worker lifecycle, history, browser resources, exports, container, deployment workflow, and dependency acquisition. The final source and regression evidence verifies:

- opaque HttpOnly browser-scope authorization on every history operation;
- an 8 KiB streamed JSON limit on history mutations;
- exact production Origin enforcement for state changes;
- per-client minute rate fairness below the global allowance;
- formula-safe CSV cells;
- lifecycle-managed and lazily loaded batch preview URLs;
- bounded upload, decoded-pixel, timeout, worker, and capacity controls;
- non-root container execution and pinned GitHub Actions;
- no content logging or runtime cloud inference.

No critical or high security finding remains unresolved. Python and production npm dependency audits reported zero known vulnerabilities on the execution date.

## Integrated interface validation

The Fable interface was exercised against the real local API and OCR worker. The built-in two-panel distilled-spirits sample completed in 4.0 seconds. The reviewer could inspect the 24 checks, select brand evidence and see `OLD TOM DISTILLERY` on the original image, open the exact-warning view, save an Approve disposition without changing machine findings, and reopen the result, source panels, note, checks, and evidence from History.

## Remaining release-bound checks

Three independent RT reviewers inspect the frozen candidate for requirements fidelity, architecture and security, and delivery and UAT readiness. The exact reviewed content is recorded in the release manifest and RT signoff. After the commit is pushed, the deployment workflow must prove the same commit and immutable image digest are live before requester UAT begins.
