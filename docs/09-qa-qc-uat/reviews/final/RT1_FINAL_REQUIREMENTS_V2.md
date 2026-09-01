# Final RT1 V2 Requirements Fidelity and Traceability Review

Document control ID: LV-FINAL-RT1-002  
Revision: 2.0  
Date: 2026-09-01  
Reviewer role: RT1 requirements fidelity and traceability  
Review mode: Independent read-only review of the exact sealed local candidate  
Verdict: REWORK_REQUIRED

## 1. Immutable review target

- Release manifest: `docs/10-release/RELEASE_MANIFEST.sha256`
- Required manifest SHA-256: `9EBD7ABEF664A24680987C070EDEA5A5C2EF4861BE79344246516B890BDF16A3`
- Observed manifest SHA-256: `9EBD7ABEF664A24680987C070EDEA5A5C2EF4861BE79344246516B890BDF16A3`
- Manifest entries: 528
- Entries independently hash-verified: 528
- Missing entries: 0
- Hash mismatches: 0
- Duplicate paths: 0

The manifest-listed content is internally intact and was treated as immutable. This V2 review report is created after the freeze and is not represented as part of the reviewed manifest.

## 2. Review scope and method

The review compared the sealed candidate with:

- the sanitized take-home assignment, stakeholder discovery, and requester instructions;
- Intake, scope, success criteria, assumptions, decisions, source traceability, and design-reference disposition;
- BAIRD defined and undefined analysis and the source disposition matrix;
- I2R Architecture and Engineering, data flow, interfaces, security, UX workflow, decisions, and traceability;
- the FRD, test traceability, Build Instructions, work-package ownership, QA/QC, UAT, and Definition of Done;
- production source, generated contracts, governed fixtures, independent oracles, tests, lockfiles, container source, and deployment template;
- the assertion ledger, product corpus, performance, security, privacy, accessibility, UAT, defect, and release evidence; and
- the README and release statements required for the take-home submission.

Independent static checks also verified all 528 manifest hashes, all local Markdown link targets, prohibited Unicode dash characters, requester-specific absolute paths, production imports, unsupported batch or legal-decision wording, and Git or deployment state.

## 3. Requirements fidelity and traceability assessment

| Area | Result | Decisive evidence |
|---|---|---|
| Original assignment and stakeholder discovery | ALIGNED | `docs/intake/assignment-source-baseline.md` preserves the 150,000 application workload, 47-agent context, manual comparison workflow, about-five-second adoption need, simple UX, human judgment, exact warning concern, degraded images, restricted outbound traffic, repository deliverable, README deliverable, and deployed URL deliverable. |
| Intake | ALIGNED | The approved Intake bounds a standalone proof of concept, manual application entry, synthetic or sanitized data, selected distilled-spirits scope, human decision authority, and complete-core priority. The three Intake re-reviews are CLEAR. |
| BAIRD | ALIGNED | `docs/03-baird/02_BAIRD_SOURCE_DISPOSITION_MATRIX.md` dispositions 58 of 58 source requirements and 3 of 3 requester decisions. The V4 BAIRD reviews are unanimously CLEAR. |
| I2R Architecture and Engineering | ALIGNED | The modular monolith, same-origin boundary, reference-blind observation path, supervised killable worker, deterministic 19-check engine, session-only UI, no database, local OCR, and bounded ingress/egress design support the validated requirements without unnecessary distributed infrastructure. |
| FRD and test traceability | ALIGNED | All 31 BAIRD requirements map downstream. `FR-001` through `FR-041` each have one governed `T-001` through `T-041` test identity and binary acceptance. The combined I2R and FRD gate is CLEAR. |
| Build Instructions | ALIGNED | `docs/06-build-instructions/02_WORK_PACKAGE_LEDGER.md` maps all 41 features to primary ownership, tasks, dependencies, tests, and evidence. The BI gate records three CLEAR reviews on the same V3 baseline. |
| Product scope | ALIGNED | The source implements one to six label panels, manual reference values, built-in sample, 19 selected checks, evidence-linked comparison, typed failures, cancellation, retry, guarded reset, notes and disposition, and human review. There is no batch route or UI, no COLAs Online integration, no official TTB seal, no approval or rejection action, no database, and no required runtime cloud inference. |
| Grok and Gemini design inputs | ALIGNED | `docs/intake/design-reference-analysis.md` treats the supplied concepts as non-authoritative. Useful side-by-side comparison, evidence focus, concise statuses, and warning-detail patterns were retained. Official seals, approval semantics, fictional regulatory text, and decorative scanning effects were rejected. |
| Local correctness evidence | ALIGNED | The assertion ledger records 75 assertions across 41 tests: 56 PASS, 0 FAIL, 0 NOT_RUN, 7 BLOCKED, and 12 `PENDING_REQUESTER_GATE`. Product-corpus evidence records 30 of 30 cases, 456 of 456 expected rows, 8 of 8 mutation controls, and zero false-clean results. |
| Internal UAT | ALIGNED | Two independent non-frontend reviewers completed both no-help journeys within the governed limits: Reviewer 1 at 46.135 and 185.816 seconds, and Reviewer 2 at 29.561 and 139.780 seconds. Requester UAT remains separate. |
| Submission posture | HONESTLY INCOMPLETE | `README.md` and `docs/10-release/RELEASE_CANDIDATE_STATUS.md` state that no Git repository, GitHub repository, Fly application, public URL, or deployment exists. They do not claim the final assignment was submitted. |

