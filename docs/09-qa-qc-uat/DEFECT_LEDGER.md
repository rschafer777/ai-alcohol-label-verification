# Defect Ledger

Document control ID: LV-QA-001  
Revision: 0.7  
Date: 2026-09-01  
Status: Active validation record

## 1. Severity and disposition rules

| Severity | Release effect |
|---|---|
| Stop-ship | No candidate may advance until corrected and independently regressed. |
| High | Development return and full affected regression are mandatory. |
| Medium | Correction and focused regression are mandatory before local acceptance. |
| Low | May remain only when it has no correctness, accessibility, clarity, privacy, security, or delivery effect and is documented. |

No open defect is silently waived. Environment and authorization gates are tracked separately from product defects.

## 2. Product defect ledger

| ID | Severity | Found by | Description | Root cause | Corrective action | Regression | Status |
|---|---|---|---|---|---|---|---|
| `DEV-001` | High | Governed sample integration | Normal S001 verification exceeded the worker deadline. | The pipeline performed four OCR image passes for every panel. | Use original view for sufficient panels and add enhanced OCR only for poor or unreadable panels. | Real S001 completed under the worker deadline. | CLOSED |
| `DEV-002` | Stop-ship | Governed oracle comparison | Clean S001 produced false differences. | Candidate selection admitted fixture legend text and did not safely reconcile warning spacing and producer lines. | Correct candidate selection and permitted normalization while keeping extraction reference-blind. | Exact clean summary, 19 checks, and all applicable checks Match. | CLOSED |
| `DEV-003` | High | Live browser integration | Verification returned `invalid_multipart`. | The reference JSON was sent as a file part with a filename. | Append reference as a JSON text field and panels as file parts. | Multipart unit regression plus live browser success. | CLOSED |
| `DEV-004` | High | Live browser integration | Valid server result failed frontend contract parsing. | Panel dimensions were serialized as flat fields rather than `originalDimensions`. | Correct response model, aliases, serializer, and API tests. | Contract tests and live browser parsing passed. | CLOSED |
| `DEV-005` | Medium | Dependency inspection | Both GUI and headless OpenCV were installed. | RapidOCR's transitive GUI package was not excluded. | Add a uv dependency exclusion and rebuild the virtual environment. | Lock and environment contain only `opencv-python-headless`; RapidOCR import passed. | CLOSED |
| `DEV-006` | High | Root gate negative test | The root gate could continue after a native command failed. | PowerShell did not convert every native nonzero exit into a terminating error. | Check `$LASTEXITCODE` after every Python and npm command. | Root gate now stops on any failed stage. | CLOSED |
| `DEV-007` | Low | Browser UAT | A Match result could display `Not found` for a rule check without a scalar display value. | Generic null fallback copy implied missing evidence. | Add state-aware reference and observed fallback text. | Component test and live result had zero misleading fallbacks. | CLOSED |
| `DEV-008` | High | Axe in Chrome and Edge | Hidden multi-file input had no accessible name. | The visible choose button triggered an unlabeled input. | Add accessible name and description relationships to the input. | Chrome and Edge axe journeys passed with no serious or critical violations. | CLOSED |
| `DEV-009` | Medium | Integrated test collection | Vitest attempted to collect Playwright E2E tests. | The unit-test include boundary was not explicit. | Restrict Vitest collection to frontend unit tests. | Vitest reported 14 passing tests and Playwright separately reported 2 passing browser tests. | CLOSED |
| `DEV-010` | High | CSP browser regression | Zoom and rotation depended on inline styles prohibited by the production CSP. | Dynamic transforms were applied through React style properties. | Replace inline transforms with allowlisted CSS classes and attributes. | Chrome and Edge evidence interaction passed under the governed CSP. | CLOSED |
| `DEV-011` | High | Packaging review | The documented local container command selected production boundary rules that cannot be satisfied on plain loopback HTTP. | Runtime mode and local container instructions were inconsistent. | Make direct local startup explicit and preserve production-only Host, Origin, and proxy identity requirements. | Source review and direct-mode regressions passed. | CLOSED |
| `DEV-012` | Medium | SBOM review | The npm-generated frontend SBOM contained no components. | The private package graph was not represented by that generation path. | Build a deterministic CycloneDX inventory from the exact production package lock and verify it against `npm ls`. | Four production components and three root dependencies are recorded and hashed. | CLOSED |
| `DEV-013` | High | Dependency audit | Current advisories affected locked runtime and development packages. | The baseline lock predated the advisory review. | Upgrade and relock FastAPI, Starlette, Pillow, python-multipart, and pytest. | `pip-audit` found no known vulnerabilities and `npm audit --omit=dev` found zero. | CLOSED |
| `DEV-014` | High | Requester scope review | The first core release excluded the stakeholder-requested batch workflow. | The initial time-box decision treated batch as optional future scope. | Implement a session-only client queue for 1 to 300 manifest rows with cancellation, retry, detail review, CSV, and JSON export while reusing the governed single-verification endpoint. | 38 frontend tests pass; a governed 300-application run completed all rows and passed the 10, 20, and 300 timing thresholds. | CLOSED |
| `VAL-006` | High | Warning compliance review | Printed scale text could be mistaken for reliable physical calibration. | Synthetic marker text had been trusted as measurement evidence. | Treat physical scale and character density as unverified unless independently reliable calibration is supplied. | Boundary tests cover 1, 2, and 3 mm tiers and 40, 25, and 12 character-per-inch limits; the product corpus has zero false-clean results. | CLOSED |
| `VAL-007` | High | OCR warning review | Punctuation introduced at OCR line wraps could be normalized into a false exact match. | Visual line wrapping and legal punctuation were not distinguished. | Preserve a punctuation-uncertainty signal and route the otherwise exact warning to Review. | Exact, title-case, wording-error, and line-wrap uncertainty regressions pass. | CLOSED |
| `VAL-008` | Medium | Difficult-image review | The recovery path did not attempt bounded deskew or perspective correction. | The original enhancement path handled exposure but not clear geometry defects. | Add one conservative deskew or perspective recovery view and map derived evidence back to original pixels. | Perspective-coordinate and dark rotated-image regressions pass; unsupported glare and curved-bottle recovery remain documented limitations. | CLOSED |
| `VAL-001` | High | Product corpus | Unreadable evidence could create false field differences or unsupported confidence. | Evidence dependency was not applied uniformly. | Gate comparisons and evidence-dependent checks on readable source evidence. | Degraded and unreadable corpus cases matched conservative oracle states. | CLOSED |
| `VAL-002` | High | Product corpus | Warning and imported-producer edge cases were inconsistently classified. | Candidate and presentation heuristics lacked several bounded cases. | Refine reference-blind extraction and deterministic warning subchecks. | All governed warning and producer scenarios passed. | CLOSED |
| `VAL-003` | High | Six-panel holdout | Maximum accepted panel case exceeded the 6.25 second worker deadline. | Exact duplicate views were recomputed and independent images ran serially. | Reuse exact request-local duplicate inference and use two deterministic lanes inside the same supervised worker. | H001 completed in 4.51 seconds and full deadline regressions passed. | CLOSED |
| `VAL-004` | High | Cold-start resource envelope | Concurrent OCR-engine construction briefly exceeded the selected 2 GiB RSS limit. | Both inference engines allocated startup working memory at the same time. | Initialize the two engines sequentially and close multiprocessing queues on supervisor teardown. | Warm peak was 1,466,724,352 bytes, cold peak was 1,578,123,264 bytes, and 300-row batch peak was 847,986,688 bytes, all below 2 GiB. | CLOSED |
| `VAL-004` | Medium | Oracle review | Some expected reason classes relied on generator-only roles or rejected contract-permitted safe equivalence. | The independent oracle overstated observable production knowledge. | Correct, regenerate, validate, and reseal the oracle package. | Fixture validator and 20 validation tests passed. | CLOSED |
| `VAL-005` | High | Product corpus | Promotional interruption text won brand ranking in D015. | It was one pixel taller than the true brand. | Exclude only text structurally located between warning parts from brand eligibility. | D015 brand Match and continuity Mismatch passed. | CLOSED |

