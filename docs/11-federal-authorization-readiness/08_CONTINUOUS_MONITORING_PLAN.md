# Continuous Monitoring Plan

Artifact status: DRAFT  
Official sources retrieved: 2026-09-01  
Certification class: PENDING  
Continuous monitoring owner: PENDING

## 1. Objective

Maintain current, understandable, human-readable, and machine-readable security information that supports provider risk decisions, FedRAMP Certification, independent assessment, and agency ongoing authorization.

## 2. Cadence baseline

| Activity | Current official baseline | Planned cadence | Status |
|---|---|---|---|
| Certification package maintenance | Class B at least monthly; Class C at least every two weeks | PENDING class selection | PENDING |
| Ongoing Certification Report | Every three months | Every three months after certification | PENDING |
| Quarterly Review | Class B SHOULD host every three months; Class C MUST host every three months | PENDING class selection | PENDING |
| Independent KSI assessment | At least annually for Class B and Class C | Annual | PENDING ASSESSOR |
| Human-readable vulnerability activity report | At least monthly | Monthly | PENDING |
| Class C machine-resource verification and validation | At least every three days | Every three days if Class C | PENDING |
| Non-machine resource verification and validation | At least every three months under current VDR rule | Every three months | PENDING |
| Change review | On every change, with significant-change handling where applicable | On change | PARTIAL SOURCE PROCESS |
| Incident reporting | On reportable incident according to current FedRAMP and agency rules | Event driven | PENDING INCIDENT PLAN |
| Risk register review | Provider-defined preparation cadence | Monthly and on material change | OPEN |

The selected class and current effective rules control the final cadence. Recheck the FedRAMP changelog before implementation and each assessment.

## 3. Monitored resources and signals

| Area | Required sources and signals | Current source seed | Status |
|---|---|---|---|
| Resource inventory | Cloud resources, services, regions, identities, dependencies, third parties, endpoints, data stores | Architecture source only | PENDING AUTOMATION |
| Configuration | IaC, cloud settings, application environment, network, TLS, identity, secrets, logging, backup | `.env.example`, Dockerfile, planned template | PENDING EFFECTIVE SOURCE |
| Availability and capacity | Readiness, latency, errors, admission, worker state, memory, CPU, storage, queue | Local performance and lifecycle evidence | PARTIAL |
| Vulnerabilities | Hosts, images, packages, source, dependencies, third parties, KEV status, exposure, mitigation | Point-in-time audits and security scans | PARTIAL |
| Identity | Account lifecycle, owner, MFA, JIT, privilege, dormant state, service identities, access reviews | None | PENDING |
| Logging and detection | Source delivery, parsing, filtering, alert state, access, retention, time | Aggregate application counters only | PENDING |
| Data protection | Data flows, encryption, keys, temporary storage, deletion, backups, support handling | Current request lifecycle and cleanup evidence | PARTIAL |
| Supply chain | SBOM drift, model and dependency provenance, supplier notices, upstream vulnerabilities | SBOMs, locks, hashes, licenses | PARTIAL |
| Incident and recovery | Incidents, exercises, RTO, RPO, restore and failover results, corrective actions | Worker lifecycle recovery only | PARTIAL |
| Change | Approved, emergency, adaptive, routine, and transformative changes plus rollback | ADRs, implementation log, release manifest | PARTIAL |

## 4. Ongoing Certification Report content

Prepare a report every three months that includes:

- changes to Certification Data;
- planned changes for at least the next three months;
- accepted vulnerabilities;
- transformative changes;
- updated security and configuration recommendations;
- agencies directly using the service;
- reportable incidents or an attestation that none occurred;
- next report date;
- anonymized and desensitized feedback summary;
- links to current machine-readable data where required.

Do not include federal customer content or sensitive details that would likely harm the service. Establish controlled access for sensitive supporting evidence.

## 5. Operational workflow

1. Collect evidence from authoritative systems, not manual summaries where automation is practical.
2. Verify that each measure is implemented as described.
3. Validate that each measure produces the intended outcome.
4. Reconcile all effective resources to coverage.
5. Triage failures and drift into the risk register or incident process.
6. Correct, mitigate, accept, or transfer risk using approved authority.
7. Update CPO, SDR, SCG, KSI records, vulnerability data, and change records.
8. Publish or share the required reports through approved repositories.
9. Retain assessor and agency feedback and respond without changing its intent.
10. Review recurring patterns and improve controls, tests, and monitoring.

## 6. Roles

| Role | Responsibility | Status |
|---|---|---|
| Accountable package official | Approves current certification data and risk decisions | PENDING |
| Continuous monitoring owner | Coordinates collection, reconciliation, reporting, and review | PENDING |
| Security operations | Detection, triage, incident, logging, and vulnerability operations | PENDING |
| Platform owner | Resource, configuration, network, identity, key, backup, and availability sources | PENDING |
| Application owner | Application security, tests, release, lifecycle, SBOM, and product behavior | PENDING |
| Privacy and records owners | Information lifecycle, retention, disclosure, and agency requirements | PENDING |
| Independent assessor | Annual independent verification and validation | PENDING |
| Agency security team | Reviews ongoing data for agency risk and authorization | PENDING |

## 7. Current implementation steps

- [ ] Select class and import current applicable timeframes
- [ ] Select effective cloud and inventory APIs
- [ ] Define authoritative sources and data schemas
- [ ] Implement coverage reconciliation and stale-data alerts
- [ ] Implement selected-class KSI automation and metrics retention
- [ ] Establish vulnerability, incident, change, and risk workflows
- [ ] Establish trust center and controlled evidence repositories
- [ ] Generate and validate CPO, SDR, report, vulnerability, and change JSON
- [ ] Schedule independent assessment and agency review
- [ ] Exercise missed-report, sensor-failure, stale-data, and incident scenarios

## 8. Official basis

- [Collaborative Continuous Monitoring](https://www.fedramp.gov/2026/providers/20x/rules/collaborative-continuous-monitoring/)
- [Certification Package Overview maintenance](https://www.fedramp.gov/2026/providers/20x/rules/certification-package-overview/)
- [Vulnerability Detection and Response](https://www.fedramp.gov/2026/reference/20x/c/vulnerability-detection-and-response/)
- [Vulnerability Evaluation and Reporting](https://www.fedramp.gov/2026/reference/vulnerability-evaluation-and-reporting/)
- [NIST RMF Monitor step](https://csrc.nist.gov/Projects/risk-management/about-rmf/monitor-step)
