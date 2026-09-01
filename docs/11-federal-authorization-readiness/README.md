# Federal Authorization Readiness Start Package

Package status: PREPARATION DRAFT  
Prepared: 2026-09-01  
Official sources retrieved: 2026-09-01  
Current target: FedRAMP 20x preparation plus agency RMF handoff  
Certification class: PENDING  
Federal use case and agency owner: PENDING  

## Purpose

This directory organizes existing LabelVerify source evidence into a starting structure for FedRAMP 20x preparation and a later agency authorization decision. It records what is known from the repository, what must be established by the provider organization, and what belongs to an agency, a selected cloud platform, or a FedRAMP Recognized independent assessment service.

The package is designed to be updated after a federal use case, provider legal entity, certification class, deployment boundary, and operating model are selected.

## Artifact inventory

| File | Purpose | Status |
|---|---|---|
| `01_PATH_SCOPE_INTAKE.md` | Intake for FedRAMP scope, path, class, federal information, boundary, organization, and deployment decisions | OPEN |
| `02_CERTIFICATION_PACKAGE_OVERVIEW.md` | Human-readable preparation draft of the 20x Certification Package Overview | DRAFT |
| `02_CERTIFICATION_PACKAGE_OVERVIEW.template.json` | Template linked to the official CPO JSON Schema | INCOMPLETE TEMPLATE |
| `03_SECURITY_DECISION_RECORD.md` | Human-readable initial Security Decision Record | DRAFT |
| `03_SECURITY_DECISION_RECORD.template.json` | Template linked to the official SDR JSON Schema | PARTIAL TEMPLATE |
| `04_SECURE_CONFIGURATION_GUIDE.md` | Current secure defaults and pending production configuration decisions | DRAFT |
| `05_KSI_EVIDENCE_PLAN.md` | KSI applicability, implementation, verification, validation, and evidence plan | OPEN |
| `06_INDEPENDENT_ASSESSMENT_PLAN.md` | Assessor selection and independent verification and validation preparation | OPEN |
| `07_PRELIMINARY_POAM_RISK_REGISTER.md` | Preliminary remediation and risk tracking | OPEN |
| `08_CONTINUOUS_MONITORING_PLAN.md` | Persistent validation, vulnerability, reporting, change, and incident cadence | DRAFT |
| `09_AGENCY_RMF_ATO_HANDOFF.md` | Provider-to-agency RMF and ATO handoff checklist | DRAFT |
| `10_SHARED_RESPONSIBILITY_MATRIX.md` | Provider, Microsoft/Azure, agency, and assessor responsibility allocation | PENDING PLATFORM SELECTION |

## Existing repository evidence used

- Architecture and component boundary: `../04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md`
- Data, interface, lifecycle, and security decisions: `../04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md`
- Current runtime security behavior: `../04-i2r-ae/09_I2R_AS_BUILT_SECURITY_RUNTIME_ADDENDUM.md`
- Architecture decisions: `../04-i2r-ae/04_I2R_ADR_REGISTER.md`
- Runtime configuration examples: `../../.env.example`, `../../Dockerfile`, and `../../ops/fly.toml.example`
- Dependency and model inventory: `../10-release/DEPENDENCY_AND_MODEL_INVENTORY.md`
- SBOMs: `../10-release/sbom-python.cdx.json` and `../10-release/sbom-frontend.cdx.json`
- Local validation ledger: `../08-validation/ASSERTION_EVIDENCE_LEDGER.md`
- Machine-readable validation ledger: `../08-validation/evidence/assertion-evidence-ledger.json`
- Security lifecycle report: `../08-validation/evidence/security-post-fix/SECURITY_POST_FIX_REPORT.md`
- Browser privacy evidence: `../08-validation/evidence/browser-privacy-matrix.json`
- Release manifest: `../10-release/RELEASE_MANIFEST.sha256`

These artifacts are point-in-time source and local test evidence. Operational records begin only after an actual environment and operating organization exist.

## Status vocabulary

