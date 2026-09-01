# Agency RMF and ATO Handoff

Artifact status: DRAFT  
Official sources retrieved: 2026-09-01  
Agency system owner: PENDING  
Agency authorizing official: PENDING  
Agency system and boundary: PENDING

## 1. Handoff objective

Supply reusable provider evidence for an agency information system that plans to use LabelVerify. The agency remains responsible for deciding the use, categorizing the information system, selecting and tailoring controls, configuring its integration, assessing its responsibilities, making the risk decision, issuing its ATO or ATU, and monitoring the use over time.

The agency authorization should cover the federal information system that uses LabelVerify as an external cloud service. It should not create a separate agency SSP by copying the provider Certification Package.

## 2. Agency use intake

| Topic | Required agency decision | Status |
|---|---|---|
| Mission and business use | Work supported, expected outcomes, service owner, business owner | PENDING |
| Users | User populations, administrators, support, contractors, public access | PENDING |
| Information | Federal information types, PII, CUI, records, enforcement, procurement, metadata | PENDING |
| Integrations | Identity provider, SIEM, ticketing, records, network, browser, APIs | PENDING |
| Prohibited uses | Data, features, jurisdictions, devices, integrations, and actions not permitted | PENDING |
| Availability | RTO, RPO, uptime, support, incident and continuity needs | PENDING |
| Legal and policy | Privacy, records, accessibility, acquisition, retention, incident, agency policy | PENDING |
| FedRAMP scope | Agency determination for this use | PENDING |

## 3. RMF work plan

| RMF step | Agency activity | Provider handoff | Exit artifact |
|---|---|---|---|
| Prepare | Identify roles, risk strategy, common controls, stakeholders, privacy and continuous monitoring needs | Provider contacts, service overview, responsibility matrix, current risk summary | Agency RMF plan and roles |
| Categorize | Categorize information and system under FIPS 199 based on confidentiality, integrity, and availability impact | Provider data-flow and service-boundary information | Approved security categorization |
| Select | Select and tailor SP 800-53B baseline and privacy controls; set parameters | FedRAMP class, provider capabilities, inheritance and customer responsibility information | Control baseline and allocation |
| Implement | Configure identity, logs, network, data, records, privacy, training, incident and recovery responsibilities | Secure Configuration Guide, APIs, service settings, integration instructions | Agency SSP implementation statements |
| Assess | Assess agency-owned and shared controls; reuse provider evidence for provider-owned capabilities | Current CPO, SDR, KSI, independent assessment, risk, vulnerability and ongoing data | Agency assessment report and findings |
| Authorize | Prepare risk response and decide whether the residual risk is acceptable | Provider open risks, restrictions, conditions and monitoring commitments | Authorization package and signed decision |
| Monitor | Review agency controls, integrations, configuration, provider reports, vulnerabilities, incidents and changes | Ongoing Certification Reports, quarterly reviews, vulnerability and change data | Ongoing authorization records |

## 4. Provider handoff package

- Current Certification Package Overview in human and JSON forms
- Current Security Decision Record in human and JSON forms
- Complete service list and Minimum Assessment Scope
- Information flows, security categories, metadata, third-party resources, and exclusions
- Secure Configuration Guide and machine-readable settings where available
- KSI records, metrics, internal verification, internal validation, and independent assessment
- Shared responsibility matrix and inherited capability references
- Cryptographic module inventory and data protection decisions
- Vulnerability, accepted-risk, incident, change, availability, and recovery information
- Current Ongoing Certification Report and next report date
- Provider and assessor contacts plus evidence access instructions

## 5. Agency SSP content

The agency SSP should identify:

- authorized use, users, information, and system boundary;
- exact LabelVerify service, features, class, deployment, and configuration;
- selected and tailored controls plus organization-defined parameters;
- agency common controls and outside dependencies;
- agency identity, network, SIEM, device, training, privacy, records, support, incident, and recovery implementation;
- provider capabilities used or relied upon by reference to the current Certification Package;
- restrictions, compensating controls, risks, and conditions for continued use.

## 6. Agency assessment and authorization package

| Artifact | Owner | Status |
|---|---|---|
| Agency system security and privacy plan | Agency system and privacy owners | PENDING |
| Security and privacy assessment report | Agency assessor | PENDING |
| Agency POA&M | Agency risk owners | PENDING |
| Risk assessment and response | Agency risk executive and system owner | PENDING |
| Authorization decision or ATO letter | Agency authorizing official | PENDING |
| FedRAMP notification after authorization | Agency | PENDING |
| Agency continuous monitoring strategy | Agency system owner and security team | PENDING |

## 7. Configuration and assessment checks

- [ ] Agency identity integration and access policy work as designed
- [ ] Required logs reach the agency SIEM with approved fields and timing
- [ ] Sharing, retention, encryption, support, and administrative settings remain approved
- [ ] Agency devices and browsers meet policy
- [ ] Incident and recovery contacts and exercises include both provider and agency
- [ ] Prohibited features and information are technically and procedurally controlled
- [ ] Provider risks and Certification Data fit agency risk tolerance
- [ ] Agency-owned findings remain in the agency POA&M
- [ ] Conditions for continued use and review cadence are explicit

## 8. Pilot treatment

If an agency approves a limited pilot, record the permitted information, users, duration, controls, prohibited uses, monitoring, and exit criteria. A pilot still follows applicable authorization, privacy, acquisition, records, and agency policy requirements.

## 9. Official basis

- [Using a FedRAMP Certified Cloud Service](https://www.fedramp.gov/2026/agencies/use/)
- [Initial Agency Authorization](https://www.fedramp.gov/2026/agencies/use/initial/)
- [Agency System Security Plan](https://www.fedramp.gov/2026/agencies/use/initial/ssp/)
- [NIST Risk Management Framework](https://csrc.nist.gov/Projects/risk-management/about-rmf)
- [NIST RMF Authorize step](https://csrc.nist.gov/Projects/risk-management/about-rmf/authorize-step)
- [NIST RMF Monitor step](https://csrc.nist.gov/Projects/risk-management/about-rmf/monitor-step)
- [NIST SP 800-53B](https://csrc.nist.gov/pubs/sp/800/53/b/upd1/final)
