# Build Instructions

Document ID: LV-BI-001  
Inputs: LV-I2R-001 and LV-FRD-001  
Status: Approved execution baseline

## Delivery sequence

| Work package | Scope | Required evidence |
| --- | --- | --- |
| WP-01 Contracts | API schema, rule registry, 24-check registry, errors, generated TypeScript | Integrity hashes and contract tests |
| WP-02 Image ingress | Multipart limits, signatures, pixel limits, decode, orientation, recovery views | Boundary and imaging tests |
| WP-03 OCR and candidates | Local RapidOCR, bounded exact-pixel result reuse, strict equivalent-panel deduplication, field extraction, alternatives, provenance, coordinate inversion | OCR, cache, deduplication, candidate, and evidence tests |
| WP-04 Regulatory engine | Beverage inference, common rules, family rules, warning rules, aggregation | Unit, mutation, and beverage-profile tests |
| WP-05 Orchestration | One-pass analysis, independent verification, supervised execution, cancellation and timeout | Pipeline, supervisor, and API tests |
| WP-06 Persistence | SQLite schema, image store, browser-scope authorization, FIFO 500, disposition, delete, reopen | Repository and API isolation tests |
| WP-07 Frontend shell | Approved TTB visual system, two entry doors, navigation, responsive and accessibility behavior | Component, accessibility, and browser tests |
| WP-08 Review | Evidence viewer, 24 checks, warning detail, disposition, keyboard use | Component and live browser evidence |
| WP-09 Batch | Mixed-folder filtering, per-image reads, server grouping, confirmation, queue, live count, rate, ETA, retry, cancel, CSV and JSON | Unit, full-corpus API, capacity, and browser tests |
| WP-10 History | Filter, paging, detail, retained images, evidence, disposition, delete | Component and browser tests |
| WP-11 Packaging | Build, non-root container, local run, Azure template and OIDC workflow | Container and deployment contract tests |
| WP-12 Verification | Full regression, governed visual-oracle diagnostic, complete private-corpus individual and grouped-product API run, performance, security, RT, UAT | Versioned reports and release record |

## Agent and team ownership model

- Product and requirements owner controls Intake, BAIRD, scope, and acceptance.
- Architecture owner controls interfaces, data flow, rule boundaries, and nonfunctional decisions.
- Backend owner implements ingress, OCR orchestration, rules, storage, and APIs.
- Frontend owner implements the approved experience against the generated contract.
- Verification owner maintains independent oracles, tests, performance evidence, accessibility review, and defect ledger.
- Release owner verifies public contents, provenance, Git state, deployment controls, and live smoke results.
- Three independent red-team reviewers inspect requirements fidelity, architecture/security, and UX/delivery before release.

One contributor may hold multiple roles for this take-home project, but evidence and review criteria remain separated.

## Engineering rules

- Python modules and files use lowercase snake_case; classes use PascalCase; functions and variables use snake_case.
- TypeScript components use PascalCase; functions and values use camelCase; tests describe user-observable behavior.
- Public JSON uses camelCase. Stable IDs use lowercase snake_case and must not be repurposed.
- API and registry changes update machine contracts, hashes, generated frontend values, tests, traceability, and release notes in one change.
- OCR observation occurs before independent-reference comparison.
- Rule code is deterministic and side-effect free. Persistence and transport do not decide compliance states.
- Errors contain no uploaded text, paths, stack traces, credentials, or internal host detail.
- Code comments explain why a non-obvious safety or regulatory decision exists, not what ordinary syntax does.
- Public documentation uses relative repository paths, current facts, and reproducible commands.
- Source and documentation contain no prohibited Unicode dash characters.

## Test strategy

1. Unit tests cover normalization, candidates, classification, warning logic, comparisons, storage, and grouping.
2. Contract tests prove backend, frontend, error, check, and deployment agreement.
3. Integration tests exercise API uploads, analysis, verification, history, sample, and public errors.
4. Browser tests cover home, intake, processing, result, keyboard, batch capacity, history, error states, responsive layout, and accessibility.
5. Fixture tests use synthetic development and sealed holdout cases with independent expected outcomes.
6. Every supported image installed in the private UAT folder is exercised individually through the production API, grouped without product-specific runtime overrides, and exercised again by product group.
7. The governed subset is evaluated against its independent visual oracle without publishing raw images. New images without oracle entries remain technical UAT coverage until independently classified.
8. Performance tests report cold, warm, difficult-image, individual-corpus, grouped-product, and batch behavior without hiding outliers.
9. Multi-panel performance includes equivalent cross-format inputs and proves completion within the worker limit without a worker-generation restart.
10. Security validation covers source, dependencies, upload and JSON abuse, history isolation, CSV neutralization, rate fairness, timeouts, cleanup, identity, headers, container, and deployment.
11. Three RT reviews run only after the code and documents are frozen by manifest.
12. Requester UAT begins only after automated and independent gates are complete.

## Definition of Done

- All INT and FR requirements are implemented or represented by an explicit, accepted limitation.
- The frontend, API, middleware, rule engine, and persistence use the same contracts.
- Beer or malt beverage, wine, and distilled spirits paths are tested.
- One product supports 1 to 3 images and batch supports up to 300 confirmed products and 900 images.
- A mixed folder cannot be blocked by an unrelated file; selection and processing status expose accepted, skipped, completed, rate, and ETA values.
- History retains at most 500 records with usable evidence images.
- All 24 rows are returned in order and uncertainty cannot become a false deterministic clearance.
- Lint, strict types, unit, integration, frontend, browser, and deployment-contract tests pass.
- Performance evidence is reported against the 5-second and 9-second targets.
- The worker safety timeout is verified independently from the performance targets.
- Security scan has no unresolved release-blocking finding.
- README contains accurate setup, run, test, architecture, tools, assumptions, trade-offs, and limitations.
- Public staging scan finds no secret, credential, personal detail, machine path, raw unlicensed image, local agent instruction, cache, report scratch, or oversized file.
- Three RT reviewers return Clear after verified findings are closed.
- The exact commit is pushed to main, deployed by immutable digest, and smoke-tested at the public URL.
- UAT instructions and expected results are available to the requester.

## Local build commands

```powershell
uv sync --frozen --link-mode copy
uv run python ops/fetch_models.py models

Push-Location frontend
npm ci
npm run build
Pop-Location

uv run uvicorn labelverify.api.app:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

Open `http://127.0.0.1:8000`.

## Full gate

```powershell
./scripts/release-check.ps1
```

`scripts/check.ps1` remains the faster code-quality subset used during implementation. The release owner records the exact command results, commit, runtime build identity, and deployment evidence. A failed gate returns to the owning work package and the complete release gate is rerun after the fix.
