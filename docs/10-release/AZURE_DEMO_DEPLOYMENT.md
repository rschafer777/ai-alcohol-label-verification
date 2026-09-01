# Azure Demo Deployment

**Document ID:** LV-REL-004  
**Status:** Deployment contract implemented, live evidence pending  
**Environment:** GitHub environment `demo`

## 1. Purpose

The deployment workflow builds the same repository revision that passed the release gate, pushes an immutable image to Azure Container Registry, deploys that image digest to Azure Container Apps, validates the effective resource configuration, and exercises the public application through HTTPS.

The workflow does not use a client secret, registry password, publishing profile, or registry administrator account. GitHub obtains a short-lived Azure token through the environment-scoped OIDC federation configured for this repository.

## 2. GitHub environment contract

The `demo` environment must contain these encrypted secrets:

- `AZURE_CLIENT_ID`
- `AZURE_TENANT_ID`
- `AZURE_SUBSCRIPTION_ID`

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
- Before deployment, the workflow captures the prior active image. If effective-configuration or public-smoke validation fails after deployment and a prior image exists, the workflow restores that prior digest through the same governed template.

## 4. Effective runtime contract

- external ingress on port 8080;
- automatic HTTP transport with insecure ingress disabled;
- single revision mode;
- one container, one vCPU, and 2 GiB memory;
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
4. a complete 19-check governed-sample verification with the exact expected Review outcome, no Mismatch, and only the two documented warning limitations;
5. HTTP redirection to HTTPS;
6. the HSTS response header.

The workflow summary records the deployed revision, image digest, public URL, and smoke-test result. GitHub retains the authoritative run log and environment deployment record.

## 6. Known boundary

The Consumption environment has no VNet and does not itself prove a deny-by-default outbound network policy. Runtime OCR and comparison remain self-contained and do not require an outbound API. A federal production transition must separately select and test platform egress controls, centralized audit logging, retention, identity, monitoring, and the final authorization boundary.
