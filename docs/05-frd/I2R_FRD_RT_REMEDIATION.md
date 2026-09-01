# I2R and FRD Red-Team Remediation

Document control ID: LV-FRD-003  
Revision: 1.4  
Date: 2026-09-01  
Status: Controlled through post-build validation change

| Finding | Resolution | Controlled artifacts |
|---|---|---|
| `RT1-I2R-F001` upload envelope and deadline infeasible | Reduced server payload to 4 MiB per file and 8 MiB aggregate, set exact 8,650,752 raw bytes, set 20 second body deadline, separated normal five-second profile from maximum accepted input, and required shaped-network/deployed tests | LV-I2R-001, LV-I2R-002, `FR-008`, `FR-031`, `T-008`, `T-031` |
| `RT1-I2R-F002` and `RT3-I2R-F004` public identity/edge controls undefined | Defined Fly-Client-IP trust, forwarding-header rejection, per-process HMAC digest, Host/Origin algorithms, response headers, no-store behavior, and direct/proxied test matrix | LV-I2R-002 Section 10, `FR-040`, `T-040` |
| `RT1-I2R-F003` regulatory recheck and browser persistence dropped | Added release source re-verification and browser storage/cache inspection across every terminal path | `FR-038`, `T-038`, `FR-039`, `T-039`, LV-I2R-005 |
| `RT1-I2R-F004` OCR comparative evidence outside seal | Added controlled candidate comparison and included raw Tesseract, RapidOCR, browser, BOM, and legacy technical report evidence in V2 | LV-I2R-008 and V2 snapshot |
| `RT2-I2R-F001` no binary first-time manual journey | Added two independent no-instruction sample and complete manual sessions with time and help/error criteria | `FR-037`, `T-037` |
| `RT2-I2R-F002` warning registry combined/omitted checks | Added authoritative 19-check registry with separate contrast, legibility, and physical-size rows and updated warning FRs | `selected-check-registry-v1.json`, `FR-019`, `FR-020` |
| `RT3-I2R-F001` evidence references unresolved | Defined evidence identity, panel binding, original-coordinate polygon, transforms, ambiguity ownership, schema failures, and browser behavior | LV-I2R-006, `FR-023`, `FR-024` |
| `RT3-I2R-F002` total timeout/cancel contract missing | Added composed server and browser deadlines, client cancellation, disconnect ownership, response/abort race, phase-stall tests, and dedicated feature | LV-I2R-002 Section 8, `FR-041`, `T-041` |
| `RT3-I2R-F003` raw request ceiling omitted | Added exact 8,650,752 complete-request ceiling and Content-Length/streaming rules | LV-I2R-002 Sections 1 and 6, `FR-008`, `T-008` |
| `RT3-I2R-F005` normative errors missing | Added fixed server/browser code, HTTP, retryability, locator, next-action, log, and fallback registry | LV-I2R-007, `FR-025`, `T-025` |

## Remediation result

- V1 material findings: 11 unique findings after overlap consolidation
- Findings remediated in controlled documents: 11
- New feature requirements: `FR-037` through `FR-041`
- Current active feature requirements and tests: 41 and 41
- Architecture selections reopened: 0
- Requirements scope expanded: 0
- BI authorized before V2 unanimous CLEAR: No

## V2 review remediation

| Finding | Resolution | Controlled artifacts |
|---|---|---|
| Conflicting 3/20 second body deadlines | Removed the stale 3 second threat-table value. All active contracts now use 20 seconds. | LV-I2R-002, `FR-008`, `FR-031`, `FR-041` |
| Decode timeout not killable | Moved full decode, pixel enforcement, preprocessing, OCR, candidates, comparison, and aggregation into the supervised child job under the 6.25 second killable deadline. | LV-I2R-001, LV-I2R-002, `FR-009`, `FR-029`, `FR-041` |
| OCR comparison not reproducible | Removed historical Tesseract field/timing claims from the decision basis, classified those runs as exploratory, qualified RapidOCR on its controlled positive full-contract evidence, and explicitly superseded stale report metrics. | LV-I2R-008 |
| Retry/cancel preservation and destructive reset confirmation | Made form/file preservation binary for retry and cancel and made Start over confirmation/cancel/confirm behavior binary. | LV-I2R-003, `FR-025`, `FR-027`, `FR-041` |
| FRD authority excluded required contracts | Expanded the FRD authority line through LV-I2R-008 and the 19-check registry. | LV-FRD-001 |

V2 findings remediated: 5 of 5. BI remains unauthorized until three reviewers return CLEAR on the next sealed revision.

## V3 review remediation

| Finding | Resolution | Controlled artifacts |
|---|---|---|
| Controlled model BOM retained a superseded Tesseract field-coverage rationale | Replaced the stale rejection statement in the model BOM and legacy feasibility report with the governing qualification result. Historical Tesseract runs prove exploration only. They do not provide a reproducible full result-contract proof, and no historical field-miss or timing claim controls selection. | LV-I2R-008, `MODEL_BOM.md`, `BAIRD_FEASIBILITY_REPORT.md` |

V3 findings remediated: 1 of 1. BI remains unauthorized until all three reviewers return CLEAR on the V4 sealed revision.

## V4 review remediation

| Finding | Resolution | Controlled artifacts |
|---|---|---|
| Retained research report mixed historical Tesseract observations, 3.0 second upload timing, and 17-check aggregation with current direction | Marked the report as historical I2R evidence, made current I2R and FRD authority explicit, replaced non-reproducible candidate claims with qualification status, and distinguished the historical harness from the current 20/30/35-second deadlines and 19-check product registry. | LV-I2R-001, LV-I2R-002, LV-I2R-008, `selected-check-registry-v1.json`, `BAIRD_FEASIBILITY_REPORT.md` |

V4 findings remediated: 1 of 1. BI remains unauthorized until all three reviewers return CLEAR on the V5 sealed revision.

## Post-build validation change control

| Finding | Decision | Rationale | Controlled artifacts |
|---|---|---|---|
| `QA-T041-001` treated every named browser operation as an independent asynchronous stall point | Refined the matrix without reducing the 20/30/35-second deadlines, cancellation behavior, ownership rules, recovery, or cleanup outcomes | Client validation, React result rendering, focus placement, and live-region DOM output execute synchronously in the browser commit path. Adding dormant test-only phase adapters would increase production complexity without controlling a real wait boundary. The governed test now stalls every actual asynchronous wait boundary and separately proves immediate client rejection plus one complete render, focus, and live-region commit. | LV-I2R-002 Revision 1.1, LV-FRD-001 Revision 1.1, LV-FRD-002 Revision 1.1, `T-041` phase evidence |

This is a verification correction under BI change control. It does not add or remove a user feature and does not change any original assignment outcome. The final three RT reviewers must assess the refinement against the same release manifest.
