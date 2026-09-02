# I2R Data, Interface, Security, and Operations Specification

Document control ID: LV-I2R-002  
Revision: 1.1  
Date: 2026-08-31  
Status: Controlled as-built baseline

As-built precedence: `09_I2R_AS_BUILT_SECURITY_RUNTIME_ADDENDUM.md` and `11_I2R_AZURE_DEPLOYMENT_ADDENDUM.md` control when an implementation mechanism differs from this design-stage record.

## 1. Ingress contract

`POST /api/v1/verifications` accepts `multipart/form-data` containing:

- exactly one `reference` JSON part, maximum 32 KiB;
- 1 to 6 `panels` file parts;
- JPEG, PNG, or WebP content verified by decode and content signature, not extension alone;
- maximum 4 MiB per file;
- maximum 8 MiB aggregate encoded file payload;
- maximum 8,650,752 bytes for the complete multipart request, including boundaries, headers, reference JSON, and file payloads;
- maximum 12 megapixels per source and 36 megapixels per request.

Reference record:

| Field | Type and rule |
|---|---|
| `profileId` | Fixed `distilled_spirits_demo_v1` |
| `caseLabel` | Optional, 80 characters, display only, never logged |
| `brandName` | Required, 1 to 160 characters |
| `classType` | Required, 1 to 240 characters |
| `abvPercent` | Required decimal greater than 0 and at most 100 |
| `proof` | Optional non-negative decimal, checked against ABV when present |
| `netContentsValue` | Required positive decimal |
| `netContentsUnit` | `mL` or `L` |
| `producerNameAddress` | Required multiline text, 1 to 500 characters |
| `isImported` | Required boolean |
| `countryOfOrigin` | Required only when imported, 1 to 80 characters |

Raw request handling:

- exactly one decimal, non-negative `Content-Length` is accepted when present;
- duplicate, signed, non-decimal, or conflicting `Content-Length` is `400 invalid_content_length`;
- `Content-Length` above 8,650,752 is `413 request_too_large` before body consumption;
- missing `Content-Length` is allowed only through streaming count enforcement;
- a body that exceeds its declared length is `400 content_length_mismatch`;
- a stream that exceeds 8,650,752 bytes is `413 request_too_large` immediately;
- simultaneous `Content-Length` and `Transfer-Encoding` is `400 invalid_content_length`;
- aggregate file bytes, per-file bytes, and complete raw request bytes are independently enforced.

## 2. API surface

| Method and path | Purpose | Success |
|---|---|---|
| `GET /health/live` | Process liveness | `200` with no model invocation |
| `GET /health/ready` | Model, rule, worker, and governed-asset readiness | `200` only after exact checks and representative warmup |
| `GET /api/v1/meta` | Safe build, profile, model, rule, and limit metadata | `200`, no secrets or local paths |
| `GET /api/v1/samples/distilled-spirits-v1` | Built-in synthetic sample manifest and static asset links | `200` |
| `POST /api/v1/verifications` | Complete synchronous verification | `200` complete result or typed result-free error |

Public error contract:

```json
{
  "requestId": "opaque-id",
  "code": "stable_machine_code",
  "message": "Plain-language explanation",
  "fieldOrPanel": "optional locator",
  "retryable": true,
  "nextAction": "What the user can do next"
}
```

All allowed codes, statuses, retryability, locator rules, action classes, and logging classes are normative in LV-I2R-007. The API and UI generate their typed mappings from that registry or an equivalent single source.

No stack trace, raw label text, file path, model internals, or secret appears in an error.

## 3. Verification result contract

```text
VerificationResult
  requestId
  buildId
  profileId
  profileVersion
  modelIdentity
  ruleSources[]
  serverDurationMs
  stageTimings
  panels[]
    panelId
    originalDimensions
    qualitySignals
    coverageState
  evidence[]
    evidenceId
    panelId
    polygonOriginalPixels[4]
    sourceView
    transformId
    textSnippet
    confidenceProvenance
  checks[]
    checkId
    label
    applicable
    referenceDisplay
    observedDisplay
    state
    reasonCode
    reasonText
    evidenceRef or null
    alternatives[] { value, evidenceRef }
    capability
    policyVersion
  limitations[]
  summary
```

Every applicable registry check appears once. The browser must render the server summary and must not compute a competing summary.

## 4. State and aggregation rules

