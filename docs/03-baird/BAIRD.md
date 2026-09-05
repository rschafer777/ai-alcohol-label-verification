# Beginning Assessment Intake Requirements Document

Document ID: LV-BAIRD-001  
Input: LV-INTAKE-001  
Gate result: CR-002 requirements approved by three independent reviews and released to implementation

## Revision history

| Revision | Date | Change | Authority |
| --- | --- | --- | --- |
| 1.0 | 2026-09-01 | Validated the initial intake for I2R | LV-INTAKE-001 revision 1.0 |
| 1.1 | 2026-09-04 | Assessed UAT findings, measurement gaps, correction provenance, review utility, numeric brands, producer extraction, language boundaries, and deployed performance | CR-002 and LV-INTAKE-001 revision 1.1 |
| 1.2 | 2026-09-04 | Recorded requirements clearance and linked the approved corrective baseline to implementation and validation | CR-002 |
| 1.3 | 2026-09-04 | Closed final-review gaps in unresolved type, correction evidence, mutation boundaries, persistence ordering, and canonical release evidence | CR-002 |
| 1.4 | 2026-09-05 | Assigned one unique, sequential identifier to every derived requirement and reconciled downstream feature traceability | CR-002 final requirements review |

## Purpose

BAIRD determines what discovery defined, what it did not define, and which derived requirements are necessary for the product to work safely and coherently.

## Known facts

- The task is a standalone proof of concept and excludes direct COLAs Online integration.
- The primary work is OCR-assisted label evidence review with human disposition.
- Beer or malt beverage, wine, and distilled spirits require common plus category-specific logic.
- Normal response time must be near 5 seconds to remain useful.
- Runtime outbound ML endpoints are unsuitable for the operating environment.
- Users need a simple interface, batch processing, exact warning scrutiny, and imperfect-image recovery.
- Deliverables include source, README, approach, tools, assumptions, trade-offs, limitations, and a deployed URL.
- Product images form one logical product group of 1 to 3 panels.
- History must retain and manage at most 500 completed results.

## Facts not supplied by discovery

| Unknown | Product impact | BAIRD disposition |
| --- | --- | --- |
| Independent application data source | OCR output cannot prove application-to-label equality | Keep a typed reference-verification API, use label-first UI, and clearly distinguish readable label evidence from independent comparison |
| Product formula and chemistry | Some malt ABV and wine sulfite rules depend on non-image facts | Report the limitation and route unresolved applicability to human review |
| Import status when no origin text is visible | A missing country statement cannot prove domestic status | Label-derived records keep import applicability unresolved |
| Physical label scale | Pixels and PPI metadata do not prove millimeters | Report the threshold but do not assert pass or failure without reliable scale |
| State alcohol-label rules | Malt alcohol statements can depend on state law | Keep federal selected rules separate and disclose state-law dependency |
| Agency records schedule and legal hold | Determines retention and deletion | Implement 500-record prototype FIFO; require agency schedule before production |
| Identity and authorization model | Needed for production reviewer attribution | Keep demo single-user and local; define external identity as a production boundary decision |
| Azure durable data service | Needed for revision-safe history | Use local persistence for the prototype; select managed durable storage during authorization design |
| Expected file naming and folder discipline | Affects automatic grouping accuracy | Use conservative cues, never exceed 3 images per suggested group, and require explicit confirmation |
| Non-image files in selected folders | A folder can contain manifests or unrelated files | Skip unsupported entries individually, retain supported images, and report every skipped file and reason |
| Duplicate panels in different image encodings | Repeating OCR adds latency without adding evidence | Detect only near-identical full-frame images using strict aspect, correlation, and error thresholds; retain each upload record and identify its canonical panel |
| Cloud CPU allocation for local OCR | Undersized CPU changes uncached image latency even when code and models are identical | Use the 4-vCPU and 8-GiB maximum of the selected Azure Consumption workload profile and verify the effective allocation after deployment |
| High-resolution phone photographs | Direct camera files can exceed the service byte or decoded-pixel boundary even when they contain useful label evidence | Prepare supported images locally in the browser with proportional resize and bounded JPEG encoding, then retain the server limits as the authoritative security boundary |
| Warning split across curved or repeated views | One photograph may hide words that another photograph shows | Read the warning separately on every submitted panel, prefer the clearest complete read, and allow cross-image word confirmation only as Review because punctuation may remain unresolved |
| Cause of an overall Review | A conservative summary does not reveal which checks consume reviewer effort | Add normalized blocking-cause attribution and report routing separately from field and disposition accuracy |
| Numeric-only brand population | Existing governed field truth does not contain a sufficient numeric-brand sample | Annotate existing numeric products plus negative numeric controls before setting a success percentage |
| Producer failure cause | Aggregate results cannot distinguish detection, recognition, line joining, selection, vocabulary, or language errors | Categorize each producer miss or wrong result before selecting parser, OCR, or vocabulary changes |
| Reviewer-correction identity | The prototype has browser scope but no verified workforce identity | Use the scope only for authorization; never expose it as identity or evidence, and store a bounded non-secret actor label or generated audit surrogate without claiming a federal audit identity |
| Supported language matrix | Discovery requires import handling but does not define a set of supported languages | Add only field-specific languages justified by annotated cases and route unsupported language to Review |
| Representative Azure OCR timing | Existing Azure checks use repeated governed samples | Measure unique sanitized representative photographs on the governed 4-vCPU and 8-GiB environment before claiming deployed parity |
| Warning machine-clearance boundary | A blanket refusal to match photographic evidence defeats routine triage, while relaxed text comparison risks false clean | Permit machine Match only for complete exact supported evidence; retain Review for unresolved punctuation, presentation, contradiction, or scale |

