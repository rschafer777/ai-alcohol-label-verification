# Key Security Indicator Evidence Plan

Artifact status: OPEN  
Official sources retrieved: 2026-09-01  
Certification class and complete KSI applicability: PENDING

## 1. Evidence model

For every applicable KSI, maintain one record with:

1. KSI identifier and current official text.
2. Measure objective and implementation statement.
3. Effective resources and responsible owner.
4. Persistent cycle, if applicable.
5. Internal verification that the measure is implemented as described.
6. Internal validation that the measure produces the intended outcome.
7. Automation verification and validation.
8. Tests and current evidence locations.
9. Independent assessor conclusion and provider response.
10. Metrics history and current exceptions.

The complete applicable KSI list must be regenerated from the current FedRAMP rules after class selection. The rows below are preparation workstreams, not a substitute for that generated inventory.

## 2. Workstream plan

| KSI workstream | Current repository seed | Required measure and evidence | Internal verification and validation plan | Status |
|---|---|---|---|---|
| Cloud Native Architecture | Component model, dependency direction, non-root Dockerfile, supervised child, limits, readiness, ADRs | Effective resource inventory, strict functions and privileges, intended-state source, drift detection, segmentation, resilience | Compare deployed inventory and policy to source; continuously detect drift; exercise failure, replacement, and recovery | PARTIAL |
| Service Configuration | Host and Origin enforcement, security headers, no-store, input limits, local inference, cleanup | Approved configuration baseline, TLS, keys, network, secrets, storage, service settings, secure export | Export settings; compare to approved defaults; run positive and negative configuration tests | PARTIAL |
| Identity and Access Management | No application user accounts | Workforce and service identity inventory, phishing-resistant MFA, JIT, least privilege, lifecycle automation, reviews, break-glass | Reconcile accounts to owners; validate deprovisioning, privilege elevation, suspicious-activity response, and access review | PENDING |
| Monitoring, Logging, and Auditing | Content-free log policy, aggregate counters, canary tests | Production source inventory, centralized collection, access controls, retention, integrity, time, alerts, agency export | Inject safe test events; verify collection, field filtering, alerting, access, retention, and SIEM delivery | PARTIAL |
| Incident Response | Typed error behavior, no false clean, bounded cancellation and worker recovery | Organization plan, roles, reporting thresholds, communication, evidence preservation, exercises, lessons learned | Tabletop and technical exercise; measure detection, containment, notification, recovery, and corrective actions | PARTIAL |
| Recovery Planning | Worker restart and readiness recovery tests | Service RTO and RPO, backup inventory, restore, dependency and regional recovery, continuity procedures | Scheduled restore and failover exercises measured against approved objectives | PARTIAL |
| Supply Chain Risk | Lockfiles, SBOMs, model manifest, hashes, licenses, dependency audits, release manifest | Supplier inventory, criticality, provenance, upstream monitoring, contractual notice, change and remediation workflow | Reconcile effective software to SBOM; inject safe advisory scenarios; verify triage and remediation records | PARTIAL |
| Change Management | ADRs, implementation log, tests, source hashes, release manifest | Approved production change workflow, separation of duties, emergency change, rollback, drift and significant-change classification | Trace sample normal and emergency changes from request through deployment, validation, rollback, and reporting | PARTIAL |
| Cybersecurity Education | None in source package | Role inventory, general training, secure development, privileged operations, incident and recovery training | Completion evidence plus exercises and effectiveness review | PENDING |
| Vulnerability Detection and Response | Point-in-time audits, source scans, dependency upgrades, defect evidence | Persistent machine and non-machine coverage, attack-surface inventory, evaluation, PAIN decisions, KEV handling, remediation, reporting | Reconcile scanner coverage to all resources; validate finding flow, timeframes, exceptions, and monthly reporting | PARTIAL |
| Data Protection and Cryptography | Request-scoped data, no database, no-store, cleanup, source content restrictions | Federal information categories, metadata, retention, backups, TLS, storage encryption, keys, module and CMVP inventory | Trace representative data and metadata; validate encryption, deletion, access, recovery, and module configuration | PARTIAL |

