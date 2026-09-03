# Release and Operational Handoff

Document ID: LV-REL-001  
Status: Deployed demo verified; requester UAT and external production authorization pending

## Deliverable contents

- Complete Python and TypeScript source
- Locked dependency files
- Versioned API, check, error, and regulatory contracts
- Local OCR model acquisition manifest with hashes
- Synthetic sample and test fixtures
- Unit, integration, browser, accessibility, performance, security, and deployment tests
- Private 70-image production-API and server-grouping evidence without redistributing the raw images
- Numbered documentation from discovery through UAT
- OCI Dockerfile, Azure template, and GitHub OIDC workflow
- README with setup, run, test, approach, tools, assumptions, trade-offs, and limitations

## Release controls

The release owner shall:

1. Run the complete validation protocol.
2. Obtain three independent RT Clear decisions on one frozen manifest.
3. Confirm the repository root, branch main, and intended remote.
4. Review `.gitignore` and staged files.
5. Exclude local virtual environments, models, node modules, caches, coverage, temporary files, local environment values, local agent instructions, raw handoff drafts, and user images without public redistribution approval.
6. Scan staged text for credentials, keys, tokens, passwords, personal information, machine-specific paths, and protected Azure identifiers.
7. Confirm no staged file exceeds GitHub limits.
8. Confirm no LICENSE file exists unless the owner makes an explicit license choice.
9. Commit without rewriting history and push main without force.
10. Dispatch the protected demo workflow for that exact commit.
11. Verify the remote commit, public files, Azure metadata, health, UI, core analysis, and history.
12. Record commit SHA, workflow, immutable image digest, public URL, tests, exclusions, and UAT entry status.

## Deployment design

GitHub Actions uses OIDC to authenticate to Azure. It validates the source, builds the OCI image, runs it locally for readiness, pushes an immutable digest to the private registry, deploys Azure Container Apps through the governed ARM template, reads back effective security configuration, performs public HTTPS smoke and timing checks, and restores the prior governed digest if a post-mutation step fails.

## Operations

- Liveness: `/health/live`
- Readiness: `/health/ready`
- Build and contract metadata: `/api/v1/meta`
- Runtime inference: local RapidOCR and ONNX Runtime CPU, with no external inference endpoint
- Scale: zero to one replica for the demo
- Compute: 4 vCPU and 8 GiB on the Consumption workload profile
- OCR concurrency: one governed job
- OCR reuse: bounded exact-pixel result cache plus strict equivalent-panel canonicalization for redundant cross-format uploads
- Local history: maximum 500 records with FIFO eviction and opaque originating-browser access scope
- Incident action: stop new intake, preserve commit and deployment evidence, classify the fault, then restore the prior verified digest if required

## Submission addresses

- Source: `https://github.com/rschafer777/ai-alcohol-label-verification`
- Application: `https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/`

## Verified deployment record

| Item | Verified value |
| --- | --- |
| Application commit | `6863ea8eaa4074ba209cc273f79db19f84917641` |
| Branch | `main` |
| Workflow | `https://github.com/rschafer777/ai-alcohol-label-verification/actions/runs/33746505754` |
| Workflow result | PASS, validation and deployment succeeded; rollback was not invoked |
| OCI image digest | `sha256:9ab566a7a604dd558c8aefbe19af75edddc4b57165054a200b6a3698b6d8fd41` |
| GitHub deployment | `6242353833`, environment `demo`, status `success` |
| Public URL | `https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/` |
| Effective compute | 4 vCPU and 8 GiB |
| Health and metadata | HTTPS 200, live, ready, exact build ID, profile `all_beverages_demo_v2`, 24 checks, history cap 500 |
| Public difficult-image execution | PASS, 9 of 9 fresh analyses, 24 checks each, 7.148-second mean and 8.752-second maximum |

The deployed demo is ready for requester UAT. Federal production use remains outside the authority of this take-home release and requires the agency controls, integrations, operating boundary, independent testing, and authorization activities identified in `../11-federal-authorization-readiness/`.
