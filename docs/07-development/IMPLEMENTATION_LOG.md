# Implementation Log

Document control ID: LV-DEV-003  
Revision: 0.1  
Date: 2026-09-01  
Status: Active development record

## 1. Governing baselines

Development began only after the following gates returned three independent CLEAR verdicts:

- Intake baseline and source traceability;
- BAIRD requirements validation;
- I2R architecture and engineering package plus FRD;
- Build Instructions, work package ledger, QA/QC protocol, UAT, and Definition of Done.

The implementation is controlled by the four versioned contracts in `contracts/`. Contract hashes and acceptance evidence are recorded in `CONTRACT_BASELINE.md`.

## 2. Build organization

| Role | Scope | Controlled roots |
|---|---|---|
| `INT-LEAD` | Integration, shared configuration, packaging, documentation, validation coordination | Repository-wide shared files outside delegated roots |
| `ENG-BE` | Verification engine, imaging, OCR, orchestration, API, security, backend tests | `backend/labelverify/`, `backend/tests/` |
| `ENG-FE` | Intake, processing, results, evidence interaction, recovery, frontend tests | `frontend/src/`, `frontend/tests/` |
| `VV-LEAD` | Independent fixture corpus, oracles, validation tools, cross-layer tests | `fixtures/`, `tests/`, new validation scripts |

The implementation uses contract gates so each workstream consumes the same request, result, error, and selected-check definitions.

## 3. Completed foundation

- Python 3.12 and Node.js 24 toolchains recorded.
- Python and npm dependencies locked.
- RapidOCR ONNX models downloaded and verified against the governed manifest.
- Nineteen selected checks and all public errors frozen in versioned JSON registries.
- Frontend contract types generated and accepted against the source contract.
- Thirty development and holdout fixture cases plus the separate two-panel sample produced.
- Shared lint, typecheck, unit-test, build, and Unicode scan command established.

## 4. Integration cycle 1

The first integration check was intentionally run before workstream completion. It found bounded implementation defects rather than baseline drift:

- backend formatting and strict typing findings in in-progress files;
- frontend compiler configuration missing `noEmit` for TypeScript import-extension validation;
- frontend test typing, DOM cleanup, and accessible-name test defects.

Disposition:

- `INT-LEAD` added `noEmit` to the shared TypeScript configuration and expanded the root check script to include `ops/`;
- backend findings were returned to `ENG-BE` for correction and focused regression;
- frontend findings were returned to `ENG-FE` for correction and focused regression.

No feature requirement, architecture decision, selected check, public error, resource limit, or privacy boundary was changed.

## 5. Development exit result

The implementation advanced to the Validation Protocol after all development exit conditions were demonstrated:

1. backend lint, strict typing, and focused tests passed;
2. frontend lint, strict typing, focused tests, and production build passed;
3. fixture corpus validation, determinism, anti-hard-coding, and contract parity passed;
4. the frontend and backend operated together through the versioned API;
5. runtime packaging files and evaluator documentation were completed; and
6. the prohibited Unicode dash scan passed.

The missing local OCI builder remains an explicit environment blocker for the mandatory OCI proof. It does not authorize weakening or marking that assertion complete.

## 6. Independent fixture gate result

The independent fixture workstream passed its first complete local gate:

- corpus validator: PASS;
- development cases: 24;
- sealed holdout cases: 6;
- selected-check coverage: 19 of 19;
- mutation controls: 8;
- validation tests: 8 passed;
- validation-script Ruff check: PASS.

This result establishes fixture and oracle integrity. Product-result conformance remains a later Validation Protocol assertion after backend and frontend integration.

## 7. Frontend workstream handoff

`WP-005` and `WP-006` completed their focused gate:

- TypeScript strict typecheck: PASS;
- ESLint: PASS;
- Vitest: 12 of 12 tests passed;
- Vite production build: PASS;
- generated-contract parity: PASS;
- prohibited Unicode dash scan: zero matches;
- browser storage and analytics source scan: zero references.

