# Release and Operational Handoff

Document ID: LV-REL-001  
Status: Local release gates passed; the multi-image warning read, browser photo preparation, and vocabulary changes landed after the frozen manifest of the independent review, so the manifest was regenerated and the three independent reviews must be repeated on it; final commit-bound Azure verification and requester UAT pending

## Deliverable contents

- Complete Python and TypeScript source
- Locked Python and frontend dependency files
- Versioned API, check, error, and regulatory contracts
- Local OCR model acquisition manifest with cryptographic hashes
- Synthetic sample and governed test fixtures
- Unit, integration, browser, accessibility, performance, security, and deployment tests
- Private 76-image production-API and server-grouping evidence
- Field-level pixel ground truth for 70 private images and a 42-image disposition oracle
- Numbered documentation from discovery through UAT
- OCI Dockerfile, Azure infrastructure template, and GitHub OIDC workflow
- README with setup, run, test, approach, tools, assumptions, trade-offs, and limitations

The private raw images are excluded from the public repository because public redistribution rights were not established. Their hashes, test results, timing, and field-level scores are retained as public evidence.

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
- Local history: maximum 500 records with FIFO eviction and opaque originating-browser access scope
- Incident action: stop new intake, preserve commit and deployment evidence, classify the fault, then restore the last verified digest when required

## Submission addresses

- Source: `https://github.com/rschafer777/ai-alcohol-label-verification`
- Application: `https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/`

## Final deployment record

The authoritative values are written after the protected workflow and live checks complete. Until then, `DEPLOYMENT_EVIDENCE.json` is marked `PENDING` and no deployment is represented as the final candidate.

The Azure demo becomes ready for requester UAT when the exact application commit passes the protected workflow, the public service reports the matching build ID and contract profile, the engineering browser pre-UAT passes, and the release evidence is reconciled. Federal operational use requires the agency controls, integrations, operating boundary, independent testing, and authorization activities identified in `../11-federal-authorization-readiness/`.
