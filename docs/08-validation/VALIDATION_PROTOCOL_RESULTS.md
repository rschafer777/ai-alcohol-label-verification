# Validation Protocol Results

Document control ID: LV-VAL-001  
Revision: 2.0  
Date: 2026-09-01  
Status: Runnable local evidence complete; composite INCOMPLETE

## 1. Gate conclusion

The governed SDLC ledger contains 75 assertions across all 41 tests: 56 PASS, 0 FAIL, 0 NOT_RUN, 7 BLOCKED, and 12 `PENDING_REQUESTER_GATE`. A later user-supplied 50-image diagnostic adds a separate failed automatic-clear recognition gate: the visual oracle contains 33 pass and 17 do-not-pass images, while the local harness routes all 33 visual passes to review, detects 5 defects, holds 12 defects for review, clears no defect, and falsely rejects no visual pass. The candidate composite therefore remains INCOMPLETE and is not represented as a local or final PASS.

This is a local candidate conclusion. It does not convert OCI, Git, public deployment, official-source release recheck, or requester acceptance gates into PASS.

## 2. Requirements chain

The tested chain is:

`assignment and discovery -> Intake -> BAIRD BR/BQ -> I2R decisions and interfaces -> FR requirements -> BI work packages and tests -> source -> validation evidence`

The implemented product remains a standalone, human-in-the-loop verification assistant. It does not integrate with COLAs Online, persist user content, make a legal compliance determination, or claim TTB affiliation or approval.

## 3. Decisive evidence

| Assertion | Result | Evidence |
|---|---|---|
| Frozen contract completeness | PASS | 19 selected checks and governed error, API, and rule registries loaded by exact hash |
| Independent fixture integrity | PASS | 30 cases, 24 development, 6 sealed holdout, 8 mutations, 50 tags, 19-check coverage, 20 tests |
| Product corpus | PASS | 30 of 30 cases, 456 of 456 expected result rows, 8 of 8 mutations, 0 failures, 0 false-clean results |
| Assertion evidence | INCOMPLETE composite | 75 assertions: 56 PASS, 7 BLOCKED, 12 requester-gated, zero FAIL, zero NOT_RUN |
| Python quality | PASS | Ruff, strict MyPy on 34 source files, 197 tests |
| Frontend quality | PASS | ESLint, strict TypeScript, 46 Vitest tests, production Vite build |
| Integrated browser | PASS for runnable matrix | Three Playwright journeys passed: Chrome core, Chrome full privacy, and Edge core. One intentional duplicate Edge privacy run was skipped. Axe found no serious or critical violations. |
| Privacy | PASS locally | Full success, error, cancel, refresh, reopen, and Start over browser matrix remained content-free; API responses were no-store; request-scoped server resources cleaned |
| Warm performance | PASS | 30 of 30 complete; p95 2,374.123 ms; maximum 3,204.222 ms; threshold 5,000 ms |
| Cold readiness plus first result | PASS | 5 of 5 complete; p95 and maximum 7,531.501 ms; exclusive threshold 10,000 ms |
| Batch capacity and elapsed time | PASS | One warmed worker completed 10 in 18.665 seconds, 20 in 36.301 seconds, and 300 in 521.963 seconds; average 1,739.864 ms; zero false-clean results |
| User-supplied 50-image diagnostic | FAIL for automatic-clear recognition | Human oracle 33 pass and 17 do not pass; harness 0 pass, 45 review, and 5 do not pass; all 17 defects contained; zero false clearances; zero false deterministic rejections; selected-profile clear recognition 0 of 14 |
| Resource envelope | PASS locally | Warm peak parent plus worker RSS 1,466,724,352 bytes, cold peak 1,578,123,264 bytes, and batch peak 847,986,688 bytes inside the 2 GiB plan |
| Security correction | PASS locally | Local lifecycle and security assertions passed; the retained security-correction matrix contains 191 passing tests, and the current root regression contains 197 passing tests including Azure identity, evidence binding, and deployment contracts |
| Independent UAT | PASS locally | Two non-UI implementers passed both no-help timed journeys within the 3-minute and 7-minute limits |
| Accessibility | INCOMPLETE | Automated Chrome/Edge and manual keyboard/focus evidence pass; native 200 percent zoom/manual Edge and NVDA are BLOCKED by the current environment |
| Python dependency audit | PASS | No known vulnerabilities |
| Production npm audit | PASS | Zero vulnerabilities |
| Prohibited Unicode dash scan | PASS | No U+2010 through U+2015 characters in governed text/source scan |

