# Secure Configuration Guide Preparation Draft

Artifact status: DRAFT  
Official sources retrieved: 2026-09-01  
Certification class: PENDING  
Production platform and Azure services: PENDING

## 1. Intended audience

This guide is for provider operators and agency security teams preparing a production LabelVerify configuration. It separates current application defaults from decisions that cannot be made until the production cloud, identity, logging, data, and agency integration are selected.

## 2. Current application configuration

| Setting or control | Current secure direction | Source | Production status |
|---|---|---|---|
| `LABELVERIFY_RUNTIME_MODE` | Use `direct` for loopback evaluation. Use `production` only behind the selected trusted production ingress | `.env.example`, `ops/fly.toml.example`, backend security tests | EFFECTIVE PRODUCTION VALUE PENDING |
| `LABELVERIFY_ALLOWED_HOST` | Set exactly one approved external Host. Do not use a wildcard | `.env.example`, `README.md`, Host tests | PENDING PUBLIC HOST |
| `LABELVERIFY_MODEL_ROOT` | Point to the read-only governed OCR model directory | `.env.example`, `ops/model-manifest.json` | DOCUMENTED SOURCE; DEPLOYMENT PENDING |
| `LABELVERIFY_SPOOL_ROOT` | Use a dedicated private writable request-spool directory with capacity limits and cleanup ownership | `.env.example`, I2R security specification | DOCUMENTED SOURCE; STORAGE PENDING |
| `LABELVERIFY_SAMPLE_MANIFEST` | Use the governed sample manifest shipped with the selected build | `.env.example`, readiness tests | DOCUMENTED |
| `LABELVERIFY_STATIC_ROOT` | Use the frontend build produced by the selected source snapshot | `.env.example`, Dockerfile | DOCUMENTED SOURCE; BUILD PROVENANCE PENDING |
| `LABELVERIFY_BUILD_ID` | Use a unique release and deployment identifier, never `development` in production | `.env.example`, Dockerfile, release evidence | PENDING RELEASE PIPELINE |
| Runtime identity | Run the container as the non-root runtime user supplied by the Dockerfile | Dockerfile | OCI AND DEPLOYMENT PROOF PENDING |

## 3. Required application protections

- Serve the browser and API from the same approved origin.
- Keep batch coordination client-side and sequential unless a separately reviewed durable queue architecture replaces it.
- Preserve the 300-row maximum, manifest path and ownership validation, one active request, per-row deadline, and formula-safe CSV export behavior.
- Treat browser refresh or tab closure as queue and result destruction; do not describe session-only batch state as a records repository.
- Require the exact allowed Host on every request.
- Require an exact HTTPS Origin on the verification mutation route in production.
- Do not enable a broad CORS policy.
- Preserve the existing raw-body, multipart, field, signature, file-count, byte, pixel, rate, capacity, and timeout limits.
- Preserve one active OCR job and bounded admission until new capacity evidence supports a change.
- Keep full decode through aggregation inside the supervised child process.
- Keep proxy-header trust disabled unless a new trusted identity design and test matrix is approved.
- Preserve no-store API responses and content-free application logging.
- Preserve cleanup after success, error, timeout, cancellation, disconnect, replacement, and shutdown.
- Keep OCR models and regulatory registries hash governed and readiness checked.
- Use only the nineteen selected checks unless a governed rule change is approved.

## 4. Production decisions required

| Configuration area | Required decision and evidence | Status |
|---|---|---|
| Cloud and region | Exact provider, cloud, subscription, tenant, region, service type, and applicable FedRAMP package | PENDING |
| Azure services | Exact Azure or Azure Government services and features, if selected; verify each is in the applicable Microsoft audit scope | PENDING |
| Ingress and TLS | Terminating service, certificate ownership, TLS policy, client identity chain, health routing, and validation | PENDING |
| Network egress | Source-of-truth allow and deny policy plus independent enforcement evidence | PENDING |
| Administrative identity | Workforce identity provider, phishing-resistant MFA, RBAC, JIT, break-glass, service principals, and access reviews | PENDING |
| Secrets and keys | Secret store, managed identities, key ownership, rotation, recovery, and access logging | PENDING |
| Cryptographic modules | Module inventory, usage, configuration, CMVP status, and exceptions | PENDING |
| Logging and SIEM | Sources, fields, content restrictions, routing, retention, access roles, alerts, time synchronization, and agency export | PENDING |
| Data and retention | Permitted information, temporary storage location, metadata, deletion, records, legal holds, backup, and support handling | PENDING |
| Monitoring and alerting | Availability, capacity, security, vulnerability, configuration, and lifecycle signals plus response ownership | PENDING |
| Incident response | Contacts, severity, notification, evidence preservation, reporting, exercises, and agency coordination | PENDING |
| Recovery | RTO, RPO, backups, restoration, regional recovery, dependency recovery, and exercises | PENDING |
| Support | Approved support path, identity verification, access limits, data handling, and audit trail | PENDING |

## 5. Agency configuration handoff

The agency configuration record should identify:

- approved users and information;
- agency identity provider and access policy;
- required log export and SIEM integration;
- approved sharing, retention, encryption, and support settings;
- administrative roles and separation of duties;
- prohibited features and integrations;
- incident, records, privacy, accessibility, and recovery responsibilities;
- evidence that settings match this guide and remain in place.

## 6. Verification checklist

- [ ] Effective configuration exported from source of truth
- [ ] Exact Host, Origin, client identity, headers, no-store, and error behavior tested
- [ ] TLS path and cryptographic modules inventoried and validated
- [ ] Egress policy configured and negative probes retained
- [ ] Administrative MFA, least privilege, JIT, and access reviews tested
- [ ] Log routing, content canaries, retention, and SIEM integration tested
- [ ] Temporary storage and deletion tested on every terminal path
- [ ] Readiness, rollback, backup, restore, and regional recovery tested
- [ ] Configuration compared to approved defaults by automation
- [ ] Machine-readable export and change history retained

## 7. Official basis

- [FedRAMP Secure Configuration Guide](https://www.fedramp.gov/2026/reference/20x/b/secure-configuration-guide/)
- [Initial Agency Authorization](https://www.fedramp.gov/2026/agencies/use/initial/)
- [Microsoft shared responsibility](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility)
- [Microsoft Azure FedRAMP offering](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-fedramp)