The product direction, selected objectives, user journeys, architecture, feature set, and scope boundaries remain faithful to the assignment. Batch exclusion is justified by the assignment preference for a complete working core over an ambitious incomplete feature. No requirement drift, false legal-authority claim, false TTB affiliation, or false deployment claim was found.

## 4. Actionable product and process defects

### RT1-V2-F001 - HIGH - The documented local container command produces an unhealthy container

Evidence:

- `Dockerfile:35` sets the image default to production mode, but the image defines no `LABELVERIFY_ALLOWED_HOST` value.
- `README.md:95` changes only `LABELVERIFY_RUNTIME_MODE` to `direct` for the documented local container command and does not supply an environment file or `LABELVERIFY_ALLOWED_HOST`.
- `Dockerfile:56` constructs every health request with `os.environ['LABELVERIFY_ALLOWED_HOST']`. With the README command, this expression raises `KeyError` before making the readiness request.
- `backend/labelverify/settings/config.py:29-31` requires the allowed Host only in production, so direct mode intentionally supports operation without that variable. The healthcheck imposes a conflicting unconditional requirement.
- `docs/09-qa-qc-uat/DEFECT_LEDGER.md:47` marks `PKG-F002` CLOSED on the claim that the container health request uses the configured allowed Host. That closure does not cover the documented direct-mode command where no allowed Host is configured.

Impact:

The application process can start in direct mode, but Docker marks the documented evaluation container unhealthy. Packaged readiness cannot pass as written. This is a source and documentation defect visible without an OCI builder, not merely the honest `ENV-OCI-001` execution blocker. It invalidates the current `PKG-F002` closure and would prevent the future `T-028-A-OCI-READINESS` proof.

Required correction:

1. Make the healthcheck valid in both governed runtime modes. A direct-mode health request must not require an absent production-only variable.
2. Add a focused regression that proves the exact documented container environment yields a successful health command and readiness request.
3. Reopen and re-close `PKG-F002` with corrected static and OCI runtime evidence.
4. When an OCI builder is available, execute the existing non-root, readiness, clean-build, and clean-rebuild assertions against the corrected image.

### RT1-V2-F002 - MEDIUM - README performance claims do not match the sealed decisive evidence

Evidence:

- `README.md:87` claims warmed p95 of 1.98 seconds and cold readiness through first result of 9.54 seconds.
- `docs/08-validation/ASSERTION_EVIDENCE_LEDGER.md:96` identifies the decisive sealed performance artifact and reports warmed p95 of 2,151.062 ms over 30 of 30 runs and cold p95 of 9,812.494 ms over 5 of 5 runs.
- `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md:35` confirms cold p95 and maximum of 9,812.494 ms.
- `docs/08-validation/evidence/local-performance.json` is the machine-readable source bound to the assertion ledger with SHA-256 `3db1353d9ed0f84e9d9a8227d2eb644c36d992592cb6d5e0dacde15a25dac905`.
- `FR-033` requires every README claim to match tests and evidence and defines a claim conflict as FAIL.

