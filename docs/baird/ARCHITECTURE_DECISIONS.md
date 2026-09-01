# BAIRD Architecture Decision Record

**Status:** Selected architecture, pending corrected BAIRD re-review

## Decision index

| ADR | Decision | Status |
|---|---|---|
| `ADR-001` | Single-origin modular monolith | SELECTED |
| `ADR-002` | React/TypeScript/Vite frontend | SELECTED |
| `ADR-003` | Python 3.12/FastAPI backend | SELECTED |
| `ADR-004` | RapidOCR/ONNX self-contained baseline behind adapter | SELECTED FROM MEASURED SPIKE |
| `ADR-005` | Deterministic rule and aggregation engine | SELECTED |
| `ADR-006` | Request-scoped ephemeral processing, no database | SELECTED |
| `ADR-007` | Synchronous API with one killable OCR worker | SELECTED |
| `ADR-008` | Same-origin immutable OCI deployment | SELECTED |
| `ADR-009` | Fly.io always-ready primary host | SELECTED WITH RELEASE READBACK |
| `ADR-010` | Batch isolated behind post-core gate | SELECTED |
| `ADR-011` | Evidence contract is immutable; reviewer disposition is separate | SELECTED |
| `ADR-012` | No declared external inference dependency and denied common outbound ports | SELECTED WITH NETWORK POLICY |

## `ADR-001`: Single-origin modular monolith

**Decision:** Use one deployable service with internal modules for API, uploads, image processing, extraction, candidate location, comparison, regulatory rules, aggregation, and static UI.

**Why:** The take-home needs one public URL, low operational complexity, deterministic latency, and simple local reproduction. Microservices or a separate frontend host add network, CORS, versioning, and deployment surfaces without a current scaling need.

**Consequence:** Module boundaries are enforced in code and tests even though deployment is one container.

## `ADR-002`: React, TypeScript, and Vite

**Decision:** Use React with strict TypeScript and Vite. Prefer semantic HTML and small local components over a heavy design system.

**Why:** The interface has non-trivial form, upload, progress, evidence, focus, and multi-state behavior. React supports reusable field rows and accessible state transitions. Vite keeps the build direct.

**Rejected:** Next.js server features are unnecessary because FastAPI owns the server and a second runtime would complicate deployment.

## `ADR-003`: Python 3.12 and FastAPI

**Decision:** Use Python 3.12, FastAPI, Pydantic, and Uvicorn.

**Why:** Python offers the lowest-friction integration with OCR, ONNX, Pillow, and OpenCV. FastAPI creates typed request/response contracts and testable endpoints.

**Consequence:** The API event loop must not execute blocking OCR directly. Bounded worker execution and concurrency are explicit.

## `ADR-004`: RapidOCR/ONNX behind an extraction adapter

**Decision:** The core adapter returns tokens, lines, boxes, raw confidence provenance, duration, model ID/version/hash, and typed errors. RapidOCR 3.4.2, ONNX Runtime 1.22.1 CPU, and the three exact artifacts in `evidence/MODEL_BOM.md` are the selected implementation.

**Why:** It is local, produces regions, and passed the retained full-pipeline and Chrome architecture slice. Tesseract.js failed required field coverage on the same contact sheets.

**Stop gate:** A wrong model hash, rights/notice change, any false clean, a failed committed field-family minimum, or deployed p95 above five seconds blocks release and reopens BAIRD. Scope cannot be narrowed without requester-approved change control. No fixture-specific fallback map is allowed.

## `ADR-005`: Deterministic rule and aggregation engine

**Decision:** Field parsing, normalization, comparison, warning checks, capability, and submission aggregation are pure versioned logic. The versioned 17-check registry is the executable selected scope. A separate versioned regulatory-rules registry owns authoritative source metadata, exact warning text, and the 0.5 percent ABV applicability threshold. OCR confidence can route uncertainty but cannot approve a result.

**Why:** The evaluator must see correctness and code quality. Deterministic rules are explainable, unit-testable, and resistant to prompt/model drift.

## `ADR-006`: Ephemeral request processing, no database

**Decision:** No application database, object storage, saved cases, server session, or durable queue. Images exist only in bounded request memory or controlled temporary spooling and are closed/deleted on every path.

**Why:** Persistence is not required and would expand privacy/retention scope.

**Consequence:** Refresh loses the current result unless the browser retains it in memory. UI states this clearly.

## `ADR-007`: Synchronous core API

**Decision:** One verification request returns one complete result. The HTTP process delegates OCR to one long-lived child process. A separate supervisor owns the worker slot, controlled input copies, and derived buffers until true worker completion. A client disconnect suppresses delivery but does not release ownership. Any number of caller cancellations are deferred until the worker finishes or is terminated. If the independent 6.25-second worker safety deadline expires, the parent terminates and joins the child, clears readiness, and returns a 504 when delivery remains possible. The supervisor removes artifacts only after child exit is confirmed. A replacement starts and warms in a background thread. Readiness returns 503 and new verification starts return 503 until the replacement has passed model, selected-check registry, regulatory-rules registry, registry-version, read-only-asset, and representative-warmup checks.

**Why:** The result target is five seconds. A job queue would add polling, persistence, and lifecycle complexity.