## Derived requirements

1. Separate observation from judgment. OCR must not receive application values as candidate hints.
2. Preserve provenance. Every located value must retain panel ID, polygon, source view, transform, text snippet, and engine signal.
3. Use four check states: Match, Mismatch, Review, and Not verified. Do not collapse uncertainty into failure.
4. Keep reviewer disposition separate from the machine result.
5. Make beverage-profile selection explicit in the result, including confidence signal and reason.
6. Use local, hash-governed OCR assets and deterministic rule registries.
7. Enforce upload, byte, pixel, count, timeout, concurrency, and cleanup limits before expensive processing.
8. Retain images with history so evidence links do not become dead records, while isolating every history operation to the originating browser scope.
9. Use FIFO eviction and deletion that remove both metadata and associated files.
10. Provide stable API contracts and machine-readable rule/check registries.
11. Validate the complete flow in both local and deployed environments.
12. Keep the UI usable at 1366 by 768 and on smaller responsive layouts.
13. Make limit failures actionable by returning submitted values, supported limits, and a precise next action.
14. Keep the worker safety timeout separate from the latency quality target so a recoverable multi-panel product is not killed at the target boundary.
15. Avoid repeat OCR for strictly equivalent panels while retaining submitted-panel accountability and never collapsing distinct front, back, neck, or side evidence.
16. Bind deployed performance to a governed compute allocation and reject configuration drift before public verification.
17. Prepare oversized supported browser images before upload without weakening server-side byte, pixel, signature, or count enforcement.
18. Combine warning evidence conservatively across panels: one exact complete read may govern, while complementary partial reads can confirm words only and cannot machine-clear punctuation.
19. Report the exact blocking check IDs and normalized cause categories for every Review summary.
20. Keep review-routing distribution, field accuracy, disposition accuracy, and technical processing success as separate measures.
21. Preserve immutable OCR evidence when a reviewer corrects an observation; server-side re-evaluation must not invoke OCR.
22. Model observation corrections as one atomically serialized lineage with an immutable root, current head, unique revision, cumulative edits, scope isolation, bounded requests, complete-lineage deletion, independently reopenable evidence, and a Pending child disposition.
23. Treat provenance as field-level data. Independent application values are `trusted_application`, visible reviewer corrections are `reviewer_corrected`, and raw observations are `label_ocr`; mixed-source results retain every field's source through checks, history, and export.
24. Use neutral image ordinals after intake unless a semantic role is explicitly confirmed; role metadata cannot alter the rule outcome by itself.
25. Add a separate constrained numeric-brand path using position-independent page geometry, trademark proximity, repetition, and proximity to independently detected core fields, with exhaustive numeric-context exclusions and no upload-order signal.
26. Classify producer failures before changing OCR, layout joining, selection ranking, or role vocabularies.
27. Compare OCR candidates with identical detection boxes, preprocessing, candidate logic, rules, and evaluation cases; change one model component at a time.
28. Promote an OCR model only after the sealed holdout gains at least five net correct product-field scores across at least two eligible weak-field families, with zero previously correct weak-field losses, zero false clean, no protected-field regression, and operational acceptability; diagnostic regions and repeated panels cannot supply promotion wins.
29. Add bounded language phrases only after OCR and producer parsing stabilize and annotated evidence shows a vocabulary gap.
30. Preserve exact statutory warning behavior: exact supported wording may Match its row, each presentation row remains independent, physical size stays Not verified without scale, material visible differences Mismatch, and unresolved evidence Review.
31. Restrict corrections to typed, allowlisted observed fields with existing evidence or a reviewer-selected source-panel polygon. Preserve reviewer-transcribed visible text and derive normalized numbers, units, ranges, precision, abbreviations, and components on the server so normalization cannot hide a printed defect. Warning wording, warning presentation, image quality, and coverage are not manually correctable.
32. Recompute the complete declared dependency graph after a corrected beverage type, class, ABV, proof, brand, net contents, producer, country, appellation, or sulfite observation.
33. Measure corrective utility on recoverable producer and warning-wording product-fields in the sealed holdout. Require the declared bounded gain with zero loss and zero new false clean; exclude unscaled physical size and irreducible presentation uncertainty.
34. Establish representative Azure performance with distinct admitted pixel hashes and a disclosed distribution. Measure cold startup separately, apply 5-second and 9-second bands only after readiness, and include queue and rate waits in batch wall time.
35. Preserve an unresolved beverage type across all revisions unless supported label evidence or a cited reviewer correction resolves it; never substitute a default profile to make a revision executable.
36. Bind correction replay to immutable source content and coordinates rather than an order-derived display identifier, and preserve raw visible text plus server-derived values as separate audit facts.
37. Treat one correction event as the indivisible replay unit: its latest value, source image hash, panel, polygon, and original snippet travel together. After add-panel OCR, refresh label-derived comparison values from the complete read while preserving trusted application and reviewer-corrected values.
38. Make revision authority explicit. Every carried or refreshed field, including conditional malt-alcohol source, receives field provenance; each returned revision value agrees with its declared source and the reference persisted to history; newly conflicting or insufficient evidence invalidates a prior label-derived family instead of preserving stale certainty; a reviewer-corrected family cannot be replaced by later class inference; and manually cited polygons must be positive-area and strictly inside the original image bounds.
39. Restrict beverage correction to the three supported families and rerun inference after class correction. If the corrected class remains absent or conflicts across families, require an explicit cited family correction rather than selecting a default.
40. A reviewer may transcribe a visible Contains Sulfites statement, but typed text cannot establish sulfite absence or other chemistry. When OCR provides no evidence region for any correctable field, require a reviewer-drawn bounded original-pixel region before accepting the correction.
41. Apply state-change security controls before accepting any path identifier, delete persisted files only after metadata commit, and reconcile orphaned files after interrupted cleanup.
42. Hash governed source evidence using the same canonical byte representation that Git stages and the release manifest verifies.

