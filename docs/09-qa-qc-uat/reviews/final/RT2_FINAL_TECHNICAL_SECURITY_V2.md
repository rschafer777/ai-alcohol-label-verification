# Final RT2 V2 Technical, Security, and Release Integrity Review

Document control ID: LV-FINAL-RT2-V2-001  
Revision: 2.0  
Date: 2026-09-01  
Reviewer role: RT2 technical, security, and release integrity  
Review mode: Read-only review of the exact sealed local candidate  
Verdict: REWORK_REQUIRED

## 1. Sealed snapshot verification

- Required release manifest SHA-256: `9EBD7ABEF664A24680987C070EDEA5A5C2EF4861BE79344246516B890BDF16A3`
- Observed release manifest SHA-256: `9EBD7ABEF664A24680987C070EDEA5A5C2EF4861BE79344246516B890BDF16A3`
- Manifest entries checked: 528
- Badly formatted entries: 0
- Missing files: 0
- Hash mismatches: 0
- Absolute or parent-traversing manifest paths: 0
- Transient cache, dependency, test-output, log, or temporary entries: 0
- Manifest-listed files containing U+2010 through U+2015: 0

Before this review file was created, the manifest generator's inclusion rules selected exactly the same 528 files as the sealed manifest, with no unlisted or missing candidate file. This review is a post-freeze verdict record and is not represented as a member of the sealed candidate.

## 2. Technical and security conclusion

The implemented local application has a coherent same-origin architecture, strict typed contracts, bounded upload and decoded-image limits, one killable OCR child, fail-closed result validation, exact production Host and Origin controls, content-free public errors, no browser persistence API, no database, and no required runtime outbound client. No exploitable application security vulnerability was confirmed in the sealed source.

The retained local gates are also substantial. The root transcript records Ruff, strict MyPy on 34 source files, 119 Python tests, ESLint, strict TypeScript, 34 frontend tests, a production frontend build, Chrome and Edge core browser coverage, Chrome privacy coverage, and a clean Unicode scan at `docs/08-validation/evidence/local-root-check.txt`. The product corpus reports 30 of 30 cases, 456 of 456 expected rows, 8 of 8 mutation controls, and zero false-clean results at `docs/08-validation/evidence/local-product-corpus.json`. The current performance record passes with warmed p95 of 2,151.062 ms and cold readiness through first result of 9,812.494 ms at `docs/08-validation/evidence/local-performance.json:285-359`.

The candidate is not ready for a CLEAR verdict because the sealed release package contains two evidence and documentation integrity defects plus one deterministic container quick-start defect. These are actionable local defects, not permitted external gates.

## 3. Actionable findings

### RT2V2-F001 - HIGH - Retained lifecycle evidence is not fully bound to the sealed test snapshot

The post-fix lifecycle record declares `sourceStableDuringRun: true` and overall `pass: true`, but it records `backend/tests/test_lifecycle_matrix.py` as SHA-256 `ab3371dc13f871e8c9fad808382c0472cd3b02e79869b8a2512758ac22b41090` at `docs/08-validation/evidence/security-post-fix/lifecycle-matrix.json:24,37,541`. The sealed manifest records the current file as `137e69b2af075ebd417033c796248bf061beed179a7e9d002214598a5702929a` at `docs/10-release/RELEASE_MANIFEST.sha256:48`.

The complete phase matrix has the same release-binding problem. It records `frontend/tests/phase-matrix.test.tsx` as `8f9b4315cd9f597da8cbdd017f7b83279533cd1defce19b4eef46fd2828c1da9` while declaring overall PASS at `docs/08-validation/evidence/total-phase-matrix.json:21,127`. The sealed manifest records the current test as `495f2c3f95141f40f9eb2b7b7a94fa39c9c4a1d1686e9138225f793afa668b83` at `docs/10-release/RELEASE_MANIFEST.sha256:423`.

The later root transcript shows that the current aggregate suites pass, and the current total-phase record does match the sealed backend lifecycle test. That counterevidence reduces functional risk, but it does not make the two machine-readable source-hash assertions true for this sealed snapshot. Release evidence that expressly binds itself to source must match the source being cleared.

Required closure:

1. Rerun the post-fix lifecycle and complete phase evidence on the final test files.
2. Confirm every retained source hash matches the next sealed manifest.
3. Reconcile the assertion ledger to those regenerated artifacts and create a new release manifest.

### RT2V2-F002 - MEDIUM - README performance claims are stale

