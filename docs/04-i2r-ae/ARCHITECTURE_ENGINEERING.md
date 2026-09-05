# Ideation to Realization Architecture and Engineering

Document ID: LV-I2R-001  
Inputs: LV-INTAKE-001 and LV-BAIRD-001  
Status: Approved CR-002 architecture; implemented and under release validation

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-01 | Initial modular-monolith implementation design | LV-INTAKE-001 revision 1.0 and LV-BAIRD-001 revision 1.0 |
| 1.1 | 2026-09-04 | Added review-cause telemetry, immutable observation correction, provenance separation, neutral image roles, numeric brands, controlled OCR evaluation, producer parsing, and representative deployed measurement | CR-002 |
| 1.2 | 2026-09-04 | Confirmed implementation of the corrective architecture and retained PP-OCRv4 after the governed candidate evaluation | CR-002 |
| 1.3 | 2026-09-04 | Closed final-review integrity gaps in revision provenance, unresolved type, mutation boundaries, cleanup ordering, and release evidence | CR-002 |

## System objective

LabelVerify converts one to three label-panel images into a traceable evidence record. It extracts text locally, infers the beverage family, applies selected TTB rules, preserves uncertainty, and presents the result for a human disposition. The same server pipeline supports one product and browser-coordinated batches.

## Architecture

```text
React and TypeScript user interface
  -> same-origin FastAPI boundary
    -> request limits, media validation, rate and capacity controls
      -> supervised child process
        -> Pillow and OpenCV decode and bounded recovery views
          -> RapidOCR with local ONNX models
            -> candidate extraction and original-pixel evidence mapping
              -> beverage-family inference
                -> deterministic 24-check engine
                  -> result aggregation
                    -> SQLite metadata plus retained image files
```

The solution is a modular monolith. This keeps local setup and deployment small while preserving typed boundaries between UI, ingress, orchestration, extraction, rules, and persistence. Direct COLAs Online integration is not part of this proof of concept. The independent-reference endpoint is retained for a future trusted application-data adapter.

## Technology decisions

| Layer | Selection | Engineering reason |
| --- | --- | --- |
| User interface | React, strict TypeScript, Vite | Component isolation, typed API use, fast build, accessible browser delivery |
| API and orchestration | Python 3.12, FastAPI, Pydantic, Uvicorn | Strong validation and direct fit with local image and OCR libraries |
| OCR | RapidOCR with hash-verified ONNX Runtime CPU assets | No runtime cloud inference dependency and predictable local execution |
| Image processing | Pillow, OpenCV, NumPy | Orientation, resize, quality signals, deskew, perspective, and contrast views |
| Rules | Pure deterministic Python modules plus versioned JSON registries | Explainable results and testable regulatory decisions |
| Persistence | SQLite and controlled image directory | Simple FIFO history with transactional metadata and reopenable evidence |
| Packaging | Multi-stage OCI container, non-root runtime | Repeatable local and Azure deployment |
| Azure | Azure Container Apps and private Azure Container Registry | Existing Azure context, HTTPS ingress, identity-based image pull, bounded scale, 4-vCPU and 8-GiB OCR allocation |

## Primary flows

### Single product

1. The user selects 1 to 3 images. Label-first analysis is the default and requires no typing.
2. The browser shows filenames and local previews. An optional application-values drawer accepts a trusted COLA transcription when the reviewer wants label-to-application comparison; blank fields continue to use the label read.
3. The API validates multipart size, file count, signatures, and request deadlines.
4. The worker decodes each panel, identifies strictly equivalent full-frame duplicates, and creates bounded recovery views for canonical panels.
5. OCR produces text lines, engine signals, and view coordinates. Every submitted panel remains in the result, and an equivalent duplicate names its canonical panel in quality signals.
6. Candidate extraction identifies brand, class/type, ABV, proof, net contents, producer/address, country, warning, and type-specific evidence.
7. Coordinates are mapped to the original panel and stored as four-point polygons.
8. Type inference returns malt beverage, wine, distilled spirits, or an unresolved conflict.
9. The rule engine emits every row in the ordered 24-check registry.
10. The API aggregates the machine summary, persists the result and source panels, and returns a history ID.
11. The UI displays source pixels, extracted values, regulatory expectation, reason, evidence locator, and status.
12. The reviewer records Approve, Reject, or Request more information with an optional note. This disposition does not mutate machine findings.
13. If the reviewer corrects what the pixels say, the UI submits the correction against the stored result revision. The server validates scope and version, applies the cumulative correction layer to stored observations, recomputes dependent rules without OCR, creates a linked immutable child result, and leaves the parent result and original evidence unchanged.