## Feasibility assessment

| Area | Assessment | Decision |
| --- | --- | --- |
| OCR | Local RapidOCR ONNX models provide bounded CPU inference and word polygons | Feasible |
| Deterministic comparison | Pydantic models and rule modules can express the selected checks | Feasible |
| Image recovery | Pillow and OpenCV can provide bounded orientation, deskew, perspective, resize, and contrast views | Feasible with declared limitations |
| Batch | Per-image local analysis can drive server-side grouping, human confirmation, and sequential product analysis through the same bounded endpoint | Feasible for a prototype |
| History | SQLite plus controlled image storage supports FIFO 500, evidence reopening, and opaque browser-scope authorization | Feasible for one replica |
| Azure | One non-root OCI image can serve React and FastAPI on the same origin | Feasible |
| Production federal operation | Requires finalized boundary, identity, logging, retention, storage, assessment, and authorization evidence | Starter package required |

## Requirement validation

BAIRD confirms that the corrective intake contains measurable requirements for function, performance, security, accessibility, data, provenance, error handling, batch operation, regulatory profile selection, evidence, review utility, delivery, and testing. Measurement gaps are explicit prerequisites rather than hidden assumptions. No engineering stage is asked to invent a primary user workflow, provenance type, or compliance state.

## BAIRD gate

Approved for I2R subject to these non-negotiable controls:

- no fabricated application comparison
- no runtime cloud inference dependency
- no false mismatch caused solely by poor images
- no silent beverage-profile selection on conflicting evidence
- no group over 3 images
- no batch over 300 products or 900 images
- no history above 500 product lineages or 10 revisions within one lineage
- no release without traceable tests, security checks, UI validation, and deployed smoke testing
- no corrective implementation until three independent reviewers return Clear on one identical frozen lifecycle-document snapshot
- no correction path that reruns OCR or overwrites the original observation
- no positional Front or Back claim without an explicit confirmed role
- no reduced Review count obtained by converting uncertainty into Match
- no model promotion based on repeated fixtures, local-only timing, or an unannotated sample
- no broad language or translation claim without a versioned supported matrix and independent tests
- no default beverage profile when type remains unresolved
- no correction replay based only on an order-derived evidence identifier
- no metadata rollback that can leave a surviving history record without its retained image
