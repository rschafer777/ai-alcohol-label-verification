# I2R Architecture Decision Record

Document control ID: LV-I2R-004  
Revision: 1.2  
Date: 2026-09-01  
Status: Controlled architecture baseline

| ADR | Decision | Alternatives considered | Consequence and gate |
|---|---|---|---|
| `ADR-001` | Same-origin modular monolith | Microservices, separately hosted SPA/API | Smallest deployable surface; internal module contracts remain mandatory |
| `ADR-002` | React 19.2, strict TypeScript, Vite 8 | Server templates, Next.js | Better multi-state UX and testable components; lockfile and client build required |
| `ADR-003` | Python 3.12, FastAPI, Pydantic, Uvicorn | Node-only backend, .NET | Direct OCR integration and typed API; blocking work isolated from event loop |
| `ADR-004` | RapidOCR 3.4.2 and ONNX Runtime 1.22.1 CPU | Tesseract.js, external vision API | Local reproducible regions and warm performance; larger memory footprint and startup cost |
| `ADR-005` | Deterministic comparison and aggregation | LLM judgment, universal fuzzy matching | Explainable and stable; policies require explicit maintenance |
| `ADR-006` | Request-scoped processing, no database | SQLite, object storage, durable cases | Minimal privacy scope; no history and refresh loses work |
| `ADR-007` | Synchronous complete-result POST with one killable child worker | Async job queue, in-process OCR | Simple five-second flow; strict admission, timeout, and lifecycle controls required |
| `ADR-008` | Multi-stage immutable OCI image | Platform buildpacks, separate frontend deploy | One revision and one rollback artifact; larger image build |
| `ADR-009` | Azure Container Apps Consumption, 2 vCPU/4 GiB, zero to one replicas, two warmed one-thread OCR lanes, OIDC deployment, managed-identity ACR pull limited to platform use, and application-aware HTTP probes | Fly.io, Render, Railway, Azure App Service | Matches the verified Azure handoff and government-cloud trajectory while preserving one same-origin OCI service. The two vCPU allocation matches the two OCR inference lanes without thread oversubscription and is the maximum for the current Consumption-only environment. Scale-to-zero cold latency, effective configuration, FQDN, image digest, identity lifecycle, readiness, and performance require deployment proof. |
| `ADR-010` | Session-only browser-managed batch GO for 1 to 300 applications | Keep batch excluded; add a persistent server queue | Meets the stakeholder peak-season need while reusing the governed single-verification endpoint; total elapsed time scales sequentially and refresh loses the queue |
| `ADR-011` | Immutable machine evidence and separate browser-session reviewer disposition | Reviewer overwrite of findings | Preserves audit clarity; no saved review decision |
| `ADR-012` | No required external inference egress | Cloud OCR as core | Works under restricted network and avoids content transfer; bundled models and startup optimization required |
| `ADR-013` | Reference-blind extraction and candidate selection | Expected-value-guided search | Prevents reference copying and false confidence; ambiguous candidates remain Review |
| `ADR-014` | Versioned selected-check and regulatory registries | Constants scattered through code | Traceable scope and rules; readiness must verify both assets |
| `ADR-015` | Original image remains authoritative evidence | Replace original with enhanced image | Prevents invented visual certainty; coordinate transforms must be maintained |

## Decision change rule

An ADR changes only when development evidence falsifies its feasibility, a dependency or platform constraint changes, or a requirement changes through controlled scope approval. A change updates I2R, the FRD, BI work packages, tests, and the release claim before implementation proceeds.

ADR-009 supersedes the earlier Fly deployment selection after verified Azure resources and an environment-scoped OIDC federation became available. `11_I2R_AZURE_DEPLOYMENT_ADDENDUM.md` is the controlling detailed record.
