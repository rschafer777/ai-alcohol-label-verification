# Ideation to Realization Architecture and Engineering Specification

Document control ID: LV-I2R-001  
Revision: 1.0  
Date: 2026-08-31  
Status: Draft for combined I2R and FRD review

As-built precedence: `09_I2R_AS_BUILT_SECURITY_RUNTIME_ADDENDUM.md` controls when an implementation mechanism differs from this design-stage record.
Authority: BAIRD Revision 2.2, unanimous CLEAR

## 1. Purpose

This document selects the architecture and engineering needed to implement the 31 approved BAIRD requirements. It answers every `BQ-NNN` question, establishes component and dependency boundaries, defines how data enters, moves, is processed, is returned, and is removed, and supplies the technical basis for the FRD and Build Instructions.

## 2. Product architecture decision

Build LabelVerify as a same-origin modular monolith:

- React 19.2, strict TypeScript, and Vite 8 for the browser interface;
- Python 3.12, FastAPI, Pydantic, and Uvicorn for the HTTP and orchestration layer;
- RapidOCR 3.4.2 with ONNX Runtime 1.22.1 CPU for bundled local text extraction;
- Pillow and OpenCV headless for bounded image decode and preprocessing;
- deterministic Python modules for candidate location, parsing, comparison, warning rules, and aggregation;
- one synchronous verification API and one long-lived killable OCR child process;
- no application database, object store, durable queue, user account, or server session;
- one multi-stage OCI image containing the built UI, API, rules, and hash-verified OCR assets;
- Fly.io as the planned public host, using one always-running `shared-cpu-2x` Machine with 2 GiB RAM in the evaluator region, subject to deployment readback and performance proof.

This shape is appropriate for a take-home because it minimizes operational surface, provides one public URL, keeps inference independent of outbound ML endpoints, and still enforces clean internal module contracts.

## 3. System context

```text
Compliance agent
      |
      | HTTPS, same origin
      v
LabelVerify browser UI
      |
      | multipart reference JSON plus 1 to 6 images
      v
FastAPI boundary and upload guard
      |
      v
Verification orchestrator
      |
      +-> image decode and bounded preprocessing
      +-> local OCR worker
      +-> candidate location and parsing
      +-> deterministic comparison and warning rules
      +-> submission aggregation
      |
      v
Typed evidence-linked result returned to browser

No COLA connection
No runtime model download
No application database
No required external inference endpoint
```

## 4. Component model

| Component | Responsibility | Dependency rule |
|---|---|---|
| `C-001` App shell | Header, prototype notice, routing state, global status | Uses UI features only |
| `C-002` Reference form | Typed reference values and conditional imported fields | No comparison logic |
| `C-003` Panel intake | File picker, drag/drop, preview, reorder, remove, client validation | No OCR logic |
| `C-004` Verification workspace | Processing, result table, evidence selection, recovery, start-over | Renders server result without redefining aggregation |
| `C-005` Typed API client | Multipart request, cancellation, typed response and error mapping, timing | No business rules |
| `C-006` HTTP/API boundary | Routes, request IDs, public errors, schema validation | No field comparison |
| `C-007` Upload guard | Admission, request limits, multipart limits, signature sniffing, spool accounting, cleanup | Parent performs no full image decode |
| `C-008` Orchestrator | Ordered pipeline, stage timing, all-or-nothing result delivery | Calls ports, does not implement their rules |
| `C-009` Imaging | Full decode, decoded-pixel limits, EXIF orientation, quality signals, bounded derived images, coordinate transforms inside the supervised child | Never runs as an unkillable parent task or assigns legal outcome |
| `C-010` Extraction port and RapidOCR adapter | Own the killable child lifecycle for imaging, OCR, candidates, policies, aggregation, model readiness, typed completion, and typed errors | Reference-blind extraction and safe supervisor ownership |
| `C-011` Candidate locator | Observed field candidates, ambiguity alternatives, evidence references | Expected values enter only after candidate generation |
| `C-012` Comparison policies | Per-field parsing, canonicalization, comparison, reason codes | Pure deterministic functions |
| `C-013` Regulatory registry | Warning text, applicability, sources, version, capability | No runtime source retrieval |
| `C-014` Aggregator | Field-to-submission precedence and complete-check invariant | Pure deterministic function |
| `C-015` Security and observability | Rate/concurrency controls, headers, content-free logs, health/readiness, metrics | Cannot store user content |
| `C-016` Fixture and validation harness | Synthetic fixtures, independent oracle, holdout, mutation, performance runs | Never imported by production logic |