The accepted UI includes the manual and sample intake journeys, conditional imported-origin input, one to six panel controls, client-side limits and focus behavior, processing and cancel states, exhaustive public errors, all 19 result rows, original-pixel evidence interaction, retry preservation, guarded Start over, session-only notes and disposition, responsive layout, and accessibility behavior. Full browser and integrated API validation remains part of the Validation Protocol.

## 8. Backend workstream handoff

The backend workstream completed the modular monolith and its supervised OCR boundary. Focused evidence established:

- reference-blind extraction through RapidOCR and ONNX Runtime on CPU;
- all 19 selected checks with deterministic aggregation and typed evidence;
- exact request, upload, timeout, error, privacy, and cleanup boundaries;
- liveness, fail-closed readiness, safe metadata, governed sample, and same-origin SPA routes;
- no required runtime egress, database, durable queue, account, or content logging; and
- successful governed sample verification with every applicable check at Match.

## 9. Integrated correction loop

The Validation Protocol began immediately after integration and found defects that focused unit tests did not expose. Each correction retained the frozen contracts.

| Defect | Severity | Observation | Correction | Regression evidence |
|---|---|---|---|---|
| `DEV-001` | High | Four OCR image passes caused the governed sample to exceed the worker deadline. | Added a reference-blind quality cascade: sufficient panels use the original view, while poor or unreadable panels add the enhanced fallback. | Governed sample completed below the 6.25 second worker deadline. |
| `DEV-002` | Stop-ship | Synthetic fixture legend text could become a brand candidate, warning spacing could be misread, and producer candidate selection could create false differences. | Corrected candidate selection and safe warning and producer normalization without using reference values during extraction. | S001 returned the exact clean oracle and all applicable checks at Match. |
| `DEV-003` | High | The browser sent the reference JSON as a file part, violating the multipart contract. | Sent reference as a JSON text field with no filename and retained images as file parts. | Frontend multipart regression and live browser request passed. |
| `DEV-004` | High | The backend serialized panel width and height as flat fields instead of the contracted `originalDimensions` object. | Corrected the response model and serializer. | Contract tests and the live browser result parser passed. |
| `DEV-005` | Medium | The environment resolved both GUI and headless OpenCV packages. | Excluded RapidOCR's GUI OpenCV transitive dependency and retained only checksum-locked `opencv-python-headless`. | Clean virtual environment resolved one OpenCV package and imported RapidOCR successfully. |
| `DEV-006` | High | The root PowerShell gate could continue after a native command failed. | Added explicit exit-code checks after every Python and npm command. | A failing native command now terminates the gate. |
| `DEV-007` | Low | Successful rule-based checks could display `Not found` when no scalar display value applied. | Added state-aware neutral fallback text. | Component regression and live browser inspection showed zero misleading `Not found` fallbacks. |
| `DEV-008` | High | Automated axe found the hidden multi-file input had no accessible name. | Added an accessible name plus help and error descriptions to the input. | Chrome and Edge axe journeys passed with zero serious or critical violations. |

## 10. Packaging correction loop

Independent source review found six packaging issues. All six are closed at source-review level:

- all container image sources are digest pinned;
- the Debian runtime artifact has an exact version and SHA256;
- the model directory is root-owned and read-only before the runtime user starts;
- the runtime user owns only the spool directory;
- strict Host validation is used by the runtime and Fly health checks;
- the governed sample contract and panels are packaged and constrained to their governed directory;
- the build context uses a deny-all allowlist;
- a unique build identifier is mandatory; and
- the mutable external Dockerfile frontend declaration was removed.

The package status is `READY_FOR_OCI_PROOF`. Docker, Podman, nerdctl, and Buildah are absent on this workstation, so clean build, clean rebuild, non-root runtime, and container readiness assertions remain `BLOCKED`. They are not recorded as PASS.

