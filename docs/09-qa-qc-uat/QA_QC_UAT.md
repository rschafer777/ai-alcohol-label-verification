# QA, QC, and User Acceptance

Document ID: LV-QA-001  
Status: CR-002 QA, QC, protected deployment, and engineering pre-UAT passed; requester UAT ready

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-03 | Recorded initial candidate QA, QC, deployment, and UAT entry evidence | Initial release candidate |
| 1.1 | 2026-09-04 | Preserved the initial results as baseline evidence and added CR-002 corrective gates | CR-002 |
| 1.2 | 2026-09-04 | Recorded corrective source-gate results, holdout evidence, model decision, and remaining deployment and requester-UAT gates | CR-002 |
| 1.3 | 2026-09-04 | Added final-review mutation, provenance, replay, telemetry, rollback, and staged-source integrity checks | CR-002 |
| 1.4 | 2026-09-05 | Added all-field merge provenance, family-authority, resolved-to-unresolved, and polygon-boundary regression evidence | CR-002 |
| 1.5 | 2026-09-05 | Added resolved and unresolved add-panel response-to-history provenance reconciliation | CR-002 |
| 1.6 | 2026-09-05 | Recorded the final complete release gate and independent security review | CR-002 |
| 1.7 | 2026-09-05 | Recorded exact-candidate commit, protected Azure deployment, public verification, and engineering browser pre-UAT | CR-002 |

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
| Review attribution | Every Review lists all blocking check IDs and normalized causes; routing volume is never presented as accuracy |
| Observation correction | Allowlisted evidence-linked corrections preserve verbatim visible statements and server-derived parsed forms plus self-contained original OCR, pixels, and evidence; atomically create cumulative revisions under one lineage shared with add-panel writes; reset the child disposition to Pending; invoke image processing and OCR zero times; recompute every declared dependency including proof placement and distinction; remain distinct from trusted application values; and cannot normalize away a printed defect or clear warning or other visual findings by typed text |
| Neutral images | Result, history, evidence, sample, and export use Image 1 to Image 3 unless a role is explicitly confirmed; reversed order does not change rule outcomes |
| Numeric brands | Independent numeric brands are found and ABV, proof, quantity, vintage, age, postal, barcode, lot, reference, price, and deposit values are not selected as brands |
| Producer block | Role, organization, and address remain evidence-linked; wrapped lines join correctly and adjacent marketing text stays excluded |
| Model governance | Recognition candidates are compared on identical inputs; any promoted model meets accuracy, safety, integrity, offline, resource, and licensing gates |
| Demo deployed performance | Exact-build workflow checks and distinct difficult malt, wine, and spirits smoke inputs run on the effective 4-vCPU and 8-GiB Azure revision; production-scale distinct-product Azure load remains a pre-production operational qualification |

## QA and QC execution result

The initial release candidate passed 372 Python tests, strict typing, Python and frontend linting, 35 frontend component and contract tests, the production frontend build, browser workflows, privacy checks, and the explicit 300-product browser capacity run. The 30-product governed corpus passed every expected check row and mutation control. The private current-image corpus completed 221 of 221 individual API analyses and 152 of 152 server-suggested grouped-product analyses, with no group above three images. Its 3.997-second individual mean and 7.874-second maximum passed the local declared targets. Against the pixel ground truth and the disposition oracle, that candidate reported 0 false rejects and 1 disputed false clean over 42 oracle images. These results are retained as the CR-002 baseline and are not corrective-release exit evidence. In particular, 214 of 221 individual results routed to Review, 27 of 30 oracle expected-Pass cases routed to Review, representative timing came from the development workstation, and the Azure timing used repeated governed samples. Detailed baseline measurements and limitations are recorded in `../08-validation/VALIDATION_RESULTS.md`.

