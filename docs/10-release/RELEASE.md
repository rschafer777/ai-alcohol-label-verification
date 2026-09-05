# Release and Operational Handoff

Document ID: LV-REL-001  
Status: CR-002 local release gates complete; identical-candidate RT, commit, deployment, and requester UAT pending

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-03 | Recorded the initial release candidate and deployment | Initial release candidate |
| 1.1 | 2026-09-04 | Reclassified earlier evidence as the CR-002 baseline and opened corrective release gates | CR-002 |
| 1.2 | 2026-09-04 | Recorded completion of the corrective local source, representative-corpus, accuracy, holdout, and security gates | CR-002 |
| 1.3 | 2026-09-04 | Recorded final-review rejection and required integrity closure before corrective publication | CR-002 |
| 1.4 | 2026-09-05 | Recorded closure of the third architecture challenge and regenerated local evidence before final refreeze | CR-002 |
| 1.5 | 2026-09-05 | Recorded closure of mixed-source response and persisted-reference reconciliation | CR-002 |
| 1.6 | 2026-09-05 | Recorded complete local release-gate and final independent security-review passage | CR-002 |

The existing deployment and evidence below describe the initial candidate. They remain valid historical records but do not establish CR-002 completion. The corrective candidate can replace the public deployment only after the updated lifecycle requirements, implementation, VP, QA/QC, unique representative Azure performance, release manifest, and three final independent reviews pass.

The first frozen CR-002 snapshot was held after one Clear and two Not Clear final reviews. No rejected snapshot was committed, pushed, or deployed as CR-002. The identified mutation-boundary, unresolved-type, field-provenance, correction-replay, telemetry, persistence-order, error-contract, and source-evidence-binding gaps were returned to engineering with regression requirements. Publication remains blocked until the corrected candidate completes the full release gate and all three reviewers return Clear on the same tree.

Three later architecture challenges were also held rather than promoted. Their stale add-panel baseline, correction replay, family inference, sulfite, numeric audit, browser evidence, all-field provenance, reviewer-family precedence, fresh-evidence invalidation, polygon-boundary, and response-to-history source-consistency findings now have focused regressions. The corrected runtime passed the complete local release gate: 411 Python tests, 38 frontend tests, the 30-product governed corpus, 221 individual private-image requests, 155 grouped-product requests, the current ground-truth score, the sealed holdout, dependency audits, and the 375-entry release manifest. After the final requirements review found ambiguous BAIRD numbering, that documentation-control defect was corrected, a regression was added, and the full source gate passed 412 tests without a runtime-code change. A final independent security diff review covered all 46 changed executable and contract surfaces with no deferred or reportable finding. Those are local facts only; three identical-candidate reviews, commit, deployment identity, and live certification remain separate gates.

## Deliverable contents

- Complete Python and TypeScript source
- Locked Python and frontend dependency files
- Versioned API, check, error, and regulatory contracts
- Local OCR model acquisition manifest with cryptographic hashes
- Synthetic sample and governed test fixtures
- Unit, integration, browser, accessibility, performance, security, and deployment tests
- Private 221-image production-API and server-grouping evidence
- Field-level pixel ground truth for 70 private images and a 42-image disposition oracle
- Numbered documentation from discovery through UAT
- OCI Dockerfile, Azure infrastructure template, and GitHub OIDC workflow
- README with setup, run, test, approach, tools, assumptions, trade-offs, and limitations

The private raw images are excluded from the public repository because public redistribution rights were not established. Public evidence retains case identifiers, image basenames needed to join the local oracle, content hashes, test results, field-read flags, timing, and field-level scores. It does not publish raw image bytes, machine-specific paths, or raw OCR strings. Basenames are evidence keys only and do not participate in runtime selection or extraction.

## Release controls

The release owner shall:

1. Run the complete validation protocol.
2. Obtain three independent RT Clear decisions on one frozen manifest.
3. Confirm the repository root, branch `main`, and intended remote.
4. Review `.gitignore` and staged files.
5. Exclude local virtual environments, models, node modules, caches, coverage, temporary files, local environment values, local agent instructions, handoff drafts, and images without public redistribution approval.
6. Scan staged text for credentials, keys, tokens, passwords, personal information, machine-specific paths, and protected Azure identifiers.
7. Confirm no staged file exceeds GitHub limits.
8. Confirm no LICENSE file exists unless the owner makes an explicit license choice.
9. Commit without rewriting history and push `main` without force.
10. Dispatch the protected demo workflow for the exact application commit.
11. Verify the remote commit, public archive, Azure metadata, health, UI, core analysis, batch behavior, and history behavior.
12. Record the application commit, documentation commit, workflow, immutable image digest, public URL, tests, exclusions, and UAT entry status.

## Deployment design

GitHub Actions uses OIDC to authenticate to Azure. It validates the source, builds the OCI image, runs the image locally for readiness, pushes an immutable digest to the private registry, deploys Azure Container Apps through the governed ARM template, reads back effective security configuration, performs public HTTPS smoke and timing checks, and restores the last governed digest if a post-mutation step fails.

## Operations

- Liveness: `/health/live`
- Readiness: `/health/ready`
- Build and contract metadata: `/api/v1/meta`
- Runtime inference: local RapidOCR and ONNX Runtime CPU, with no external inference endpoint
- Scale: zero to one replica for the demo
- Compute: 4 vCPU and 8 GiB on the Consumption workload profile
- OCR concurrency: one governed worker job
- OCR reuse: bounded exact-pixel result cache plus strict equivalent-panel canonicalization for redundant cross-format uploads
- Local history: maximum 500 product lineages, 10 independently reopenable revisions per lineage, whole-lineage FIFO eviction and deletion, and opaque originating-browser access scope
- Incident action: stop new intake, preserve commit and deployment evidence, classify the fault, then restore the last verified digest when required

## Submission addresses

- Source: `https://github.com/rschafer777/ai-alcohol-label-verification`
- Application: `https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/`

## Initial candidate deployment record

Application commit `4a31e1a95cf6b2ec8dac5c8bc8f5763ffa7f3961` was deployed by GitHub Actions run `33815343738`, attempt 2. The immutable image digest is `sha256:c439dea1a608b4e1ba08d364eabee979d20a388c3a44fae2187c9da8dc208d9c`. Azure readback confirmed 4 vCPU, 8 GiB, and zero-to-one replicas. Public liveness, readiness, metadata, HSTS, and three sample analyses passed. Engineering browser pre-UAT also passed. `DEPLOYMENT_EVIDENCE.json` is the authoritative machine-readable record.

The current Azure demo at `https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/` is available only as the initial-candidate UAT baseline. It is not the CR-002 candidate and is not ready for CR-002 acceptance. The CR-002 commit, digest, workflow run, deployment verification, and requester-UAT entry remain Pending until every corrective gate passes. Federal operational use requires the agency controls, integrations, operating boundary, independent testing, and authorization activities identified in `../11-federal-authorization-readiness/`.