## 11. Security correction loop

The independent standard security scan identified five bounded findings. Development corrected each without changing the frozen public contracts:

- declared raster dimensions are checked before decoded allocation and against the remaining cumulative pixel budget;
- worker replacement cannot race shutdown or create an untracked child;
- structurally invalid requests do not consume the global start budget;
- framework multipart spill files use the governed spool root; and
- every owned multipart resource closes on ordinary exceptions, cancellation, and other `BaseException` paths.

The correction review also closed a circular import introduced during remediation, removed CSP-incompatible inline transforms, corrected direct local container startup behavior, rebuilt the frontend SBOM from the locked production graph, and corrected test collection so browser E2E files are not executed by Vitest. FastAPI, Starlette, Pillow, python-multipart, and pytest were upgraded and relocked after advisory review. The synchronized Python and production npm audits then reported no known vulnerabilities.

## 12. Product-corpus correction loop

The first complete product-corpus execution correctly found no false-clean result, but exposed both production defects and independent-oracle defects. The loop retained all 19 selected checks, result semantics, input limits, and timing budgets.

| Defect | Observation | Correction | Decisive regression |
|---|---|---|---|
| `VAL-001` | Unreadable evidence could create false field mismatches or unsupported confidence. | Gated field comparison and evidence-dependent checks on actual readable evidence. | Degraded and unreadable cases returned conservative Review or Not verified states. |
| `VAL-002` | Warning punctuation, heading, body, contrast, continuity, separation, and imported-producer edge cases were not consistently classified. | Refined reference-blind candidate extraction and deterministic warning subchecks. | Development and sealed warning variants matched their independent oracles. |
| `VAL-003` | The six-panel holdout exceeded the 6.25 second worker deadline. | Reused exact duplicate image inference and added two deterministic inference lanes inside the same one-job supervised child. | Six-panel result completed in 4.51 seconds in the decisive corpus; reversed order completed without semantic change. |
| `VAL-004` | Concurrent cold construction of both OCR engines briefly exceeded the selected 2 GiB RSS envelope. | Preserved two deterministic inference lanes, initialized their engines sequentially, ran the readiness probe on the first identical model configuration, and explicitly closed worker queues during shutdown. | Governed warm, cold, batch, and memory evidence must remain below the selected threshold. |
| `VAL-004` | Several oracle rows encoded generator-only panel roles or demanded exact classification where the contract permits safe equivalence. | Corrected the independent oracle, regenerated fixtures, and resealed the holdout manifest. | Fixture validator and 20 oracle-integrity tests passed before product rerun. |
| `VAL-005` | An uppercase promotional interruption one pixel taller than the brand won brand ranking. | Excluded only lines structurally located between warning parts from brand eligibility. | D015 retained brand Match and warning-continuity Mismatch. |

The decisive rerun passed all 30 cases, all 456 expected result rows, and all 8 mutation controls with zero failures and zero false-clean results.

## 13. Validation exit evidence

- Root lint and formatting gate: PASS.
- Strict MyPy across 34 source files: PASS.
- Python tests: 98 passed.
- Frontend tests: 14 passed.
- Frontend production build: PASS.
- Chrome and Edge integrated sample journeys: 2 passed.
- Axe serious and critical findings: zero.
- Product corpus: 30 of 30 cases and 8 of 8 mutations passed.
- Warm performance: 30 of 30 complete, p95 1,978.469 ms against 5,000 ms.
- Cold readiness through first result: 5 of 5 complete, p95 9,537.266 ms against the exclusive 10,000 ms threshold.
- Peak observed parent plus worker RSS: 1,612,611,584 bytes inside the planned 2 GiB envelope.
- Python dependency audit: no known vulnerabilities.
- Production npm audit: zero vulnerabilities.

The local implementation is ready for internal UAT review and final independent RT inspection. OCI, Git, public deployment, final official-source recheck, and requester acceptance remain separate gates.