## 3. Packaging review ledger

| ID | Original risk | Corrective evidence | Source-review status |
|---|---|---|---|
| `PKG-F001` | Runtime could modify governed OCR models. | Root-owned read-only model tree; runtime user owns only spool. | CLOSED |
| `PKG-F002` | Container health request could fail strict Host validation. | Health request and Fly service check use the configured allowed Host. | CLOSED |
| `PKG-F003` | Governed sample was unavailable in the packaged runtime. | Manifest and panels are copied; sample routes constrain identifiers and resolved paths. | CLOSED |
| `PKG-F004` | Build toolchain and OS artifact could drift. | Digest-pinned image sources, checksum-pinned exact Debian artifact, frozen uv/npm graphs, and no mutable external Dockerfile frontend. | CLOSED |
| `PKG-F005` | Broad build context could capture local or sensitive artifacts. | Deny-all Docker context allowlist with explicit artifact exclusions. | CLOSED |
| `PKG-F006` | Build provenance identifier could be generic or omitted. | Nonempty `LABELVERIFY_BUILD_ID` is mandatory and persisted. | CLOSED |
| `PKG-F007` | RapidOCR warmup attempted to download its default visualization font into the read-only package directory. | Fetch DejaVu Sans 2.37 only during controlled setup or build, verify source and extracted hashes, pass its absolute local path to RapidOCR, and prove container readiness before the serving Container App mutation. | CLOSED |