Machine-readable evidence:

- `docs/08-validation/evidence/local-product-corpus.json`
- `docs/08-validation/evidence/local-performance.json`
- `docs/08-validation/evidence/local-batch-performance.json`
- `docs/08-validation/evidence/local-root-check.txt`
- `docs/08-validation/evidence/governed-coverage-summary.json`
- `docs/08-validation/evidence/browser-privacy-matrix.json`
- `docs/08-validation/evidence/total-phase-matrix.json`
- `docs/08-validation/evidence/security-post-fix/lifecycle-matrix.json`
- `docs/08-validation/evidence/assertion-evidence-ledger.json`
- `docs/10-release/sbom-python.cdx.json`
- `docs/10-release/sbom-frontend.cdx.json`

## 4. Core acceptance coverage

The accepted local workflow supports:

1. manual application-value entry, one-click governed sample loading, or a governed batch manifest;
2. one to six PNG or JPEG label panels within exact file, aggregate-byte, and pixel limits;
3. local hash-verified OCR with no required runtime external call;
4. deterministic comparison of all 19 selected checks;
5. explicit Match, Review, Mismatch, and Not verified states with linked original-pixel evidence;
6. conservative handling of missing, ambiguous, low-quality, and unreadable evidence;
7. results in a clear side-by-side workspace with zoom, rotate, reset, notes, disposition, retry, and Start over;
8. a session-only sequential batch of 1 to 300 applications with progress, exception filters, cancellation, retry, detail review, CSV export, and detailed JSON export;
9. session-only state with no database, durable queue, account, analytics, or browser persistence; and
10. bounded typed errors, cancellation, worker timeout, restart, rate, resource, and cleanup behavior.

## 5. Scope decisions preserved

- Single-label verification and client-managed batch verification are committed prototype paths.
- Multiple images for one label are supported.
- Batch processing reuses the single-verification endpoint sequentially. It does not add a persistent server queue, ZIP ingestion, background scheduling, or multi-user coordination.
- The application is desktop-first for Chrome and Edge at the documented evaluation envelope.
- Government warning typography and physical size are reported conservatively when pixels do not support a reliable conclusion.
- Human review remains authoritative.

## 6. External gates

| Gate | Status | Reason |
|---|---|---|
| Local OCI build and runtime proof | BLOCKED | No Docker, Podman, nerdctl, or Buildah is installed locally; the authorized GitHub workflow must prove the public image separately |
| Native 200 percent zoom and live manual Edge | BLOCKED | The permitted browser connection cannot expose this native manual state |
| NVDA manual journey | BLOCKED | NVDA is not installed and portable execution requires requester confirmation at action time |
| Deployed network-egress enforcement | BLOCKED | The Azure Consumption environment does not establish the final deny-by-default federal egress policy |
| Git repository and clean-checkout replay | PASS FOR PUBLISHED PRE-AZURE SNAPSHOT | Repository creation, source publication, clean clone, and exact manifest replay passed; the current Azure snapshot must repeat this after push |
| Public deployment and URL | AUTHORIZED, EXECUTION PENDING | The dispatch-only Azure workflow must build, deploy, read back, and smoke-test the current RT-cleared snapshot |
| Final official TTB source recheck | PENDING_REQUESTER_GATE | Must occur immediately before public release |
| Requester code review and UAT | PENDING_REQUESTER_GATE | Follows internal clearance |

## 7. Validation disposition

Validation Protocol composite: INCOMPLETE.  
Governed SDLC ledger assertions: 56 of 56 runnable assertions PASS.  
Additional user-supplied image recognition gate: FAIL.  
Next gate: clear the Azure RT findings, regenerate one immutable candidate manifest, configure the governed GitHub environment, and execute the authorized public workflow. Automatic clear recognition remains a separate failed gate that must improve without false clearances or false deterministic rejections, or receive explicit requester acceptance. Blocked and requester-controlled assertions remain explicit until their required environment or approval exists.
