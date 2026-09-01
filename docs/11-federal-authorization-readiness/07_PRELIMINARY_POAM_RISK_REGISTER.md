# Preliminary POA&M and Risk Register

Artifact status: PRELIMINARY  
Official sources retrieved: 2026-09-01  
Risk acceptance authority: PENDING provider and agency roles  
Target dates: PENDING program approval and sequencing

## 1. Tracking rules

- One row identifies one actionable weakness or unresolved risk decision.
- Status values are OPEN, IN PROGRESS, BLOCKED, ACCEPTED, CLOSED, or TRANSFERRED.
- Closure requires evidence and an identified approver.
- An agency POA&M should contain agency-owned issues. Provider certification risks remain in the provider package and ongoing reports as required.

## 2. Preliminary register

| ID | Area | Weakness or pending condition | Preliminary impact | Required action | Owner | Target | Status |
|---|---|---|---|---|---|---|---|
| `FAR-001` | Organization | Provider legal entity, UEI, accountable official, security contact, and acquisition contact are not established in this package | Package ownership and public fields cannot be completed | Establish provider identity and accountable roles | Provider executive | PENDING | OPEN |
| `FAR-002` | Agency use | Federal use case, agency owner, permitted information, integrations, and prohibited uses are not established | Scope, categorization, and assurance needs cannot be determined | Complete agency use-case intake | Agency mission and system owners | PENDING | OPEN |
| `FAR-003` | Scope and class | FedRAMP scope determination, FIPS 199 categorization, and certification class are pending | Wrong path or under-scoped assessment | Record agency scope decision and categorization, then select class | Agency and provider | PENDING | OPEN |
| `FAR-004` | Boundary | Effective cloud, organization, third-party, metadata, support, and administrative resources are unknown | Security-relevant resources may be omitted | Build and validate effective Minimum Assessment Scope | Provider security architect | PENDING | OPEN |
| `FAR-005` | Deployment | Production cloud, service model, regions, and actual configuration are not selected | No operational implementation or inherited control evidence | Select platform and exact services; document actual configuration | Provider platform owner | PENDING | OPEN |
| `FAR-006` | Azure | Azure or Azure Government is only a candidate; exact in-scope services and regions are unknown | Microsoft inheritance may be assumed incorrectly | Select exact services and verify Microsoft and Marketplace scope before allocation | Provider platform and compliance owners | PENDING | OPEN |
| `FAR-007` | Identity | Workforce, cloud admin, CI, service, support, assessor, and break-glass identities are not defined | Unauthorized or excessive privileged access | Implement identity inventory, phishing-resistant MFA, JIT, least privilege, lifecycle, and reviews | Provider IAM owner | PENDING | OPEN |
| `FAR-008` | Logging | Production sources, SIEM, fields, content filtering, retention, access, alerting, and agency export are not defined | Detection and investigation may be incomplete or expose content | Design and validate logging and monitoring architecture | Provider security operations | PENDING | OPEN |
| `FAR-009` | Data and retention | Federal information types, metadata, records status, privacy requirements, retention, backup, deletion, support handling, and legal hold are unknown | Data may be retained, deleted, or disclosed incorrectly | Complete data inventory and approved lifecycle schedule | Agency information owner and provider privacy owner | PENDING | OPEN |
| `FAR-010` | Cryptography | TLS, storage, backup, secret, key, and cryptographic module inventory and CMVP status are unknown | Federal data protection cannot be evaluated | Select services and document modules, usage, validation, keys, and configuration | Provider crypto and platform owners | PENDING | OPEN |
| `FAR-011` | Incident response | Organization roles, detection, reporting, evidence preservation, agency coordination, exercises, and lessons learned are absent | Delayed or incomplete response and reporting | Establish and exercise provider incident plan | Provider incident commander | PENDING | OPEN |
| `FAR-012` | Recovery | Service RTO, RPO, backups, restore, dependency recovery, regional strategy, and exercises are absent | Service may not recover to agency needs | Approve objectives and validate recovery capability | Provider continuity owner with agency input | PENDING | OPEN |
| `FAR-013` | Vulnerability operations | Current audits and scans are point-in-time only | Drift and new vulnerabilities may go undetected | Implement persistent coverage, evaluation, remediation, KEV, exception, and reporting workflow | Provider vulnerability owner | PENDING | OPEN |
| `FAR-014` | Supply chain | Persistent upstream monitoring, supplier risk review, contracts, and response are not established | Third-party compromise may not be detected or managed | Establish supplier inventory, monitoring, criticality, and response | Provider supply-chain owner | PENDING | OPEN |
| `FAR-015` | KSI automation | Complete KSI applicability, automation methods, cycles, and metrics history are absent | Certification evidence will be incomplete | Generate KSI inventory and implement selected-class verification and validation | Provider compliance engineering | PENDING | OPEN |
| `FAR-016` | Independent assessment | No FedRAMP Recognized assessor is selected | Required independent verification and validation cannot occur | Select assessor and complete initial assessment | Provider compliance owner | PENDING | OPEN |
| `FAR-017` | Continuous monitoring | Package maintenance, ongoing report, change, vulnerability, incident, and review cadence is not operating | Certification data will become stale | Implement `08_CONTINUOUS_MONITORING_PLAN.md` | Provider continuous monitoring owner | PENDING | OPEN |
| `FAR-018` | Agency ATO | Agency SSP, control allocation, assessment, POA&M, risk response, and ATO plan are not established | Agency use cannot reach an authorization decision | Execute `09_AGENCY_RMF_ATO_HANDOFF.md` | Agency system owner and authorizing official | PENDING | OPEN |

## 3. Existing strengths to preserve

- Exact request and image limits
- Host and Origin enforcement
- Same-origin design and no broad CORS grant
- Request-scoped storage and explicit cleanup ownership
- Supervised full decode through aggregation
- No required runtime external inference
- Content-free application logging policy
- No-store responses and browser privacy tests
- Locked dependencies, SBOMs, model hashes, license inventory, and release manifest
- Deterministic product corpus and false-clean protections
- Human final-decision boundary

## 4. Review cadence

Review this register at least monthly during preparation, on every material architecture decision, and before any assessor or agency handoff. Replace preliminary impact with the approved provider and agency risk method after roles and categorization are established.

## 5. Official basis

- [NIST RMF Authorize step](https://csrc.nist.gov/Projects/risk-management/about-rmf/authorize-step)
- [NIST RMF Monitor step](https://csrc.nist.gov/Projects/risk-management/about-rmf/monitor-step)
- [FedRAMP Initial Agency Authorization](https://www.fedramp.gov/2026/agencies/use/initial/)
- [FedRAMP Collaborative Continuous Monitoring](https://www.fedramp.gov/2026/providers/20x/rules/collaborative-continuous-monitoring/)
