# FedRAMP Path and Scope Intake

Artifact status: OPEN  
Official sources retrieved: 2026-09-01  
Decision owner: PENDING  
Federal agency use owner: PENDING  

## 1. Decision record

| Decision | Current value | Required owner | Closure evidence |
|---|---|---|---|
| Provider legal entity | PENDING | Provider executive | Legal name, UEI if applicable, accountable official, security and sales contacts |
| Federal use case | PENDING | Agency mission and system owners | Users, mission, information, integrations, prohibited uses, expected availability |
| FedRAMP scope determination | PENDING | Federal agency | Written determination under current FedRAMP scope guidance |
| Agency system boundary | PENDING | Agency system owner | Boundary, external services, common controls, interconnections |
| FIPS 199 categorization | PENDING | Agency information and system owners | Confidentiality, integrity, and availability impact rationale |
| Certification path | 20x Program path is the preparation baseline | Provider and FedRAMP | Confirmed path and application prerequisites |
| Certification class | PENDING | Provider with agency input | Lowest class that supports the agency use and business commitment |
| Class A qualifying framework | PENDING | Provider | Current SOC 2 Type II, GovRAMP, or eligible FedRAMP evidence if Class A is considered |
| Production cloud | PENDING | Provider architecture and security owners | Selected service model, regions, inherited package, contract, and actual configuration |
| Azure service selection | PENDING | Provider and agency | Exact Azure or Azure Government services and regions, if selected |
| FedRAMP Recognized assessor | PENDING | Provider | Marketplace identity, engagement, independence, and scope |
| Agency ATO strategy | PENDING | Agency authorizing official and system owner | Agency RMF plan, SSP approach, assessment and authorization milestones |

## 2. Current use and product facts

| Topic | Current source-backed fact | Status |
|---|---|---|
| Product | LabelVerify is a browser-based evidence assistant that compares manually entered or manifest-supplied application values with OCR observations from one to six label panels per application | DOCUMENTED |
| Supported rule profile | Nineteen selected distilled-spirits checks; no comprehensive regulatory decision | DOCUMENTED |
| Human authority | The reviewer makes the final decision; OCR confidence is not an approval score | DOCUMENTED |
| User content | Reference values, batch manifest rows, selected image file objects, queue state, results, notes, and exports are handled in browser memory; each active verification also uses request-scoped storage and process memory | DOCUMENTED |
| Persistence | No application database, account, durable queue, or intended browser content persistence | DOCUMENTED |
| Runtime inference | Bundled local RapidOCR and ONNX Runtime models; no required runtime cloud inference | DOCUMENTED |
| Current deployment | No production or federal environment is established | PENDING |
| Intended production information | Synthetic or sanitized evaluation data only under current prototype guidance | DOCUMENTED |
| Federal customer data | Types, sensitivity, records status, privacy status, and retention needs are PENDING | PENDING |

## 3. Scope intake questions

Answer each question before establishing the Minimum Assessment Scope.

1. Which agency system will use LabelVerify, and is the product a shared commercial service or a single-agency operated application?
2. What federal information will be created, collected, processed, transmitted, or exposed to the service?
3. Are uploaded label images, application values, reviewer notes, IP-derived security identifiers, and operational metadata federal records?
4. Are PII, CUI, procurement-sensitive information, enforcement information, credentials, or regulated business data permitted?
5. Which users and administrators exist, and which identity provider and account lifecycle apply?
6. Which features, integrations, APIs, support channels, and administrative paths are permitted or prohibited?
7. What confidentiality, integrity, and availability impact applies to each information type under FIPS 199?
8. What recovery time, recovery point, availability, support, and incident notification objectives apply?
9. Which provider organization systems can affect the service, including source control, CI/CD, ticketing, identity, secrets, monitoring, support, and assessor portals?
10. Which third-party information resources can handle or affect federal customer data?
11. Which cloud services, regions, network boundaries, encryption services, key stores, logs, backups, and security services will be used?
12. Which controls are provider-owned, inherited, shared, or agency-owned?

