# Azure Demo Deployment

**Document ID:** LV-REL-004  
**Status:** Deployment contract implemented, OCR lane correction pending live proof  
**Environment:** GitHub environment `demo`

## 1. Purpose

The deployment workflow builds the same repository revision that passed the release gate, pushes an immutable image to Azure Container Registry, deploys that image digest to Azure Container Apps, validates the effective resource configuration, and exercises the public application through HTTPS.

The workflow does not use a client secret, registry password, publishing profile, or registry administrator account. GitHub obtains a short-lived Azure token through the environment-scoped OIDC federation configured for this repository.

## 2. GitHub environment contract

The `demo` environment must contain these encrypted secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

The repository Actions configuration must also contain `LABELVERIFY_PROHIBITED_PERSONAL_TERMS` as a JSON-array secret. It supplies the non-public term list for the exact public-archive privacy scan without embedding omitted identities in source or logs.

It must contain these environment variables:

- `AZURE_RESOURCE_GROUP`
- `AZURE_LOCATION`
- `AZURE_ACR_NAME`
- `AZURE_ACR_LOGIN_SERVER`
- `AZURE_CONTAINERAPPS_ENVIRONMENT`
- `AZURE_CONTAINER_APP_NAME`
- `AZURE_CONTAINER_APP_FQDN`
- `AZURE_ACR_PULL_IDENTITY_ID`
- `AZURE_IMAGE_NAME`
- `AZURE_EXPIRES_ON`

The workflow fails before Azure authentication if a required non-secret value is absent. The three Azure identity values are supplied only to the OIDC login action and are not committed to source.

## 3. Deployment controls

- The workflow is dispatch-only and the quality job runs only from `main`. A repository push cannot deploy by itself.
- Only the deployment job receives `id-token: write`.
- All third-party actions are pinned to full commit hashes.
- The source revision must pass Python lint, strict typing, tests, frontend lint, strict typing, tests, production build, browser journeys, accessibility checks, and the prohibited Unicode dash scan before deployment.
- The image embeds the Git commit as `LABELVERIFY_BUILD_ID`.
- Azure deploys the immutable digest, not a mutable tag.
- The image includes build provenance and an SBOM attestation in the registry.
- Deployment uses incremental ARM mode and governs only the Container App resource.
- The application resource receives only the ACR pull identity. Its identity lifecycle is `None`, which permits platform image pull without exposing an access token to application code. The GitHub deployment identity is not attached to the runtime.
- The runtime has no secrets, volumes, database, durable queue, or required external inference endpoint.
- Platform startup and liveness probes call `/health/live`; readiness calls `/health/ready`. Every internal HTTP probe sends the exact governed Host header, so strict Host validation stays enabled.
- Before any image push, the workflow captures the prior app only when its image is the governed ACR repository plus an immutable SHA256 digest, its FQDN and identity boundary match the governed contract, and the image matches the most recent successful governed Azure deployment record. A non-404 Azure read failure or any drift fails before mutation.
- The workflow has no mutable demo tag. If effective-configuration or public-smoke validation fails after deployment, a separate 15-minute rollback job exports the last governed Azure deployment template and parameters, restores the prior digest with that saved configuration, and verifies the effective image plus public readiness. If the first deployment fails, the rollback job removes the newly created failed Container App while preserving the shared environment, registry, and identities.

## 4. Effective runtime contract

- external ingress on port 8080;
- automatic HTTP transport with insecure ingress disabled;
- single revision mode;
- one container, two vCPU, and 4 GiB memory;
- minimum zero and maximum one replica;
- HTTP concurrency scale threshold of one;
- local RapidOCR inference inside the container;
- strict production Host and Origin validation;
- Azure client identity from only the rightmost value in exactly one `X-Forwarded-For` header, with every earlier value ignored as untrusted input;
- no application-level storage or session affinity;
- six lifecycle and ownership tags on the Container App.

## 5. Post-deployment gate

The workflow reads the effective Azure resource and fails unless the actual FQDN, identity lifecycle, registry authentication, image digest, runtime settings, application-aware probes, ingress, resources, scaling, volumes, and secrets match the governed template. It then validates:

1. the public readiness endpoint;
2. build metadata bound to the deployed commit;
3. the built-in sample package;
4. three consecutive complete 19-check governed-sample verifications with the exact expected Review outcome, no Mismatch, only the two documented warning limitations, a mean server duration below 5 seconds, and no run at or above 9 seconds;
5. HTTP redirection to HTTPS;
6. the HSTS response header.

The workflow summary records the deployed revision, image digest, public URL, and smoke-test result. GitHub retains the authoritative run log and environment deployment record.

## 6. Known boundary

The Consumption environment has no VNet and does not itself prove a deny-by-default outbound network policy. Runtime OCR and comparison remain self-contained and do not require an outbound API. A federal production transition must separately select and test platform egress controls, centralized audit logging, retention, identity, monitoring, and the final authorization boundary.

## 7. Deployment attempt record

GitHub Actions run `33561343127` stopped before any job started because the repository permits only actions owned by `rschafer777` or matching `actions/*`, `azure/*`, and `docker/*`. The rejected dependency was `astral-sh/setup-uv`. No Azure login, image build, registry push, resource update, or public deployment occurred in that run.