### Batch

1. The user selects a directory containing up to 900 supported images.
2. The browser screens supported filename extensions, MIME declarations, and file sizes, skips unrelated or oversized files individually, and displays accepted and skipped counts with reasons. The API remains authoritative for file-signature and decoded-image validation.
3. The browser submits each accepted image for a non-persistent label read. Live progress begins at 0 of N and reports count, current image, rate, mean, and ETA.
4. The server combines explicit relative-directory cues, normalized filename cues, and OCR-derived brand, class, and beverage family to suggest product groups.
5. Each suggested product contains at most three images. Ambiguous images remain visible and require confirmation.
6. The user may merge, split, or rename groups, then confirms no more than 300 products.
7. The browser submits one confirmed product at a time to the same analysis endpoint.
8. Product progress records queued, running, completed, review, difference, failure, retry, elapsed time, mean, and ETA.
9. One failed product does not stop later products. Failed products can be retried.
10. CSV and JSON exports are generated from completed result records. Spreadsheet formulas are neutralized in CSV cells.

The OCR worker keeps a bounded in-memory cache of at most 2,048 exact decoded view results. Its key contains image shape, pixel type, and a SHA-256 digest of the view pixels. It never contains a filename, product name, expected field, oracle value, or reviewer decision. A cache miss runs local OCR normally. The cache is cleared when the worker initializes and is lost when the process exits. This accelerates the confirmed-product rerun after the same images were read for grouping without changing extraction behavior for a new image.

### History

1. Every successful analysis or independent-reference verification creates one history record.
2. Metadata and immutable result JSON are committed to SQLite. Images are written beneath an opaque record directory.
3. The UI lists newest first and supports text, beverage, summary, and disposition filters.
4. Detail retrieves checks and retained images. Show on label reuses stored original-pixel evidence.
5. A disposition or note update changes only reviewer fields.
6. Deletion removes metadata and associated image files.
7. Every record carries an opaque browser scope. All listing, detail, image, disposition, and deletion queries require that scope.
8. The API issues the scope as an HttpOnly, SameSite Strict cookie, adding Secure in production. The identifier is high entropy and is not available to application JavaScript.
9. The 500-entry ceiling counts product lineages, not individual revisions. Each lineage has at most 10 stored revisions including its root, corrections, and add-panel reprocessing. Insertion of a new product above 500 entries evicts the oldest complete lineage and its assets in one transaction. A new revision remains inside its existing history entry and does not reset FIFO age.

The 500-entry and 10-revision ceilings are global within the demo repository, while access to each lineage remains browser-scope filtered. This bounds retained snapshots to 5,000 while content-addressed images are shared safely. The metadata contract exposes both limits. Attempting revision 11 returns `409 revision_limit` with the action to start a new product analysis. The existing per-client and global mutation-start rate controls cover correction and add-panel writes. The API deletes only complete lineages. Individual revisions cannot be deleted, so FIFO or explicit deletion cannot leave a surviving child with a missing parent.

## Corrective provenance and revision architecture

The corrective release separates three concepts that must never share one provenance value:

1. `label_ocr`: text and structured candidates produced from submitted image pixels.
2. `reviewer_corrected`: a human correction of what a stored image visibly says. It overlays a field value for deterministic re-evaluation but does not replace the raw OCR candidate or original evidence.
3. `trusted_application`: independently supplied application values used for label-to-application comparison. These values cannot be derived from the same OCR result they are compared against.

`manifest` and `sample` remain controlled fixture or integration sources. The contract version changes because existing `manual` provenance does not distinguish a trusted reference from a correction. Provenance is field-level, never record-level. Each observed or reference field carries `value`, `provenance`, and its evidence or source reference. A single result can therefore contain trusted application fields, blank application fields that fall back to label observations, unchanged OCR fields, and reviewer-corrected fields without misrepresenting any source. Checks, persistence, history detail, CSV, and JSON export preserve that field-level provenance.

