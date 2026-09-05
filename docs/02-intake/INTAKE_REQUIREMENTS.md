# Intake Requirements

Document ID: LV-INTAKE-001  
Status: Approved CR-002 requirements baseline; implementation and validation traced

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-01 | Initial integrated prototype baseline | Assignment discovery |
| 1.1 | 2026-09-04 | Added UAT-driven provenance, correction, review-attribution, numeric-brand, image-role, producer, language-boundary, warning-clearance, and representative-performance requirements | CR-002 |
| 1.2 | 2026-09-04 | Confirmed implementation trace and retained measured corrective variances through change control | CR-002 |
| 1.3 | 2026-09-04 | Clarified immutable correction evidence, unresolved-type handling, mutation controls, and release-evidence binding after final review | CR-002 |

## Objective

Build a deployable proof of concept that reads alcohol label images locally, identifies the product category, extracts and localizes mandatory label information, applies the selected TTB rules for beer or malt beverages, wine, and distilled spirits, and presents concise evidence for a human decision.

## Users and outcomes

Primary users are TTB label compliance agents with widely varying technical comfort. A first-time user must be able to start a single or batch review without training, see what the machine read and where it read it, understand why an item needs attention, and record a disposition without losing the machine evidence.

## Functional requirements

| ID | Requirement | Acceptance measure |
| --- | --- | --- |
| INT-001 | Provide two obvious entry paths: one product and batch | Both are visible on initial load and keyboard reachable |
| INT-002 | Accept 1 to 3 JPEG, PNG, or WebP images for one product | The browser proportionally prepares supported phone photos that exceed upload limits; the API remains authoritative and the UI rejects unsupported or excessive input without silent loss; measurable limit errors compare submitted and supported values and state the exact correction |
| INT-003 | OCR label images without requiring manual data entry, and compare the label with application values when the reviewer supplies them | No application field is required; an optional application form turns the read into a label-to-application comparison in which every entered value is searched across all readable lines |
| INT-004 | Infer beer or malt beverage, wine, or distilled spirits | A unique supported class/type signal selects the profile; conflicts remain unresolved |
| INT-005 | Extract brand, class/type, alcohol content, net contents, producer/name and address, import country when visible, proof when shown, and selected type-specific fields | Each found value has status, evidence reference, and original-pixel polygon |
| INT-006 | Apply common and beverage-specific deterministic checks | The ordered 24-check registry is complete in every result |
| INT-007 | Check the government warning exactly | Each panel carrying the warning is evaluated independently; the clearest complete read is used, complementary partial reads may confirm statutory words across images, and wording, capitalization, heading emphasis, body weight, separation, continuity, contrast, legibility, applicability, and physical-size capability are reported independently |
| INT-008 | Preserve reasonable human judgment | Case-only or punctuation-only brand differences route to Review rather than deterministic rejection |
| INT-009 | Handle recoverable imperfect images | EXIF orientation, bounded resize, deskew or perspective correction, and contrast recovery are attempted without inventing obscured text |
| INT-010 | Show evidence on the original image | Selecting a finding highlights the corresponding original-pixel region |
| INT-011 | Support reviewer disposition | Approve, Reject, and Request more information stay separate from immutable machine findings |
| INT-012 | Support batches of up to 300 products and 900 images | Supported images are accepted even when the selected folder also contains non-images; skipped files and reasons are reported; images are conservatively grouped to a maximum of 3 per product and confirmed by a reviewer |
| INT-013 | Show batch operating status | Selection begins at 0 of N; products, images, processed, remaining, running, queued, reviews, differences, failures, active time, rate, average, ETA, attempts, retry, and cancel are available |
| INT-014 | Export batch results | Formula-safe CSV summary and detailed JSON are downloadable |
| INT-015 | Retain a manageable history | Up to 500 product results are browsable as lineages within the originating browser scope; each lineage retains no more than 10 independently reopenable root, add-panel, or correction revisions; insertion of product 501 evicts the oldest complete lineage; deleting any revision deletes its complete lineage |
| INT-016 | Reopen historical evidence | A stored check can relocalize its evidence on the retained image |
| INT-017 | Provide a built-in sample | A local synthetic sample exercises the complete primary flow |
| INT-018 | Distinguish machine findings from reviewer disposition | Match means the checked photographic evidence satisfied the implemented deterministic rule; it does not approve a label, and Approve, Reject, or Request more information remains an independent human action |
| INT-019 | Distinguish trusted application values, machine observations, and reviewer-corrected observations | Every individual observed and reference field, check, returned revision draft, stored revision, history detail, and export preserves its own `trusted_application`, `label_ocr`, `reviewer_corrected`, `manifest`, or `sample` provenance; each returned value agrees with its declared source and persisted reference; mixed-source results never use one record-level provenance |
| INT-020 | Correct an observed label value without rerunning OCR | An allowlisted correction is bound to an immutable source image hash, panel, and polygon, including a reviewer-drawn region when OCR has no box; retains the original OCR snippet; preserves the verbatim visible statement and server-derived normalized form; creates an immutable cumulative child revision under one atomically serialized lineage; preserves the original OCR, pixels, unresolved beverage state, and parent disposition; starts the child disposition at Pending; invokes OCR zero times; and server-recomputes every declared dependent check. Repeated-field replay uses the latest correction value and that same event's locator. Beverage correction uses a closed three-family choice, class correction reruns family inference, and typed sulfite text can establish only a visibly printed Contains Sulfites statement, never chemical absence. A normalized number alone and typed warning, presentation, quality, or coverage data cannot clear a visible defect |
| INT-021 | Explain and measurably reduce recoverable review work | Every overall Review identifies its blocking checks and normalized causes; on the sealed holdout CR-002 also achieves the declared recoverable producer and warning-wording utility gain without reducing unscaled physical-size or irreducible presentation safeguards |
| INT-022 | Avoid unconfirmed semantic image roles | Result, evidence, history, and export surfaces use Image 1, Image 2, and Image 3 unless a reviewer explicitly assigns a role; upload order never changes compliance behavior |
| INT-023 | Recognize numeric-only and digit-led brands without product-specific logic | Prominent numeric marks may be brand candidates only after excluding ABV, proof, quantity, vintage, age, ZIP, barcode, lot, reference, price, and deposit contexts; ambiguity remains Review |
| INT-024 | Extract the responsible-party block as structured evidence | Producer, bottler, brewer, vintner, distiller, and importer role, organization, and address lines remain evidence-linked; unrelated adjacent marketing copy is excluded and partial text is not treated as a complete trusted match |
| INT-025 | Bound supported language behavior | Versioned field-specific vocabularies may support measured class, role, importer, and origin phrases; original text is preserved, unsupported or conflicting language remains Review, and translation never satisfies the English government warning |
| INT-026 | Allow exact photographic warning evidence to receive a machine Match | Exact supported wording may make the wording row Match while every presentation row remains independently adjudicated; physical size stays Not verified without scale, uncertainty remains Review for the affected row, the all-Match summary says only `No differences found in checked fields`, and no machine state records Approve |
| INT-027 | Preserve authority and evidence validity across revisions | Every add-panel merge assigns explicit field provenance, including conditional rule triggers; fresh conflicting or insufficient evidence may return a label-derived family to unresolved; a reviewer-corrected family remains authoritative during later class corrections; and reviewer-selected polygons use the same strictly in-bounds, positive-area original-pixel rule as OCR evidence |

