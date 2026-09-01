# Security Decision Record Preparation Draft

Artifact status: DRAFT  
Official sources retrieved: 2026-09-01  
Official JSON Schema: [FedRAMP Security Decision Record Schema, 2026-06-24](https://www.fedramp.gov/schemas/fedramp-security-decision-record-schema-2026-06-24.json)  
Machine-readable companion: `03_SECURITY_DECISION_RECORD.template.json`

## 1. Record metadata

| Field | Value |
|---|---|
| Service | LabelVerify |
| Version | 0.1 preparation draft |
| Last update | 2026-09-01 |
| Update source | Current local repository evidence plus official FedRAMP 2026 rules |
| Package Overview URI | PENDING trust center or package repository |
| Certification class | PENDING |
| Effective environment | PENDING |
| Accountable official | PENDING |

## 2. Current architecture decision summary

LabelVerify uses a same-origin modular monolith. The browser supports a bounded single request or validates a batch manifest and holds an ordered queue of 1 to 300 applications, image file objects, progress, and row results in session memory. It submits one bounded multipart request at a time to a FastAPI boundary. The API enforces request, Host, Origin, rate, capacity, error, response-header, and cleanup rules. An admitted request is processed inside one supervised child process that performs full decode through deterministic aggregation. OCR models and rule registries are local and hash governed. A typed result returns to the current browser session. CSV and detailed JSON batch exports are created locally in the browser.

The current application does not implement user accounts, a database, a durable queue, durable reviewer notes, or required runtime cloud inference. Production platform, organization, identity, logging, retention, cryptographic, incident, support, and deployment decisions remain PENDING.

## 3. Initial FedRAMP rule decisions

| Rule or ruleset | Current implementation statement | Provider verification | Current validation | Independent assessment | Status |
|---|---|---|---|---|---|
| `MAS-CSO-IIR` | Source architecture identifies browser single and batch coordination, API, supervised child, request spool, models, rules, exports, and candidate deployment resources | Compare source, configuration, runtime inventory, and data-flow inventory | Source, batch tests, capacity evidence, and local lifecycle tests cover the current code path | PENDING assessor | PARTIAL |
| `MAS-CSO-FLO` | Current single-request and cleanup flows are documented in `02_I2R_DATA_INTERFACE_SECURITY.md`; browser batch state, sequential requests, and export flows are documented in `10_I2R_BATCH_AND_READINESS_ARCHITECTURE.md` | Trace each data object through browser queue, API, spool, child, response, in-memory results, export, and cleanup | Local lifecycle, batch, and browser privacy evidence | PENDING assessor and deployment | PARTIAL |
| `MAS-CSO-TPR` | Dependencies and OCR models are inventoried; cloud, CI, identity, logging, support, and security services are not selected | Reconcile contracts, service inventory, SBOMs, and effective connections | PENDING effective environment | PENDING assessor | PARTIAL |
| `CPO-CSO-OVR` | Human and machine preparation drafts exist in this package | Validate current fields against official CPO schema | PENDING completion of required identities and services | PENDING assessor | PARTIAL |
| `SDR-CSO-FRR` | This record captures initial source-backed decisions and gaps | Validate current rules inventory and linked evidence | PENDING complete current-rule coverage | PENDING assessor | PARTIAL |
| `SCG-CSO-RSC` | Current source defaults and production decisions are listed in `04_SECURE_CONFIGURATION_GUIDE.md` | Compare deployment source of truth to the guide | PENDING deployed configuration tests | PENDING assessor | PARTIAL |
| `CMU-CSO-CMD` | Application-level cryptographic modules are not inventoried because TLS, key, disk, secret, log, and backup services are not selected | Generate module inventory from effective services and configurations | PENDING CMVP and configuration evidence | PENDING assessor | PENDING |
| `IVV-CSO-SEI` and `IVV-CSO-SEE` | Source evidence is available for selected application measures | Supply implementation source and effectiveness evidence to the selected assessor | Current internal validation exists only for the local application scope | PENDING FedRAMP Recognized assessor | PENDING |
| Vulnerability Detection and Response | Lockfiles, SBOMs, model hashes, dependency audits, security scans, and correction evidence exist | Repeat scans and reconcile results to inventory | Point-in-time local release evidence passes | PENDING assessor and persistent operations | PARTIAL |
| Collaborative Continuous Monitoring | A proposed cadence and evidence set is defined in `08_CONTINUOUS_MONITORING_PLAN.md` | Generate scheduled reports from effective sources | PENDING operating history | PENDING assessor and agency review | PENDING |

## 4. Initial Key Security Indicator decisions

| KSI area | Current measures | Verification and validation seed | Gap | Status |
|---|---|---|---|---|
| Cloud Native Architecture | Components, privileges, dependencies, timeouts, ownership, and limits are explicitly defined; container source uses a non-root identity | Architecture, security tests, lifecycle matrix, release manifest | No effective infrastructure inventory or persistent intended-state enforcement | PARTIAL |
| Service Configuration | Exact Host and Origin rules, response headers, no-store behavior, input limits, and same-origin design | Backend security tests and browser privacy matrix | TLS, platform networking, secret, encryption, and tenant configuration PENDING | PARTIAL |
| Identity and Access Management | No application end-user accounts are implemented | Tests prove no account surface in the current application | Provider workforce, cloud admin, CI, support, service identity, MFA, JIT, and review processes PENDING | PENDING |
| Monitoring, Logging, and Auditing | Content-free application log policy and aggregate operational counters are defined | Content canaries and local lifecycle evidence | Production log sources, SIEM, retention, access authorization, alerting, and review PENDING | PARTIAL |
| Incident Response | Typed failures, bounded worker recovery, cleanup, and no false-clean behavior are implemented | Failure, timeout, cancellation, disconnect, replacement, and shutdown tests | Organizational incident plan, roles, notification, evidence preservation, exercises, and agency coordination PENDING | PARTIAL |
| Recovery Planning | Worker replacement and application recovery paths are tested | Lifecycle matrix and readiness tests | Service RTO, RPO, backups, region strategy, continuity plan, and recovery exercise PENDING | PARTIAL |
| Supply Chain Risk | Locked dependencies, SBOMs, model hashes, licenses, audits, and release manifest exist | Release inventory and point-in-time audits | Persistent upstream monitoring, supplier risk decisions, contracts, and response workflow PENDING | PARTIAL |
| Cybersecurity Education | No provider training evidence is stored in the repository | None | Organization roles, training content, completion, exercises, and effectiveness review PENDING | PENDING |
| Change Management | ADRs, implementation log, deterministic gates, source hashes, and release manifest exist | Local gate and release evidence | Organization approval workflow, production source of truth, emergency change, rollback, and continuous change metrics PENDING | PARTIAL |

## 5. Current ports and protocols

| Service | Port | Transport | Encryption | Status |
|---|---|---|---|---|
| Local evaluator HTTP | 8000 or mapped 8080 | TCP/HTTP | None on loopback | DOCUMENTED LOCAL ONLY |
| Candidate production web service | 443 | TCP/HTTPS | TLS configuration and terminating service PENDING | PENDING |
| Candidate internal application port | 8080 | TCP/HTTP within selected platform boundary | Platform path PENDING | PENDING |
| Administrative, monitoring, and platform APIs | PENDING | PENDING | PENDING | PENDING |

## 6. Completion method

1. Import the complete current FedRAMP rules and KSI inventory applicable to the selected class.
2. Map every rule and KSI to an implementation decision, internal verification, internal validation, independent assessment, and evidence location.
3. Bind the record to actual effective resources and organization-owned procedures.
4. Include non-implementation rationale and customer risk where applicable.
5. Generate current human-readable and JSON forms from one source of truth.
6. Validate the JSON against the current official schema.
7. Incorporate the independent assessor results without changing their intent.

## 7. Official basis

- [Security Decision Record](https://www.fedramp.gov/2026/providers/20x/rules/security-decision-record/)
- [Key Security Indicators](https://www.fedramp.gov/2026/reference/20x/c/key-security-indicators/)
- [Independent Verification and Validation](https://www.fedramp.gov/2026/providers/20x/rules/independent-verification-and-validation/)
- [FedRAMP JSON Schemas](https://www.fedramp.gov/schemas/)