Field states:

- Match: sufficient evidence and exact or explicitly safe equivalence;
- Mismatch: sufficient evidence shows a definite difference;
- Review: evidence exists but ambiguity, heuristic presentation, or judgment remains;
- Not verified: applicable evidence is absent, unreadable, unsupported, or not measurable.

Summary precedence:

1. Any Mismatch means Differences detected.
2. Otherwise any Review or Not verified means Review needed.
3. No differences found in checked fields is allowed only when every applicable selected check is Match.

Reviewer notes or disposition exist only in browser session state and never modify machine findings.

## 5. Data movement and lifecycle

| Stage | Data | Location | Retention | Cleanup owner |
|---|---|---|---|---|
| Browser entry | Reference values and selected files | Browser memory and file handles | Current page session | Browser on remove, reset, refresh, or close |
| Multipart intake | Raw request chunks | Framework spool under application-controlled directory | Request duration only | Upload guard |
| Controlled request | Validated file copies and reference object | Per-request private directory and process memory | Worker ownership only | Worker supervisor after confirmed completion or termination |
| Imaging | Decoded arrays and derived OCR views | Supervised child memory only | Child job only | Worker supervisor after child exit or termination |
| OCR and rules | Tokens, boxes, confidence provenance, candidates, field results | Supervised child memory, then typed result in parent memory | Current request only | Worker supervisor, then parent response finalizer |
| Result | Typed response | Parent memory then browser memory | Response and current page session | Parent after send; browser on reset/refresh |
| Logs | Request ID, status, durations, counters, build ID | Standard output/platform logs | Platform operational policy | Platform retention configuration |

Prohibited in logs: form values, OCR text, image bytes, filenames, evidence crops, reviewer notes, local paths, and IP addresses beyond a non-reversible in-memory limiter digest.

## 6. Request and runtime controls

| Control | Selected value |
|---|---|
| Verification admissions | 2 before body consumption |
| OCR execution | 1 at a time |
| Complete raw request ceiling | 8,650,752 bytes |
| Per-file / aggregate file payload | 4,194,304 / 8,388,608 bytes |
| Total request-body deadline | 20.0 seconds from pre-body admission; activity does not reset it |
| Worker acquisition deadline | 200 ms |
| Worker execution safety deadline | 9 seconds |
| Server admission-to-response safety deadline | 30.0 seconds, including body, validation, decode, queue, inference, serialization, and response start |
| Browser Verify-to-terminal safety deadline | 35.0 seconds, including client validation, upload, server work, transfer, render, and announcement |
| Per-client start policy | 20 starts per 10 minutes and 1 active request |
| Global start policy | 30 starts per minute |
| Limiter table | Maximum 4,096 keys, 15 minute inactive TTL |
| Per-admission two-copy reservation | 17,301,504 bytes |
| Two-admission reservation | 34,603,008 bytes |
| Application spool quota | 50,331,648 bytes |

The parser and lifecycle mechanisms were proven in the retained real-stack control harness at a larger research envelope. The reduced production byte envelope, 20 second body deadline, 30 second server deadline, and shaped-network behavior require product tests. They are implementation limits, not claims about production federal capacity.

Performance profiles are separate from maximum accepted input:

- normal five-second benchmark: at most 1 MiB aggregate encoded input, at most 6 MP cumulative decoded pixels, 1 to 3 panels, at least 20 Mbps sustained upstream, at most 80 ms round-trip time to the selected region;
- accepted maximum: up to the limits above, with a bounded terminal outcome but no five-second claim;
- shaped-network proof: representative one-panel, multi-panel, and near-8-MiB requests at 5 Mbps upstream and 100 ms round-trip time must upload within 20 seconds and reach a terminal state within 35 seconds;
- deployed evidence records actual client region, server region, bytes, pixels, panels, uplink shaping, round-trip time, and every duration.

## 7. Worker lifecycle

