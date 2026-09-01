# Final RT2 Technical, Security, and Release Integrity Review

Document control ID: LV-FINAL-RT2-001  
Revision: 1.0  
Date: 2026-09-01  
Reviewer role: RT2 technical, security, and release integrity  
Review mode: Read-only source and evidence review of the sealed local candidate  
Verdict: REWORK_REQUIRED

## 1. Reviewed snapshot

- Release manifest: `docs/10-release/RELEASE_MANIFEST.sha256`
- Required manifest SHA-256: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Observed manifest SHA-256: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Manifest entries independently checked: 489
- Missing entries: 0
- Hash mismatches: 0

The sealed snapshot is internally intact. This review report is created after the freeze and is not represented as a member of that snapshot.

## 2. Scope and conclusion

The review traced the I2R and FRD controls into contracts, backend and frontend implementation, tests, validation evidence, privacy and cleanup behavior, worker lifecycle, dependency locks, SBOMs, model integrity, README setup, Docker source, Fly template, QA records, and release claims.

No source-backed exploitable security vulnerability was confirmed in the implemented local application. The upload parser uses the configured spool root, exceptional parser cleanup includes cancellation, generated request paths do not use client filenames, image decode remains in the spawned worker, worker replacement cannot start after terminal stop, production Host and Origin checks are exact, production client identity accepts one parsed `Fly-Client-IP`, API responses are no-store, the HTML CSP does not permit inline styles or scripts, and documented launches disable access logs. The application source also has no required runtime outbound call, database, durable queue, analytics SDK, or browser persistence API.

The candidate is nevertheless not technically releasable as a cleared local candidate. Its own approved Build Instructions require assertion-level evidence and several specific local proofs that are absent from the sealed snapshot, while the release narrative states that all local correctness, accessibility, privacy, security, and performance gates pass. There is also conflicting governed fixture provenance and unnecessary personal filesystem identity in deliverable documentation.

## 3. Evidence that is supported

- The decisive product corpus is current and source-bound. Its recorded validator, supervisor, pipeline, contracts, fixture oracles, corpus manifest, holdout seal, mutation plan, and model manifest hashes match the sealed files. It reports zero failed cases, 456 expected and observed result rows, zero failed mutations, and zero false-clean outcomes at `docs/08-validation/evidence/local-product-corpus.json:11-57,1302-1314`.
- The retained performance record reports warmed p95 of 1,978.469 ms, warmed maximum of 3,115.038 ms, cold readiness through first result of 9,537.266 ms, and peak parent plus worker RSS of 1,612,611,584 bytes at `docs/08-validation/evidence/local-performance.json:285-363`.
- The controlled multipart parser supplies `LABELVERIFY_SPOOL_ROOT` to every `SpooledTemporaryFile` and closes parser-owned files on `BaseException` at `backend/labelverify/api/multipart.py:20-25,50-87`. The route closes uploads and removes its generated request directory after the shielded worker task reaches completion or termination at `backend/labelverify/api/routes.py:165-189,273-293`.
- The worker supervisor has a terminal stopping flag, tracked replacement threads, interruptible readiness polling, child termination and kill fallback, and post-stop replacement prevention at `backend/labelverify/orchestration/supervisor.py:65-68,89-134,185-234`.
- Production edge handling validates Host and Origin before request admission and enforces exact raw request accounting and fixed upload and server deadlines at `backend/labelverify/security/boundary.py:63-100,102-173`. The response policy supplies CSP, HSTS in production, anti-framing, referrer, permissions, and no-store controls at `backend/labelverify/security/boundary.py:192-216`.
- The Python and frontend SBOM files have the exact hashes stated in `docs/10-release/DEPENDENCY_AND_MODEL_INVENTORY.md:10-18`. Their component versions agree with the frozen lockfiles, and the three OCR model hashes agree with `ops/model-manifest.json`.
- README separates direct loopback use from production mode and does not claim that a container or deployment was run locally at `README.md:20-48,89-102`. Docker source uses digest-pinned base inputs and a non-root runtime identity at `Dockerfile:1-18,27-58`; the Fly file remains an explicit placeholder template with HTTPS and an allowed Host at `ops/fly.toml.example:1-38`.

## 4. Blocking findings

### RT2-F001 - HIGH - The mandatory assertion evidence ledger and local gate reconciliation are absent