## 4. Security defect ledger

| ID | Severity | Description | Corrective action | Regression | Status |
|---|---|---|---|---|---|
| `SEC-001` | Medium | Decoded raster allocation could occur before pixel-limit enforcement. | Validate declared dimensions before raster load and pass the remaining cumulative budget into decode. | Boundary decode and cumulative-limit tests passed. | CLOSED |
| `SEC-002` | Medium | Worker replacement could race shutdown. | Add terminal stopping state, tracked replacement threads, interruptible readiness, and joined shutdown. | Replacement and interrupted-warmup tests passed. | CLOSED |
| `SEC-003` | Medium | Invalid framing could consume the global start budget. | Perform structural framing validation before limiter charge and track charge ownership. | Invalid and concurrent ownership tests passed. | CLOSED |
| `SEC-004` | Low | Framework multipart spill could use an uncontrolled temp root. | Supply the governed spool root to every multipart `SpooledTemporaryFile`. | Real spill-location regression passed. | CLOSED |
| `SEC-005` | Low | Partial multipart files might remain open on cancellation or nonstandard exceptions. | Close every parser-owned resource on `BaseException`. | RuntimeError and CancelledError cleanup regressions passed. | CLOSED |

The security correction review also closed its circular-import regression before the final root gate.

## 5. Final validation process defects

