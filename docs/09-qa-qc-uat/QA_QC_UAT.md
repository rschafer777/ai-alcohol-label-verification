# QA, QC, and User Acceptance

Document ID: LV-QA-001  
Status: QA and QC, protected Azure deployment, and engineering browser pre-UAT gates passed; requester UAT pending

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
| Warning | Exact text, title-case heading, missing sentence, bold body, contrast, legibility, unknown size, best complete read across panels, and conservative word confirmation across partial panel reads |
| Human judgment | STONE'S THROW compared with Stone's Throw routes to Review when an independent reference is used |
| Imperfect image | Angle, low light, glare, blur, and partial coverage do not become automatic label defects |
| Equivalent panels | Cross-format duplicate uploads preserve both panel records, identify the canonical panel, avoid repeat OCR, and do not restart the worker |
| Batch | Auto-group, merge, split, confirm, progress, failure isolation, retry, cancel, and export |
| Capacity | Up to 300 products and 900 images with no group above 3 images |
| History | 500-record FIFO, originating-browser isolation, filters, detail, evidence, disposition, delete, and clear |
| Errors | Unsupported type, corrupt file, too many panels, browser preparation of supported oversized photos, authoritative server pixel and byte limits, timeout, rate, capacity, and service unavailable |
| Accessibility | Keyboard, focus, labels, headings, status text, target size, contrast, responsive reflow |
| Security | History isolation, bounded bodies, formula-safe CSV, rate fairness, safe errors, no content logs, cleanup, non-root runtime, pinned actions, OIDC, no secrets in source |

## QA and QC execution result

The release candidate passed 372 Python tests, strict typing, Python and frontend linting, 35 frontend component and contract tests, the production frontend build, browser workflows, privacy checks, and the explicit 300-product browser capacity run. The 30-product governed corpus passed every expected check row and mutation control. The private current-image corpus completed 221 of 221 individual API analyses and 152 of 152 server-suggested grouped-product analyses, with no group above three images. Its 3.997-second individual mean and 7.874-second maximum passed the declared targets. Against the pixel ground truth and the disposition oracle, the candidate reports 0 false rejects and 1 disputed false clean over 42 oracle images (see the Validation Results accuracy section). The source-bound integration record shows a cross-format two-panel request completed in 6.086 seconds, retained both panels, recorded the duplicate linkage, and kept worker generation at 1 with zero restarts. Security boundary tests, staged-source inspection, production dependency audits, and security scan `b8501684-ed2e-4d83-8fe9-5775bc5f81d7` found no unresolved release blocker. That scan completed all 34 changed surfaces in its fixed integration range with no deferred surface and no plausible finding. Detailed measurements, oracle coverage, and limitations are recorded in `../08-validation/VALIDATION_RESULTS.md`.

The Azure deployment workflow verifies the exact build, effective 4 vCPU and 8 GiB configuration, health, metadata, public analysis, and latency gates. The 221 of 221 count is a technical processing result. The current folder has field-level ground truth for 70 images, not an agency-approved oracle for every current image, so final legal-label acceptance remains part of requester UAT. Public technical evidence retains case identifiers, content hashes, field-read flags, outcomes, counts, and timing without publishing private filenames or raw OCR text.

A corrective candidate followed on 2026-09-04 after the operator photographed bottles in a store and normalized 145 photographs into the private folder (221 images in all). Four adversarial review rounds, each measured on a frozen copy against the committed candidate, found and drove the correction of extraction and warning-rule defects that had turned compliant labels into differences or hidden real ones; the store photographs themselves exposed three false rejects (garbled warning reads, a read cut inside the first clause, and medium-gray print rejected on contrast), a crash on a zero net-contents read, and dense back labels that overran the hard-case time bound until the second OCR read was placed under a time budget. The gates in this record were rerun on the corrected code and the numbers above are from those runs; `../10-release/FINAL_RT_SIGNOFF.md` carries the corrective-candidate gate table.

Commit-bound engineering browser pre-UAT passed and is recorded in `../08-validation/evidence/live-browser-uat.json`. The requester acceptance record below remains intentionally unsigned.

## UAT script

Run against the release URL in a new browser session.

