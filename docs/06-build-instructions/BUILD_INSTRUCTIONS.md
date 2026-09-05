# Build Instructions

Document ID: LV-BI-001  
Inputs: LV-I2R-001 and LV-FRD-001  
Status: CR-002 build executed; final release and deployment gates in progress

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-01 | Initial work packages and release Definition of Done | LV-FRD-001 revision 1.0 |
| 1.1 | 2026-09-04 | Added corrective measurement, provenance, extraction, model-evaluation, deployed-performance, and change-control work packages | CR-002 |
| 1.2 | 2026-09-04 | Recorded completed implementation packages and remaining commit-bound deployment gates | CR-002 |
| 1.3 | 2026-09-04 | Added final-review integrity closures to the revision, persistence, security, and release-evidence work | CR-002 |
| 1.4 | 2026-09-05 | Separated demo-UAT live smoke from pre-production production-scale Azure load qualification | Product-owner release direction |

## Delivery sequence

| Work package | Scope | Required evidence |
| --- | --- | --- |
| WP-01 Contracts | API schema, rule registry, 24-check registry, errors, generated TypeScript | Integrity hashes and contract tests |
| WP-02 Image ingress | Browser-side proportional preparation, multipart limits, signatures, pixel limits, decode, orientation, recovery views | Boundary, browser preparation, and imaging tests |
| WP-03 OCR and candidates | Local RapidOCR, bounded exact-pixel result reuse, strict equivalent-panel deduplication, field extraction, alternatives, provenance, coordinate inversion | OCR, cache, deduplication, candidate, and evidence tests |
| WP-04 Regulatory engine | Beverage inference, common rules, family rules, panel-scoped warning reads, conservative cross-image warning aggregation | Unit, mutation, multi-panel warning, and beverage-profile tests |
| WP-05 Orchestration | One-pass analysis, independent verification, supervised execution, cancellation and timeout | Pipeline, supervisor, and API tests |
| WP-06 Persistence | SQLite schema, image store, browser-scope authorization, FIFO 500, disposition, delete, reopen | Repository and API isolation tests |
| WP-07 Frontend shell | Approved TTB visual system, two entry doors, navigation, responsive and accessibility behavior | Component, accessibility, and browser tests |
| WP-08 Review | Evidence viewer, 24 checks, warning detail, disposition, keyboard use | Component and live browser evidence |
| WP-09 Batch | Mixed-folder filtering, per-image reads, server grouping, confirmation, queue, live count, rate, ETA, retry, cancel, CSV and JSON | Unit, full-corpus API, capacity, and browser tests |
| WP-10 History | Filter, paging, detail, retained images, evidence, disposition, delete | Component and browser tests |
| WP-11 Packaging | Build, non-root container, local run, Azure template and OIDC workflow | Container and deployment contract tests |
| WP-12 Verification | Full regression, governed visual-oracle diagnostic, complete private-corpus individual and grouped-product API run, performance, security, RT, UAT | Versioned reports and release record |
| WP-13 Corrective baseline | Review-cause attribution, annotated numeric cases, producer failure taxonomy, product-separated holdout, difficult-region truth | Frozen baseline report, hashes, and annotation checks |
| WP-14 Revision lineages | Field-level provenance contract, verbatim statement correction union with server-derived normalized forms, latest-event source-image, panel and polygon replay locator, self-contained observation snapshot, atomic shared head for corrections and add-panel reprocessing, unresolved-type preservation, class-driven family inference, positive-only sulfite transcription, fresh label-derived add-panel baseline and telemetry, 10-revision cap, commit-consistent complete-lineage retention and deletion, Pending child disposition, and explicit dependency re-evaluation without OCR for corrections | Contract, mixed-provenance presentation, raw-versus-derived audit, latest immutable-locator replay, reviewer-drawn region, controlled beverage selector, class inference, abbreviation, precision, range, unit, sulfite false-clear, producer, proof-placement, fresh-reference merge, repository rollback, API, metadata, same-origin invalid-ID, body-limit, mutation-rate, dependency, scope, concurrency, add-panel, revision-limit, FIFO, lineage-deletion, actor-nondisclosure, and zero-OCR tests |
| WP-15 Cause-routed OCR bakeoff | For producer or warning failures classified as recognition-caused by WP-13, compare PP-OCRv4 and PP-OCRv5 with the same detector model, configuration, preprocessing, rules, inputs, and hardware; if a candidate clears the preliminary gates, replay identical frozen detector boxes before promotion; analyze detector misses separately and record the governed promotion or retention decision | Model comparison report, sealed-holdout product-field wins and losses, diagnostic regions, safety regression, integrity, license, SBOM, offline, resource, and Azure evidence |
| WP-16 Deterministic corrective logic | Neutral image names, numeric-brand path, presentation and applicability calibration, warning-specific recovery, and producer joining, selection, or vocabulary changes only for failures proven to occur after recognition or after the WP-15 model decision | Unit, mutation, order-invariance, correction-utility, field, warning, and browser tests |
| WP-17 Corrective release | Representative unique-image local and Azure performance, final regression, documentation reconciliation, manifest, independent reviews, deployment, and UAT handoff | Corrective validation results, deployment evidence, Clear decisions, and signed requester UAT entry |

## Delivery roles and ownership model