| Status | Meaning |
|---|---|
| DOCUMENTED | Supported by an identified current repository artifact |
| PARTIAL | Some implementation or evidence exists, but the full FedRAMP outcome is not established |
| PENDING | A required owner, decision, implementation, or evidence source has not been selected or supplied |
| NOT APPLICABLE | Determined inapplicable with approved rationale and risk review |
| IMPLEMENTED | Implemented in the effective environment and backed by current evidence |
| VALIDATED | Effectiveness was tested and current results are retained |
| INDEPENDENTLY ASSESSED | A FedRAMP Recognized independent assessment service completed the applicable review |

## Official source register

All external requirements and guidance in this package use the following primary sources. Retrieval date for every source is 2026-09-01.

### FedRAMP

- [Consolidated Rules for 2026 timeline](https://www.fedramp.gov/2026/timeline/)
- [Scope of FedRAMP](https://www.fedramp.gov/2026/scope/)
- [Choosing a Certification Path](https://www.fedramp.gov/2026/providers/start/path/)
- [Choosing a Certification Class](https://www.fedramp.gov/2026/providers/start/class/)
- [Minimum Assessment Scope](https://www.fedramp.gov/2026/providers/20x/rules/minimum-assessment-scope/)
- [Certification Package Overview](https://www.fedramp.gov/2026/providers/20x/rules/certification-package-overview/)
- [Security Decision Record](https://www.fedramp.gov/2026/providers/20x/rules/security-decision-record/)
- [Package Materials](https://www.fedramp.gov/2026/providers/20x/package/)
- [Secure Configuration Guide](https://www.fedramp.gov/2026/reference/20x/b/secure-configuration-guide/)
- [Key Security Indicators](https://www.fedramp.gov/2026/reference/20x/c/key-security-indicators/)
- [Independent Verification and Validation](https://www.fedramp.gov/2026/providers/20x/rules/independent-verification-and-validation/)
- [Vulnerability Detection and Response](https://www.fedramp.gov/2026/reference/20x/c/vulnerability-detection-and-response/)
- [Collaborative Continuous Monitoring](https://www.fedramp.gov/2026/providers/20x/rules/collaborative-continuous-monitoring/)
- [Using a FedRAMP Certified Cloud Service](https://www.fedramp.gov/2026/agencies/use/)
- [Initial Agency Authorization](https://www.fedramp.gov/2026/agencies/use/initial/)
- [FedRAMP JSON Schemas](https://www.fedramp.gov/schemas/)
- [Official CPO JSON Schema](https://www.fedramp.gov/schemas/fedramp-certification-package-overview-schema-2026-06-24.json)
- [Official SDR JSON Schema](https://www.fedramp.gov/schemas/fedramp-security-decision-record-schema-2026-06-24.json)

### NIST

- [FIPS 199, Security Categorization](https://csrc.nist.gov/pubs/fips/199/final)
- [SP 800-53 Rev. 5 controls](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final)
- [SP 800-53A Rev. 5 assessment procedures](https://csrc.nist.gov/pubs/sp/800/53/a/r5/final)
- [SP 800-53B control baselines](https://csrc.nist.gov/pubs/sp/800/53/b/upd1/final)
- [SP 800-37 Rev. 2 Risk Management Framework](https://csrc.nist.gov/pubs/sp/800/37/r2/final)
- [RMF Authorize step](https://csrc.nist.gov/Projects/risk-management/about-rmf/authorize-step)
- [RMF Monitor step](https://csrc.nist.gov/Projects/risk-management/about-rmf/monitor-step)

### Microsoft

- [Azure FedRAMP offering](https://learn.microsoft.com/en-us/azure/compliance/offerings/offering-fedramp)
- [Shared responsibility in the cloud](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility)

## Immediate next decision

Complete `01_PATH_SCOPE_INTAKE.md` before choosing a certification class, cloud service, or assessor. The existing Fly.io template is current prototype delivery planning. Azure, Azure Government, or any other federal production platform remains a separate pending selection.