## Quality requirements

| ID | Requirement | Acceptance measure |
| --- | --- | --- |
| INT-Q-001 | Typical latency | Normal readable labels target about 5 seconds; difficult recoverable labels may take 5 to 9 seconds |
| INT-Q-002 | Batch efficiency | Warm batch mean targets about 5 seconds per processed product, with total time reported; equivalent duplicate panels must not consume repeated OCR work |
| INT-Q-003 | Local runtime | OCR, models, fonts, and rule evaluation require no runtime outbound connection |
| INT-Q-004 | Accessibility | Semantic controls, keyboard operation, visible focus, non-color status cues, readable density, and responsive layout |
| INT-Q-005 | Safety | Unreadable or incomplete evidence cannot become a deterministic mismatch solely due to image quality and cannot be invented as a pass |
| INT-Q-006 | Security | Bounded multipart and JSON input, signature validation, decode limits, Host and Origin controls before resource-identifier acceptance, browser-scoped history access, per-client and global rate controls, supervised worker timeout, commit-consistent history and blob cleanup, non-root container, content-safe errors, and no content logging |
| INT-Q-007 | Traceability | Every feature traces to intake, design, code, and verification evidence |
| INT-Q-008 | Deployed performance parity | The Azure demo allocates the maximum 4 vCPU and 8 GiB available to its Consumption workload profile so uncached local OCR can remain within the declared latency bands |
| INT-Q-009 | Trustworthy evaluation | Runtime code cannot access filenames, oracle values, or expected answers; accuracy changes use one published score per sealed-holdout product and eligible field family, never count repeated panels or transforms as separate wins, and report diagnostic region, routing, and accuracy results separately |
| INT-Q-010 | Governed OCR model selection | A candidate recognizer or detector is adopted only after a one-variable-at-a-time bakeoff proves net field improvement, zero new false clean, no protected-field regression under the definition below, reproducible evidence, offline operation, acceptable licensing, pinned integrity, and resource compliance |
| INT-Q-011 | Representative deployed measurement | Azure claims use sanitized representative products with distinct admitted pixel hashes and disclosed beverage, panel, difficulty, and dimension distributions; cold startup is separate from post-ready latency, rate and queue waits remain in total batch time, and repeated or re-encoded samples remain diagnostic evidence only |
| INT-Q-012 | Controlled change history | Material requirement, design, implementation, validation, and release changes retain reason, evidence, impact, decision, and closure status without assistant names or informal implementation transcripts; release evidence hashes bind to the canonical staged source bytes |

