# I2R Batch and Federal Readiness Architecture

Document control ID: LV-I2R-010  
Revision: 1.0  
Date: 2026-09-01  
Status: Implementation authority  
Upstream: LV-BRD-002

## 1. Selected architecture

The existing same-origin modular monolith remains the architecture. Batch adds a browser coordinator, not a second backend pipeline.

```text
Folder picker
  -> manifest parser and local safety validation
  -> ordered in-memory queue, 1 to 300 rows
  -> one POST /api/v1/verifications at a time
  -> existing FastAPI admission and supervised OCR child
  -> existing 19-check result contract
  -> row state, progress, exception filters, detail view
  -> formula-safe CSV and complete JSON download
```

This design preserves the measured single-request behavior, keeps server concurrency bounded, and avoids a database, durable worker queue, ZIP extraction surface, new API schema, and divergent comparison rules.

## 2. Batch ingress and state

The browser reads one `manifest.csv`. Required columns are `case_id`, `brand_name`, `class_type`, `abv_percent`, `net_contents_value`, `net_contents_unit`, `producer_name_address`, `is_imported`, and `panel_paths`. Optional columns are `proof` and `country_of_origin`. Panel paths are relative to the selected folder and separated by `|` or `;`.

Structural faults reject the import. Row faults create terminal visible Error rows. Files cannot be unreferenced, assigned to more than one application, addressed through an absolute or traversing path, or confused through case-only collisions. Each valid row retains the existing per-application byte, MIME, panel, decoded-pixel, timeout, and rate controls.

Queue state is memory-only. Stable ordering is the manifest order. The coordinator starts one row only after the prior row is terminal. The browser deadline remains 35 seconds per row. Cancel aborts the active request, prevents later starts, preserves completed results, and marks remaining queued rows Cancelled. Error and Cancelled rows can be retried without reselecting the folder during the same session.

The per-client start allowance is 360 verifications per ten minutes. This permits one 300-row sequential batch plus bounded retry headroom. One active request per client, a separate global start limit of 120 per minute, admission reservation, request deadlines, and the single governed OCR worker remain independent aggregate-demand controls.

## 3. Data movement and storage

1. The user selects a folder. The browser receives file handles and parses the manifest locally.
2. The browser validates structure, paths, ownership, row values, and per-row input limits.
3. For each valid row, the browser sends only that row's reference JSON and panels to the existing same-origin endpoint.
4. The API writes request files to a request-owned temporary directory, passes paths to the supervised child, validates the complete result, returns it with `no-store`, and removes temporary files after child ownership ends.
5. The browser holds queue results only in React memory. Export is an explicit local download.
6. No application content is written to a database, browser storage, analytics service, or required external inference endpoint.

## 4. Technology decision and .NET comparison

The legacy COLA system being .NET does not create an integration requirement for this standalone prototype. The selected stack is React 19.2 with strict TypeScript, Python 3.12 with FastAPI and Pydantic, RapidOCR 3.4.2, ONNX Runtime CPU, OpenCV, Pillow, and one supervised child process.

| Decision factor | Selected Python and FastAPI | .NET 8 alternative |
|---|---|---|
| OCR integration | Direct, tested RapidOCR package and governed ONNX assets | ONNX Runtime is strong, but candidate location, image rules, and OCR integration would require additional implementation or a different OCR package |
| Existing evidence | Complete local unit, corpus, lifecycle, security, and performance evidence already exists | A rewrite would invalidate evidence and consume the assignment time box |
| Process isolation | Existing killable child contains decode through aggregation | Worker process or isolated service is feasible but not already proven here |
| Contract integration | Pydantic models generate and validate the same versioned JSON contract used by TypeScript | ASP.NET can implement the same OpenAPI and JSON boundary |
| Azure operations | Runs in OCI platforms and can transition to Azure Container Apps, App Service, or AKS subject to the selected boundary | Native Azure operational familiarity may be better for a future agency team |
| COLA integration | Future adapter remains an HTTP or file contract outside the domain pipeline | Shared enterprise libraries could help only after an actual COLA integration contract exists |
| Schedule risk | Lowest because it is built and measured | High for this take-home because it is a full rewrite |

The architecture therefore selects Python for the prototype and preserves a technology-neutral API and rule contract for later procurement or COLA-adapter decisions.

## 5. Difficult-image engineering

The image path performs safe decode, EXIF orientation, bounded resizing, blur and exposure signals, estimated small-angle skew, and clipped-highlight reporting. Each difficult panel receives at most one recovery view. A clearly detected trapezoid receives perspective correction; otherwise a bounded small-angle deskew may be used. Review or Unreadable images also receive CLAHE contrast recovery. Transform matrices map derived-view OCR polygons back to original pixels.

Recovery is intentionally conservative. The system does not claim general glare removal, arbitrary bottle-surface unwarping, or reliable OCR from every photograph. A degraded source cannot convert an apparent difference into an automatic clean result, and an unreadable panel requests replacement.

## 6. Warning engineering

Warning body wording and punctuation are compared exactly after whitespace and line-wrap joining. Terminal punctuation is preserved. The heading is independently checked for exact `GOVERNMENT WARNING:` capitalization and punctuation. Heading emphasis, body emphasis, separation, continuity, contrast, and legibility remain separate visual findings.

Physical requirements depend on declared container capacity:

| Capacity | Minimum type size | Maximum characters per inch |
|---|---:|---:|
| 237 mL or less | 1 mm | 40 |
| More than 237 mL through 3 L | 2 mm | 25 |
| More than 3 L | 3 mm | 12 |

Printed text such as `2 mm` is not calibration evidence. An ordinary photograph returns Not verified for physical size and density. The domain contract supports a measured result only when separately reliable scale evidence is supplied.

## 7. Federal transition architecture

The source package supports two transition lanes. An agency-hosted application enters the agency Risk Management Framework and ATO process while inheriting applicable Azure controls. A provider-operated cloud service offering evaluates the current FedRAMP 20x path and certification class. The authorization-start package keeps the boundary, impact, identity, Azure service inventory, shared responsibility, assessor, and operations decisions open until the production deployment is selected.

The current source provides useful evidence for secure development, input controls, local inference, dependency locking, model integrity, privacy-safe logging, cleanup, testing, and configuration. Production evidence must add the actual Azure boundary, identity, encryption, centralized logging, vulnerability operations, incident handling, backup and recovery, network enforcement, retention, change control, and operating history.

## 8. Performance and resource model

The coordinator has concurrency one. Under the warmed target, the governing total limit is `10 seconds + 5 seconds * row count`. The release proves 10 and 20 row execution and a 300-row deterministic capacity run or equivalent full-pipeline evidence. It records complete rows, false-clean count, client and server timings, peak server RSS, active worker counters, cancellation, and retry. No conceptual per-item number is published as measured evidence.