1. Confirm the page identifies LabelVerify as an unofficial prototype and offers Check one product and Check a batch.
2. Select one to three readable malt beverage images. Confirm each preview, reorder two panels, remove and restore one panel, then start verification without typing label data. Confirm the inferred family and 24 check rows.
3. Repeat with wine and distilled spirits. Confirm the applicable family-specific row changes and non-applicable rows remain visible.
4. Select Show on label for brand, ABV, net contents, producer, and warning. Confirm each highlight appears on the correct image and text. Scroll the mouse wheel over the image to zoom, drag the enlarged image to move around it, and use the View as switch at the head of the checks to change between Table, Cards, and Image first.
5. Open warning detail. Confirm prescribed text, observed text, each warning subcheck, and clear reasons.
6. Upload an imperfect but readable image. Confirm recoverable fields are evaluated and the angle or lighting alone is not marked a label defect. Upload a phone photograph above 12 megapixels and confirm it is accepted without manual resizing. Submit two photographs of the same back label taken at different angles and confirm the warning result names the best-read image or reports the words confirmed across images.
7. Upload an incomplete or unreadable image. Confirm the result requests review or another image and does not invent a pass.
8. Record Approve, Reject, and Request more information on separate cases. Confirm machine findings remain unchanged.
9. Select a folder with product filenames or subfolders. Confirm suggested groups contain no more than three images. Rename one product, merge or split one group, and confirm all groups. Confirm that the step states how many products are confirmed, that Show the N that still need confirmation hides the confirmed cards, that Confirm the remaining N as suggested confirms them, and that Run reports why it is locked until then.
10. Include one JSON or other unsupported file in that folder. Confirm the UI reports it as skipped, shows the accepted image count, and continues without stopping the batch.
11. Run a batch. Confirm the live processed/total counter, progress bar, current item, rate, average, ETA, remaining work, isolated failures, retry, cancel, CSV, and JSON.
12. Open History. Filter records, open an image and evidence highlight, edit a disposition, delete a record, and verify newest-first order.
13. Navigate by keyboard at 1366 by 768 and at a narrow mobile width. Confirm focus remains visible and no required action depends on color.
14. Upload a fourth panel, unsupported file, and corrupt image. Confirm clear, safe next actions.
15. Upload a supported browser-decodable image above the decoded-pixel limit. Confirm it is proportionally prepared and uploaded without external editing. Exercise the API directly or use an undecodable input to confirm the authoritative server error still shows expected width, actual width, expected height, actual height, expected decoded pixels, actual decoded pixels, the offending rows in red, and an exact resize action.
16. Exercise the Jack Daniel's, Organic Vodka, Cascade Light, Peak Farm, and Blood & Honey files. Confirm the extracted values listed in `../08-validation/VALIDATION_RESULTS.md` and inspect each evidence highlight.
17. Upload the same label panel as JPEG and PNG in one product. Confirm both uploads remain visible, the duplicate panel identifies the canonical panel, the result completes within 9 seconds, and readiness still reports the same worker generation.
18. Submit two views of one product where glare or curvature hides different warning lines. Confirm an exact complete panel read governs when available; otherwise confirm complementary statutory words remain Review with punctuation explicitly left to the reviewer.

## UAT acceptance record

| Field | Entry |
| --- | --- |
| Release commit | `4a31e1a95cf6b2ec8dac5c8bc8f5763ffa7f3961` |
| Public URL | `https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/` |
| Browser and version | Requester entry |
| Date | Requester entry |
| Result | Engineering entry gates passed; requester execution pending |
| Accepted by | Requester entry |
| Findings | Requester entry |

The engineering browser pre-UAT passed after final deployment. It is not a substitute for requester acceptance.

## Definition of acceptance

UAT passes when the requester can complete the core flows without developer assistance, results and uncertainty are understandable, each beverage family uses the correct selected rule profile, evidence can be verified on pixels, batch and history behave as specified, and no Severity 1 or Severity 2 defect remains open.

Severity 1 blocks use or creates a false clearance. Severity 2 breaks a required feature or loses evidence. Severity 3 degrades usability with a viable path. Severity 4 is cosmetic or editorial.
