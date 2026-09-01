# BAIRD Technical Source Register

**Research date:** 2026-08-31  
**Release source recheck:** 2026-09-01  
**Use:** Current primary-source evidence for product, architecture, engineering, security, testing, and deployment decisions

## Source standard

Technical decisions use official project documentation, official repositories, standards bodies, government sources, and OWASP guidance. Product marketing claims are not treated as benchmark evidence. Version-specific behavior must be rechecked when dependencies are locked and again before release.

## OCR and inference

| ID | Primary source | Current evidence used | Decision consequence |
|---|---|---|---|
| `BTS-001` | [RapidOCR official repository](https://github.com/RapidAI/RapidOCR) | RapidOCR supports local, cross-platform OCR; current installation pairs `rapidocr` with `onnxruntime`; the repository separates the Apache 2.0 engineering project from model copyright and attribution. | Selected self-contained CPU adapter. Exact artifacts, sources, hashes, attribution, and release stops are recorded in `evidence/MODEL_BOM.md`. |
| `BTS-002` | [RapidOCR documentation](https://rapidai.github.io/RapidOCRDocs/main/quickstart/) | Defines current initialization and inference usage. | Adapter must isolate API/version changes. |
| `BTS-003` | [PaddleOCR general OCR pipeline](https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/OCR.html) | Current pipeline supports CPU, ONNX Runtime, multiple OCR model versions, and documented performance modes. | Full PaddleOCR was not measured on the committed workload and is not an automatic fallback. A future selection reopens BAIRD. |
| `BTS-004` | [PaddleOCR installation](https://www.paddleocr.ai/v3.3.0/en/version3.x/installation.html) | Current PaddleOCR 3.x installation requires an inference engine and supports Docker deployment. | Confirms that substituting the full stack changes dependency, image, startup, and resource assumptions. |
| `BTS-005` | [ONNX Runtime license](https://github.com/Microsoft/onnxruntime/blob/main/LICENSE) | ONNX Runtime is MIT licensed. | Compatible with repository distribution subject to notices and dependency scan. |
| `BTS-006` | [ONNX Runtime data and telemetry notice](https://github.com/microsoft/onnxruntime) | The project discloses that usage data may be collected. | Runtime configuration and blocked-egress tests must verify the selected package does not emit undeclared telemetry. |
| `BTS-007` | [ONNX Runtime Web](https://onnxruntime.ai/docs/tutorials/web/) | Browser inference supports WASM and selected accelerated providers; in-browser inference can keep data on device. | Credible fallback architecture, but device variability and model-load cost make it secondary until benchmarked. |
| `BTS-008` | [ONNX Runtime WebGPU](https://onnxruntime.ai/docs/tutorials/web/ep-webgpu.html) | WebGPU is available in current Chrome/Edge but not uniformly across all browsers. | Browser-WebGPU-only inference would narrow the supported environment and needs a WASM fallback. |
| `BTS-009` | [Tesseract.js worker/scheduler guidance](https://github.com/naptha/tesseract.js/blob/master/docs/workers_vs_schedulers.md) | Reusable workers and schedulers can process jobs in browser or Node. | Measured as a comparison. Its recognition timing was fast, but it missed committed fields in multiple scenarios, so it is rejected as the primary adapter. |

## Web and API stack

| ID | Primary source | Current evidence used | Decision consequence |
|---|---|---|---|
| `BTS-010` | [React official repository](https://github.com/facebook/react) | React is MIT licensed and supports component-based interfaces. | Suitable for the stateful evidence workspace and reusable status components. |
| `BTS-011` | [FastAPI official repository](https://github.com/FastAPI/FastAPI) | FastAPI is MIT licensed and current releases support typed Python APIs. | Suitable for Python OCR integration and generated OpenAPI contracts. |
| `BTS-012` | [FastAPI request files](https://fastapi.tiangolo.com/tutorial/request-files/) | Multipart files can be handled as bytes or `UploadFile`. | Upload handling must account for possible spooling and explicitly close/clean all files. |
| `BTS-013` | [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) | FastAPI uses HTTPX/TestClient and pytest-compatible testing. | API and failure paths can be verified without a running external service. |
| `BTS-014` | [OpenCV official repository](https://github.com/opencv/opencv) | Current OpenCV is Apache 2.0 licensed and provides image-processing primitives. | Use only bounded, explainable preprocessing and quality metrics; preserve originals. |

## Testing and accessibility

| ID | Primary source | Current evidence used | Decision consequence |
|---|---|---|---|
| `BTS-015` | [Playwright accessibility testing](https://playwright.dev/docs/accessibility-testing) | Playwright integrates with `@axe-core/playwright`; automated scans catch only part of accessibility conformance and must be paired with manual testing. | Use axe in E2E plus keyboard, zoom, and NVDA evidence. |
| `BTS-016` | [Vitest guide](https://vitest.dev/guide/) | Vitest supports TypeScript unit tests and coverage. | Use for frontend state, schema, and component logic. |
| `BTS-017` | [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | WCAG 2.2 defines current accessibility success criteria. | Core interface targets Level AA within the attested envelope. |

## Upload security and privacy

| ID | Primary source | Current evidence used | Decision consequence |
|---|---|---|---|
| `BTS-018` | [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html) | Use extension allowlists, do not trust MIME headers, validate signatures/content, limit size, generate safe names, keep content outside webroot, and apply defense in depth. | Drives upload validation, no remote URLs, no public serving, safe decode, limits, and cleanup. |
| `BTS-019` | [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html) | ZIP inputs require traversal, compression, and expanded-size checks; image content must be decoded and validated. | Core excludes ZIP. Any batch archive requires a separate security gate. |

## Deployment

| ID | Primary source | Current evidence used | Decision consequence |
|---|---|---|---|
| `BTS-020` | [Railway pricing](https://docs.railway.com/pricing) | Railway uses subscription plus resource usage; current Hobby baseline is listed at 5 USD monthly with usage-based CPU/RAM/egress. | Retained as an unselected comparison. The measured 1.15 GiB direct worker peak and always-ready requirement make its expected cost less favorable than the selected Fly class. |
| `BTS-021` | [Railway Serverless](https://docs.railway.com/deployments/serverless) | Sleeping is optional; when enabled, cold boot can delay or produce a first-request 502. | Serverless/App Sleep must be disabled for the release benchmark. |
| `BTS-022` | [Railway public networking](https://docs.railway.com/networking/public-networking) | Railway can expose an HTTP service through a public domain. | Supports one-origin frontend/API deployment. |
| `BTS-023` | [Railway deployments](https://docs.railway.com/deployments) | Railway supports source/container deployments and deployment history. | Deployment must be tied to the submitted revision and verified after release. |
| `BTS-024` | [Fly.io autostop/autostart](https://fly.io/docs/launch/autostop-autostart/) | Fly can keep a minimum running Machine or stop/suspend idle Machines. | Selected deployment keeps one Machine running and disables the release Machine's automatic stop path. |
| `BTS-025` | [Fly.io health checks](https://fly.io/docs/reference/health-checks/) | Health checks can prevent routing and halt/roll back a bad deployment. | Selected deployment does not receive traffic until model and both registry hashes and versions, read-only governed assets, and representative warmup succeed. |
| `BTS-026` | [Azure Container Apps scaling](https://learn.microsoft.com/en-us/azure/container-apps/scale-app) | Default HTTP scaling can reach zero; minimum replicas at 1 or higher keeps an instance running. | Future stakeholder-aligned host or fallback, with min replicas 1 for the latency contract. |
| `BTS-027` | [Azure Container Apps revisions](https://learn.microsoft.com/en-us/azure/container-apps/revisions) | Revisions are immutable and support readiness-controlled traffic and rollback patterns. | Strong production-direction option but more setup than needed for the take-home. |
| `BTS-028` | [Render free service behavior](https://render.com/docs/free) | Free web services sleep after 15 minutes and may take about one minute to resume. | Free Render is rejected because it directly violates the adoption and evaluator cold-start boundary. |

## Selected deployment and release controls

| ID | Primary source | Current evidence used | Decision consequence |
|---|---|---|---|
| `BTS-031` | [Fly.io pricing](https://fly.io/docs/about/pricing/) | Fly publishes resource-based Machine pricing and notes that shared CPU capacity can burst but is not dedicated. | `shared-cpu-2x` with 2 GiB is the first deployment envelope, not a performance guarantee. Release requires a current `iad` quote and deployed benchmarks under the actual class. |
| `BTS-032` | [Fly.io network policies](https://fly.io/docs/machines/guides-examples/network-policies/) | Directional policy rules create allowlist behavior for covered ports; traffic not allowed by the policy is denied. | The release allows only outbound TCP destination port 65535, reads the policy back, and proves conventional DNS 53 plus direct-IP HTTP 80 and HTTPS 443 denial. This is a port-level claim, not proof that arbitrary outbound application traffic is impossible over the allowed port. |
| `BTS-033` | [Fly Proxy request headers](https://fly.io/docs/networking/request-headers/) | Fly documents `Fly-Client-IP` and forwarding headers added by Fly Proxy. | The Fly profile trusts only `Fly-Client-IP`, ignores client-supplied forwarding chains, and has no additional proxy. Any topology change requires a new trust review. |
| `BTS-034` | [Fly.io logging](https://fly.io/docs/monitoring/logging-overview/) | Fly captures application standard output and standard error and makes recent logs available through its platform. | Application logging uses an allowlist and excludes uploads, extracted text, form values, headers, addresses, and query data. Platform metadata handling is disclosed. |
| `BTS-035` | [Fly.io metrics](https://fly.io/docs/monitoring/metrics/) | Fly exposes platform and application metrics for operational diagnosis. | Release evidence records only aggregate timing/resource measures and excludes label or reference content. |
| `BTS-036` | [PaddleOCR official repository](https://github.com/PaddlePaddle/PaddleOCR) | PaddleOCR publishes its project under Apache License 2.0 and identifies the PP-OCR model family from which the selected converted files originate. | Release notices preserve RapidOCR, PaddleOCR, Baidu model attribution, exact filenames, versions, sources, and hashes. Any provenance or rights change stops release. |
| `BTS-037` | [Starlette request files](https://www.starlette.io/requests/) | Starlette multipart parsing supports bounded file and field counts and uses spooled temporary files for uploads. | A two-request process-global gate rejects excess POSTs before body consumption. Each admission reserves both the multipart parser copy and the controlled request copy, totaling 101,187,584 bytes for two admissions inside a 128 MiB application spool quota. A 3.0 second total body deadline and raw-byte ASGI receive guard run before routing; multipart counts and field sizes are bounded; spooling is isolated, permission-restricted, and cleaned on every terminal path. |

## Regulatory authority carried into BAIRD

| ID | Primary source | Current evidence used | Decision consequence |
|---|---|---|---|
| `BTS-029` | [27 CFR 5.63](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-5/subpart-E/section-5.63) | Defines current distilled-spirits mandatory information, placement, and additional conditional disclosures. | The demo profile must enumerate its subset and cannot claim comprehensive coverage. |
| `BTS-030` | [27 CFR Part 16](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-16) | Sections 16.10, 16.21, and 16.22 define warning applicability, text, placement, capitalization, emphasis, contrast, density, and size. | Canonical rule constants cite both eCFR and TTB guidance; physical checks require evidence limits. |

## Reverification gates

- Preserve the selected dependency versions, exact model hashes, selected-check registry hash/version, and regulatory-rules registry hash/version in the lockfiles or release manifest and the governed BAIRD evidence.
- Record licenses for libraries and bundled model artifacts separately, including model provenance and attribution.
- Generate a dependency inventory and third-party notices before release.
- Recheck Fly price, Machine class, sleep settings, network policy, resource limits, and `iad` availability immediately before deployment.
- Recheck TTB and eCFR sources immediately before the final fixture manifest and release.

The 2026-09-01 release recheck confirmed the official TTB health-warning guidance last updated 2025-11-19, the official TTB mandatory distilled-spirits checklist last updated 2026-05-27, and 27 CFR Part 16 displayed current through 2026-08-28. No selected-profile rule change was required.