The correction command is `POST /api/v1/history/{id}/corrections`. The request envelope is `{ "expectedRevision": integer, "reason": string, "actorLabel": string optional, "corrections": [field-specific correction union] }`. Every correction also carries either `evidenceRef`, or `panelId` plus a valid original-pixel four-point `polygon` for a visible value missed by OCR. The field-specific union is:

| Field ID | Correction value | Server behavior |
| --- | --- | --- |
| `beverage_type` | `{ "family": "malt_beverage" | "wine" | "distilled_spirits" }` | Preserve the family choice and cited class evidence |
| `brand_name`, `class_type`, `country_of_origin`, `wine_appellation` | `{ "visibleText": string }` | Preserve the bounded verbatim transcription and derive any normalized vocabulary match |
| `wine_sulfite_declaration` | `{ "visibleText": string }` | Accept only a visible Contains Sulfites transcription and derive presence; typed absence is not evidence of chemistry |
| `alcohol_content` | `{ "visibleText": string }` | Parse number or range, percent form, abbreviation, and decimal precision from the transcription |
| `proof` | `{ "visibleText": string }` | Parse proof value and proof wording while retaining spatial evidence for relation, placement, and distinction checks |
| `net_contents` | `{ "visibleText": string }` | Parse quantity and unit from the transcription and retain the exact printed unit form |
| `producer_name_address` | `{ "visibleText": string }` | Parse role, organization, importer signal, and up to four address lines from the transcribed visible block |

Visible text is trimmed, line-preserving, and bounded to 500 characters except the producer block, which is bounded to 1,000 characters and five lines. The server never accepts a client-supplied normalized decimal, range, unit, sulfite Boolean, or producer component as authoritative. It stores both `visibleText` and its derived parsed representation with `reviewer_corrected` provenance. Rules use the verbatim form for abbreviation, precision, range, unit, required wording, placement, and presentation decisions, and the parsed form only where numeric or vocabulary comparison is required. The browser renders beverage type as a closed selector. For a correctable field with no OCR evidence, it requires the reviewer to select the image and draw the original-pixel rectangle that contains the visible text. A sulfite correction must transcribe a visible Contains Sulfites statement and can derive presence only; `none`, `not present`, and other absence assertions are rejected. `warning_wording`, warning presentation, image quality, panel coverage, and every other visual or machine-capability finding are not correctable. Typed text alone can never create warning, chemistry, or visual-presentation clearance.

The response is `{ "historyId": string, "rootId": string, "parentId": string, "revision": integer, "result": verification result }`. Each lineage has an immutable `root_id`, monotonically increasing `revision`, and one authoritative `latest_record_id`. A database transaction verifies browser scope, verifies that `{id, expectedRevision}` is the current lineage head, inserts a child under uniqueness constraint `(root_id, revision)`, and compare-and-swaps the current pointer. Concurrent attempts against the same parent yield one success and one `409 revision_conflict`; divergent heads cannot be created. Unknown fields or invalid types return bounded `422` errors, oversized bodies return `413`, wrong-origin mutations return `403`, and a record outside the scope returns `404`.

History persists a self-contained original observation and evidence snapshot on every revision, the cumulative correction set, revision number, root and parent IDs, correction event, and recomputed result. Every correction event carries the raw submitted transcription, line-preserving visible text, server-derived representation, original snippet, source panel, original-pixel polygon, and source image SHA-256. Replay collapses repeated edits by field but treats the latest event as one indivisible unit, so the latest value, image hash, panel, polygon, and snippet always travel together. It resolves that locator against retained content; an order-derived evidence display ID is not sufficient. Images use content-addressed blobs and every revision holds its own references. Explicit deletion and FIFO eviction remove a complete lineage in the SQLite transaction, commit that metadata change, and only then unlink newly unreferenced blobs. Startup reconciliation safely retries orphan cleanup after interruption. Original OCR evidence, source pixels, and parent results remain immutable. A corrected child starts with a Pending human disposition and no inherited note, while the parent retains its earlier disposition and note. Correction never calls image decoding, preprocessing, detection, recognition, or the supervised OCR worker.

