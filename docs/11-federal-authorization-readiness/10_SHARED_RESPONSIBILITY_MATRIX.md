# Shared Responsibility Matrix

Artifact status: DRAFT  
Official sources retrieved: 2026-09-01  
Provider organization: PENDING  
Microsoft Azure or Azure Government services: PENDING  
Federal agency and use: PENDING  
Independent assessor: PENDING

## 1. Allocation method

This matrix is a starting allocation. Replace each PENDING cell with the exact service, organization, contract, provider package reference, agency common control, implementation, and evidence source after decisions are made.

Microsoft states that cloud customers retain responsibility for data, identities, configurations, and access management across service models. Application, network, operating-system, and infrastructure responsibility changes with IaaS, PaaS, or SaaS. The exact allocation therefore depends on the selected Azure or Azure Government services and features.

## 2. Responsibility matrix

Legend: `P` provider organization, `M` Microsoft/Azure, `A` federal agency, `I` independent assessor, `S` shared, `-` no primary implementation responsibility.

| Responsibility | P | M | A | I | Current allocation and evidence status |
|---|:---:|:---:|:---:|:---:|---|
| Determine agency use and FedRAMP scope | S | - | S | - | Agency decision with provider use-case input; PENDING |
| Categorize agency information system under FIPS 199 | - | - | A | - | PENDING agency information and system owners |
| Select FedRAMP certification path and class | P | - | S | - | 20x preparation baseline; class PENDING |
| Define provider Minimum Assessment Scope | P | S | - | I | Source draft exists; effective cloud and organization resources PENDING |
| Maintain CPO, SDR, SCG, KSI and ongoing data | P | S | - | I | Preparation drafts exist; operating process PENDING |
| Physical datacenter and physical network | - | M | - | I | Applies only after exact Microsoft service and region selection; PENDING |
| Physical hosts and virtualization | S | M | - | I | Allocation depends on IaaS, PaaS, or SaaS; PENDING |
| Operating system and runtime | S | S | - | I | Provider owns application runtime in current container design; Microsoft allocation PENDING service choice |
| Application code and dependencies | P | - | - | I | Repository, lockfiles, tests, SBOMs and model manifest exist |
| Container build and image provenance | P | S | - | I | Dockerfile exists; effective builder, registry, signing, scan and OCI evidence PENDING |
| Cloud service and feature selection | P | S | S | I | Exact Azure or Azure Government services and audit scope PENDING |
| Network architecture and egress | P | S | S | I | Application no-egress source behavior exists; platform enforcement and agency integration PENDING |
| TLS and cryptographic modules | S | S | S | I | Termination, modules, CMVP status, keys and agency requirements PENDING |
| Customer data classification | S | - | A | - | Prototype synthetic and sanitized guidance exists; production categories PENDING |
| Data minimization and application lifecycle | P | S | S | I | Request-scoped design and cleanup tests exist; platform metadata, backup and support paths PENDING |
| Retention, records, privacy and legal holds | S | S | A | I | PENDING agency requirements and provider implementation |
| End-user identities and devices | S | S | A | I | Application accounts are not implemented; agency identity and device design PENDING |
| Provider workforce and privileged identities | P | S | - | I | Identity provider, MFA, JIT, RBAC, reviews and break-glass PENDING |
| Service identities, secrets and keys | P | S | - | I | PENDING cloud and CI design |
| Secure application configuration | P | S | S | I | Application defaults documented; effective environment and agency settings PENDING |
| Logging and telemetry generation | P | S | S | I | Content-free application policy exists; cloud and agency log sources PENDING |
| SIEM collection, detection and alert response | S | S | S | I | Tooling, routing, retention, access and procedures PENDING |
| Vulnerability detection and response | P | S | S | I | Point-in-time application evidence exists; cloud, persistent and agency workflows PENDING |
| Software supply-chain risk | P | S | S | I | SBOM and lock evidence exists; supplier and upstream monitoring PENDING |
| Incident detection and provider response | P | S | S | I | Application failures are bounded; organization process and coordination PENDING |
| Agency incident handling and reporting | S | S | A | I | PENDING agency integration and reporting plan |
| Backup, restore and service recovery | P | S | S | I | Worker recovery exists; cloud backup, RTO, RPO and service recovery PENDING |
| Change and significant-change handling | P | S | S | I | Source change records exist; production and FedRAMP process PENDING |
| Independent verification and validation | S | S | S | I | FedRAMP Recognized assessor PENDING |
| Agency SSP, assessment, POA&M and ATO | S | S | A | S | Agency-owned; all artifacts PENDING |
| Provider ongoing certification reporting | P | S | - | I | Plan exists; operation and history PENDING |
| Agency ongoing authorization monitoring | S | S | A | - | PENDING agency strategy and review owners |

## 3. Evidence inheritance rules

- Use Microsoft evidence only for the exact selected service, feature, deployment model, and region in the applicable Microsoft and FedRAMP package.
- Record Microsoft-responsible, provider-responsible, agency-responsible, and shared measures separately.
- Azure Policy mappings and compliance dashboards can support assessment, but Microsoft states they provide only a partial view of overall compliance.
- Provider source tests do not prove Microsoft controls or deployed effectiveness.
- Microsoft package evidence does not cover LabelVerify application code, customer configuration, data classification, identities, or agency controls.
- Agency authorization should reference provider and Microsoft evidence where appropriate and describe the agency implementation it owns.

## 4. Completion gates

- [ ] Provider legal entity and roles assigned
- [ ] Agency use and roles assigned
- [ ] Azure or other cloud platform selected
- [ ] Exact services, features, regions and applicable package references recorded
- [ ] Effective resources reconciled to the Minimum Assessment Scope
- [ ] Every shared row decomposed into named measures and evidence
- [ ] Agency common controls and integrations recorded
- [ ] Assessor agrees that allocation and evidence access are adequate
- [ ] Matrix versioned and reviewed on every material change

## 5. Official basis

- [FedRAMP shared agency use model](https://www.fedramp.gov/2026/agencies/use/)
- [FedRAMP Minimum Assessment Scope](https://www.fedramp.gov/2026/providers/20x/rules/minimum-assessment-scope/)
- [Microsoft shared responsibility](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility)
- [Microsoft Azure FedRAMP offering](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-fedramp)