## 3. Candidate source evidence map

| Evidence | Supports | Limit |
|---|---|---|
| `../04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md` | Architecture, components, workflow, technology, data lifecycle | Design and local implementation only |
| `../04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md` | Ingress, flows, lifecycle, limits, worker ownership, threats, response security | Effective cloud and organization controls PENDING |
| `../04-i2r-ae/10_I2R_BATCH_AND_READINESS_ARCHITECTURE.md` | Browser batch manifest, file ownership, in-memory queue, sequential requests, cancellation, retry, results, and exports | Session-only client coordination; no durable server queue |
| `../04-i2r-ae/09_I2R_AS_BUILT_SECURITY_RUNTIME_ADDENDUM.md` | Current runtime implementation details | No production environment |
| `../08-validation/evidence/security-post-fix/SECURITY_POST_FIX_REPORT.md` | Lifecycle, cleanup, recovery, canaries, source no-egress | Point-in-time local evidence |
| `../08-validation/evidence/browser-privacy-matrix.json` | Browser storage and lifecycle behavior | Chrome test environment only |
| `../08-validation/evidence/local-batch-performance.json` | Actual 10, 20, and 300 application sequential capacity and elapsed time | One Windows host and governed two-panel sample |
| `../10-release/DEPENDENCY_AND_MODEL_INVENTORY.md` and SBOMs | Software, models, hashes, license, audit snapshot | Persistent supply-chain operations PENDING |
| `../08-validation/evidence/assertion-evidence-ledger.json` | Local test outcomes and honest blockers | Not a FedRAMP KSI inventory |

## 4. Automation plan

| Automation | Input | Output | Frequency | Status |
|---|---|---|---|---|
| Effective resource inventory | Cloud APIs, IaC, identity, services, dependencies | Human and JSON inventory with owners and scope | Persistent and on change | PENDING |
| Configuration comparison | Approved secure defaults and effective settings | Drift and exception report | Persistent | PENDING |
| Vulnerability detection | Images, hosts, packages, source, dependencies, third parties | Normalized findings and coverage | Selected-class cadence | PENDING |
| Identity reconciliation | Identity provider, cloud IAM, CI, support, service accounts | Owner, privilege, MFA, JIT, dormant and exception report | Persistent | PENDING |
| Log and alert validation | Source catalog, safe synthetic events, SIEM rules | Delivery, parsing, alert, retention and access results | Scheduled and on change | PENDING |
| Data lifecycle canaries | Safe markers across request, storage, logs, backup, support | Presence, absence, deletion, and unauthorized-flow results | Release and scheduled operations | PARTIAL LOCAL |
| Recovery exercise | Backup, restore, worker, service and regional procedures | RTO, RPO, integrity and action record | Approved cadence | PARTIAL LOCAL |
| Package generation | Authoritative control and evidence sources | CPO, SDR, KSI, report, inventory and change data | Selected-class cadence | PENDING |

If Class C is selected, the implementation plan must meet the current requirement for at least two automated verification and validation methods per KSI and the required historical metrics period.

## 5. Evidence quality rules

- Evidence must identify the effective resource, environment, source, time, owner, result, and applicable rule or KSI.
- Verification proves the measure is implemented as described.
- Validation proves the measure produces the intended security outcome.
- A source file or screenshot alone is not effectiveness evidence.
- Sensitive content must be excluded or protected according to the package access model.
- Failed and partial outcomes remain visible and link to the risk register.
- Assessor statements are retained without changing their intent.

## 6. Official basis

- [Key Security Indicators](https://www.fedramp.gov/2026/reference/20x/c/key-security-indicators/)
- [Security Decision Record](https://www.fedramp.gov/2026/providers/20x/rules/security-decision-record/)
- [Class C Certification requirements](https://www.fedramp.gov/2026/reference/20x/c/fedramp-certification/)
- [Vulnerability Detection and Response](https://www.fedramp.gov/2026/reference/20x/c/vulnerability-detection-and-response/)
- [NIST SP 800-53A Rev. 5](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final)