## 4. Candidate Minimum Assessment Scope

The following is a starting inventory, not an approved boundary.

| Candidate resource | Function | Handles or affects federal customer data | Current status |
|---|---|---|---|
| React browser application | Single intake, batch manifest validation, ordered queue coordination, result, evidence, session-only review state, and exports | Handles entered values, manifests, image file objects, queue state, results, notes, CSV, and JSON in browser memory | SOURCE EXISTS; FEDERAL USE PENDING |
| FastAPI service | Same-origin UI delivery, request boundary, validation, admission, response | Handles request data and result data | SOURCE EXISTS; DEPLOYMENT PENDING |
| Supervised worker child | Decode, preprocessing, OCR, candidate location, comparison, aggregation | Handles decoded images, OCR tokens, candidates, and results | SOURCE EXISTS; DEPLOYMENT PENDING |
| Request spool | Private request-scoped temporary files | Handles uploaded image copies | SOURCE EXISTS; EFFECTIVE STORAGE PENDING |
| OCR models and rule registries | Deterministic inference and selected checks | Affect integrity of results | GOVERNED SOURCE EXISTS |
| Container and base image | Runtime packaging | Affects all service security objectives | SOURCE EXISTS; OCI PROOF PENDING |
| Cloud compute and networking | Hosting, TLS, routing, isolation, availability | Handles traffic and can affect all data | PLATFORM AND SERVICES PENDING |
| Provider identity and CI/CD | Administrative access and software delivery | Can affect confidentiality, integrity, and availability | ORGANIZATION AND TOOLING PENDING |
| Logging, monitoring, and incident tooling | Detection, investigation, response, evidence | May handle metadata or sensitive security information | PENDING |
| Support and ticketing | Customer support and incident coordination | Potential federal data exposure depends on procedure | PENDING |
| Agency identity, SIEM, devices, and operating procedures | Agency integration and use | Agency-owned or shared | PENDING AGENCY DESIGN |

## 5. Path and class decision logic

- Use the current 20x Program Certification path as the planning baseline unless FedRAMP confirms a specific alternative.
- Do not use the retired FedRAMP Ready intake as the target package.
- Consider Class A only if the provider has a current qualifying alternative framework assessment and a mature operating program.
- Select Class B or Class C only after the agency use, FIPS 199 categorization, assurance needs, and provider investment are understood.
- Do not treat a certification class as a substitute for the agency security categorization or risk decision.
- Do not select Azure services solely because Azure has FedRAMP coverage. Confirm that every exact service, feature, region, and configuration is in the applicable Microsoft audit scope and record the customer responsibilities.

## 6. Intake exit criteria

- [ ] Provider legal entity and accountable official named
- [ ] Federal use case and agency owner documented
- [ ] FedRAMP scope determination recorded
- [ ] FIPS 199 categorization recorded
- [ ] Certification path and class approved
- [ ] Production platform and exact services selected
- [ ] Candidate Minimum Assessment Scope reconciled to effective resources
- [ ] Third-party information resources identified
- [ ] Provider, platform, agency, and assessor responsibilities allocated
- [ ] FedRAMP Recognized assessor engagement plan approved
- [ ] Agency RMF and ATO handoff owner identified

## 7. Official basis

- [FedRAMP scope](https://www.fedramp.gov/2026/scope/)
- [Choosing a Certification Path](https://www.fedramp.gov/2026/providers/start/path/)
- [Choosing a Certification Class](https://www.fedramp.gov/2026/providers/start/class/)
- [Minimum Assessment Scope](https://www.fedramp.gov/2026/providers/20x/rules/minimum-assessment-scope/)
- [FIPS 199](https://csrc.nist.gov/pubs/fips/199/final)
- [Microsoft Azure FedRAMP offering](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-fedramp)