The correction dependency graph is deterministic and is the same contract used by FR-053.

| Corrected field | Required recomputation |
| --- | --- |
| `beverage_type` | Every common and family applicability decision, class, alcohol, proof, net contents, country and import status, every type-specific row, warning applicability, and aggregation |
| `class_type` | Beverage inference unless an explicit corrected beverage type exists, warning applicability, every class-triggered wine, malt, and spirits rule, and aggregation; conflicting or insufficient corrected class evidence requires a cited beverage-type correction rather than a default family |
| `alcohol_content` | Alcohol result; proof-to-ABV relation; proof same-field-of-vision placement and visual distinction or adjacency relative to the corrected ABV evidence; warning applicability; family range rules; distilled-spirit field of vision using cited spatial evidence; and aggregation |
| `proof` | Observed proof value and wording, twice-ABV relation, same-field-of-vision placement relative to ABV, visual distinction or adjacency, and aggregation |
| `brand_name` | Distilled-spirit field of vision using cited spatial evidence and aggregation |
| `net_contents` | Net contents, government-warning physical-size threshold and displayed requirement, and aggregation |
| `producer_name_address` | Producer result, importer detection, country applicability, import status, and aggregation |
| `country_of_origin` | Country result, import applicability, import status, and aggregation |
| `wine_appellation` | Wine appellation result and aggregation |
| `wine_sulfite_declaration` | Wine sulfite result and aggregation |

Every recomputed row identifies whether it used `label_ocr`, `reviewer_corrected`, or `trusted_application`, and reviewer-corrected Matches remain visibly labelled as reviewer-corrected rather than machine-only Matches.

Protected fields are beverage type, brand name, class/type, alcohol content, proof, net contents, producer/name and address, country and import applicability, wine appellation, wine sulfite declaration, distilled-spirit field of vision, malt-beverage class designation, and all government-warning checks. Protection covers exact normalized field accuracy, independently expected check state, and evidence-reference and polygon integrity. A regression means a previously correct protected value or expected state becomes incorrect, or valid evidence becomes invalid or unbound. Evidence integrity remains mandatory for every field.

The reviewer label is a bounded prototype display value and is stored as a non-secret actor label or generated opaque audit surrogate. The browser-scope bearer value authorizes access but is never returned, exported, logged, or displayed as reviewer identity or correction evidence. This is not represented as a verified federal workforce identity or complete audit system.

Add-panel reprocessing uses the same lineage transaction and revision cap. `POST /api/v1/history/{id}/panels` accepts one supported panel plus `expectedRevision`, requires the addressed revision to be the current head, enforces the three-panel product limit, and runs OCR over the complete retained panel set. The server builds a fresh label-derived reference from that complete read, merges only trusted application and reviewer-corrected fields from the prior head, reapplies the latest still-valid cumulative correction event per field to its unchanged source-image hash and polygon, and recomputes all rules. This prevents newly readable label text from being compared against a stale earlier label-derived baseline. The new analysis retains its own OCR timings, limitations, and model identity. An unresolved label-derived beverage type remains unresolved unless the complete retained evidence now resolves it or an existing cited reviewer correction selected the family; no default profile is introduced for persistence or recomputation. The immutable child has revision kind `panel_added`, starts at Pending disposition, preserves the root FIFO timestamp, and becomes the current head by compare-and-swap. A stale head, invalidated correction evidence, panel overflow, or revision-limit attempt returns a bounded actionable error without creating a child. Add-panel and correction requests serialize on the same authoritative head.

The merge enumerates every reference field and assigns its source explicitly; absence of a provenance entry is never interpreted as permission to borrow the record-wide source. If the prior family was label-derived, the fresh complete read is authoritative and may resolve it or return it to unresolved when evidence becomes conflicting or insufficient. If the family was explicitly reviewer-corrected, later class corrections do not replace it through inference. OCR polygons and reviewer-selected rectangles share one validation function: all vertices use half-open original-image bounds (`0 <= x < width`, `0 <= y < height`) and the polygon must have positive area before it can become audit evidence.

The add-panel response is assembled from the same merged authority that is committed to history. Fresh `label_ocr` values remain from the new complete read; every `trusted_application` or `reviewer_corrected` value is overlaid from its authoritative reference. The returned draft and stored reference therefore expose the same value-source pairs in both resolved and unresolved beverage-family paths.

