# Intake Requirements

Document ID: LV-INTAKE-001  
Status: Approved baseline

## Objective

Build a deployable proof of concept that reads alcohol label images locally, identifies the product category, extracts and localizes mandatory label information, applies the selected TTB rules for beer or malt beverages, wine, and distilled spirits, and presents concise evidence for a human decision.

## Users and outcomes

Primary users are TTB label compliance agents with widely varying technical comfort. A first-time user must be able to start a single or batch review without training, see what the machine read and where it read it, understand why an item needs attention, and record a disposition without losing the machine evidence.

## Functional requirements

| ID | Requirement | Acceptance measure |
| --- | --- | --- |
| INT-001 | Provide two obvious entry paths: one product and batch | Both are visible on initial load and keyboard reachable |
| INT-002 | Accept 1 to 3 JPEG, PNG, or WebP images for one product | The API and UI reject unsupported or excessive input without silent loss; measurable limit errors compare submitted and supported values and state the exact correction |
| INT-003 | OCR label images without requiring manual data entry, and compare the label with application values when the reviewer supplies them | No application field is required; an optional application form turns the read into a label-to-application comparison in which every entered value is searched across all readable lines |
| INT-004 | Infer beer or malt beverage, wine, or distilled spirits | A unique supported class/type signal selects the profile; conflicts remain unresolved |
| INT-005 | Extract brand, class/type, alcohol content, net contents, producer/name and address, import country when visible, proof when shown, and selected type-specific fields | Each found value has status, evidence reference, and original-pixel polygon |
| INT-006 | Apply common and beverage-specific deterministic checks | The ordered 24-check registry is complete in every result |
| INT-007 | Check the government warning exactly | Wording, capitalization, heading emphasis, body weight, separation, continuity, contrast, legibility, applicability, and physical-size capability are reported independently |
| INT-008 | Preserve reasonable human judgment | Case-only or punctuation-only brand differences route to Review rather than deterministic rejection |
| INT-009 | Handle recoverable imperfect images | EXIF orientation, bounded resize, deskew or perspective correction, and contrast recovery are attempted without inventing obscured text |
| INT-010 | Show evidence on the original image | Selecting a finding highlights the corresponding original-pixel region |
| INT-011 | Support reviewer disposition | Approve, Reject, and Request more information stay separate from immutable machine findings |
| INT-012 | Support batches of up to 300 products and 900 images | Supported images are accepted even when the selected folder also contains non-images; skipped files and reasons are reported; images are conservatively grouped to a maximum of 3 per product and confirmed by a reviewer |
| INT-013 | Show batch operating status | Selection begins at 0 of N; products, images, processed, remaining, running, queued, reviews, differences, failures, active time, rate, average, ETA, attempts, retry, and cancel are available |
| INT-014 | Export batch results | Formula-safe CSV summary and detailed JSON are downloadable |
| INT-015 | Retain a manageable history | Up to 500 results and their images are browsable, filterable, editable by disposition, and deletable within the originating browser scope; insertion 501 evicts the oldest |
| INT-016 | Reopen historical evidence | A stored check can relocalize its evidence on the retained image |
| INT-017 | Provide a built-in sample | A local synthetic sample exercises the complete primary flow |

## Quality requirements

| ID | Requirement | Acceptance measure |
| --- | --- | --- |
| INT-Q-001 | Typical latency | Normal readable labels target about 5 seconds; difficult recoverable labels may take 5 to 9 seconds |
| INT-Q-002 | Batch efficiency | Warm batch mean targets about 5 seconds per processed product, with total time reported; equivalent duplicate panels must not consume repeated OCR work |
| INT-Q-003 | Local runtime | OCR, models, fonts, and rule evaluation require no runtime outbound connection |
| INT-Q-004 | Accessibility | Semantic controls, keyboard operation, visible focus, non-color status cues, readable density, and responsive layout |
| INT-Q-005 | Safety | Unreadable or incomplete evidence cannot become a deterministic mismatch solely due to image quality and cannot be invented as a pass |
| INT-Q-006 | Security | Bounded multipart and JSON input, signature validation, decode limits, Host and Origin controls, browser-scoped history access, per-client and global rate controls, supervised worker timeout, non-root container, content-safe errors, and no content logging |
| INT-Q-007 | Traceability | Every feature traces to intake, design, code, and verification evidence |
| INT-Q-008 | Deployed performance parity | The Azure demo allocates the maximum 4 vCPU and 8 GiB available to its Consumption workload profile so uncached local OCR can remain within the declared latency bands |

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
- History is capped at 500 records and supports explicit deletion.
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

## Definition of intake success

The intake is complete when all known needs, derived requirements, constraints, selected regulatory rules, data handling, success measures, and unresolved external dependencies are explicit enough for BAIRD to test feasibility and completeness.