| ID | Severity | Linked assertions | Description | Corrective action | Regression evidence | Status |
|---|---|---|---|---|---|---|
| `QA-001` | High | `T-001` through `T-041` | Final RT V1 found that the required assertion-level evidence ledger was absent even though suite-level evidence existed. | Build and cross-validate one record for every governed assertion, preserving FAIL, NOT_RUN, BLOCKED, and requester-gated states exactly. | The independently reconciled ledgers contain 75 assertions across all 41 tests: 56 PASS, zero FAIL, zero NOT_RUN, seven BLOCKED, and 12 requester-gated records, with required metadata, hashes, composites, and defect links. | CLOSED |
| `QA-002` | Medium | `T-005`, `T-006`, `T-022`, `T-030`, `T-033` | Initial governed coverage measured aggregation at 83.33 percent branches, comparison plus warning policy at 81.25 percent branches, and frontend business modules at 67.26 percent branches. | Add behavior-focused branch tests and enforce an 80 percent frontend line and branch floor in Vitest. Do not reduce the approved thresholds. | Independent retest passed: aggregation 12 of 12 branches, comparison plus warnings 62 of 64 branches, backend business subset 87.14 percent branches, and frontend business subset 84.52 percent branches. | CLOSED |
| `QA-003` | High | `T-009`, `T-029`, `T-039`, `T-041` | Final RT V1 found incomplete machine-readable proof for lifecycle ownership, cleanup, cancellation, disconnect, timeout, replacement, recovery, shutdown, content canaries, and final zero counters. | Execute the complete post-fix lifecycle matrix and retain machine-readable evidence with exact phase counters and canary assertions. | Current canonical lifecycle evidence passed 46 focused tests and 182 full Python tests with stable source hashes. The first concurrent-load failure is retained separately and the isolated clean rerun is canonical. Deployed network egress remains BLOCKED, not promoted to local PASS. | CLOSED |
| `QA-004` | High | `T-030`, `T-037` | Final RT V1 found only automated UAT evidence and no two independent first-time reviewer records. | Run both timed journeys with two independent non-frontend implementers and retain reviewer-specific evidence. | Reviewer 1 passed UAT-001 in 46.135 seconds and UAT-002 in 185.816 seconds. Reviewer 2 passed UAT-001 in 29.561 seconds and UAT-002 in 139.780 seconds. Both records confirm no facilitator help and all required steps. | CLOSED |
| `A11Y-001` | High | `T-030` | Manual reviewer 1 found a duplicate, visually clipped keyboard stop on the hidden file input. | Remove the hidden input from sequential keyboard navigation while retaining the visible Choose images control and programmatic file dialog activation. | `tabIndex=-1`, focused 8-test regression, manual focus-sequence retest, and current Edge automated smoke passed. Tab moves directly from Choose images to Verify label. | CLOSED |
| `QA-005` | Medium | `T-032`, `T-033` | Final RT V1 found historical fixture hashes presented as current and requester-local absolute paths in distributable documents and raw evidence. | Mark superseded hashes historical, establish the corrected authoritative hashes, sanitize requester-local paths, and repeat the repository-neutral path scan. | Contract baseline identifies the authoritative corrected hashes. The repository-neutral scan found no requester-local path; its only match is the intentional private-path detection expression in the validation script. | CLOSED |
| `QA-006` | High | `T-033`, `T-037` | Validation, UAT, and release status documents claimed local PASS before assertion, lifecycle, accessibility, and two-reviewer proof was complete. | Set conclusions from the assertion ledger only and distinguish locally runnable PASS from OCI, requester, deployment, release-recheck, and NVDA blockers. | LV-VAL-001 Revision 1.2, LV-UAT-001 Revision 1.2, and LV-REL-002 Revision 1.2 consistently report 56 runnable PASS assertions, seven BLOCKED assertions, 12 requester gates, and an INCOMPLETE composite. | CLOSED |

## 6. Final RT V2 correction findings

| ID | Severity | Description | Corrective action | Regression evidence | Status |
|---|---|---|---|---|---|
| `RTV2-001` | High | The README direct-container command omitted the allowed Host required by the image health check. | Supply `LABELVERIFY_ALLOWED_HOST=127.0.0.1:8080` in the documented direct-mode command and add a release-claim regression. | Focused release-claim tests passed 2 of 2 and the full gate passed 122 Python tests. | CLOSED |
| `RTV2-002` | Medium | README displayed exact performance values from the superseded run. | Bind README values to the current decisive performance evidence and add a release-claim regression. | README now derives the exact 2.151-second warm and 9.812-second cold values from the decisive JSON; focused and full regressions passed. | CLOSED |
| `RTV2-003` | High | Lifecycle and total-phase evidence retained source hashes from before the final test-source changes. | Rerun both governed evidence producers on the corrected snapshot and rebind the assertion ledger. | Lifecycle evidence passed 46 focused and 182 full tests; total-phase evidence passed 16 backend and 4 frontend tests; every recorded source hash matches the current file. | CLOSED |
| `RTV2-004` | Medium | The regenerated total-phase command transcript exposed the requester-local Windows temp directory. | Sanitize project and temp roots in the evidence producer, including command and output fields, and add a producer regression. | Focused sanitizer test and repository-neutral evidence scan passed; regenerated evidence contains `<TEMP_ROOT>` and zero requester-local paths. | CLOSED |

