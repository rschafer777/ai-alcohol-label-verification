# I2R Azure Demo Deployment Addendum

Document control ID: LV-I2R-011  
Revision: 1.0  
Date: 2026-09-01  
Status: Active architecture authority

## 1. Purpose and precedence

This addendum records the selected Azure demo architecture after the requester supplied a verified Azure resource handoff and an environment-scoped GitHub OIDC federation. It supersedes earlier Fly deployment statements in LV-I2R-001, LV-I2R-002, and ADR-009. It does not change the verification request, result, rule, or selected-check contracts.

## 2. Selected deployment boundary

The demo uses:

- one Azure Container Apps Consumption environment in Central US;
- one externally accessible Container App in single-revision mode;
- one non-root LabelVerify container with 2 vCPU and 4 GiB memory;
- zero to one replicas with an HTTP concurrency threshold of one;
- one private Azure Container Registry;
- one user-assigned identity with AcrPull for platform image retrieval;
- one GitHub deployment identity federated only to the repository `demo` environment;
- one same-origin HTTPS URL for the UI and API;
- no application database, durable queue, object store, account, server session, mounted volume, or runtime secret.

Scale to zero is a demo cost control. It can add platform cold-start delay and therefore does not count as evidence that the cold-start target passes.

## 3. Build and deployment flow

```text
GitHub main revision
  -> complete release gate
  -> short-lived Azure OIDC token
  -> build one OCI image with the Git revision as build ID
  -> push revision tag and immutable digest to private ACR
  -> deploy only the digest through the governed ARM template
  -> read back effective Azure configuration
  -> exercise readiness, metadata, sample, full verification, HTTPS redirect, and HSTS
```

The workflow has repository read permission globally. Only the deployment job receives `id-token: write`. Third-party actions are pinned to full commit hashes. No client secret, registry password, publishing profile, or registry administrator credential is used.

## 4. Runtime identity boundaries

### 4.1 Deployment identity

The dispatch-only workflow can run only from `main`. GitHub exchanges the environment-scoped OIDC assertion for a short-lived Azure token. This identity can deploy within the governed resource group and push to the registry. It is never attached to the Container App.

### 4.2 Registry pull identity

The Container App resource receives only the user-assigned ACR pull identity. `configuration.identitySettings` sets its lifecycle to `None`. Azure can use it to pull the private image, but the main application and any init container cannot request a token for it.

### 4.3 Request identity

Uvicorn proxy-header trust remains disabled. In Azure Container Apps mode, the mutation route requires exactly one `X-Forwarded-For` header and uses only the rightmost comma-separated IP address. Microsoft documents that Container Apps appends the source address it observes as that rightmost value. Every earlier value is treated as untrusted input and ignored. Missing, duplicate, empty, malformed, non-ASCII, or zone-qualified identity values fail before the request body is consumed.

The selected address is normalized and HMAC-SHA256 digested with a random per-process key. The raw address is not logged or retained. Direct local mode uses the ASGI peer and ignores forwarding headers. The implemented Fly source remains a portability path and is not the active deployment mode.

## 5. Host, Origin, and probe contract

The allowed Host is the exact Container App FQDN supplied through the governed GitHub environment. The ARM readback gate compares that value with Azure's effective ingress FQDN. A mismatch fails deployment validation.

Production requests require the exact allowed Host. The verification POST also requires the exact HTTPS Origin. CORS credentials are not enabled.

Azure internal probes use HTTP on port 8080 with the exact governed Host header:

- startup: `GET /health/live`;
- liveness: `GET /health/live`;
- readiness: `GET /health/ready`.

The readiness probe therefore tests OCR worker and governed-asset readiness, not only whether the TCP port accepts a connection.

## 6. Effective configuration gate

The workflow fails unless Azure readback proves:

- the expected FQDN and external TLS-only ingress;
- single-revision mode;
- the exact immutable image digest;
- exactly one 2 vCPU/4 GiB container;
- zero to one replicas and concurrency one;
- exactly one ACR registry binding using the pull identity;
- pull-identity lifecycle `None`;
- production runtime mode, exact allowed Host, and Azure identity source;
- all three application-aware probes and their Host header;
- zero application secrets and zero volumes.

The public smoke gate then requires application readiness, build metadata equal to the deployed Git revision, the governed sample, three consecutive complete 19-check verifications, a mean server duration below 5 seconds, no duration at or above 9 seconds, retained duration statistics, HTTP to HTTPS redirect, and HSTS.

## 7. Data movement and storage

Images and reference values enter through the same-origin verification POST, remain in request-scoped files and memory, and are removed on every terminal path. OCR and comparison run inside the container. Results return to browser memory only. The deployment adds no database, storage account, durable queue, runtime model download, or external inference service.

The platform can still emit infrastructure logs and the Consumption environment does not prove deny-by-default egress. These remain documented federal-transition decisions and are not represented as implemented controls.

## 8. Failure, rollback, and operations

- A quality failure prevents build and deployment.
- A build or registry failure leaves the prior revision active.
- An ARM or readback mismatch fails the run and blocks the release claim.
- A public smoke failure fails the run and preserves the evidence in GitHub Actions.
- Before any image push, the workflow accepts a rollback target only when the prior app uses the governed ACR repository plus an immutable SHA256 digest, its FQDN and identity boundary match the governed contract, and the image matches the latest successful governed Azure deployment record. A non-404 read error or drift fails closed.
- A separate 15-minute rollback job exports that successful Azure deployment template and parameters, restores the prior governed digest with its saved configuration, and verifies the effective image plus public readiness. If no prior app existed, it removes only the newly created failed Container App. The shared environment, registry, and identities remain intact.
- The resource group and Container App carry lifecycle tags, including the demo expiration date.

## 9. Verification obligations

Before the public demo is called complete, evidence must show:

1. the exact GitHub environment secret and variable names exist without exposing secret values;
2. the complete quality job passes on the deployed revision;
3. the effective Azure configuration matches Section 6;
4. the public smoke gate passes through the actual FQDN;
5. deployed page-load, warm, cold, shaped-network, and public-edge tests are classified honestly;
6. the release manifest and README match the deployed revision and URL;
7. three independent RT reviewers accept the same immutable snapshot.

## 10. Authoritative platform references

- [Azure Container Apps ARM template reference](https://learn.microsoft.com/en-us/azure/templates/microsoft.app/containerapps)
- [Managed identities in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity)
- [Azure Container Apps image pull with managed identity](https://learn.microsoft.com/en-us/azure/container-apps/managed-identity-image-pull)
- [Azure Container Apps ingress](https://learn.microsoft.com/en-us/azure/container-apps/ingress-overview)
- [Health probes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/health-probes)
- [Azure Login with OpenID Connect](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure-openid-connect)
