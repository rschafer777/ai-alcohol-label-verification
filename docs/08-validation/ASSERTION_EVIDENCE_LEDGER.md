# Assertion Evidence Ledger

Document control ID: LV-VAL-AEL-001  
Revision: 0.3  
Date: 2026-09-01  
Product snapshot: `PENDING_FINAL_RELEASE_MANIFEST`  
Overall state: INCOMPLETE

This ledger is the retained pre-final SDLC assertion compilation and is not a current-source evidence index. It does not include the later user-supplied 50-image diagnostic or subsequent regression-count and performance refreshes. Current candidate results and hashes are governed by `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md`, `docs/08-validation/TEST_IMAGES_VALIDATION_REPORT.md`, the evidence files they cite, and `docs/10-release/RELEASE_MANIFEST.sha256`. Raw unit-coverage outputs named in this historical ledger are intentionally excluded from the public package; the governed coverage summary and documented test commands reproduce those local artifacts.

## 1. Decision

The local evidence package has no failed or unexecuted assertion. It does not yet satisfy the full local Definition of Done because seven assertions are BLOCKED by unavailable OCI, accessibility, or deployed network-policy capabilities. The 12 exact requester-controlled assertions remain `PENDING_REQUESTER_GATE`.

Current machine-ledger totals:

| Measure | Count |
|---|---:|
| Governed tests | 41 |
| Assertion records | 75 |
| PASS | 56 |
| FAIL | 0 |
| NOT_RUN | 0 |
| BLOCKED | 7 |
| PENDING_REQUESTER_GATE | 12 |
| FINAL_PASS tests | 33 |
| LOCAL_READY tests | 4 |
| INCOMPLETE tests | 4 |

The authoritative assertion records are in `docs/08-validation/evidence/assertion-evidence-ledger.json`. Each record contains the stable assertion ID, mapped FR, scope, snapshot placeholder, UTC timestamp, environment, command, inputs, expected result, observed result, status, composite state, counters, artifact hashes, executor, reviewer, and defect links required by LV-BI-003 Section 7.

## 2. Test-level traceability