## 7. Public release integrity findings

| ID | Severity | Description | Corrective action | Regression evidence | Status |
|---|---|---|---|---|---|
| `PUB-001` | High | Active release records retained superseded test, performance, and 50-image counts after the final correction wave. | Rebind both active release records to the current 182 Python, 46 frontend, performance, memory, batch, and 0 pass, 45 review, 5 difference evidence. | Three independent RTs verified the corrected current claims. | CLOSED |
| `PUB-002` | High | Raw unit-coverage outputs remained in the initial Git index after ignore rules were added. | Remove the raw outputs from the index without deleting local evidence, stage the final ignore rules, and compare the governed manifest path set to the public index. | Public-path scan excludes raw coverage while retaining the governed coverage summary. | CLOSED |
| `PUB-003` | High | The first release-manifest generator hashed Windows working-tree bytes even though Git normalized staged text to LF, causing 143 staged-blob mismatches. | Generate the seal from `git write-tree` and `git archive`, hashing the exact normalized staged bytes rather than the working tree. | A CRLF-to-LF normalization regression passes, and every staged archive entry matches the final manifest. | CLOSED |
| `PUB-004` | Medium | Final browser E2E execution updated one governed timing field after the preceding manifest seal. | Restage the final browser evidence before regenerating the staged-tree manifest. | Zero unstaged files and exact staged-tree equality are required immediately before commit. | CLOSED |
| `PUB-005` | High | Clean-checkout replay exposed that MyPy imported `typing_extensions` even though the development dependency was not explicitly installed by the locked clean environment. | Add the exact `typing-extensions` version already present in the governed lock and SBOM to the development dependency group, then refresh the lock. | Clean locked install and strict MyPy execution from the remote clone must pass. | CLOSED |
| `PUB-006` | High | Clean-checkout replay exposed that the fixture generator wrote Windows CRLF text while Git stored governed JSON as LF, invalidating fixture-tree hashes and the holdout seal after checkout. | Make fixture JSON and seal writes explicitly LF, require LF checkout for SHA256 manifests, regenerate governed hashes, and add a line-ending regression. | Fixture generation, corpus validation, holdout seal validation, and the complete root gate must pass from a clean checkout. | CLOSED |

## 8. Non-defect blockers and requester gates

| ID | Type | Condition | Current status | Required closure evidence |
|---|---|---|---|---|
| `ENV-OCI-001` | Environment | No Docker, Podman, nerdctl, or Buildah executable is installed. | BLOCKED | Clean OCI build and rebuild, image digest, non-root identity, governed hashes, and readiness smoke. |
| `ENV-NVDA-001` | Environment and action authorization | NVDA is not installed. Running the verified portable package requires requester confirmation at action time. | BLOCKED | Manual NVDA core-journey transcript against the final source snapshot. |
| `ENV-A11Y-001` | Environment | The permitted browser connection does not expose native 200 percent browser zoom or a live manual Edge connection. | BLOCKED | Exact native 200 percent zoom inspection at 1024 by 768 and live manual Edge visual inspection. |
| `REQ-GIT-001` | Authorization and publication | Requester authorized Git initialization and publication on 2026-09-01. | IN_PROGRESS | Push the verified commit and complete clean-checkout replay. |
| `REQ-DEPLOY-001` | Authorization | Requester has not authorized public deployment. | PENDING_REQUESTER_GATE | Public URL plus deployed configuration, edge, warm, cold, load, and shaped-network evidence. |
| `REQ-REG-001` | External verification | Final official-source regulatory recheck was completed on 2026-09-01. | PASS | Dated TTB and eCFR verification is recorded in the regulatory and technical source registers. |

## 9. Current defect conclusion

Open product defects: 0.  
Open packaging source findings: 0.  
Open security findings: 0.  
Open final-validation process defects: 0.  
Environment and requester-controlled gates remain explicit and cannot be converted to PASS by documentation.