`README.md:87` states warmed p95 of 1.98 seconds and cold readiness through first result of 9.54 seconds. The sealed decisive evidence reports 2,151.062 ms warmed p95 and 9,812.494 ms cold p95 at `docs/08-validation/evidence/local-performance.json:285,356`. The assertion ledger and Validation Protocol results use the newer values.

Both current measurements pass their governed thresholds, so this is not a performance failure. It is an evaluator-facing release-claim conflict under the README reproducibility requirement.

Required closure: update the README to the exact current retained measurements, check other current release summaries for the same stale values, and include the correction in the next sealed manifest.

### RT2V2-F003 - MEDIUM - The documented local container command produces a failing healthcheck

The README local container command sets `LABELVERIFY_RUNTIME_MODE=direct` but does not set `LABELVERIFY_ALLOWED_HOST` at `README.md:95`. The image healthcheck unconditionally indexes `os.environ['LABELVERIFY_ALLOWED_HOST']` at `Dockerfile:55-56`. The application itself requires that variable only in production mode at `backend/labelverify/settings/config.py:26-31`.

Under the documented direct-mode command, the application may start, but the image healthcheck raises for the missing environment variable and marks the container unhealthy. This conclusion follows directly from the sealed source and is separate from the valid unavailable-builder gate.

Required closure: make the healthcheck safe for documented direct mode or supply the required Host environment value in the README command. Retain OCI execution proof when a builder becomes available, but do not defer this source-level inconsistency to that external gate.

## 4. Supported controls and evidence

- Architecture and engineering: business comparison, extraction, imaging, orchestration, API, and UI responsibilities remain separated. Reference values are not passed into OCR candidate location, and the result contract is validated before presentation.
- Runtime lifecycle: upload timeout, admission, near-limit spooling, cancellation, disconnect, real child timeout and replacement, shutdown overlap, and enqueue race tests are present. Current production supervisor and boundary hashes agree with the sealed manifest.
- Security and privacy: current source validates raw and decoded limits before unbounded work, owns multipart spooling, removes request data after child completion, applies production Host, Origin, HSTS, CSP, anti-framing, and no-store controls, and contains no runtime logging call or external client import. The local source-backed egress result is PASS while deployed network enforcement remains BLOCKED at `docs/08-validation/evidence/security-post-fix/source-security-scan.json:55-67`.
- Dependency posture: Python and frontend SBOM hashes exactly match `docs/10-release/DEPENDENCY_AND_MODEL_INVENTORY.md`; the SBOMs are CycloneDX 1.5 with 40 Python and 4 frontend components. Retained `pip-audit` reports no known vulnerabilities and retained production `npm audit` reports zero vulnerabilities. These are time-bound checks, not permanent vulnerability guarantees.
- Product and performance: the product corpus, mutation controls, coverage thresholds, local page load, warmed verification, cold readiness, and local memory envelope all report PASS. The cold result has limited margin below the exclusive 10,000 ms threshold and should continue to be measured on the eventual target environment.
- Release claims: `docs/10-release/RELEASE_CANDIDATE_STATUS.md` correctly labels the composite INCOMPLETE and does not claim Git, OCI, deployment, final regulatory recheck, or requester acceptance. The earlier RT reports are explicitly tied to the prior 489-entry manifest and do not clear this V2 snapshot.

## 5. Valid external and environment gates

The following documented conditions do not independently cause this verdict and must remain non-PASS until their authorized evidence exists:

- clean OCI build, rebuild, runtime identity, packaged readiness, and image provenance;
- deployed network egress enforcement, edge header provenance, TLS, public load, warm, cold, and shaped-network proof;
- native 200 percent zoom with live manual Edge and the NVDA journey;
- Git creation, clean-checkout replay, publication, public deployment, and public URL;
- final official regulatory-source recheck; and
- requester code review, functional test, UAT, acceptance, and submission approval.

The assertion ledger honestly records 56 PASS, 7 BLOCKED, 12 `PENDING_REQUESTER_GATE`, zero FAIL, zero NOT_RUN, and overall INCOMPLETE at `docs/08-validation/evidence/assertion-evidence-ledger.json:7,11-15`.

## 6. Verdict

Verdict: REWORK_REQUIRED

The sealed candidate is internally hash-clean and its local implementation is technically strong. Clearance requires correcting RT2V2-F001 through RT2V2-F003, rerunning the affected evidence against the final files, reconciling the README and assertion ledger, and sealing a new manifest for independent review. External gates may remain honestly BLOCKED or requester-controlled; they must not be used to excuse the three local defects above.