1. The parent starts one OCR child and verifies model and registry hashes, versions, non-writable governed assets, and representative warmup.
2. Readiness remains false until all checks pass.
3. After parent schema, byte, and signature validation, one admitted request acquires the worker. A second may wait up to 200 ms. Later requests are rejected before body read.
4. A separate supervisor owns request files and worker capacity independently of caller cancellation. The child opens and fully decodes the files, enforces decoded-pixel limits, preprocesses, extracts, locates candidates, compares, and aggregates.
5. Client disconnect suppresses response delivery but does not release capacity or delete files while the worker may still read them.
6. At 9 seconds, including a stalled or malicious decode, the parent terminates and joins the child, clears readiness, returns a result-free 504 when delivery is possible, and cleans only after confirmed exit.
7. A background replacement initializes and warms. New verification starts return 503 until readiness passes.
8. Shutdown stops intake, drains supervisors through the deadline, terminates and joins any remaining child, deletes request directories, and confirms zero reservations.

## 8. Total deadline and cancellation contract

- The server admission clock starts before any request body byte is read.
- The non-resetting 20 second body deadline is nested inside the non-resetting 30 second server deadline.
- Parent-side schema, byte, signature, and multipart validation remains inside the 30 second server deadline and performs no full image decode.
- Full image decode, decoded-pixel enforcement, preprocessing, OCR, candidate location, comparison, and aggregation execute as one supervised child job. Worker acquisition is at most 200 ms and child execution is at most 9 seconds, both inside the 30 second server deadline.
- Serialization and response start must occur before the 30 second deadline. If not, the server returns `504 request_deadline_exceeded` when delivery remains possible.
- The browser clock starts at Verify activation. It aborts the fetch and shows `client_deadline_exceeded` at 35 seconds if no complete result or typed error has rendered and been announced.
- A visible Cancel verification action is available throughout client validation, upload, and processing. Activation aborts client work and enters Cancelled within 1 second.
- A client abort or disconnect suppresses result delivery only. The server supervisor retains files and capacity until worker completion or termination and then cleans them.
- Timeout, disconnect, cancellation, and shutdown cannot delete files, release the worker slot, or release spool reservations until the child is confirmed exited. A real decoder-stall test must prove termination, restart, recovery, and zero final handles, request directories, reservations, owned jobs, and child leaks.
- If response completion and client abort race, the first browser terminal event wins. A response received after the abort flag is set is ignored and never rendered.
- User cancellation and the 35 second client deadline are reported separately from valid-result performance and are never counted as successful verification.
- Controlled stalls test every asynchronous wait boundary: upload, parent validation, worker queue, the single supervised child job that contains decode through inference, response transfer, and the browser request deadline.
- Client validation, result rendering, focus placement, and live-region output are synchronous browser commit paths, not independent wait boundaries. Their tests must prove immediate client rejection or one deterministic complete commit with the expected focus and live-region content.

## 9. Threat controls

| Threat | Control and proof |
|---|---|
| Oversize or deceptive upload | Raw byte limit, multipart count/size limits, content sniff, decoded-pixel limits, result-free errors before OCR |
| Slow request body | Non-resetting 20 second total body deadline, exact raw counter, explicit partial spool closure |
| Decompression/resource abuse | Sequential decode, per-image and cumulative pixel limits, bounded working canvas |
| Capacity exhaustion | Pre-body admission, one OCR job, short worker queue, rate limits, bounded key table |
| Path traversal | No client filename used as a path; generated private request directory and internal names |
| Data leakage | No persistence, no content logs, no analytics/crash SDK, original neutral sample-only notice |
| External inference failure | No required external inference dependency; blocked-egress test still proves bounded safe behavior |
| Stale or substituted model/rules | Hash/version/read-only readiness checks and immutable image manifest |
| Reference leakage into extraction | Extraction and candidate selection are reference-blind; expected values enter only at comparison |
| False clean | Complete-check invariant plus independent negative fixtures and holdouts |
| Cross-origin abuse | Same-origin UI, exact Host and Origin allowlists for mutation routes, no CORS grant, secure headers, no cookies or credentials |
| Supply-chain drift | Exact Python and npm lockfiles, model BOM, license notices, dependency and image scans |

## 10. Public edge identity and response security

Production client identity is selected explicitly by deployment configuration:

- Uvicorn proxy-header trust is disabled. The application does not allow Uvicorn to rewrite the ASGI peer from forwarding headers.
- Azure Container Apps mode requires exactly one `X-Forwarded-For` header and uses only its rightmost comma-separated item. Azure documents that it appends the address it observed as that rightmost value. Earlier items are treated as untrusted caller or intermediary input and are ignored.
- Missing, duplicate, empty, malformed, non-ASCII, or zone-qualified Azure identity values return `400 invalid_client_identity` before body consumption.
- Fly mode remains implemented for portability and accepts exactly one parseable `Fly-Client-IP` value. Missing, duplicate, comma-delimited, malformed, or zone-qualified values fail closed.
- An unknown production identity source fails closed. Direct local/test mode ignores forwarding headers and uses the ASGI peer address.
- The normalized compressed address is HMAC-SHA256 digested with a random per-process secret and the raw address is discarded. Logs and limiter keys contain only the digest.