Protected fields are beverage type, brand name, class/type, alcohol content, proof, net contents, producer/name and address, country and import applicability, wine appellation, wine sulfite declaration, distilled-spirit field of vision, malt-beverage class designation, and all government-warning checks. A protected-field regression occurs when an independently correct exact normalized value becomes incorrect, an independently correct expected check state becomes incorrect, or a valid source-panel evidence reference or polygon becomes invalid or unbound. Evidence integrity is mandatory for every field, including fields outside this protected accuracy set.

## Regulatory rule selection

Common visible checks cover brand, class/type, net contents, producer/name and address, country for imports, government warning, panel coverage, and image quality.

Wine adds alcohol-content handling, table/light wine exception handling, conditional appellation, and conditional sulfite declaration. Chemistry, production records, permit truth, and wine below 7 percent jurisdiction cannot be established from pixels alone and remain visible limitations or review conditions.

Malt beverage adds recognized class/type handling, the rule that `IPA` alone is insufficient, U.S. customary net contents, and alcohol-statement triggers. Whether alcohol comes from added flavors or other non-beverage ingredients requires a trusted formula fact. `ABV` is not accepted as an abbreviation. Ranges are not permitted. Statements at or above 0.5 percent use no more than one decimal place, and statements below 0.5 percent use no more than two.

Wine supports a specific percentage or a permitted range. A range may span at most 3 percentage points at or below 14 percent and 2 points above 14 percent, must contain the trusted actual value when available, and may not cross the 14 percent class boundary. Specific-value product tolerances and other class or tax boundaries require trusted application or laboratory facts and cannot be inferred from pixels.

Distilled spirits requires alcohol content and checks that brand, class/type, and alcohol content appear in the same submitted field of vision. Proof is optional but, when shown, is compared with the two-times-ABV relationship and must be in the same field of vision as, yet adequately distinguished from, the ABV statement.

The federal health warning applies at 0.5 percent alcohol by volume or more for every beverage family. Unknown strength preserves unknown applicability. The app never assumes a missing value is below the threshold.

## Data and privacy requirements

- Uploaded images and extracted text are treated as user content.
- Temporary request files are removed after completion, cancellation, timeout, or failure.
- History stores the final result and 1 to 3 images under application control.
- History is capped at 500 product lineages and 10 revisions per lineage, and explicit deletion removes one complete lineage.
- The public demo assigns an opaque browser scope and authorizes list, read, update, image, and delete operations only within that scope.
- Logs contain request identifiers and operational metadata, not label text or images.
- The public demo is limited to synthetic or sanitized data.

## Assumptions, trade-offs, and limitations

- COLAs Online integration is not part of the prototype. The primary interface therefore performs label-first regulatory evidence review rather than pretending OCR-derived values are an independent application record.
- Product grouping uses conservative directory and filename cues, followed by mandatory human confirmation. It favors avoiding false merges over automatic grouping recall.
- Multiple uploaded files that contain the same rendered panel remain visible as separate submitted files, but the processor may OCR one canonical copy when a strict visual-equivalence test proves they carry the same pixels in a different encoding.
- OCR-derived brand, class, and beverage-family evidence supplements directory and filename cues. OCR disagreement keeps the suggested group visible for confirmation instead of silently splitting or merging it.
- Physical type size cannot be proven from an ordinary unscaled photograph. The check reports the applicable requirement and remains Not verified unless reliable scale exists.
- Formula, chemistry, permit, source, production-method, state-law, and product-origin truth require independent records.
- General glare removal, curved-bottle reconstruction, and recovery of pixels outside the frame are not promised.
- Local SQLite and retained images satisfy prototype history. Local-container storage can reset when an Azure revision is replaced; a production boundary must select managed durable storage and an agency retention schedule.
- Sequential batch execution favors predictable CPU and memory. Total elapsed time grows with product count.
- OCR confidence is an engine signal, not a calibrated compliance probability.
- The 221-image result distribution is a review-routing baseline, not an accuracy rate. Only independently annotated cases support accuracy claims.
- Exact machine Match applies only to the implemented check and its visible evidence. It never establishes complete legal compliance or records a reviewer approval.
- Broad multilingual compliance is not claimed. Supported field and language combinations are versioned and tested; all others fail closed to Review.

## Definition of intake success

The intake is complete when all known needs, derived requirements, constraints, selected regulatory rules, data handling, success measures, and unresolved external dependencies are explicit enough for BAIRD to test feasibility and completeness.