**Consequence:** Only one OCR job runs on the selected 2 vCPU instance. A process-global pre-body gate admits no more than two verification POSTs. Each admission reserves 50,593,792 bytes for both the multipart parser copy and the controlled request copy, so aggregate admitted spool reservation is at most 101,187,584 bytes inside a 128 MiB application spool quota. One application-owned multipart parser applies the selected limits on the real endpoint. Later requests receive 429 or 503 before body consumption. Every admitted request has a 3.0 second total body deadline starting at pre-body admission; chunk activity does not reset it, and expiry returns 408 `upload_timeout` after explicit partial-upload cleanup and reservation release. The single worker lock has a 200 ms acquisition deadline, after which a waiting admitted request returns 503 `worker_queue_busy`. A supervisor owns worker artifacts independently of caller cancellation. A global start bucket allows 30 starts per minute. A client digest allows 20 starts per 10 minutes and one active request. Its table is capped at 4,096 entries with a 15-minute inactive TTL. Shutdown stops intake, drains owned supervisors through the worker deadline, then terminates and joins the child if needed. Real-stack parser-limit, partial-spool timeout, repeated-cancellation, abort-storm, shutdown, child-count, and cleanup tests are required.

## `ADR-008`: Multi-stage one-container delivery

**Decision:** Node builds static assets in an earlier Docker stage. A non-root Python runtime contains only production dependencies, hash-verified OCR models, the API, and built static files. CI builds one OCI image, records its digest, and promotes that exact digest to Fly.io.

**Why:** One artifact ties source revision, model, UI, and API together and works on Fly.io, Azure, and local Docker.

**Consequence:** The immutable release tuple contains source commit, `package-lock.json` digest, `uv.lock` digest, base-image digest, OCI image digest, model digests, selected-check registry version/digest, regulatory-rules registry version/digest, fixture-manifest digest, build ID, Fly deployment ID, and Machine image reference. `/api/v1/meta` exposes the safe subset. The checksummed release manifest, platform readback, clean-browser smoke result, and rollback digest are retained as release evidence.

## `ADR-009`: Fly.io primary deployment with one running Machine

**Decision:** Deploy the take-home image to Fly.io in `iad` on one `shared-cpu-2x` Machine with 2 GiB RAM. Configure `min_machines_running = 1`, disable automatic stop for the release Machine, set request concurrency to soft limit 2 and hard limit 4, and route only after readiness. The application two-POST pre-body gate remains the controlling upload boundary so health and static GETs retain limited headroom.

**Why:** The measured worker peak fits the 2 GiB class and the architecture needs two CPU threads. The selected class has memory margin, is below the 15 USD monthly ceiling at the currently published regional price, supports immutable Machine images, and provides outbound port-policy control. Free Render is disqualified by its documented minute-scale wake path. Railway is no longer primary because its expected always-ready memory cost is higher and its documented Hobby network does not provide the selected outbound port control.

**Stop gate:** Before release, read back region, resource class, Machine count, autostop state, image digest, network policy, current monthly quote, readiness, peak RAM, deployed warmed p95, and five forced-restart cold trials. The warmed fixed set must be 100 percent complete at p95 no more than 5.0 s. The restart set must have p95 below 10 s and never route traffic before readiness. Any mismatch blocks release. Azure Container Apps with at least one replica and enforced outbound policy is the reconsideration path and requires BAIRD reapproval.

## `ADR-010`: Batch after core only

**Decision:** Core domain and result schemas are batch-compatible, but no batch endpoint, ZIP parser, queue, or UI is built until all core gates pass.

**Why:** Batch is high value but not an assignment deliverable and has separate security/performance complexity.

**Consequence:** If delivered, use a separate coordinator over the same verification service and validate the exact 250-row claim.

## `ADR-011`: Immutable evidence, separate reviewer disposition

**Decision:** System findings remain unchanged. A reviewer can add a session-only note/disposition in a separate object.

**Why:** Human judgment is required, but it should not rewrite what the model/rules observed.

## `ADR-012`: No declared external inference dependency and denied common outbound ports

**Decision:** Bundle and hash-check the OCR assets, selected-check registry, and regulatory-rules registry; verify expected registry versions and non-writable runtime state; declare no runtime downloader or analytics/crash SDK; disable supported telemetry; and apply a Fly Machine outbound policy whose sole allowed TCP destination port is 65535. Under that port-level policy, conventional DNS on 53, HTTP on 80, and HTTPS on 443 are denied. The release reads the policy back and probes DNS plus direct-IP HTTP and HTTPS. Any successful probe blocks release.

**Why:** The assignment explicitly warns that cloud ML endpoints can be blocked. It also improves privacy and removes API credentials and per-call cost.

**Consequence:** Model updates happen through reviewed build-time dependency changes, not runtime downloads. Dependency inventory and code review must show no declared external inference, runtime model-download, analytics, or crash-reporting dependency. Network evidence proves only the tested port-level property: outbound traffic on conventional ports 53, 80, and 443 is denied. It does not prove that all outbound traffic is impossible because an application could send arbitrary traffic over the allowed TCP port 65535. The image contains no outbound credentials. Public wording must preserve this distinction.
