# Certification Package Overview Preparation Draft

Artifact status: DRAFT  
Official sources retrieved: 2026-09-01  
Official JSON Schema: [FedRAMP Certification Package Overview Schema, 2026-06-24](https://www.fedramp.gov/schemas/fedramp-certification-package-overview-schema-2026-06-24.json)  
Machine-readable companion: `02_CERTIFICATION_PACKAGE_OVERVIEW.template.json`

## 1. Package metadata

| Field | Value | Status |
|---|---|---|
| Provider name | PENDING provider legal entity | PENDING |
| Service name | LabelVerify | DOCUMENTED |
| Service acronym | LV | PRELIMINARY |
| FedRAMP ID | PENDING assignment | PENDING |
| UEI | PENDING organization decision and registration | PENDING |
| Certification type | 20x preparation baseline | PRELIMINARY |
| Certification class | PENDING path and use-case decision | PENDING |
| Service model | SaaS candidate | PENDING CONFIRMATION |
| Deployment model | PENDING | PENDING |
| Business category | Legal and Policy candidate | PENDING CONFIRMATION |
| Accountable package official | PENDING | PENDING |
| Security contact | PENDING | PENDING |
| Sales or acquisition contact | PENDING | PENDING |
| Product website | PENDING | PENDING |
| Trust center | PENDING | PENDING |
| Next Ongoing Certification Report | PENDING certification schedule | PENDING |
| Independent assessor | PENDING FedRAMP Recognized service | PENDING |

## 2. Service description

LabelVerify is a same-origin web application that helps a human reviewer compare manually entered or batch-manifest-supplied distilled-spirits application values with observations extracted from uploaded label images. The current source implements a React user interface, a session-only browser batch coordinator for 1 to 300 applications, a FastAPI request boundary, a supervised child process for full image decode through deterministic result aggregation, bundled RapidOCR and ONNX Runtime models, nineteen selected checks, evidence-linked results, and browser-generated CSV and detailed JSON exports.

The application does not issue a legal decision. A clean result means only that no difference was found in the selected checks. The current prototype has no application user accounts, database, durable queue, analytics, or required runtime external inference.

## 3. Candidate included services

| Service or feature | Description | Security category | Scope status |
|---|---|---|---|
| LabelVerify web interface | Same-origin intake, upload, processing, result, evidence, notes, and reset workflow | PENDING FIPS 199 and agency use | CANDIDATE IN SCOPE |
| Browser batch coordinator | Manifest and file inventory validation, ordered in-memory queue, sequential same-origin requests, progress, cancellation, retry, exception filtering, and local CSV or JSON export | PENDING | CANDIDATE IN SCOPE |
| LabelVerify verification API | Request validation, Host and Origin enforcement, admission, worker supervision, result and error delivery | PENDING | CANDIDATE IN SCOPE |
| Local OCR and rules pipeline | Image processing, OCR, candidate location, deterministic comparisons, selected rule evaluation | PENDING | CANDIDATE IN SCOPE |
| Health and readiness endpoint | Reports readiness only after required governed assets and worker checks | PENDING | CANDIDATE IN SCOPE |

## 4. Candidate excluded or unavailable features

- Direct COLAs Online integration
- External cloud OCR or generative inference in the required runtime path
- Accounts and tenant administration
- Durable reviewer notes or saved cases
- Database and durable application queue
- Comprehensive distilled-spirits regulatory determination

Exclusion from the product does not by itself remove provider administration, cloud platform, build, logging, monitoring, or support resources from the Minimum Assessment Scope.

## 5. Candidate information flows

1. For one label, a reviewer enters reference values and selects one to six images in the browser.
2. For a batch, the reviewer selects a folder containing exactly one manifest and its referenced images. The browser validates 1 to 300 rows, relative paths, file ownership, headers, case identifiers, and unreferenced files, then holds the ordered queue and source file objects in memory.
3. The browser sends one same-origin multipart request per application to the verification API. Batch requests are sequential and use the same endpoint and contract as the single-label path.
4. The API applies raw-body, multipart, field, signature, Host, Origin, rate, and capacity controls.
5. Admitted images are copied to a private request directory with generated internal names.
6. A supervised child process decodes images, applies pixel limits, preprocesses, runs local OCR, locates candidates, compares values, and aggregates all nineteen result rows.
7. The typed result returns to the browser. A batch result is attached to its in-memory row before the next request begins.
8. The supervisor closes handles and removes request-scoped artifacts after terminal outcomes.
9. Reviewer notes, disposition, queue state, row results, and selected evidence remain in the current browser tab and do not alter system findings.
10. CSV and detailed JSON exports are assembled and downloaded locally by the browser. They are not uploaded to a separate service by the application.

Actual TLS termination, cloud routing, provider administrative access, monitoring, backup, and agency integration flows are PENDING the production design.

## 6. Candidate third-party information resources

| Resource | Use | Certification or assurance status | Scope decision |
|---|---|---|---|
| Production cloud platform | Compute, network, TLS, availability, and platform administration | PENDING | PENDING |
| Microsoft Azure or Azure Government | Candidate only; no service selected | Exact services, regions, and FedRAMP package PENDING | PENDING |
| Python and npm dependencies | Application runtime and frontend | Versions and SBOMs documented; persistent upstream monitoring PENDING | CANDIDATE IN SCOPE |
| RapidOCR and ONNX model assets | OCR inference | Exact hashes and licenses documented | CANDIDATE IN SCOPE |
| Source control and CI/CD | Software change and delivery | Organization and service PENDING | PENDING |
| Logging, SIEM, ticketing, support | Operations and incident handling | Services PENDING | PENDING |

## 7. Current supporting repositories

| Repository type | Location | Authentication | Status |
|---|---|---|---|
| Preparation package | This directory | Local repository access | DOCUMENTED |
| Architecture and data flow | `../04-i2r-ae/` | Local repository access | DOCUMENTED |
| Validation and security evidence | `../08-validation/` | Local repository access | DOCUMENTED |
| QA, UAT, and defect evidence | `../09-qa-qc-uat/` | Local repository access | DOCUMENTED |
| Release manifest and SBOM | `../10-release/` | Local repository access | DOCUMENTED |
| FedRAMP-compatible trust center | PENDING | PENDING | PENDING |

## 8. Completion gates

- Establish every required identity, contact, website, and repository field.
- Select class, deployment model, cloud services, regions, and effective resources.
- Reconcile every information resource and third party to the Minimum Assessment Scope.
- Assign security categories and document cryptographic modules.
- Publish a complete service list and Secure Configuration Guide.
- Include the assessor-supplied assessment summary when required.
- Populate the official JSON format and validate it against the current schema.

## 9. Official basis

- [Certification Package Overview](https://www.fedramp.gov/2026/providers/20x/rules/certification-package-overview/)
- [Certification Data Sharing](https://www.fedramp.gov/2026/reference/certification-data-sharing/)
- [Minimum Assessment Scope](https://www.fedramp.gov/2026/providers/20x/rules/minimum-assessment-scope/)
- [FedRAMP JSON Schemas](https://www.fedramp.gov/schemas/)