## Review-cause attribution

Aggregation returns both the existing summary and a deterministic `reviewCauses` collection. Each cause contains the blocking check ID, normalized category, reason code, and evidence reference when available. Categories are `missing_evidence`, `ocr_uncertainty`, `presentation_uncertainty`, `trusted_context_missing`, `conflicting_evidence`, and `policy_review`.

Technical completion, review routing, field accuracy, and disposition accuracy are reported separately. A lower Review count is not an improvement unless paired ground truth shows no new false clean and no protected-field regression.

## Numeric-brand design

Numeric and digit-led marks use a separate candidate path. The path first removes numeric strings tied to percent alcohol, proof, volume units, vintage or establishment years, age statements, postal codes, barcodes, lot or reference prefixes, prices, and container deposits. Remaining candidates receive positive weight from position-independent page geometry: relative text height and area, isolation from dense text, trademark proximity, repetition across submitted panels, and proximity to independently detected class or core-field evidence. Upload order and semantic panel names never contribute. Multiple plausible numeric marks remain Ambiguous and route to Review. No product name, filename, directory, oracle, or expected application value participates.

## Producer-block design

Producer extraction is a structured block operation, not a single longest-line choice. It identifies a role phrase, bounded organization lines, and adjacent address lines while excluding warning text, websites, tasting copy, composition statements, and unrelated promotional text. It preserves component evidence and a combined display value. Evaluation classifies misses by detection, recognition, line joining, selection, vocabulary, and language before changing the corresponding layer.

## Warning machine-match boundary

Photographic evidence may produce Match for an individual warning check when the pixels and OCR support that specific conclusion. Exact supported statutory words and punctuation may make the `warning_wording` row Match. Heading capitalization, colon, emphasis, body weight, separation, continuity, contrast, and legibility remain independently adjudicated rows and do not change a supported wording result. Physical size is Not verified without a scale reference and does not become applicable merely because other warning rows Match. Ambiguous punctuation, damaged OCR, incomplete views, contradictory reads, or uncertain typography remain Review for the affected row. A product summary may say only `No differences found in checked fields` when every applicable row Matches. No machine state records Approve or claims complete legal compliance.

Warning-specific recovery may reread only bounded warning regions when the primary result is missing or uncertain and the remaining request budget permits. Agreement can increase evidence confidence; disagreement cannot be resolved by majority vote and remains Review.

## OCR evaluation and promotion architecture

The deployed OCR model does not change by assumption. A controlled harness reuses identical decoded views and PP-OCRv3 detection boxes while comparing the current PP-OCRv4 English recognizer with PP-OCRv5 English mobile and, for separately identified Latin-script cases, PP-OCRv5 Latin. A recognizer can be promoted only after paired development and sealed-holdout results satisfy LV-VP-001.

Detection is tested separately only when region annotations show that expected text was absent from detector boxes. PP-OCRv6, a second full-image OCR lane, general-purpose language models, vision-language models, translation engines, and fine-tuning are outside CR-002. A later change record is required to introduce any of them.

All governed model assets require an approved source, redistribution review, SHA-256 integrity, read-only runtime placement, SBOM coverage, explicit runtime identity, and operation with outbound network access blocked.

## Evaluation data and deployed performance

The 70-image field corpus remains paired development evidence and the 42-case disposition oracle remains safety evidence. CR-002 adds an independently annotated, product-separated sealed 24-product holdout with eight products from each beverage family, one to three images, numeric controls, producer blocks, exact and defective warnings, import conditions, and difficult-image characteristics. One score is recorded per product and eligible field family. Eligible OCR weak-field families are `brand_name`, `alcohol_content`, `producer_block`, and `warning_wording`. Correct means an exact field value after the field's published normalization; partial and containment results do not count as correct. Multiple panels, crops, transforms, and recognizer attempts for the same product-field remain one scoring unit. A separate 30 to 50 predeclared region set records one exact box and transcript per unique source region and is diagnostic evidence only, not an additional sealed-holdout win.