The remediation preserves the repository policy. The workflow now installs the pinned `uv==0.11.32` package through the Python runtime established by the allowed, commit-pinned `actions/setup-python` action. A deployment-contract regression test prohibits reintroducing `astral-sh/setup-uv` and requires the pinned package installation command. Live evidence remains pending until the corrected workflow succeeds.

Run `33565168381` then passed workflow startup and locked dependency installation but stopped in the quality job before Azure authentication. The Linux runner exposed two portability gaps. Controlled model acquisition left valid ONNX files writable on POSIX, which correctly failed the existing read-only readiness contract. The fixture generator also produced platform-specific raster bytes because Pillow wheels can use different native font rasterization, even when the governed semantic recipe is unchanged.

Model acquisition now removes POSIX write bits after both cache hits and downloads, with a behavioral regression assertion. Fixture generation now proves byte-for-byte repeatability across two runs on the same toolchain, validates each generated corpus against its internal hashes and seals, compares references and independent oracles exactly, and applies content-sensitive visual equivalence checks where native font rasterization can differ by platform. An adversarial blank-image control must fail the visual comparison. Canonical fixture bytes, manifest hashes, holdout seals, independent oracles, and the production corpus remain unchanged and separately enforced. No Azure login, image build, registry push, or resource update occurred in run `33565168381`.

Run `33568696374` passed dependency installation, all 191 Python tests, all 46 frontend tests, the production build, and all three required browser journeys. The final tracked-source Unicode scan then failed because the Ubuntu runner does not include `rg`. The scan now uses Git's checkout-provided grep implementation against tracked source, with the same prohibited character range and governed exclusions. A deployment-contract regression assertion prevents reintroducing the unavailable command. Privacy, product-corpus, OIDC, image build, registry push, and Azure mutation steps did not run in `33568696374`.

The first portability correction retained exclusions for `research/` and checksum files. Adversarial RT rejected that control because those tracked files are part of the public deliverable. The final scan has no path exclusions. Its behavioral regression creates prohibited characters inside both formerly excluded path classes and requires Git to detect both before the candidate can pass.

Run `33570716009` passed the complete release gate, privacy scan, and 30-case product corpus. Azure OIDC authentication then rejected the original classic repository subject because GitHub presented its immutable organization-and-repository identity form. No image build, registry push, or Azure resource mutation occurred. The existing environment-scoped federated credential was corrected in place and read back through Azure before another dispatch.

Run `33572176211` proved the corrected OIDC exchange, governed prior-state check, and private-registry authentication. The multi-stage image build then exposed that the frontend stage copied `frontend/` but not the root `contracts/` registry imported during TypeScript compilation. The build stopped before image push completion and before the workflow's Container App mutation boundary. The Dockerfile now copies the root contracts into the frontend build context before compilation, and a deployment-contract regression test enforces that order. The corrected local gate passed 192 Python tests, 46 frontend tests, the production build, and the required browser journeys.

Run `33573352505` passed the release gate, privacy scan, product corpus, OIDC exchange, registry authentication, immutable image build and push, and Azure ARM deployment. The new revision never became ready because RapidOCR warmup attempted to download its default `FZYTK.TTF` visualization font into the read-only Python package directory. The container correctly denied that write, but the worker exited before readiness. A live read-only container console diagnostic established the exact exception. The governed rollback job then succeeded and removed the failed first application. The application now fetches DejaVu Sans 2.37 from its official release archive only during controlled setup or build, verifies both archive and extracted-file SHA-256 values, marks the font read-only, and passes its local absolute path to RapidOCR. The workflow now runs the built digest locally and requires readiness plus metadata before marking the Container App mutation boundary.

Run `33577226574` passed every protected source gate, the exact-archive privacy scan, all 30 governed product cases, OIDC authentication, immutable OCI build and push, local digest readiness, Azure effective-configuration readback, HTTPS controls, and one complete public sample verification. It deployed commit `4024aded5beae416d471f13cbdb5563572a06328` with image digest `sha256:5521af5a3714cfb78f5329f91213ae1ef1a79c392a502b16c94697e345803715`. Independent browser UAT then reproduced a real 504 worker timeout on the two-panel built-in sample, including a retry. A direct public API attempt reached the same 6.25-second boundary. The original 1 vCPU profile forced two OCR lanes, each configured for two ONNX Runtime threads, to compete for one vCPU. The correction assigns 2 vCPU and 4 GiB to the single scale-to-zero replica, keeps concurrency at one, and strengthens the deployment gate from one sample attempt to three consecutive attempts with a mean below 5 seconds and no attempt at or above 9 seconds. This correction requires a new immutable workflow result before the deployed performance assertion can pass.

Run `33578923408` passed all source, privacy, product, OIDC, image, local readiness, Azure deployment, and effective-configuration gates for commit `fd9a030e06bb699a51507bc4ecdb2d0c6e926caa`. The strengthened three-run public gate rejected the revision, and rollback restored the prior governed digest successfully. The effective 2 vCPU resource matched the template, but the adapter still assigned two intra-operation threads to each of two simultaneous OCR lanes and warmed only the first lane. The current correction assigns one ONNX Runtime intra-operation thread to each lane and warms both engines before readiness. The timing summary is now emitted before the performance assertion so every successful HTTP result remains visible even when its statistical gate fails.
