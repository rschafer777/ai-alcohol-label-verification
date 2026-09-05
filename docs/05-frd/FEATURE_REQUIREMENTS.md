# Feature Requirements Document

Document ID: LV-FRD-001  
Inputs: LV-INTAKE-001, LV-BAIRD-001, LV-I2R-001  
Status: Approved CR-002 feature baseline; implemented and under release validation

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-01 | Initial integrated feature baseline | LV-INTAKE-001 revision 1.0 |
| 1.1 | 2026-09-04 | Added CR-002 corrective features and measurable promotion gates | CR-002 |
| 1.2 | 2026-09-04 | Traced implemented corrective features and the evidence-backed model and utility decisions | CR-002 |
| 1.3 | 2026-09-04 | Clarified final-review integrity acceptance for revisions, persistence, mutation controls, and release evidence | CR-002 |
| 1.4 | 2026-09-05 | Reconciled unique BAIRD derived-requirement identifiers through the corrective feature baseline | CR-002 final requirements review |

## Feature requirements

| ID | Feature and acceptance criteria | Source |
| --- | --- | --- |
| FR-001 | Home presents Check one product and Check a batch as the two primary actions | INT-001 |
| FR-002 | Single intake accepts 1 to 3 JPEG, PNG, or WebP images with preview, reorder, remove, and clear validation; supported browser images above the server pixel or byte limit are proportionally resized and re-encoded before upload | INT-002 |
| FR-003 | Verify starts OCR without requiring typed label or application fields | INT-003 |
| FR-004 | OCR executes with local ONNX assets and no runtime external inference request | INT-Q-003 |
| FR-005 | Decode honors orientation and creates only bounded recovery views | INT-009 |
| FR-006 | Candidate extraction returns field values, alternatives, panel, transform, and original-pixel polygon | INT-005, INT-010 |
| FR-007 | Type inference returns malt beverage, wine, distilled spirits, or unresolved with a reason | INT-004 |
| FR-008 | Whole-term matching prevents incidental substring classification | BAIRD-5 |
| FR-009 | Every result returns the ordered 24-check registry | INT-006 |
| FR-010 | Common checks cover beverage type, brand, class/type, ABV, proof, net contents, producer/address, country, warning, coverage, and quality | INT-005, INT-006 |
| FR-011 | Malt rules cover recognized designation, `IPA` limitation, customary net contents, formula/state ABV dependency, prohibited `ABV` abbreviation, prohibited ranges, and one-place or two-place precision at the 0.5 percent boundary | INT-006 |
| FR-012 | Wine rules cover numeric ABV, permitted range span and 14 percent boundary, table/light wine exception, conditional appellation, and conditional sulfite declaration | INT-006 |
| FR-013 | Spirits rules require ABV and evaluate brand, class/type, and ABV field of vision; optional proof is compared with twice ABV and its visual distinction remains reviewable | INT-006 |
| FR-014 | Warning applicability is based on known ABV at the 0.5 percent boundary; unknown ABV remains Review | INT-007 |
| FR-015 | Warning text comparison reads every panel carrying the statement, selects the clearest complete read, and may confirm statutory words in expected positions across complementary partial reads while retaining Review for punctuation; it normalizes whitespace, line wrapping, letter case, and OCR-glued clause markers for the statutory words; the separate heading-capitalization check enforces `GOVERNMENT WARNING:` in capitals, and any other punctuation difference remains Review | INT-007 |
| FR-016 | Warning presentation reports capitalization, heading emphasis, body weight, separation, continuity, contrast, legibility, and size capability independently using the closed measurement boundaries in LV-I2R-001; intermediate evidence routes to Review | INT-007 |
| FR-017 | Missing or unreadable evidence never becomes a deterministic label failure by itself | INT-Q-005 |
| FR-018 | Case-only or punctuation-only brand variations route to Review | INT-008 |
| FR-019 | Review workspace shows rule expectation, extracted value, state, reason, and evidence action | INT-010 |
| FR-020 | Show on label highlights the correct original-pixel polygon on the correct panel | INT-010 |
| FR-021 | User can zoom, rotate, enhance, and switch among up to three panels without changing evidence coordinates; the mouse wheel zooms about the point under the cursor, the enlarged image pans by dragging or arrow keys, the zoom readout resets the view, and the Table, Cards, and Image first switcher sits at the head of the checks with icons and tooltips | INT-009, INT-010 |
| FR-022 | Warning detail shows prescribed and observed text plus all warning subchecks | INT-007 |
| FR-023 | Reviewer can record Approve, Reject, or Request more information and an optional note | INT-011 |
| FR-024 | Keyboard shortcuts operate reviewer disposition without trapping focus | INT-Q-004 |
| FR-025 | Batch accepts up to 900 supported images, skips unsupported selected files individually, and reports accepted and skipped counts and reasons | INT-012 |
| FR-026 | Grouping uses directory, filename, OCR brand, class/type, and beverage-family cues and never silently places more than three images in a product | INT-012 |
| FR-027 | User can inspect, merge, split, name, and confirm groups before processing; the step states how many products are confirmed and how many still need a decision, filters the wall to those cards, confirms the remaining suggestions in one step while leaving conflicts to the reviewer, states beside the run button why it is locked, explains each grouping tool with a tooltip, and, when a large run reaches the API's per-minute start limit, waits and tries the same product again rather than failing it | INT-012 |
| FR-028 | Batch reuses the analysis endpoint sequentially with failure isolation | INT-012 |
| FR-029 | Batch begins at 0 of N and reports products, images, processed, remaining, running, queued, review, differences, failures, active time, rate, mean, ETA, and attempts | INT-013 |
| FR-030 | User can cancel remaining work and retry failed groups | INT-013 |
| FR-031 | Batch exports formula-safe CSV and detailed JSON | INT-014 |
| FR-032 | Every successful analysis or reference verification creates one root history lineage with retained images; corrections and add-panel reprocessing create revisions inside that product result rather than separate visible history entries | INT-015 |
| FR-033 | History supports newest-first paging and filters for query, beverage, summary, and disposition | INT-015 |
| FR-034 | History detail reopens the current head and every retained revision with self-contained checks, images, and evidence location | INT-016 |
| FR-035 | Disposition updates do not alter immutable machine findings | INT-011, INT-015 |
| FR-036 | Deleting any revision ID removes its complete lineage; metadata deletion commits before unreferenced image blobs are unlinked, interrupted cleanup is reconciled at startup, and Clear all removes all lineages in the browser scope and requires confirmation | INT-015, INT-Q-006 |
| FR-037 | History retains no more than 500 product lineages and 10 revisions per lineage; product 501 evicts the oldest complete lineage, revision 11 is rejected with an actionable error, and a revision does not reset root FIFO age | INT-015 |
| FR-038 | Built-in sample completes the primary workflow without a network dependency | INT-017 |
| FR-039 | UI is semantic, keyboard reachable, visibly focused, non-color dependent, and usable at 1366 by 768 | INT-Q-004 |
| FR-040 | Public errors are bounded, content-safe, actionable, and include retry behavior; measurable limit errors show supported, submitted, pass or fail, and exact correction values | INT-002, INT-Q-006 |
| FR-041 | Upload, pixel, timeout, rate, capacity, cleanup, and non-root controls match the versioned contracts; the 15-second worker safety limit remains distinct from the 5-second typical and 9-second difficult-image quality targets | INT-Q-001, INT-Q-006 |
| FR-042 | Normal readable labels target about 5 seconds and difficult recoverable labels target no more than 9 seconds | INT-Q-001 |
| FR-043 | Warm sequential batches target about 5 seconds mean per product | INT-Q-002 |
| FR-044 | Metadata exposes build, contract, profile, check count, rules, request limits, runtime, 500-lineage history capacity, 10-revision lineage capacity, and FIFO policy | INT-Q-007, INT-015 |
| FR-045 | Independent-reference verification remains available for a future trusted COLA adapter and does not influence OCR candidate discovery | BAIRD unknown 1 |
| FR-046 | History reads and mutations require the originating opaque browser scope; state-change Origin, body-size, and rate controls apply before accepting any history identifier; errors are content-safe; cross-scope records return Not Found; and the bearer scope is never returned, displayed, exported, or logged as identity or evidence | INT-Q-006, BAIRD-41 |
| FR-047 | The OCR worker may reuse a bounded result only for byte-identical decoded view pixels and dimensions; filenames, product names, expected fields, and oracle data never form a cache key or extraction override | INT-Q-001, INT-Q-002 |
| FR-048 | Equivalent full-frame panels may share canonical OCR work only when strict aspect, visual-correlation, and normalized-error gates all pass; every upload remains in the result, duplicates identify the canonical panel, and distinct product surfaces are never collapsed | INT-002, INT-Q-002, BAIRD-15 |
| FR-049 | The governed Azure template allocates 4 vCPU and 8 GiB to the Consumption replica, and deployment readback blocks any resource configuration drift before smoke testing | INT-Q-008, BAIRD-16 |
| FR-050 | A machine Match states only that visible evidence satisfied the implemented check; it never creates or implies a reviewer approval, and the human disposition remains separately editable | INT-018, BAIRD-30 |
| FR-051 | Provenance is attached to each observed and reference field, not the result as a whole; contracts distinguish `label_ocr`, `reviewer_corrected`, `trusted_application`, `manifest`, and `sample`, and checks, displays, persistence, history, CSV, and JSON preserve mixed-source results truthfully even when one result contains several sources | INT-019, BAIRD-23 |
| FR-052 | `POST /api/v1/history/{id}/corrections` accepts expected revision, bounded reason and actor label, and 1 to 10 field-specific corrections from the I2R allowlist; statement-sensitive fields require verbatim `visibleText` bound to source image SHA-256, panel, and polygon while retaining the original snippet; when OCR supplies no region, the reviewer must draw a bounded original-pixel region; the server derives and stores normalized values, ranges, precision, abbreviations, units, sulfite wording, and producer components alongside the raw value; typed sulfite text may establish presence only from a visible Contains Sulfites statement and may never establish absence; client-supplied normalized substitutes are rejected; exact same-origin and browser scope are enforced; warning and visual findings are prohibited; and image processing and OCR are invoked zero times | INT-020, INT-Q-006, BAIRD-21 to BAIRD-22, BAIRD-31, BAIRD-36, BAIRD-40 |
| FR-053 | A successful correction atomically advances one root lineage from its authoritative current head under unique root-and-revision constraints, preserves self-contained parents, starts the child disposition at Pending, and applies these dependencies: beverage type is selected from the closed malt-beverage, wine, or distilled-spirits set and reruns all applicability and family rows; class reruns inference, warning applicability, and class-triggered rows, and fails safely when the corrected class cannot resolve one family without a cited type correction; ABV reruns proof-to-ABV relation, proof same-field-of-vision placement, proof visual distinction or adjacency relative to the corrected ABV evidence, warning applicability, family ranges, and spirits field of vision; proof reruns observed value and wording, twice-ABV relation, same-field-of-vision placement, and visual distinction or adjacency; brand reruns spirits field of vision; net contents reruns warning physical-size threshold; producer reruns importer and country applicability; country reruns import applicability; appellation and sulfite rerun their wine rows; every change reruns aggregation | INT-020, INT-Q-006, BAIRD-21 to BAIRD-23, BAIRD-32, BAIRD-39 |
| FR-054 | Every overall Review includes blocking check IDs and normalized review-cause categories; reporting separates processing, routing, field, and disposition accuracy; and the sealed holdout gains `min(4, recoverable baseline error count)` correct producer-block or warning-wording product-fields, including one in each family with a recoverable baseline error, with zero lost correct fields, zero new false clean, and no protected-field regression | INT-021, INT-Q-009, BAIRD-19 to BAIRD-20, BAIRD-33 |
| FR-055 | Result, evidence, history, and export views use Image 1, Image 2, and Image 3 unless a reviewer explicitly confirms a semantic role; reversing input order produces equivalent checks and evidence bindings, and upload order or a display role never changes extraction ranking or rule applicability | INT-022, BAIRD-24 |
| FR-056 | Numeric-only and digit-led brand candidates use position-independent relative text geometry, isolation, trademark proximity, cross-panel repetition, and proximity to independently detected core fields, with exclusions for ABV, proof, quantity, vintage, age, postal, barcode, lot, reference, price, and deposit contexts; unresolved competitors remain Review and runtime contains no product-specific or upload-order exception | INT-023, BAIRD-25 |
| FR-057 | Producer extraction returns evidence-linked role, organization, and address components, excludes adjacent unrelated copy, distinguishes producer, bottler, brewer, vintner, distiller, and importer roles, and never represents partial label text as a complete trusted application match | INT-024, BAIRD-26 |
| FR-058 | Exact supported warning words and punctuation may make `warning_wording` Match; capitalization, colon, emphasis, body weight, separation, continuity, contrast, and legibility remain independent rows; physical size remains Not verified without scale; the all-applicable-Match summary says only `No differences found in checked fields`; and no machine state records Approve | INT-026, BAIRD-30 |
| FR-059 | The evaluation harness attributes detector, recognizer, parser, rule, and evidence-boundary failures and cannot expose filenames or expected values to runtime logic; the sealed 24-product holdout records one exact normalized score per product and `brand_name`, `alcohol_content`, `producer_block`, or `warning_wording` family; repeated panels, crops, and transforms cannot add wins; the 30 to 50 unique-region set is diagnostic only | INT-Q-009, BAIRD-20, BAIRD-26 |
| FR-060 | The PP-OCRv4 versus PP-OCRv5 bakeoff holds detection boxes, preprocessing, candidates, rules, and hardware constant; detector experiments occur only when region truth proves a detection miss | INT-Q-010, BAIRD-27 |
| FR-061 | An OCR model is promoted only when the sealed holdout itself gains at least five net exact normalized product-field scores across at least two eligible FR-059 families, loses zero previously correct weak fields, creates zero false clean and no protected-field or warning-safety regression, preserves stable evidence, operates offline, uses governed assets, and passes resource-compliant local and Azure gates; development and diagnostic-region scores are reported but not pooled into the threshold | INT-Q-010, BAIRD-28 |
| FR-062 | Deployed performance uses sanitized products with distinct admitted pixel hashes and disclosed beverage, panel, difficulty, and dimension distributions on the governed 4-vCPU and 8-GiB revision; 30 distinct products provide a quick gate and at least 100 distinct product fingerprints support p95; cold startup is separate; post-ready normal and difficult runs establish the 5-second and 9-second bands; and 20-product and 300-product totals include queue and rate waits | INT-Q-011, BAIRD-34 |
| FR-063 | Language support uses a versioned field-and-language matrix for measured class, role, importer, and origin phrases; original OCR is preserved, unsupported or conflicting language remains Review, Unicode abuse is tested, and translation never satisfies the English warning | INT-025, BAIRD-29 |
| FR-064 | Material changes retain a professional revision and change-control record linking evidence, decision, requirements, implementation, verification, and closure without informal assistant attribution | INT-Q-012, BAIRD-42 |
| FR-065 | Add-panel reprocessing accepts one panel plus expected current revision, shares the atomic lineage head and 10-revision cap with corrections, enforces three total panels, reruns the complete retained panel set, refreshes every label-derived comparison value from that fresh complete read while preserving trusted application and reviewer-corrected fields, preserves unresolved beverage state unless the new evidence resolves it, reapplies only the latest correction per field using that event's source image hash, panel, polygon, and snippet when all remain valid, reports the fresh OCR timing and limitations, starts the child at Pending without resetting FIFO age, and fails safely without creating a child on stale head, invalid correction evidence, panel overflow, or revision limit | INT-002, INT-015, INT-020, BAIRD-35 to BAIRD-37 |
| FR-066 | Revision recomputation enumerates explicit provenance for every reference field, including malt alcohol-source applicability; returns the same value-source pairs that it persists; accepts fresh evidence that resolves or invalidates a label-derived beverage family; preserves an explicitly reviewer-corrected family across later class corrections; and admits OCR or reviewer-selected polygons only when every vertex is strictly within the original image and the polygon has positive area | INT-019, INT-027, BAIRD-38 |