OCR promotion requires at least five net additional correct product-field scores across at least two eligible weak-field families on the sealed holdout itself, with zero previously correct weak-field losses. Development and region results are reported separately and cannot be pooled into the five-win threshold. All zero-false-clean, protected-field, evidence-stability, integrity, licensing, offline, resource, and Azure gates also remain mandatory.

CR-002 utility is measured separately from OCR promotion. After WP-13 freezes the recoverable baseline errors, the corrected system must gain `min(4, recoverable baseline error count)` additional correct product-field scores across `producer_block` and `warning_wording` on the sealed holdout, with at least one gain in each family that has a recoverable baseline error, zero lost previously correct scores, zero new false clean, and no protected-field regression. Unscaled physical size and irreducible presentation uncertainty are excluded from the recoverable baseline and reduction target. Cause attribution still must reconcile every Review result, but attribution alone cannot satisfy this utility gate.

Formal deployed timing uses sanitized representative products with distinct admitted pixel hashes on the governed 4-vCPU and 8-GiB Azure revision. The harness publishes beverage-family, one-to-three-panel, normal-versus-difficult, and image-dimension distributions. Thirty distinct products provide a quick gate. At least 100 distinct product request fingerprints are required for a formal p95 claim. Re-encoding, metadata changes, cache-busted duplicates, and repeated governed samples are diagnostic smoke evidence only. A governed cache-disabled mode may replace uniqueness for a diagnostic comparison but cannot establish the representative p95 claim.

Cold scale-to-zero activation is measured from request start through readiness and first result, reported separately, and excluded from the 5-second normal and 9-second difficult post-ready request bands. Warm one-panel, two-panel, and three-panel request latency establishes those per-product bands. The 20-product and 300-product tests report both active processing time per product and total end-to-end wall time. Queueing, retries, capacity waits, and rate-limit waits are included in total batch time. The warm active mean must be no more than 5 seconds per product, every selected difficult product must remain below 9 seconds, and total wall time targets are no more than 100 seconds for 20 products and 1,500 seconds for 300 products. No restart, timeout, dropped item, or memory failure is permitted.

## Beverage classification

Classification is vocabulary-based and explainable. Whole terms prevent substring errors such as finding `gin` inside `origin`.

- Malt beverage signals include beer, lager, ale, porter, stout, malt beverage, and India pale ale. `IPA` alone is not treated as a complete mandatory class designation.
- Wine signals include wine, table wine, light wine, red wine, white wine, rose, sparkling wine, and recognized varietal or appellation language when accompanied by wine context.
- Distilled spirits signals include whiskey, whisky, bourbon, vodka, gin, rum, tequila, brandy, liqueur, and distilled spirits.
- One clear family selects the profile. No signal or conflicting families produces Review, never an invented family.

The supported beer path is the federal malt-beverage profile in 27 CFR part 7. The interface says Beer or malt beverage because beer, lager, ale, porter, and stout are recognized malt-beverage class signals. Pixels cannot establish the statutory ingredient composition of an ambiguous non-malt product. A generic or conflicting cue may select candidates for display, but the beverage-type check remains Review unless the submitted class/type evidence supports the malt-beverage profile.

The selected family activates distinct checks. A future classifier may improve ranking, but it must retain these observable conflict and fail-safe rules.

## Rule activation

All results contain the complete registry in a stable order. Non-applicable checks remain present as Not verified so consumers do not mistake omission for success.

| Area | Malt beverage | Wine | Distilled spirits |
| --- | --- | --- | --- |
| Brand and class/type | Required | Required | Required |
| Alcohol content | Conditional on formula or state rule | Numeric statement above 14 percent; table/light wine exception from 7 through 14 percent | Required |
| Net contents | U.S. customary units | Applicable wine standard | Applicable spirits standard |
| Producer/address | Required visible responsible party statement | Required visible responsible party statement | Required visible responsible party statement |
| Country | Required when imported | Required when imported | Required when imported |
| Type-specific | Recognized class; `ABV` abbreviation not accepted for a mandatory statement | Conditional appellation and sulfite declaration | Brand, class/type, and ABV same field of vision |
| Government warning | Required at 0.5 percent ABV or more | Required at 0.5 percent ABV or more | Required at 0.5 percent ABV or more |