The Azure deployment workflow verifies the exact build, effective 4 vCPU and 8 GiB configuration, health, metadata, public analysis, and latency gates. Post-deployment distinct malt, wine, and spirits smoke checks selected the correct family, returned 24 checks, preserved safe partial reads where the recognizer did not capture the entire visible mark, and remained below the 9-second hard-image ceiling. Their 6.734-second mean is a limited difficult-image smoke, not representative deployed-performance evidence and not a substitute for the 221-image workload mean. The local gates cover 221 admitted images, 155 grouped products, the 20-product timing path, and the 300-product browser-capacity path. A separate production-scale distinct-product Azure load campaign is not claimed as complete and is not required to begin requester demo UAT. The 221 of 221 count is a technical processing result. The current folder has field-level ground truth for 70 images, not an agency-approved oracle for every current image, so final legal-label acceptance remains part of requester UAT. Public technical evidence retains case identifiers, image basenames needed to join the local oracle, content hashes, field-read flags, outcomes, counts, and timing. It excludes raw image bytes, machine-specific paths, and raw OCR text.

The CR-002 corrective candidate passed the complete release gate with 411 Python and validation tests, strict typing, Python and frontend lint, 38 frontend tests, the 134-module production build, applicable browser and accessibility workflows, Python and production npm dependency audits, and the 375-entry release-manifest validation. After final requirements review exposed ambiguous BAIRD numbering, the corrected requirement and its new regression passed the focused test and the full source gate with 412 Python and validation tests; runtime code was unchanged. The production path processed 221 of 221 individual images and 155 of 155 suggested product groups, with no group above three images, a 3.840-second individual mean, a 7.237-second individual maximum, a 0.935-second grouped mean, and a 5.764-second grouped maximum. The 70-image pixel-ground-truth run preserved exact results for all 65 applicable ABV, 28 proof, and 64 net-contents fields; producer exact results increased from 31 to 35. Six directly conflicting oracle rows are reported and excluded from confusion counts. The 36 remaining oracle cases have zero false clean and zero false reject. The sealed 24-product holdout records 137 exact results across 195 eligible fields, zero false clean against annotated deterministic defects, a 4.628-second mean, a 5.868-second p95, a 7.831-second maximum, and an accepted `LV-VAR-002` utility variance. All-field merge provenance, response-to-history source reconciliation, family-authority precedence, resolved-to-unresolved, and polygon-boundary regressions pass. The final independent security diff review completed all 46 changed executable and contract surfaces with no reportable or deferred finding. PP-OCRv5 English and Latin candidates each regressed protected evidence, so PP-OCRv4 remains the single runtime recognizer.