For FR-054 and FR-061, protected fields are beverage type, brand name, class/type, alcohol content, proof, net contents, producer/name and address, country and import applicability, wine appellation, wine sulfite declaration, distilled-spirit field of vision, malt-beverage class designation, and every government-warning check. Protection covers exact normalized field accuracy, independently expected check state, and evidence-reference and polygon integrity. Evidence integrity is mandatory for every field.

### CR-002 variance disposition

FR-054 established a provisional four-exact sealed-holdout utility target before the failure classes were fully measured. General producer parsing increased exact results from 31 to 35 on the 65 applicable full-corpus cases and from 7 to 8 on the sealed holdout, while also recovering an additional previously missed or wrong producer block. It did not produce four new exact holdout transcriptions. The remaining cases are dominated by recognizer damage, absent readable pixels, and a disputed expected brand or producer interpretation. Both PP-OCRv5 candidates improved several producer transcriptions but regressed protected ABV or warning evidence as full replacements. CR-002 therefore accepts variance LV-VAR-002 rather than add product-specific corrections, weaken warning rules, or introduce a dual-recognizer runtime. Blocking-cause attribution, zero new false clean, protected-field preservation, and the full evidence report remain mandatory.

## UX states

The frontend must provide Home, single intake, grouping, processing, review workspace, government warning detail, batch queue and exceptions, history list and detail, unsupported input, decoded-pixel comparison, bad image, timeout, capacity, cancellation, and service unavailable states. Every state provides a plain-language next action.

## Definition of feature complete

A feature is complete only when its contract, implementation, automated tests, browser behavior, documentation, and traceability agree. A visual mock alone or a backend route without a usable frontend path is not complete.

## Sizing

| Epic | Features | Size |
| --- | --- | --- |
| EP-1 Local evidence engine | FR-004 through FR-018 | Large |
| EP-2 Single review experience | FR-001 through FR-003, FR-019 through FR-024, FR-038 | Medium |
| EP-3 Batch | FR-025 through FR-031 | Medium |
| EP-4 History | FR-032 through FR-037, FR-065 | Medium |
| EP-5 Platform and quality | FR-039 through FR-049 | Large |
| EP-6 Corrective provenance and review utility | FR-050 through FR-058 | Large |
| EP-7 Corrective measurement and model governance | FR-059 through FR-064 | Medium |

Sizing describes relative delivery effort, not elapsed time.