Production request validation:

- allowed Host values come from one required deployment variable and must exactly match after lowercase IDNA normalization and default-port removal;
- missing, duplicate, malformed, or disallowed Host returns `400 invalid_host`;
- `POST /api/v1/verifications` requires exactly one Origin equal to `https://<allowed-host>` in production;
- missing, duplicate, `null`, malformed, or different Origin returns `403 origin_not_allowed`;
- no credentialed CORS response is emitted and cross-origin preflight to the mutation route is rejected;
- direct, proxied, spoofed, duplicate, malformed, and missing-header cases are mandatory tests.

Response headers:

- verification successes and every API error: `Cache-Control: no-store, private` and `Pragma: no-cache`;
- all HTML/API responses: `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, `X-Frame-Options: DENY`, `Cross-Origin-Opener-Policy: same-origin`, and `Permissions-Policy: camera=(), microphone=(), geolocation=()`;
- HTML: `Content-Security-Policy: default-src 'self'; img-src 'self' blob:; connect-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'`;
- production HTTPS: `Strict-Transport-Security: max-age=31536000; includeSubDomains`;
- static fingerprinted assets may use immutable caching because they contain no user data.

## 11. Deployment and operations

- Multi-stage build: Node builds static UI; Python runtime receives only production Python dependencies, UI output, rules, sample assets, and OCR models.
- Runtime user is non-root with a read-only application filesystem and one writable request spool.
- Static UI and API share one origin.
- Azure Container Apps Consumption runs one 2 vCPU, 4 GiB non-root container with zero to one replicas and single-revision ingress. The two vCPU allocation matches the two governed OCR lanes. Each lane uses one ONNX Runtime intra-operation thread, and both lanes complete representative warmup before readiness, so the first two-panel request does not enter an unwarmed lane or oversubscribe the Consumption-only environment's two vCPU maximum.
- Startup and liveness probes call `/health/live`; readiness calls `/health/ready`. Each internal HTTP probe supplies the governed Host value so production Host validation remains enabled.
- The ACR pull identity is available to the platform for image pull but is configured with identity lifecycle `None`, so application code cannot obtain its access token.
- GitHub Actions authenticates through the environment-scoped OIDC federation and deploys an immutable image digest. No client secret, registry password, or publishing profile is used.
- The release manifest records source revision, lockfile hashes, base image digest, OCI digest, model hashes, rule/profile hashes, fixture manifest hash, build ID, deployment ID, and rollback image digest.
- Scale to zero is a demo cost trade-off and does not waive the cold-start performance gate.

## 12. Observability

Allowed measurements:

- request ID;
- build and profile version;
- status and stable error code;
- input panel count and aggregate byte/pixel buckets, not filenames or values;
- stage durations;
- worker PID generation, readiness, timeout, restart, and queue counters;
- admission, reservation, cleanup, and rate-limit counters;
- process RSS and health status.

Every log call uses an allowlisted structured schema. Tests fail if prohibited content is present.

## 13. Verification obligations

- raw ASGI and HTTP boundary tests for missing, duplicate, invalid, conflicting, understated, and oversized content length, exact 8,650,752 byte raw ceiling, multipart part counts, per-file and aggregate limits;
- two concurrent slow multipart clients plus a third pre-body rejection under the 20 second body deadline;
- two concurrent near-limit multipart requests and zero final spool usage;
- worker hang, timeout, replacement, readiness, recovery, repeated cancellation, disconnect storm, and shutdown ownership;
- egress-blocked core or bounded non-clean outcome;
- normal and shaped-network upload/terminal timing at the declared network profiles;
- Azure rightmost forwarded identity, Fly portability identity, direct-mode isolation, spoofed/duplicate/malformed forwarding header, Host, Origin, security header, and no-store tests;
- secret, dependency, license, container, and content-log scans;
- deployed configuration readback and clean-browser smoke;
- all acceptance tests defined in the FRD.
