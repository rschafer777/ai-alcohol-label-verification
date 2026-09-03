# Implementation Record

Document ID: LV-DEV-001  
Build baseline: LV-BI-001  
Status: Implementation complete; local release validation passed

## Implemented components

| Component | Location | Responsibility |
| --- | --- | --- |
| Contract loader and models | `backend/labelverify/contracts/` | Integrity-checked contracts and typed records |
| HTTP API | `backend/labelverify/api/` | Health, metadata, sample, analysis, verification, history, and public errors |
| Security boundary | `backend/labelverify/security/` | Host, Origin, length, multipart, JSON, browser-scope, rate, capacity, and identity controls |
| Supervised pipeline | `backend/labelverify/orchestration/` | Lifecycle, timeout, cancellation, one-pass analysis, result assembly |
| Image pipeline | `backend/labelverify/imaging/` | Decode, limits, quality, orientation, and recovery transforms |
| OCR and candidates | `backend/labelverify/extraction/` | Local OCR, bounded exact-pixel result reuse, field candidates, warning evidence, coordinate provenance |
| Deterministic rules | `backend/labelverify/domain/` | Normalization, family selection, comparison, warning, and 24-check aggregation |
| History repository | `backend/labelverify/persistence/` | SQLite metadata, image retention, FIFO, disposition, and deletion |
| Frontend API | `frontend/src/api/` | Typed multipart, result, metadata, and history clients |
| Application shell | `frontend/src/app/` | TTB application bar, notice band, left tray, shortcuts dialog, hash routing, single-label session, design tokens with vendored Merriweather and Public Sans |
| Shared status vocabulary | `frontend/src/components/` | Status tags and badges (color + icon + word), Lucide-style icons, blueprint frame, governed state cards, and submitted-versus-supported limit comparisons |
| Home | `frontend/src/features/home/` | Two doors, drop zones, mixed-folder image filtering, skipped-file reporting, recent checks, first-run tips |
| Review workspace | `frontend/src/features/verification/` | Processing stepper, evidence viewer with three image slots and add-image progress, table, cards and image-first layouts, warning inspect with crop and word diff, reviewer corrections, decision bar |
| Batch workspace | `frontend/src/features/batch/` | Per-image analysis with live count, rate, average and ETA, server grouping suggestions, card wall with drag and drop, merge, split, move, undo, sequential run, stats strip, exceptions, batch rail review, retry, cancel, export |
| History workspace | `frontend/src/features/history/` | Filter, paging, stored-result drawer with image slots, colored evidence regions, 24-check list, disposition override, and deletion |
| Presentation layer | `backend/labelverify/domain/presentation.py` | Display-only check groups, rule expectations, short reasons, quality summaries, beverage inference, warning wording diff |
| Grouping suggestions | `backend/labelverify/domain/grouping.py` | Directory, normalized filename, OCR brand, class/type, and beverage-family product suggestions with conflict flags |
| Deployment | `Dockerfile`, `ops/`, `.github/workflows/` | Reproducible OCI build and Azure Container Apps release |

## Implemented data movement

The browser owns only selected `File` objects, lifecycle-managed previews, unconfirmed group edits, and active batch state. The API streams admitted content to a controlled spool, the worker reads local files, and cleanup removes spool content at every terminal path. Result persistence copies admitted source panels to an opaque history directory only after a successful result. SQLite stores immutable result JSON plus mutable reviewer disposition fields. Every record is assigned to a high-entropy browser scope that is enforced by every history query. It stores no external application record because none is supplied by the label-first flow.

The UI receives original dimensions and polygons. Image display uses an SVG view box equal to original dimensions, so resized presentation does not change evidence alignment. Historical images reuse the same coordinate contract.

Every admitted analysis returns the complete 24-row registry. When beverage type is unresolved or conflicting, type-dependent rows remain Review rather than selecting a family silently. These results stay usable for human disposition and are retained in history as Type uncertain. A wine alcohol range read from the label cannot validate itself; a conforming visible range remains Review until a trusted actual value is supplied.

Candidate aggregation treats one original-pixel region as one piece of evidence even when bounded and recovery OCR views produce different readings. The strongest reading for that region is retained before independently located alternatives are classified as ambiguous. This prevents duplicate-view evidence from becoming an internal error while preserving real conflicts across distinct regions.

The worker caches no more than 2,048 OCR outputs keyed only by decoded view shape, pixel type, and pixel digest. It clears the cache at initialization. Filenames, product identities, expected values, and test-oracle data never influence a cache key or extracted value. Confirmed batch groups can therefore reuse the exact pixels already read during grouping without creating product-specific behavior.

## Selected rule inventory

The implemented registry contains beverage type, brand, class/type, ABV, proof, net contents, producer, country, wine appellation, wine sulfites, spirits field of vision, malt class designation, warning applicability, eight warning content/presentation checks, warning physical size, panel coverage, and image quality. The machine registry in `contracts/selected-check-registry-v1.json` is authoritative for order and count.

## Build dependencies

Python and frontend dependencies are locked in `uv.lock` and `frontend/package-lock.json`. OCR models and the DejaVu font are acquired during setup or image build from a manifest that verifies SHA-256. They are not fetched during label processing.

## Operational configuration

Environment settings control runtime mode, allowed host, client identity source, model root, spool root, history root, static root, sample manifest, and build ID. The default local history root is beneath the operating system temporary directory. Production uses the configured container filesystem unless a durable service is introduced at the system boundary.

The request contract uses a 15-second worker safety timeout inside the 30-second server boundary. Performance acceptance remains separate: about 5 seconds for typical work and no more than 9 seconds for difficult recoverable images.

## Implementation completion criteria

Implementation is complete when code compiles, typed contracts agree, all component and integration tests pass, frontend production assets build, and the validation protocol has no open release-blocking defect. Requester acceptance remains the UAT gate.