## 5. Dependency direction

`UI -> API boundary -> orchestrator -> ports -> deterministic domain`

The deterministic domain contains contracts, parsers, comparison policies, rule registry, and aggregation. It does not import FastAPI, React, OCR libraries, file handles, environment configuration, or fixture expected results. The RapidOCR implementation sits behind an extraction port so a future adapter can be substituted without changing field rules or the UI result contract.

## 6. End-to-end workflow

1. The user opens the public same-origin app and sees the unofficial-prototype and synthetic-data notice.
2. The user selects Try sample or enters a distilled-spirits reference record.
3. The user adds 1 to 6 JPEG, PNG, or WebP label panels.
4. Client checks provide immediate required-field and obvious file feedback.
5. Verify creates one multipart request containing one JSON reference part and the selected images.
6. The API admits or rejects the request before reading the body, enforces the total upload deadline and multipart limits, and validates actual file content.
7. Valid request content is copied into a request-scoped controlled workspace. No durable record is created.
8. The supervisor passes file paths and the reference record to one killable child job.
9. Inside the child, images are fully decoded sequentially, decoded-pixel limits and quality signals are enforced, and bounded OCR views are derived while originals remain available as evidence.
10. The child obtains OCR tokens, reading order, confidence provenance, and polygons.
11. Candidate logic locates each supported field without using the expected reference value to choose a candidate.
12. Per-field policies compare the observed candidate with the reference or rule registry, and aggregation creates one complete result.
13. The browser renders the complete result, announces it, and lets the reviewer focus each evidence region or ambiguity alternative.
14. The server closes handles and removes request-scoped artifacts on success, error, timeout, cancellation, and shutdown.
15. Refresh or start-over clears the browser state because no case history is stored.

## 7. Selected technology rationale

| Decision | Selected option | Rationale and trade-off |
|---|---|---|
| Browser framework | React 19.2 with strict TypeScript | Well-suited to form, upload, focus, evidence, and multi-state UI. Adds a build step but keeps the interaction model explicit. Official React documentation identifies 19.2 as the current line. |
| Build tool | Vite 8 | Small, fast client build with a static production output. Exact versions are lockfile-pinned because Vite recommends pinning when relying on current behavior. |
| API framework | FastAPI and Pydantic | Typed contracts and direct Python OCR integration. Blocking OCR must remain outside the event loop. |
| OCR | RapidOCR with ONNX Runtime CPU | Local regions and text, no runtime egress, reproducible model hashes, measured warm performance. Larger image and memory footprint than an external API. |
| Rules | Deterministic Python | Explainable and independently testable. Deliberately avoids generative judgment. |
| Storage | Request-scoped files and memory only | Minimizes privacy scope. Refresh loses the result, which is disclosed. |
| API style | Synchronous complete-result POST | Matches the five-second goal and avoids a queue or polling surface. Capacity must be bounded. |
| Deployment | One same-origin OCI service on Fly.io | One artifact and URL, configurable always-running Machine, readiness routing, and current low-cost 2 CPU/2 GiB class. Final cost and configuration require platform readback. |
| Batch | GO for the bounded release extension | The single-submission core passed its gate. A browser-managed sequential coordinator reuses the existing API and supervised OCR worker for 1 to 300 manifest rows without a database, durable queue, ZIP parser, or second verification pipeline. |

Primary technical references:

- [React version policy](https://react.dev/versions)
- [Vite releases](https://vite.dev/releases)
- [RapidOCR quick start](https://rapidai.github.io/RapidOCRDocs/main/quickstart/)
- [FastAPI static files](https://fastapi.tiangolo.com/tutorial/static-files/)
- [Fly.io autostop and minimum running Machines](https://fly.io/docs/launch/autostop-autostart/)
- [Fly.io resource pricing](https://fly.io/docs/about/pricing/)
- [Playwright installation and test runner](https://playwright.dev/docs/intro)

## 8. I2R decisions for all BAIRD questions

| Question | Decision |
|---|---|
| `BQ-001` OCR/vision | RapidOCR and ONNX Runtime CPU, bundled and hash-verified, behind an adapter. No runtime model download. |
| `BQ-002` Preprocessing | EXIF normalization, bounded downscale, optional grayscale/contrast, and bounded deskew. Preserve originals and map polygons back to original coordinates. No generative reconstruction. |
| `BQ-003` Request contract | Typed distilled-spirits record plus 1 to 6 files. JSON reference is no more than 32 KiB. Conditional origin field is required only for imports. |
| `BQ-004` Comparison | Per-field explicit parsers and policies. Case-only brand differences and unproven punctuation route to Review. Numeric units normalize exactly. No universal fuzzy score. |
| `BQ-005` Warning | The 19-row `selected-check-registry-v1.json` makes exact wording, capitalization, heading/body emphasis, continuity, separation, contrast, legibility, and physical-size limitation independent. Physical size is Not verified without reliable scale. |
| `BQ-006` UX | One-page guided entry transitioning to a side-by-side verification workspace, with explicit loading, failure, review, and start-over states. Keyboard and screen-reader behavior are acceptance criteria. |
| `BQ-007` Components and APIs | Same-origin modular monolith with the 16 component contracts above and a versioned `/api/v1` HTTP surface. |
| `BQ-008` Data lifecycle | Request-scoped only, content-free logs, no database, explicit cleanup, no required inference egress. |
| `BQ-009` Limits | 6 files, 4 MiB each, 8 MiB aggregate encoded payload, 8,650,752 raw multipart bytes, 12 MP each, 36 MP cumulative, 20 second body deadline, 30 second server deadline, 35 second browser terminal deadline, 6.25 second worker deadline, one OCR job, and two admitted requests. Cancellation and response races follow LV-I2R-002. |
| `BQ-010` Languages and dependencies | Python 3.12 and TypeScript, exact lockfiles, reviewed licenses, hash-verified models, multi-stage container. |
| `BQ-011` Deployment | Fly.io, one always-running shared-cpu-2x Machine with 2 GiB in the selected region, one container, non-root, readiness-gated routing. Azure Container Apps is the documented fallback if deployment proof fails. |
| `BQ-012` Validation corpus | At least 24 deterministic submissions with 6 sealed holdouts; current architecture evidence uses 37 cases and 74 repeated runs but does not replace the product fixture gate. |
| `BQ-013` Batch | GO. Implement and validate the bounded client coordinator defined in the batch architecture addendum. |
| `BQ-014` Operations | Liveness, fail-closed readiness, safe metadata endpoint, allowlisted stage timings, request IDs, no raw content, immutable release manifest, post-deploy smoke and rollback digest. |

## 9. Performance and feasibility evidence

The retained I2R feasibility slice supports the architecture direction:

| Evidence | Result | Interpretation |
|---|---|---|
| Direct full pipeline | 74 runs, p50 2652.50 ms, p95 3994.82 ms, max 4342.39 ms | Warm local direction meets the five-second requirement |
| Browser-visible pipeline | 74 of 74 complete, p50 2646.80 ms, p95 3963.00 ms, max 4334.10 ms | Full visible result meets the local warm target |
| Correctness | 1,258 field rows, 0 field errors, 0 missing evidence, 0 false clean, 0 false mismatch | Supports deterministic result architecture on the legacy 17-check research corpus; the final 19-check product registry requires new fixture proof |
| Security controls | Parser, raw-body, slow upload, two-copy spool, admission, rate, and recovery probes pass | Selected limits are implementable on the real stack |
| Runtime controls | Timeout, repeated cancellation, abort storm, shutdown, child replacement, and cleanup probes pass | Killable worker design is feasible |
| Cold start | 5 runs, conservative p95 10,949.98 ms | BR-026 is not yet closed; development must optimize startup and deployed restart proof must pass |
| Peak observed process memory | 801,320,960 bytes during cold testing | Supports 2 GiB deployment with margin, subject to deployed readback |

Evidence resides under `docs/baird/evidence` because it was produced before the process correction. It is classified as I2R technical evidence. It is not BAIRD requirements authority.

## 10. Open engineering gates

These do not reopen requirements, but they block release:

- cold-start p95 must improve below 10 seconds;
- deployed warmed p95 and 100 percent completion must pass;
- actual Fly region, size, Machine count, autostop state, cost, image digest, and readiness must be read back;
- exact dependency and model licenses/notices must be shipped;
- final frontend dependency versions must be captured in the lockfile;
- product fixtures and holdouts must be built independently from production logic;
- accessibility, security, clean-checkout, and browser evidence must pass the FRD and DoD.

## 11. Architecture exit criteria

I2R A&E is ready for FRD review when:

1. every `BQ-NNN` has a selected decision;
2. every `BR-NNN` maps to one or more components and an engineering verification path;
3. ingress, processing, egress, storage, cleanup, error, timeout, and recovery behavior are explicit;
4. selected technologies are justified and reproducible;
5. known evidence and open release gates are distinguished honestly;
6. three independent reviewers return CLEAR on the combined I2R A&E and FRD snapshot.