- Product and requirements owner controls Intake, BAIRD, scope, and acceptance.
- Architecture owner controls interfaces, data flow, rule boundaries, and nonfunctional decisions.
- Backend owner implements ingress, OCR orchestration, rules, storage, and APIs.
- Frontend owner implements the approved experience against the generated contract.
- Verification owner maintains independent oracles, tests, performance evidence, accessibility review, and defect ledger.
- Release owner verifies public contents, provenance, Git state, deployment controls, and live smoke results.
- Three independent reviewers inspect requirements fidelity, architecture and security, and UX and delivery before release.

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
- Public source and documentation contain no references to specific AI assistants or informal implementation transcripts.
- Corrective field, rule, and model changes are measured separately. A combined change cannot be promoted when its individual effect is unknown.
- Machine Match, reviewer disposition, reviewer-corrected observation, and trusted application comparison remain distinct in code, contracts, storage, and user language.

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
10. The governed Azure template allocates 4 vCPU and 8 GiB, and deployment verification rejects any effective configuration that differs.
11. Security validation covers source, dependencies, upload and JSON abuse, history isolation, CSV neutralization, rate fairness, timeouts, cleanup, identity, headers, container, and deployment.
12. Three RT reviews run only after the code and documents are frozen by manifest.
13. Requester UAT begins only after automated and independent gates are complete.
14. Review-routing attribution reports every blocking check and normalized cause without treating routing volume as accuracy.
15. Numeric-brand tests include positive marks and negative ABV, proof, quantity, vintage, age, postal, barcode, lot, reference, price, and deposit controls.
16. Revision tests prove zero image-processing and OCR calls for correction, the field-specific visible-text union, server-only derivation of normalized numbers and components, preservation of printed abbreviation, precision, range, unit, sulfite, and producer form, positive-only sulfite evidence, closed beverage-family selection, class-driven family inference that cannot override an explicitly reviewer-corrected family, mandatory OCR or reviewer-drawn spatial evidence under one strictly in-bounds positive-area polygon rule, latest-event value-and-locator replay, fresh label-derived add-panel baseline with explicit provenance for every field, resolved-to-unresolved transition when fresh label evidence conflicts, protected trusted and corrected fields, immutable and independently reopenable revisions, Pending child disposition, cumulative changes, every FR-053 dependency including an ABV-only correction that reruns proof relation, placement, and distinction, one atomic head shared by correction and add-panel writes, stale-version rejection, 10-revision and three-panel limits, unchanged FIFO age, metadata and actionable errors, mutation-rate control, same-origin and scope isolation, bounded bodies, complete-lineage eviction and deletion, and bearer-scope nondisclosure.
17. OCR bakeoff tests first hold the detector model and configuration, preprocessing, rules, inputs, and hardware constant; one exact normalized score is recorded per sealed-holdout product and eligible weak-field family, diagnostic regions remain separate, and detector experiments require region truth. A candidate must then pass an identical-box replay before promotion. A failed preliminary candidate may be rejected without that additional run when the limitation is recorded.
18. Representative performance uses sanitized products with distinct admitted pixel hashes and a disclosed beverage, panel, difficulty, and dimension distribution. Repeated, re-encoded, or cache-busted fixtures remain diagnostic smoke evidence only.
19. A 24-product sealed holdout and 30 to 50 unique difficult-region annotations remain unavailable to runtime selection and extraction code. Panels, crops, and transforms of one product-field cannot add scoring wins.
20. CR-002 utility is evaluated against the FR-054 bounded gain. If safe general logic does not reach the provisional numerical threshold, release requires an explicit change-control variance that reports the measured full-corpus and sealed-holdout result, explains the remaining failure classes, and confirms zero new false clean and no protected-field regression.
21. Azure timing reports cold startup separately from post-ready latency; 20-product and 300-product wall time includes queue, retry, capacity, and rate-limit waits.
22. Release-source hashes normalize text to Git's LF representation before evidence is emitted, and a validation test compares those hashes with the staged candidate rather than the platform working-tree bytes.

## Definition of Done

- All INT and FR requirements are implemented or represented by an explicit, accepted limitation.
- The frontend, API, middleware, rule engine, and persistence use the same contracts.
- Beer or malt beverage, wine, and distilled spirits paths are tested.
- One product supports 1 to 3 images and batch supports up to 300 confirmed products and 900 images.
- A mixed folder cannot be blocked by an unrelated file; selection and processing status expose accepted, skipped, completed, rate, and ETA values.
- History retains at most 500 product lineages and 10 revisions per lineage with usable self-contained evidence; correction and add-panel writes share one atomic head, do not create a second visible entry or reset FIFO age, and deletion cannot strand a child revision.
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
- Review-causes identify every check that blocks a clean machine summary.
- Field-level correction provenance and trusted application provenance cannot be confused; observation correction completes without OCR, advances one atomic lineage head, resets the child disposition to Pending, preserves every parent, and cannot manually clear warning or other visual findings.
- Neutral image names and reversed-order tests pass.
- Numeric brands pass independent positives without selecting protected numeric negatives.
- Producer and warning recoverable-field utility meets FR-054 or carries an explicitly accepted evidence-backed variance; product-specific and filename-specific behavior is prohibited in either case.
- Any OCR model change meets FR-061, including paired accuracy, false-clean, protected-field, integrity, licensing, offline, resource, and Azure gates.
- Demo-UAT deployed parity requires exact-build Azure checks and distinct difficult smoke across all three beverage families, bound to the passing local representative and capacity evidence. Distinct-hash 30-product, 100-fingerprint p95, cold, and production-scale Azure batch paths remain mandatory before a production-scale deployed-performance claim.
- CR-002 is closed in the change-control register only after implementation, validation, independent review, deployment, and UAT entry evidence agree.

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