Malt alcohol ranges are deterministic mismatches. Decimal precision above the permitted one or two places is a deterministic mismatch. Wine ranges are parsed as two bounds and compared with the trusted reference value, maximum span, and 14 percent boundary. When no trusted actual value exists, a range cannot be treated as proof of compliance. Spirits and malt ranges are not authorized by the selected profile. Proof is compared with twice ABV; unresolved visual distinction from the ABV statement remains Review rather than being guessed.

The warning engine separately evaluates applicability, exact wording, uppercase heading, heading emphasis, body not bold, separation, continuity, contrast, legibility, and physical-size capability. Exact wording normalizes whitespace, letter case (27 CFR 16.22 fixes the case of the heading only), line wrapping, and clause numbers fused to the next word; any other punctuation difference is a review item that names the marks, and word differences follow the substitution, omission, and noise rules recorded in `docs/08-validation/REGULATORY_VALIDATION.md`. Unknown ABV keeps applicability under Review while the visible warning is still inspected.

Visual presentation decisions use closed, testable boundaries. Type weight is measured as stroke width (area over half perimeter) divided by letter height (upper quartile of connected-component heights) for the heading and each body line; a heading at 1.3 times the body's ratio or more is bold, at 1.05 or less it is no heavier than the body and goes to review, and the band between is inconclusive and goes to review. The older ink-density boundaries (heading at or above 0.32 supports bold, at or below 0.25 supports not bold; body at or above 0.25 supports bold, at or below 0.22 supports not bold) decide only when the type is too small to measure. Contrast needs the WCAG luminance ratio and the gray-level range to agree: both low over at least two lines is a difference when the ratio is below 2.0 or the read of those lines is weak, and a review item when medium-gray type between 2.0 and the 3.0 minimum was read with confidence (capture flattens the contrast a photograph records); both clear is a match, disagreement is review. Separation compares the box gap to the statement's line height: three quarters of a line height or more is separate, a quarter or less is adjoining and goes to review, and the band between (ordinary line spacing) goes to review. Type weight and separation never reject on their own, the ink-density contrast heuristic never rejects without the measurements, and a continuity failure rejects only inside a cleanly read statement.

## Result and evidence contract

Machine states are Match, Mismatch, Review, and Not verified.

- Match requires reliable evidence that satisfies the implemented rule.
- Mismatch requires a visible, deterministic difference.
- Review means judgment, conflicting candidates, missing trusted context, or recoverable uncertainty.
- Not verified means the check is not applicable or the capability cannot establish it.

Each evidence item includes an opaque ID, panel ID, four original-pixel points, source view, transform ID, OCR text snippet, and engine signal marked as not a calibrated probability. The result includes accepted panels, extracted observations, all 24 checks, limitations, summary, server duration, policy versions, and history ID.

## Image engineering

The browser applies EXIF orientation when decoding supported images and proportionally prepares a photo that exceeds 12 megapixels or 4 MiB. It uses a small pixel headroom, bounded JPEG quality ladder, and bounded size reductions before upload. The server remains authoritative and enforces 12 megapixels per image, 36 megapixels per request, bytes, signatures, and counts. The backend decoder measures blur, exposure, coverage, and glare indicators. The recovery path may create bounded resize, contrast, deskew, or clear trapezoid views. It never fills missing pixels or fabricates text. Coordinates from derived server views are inverted to the admitted panel pixels before delivery.

Warning extraction is panel-scoped. Every submitted panel containing a warning produces its own observation and evidence. A complete exact read outranks a partial read. When no panel is complete, statutory words may be confirmed only when their expected positions are covered across independent panel reads; that outcome remains Review so punctuation and physical presentation are not inferred across images.

Full-frame visual deduplication uses a 64 by 64 grayscale fingerprint, an aspect-ratio tolerance of 0.2 percent, normalized correlation of at least 0.999, and normalized mean absolute error of at most 0.025. This narrow gate removes redundant OCR work for equivalent JPEG and PNG encodings while preserving distinct product surfaces. The API retains all submitted panels and marks only the duplicate panel with `duplicateOfPanelId`.

Decoded-pixel errors carry image width, height, total decoded pixels, aspect-preserving target dimensions, supported maximum, pass or fail state for each comparison, and a precise retry instruction. These values cross the typed API boundary and are rendered side by side in the browser.

