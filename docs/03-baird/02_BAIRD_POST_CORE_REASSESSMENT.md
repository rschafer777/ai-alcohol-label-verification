# BAIRD Post-Core Reassessment

Document control ID: LV-BRD-002  
Revision: 1.0  
Date: 2026-09-01  
Status: Approved requirements correction  
Authority: Original discovery, LV-BRD-001, completed single-submission validation, and requester direction

## 1. Purpose

This reassessment executes the post-core decision that the original BAIRD required. The single-submission core passed its local product, correctness, lifecycle, accessibility, and performance gates. Batch is therefore promoted from a gated objective to an active release requirement. This document also closes requirements gaps found during requester UAT concerning federal authorization preparation, warning size rules, local operation, harmless brand variation, and difficult images.

## 2. What is defined

| Area | Defined requirement |
|---|---|
| Batch population | 1 to 300 distilled-spirits application rows |
| Batch ingress | One UTF-8 `manifest.csv` and a selected folder of JPEG, PNG, or WebP panels |
| Processing | Sequential, concurrency one, through the same versioned single-verification API and supervised local OCR worker |
| Accounting | Every nonblank manifest row remains visible and exportable, including invalid rows, errors, and cancellations |
| Isolation | One invalid row, timeout, bad image, or service error does not abort later valid rows |
| User control | Progress, current case, elapsed time, rolling average, estimate, cancel, individual retry, retry remaining, filters, details, and export |
| Result vocabulary | No differences, Needs review, Differences, Bad image, Error, Cancelled, Queued, and Running |
| Export | Formula-safe summary CSV plus detailed JSON containing inputs, all 19 checks, reasons, evidence, timings, limitations, and errors |
| Capacity proof | Functional and timing gates at 10, 20, and 300 rows |
| Runtime inference | Hash-verified RapidOCR and ONNX Runtime on the local host, with no required runtime external inference call |
| Brand judgment | Case-only and punctuation-only differences, including `STONE'S THROW` versus `Stone's Throw`, route to Review |
| Warning text | Wording and punctuation are exact; heading capitalization is exact; presentation properties remain independent |
| Warning size | Minimum size and maximum characters per inch use the 237 mL and 3 L regulatory boundaries; an ordinary unscaled image is Not verified |
| Difficult images | EXIF orientation, bounded decode, quality signals, conservative deskew or perspective recovery, and contrast recovery are attempted; uncertainty never becomes clean |
| Federal preparation | Provide an authorization-start document set for deciding and initiating either an agency RMF/ATO path or a FedRAMP 20x cloud-service path |

## 3. What remains dependent on deployment or agency input

| Pending item | Needed decision or evidence | Owner at transition |
|---|---|---|
| Authorization path | Agency-owned application boundary or commercial cloud service offering | Agency system owner and provider leadership |
| Impact categorization | Final FIPS 199 confidentiality, integrity, and availability values | Agency authorizing officials |
| Azure boundary | Subscription, region, services, tenant, identity, networking, logging, backup, and inherited controls | Cloud architect and agency security |
| External access | Public, agency-only, VPN, private endpoint, or managed-device access | Agency system owner |
| Identity and roles | Production IdP, MFA, reviewer roles, administrators, and service identities | Agency IAM owner |
| Records and privacy | Production data types, PII determination, retention schedule, legal hold, and records disposition | Privacy and records officials |
| Independent assessment | Assessor, certification class, assessment scope, test plan, and evidence period | Provider and independent assessor |
| Operations | Incident response integration, vulnerability operations, recovery targets, monitoring, and change approvals | Production operations owner |
| Human usability | First-time low-technical-comfort participant evidence for single and batch journeys | UAT coordinator |

These are not reasons to omit the starter documents. They are fields the starter package must surface and route to named decision owners.

## 4. Derived batch requirements

| ID | Requirement | Acceptance |
|---|---|---|
| `BR-032` | Reject absolute paths, traversal, duplicate normalized paths, case-only path ambiguity, unsupported headers, and more than 300 rows. | Controlled hostile manifests are rejected before transport. |
| `BR-033` | Enforce unique case IDs and one-application ownership for every panel file. | Duplicate IDs and shared panels become visible intake errors. |
| `BR-034` | Preserve valid row progress when another row is invalid or fails. | Later valid rows complete and retain stable manifest ordering. |
| `BR-035` | Enforce the existing 1 to 6 panel, 4 MiB per file, 8 MiB aggregate, MIME, pixel, and request deadlines for each application. | Batch cannot bypass a single-request security limit. |
| `BR-036` | Cancel the active request, stop new starts, preserve completed results, and mark remaining rows Cancelled. | Cancellation reaches a terminal state and affected rows can be retried. |
| `BR-037` | Neutralize spreadsheet formula prefixes and export complete machine evidence. | CSV begins risky cells with an apostrophe and detailed JSON includes the complete result contract. |
| `BR-038` | Keep browser-held files, results, and reviewer work session-only. | No database, durable queue, service worker, or browser storage contains application content. |
| `BR-039` | Complete 10 rows in at most 60 seconds, 20 rows in at most 110 seconds, and 300 rows in at most 1,510 seconds under the declared warmed local profile. | Timed evidence reports completeness, throughput, peak memory, and zero false clean results. |
| `BR-040` | Provide a federal authorization-start package grounded in current official rules. | Package inventory maps every starter artifact to an owner and its next required input. |

## 5. BAIRD verdict

The corrected requirements are complete enough for the I2R batch architecture, FRD addendum, Build Instructions addendum, implementation, and Validation Protocol loop. No new database, account system, durable queue, server batch endpoint, cloud inference dependency, wine rules, beer rules, or COLA integration is required.
