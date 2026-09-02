# System Security Plan Starter

Document ID: LV-FED-SSP-001

## System description

LabelVerify is a same-origin web application that accepts alcohol label images, performs local OCR and deterministic rule evaluation, stores up to 500 evidence records, and supports a human review disposition. The current Azure demo is one Azure Container App using a private registry image and public HTTPS ingress.

## Proposed boundary

In-boundary components are browser application code, FastAPI service, supervised OCR worker, local ONNX assets, container filesystem history, Azure Container Apps configuration, image registry, deployment workflow, and associated identity. Direct COLAs Online, applicant systems, agency identity, centralized logging, durable records, backup, and agency network controls are external until selected.

## Data types and flow

Inputs are label images, generated OCR text, evidence coordinates, processing metadata, optional reviewer notes, and reviewer disposition. The browser sends HTTPS multipart data to the API. Processing remains within the application container. Successful results and copied source images enter the history store. No runtime cloud ML API is called. No label content is intentionally logged.

## Security properties

- HTTPS-only public ingress in Azure
- Same-origin UI and API
- Host, Origin, multipart, type, byte, pixel, rate, capacity, and timeout enforcement
- Supervised child process and lifecycle cleanup
- Non-root container
- Locked dependencies, model hashes, pinned GitHub actions, OIDC deployment, private registry, immutable digest
- Content-safe errors and no content logging
- Deterministic rules and immutable machine findings

## Inventory baseline

See `Dockerfile`, `uv.lock`, `frontend/package-lock.json`, `ops/model-manifest.json`, `docs/10-release/sbom-python.cdx.json`, and `docs/10-release/sbom-frontend.cdx.json`. The final environment inventory adds Azure resource IDs, regions, endpoints, identities, diagnostic settings, keys, certificates, dependencies, owners, and support dates.

## Required authorization decisions

- Sponsoring organization, authorizing official, system owner, ISSO, privacy official, records official, and assessor
- Impact categorization and applicable control baseline
- Production Azure subscription, tenant, region, network topology, egress policy, WAF or gateway, and private endpoints
- Identity, role model, privileged access, session policy, and reviewer attribution
- Durable database and object storage, encryption keys, backup, restoration, recovery targets, and legal hold
- Audit events, retention, centralized SIEM, alert routing, and time synchronization
- Records schedule, PII determination, privacy notice, data minimization, and deletion policy
- Vulnerability response SLAs, penetration testing, supply-chain review, incident response, and contingency exercises

## Control implementation worksheet

For each selected control record control ID, owner, implementation statement, inherited provider, parameter values, evidence path, test method, frequency, status, POA&M link, and approval. Technical source inspection alone is not sufficient for operational, personnel, physical, or inherited controls.
