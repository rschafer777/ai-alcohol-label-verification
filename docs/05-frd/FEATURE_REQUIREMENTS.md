# Feature Requirements Document

Document ID: LV-FRD-001  
Inputs: LV-INTAKE-001, LV-BAIRD-001, LV-I2R-001  
Status: Approved build baseline

## Feature requirements

| ID | Feature and acceptance criteria | Source |
| --- | --- | --- |
| FR-001 | Home presents Check one product and Check a batch as the two primary actions | INT-001 |
| FR-002 | Single intake accepts 1 to 3 JPEG, PNG, or WebP images with preview, reorder, remove, and clear validation | INT-002 |
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
| FR-015 | Warning text comparison normalizes only whitespace and line wrapping | INT-007 |
| FR-016 | Warning presentation reports capitalization, heading emphasis, body weight, separation, continuity, contrast, legibility, and size capability independently using the closed measurement boundaries in LV-I2R-001; intermediate evidence routes to Review | INT-007 |
| FR-017 | Missing or unreadable evidence never becomes a deterministic label failure by itself | INT-Q-005 |
| FR-018 | Case-only or punctuation-only brand variations route to Review | INT-008 |
| FR-019 | Review workspace shows rule expectation, extracted value, state, reason, and evidence action | INT-010 |
| FR-020 | Show on label highlights the correct original-pixel polygon on the correct panel | INT-010 |
| FR-021 | User can zoom, rotate, enhance, and switch among up to three panels without changing evidence coordinates | INT-009, INT-010 |
| FR-022 | Warning detail shows prescribed and observed text plus all warning subchecks | INT-007 |
| FR-023 | Reviewer can record Approve, Reject, or Request more information and an optional note | INT-011 |
| FR-024 | Keyboard shortcuts operate reviewer disposition without trapping focus | INT-Q-004 |
| FR-025 | Batch accepts up to 900 supported images, skips unsupported selected files individually, and reports accepted and skipped counts and reasons | INT-012 |
| FR-026 | Grouping uses directory, filename, OCR brand, class/type, and beverage-family cues and never silently places more than three images in a product | INT-012 |
| FR-027 | User can inspect, merge, split, name, and confirm groups before processing | INT-012 |
| FR-028 | Batch reuses the analysis endpoint sequentially with failure isolation | INT-012 |
| FR-029 | Batch begins at 0 of N and reports products, images, processed, remaining, running, queued, review, differences, failures, active time, rate, mean, ETA, and attempts | INT-013 |
| FR-030 | User can cancel remaining work and retry failed groups | INT-013 |
| FR-031 | Batch exports formula-safe CSV and detailed JSON | INT-014 |
| FR-032 | Every successful analysis or reference verification creates a history record with images | INT-015 |
| FR-033 | History supports newest-first paging and filters for query, beverage, summary, and disposition | INT-015 |
| FR-034 | History detail reopens checks, images, and evidence location | INT-016 |
| FR-035 | Disposition updates do not alter immutable machine findings | INT-011, INT-015 |
| FR-036 | Record deletion removes metadata and files; Clear all requires confirmation | INT-015 |
| FR-037 | Insertion 501 evicts the oldest metadata and image directory | INT-015 |
| FR-038 | Built-in sample completes the primary workflow without a network dependency | INT-017 |
| FR-039 | UI is semantic, keyboard reachable, visibly focused, non-color dependent, and usable at 1366 by 768 | INT-Q-004 |
| FR-040 | Public errors are bounded, content-safe, actionable, and include retry behavior; measurable limit errors show supported, submitted, pass or fail, and exact correction values | INT-002, INT-Q-006 |
| FR-041 | Upload, pixel, timeout, rate, capacity, cleanup, and non-root controls match the versioned contracts; the 15-second worker safety limit remains distinct from the 5-second typical and 9-second difficult-image quality targets | INT-Q-001, INT-Q-006 |
| FR-042 | Normal readable labels target about 5 seconds and difficult recoverable labels target no more than 9 seconds | INT-Q-001 |
| FR-043 | Warm sequential batches target about 5 seconds mean per product | INT-Q-002 |
| FR-044 | Metadata exposes build, contract, profile, check count, rules, limits, runtime, and history policy | INT-Q-007 |
| FR-045 | Independent-reference verification remains available for a future trusted COLA adapter and does not influence OCR candidate discovery | BAIRD unknown 1 |
| FR-046 | History reads and mutations require the originating opaque browser scope; mutation bodies are bounded and production mutations require exact same-origin evidence | INT-Q-006 |
| FR-047 | The OCR worker may reuse a bounded result only for byte-identical decoded view pixels and dimensions; filenames, product names, expected fields, and oracle data never form a cache key or extraction override | INT-Q-001, INT-Q-002 |
| FR-048 | Equivalent full-frame panels may share canonical OCR work only when strict aspect, visual-correlation, and normalized-error gates all pass; every upload remains in the result, duplicates identify the canonical panel, and distinct product surfaces are never collapsed | INT-002, INT-Q-002, BAIRD-15 |
| FR-049 | The governed Azure template allocates 4 vCPU and 8 GiB to the Consumption replica, and deployment readback blocks any resource configuration drift before smoke testing | INT-Q-008, BAIRD-16 |

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
| EP-4 History | FR-032 through FR-037 | Medium |
| EP-5 Platform and quality | FR-039 through FR-049 | Large |

Sizing describes relative delivery effort, not elapsed time.