CR-001 stabilization followed on 2026-09-04 after the operator photographed bottles in a store and normalized 145 photographs into the private folder (221 images in all). Four adversarial review rounds, each measured on a frozen copy against the committed candidate, found and drove the correction of extraction and warning-rule defects that had turned compliant labels into differences or hidden real ones; the store photographs themselves exposed three false rejects (garbled warning reads, a read cut inside the first clause, and medium-gray print rejected on contrast), a crash on a zero net-contents read, and dense back labels that overran the hard-case time bound until the second OCR read was placed under a time budget. The gates in this record were rerun on the stabilized CR-001 code and the numbers above are from those runs; `../10-release/FINAL_RT_SIGNOFF.md` carries the historical gate table. These results form the measured baseline for CR-002 and are not CR-002 exit evidence.

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
19. Correct brand, class, producer, ABV, proof, net contents, and a visibly printed Contains Sulfites statement using verbatim text in cited regions. When OCR has no region, select the image and draw a four-point source region before saving. Confirm a class correction reruns beverage-family inference and requires explicit cited type confirmation if the corrected class remains ambiguous. Confirm typed sulfite absence such as `none` or `not present` is rejected. For an ABV-only correction, confirm the server reruns the proof-to-ABV relation, same-field-of-vision placement, and visual distinction or adjacency against the corrected ABV polygon. Confirm normalized forms are derived while printed transcriptions, abbreviations, precision, ranges, units, and proof wording remain, and every other FR-053 dependency updates. Confirm every revision independently reopens with original OCR, pixels, and evidence; each atomic child starts Pending; earlier disposition stays on its parent; reviewer-corrected Matches are identified; and no image-processing stage runs. Race one correction against add-panel and confirm only one advances the head. Confirm revision 11 and panel 4 fail actionably, and deleting any revision removes the full lineage.
20. Enter an independently supplied application value separately from an observation correction. Confirm the interface and history identify their distinct provenance and that the correct dependent checks run.
21. Submit oversized and wrong-Origin correction bodies to a syntactically invalid history ID and confirm the same `413` and `403` mutation controls apply before resource lookup. Correct fields in a mixed application-and-label result and confirm only trusted fields are labelled as application values.
22. Add a panel to an unresolved record and confirm it remains unresolved unless the new label evidence resolves the type. Add a panel to a label-derived record whose new image improves a field and confirm the comparison baseline refreshes from the complete new label read without creating a false mismatch, while trusted application and reviewer-corrected fields remain unchanged. Confirm the child reports timings, limitations, and model identity from the fresh OCR run. Correct the same field twice from different panels, add another panel, and confirm replay uses the latest value with that latest event's image hash, panel, polygon, and original snippet.
23. Inject a failure after lineage metadata deletion but before commit and confirm both metadata and images survive rollback. Restart with a committed orphan and confirm reconciliation removes only unreferenced blobs.
24. Stage the candidate with Git line-ending normalization and confirm every tracked source hash in public evidence equals the staged LF bytes before generating the release manifest.
25. Upload the same two images in opposite orders. Confirm the interface uses neutral image ordinals and produces equivalent checks and evidence bindings.
26. Exercise independently annotated numeric-brand positives plus volume, proof, vintage, barcode, lot, price, and deposit negatives. Confirm only supported numeric marks become brand candidates and ambiguous competitors remain Review.
27. Confirm an exact warning can receive machine Match for supported checks without recording Approve, while uncertain punctuation, damaged text, conflicting panels, typography, and physical size remain Review or Not verified.
28. Review the blocking-cause list for several Review results and confirm every cause links to the responsible check and evidence where available.
29. Add a panel whose fresh label evidence conflicts with a formerly resolved label-derived beverage family. Confirm the child becomes type-unresolved instead of retaining stale certainty. Then correct the family explicitly and correct class/type in a later revision; confirm the reviewer-selected family remains authoritative. Inspect resolved and unresolved mixed-source add-panel results and confirm every field, including malt alcohol-source applicability, retains explicit provenance, its value agrees with that source, and the returned draft agrees with the reference reopened from history.
30. In the browser, drag correction rectangles toward and beyond the right or bottom display boundary. Confirm the client clamps each positive-area rectangle to a furthest original-pixel vertex one pixel inside the image boundary, accepts it, and reopens it on the same source pixels. Separately submit direct API correction requests whose polygon touches the right or bottom original-pixel boundary, and one with zero area; confirm each is rejected with an actionable field error.

## UAT acceptance record

| Field | Entry |
| --- | --- |
| CR-002 release commit | `0e9e79f37b074ba2f432ec7f6cf3e99495a4f007` |
| CR-002 public deployment | PASS; run `33942995735`, attempt 1, exact build and immutable digest verified |
| Browser and version | Requester entry |
| Date | Requester entry |
| Result | CR-002 engineering gates passed; requester UAT ready |
| Accepted by | Requester entry |
| Findings | Requester entry |

The engineering browser pre-UAT passed after final deployment. It is not a substitute for requester acceptance.

## Definition of acceptance

UAT passes when the requester can complete the core flows without developer assistance, results and uncertainty are understandable, each beverage family uses the correct selected rule profile, evidence can be verified on pixels, batch and history behave as specified, and no Severity 1 or Severity 2 defect remains open.

Severity 1 blocks use or creates a false clearance. Severity 2 breaks a required feature or loses evidence. Severity 3 degrades usability with a viable path. Severity 4 is cosmetic or editorial.
