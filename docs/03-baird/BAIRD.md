# Beginning Assessment Intake Requirements Document

Document ID: LV-BAIRD-001  
Input: LV-INTAKE-001  
Gate result: Approved for I2R

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

## Feasibility assessment

| Area | Assessment | Decision |
| --- | --- | --- |
| OCR | Local RapidOCR ONNX models provide bounded CPU inference and word polygons | Feasible |
| Deterministic comparison | Pydantic models and rule modules can express the selected checks | Feasible |
| Image recovery | Pillow and OpenCV can provide bounded orientation, deskew, perspective, resize, and contrast views | Feasible with declared limitations |
| Batch | Browser coordination can reuse the same single-pass server endpoint sequentially | Feasible for a prototype |
| History | SQLite plus controlled image storage supports FIFO 500, evidence reopening, and opaque browser-scope authorization | Feasible for one replica |
| Azure | One non-root OCI image can serve React and FastAPI on the same origin | Feasible |
| Production federal operation | Requires finalized boundary, identity, logging, retention, storage, assessment, and authorization evidence | Starter package required |

## Requirement validation

BAIRD confirms that the intake contains measurable requirements for function, performance, security, accessibility, data, error handling, batch operation, regulatory profile selection, evidence, delivery, and testing. No engineering stage is asked to invent a primary user workflow or compliance state.

## BAIRD gate

Approved for I2R subject to these non-negotiable controls:

- no fabricated application comparison
- no runtime cloud inference dependency
- no false mismatch caused solely by poor images
- no silent beverage-profile selection on conflicting evidence
- no group over 3 images
- no batch over 300 products or 900 images
- no history above 500 records
- no release without traceable tests, security checks, UI validation, and deployed smoke testing