The approved Validation Protocol requires assertion-level status for every `T-001` through `T-041`, exact composite states, and complete command, environment, input, expected, observed, counter, artifact-hash, executor, reviewer, and defect-link metadata at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:23-45,125-142`. The local Definition of Done also requires zero missing or unclassified local assertions, coverage thresholds, local page-load evidence, lifecycle recovery, accessibility scripts, and independent first-time UAT at `docs/06-build-instructions/03_QA_QC_UAT_DOD.md:79-104`.

The sealed snapshot retains aggregate prose, product-corpus JSON, backend performance JSON, and pre-fix security-scan JSON. It does not retain an assertion ledger for all 41 tests or the required composite `LOCAL_READY` and `FINAL_PASS` determinations. It also does not retain test-coverage results for the exact thresholds in `docs/05-frd/02_FRD_TEST_TRACEABILITY.md:25-31`, five-run local page-load evidence, a signed NVDA record, or timed evidence for the two required independent first-time user sessions. Despite those gaps, `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md:6-12` states that the Local Validation Protocol passed and all locally executable stop-ship assertions passed, and `docs/10-release/RELEASE_CANDIDATE_STATUS.md:8-12` states that all local gates pass.

Impact: the sealed evidence cannot reproduce or audit the claimed local release state under the candidate's governing acceptance contract. Missing proof cannot be promoted to PASS.

Required closure:

1. Create the governed assertion ledger for every `T-001` through `T-041` with all required metadata.
2. Execute or retain the missing local coverage, page-load, NVDA, independent first-time UAT, and other required local records.
3. Reconcile every assertion with the defect ledger and compute the exact composite state.
4. Correct the validation and release status until the evidence reaches the required state, then generate a new sealed manifest.

### RT2-F002 - HIGH - The retained lifecycle evidence does not support the complete security and cleanup PASS claim

The governing I2R verification obligations require concurrent slow multipart requests, near-limit spool use, worker hang and recovery, repeated cancellation, disconnect storm, shutdown ownership, blocked-egress behavior, content-log scanning, and zero final resource counters at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:276-287`. FR-041 further requires controlled stalls across client validation, upload, parent validation, real child decode, queue, inference, response transfer, render, and announcement, with exact cancellation, late-response, disconnect, worker-recovery, and zero-cleanup outcomes at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:63`.

The retained source tests provide useful but narrower proof: one successful API request cleans its spool, parser-level `RuntimeError` and `CancelledError` close rolled files, and two supervisor tests cover terminal stop and interrupted replacement warmup at `backend/tests/test_api.py:128-146`, `backend/tests/test_multipart.py:49-94`, and `backend/tests/test_supervisor_boundary.py:236-258`. The product corpus adds one controlled inference-timeout case. No retained executable record proves the complete route-level cancellation and disconnect ownership matrix, concurrent slow and near-limit uploads, real decoder stall, shutdown with an owned job, or final handles, directories, reservations, jobs, and child counters. The only canonical machine-readable security scan retained under `docs/08-validation/evidence/security-pre-fix/` describes the vulnerable pre-fix snapshot, while `docs/08-validation/SECURITY_VALIDATION.md:20-30` records the post-fix disposition only in prose.

Impact: the source corrections are plausible and no bypass was confirmed, but the blanket local security, privacy, cancellation, resource, and cleanup PASS at `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md:31-39,49-61` exceeds the retained proof. This is a release-integrity failure against a stop-ship class that explicitly includes cleanup leaks and unkillable workers.

Required closure:

1. Run the complete local lifecycle matrix on the sealed corrected implementation.
2. Retain machine-readable outcomes and zero-final-resource counters, including route cancellation, disconnect, upload timeout, maximum accepted input, real worker stall, replacement, and shutdown overlap.
3. Retain a post-fix security review artifact bound to the corrected snapshot and link it through the assertion ledger.

### RT2-F003 - MEDIUM - The accepted fixture baseline conflicts with the current sealed fixture package

`docs/07-development/CONTRACT_BASELINE.md:57-73` declares the fixture and oracle baseline accepted and says later changes require formal change control and renewed consumer verification. It records the corpus manifest as `cf55ca7c...`, the holdout seal as `7dc3c01e...`, and the mutation plan as `12bc5b89...` at lines 63-65. The actual sealed values, also bound into the passing corpus evidence, are `c7ba0668...`, `fa43f21a...`, and `7b35bf40...`.

Impact: current functional evidence is internally consistent, but the package contains two incompatible authoritative provenance statements. A reviewer cannot determine from the accepted baseline alone which fixture change was approved.

Required closure: mark the earlier hashes as historical or superseded, link the final correction and consumer revalidation, record the current authoritative hashes, and generate a new sealed manifest.

### RT2-F004 - MEDIUM - Deliverable documentation contains unnecessary personal filesystem identity

FR-035 requires zero unnecessary personal details or private design-source findings in the repository at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:57`. The sealed deliverables include the workstation username and private Downloads paths at `docs/intake/design-reference-analysis.md:13-14`, `docs/reviews/intake/RT1_REQUIREMENTS_FIDELITY.md:28,51-52`, and `docs/reviews/intake/RT2_UX_STAKEHOLDER.md:44-45`.

Impact: publishing the candidate as planned would unnecessarily disclose a personal identifier and private workstation layout, contradicting the repository privacy gate.

Required closure: replace absolute local paths with repository-neutral artifact identifiers and hashes, repeat the personal/private-content scan, and generate a new sealed manifest.

## 5. External gates accepted as pending

The following conditions do not cause this verdict because the review instruction permits them as external gates and the candidate does not misrepresent them as locally proven:

- Git repository creation, clean-checkout replay, and publication;
- clean OCI build, rebuild, runtime identity, governed-hash readback, and image digest;
- public deployment URL and deployed edge, TLS, Fly header provenance, warm, cold, load, shaped-network, platform logging, and retention evidence;
- final official-source regulatory recheck; and
- requester code review, functional test, UAT, and acceptance.

The source also does not establish a filesystem quota, read-only container root, or network-level denied-egress policy. The as-built authority records these limitations accurately at `docs/04-i2r-ae/09_I2R_AS_BUILT_SECURITY_RUNTIME_ADDENDUM.md:19-28,44-56`, so they are not treated as hidden local passes.

## 6. Advisory observations

- The SBOM and lockfile identities are consistent, but raw `pip-audit` and `npm audit` output is not retained. The corrected assertion ledger should retain time-bound audit results rather than relying only on prose attestation.
- Several stage documents retain Draft, Candidate, or Pending status text even though later gate-result documents supersede them. This is not independently blocking, but one authority and supersession index would reduce evaluator ambiguity.
- The custom Starlette parser is intentionally coupled to framework internals such as `_current_part` and `_files_to_close_on_error`. Dependency upgrades should keep the real spill-location and exceptional-cleanup regression as mandatory compatibility tests.

## 7. Verdict

Verdict: REWORK_REQUIRED

The source-backed product behavior, sealed corpus, performance record, and corrected security mechanisms are strong. Clearance requires closing RT2-F001 through RT2-F004, rerunning the affected local gates on one corrected snapshot, and producing a new release manifest for independent final review.