Impact:

Both measured results still meet their governed thresholds, so this is not a product performance failure. It is a false submission-document claim and a traceability failure in one of the assignment's explicitly required deliverables. The local `T-033-A-LOCAL-DELIVERY-PACKAGE` assertion and the zero-open-process-defect statement must be reconsidered until the README is corrected.

Required correction:

1. Replace the stale README values with the exact decisive sealed performance values, with units and run counts.
2. Repeat the cross-artifact claim-consistency check.
3. Link the correction through the defect and assertion ledgers.

No other actionable product, requirements, architecture, engineering, feature, UX, QA, or delivery defect was found in this review.

## 5. Seven honest environment or deployment blockers

These seven assertion states are explicit, evidence-backed, and are not the cause of the REWORK_REQUIRED verdict:

| Assertion | Governing blocker | Required future evidence |
|---|---|---|
| `T-028-A-OCI-NONROOT` | `ENV-OCI-001` | OCI runtime identity and filesystem proof |
| `T-028-A-OCI-READINESS` | `ENV-OCI-001` | Corrected packaged readiness and governed-asset hashes |
| `T-029-A-NETWORK-EGRESS-ENFORCEMENT` | `REQ-DEPLOY-001` | Deployed network-policy inspection |
| `T-030-A-NATIVE-200-ZOOM-EDGE` | `ENV-A11Y-001` | Native 200 percent zoom and live manual Edge visual inspection |
| `T-030-A-NVDA` | `ENV-NVDA-001` | Manual NVDA journey transcript |
| `T-033-A-OCI-CLEAN-BUILD` | `ENV-OCI-001` | Clean OCI build, digest, and governed identities |
| `T-033-A-OCI-CLEAN-REBUILD` | `ENV-OCI-001` | Second clean OCI build and comparable provenance |

The Docker healthcheck finding must be corrected before the blocked OCI readiness assertion can pass. That static defect does not make the environment blocker dishonest.

## 6. Twelve honest requester-controlled gates

These are the only assertions marked `PENDING_REQUESTER_GATE`. Their pending state is consistent with the requester's instruction to keep the project local until approval for GitHub setup and deployment:

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

The source repository URL and deployed application URL remain required take-home deliverables, but they are valid later gates under the requester's explicit authority boundary. The candidate does not falsely claim they exist.

## 7. Additional integrity observations

- All local Markdown links in 135 manifest-listed Markdown files resolve to existing targets.
- No manifest-listed readable file contains U+2010 through U+2015.
- No manifest-listed readable file contains a requester-specific `C:/Users` or `C:\Users` path.
- Production source contains no expected-result oracle or research import. The only fixture reference is the governed built-in sample manifest path.
- Production UI text contains no Approve, Reject, TTB approved, or compliant decision claim.
- `.git` is absent and root `fly.toml` is absent. Only `ops/fly.toml.example` is present as a template.
- Historical stage documents sometimes preserve draft-era status labels, but the current gate results identify the authoritative CLEAR baselines. This is advisory and does not create an additional defect.
- The assertion ledger's final-manifest placeholder is not treated as a defect because a file inside a hash manifest cannot safely contain that manifest's final hash without circularity. This V2 report supplies the immutable manifest binding for the independent review.

## 8. Verdict and re-review entry condition

Verdict: REWORK_REQUIRED

The sealed candidate substantially meets and often exceeds the take-home's functional, engineering, validation, documentation, and usability expectations. It cannot receive CLEAR because the documented container healthcheck is defective and the required README contains performance values that conflict with the sealed decisive evidence.

Re-review may begin after RT1-V2-F001 and RT1-V2-F002 are corrected, affected defects and assertions are reconciled, focused and full local validation pass, OCI assertions remain honestly BLOCKED unless actually executed, and a new release manifest is generated for all final reviewers.
