# QA, QC, and User Acceptance

Document ID: LV-QA-001  
Status: QA and QC release gates passed; requester UAT follows release deployment

## Quality assurance controls

QA verifies the process used to build the product:

- requirements are testable and traced;
- contracts are versioned and integrity checked;
- local inference is isolated from reference comparison;
- fixtures and expected outcomes are independent of production logic;
- negative and ambiguity paths are first-class tests;
- deployment validates the exact commit and image digest;
- documentation and code are reviewed together.

## Quality control checks

QC verifies the produced artifact:

| Area | Required inspection |
| --- | --- |
| Single product | 1, 2, and 3 panels; remove and retry; no manual source fields |
| Beverage types | Malt beverage, wine, spirits, unknown, and conflicting signals |
| Evidence | Correct panel, original-pixel polygon, text snippet, and Show on label |
| Warning | Exact text, title-case heading, missing sentence, bold body, contrast, legibility, and unknown size |
| Human judgment | STONE'S THROW compared with Stone's Throw routes to Review when an independent reference is used |
| Imperfect image | Angle, low light, glare, blur, and partial coverage do not become automatic label defects |
| Batch | Auto-group, merge, split, confirm, progress, failure isolation, retry, cancel, and export |
| Capacity | Up to 300 products and 900 images with no group above 3 images |
| History | 500-record FIFO, originating-browser isolation, filters, detail, evidence, disposition, delete, and clear |
| Errors | Unsupported type, corrupt file, too many panels, too many pixels, timeout, rate, capacity, and service unavailable |
| Accessibility | Keyboard, focus, labels, headings, status text, target size, contrast, responsive reflow |
| Security | History isolation, bounded bodies, formula-safe CSV, rate fairness, safe errors, no content logs, cleanup, non-root runtime, pinned actions, OIDC, no secrets in source |

## QA and QC execution result

The release candidate passed the 225-test Python suite, strict typing, Python and frontend linting, nine frontend component and contract tests, the production frontend build, Chrome and Edge primary workflows, the Chrome privacy matrix, and the explicit 300-product browser capacity run. The 30-product governed corpus passed every expected check row and mutation control. The 50-image diagnostic contained every expected defect with no false clearance or false deterministic rejection. Warm, cold, and 20-product sequential timing gates passed. Security boundary tests, staged-source inspection, and production dependency audits found no unresolved release blocker. Detailed measurements and limitations are recorded in `../08-validation/VALIDATION_RESULTS.md`.

## UAT script

Run against the release URL in a new browser session.

1. Confirm the page identifies LabelVerify as an unofficial prototype and offers Check one product and Check a batch.
2. Select one to three readable malt beverage images. Confirm each preview, reorder two panels, remove and restore one panel, then start verification without typing label data. Confirm the inferred family and 24 check rows.
3. Repeat with wine and distilled spirits. Confirm the applicable family-specific row changes and non-applicable rows remain visible.
4. Select Show on label for brand, ABV, net contents, producer, and warning. Confirm each highlight appears on the correct image and text.
5. Open warning detail. Confirm prescribed text, observed text, each warning subcheck, and clear reasons.
6. Upload an imperfect but readable image. Confirm recoverable fields are evaluated and the angle or lighting alone is not marked a label defect.
7. Upload an incomplete or unreadable image. Confirm the result requests review or another image and does not invent a pass.
8. Record Approve, Reject, and Request more information on separate cases. Confirm machine findings remain unchanged.
9. Select a folder with product filenames or subfolders. Confirm suggested groups contain no more than three images. Rename one product, merge or split one group, and confirm all groups.
10. Run a batch. Confirm progress, remaining work, active time, average, ETA, isolated failures, retry, cancel, CSV, and JSON.
11. Open History. Filter records, open an image and evidence highlight, edit a disposition, delete a record, and verify newest-first order.
12. Navigate by keyboard at 1366 by 768 and at a narrow mobile width. Confirm focus remains visible and no required action depends on color.
13. Upload a fourth panel, unsupported file, and corrupt image. Confirm clear, safe next actions.

## UAT acceptance record

| Field | Entry |
| --- | --- |
| Release commit | To be bound at deployment |
| Public URL | `https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/` |
| Browser and version | Requester entry |
| Date | Requester entry |
| Result | Pending requester execution |
| Accepted by | Requester entry |
| Findings | Requester entry |

## Definition of acceptance

UAT passes when the requester can complete the core flows without developer assistance, results and uncertainty are understandable, each beverage family uses the correct selected rule profile, evidence can be verified on pixels, batch and history behave as specified, and no Severity 1 or Severity 2 defect remains open.

Severity 1 blocks use or creates a false clearance. Severity 2 breaks a required feature or loses evidence. Severity 3 degrades usability with a viable path. Severity 4 is cosmetic or editorial.