| Test | FR | Composite state | Assertion result summary |
|---|---|---|---|
| `T-001` | `FR-001` | FINAL_PASS | 1 PASS |
| `T-002` | `FR-002` | FINAL_PASS | 1 PASS |
| `T-003` | `FR-003` | FINAL_PASS | 1 PASS |
| `T-004` | `FR-004` | FINAL_PASS | 1 PASS |
| `T-005` | `FR-005` | FINAL_PASS | 1 PASS |
| `T-006` | `FR-006` | FINAL_PASS | 1 PASS |
| `T-007` | `FR-007` | FINAL_PASS | 1 PASS |
| `T-008` | `FR-008` | FINAL_PASS | 1 PASS |
| `T-009` | `FR-009` | FINAL_PASS | 1 PASS |
| `T-010` | `FR-010` | FINAL_PASS | 1 PASS |
| `T-011` | `FR-011` | FINAL_PASS | 1 PASS |
| `T-012` | `FR-012` | FINAL_PASS | 1 PASS |
| `T-013` | `FR-013` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-014` | `FR-014` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-015` | `FR-015` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-016` | `FR-016` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-017` | `FR-017` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-018` | `FR-018` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-019` | `FR-019` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-020` | `FR-020` | FINAL_PASS | Functional and coverage assertions PASS |
| `T-021` | `FR-021` | FINAL_PASS | 1 PASS |
| `T-022` | `FR-022` | FINAL_PASS | Functional and 100 percent aggregation branch assertions PASS |
| `T-023` | `FR-023` | FINAL_PASS | 1 PASS |
| `T-024` | `FR-024` | FINAL_PASS | 1 PASS |
| `T-025` | `FR-025` | FINAL_PASS | 1 PASS |
| `T-026` | `FR-026` | FINAL_PASS | 1 PASS |
| `T-027` | `FR-027` | FINAL_PASS | 1 PASS |
| `T-028` | `FR-028` | INCOMPLETE | Local readiness PASS; OCI non-root and packaged readiness BLOCKED |
| `T-029` | `FR-029` | INCOMPLETE | Local lifecycle/canary PASS; deployed network-egress enforcement BLOCKED |
| `T-030` | `FR-030` | INCOMPLETE | Automated and manual keyboard/focus PASS; native 200 percent zoom/manual Edge and NVDA BLOCKED |
| `T-031` | `FR-031` | LOCAL_READY | Three local metrics PASS; four deployed metrics pending requester gate |
| `T-032` | `FR-032` | FINAL_PASS | 30 cases, 456 checks, 8 mutations, and zero false clean PASS |
| `T-033` | `FR-033` | INCOMPLETE | Local delivery package PASS; two OCI assertions BLOCKED; five requester assertions pending |
| `T-034` | `FR-034` | FINAL_PASS | Static architecture and all governed coverage thresholds PASS |
| `T-035` | `FR-035` | FINAL_PASS | Unicode and repository-neutral path scans PASS |
| `T-036` | `FR-036` | FINAL_PASS | Batch no-go assertion PASS |
| `T-037` | `FR-037` | LOCAL_READY | Two independent timed local UAT reviewers PASS; requester UAT pending |
| `T-038` | `FR-038` | LOCAL_READY | Local rule provenance PASS; release source recheck pending |
| `T-039` | `FR-039` | FINAL_PASS | Automated smoke and full Chrome browser privacy matrix PASS |
| `T-040` | `FR-040` | LOCAL_READY | Local boundary matrix PASS; public edge pending |
| `T-041` | `FR-041` | FINAL_PASS | Controlled baseline, lifecycle, and complete total-phase matrix PASS |

## 3. Governed coverage result

Coverage was calculated only across the governed business-module subsets, not inferred from repository aggregates.

| Scope | Lines | Branches | Threshold | Result |
|---|---:|---:|---:|---|
| Backend business modules | 503 of 531, 94.73% | 183 of 210, 87.14% | At least 80% line and branch | PASS |
| Comparison plus warning policies | 151 of 155, 97.42% | 62 of 64, 96.88% | At least 90% branch | PASS |
| Aggregation | 23 of 23, 100% | 12 of 12, 100% | 100% branch | PASS |
| Frontend business modules | 365 of 397, 91.94% | 284 of 336, 84.52% | At least 80% line and branch | PASS |

`QA-002` is CLOSED by the independent retained coverage retest. The approved thresholds were not reduced.

## 4. Decisive local evidence

| Evidence | Result | SHA-256 |
|---|---|---|
| `docs/08-validation/evidence/local-root-check.txt` | Ruff, strict MyPy, 122 Python tests, ESLint, strict TypeScript, 34 frontend tests, production build, Chrome and Edge core E2E, Chrome privacy E2E, and Unicode scan PASS | `a16308b35757414dc369a882d7b96b96685f2dbfe1b509b348bab2d87c73344e` |
| `docs/08-validation/evidence/governed-coverage-summary.json` | All four governed coverage scopes PASS | `6b19fa2985828ac3787fe41b89d91bcaf79db5a67ef6f7cb0989c2b1dcf188db` |
| `docs/08-validation/evidence/local-product-corpus.json` | 30 of 30 cases, 456 of 456 rows, 8 of 8 mutations, zero false clean | `9f94782f061bcc3190bf42d5532443a183ae08863cfca22f78ed0777893623f8` |
| `docs/08-validation/evidence/local-performance.json` | Warm 30 of 30 at 2,151.062 ms p95; cold 5 of 5 at 9,812.494 ms p95 | `3db1353d9ed0f84e9d9a8227d2eb644c36d992592cb6d5e0dacde15a25dac905` |
| `docs/08-validation/evidence/local-page-load.json` | Five of five loads; 113.052 ms p95 | `ce30bd63f8d659a8821dd2bd151dfa241bfa0627f156aedb2fbc5ef9b1e130de` |
| `docs/08-validation/evidence/security-post-fix/lifecycle-matrix.json` | 45 focused and 121 full Python tests PASS with cleanup/canary evidence and 21 of 21 current source hashes | `48a4be14ec13c1a0137eb078461c745fe2604bbbe756346d505b6c4f9f8fa360` |
| `docs/08-validation/evidence/security-post-fix/source-security-scan.json` | Runtime content, path, and no-required-egress source checks PASS; deployed network enforcement remains BLOCKED | `2362f3db40e4a060d6fcaf89222d2128b225a10eb02444049f59daddcb5e9194` |
| `docs/08-validation/evidence/security-post-fix/SECURITY_POST_FIX_REPORT.md` | Security lifecycle and source evidence summary; all local assertions PASS | `7e2042ae87aff70319874b3e931742393663fb16c0668db3e9cb53abf334de13` |
| `docs/08-validation/evidence/browser-privacy-matrix.json` | Complete required Chrome browser lifecycle and storage matrix PASS | `ef166279fd401d076d52266edfef77d7da7bdc56cf9a416c611e16adeccde6e9` |
| `docs/08-validation/evidence/total-phase-matrix.json` | All 11 recorded phase groups PASS, all 6 current source hashes match, and project/temp paths are sanitized | `4b9442d08e05dbbbe605dae2f39ba58b8691415de99ab329613def713b4f8f44` |
| `README.md` | Direct-container Host and decisive 2.151-second warm and 9.812-second cold claims are corrected | `7bce8f79d2482d49c6e7318e19f8cd78dbc6002de644bf51fc3d65efc872be58` |
| `docs/09-qa-qc-uat/DEFECT_LEDGER.md` | Revision 0.6 closes `RTV2-001` through `RTV2-004` with focused and full regression evidence | `545e150f87e7f088d5a6c347debfd701d5944dbba502c686a1506fef608a85a4` |
| `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md` | Revision 1.4 reconciles the 122-test root gate and the unchanged incomplete composite | `35b5861008700d036da3a51c2d0ff17163cff0480d9383766872bf191f1c47f1` |
| `docs/10-release/RELEASE_CANDIDATE_STATUS.md` | Revision 1.4 records V2 correction closure without promoting external gates | `3ff5f21f35ec42e47469f1d1d1813fe6838bcac3ad789e38a3ec5709c2e6bea8` |
| `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md` | LV-I2R-002 Revision 1.1 controlled T-041 timing and phase baseline | `068ccdaa991ceb5de99658680aeb15ec3c836c9e60ee971bfcb342ce7ac9b833` |
| `docs/04-i2r-ae/09_I2R_AS_BUILT_SECURITY_RUNTIME_ADDENDUM.md` | LV-I2R-009 Revision 1.1 active as-built T-041 interpretation | `cf91c3de794d22bf77eeff80fce47edd8e2f2166deb0c3d00b6391dbc59a1eca` |
| `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md` | LV-FRD-001 Revision 1.1 FR-041 acceptance baseline | `7338e368a97e3e789b6cf1c3b481e65e54642a6d0a7d9e603976fd595ebb7dd1` |
| `docs/05-frd/02_FRD_TEST_TRACEABILITY.md` | LV-FRD-002 Revision 1.1 T-041 traceability baseline | `62170150fd8749bb7c0e6d96f0798385bb136c111de9421903d6cbe73edc4d51` |
| `docs/05-frd/I2R_FRD_RT_REMEDIATION.md` | LV-FRD-003 Revision 1.4 controlled change record | `04ad1dfb73558e1904c9272429662d84837173279d3eec7800b2d7256458ea66` |
| `docs/09-qa-qc-uat/evidence/UAT_REVIEWER_1.md` | UAT-001 and UAT-002 PASS | `a53607f716b213ea99eb6eada76fcee2c484aff8ecba46b86f37636d9fc545bf` |
| `docs/09-qa-qc-uat/evidence/UAT_REVIEWER_2.md` | UAT-001 and UAT-002 PASS | `001181b61ba6810417127cfb1881b084d5d8ce865ce49806ec268d1180034b49` |
| `docs/08-validation/evidence/pip-audit.json` | 57 synchronized packages, zero known vulnerabilities | `2586ffbfd9a72cd00e2f8b975e925a360e56521c528383872675095c1a9335da` |
| `docs/08-validation/evidence/npm-audit-production.json` | Zero production vulnerabilities | `4bf7808ba7730114a719cd9f15cb3ae5aa39c1fe0fcda99f22df22a7d3cd2065` |
| `docs/08-validation/evidence/repository-neutral-path-scan.txt` | Zero requester-specific absolute paths and zero raw-evidence profile paths | `5ebf59d3bed335ac6e15edd1015e36252ffccb03d09712691fcc3629c5203fa4` |

## 5. Blocked assertions

| Assertion | Status | Governing record | Required closure evidence |
|---|---|---|---|
| `T-028-A-OCI-NONROOT` | BLOCKED | `ENV-OCI-001` | OCI runtime identity and filesystem proof |
| `T-028-A-OCI-READINESS` | BLOCKED | `ENV-OCI-001` | Packaged readiness and governed-asset hashes |
| `T-029-A-NETWORK-EGRESS-ENFORCEMENT` | BLOCKED | `REQ-DEPLOY-001` | Deployed network-policy inspection |
| `T-030-A-NATIVE-200-ZOOM-EDGE` | BLOCKED | `ENV-A11Y-001` | Exact native 200 percent zoom and live manual Edge visual inspection |
| `T-030-A-NVDA` | BLOCKED | `ENV-NVDA-001` | Manual NVDA core-journey transcript after requester action authorization |
| `T-033-A-OCI-CLEAN-BUILD` | BLOCKED | `ENV-OCI-001` | Clean OCI build, digest, and governed identities |
| `T-033-A-OCI-CLEAN-REBUILD` | BLOCKED | `ENV-OCI-001` | Second clean OCI build and comparable provenance |

No blocked assertion is relabeled as PASS. The manual keyboard and focus defect `A11Y-001` is CLOSED; the exact native zoom/manual Edge and NVDA environment gates remain separate.

## 6. Exact requester-controlled assertions

The following 12 assertions are the only records using `PENDING_REQUESTER_GATE`:

1. `T-033-A-REPO-CHECKOUT`
2. `T-033-A-PUBLIC-URL`
3. `T-031-A-DEPLOYED-LOAD`
4. `T-031-A-DEPLOYED-WARM`
5. `T-031-A-DEPLOYED-COLD`
6. `T-031-A-SHAPED-NETWORK`
7. `T-040-A-PUBLIC-EDGE`
8. `T-038-A-RELEASE-RECHECK`
9. `T-033-A-REQUESTER-CODE-REVIEW`
10. `T-033-A-REQUESTER-FUNCTIONAL-TEST`
11. `T-037-A-REQUESTER-UAT`
12. `T-033-A-FINAL-SUBMISSION-APPROVAL`

## 7. Defect-ledger cross-check

- `QA-002`, governed coverage, is CLOSED and linked to the passing coverage assertions.
- `QA-003`, lifecycle and privacy evidence, is CLOSED and linked to the current 45-focused and 121-full-test post-fix matrix assertions.
- `A11Y-001`, hidden duplicate keyboard focus, is CLOSED and linked to the manual keyboard retest.
- `QA-004`, two independent timed UAT reviewers, is CLOSED and linked to both signed reviewer records.
- `QA-001`, the missing assertion-level evidence ledger, is CLOSED by this independently reconciled human and machine package.
- `QA-006`, inconsistent validation and release status claims, remains CLOSED by the current Revision 1.4 validation and release records.
- `RTV2-001` and `RTV2-002`, the direct-container Host and README performance claims, are CLOSED and linked to `T-033-A-LOCAL-DELIVERY-PACKAGE`.
- `RTV2-003`, stale lifecycle and phase source hashes, is CLOSED and linked to the current `T-029` and `T-041` evidence.
- `RTV2-004`, the requester-local temp path in phase evidence, is CLOSED and linked to the current `T-035` and `T-041` evidence.

## 8. Remaining release blockers

No process defect remains open. OCI, exact native zoom/manual Edge, NVDA, deployed network enforcement, Git, deployment, final regulatory recheck, and requester acceptance remain honest external or environment gates.

This package does not claim final assignment submission readiness while those gates remain open.