Recommended UAT input is 2400 by 3200 pixels in portrait, or 3200 by 2400 in landscape, with 300 PPI metadata, JPEG quality 85 to 92, and roughly 1 to 4 MiB per file. The label should occupy at least 60 percent of the frame and important character height should be at least 20 pixels. PPI metadata is not a reliable physical scale. A 736 by 532 image is accepted when readable but is below the recommended evidence density.

## Security and reliability

- Accept only JPEG, PNG, and WebP signatures.
- Enforce 4 MiB per file, 12 MiB aggregate file content, 3 files, 12 MP per image, and 36 MP total.
- Bound raw multipart input at 13 MiB plus the defined envelope and reject malformed or mismatched lengths.
- Enforce Host and Origin controls, browser-scoped history authorization, bounded multipart and JSON bodies, per-client and global start rates, and one governed OCR worker.
- Use upload, worker safety, server, and browser deadlines of 20, 15, 30, and 35 seconds. The 15-second worker boundary is a fault-containment limit, not the performance goal. Typical and difficult-image quality targets remain about 5 seconds and no more than 9 seconds. The extraction stage keeps a dense label inside those bounds by skipping the second, closer OCR read when the first pass has used four seconds of OCR time, and the result lists the skipped read as a limitation.
- Allocate 4 vCPU and 8 GiB to the Azure Consumption workload profile so the local ONNX inference path has sufficient parallel CPU for the same latency bands used by local validation.
- Run expensive processing in a killable child and clean temporary files after success, error, cancellation, disconnect, and shutdown.
- Do not log label content, notes, or OCR text.
- Serve UI and API from one origin with security headers.
- Run the container as a non-root user and deploy immutable image digests.

## Storage and deployment boundaries

Local SQLite and file persistence are correct for a single-instance demonstration and preserve the 500-record workflow. Azure Container Apps may replace local instance storage during revision changes or scale-to-zero lifecycle events. A production boundary must select durable managed storage, identity, audit logging, encryption-key policy, records retention, backup, legal hold, and recovery objectives. Those decisions do not change the result contract.

The browser retains the selected `File` objects and preview URLs while a batch workspace is open. The API bounds every request and product, but the maximum 900-image selection can consume significant operator-workstation memory. Production rollout must validate browser memory on the agency workstation baseline and may add staged selection or virtualized preview loading without changing the server contract.

## External interfaces

| Method and path | Purpose |
| --- | --- |
| `GET /health/live` | Process liveness |
| `GET /health/ready` | Model and service readiness |
| `GET /api/v1/meta` | Contract, rule, limit, and build identity |
| `GET /api/v1/samples/distilled-spirits-v1` | Built-in local sample metadata |
| `GET /api/v1/samples/distilled-spirits-v1/panels/{panelId}` | Built-in sample panel |
| `POST /api/v1/analyses` | Label-first OCR, inference, checks, and persistence |
| `POST /api/v1/verifications` | Independent trusted-reference comparison |
| `POST /api/v1/grouping-suggestions` | Analyze batch image facts without persistence, propose conservative product groups, and identify groups that require reviewer confirmation |
| `GET /api/v1/history` | Filtered and paged history |
| `GET /api/v1/history/{id}` | Full stored result |
| `GET /api/v1/history/{id}/panels/{panelId}` | Retained source image |
| `POST /api/v1/history/{id}/panels` | Add one panel to the current lineage head with expected revision, reprocess the complete panel set, reapply valid correction overlays, reset disposition to Pending, and atomically advance the shared revision head |
| `POST /api/v1/history/{id}/corrections` | Apply bounded cumulative reviewer corrections to stored observations, recompute deterministic checks without OCR, and persist an immutable linked revision |
| `PATCH /api/v1/history/{id}/disposition` | Reviewer disposition and note |
| `DELETE /api/v1/history/{id}` | Delete the addressed record's complete lineage, all revisions, and unreferenced image blobs |
| `DELETE /api/v1/history` | Delete every lineage visible to the originating browser scope and its unreferenced image blobs |

## Architecture acceptance

The design is realizable within the take-home scope, has one implementation path for single and batch processing, preserves evidence and uncertainty, covers all three required beverage families, supports local inference, and exposes clear production transition boundaries. It is approved for feature definition and build planning.
