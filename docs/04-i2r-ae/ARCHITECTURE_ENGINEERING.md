# Ideation to Realization Architecture and Engineering

Document ID: LV-I2R-001  
Inputs: LV-INTAKE-001 and LV-BAIRD-001  
Status: Approved design baseline

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
| Azure | Azure Container Apps and private Azure Container Registry | Existing Azure context, HTTPS ingress, identity-based image pull, bounded scale |

## Primary flows

### Single product

1. The user selects 1 to 3 images.
2. The browser shows filenames and local previews. No label values are requested.
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

### Batch

1. The user selects a directory containing up to 900 supported images.
2. The browser accepts supported image signatures and sizes, skips unrelated or oversized files individually, and displays accepted and skipped counts with reasons.
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
9. Insertion above 500 records evicts the oldest record and images in FIFO order.

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

The warning engine separately evaluates applicability, exact wording, uppercase heading, heading emphasis, body not bold, separation, continuity, contrast, legibility, and physical-size capability. Exact wording normalizes only whitespace and line wrapping. Unknown ABV keeps applicability under Review while the visible warning is still inspected.

Visual presentation decisions use closed, testable boundaries. Heading ink density at or above 0.32 supports bold and at or below 0.25 supports not bold. Body mean ink density at or above 0.25 supports bold and at or below 0.22 supports not bold. Values between boundaries remain Review. A heading-to-body density ratio at or above 1.8 supports heading emphasis; a ratio at or below 1.65 combined with no meaningful height difference supports lack of emphasis. Separation passes when the preceding-text gap is at least 0.75 times the smaller line height and fails at or below 0.25, subject to surrounding-text ambiguity. Contrast below 0.30 fails; contrast at or above 0.30 with every supporting OCR signal at or above 0.80 passes. Legibility passes when every supporting OCR signal is at least 0.80 and fails when any is below 0.50. Intermediate or missing measurements remain Review. Ordinary image metadata does not prove physical type size, so that check remains Not verified without reliable scale.

## Result and evidence contract

Machine states are Match, Mismatch, Review, and Not verified.

- Match requires reliable evidence that satisfies the implemented rule.
- Mismatch requires a visible, deterministic difference.
- Review means judgment, conflicting candidates, missing trusted context, or recoverable uncertainty.
- Not verified means the check is not applicable or the capability cannot establish it.

Each evidence item includes an opaque ID, panel ID, four original-pixel points, source view, transform ID, OCR text snippet, and engine signal marked as not a calibrated probability. The result includes accepted panels, extracted observations, all 24 checks, limitations, summary, server duration, policy versions, and history ID.

## Image engineering

The decoder applies EXIF orientation and enforces 12 megapixels per image and 36 megapixels per request. It measures blur, exposure, coverage, and glare indicators. The recovery path may create bounded resize, contrast, deskew, or clear trapezoid views. It never fills missing pixels or fabricates text. Coordinates from derived views are inverted to original pixels before delivery.

Full-frame visual deduplication uses a 64 by 64 grayscale fingerprint, an aspect-ratio tolerance of 0.2 percent, normalized correlation of at least 0.999, and normalized mean absolute error of at most 0.025. This narrow gate removes redundant OCR work for equivalent JPEG and PNG encodings while preserving distinct product surfaces. The API retains all submitted panels and marks only the duplicate panel with `duplicateOfPanelId`.

Decoded-pixel errors carry image width, height, total decoded pixels, aspect-preserving target dimensions, supported maximum, pass or fail state for each comparison, and a precise retry instruction. These values cross the typed API boundary and are rendered side by side in the browser.

Recommended UAT input is 2400 by 3200 pixels in portrait, or 3200 by 2400 in landscape, with 300 PPI metadata, JPEG quality 85 to 92, and roughly 1 to 4 MiB per file. The label should occupy at least 60 percent of the frame and important character height should be at least 20 pixels. PPI metadata is not a reliable physical scale. A 736 by 532 image is accepted when readable but is below the recommended evidence density.

## Security and reliability

- Accept only JPEG, PNG, and WebP signatures.
- Enforce 4 MiB per file, 12 MiB aggregate file content, 3 files, 12 MP per image, and 36 MP total.
- Bound raw multipart input at 13 MiB plus the defined envelope and reject malformed or mismatched lengths.
- Enforce Host and Origin controls, browser-scoped history authorization, bounded multipart and JSON bodies, per-client and global start rates, and one governed OCR worker.
- Use upload, worker safety, server, and browser deadlines of 20, 15, 30, and 35 seconds. The 15-second worker boundary is a fault-containment limit, not the performance goal. Typical and difficult-image quality targets remain about 5 seconds and no more than 9 seconds.
- Run expensive processing in a killable child and clean temporary files after success, error, cancellation, disconnect, and shutdown.
- Do not log label content, notes, or OCR text.
- Serve UI and API from one origin with security headers.
- Run the container as a non-root user and deploy immutable image digests.

## Storage and deployment boundaries

Local SQLite and file persistence are correct for a single-instance demonstration and preserve the 500-record workflow. Azure Container Apps may replace local instance storage during revision changes or scale-to-zero lifecycle events. A production boundary must select durable managed storage, identity, audit logging, encryption-key policy, records retention, backup, legal hold, and recovery objectives. Those decisions do not change the result contract.

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
| `POST /api/v1/history/{id}/panels` | Add a panel to an existing result, reprocess the complete panel set, and persist a new record linked through `supersedes` |
| `PATCH /api/v1/history/{id}/disposition` | Reviewer disposition and note |
| `DELETE /api/v1/history/{id}` | Delete one record and images |
| `DELETE /api/v1/history` | Clear all history |

## Architecture acceptance

The design is realizable within the take-home scope, has one implementation path for single and batch processing, preserves evidence and uncertainty, covers all three required beverage families, supports local inference, and exposes clear production transition boundaries. It is approved for feature definition and build planning.
