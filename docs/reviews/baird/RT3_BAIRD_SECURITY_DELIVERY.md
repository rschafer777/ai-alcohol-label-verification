# BAIRD Red Team 3: Security, Privacy, Delivery, and Traceability

**Review role:** Independent security, privacy, deployment, delivery, and traceability skeptic  
**Review date:** 2026-08-31  
**Reviewed stage:** BAIRD  
**Intake basis:** CLEAR, 3 of 3 Intake reviewers  
**Snapshot:** `codex-security-snapshot/v1:sha256:6eb4777823d30c4bf90220d68f04b5b44f983db4c22c7c969a4d7ca17b09c49b`  
**Verdict:** `REWORK_REQUIRED`

## 1. Binary gate decision

BAIRD is not ready to advance to I2R on this revision. The package has a strong architectural direction, but eight material findings remain. One is High severity because the selected OCR distribution cannot be approved until the exact bundled model artifacts and their redistribution rights are known. Seven Medium findings leave the public upload boundary, cancellation ownership, client identity, egress claim, hosting privacy contract, release provenance, and downstream traceability underspecified.

This verdict does not reject the selected product direction or modular-monolith architecture. It blocks the handoff until the architecture records and I2R stop conditions make the relevant claims executable and falsifiable.

## 2. Scope and method

I reviewed:

- the complete CLEAR Intake package and Intake gate result;
- every current file in `docs/baird`;
- source, decision, component, threat, gate, and technical-source identifier coverage;
- the public upload path from hosting edge through multipart parsing, decoding, OCR, response, cleanup, and logs;
- the synchronous concurrency and cancellation model;
- same-origin, CORS, CSRF, proxy, client identity, and rate-limit assumptions;
- container, dependency, model, and release supply chain controls;
- Railway, Fly.io, and Azure Container Apps deployment claims;
- batch boundaries and archive controls;
- BAIRD to I2R handoff completeness.

The review used a standard security scan with ten closed review surfaces. Worker slots were unavailable for additional internal parallel investigators because the requested three BAIRD red teams were already running concurrently. I therefore performed the baseline and attack passes sequentially with no scope reduction.

## 3. Attack cases and coverage

| Attack case | Evidence challenged | Result |
|---|---|---|
| Send a chunked or understated multipart body above the documented total | Pre-parser body limit and upload spooling | Finding `BAIRD-RT3-F001` |
| Send many legal multipart parts or large file parts before endpoint validation | Parser CPU, memory, and temporary storage | Finding `BAIRD-RT3-F001` |
| Start OCR, disconnect, and repeat while blocking work continues | Semaphore ownership, timeout, cleanup, and CPU capacity | Finding `BAIRD-RT3-F002` |
| Spoof forwarding headers or route all users through one edge address | Per-client concurrency and rate-limit identity | Finding `BAIRD-RT3-F003` |
| Send cross-site multipart POSTs with missing, `null`, or forged Origin | Same-origin and CSRF policy | Finding `BAIRD-RT3-F003` |
| Make a dependency or compromised process call an external HTTPS endpoint | No-runtime-egress claim on Railway Hobby | Finding `BAIRD-RT3-F004` |
| Build an image with a model whose code license and model rights differ | Public repository and container redistribution | Finding `BAIRD-RT3-F005` |
| Inspect edge logs and browser/proxy caches after a verification | Hosting metadata retention and response caching | Finding `BAIRD-RT3-F006` |
| Deploy from a mutable tag or an unbound source build | Submitted revision versus deployed artifact proof | Finding `BAIRD-RT3-F007` |
| Walk `SRC` to ADR, gate, FRD section, test, and owner | Source and control traceability | Finding `BAIRD-RT3-F008` |
| Attempt ZIP traversal, nested archives, entry-count abuse, or expansion bombs | Batch security gate | Covered correctly: ZIP is excluded from core and separately gated |
| Start a sleeping host or route before model readiness | Host and readiness choices | Covered correctly at BAIRD level, subject to later measured proof |
| Persist content through a mounted volume or privileged container | Runtime/container boundary | Covered correctly at BAIRD level, subject to implementation evidence |

## 4. Primary-source verification

The following official-source checks materially affect this verdict:

- Current [Starlette request documentation](https://www.starlette.io/requests/) states that uploaded files use `SpooledTemporaryFile`; `max_part_size` limits non-file fields, not uploaded files. It directs applications to a total body limit for files and multipart overhead.
- Current [Starlette routing documentation](https://www.starlette.io/routing/) states that `max_body_size` defaults to unlimited, counts actual received bytes, includes multipart overhead, and does not trust `Content-Length` as the enforcement mechanism. The feature arrived in [Starlette 1.6.0](https://www.starlette.io/release-notes/), so the dependency version and fallback implementation matter.
- Python 3.12 [concurrent.futures documentation](https://docs.python.org/3.12/library/concurrent.futures.html) states that a running future cannot be cancelled. Discarding a late result is therefore not the same as stopping a running OCR thread.
- Railway documents a platform-supplied [`X-Real-IP`](https://docs.railway.com/networking/public-networking/specs-and-limits) header, while Azure documents that only the rightmost [`X-Forwarded-For`](https://learn.microsoft.com/en-us/Azure/container-apps/ingress-overview) value is supplied by Azure and other values require validation. A portable rate limiter cannot leave the trusted-proxy contract implicit.
- Railway's [outbound networking documentation](https://docs.railway.com/networking/outbound-networking) describes working outbound IPv4 and HTTPS connectivity on Hobby. It does not establish a deny-all runtime egress control for the proposed service.
- Railway's [logs documentation](https://docs.railway.com/observability/logs) shows HTTP attributes including source IP and user agent and a seven-day Hobby retention period. These are part of the prototype's actual data path even when the application log allowlist is clean.
- The official [RapidOCR README](https://github.com/RapidAI/RapidOCR/blob/main/README.md?plain=1) states separately that OCR model copyright belongs to Baidu while the engineering project uses Apache 2.0. A library license alone does not settle the redistribution terms for bundled model files.
- Microsoft documents that Azure Container Apps can enforce outbound policy through [UDR and Azure Firewall](https://learn.microsoft.com/en-us/azure/container-apps/user-defined-routes). This is a viable fallback if enforced no-egress is a hard requirement rather than a software behavior claim.

## 5. Findings

### `BAIRD-RT3-F001`: The upload limit is not bound to a pre-parser enforcement contract

**Severity:** Medium  
**Affected evidence:** `SECURITY_DATA_FLOW.md:51-71`, `SECURITY_DATA_FLOW.md:79-89`, `ENGINEERING_BLUEPRINT.md:221-229`, `TECHNICAL_SOURCE_REGISTER.md:30`, `I2R_HANDOFF.md:29-47`, `I2R_HANDOFF.md:74-87`

The package defines useful per-image, total encoded, decoded-pixel, format, and count limits. It does not bind the 24 MB total to a framework version or an ASGI/edge mechanism that enforces raw body bytes before multipart parsing and file spooling. The phrase "where the platform supports it" leaves the first public resource boundary conditional. The cumulative decoded-pixel limit is also still undefined.

An attacker can omit or understate `Content-Length`, stream multipart data for several minutes, or exploit file spooling before handler-level validation. A handler check after FastAPI has constructed `UploadFile` objects is too late to prove the claimed byte and temporary-storage boundary.

**Required remediation:**

1. Select and pin a Starlette/FastAPI version with an application or route raw-body limit, or specify a custom ASGI receive wrapper that counts actual bytes.
2. Define a total body maximum that includes multipart overhead, plus maximum files, fields, non-file part size, file bytes, and exact cumulative decoded pixels.
3. Specify behavior for chunked, missing, malformed, and understated `Content-Length` requests.
4. Define spool threshold, temporary directory, permissions, quota, and close/delete ownership.
5. Add an I2R stop condition requiring over-limit rejection before endpoint parsing/decode and filesystem proof for each failure path.

**Closure proof:** Tests show 413 before handler/decode invocation for oversized fixed-length, understated, and streaming bodies; part-count and cumulative-pixel attacks are bounded; temporary storage returns to baseline.

### `BAIRD-RT3-F002`: Timeout and disconnect do not own the lifecycle of blocking OCR work

**Severity:** Medium  
**Affected evidence:** `ARCHITECTURE_DECISIONS.md:38-44`, `ARCHITECTURE_DECISIONS.md:68-74`, `ENGINEERING_BLUEPRINT.md:244-253`, `ENGINEERING_BLUEPRINT.md:337-346`, `SECURITY_DATA_FLOW.md:98-111`, `SECURITY_DATA_FLOW.md:166-178`

The design runs decode/OCR in a bounded executor, uses a global semaphore, discards late results, and requires cleanup on timeout or disconnect. It does not say whether the semaphore and input artifacts remain owned until the underlying blocking callable actually exits. A running executor future cannot be cancelled. If request cancellation releases capacity or deletes an input while the worker still runs, repeated aborts can create hidden CPU work, exceed the claimed concurrency limit, or race cleanup.

**Required remediation:**

1. Define the underlying job as the owner of its semaphore slot, model call, and input artifacts until actual completion, regardless of HTTP request state.
2. State that request timeout discards delivery but cannot release worker capacity early.
3. Decide whether bounded threads plus a proven hard inference bound are sufficient or whether a killable worker process is required.
4. Define graceful shutdown behavior for active OCR work and maximum drain time.
5. Add timeout and disconnect storm tests that inspect true executor activity, semaphore count, CPU saturation, and temp cleanup after workers finish.

**Closure proof:** Under repeated start-and-abort traffic, actual running OCR jobs never exceed the configured global limit, no capacity is released early, all artifacts are removed after the worker exits, and the service recovers without restart.

### `BAIRD-RT3-F003`: Client identity and origin enforcement are not portable or spoof-resistant

**Severity:** Medium  
**Affected evidence:** `SECURITY_DATA_FLOW.md:86`, `SECURITY_DATA_FLOW.md:93-111`, `BAIRD_ASSESSMENT.md:119-136`, `I2R_HANDOFF.md:49-60`

The design commits to per-IP limits, same-origin requests, restrictive CORS, and an Origin check. It does not define the trusted proxy chain or which client-address signal is authoritative for Railway, Fly.io, Azure, local Docker, and tests. Trusting arbitrary forwarding headers allows rate-limit bypass. Ignoring them can collapse all users behind an edge address. The Origin policy also lacks an exact decision table for allowed origin, wrong origin, missing Origin, `null` Origin, Host mismatch, and non-browser clients.

**Required remediation:**

1. Define a host-specific client identity resolver and the exact trusted proxy boundary.
2. Ignore or reject client-supplied forwarding values outside that boundary and document direct/local behavior.
3. Define the POST Origin/Host decision table, including missing and `null` Origin.
4. Keep CORS disabled or explicitly allow only the deployed origin with no credentialed cross-origin requests.
5. Document process-local rate-limit reset and single-replica limits without overstating distributed enforcement.

**Closure proof:** Spoofed forwarding headers do not change the limiter key; legitimate clients resolve correctly on the selected host; cross-site and `null` Origin POSTs fail; the deployed same-origin UI succeeds; raw client addresses do not enter application logs.

### `BAIRD-RT3-F004`: The no-runtime-egress claim exceeds the preferred host's stated control

**Severity:** Medium  
**Affected evidence:** `ARCHITECTURE_DECISIONS.md:106-112`, `BAIRD_ASSESSMENT.md:136-149`, `BAIRD_ASSESSMENT.md:170-181`, `SECURITY_DATA_FLOW.md:90-91`, `SECURITY_DATA_FLOW.md:125-139`, `I2R_HANDOFF.md:74-87`

`ADR-012` says "No external inference or runtime egress," but the selected Railway Hobby architecture permits ordinary outbound connectivity. A blocked-egress test proves that the application can operate without egress. It does not prove that the deployed runtime cannot egress if a dependency, telemetry path, or compromised process attempts it.

**Required remediation:**

1. Choose one truthful contract: either "no intended runtime network dependency" with detection evidence, or enforced deny-by-default egress.
2. If Railway remains selected, disclose that platform outbound connectivity exists, disable telemetry, prevent model download, and require DNS/network capture proving zero expected calls during startup and requests.
3. If enforced no-egress is required, select a host/network configuration that can enforce it, then rerun the cost, latency, and complexity matrix.
4. Add selected-platform configuration readback and egress evidence to I2R and release gates.

**Closure proof:** Architecture wording, privacy notice, selected host, threat control, test, and README all state the same egress property, and the evidence proves exactly that property.

### `BAIRD-RT3-F005`: Exact OCR model rights and provenance are unresolved after architecture selection

**Severity:** High  
**Affected evidence:** `ARCHITECTURE_DECISIONS.md:46-52`, `ARCHITECTURE_DECISIONS.md:76-82`, `ARCHITECTURE_DECISIONS.md:106-112`, `TECHNICAL_SOURCE_REGISTER.md:14-22`, `TECHNICAL_SOURCE_REGISTER.md:70-75`, `ENGINEERING_BLUEPRINT.md:321-335`, `I2R_HANDOFF.md:29-47`, `I2R_HANDOFF.md:74-87`

The selected architecture requires OCR models to be bundled into a public release container. The source register defers model license review until release, but the official project distinguishes model copyright from the engineering repository license. The exact detector, classifier, and recognizer artifacts are not named, and their source, version, license, notice obligations, redistribution rights, hashes, and expected image paths are absent.

This is architecture-load-bearing. If the intended artifacts cannot be redistributed in the public image or repository, the selected offline packaging approach must change. Deferring that answer to the release gate risks invalidating the architecture after implementation.

**Required remediation:**

1. Name every model file selected for detector, classifier if used, and recognizer.
2. Record upstream source, version, copyright holder, license or redistribution terms, required notices, SHA-256, and expected package/container path.
3. Decide whether model files live in Git, are fetched only during a verified build, or arrive through another reproducible mechanism.
4. Prove offline container startup with runtime downloads disabled and fail closed on a missing or wrong hash.
5. Add a BAIRD stop gate: if rights or redistribution terms are unresolved, select a legally clear alternative before I2R approves the implementation contract.

**Closure proof:** A reviewed model bill of materials and third-party notice plan cover the exact shipped artifacts, their hashes match the built image, and counsel-level uncertainty is not hidden behind the library's Apache license.

### `BAIRD-RT3-F006`: Hosting metadata and response caching are missing from the privacy contract

**Severity:** Medium  
**Affected evidence:** `SECURITY_DATA_FLOW.md:26-45`, `SECURITY_DATA_FLOW.md:113-123`, `SECURITY_DATA_FLOW.md:141-164`, `BAIRD_ASSESSMENT.md:136-149`, `I2R_HANDOFF.md:29-47`

The application logging allowlist is strong, and the security document correctly warns that hosting-edge logs must be disclosed if discoverable. They are discoverable for the preferred host: Railway HTTP logs include source IP, user agent, path, sizes, status, and timing, with seven-day Hobby retention. The BAIRD data inventory and handoff do not yet bind those facts into the privacy notice and release evidence. The security header contract also omits `Cache-Control: no-store` for verification results, errors, and any server-returned evidence crop.

**Required remediation:**

1. Add the selected host's edge-log fields, destination, access boundary, and current retention to the data inventory and public prototype notice.
2. Require the Railway project, service, deployment, and logs to remain private even though the application URL is public.
3. Keep sensitive values out of routes and query strings.
4. Require `Cache-Control: no-store, private` on verification responses and errors, and verify CDN/proxy behavior.
5. Require browser object URL revocation and in-memory state clearing on start-over and page lifecycle where practical.

**Closure proof:** Deployed header tests pass; an edge-log review matches the disclosed metadata and retention; no label/reference content appears in application or edge-visible paths; the hosting project is confirmed private.

### `BAIRD-RT3-F007`: Release provenance does not select an immutable promotion path

**Severity:** Medium  
**Affected evidence:** `ARCHITECTURE_DECISIONS.md:76-90`, `BAIRD_ASSESSMENT.md:107-117`, `ENGINEERING_BLUEPRINT.md:219-229`, `ENGINEERING_BLUEPRINT.md:321-335`, `TECHNICAL_SOURCE_REGISTER.md:53-60`, `I2R_HANDOFF.md:29-47`

The package requires the submitted revision to equal the deployed revision and records commit/model/rule data in metadata. It does not choose between Railway source builds and prebuilt OCI image promotion. It also does not bind source commit, lockfiles, base image, application image, model files, rule/profile versions, and deployment identity into one immutable release tuple. A commit string returned by `/api/v1/meta` does not prove that the running bytes came from that commit.

**Required remediation:**

1. Select one release path and registry/source-build trust boundary.
2. Define the immutable release tuple: commit SHA, lockfile digests, base-image digest, OCI image digest, model digests, rule/profile versions, build ID, and deployment ID.
3. Deploy by immutable digest where the selected platform supports it; do not use a mutable tag as release evidence.
4. Expose safe provenance in `/api/v1/meta` and preserve the complete signed or checksummed release manifest as evidence.
5. Define post-deploy readback, clean-browser smoke, rollback target, and GitHub tag/release binding.

**Closure proof:** The public URL reports a tuple that matches the release manifest and registry/platform readback, the submitted GitHub revision is the same source, and rollback points to a known prior digest.

### `BAIRD-RT3-F008`: Source and security-control traceability do not reach executable I2R ownership

**Severity:** Medium  
**Affected evidence:** `docs/intake/source-requirements.md:16`, `BAIRD_TRACEABILITY.md:22-36`, `BAIRD_ASSESSMENT.md:170-181`, `SECURITY_DATA_FLOW.md:75-96`, `I2R_HANDOFF.md:18-47`, `I2R_HANDOFF.md:74-87`

The source-theme ranges in `BAIRD_TRACEABILITY.md` cover `SRC-001` through `SRC-058` except `SRC-008`, the requirement for one documented structured reference record. `BG-006` appears only in the BAIRD hypothesis table, and each `THR-001` through `THR-018` appears only in the threat table. The handoff names identifier families and mandatory FRD sections but does not map every threat and gate to a specific requirement, component, test, stop condition, and owner.

This makes silent loss possible during I2R. A generic statement that security tests are mandatory is weaker than a closed chain that proves every public-boundary control has an implementing component and required evidence.

**Required remediation:**

1. Add `SRC-008` explicitly to the schema/API decision and proof direction.
2. Add a machine-checkable 58-of-58 source coverage assertion rather than relying only on prose ranges.
3. Map every `ADR`, `BG`, and `THR` identifier to an I2R section, requirement ID, component or integration point, acceptance test, stop gate, and decision owner.
4. Make `BG-006` and `THR-001` through `THR-018` explicit I2R handoff rows, including the unresolved controls in this report.
5. Require the same matrix to continue through Build Instructions and release evidence.

**Closure proof:** Automated identifier checks find no orphaned source, decision, gate, threat, requirement, component, test, or work-package ID, and a human walk from source to deployed evidence succeeds for every Must control.

## 6. Missing gates required before I2R

The following BAIRD-level gates are absent or incomplete and must be added before the architecture can receive CLEAR:

| Required gate | Decision on failure |
|---|---|
| Raw request-body, multipart, spool, and cumulative-pixel gate | Change parser/middleware/storage design before public implementation |
| Blocking-work cancellation ownership gate | Use stricter executor ownership or a killable worker boundary |
| Trusted proxy, client identity, and Origin decision gate | Select a host-specific resolver and exact POST policy |
| Egress semantics gate | Downgrade claim to observed no-dependency behavior or select enforceable network controls |
| Exact OCR model rights and provenance gate | Replace model/package or packaging architecture before I2R approval |
| Hosting edge-log and response no-store gate | Change host/config/privacy notice before public release |
| Immutable release tuple and promotion gate | Select one build/promotion path and bind all artifacts |
| Complete source/ADR/BG/THR to FRD/test/owner gate | Repair traceability before requirements decomposition |

## 7. Controls that passed this review

- The core excludes remote URLs, SVG, PDF, archives, and extra formats.
- The container direction is non-root, no persistent volume, bounded temporary storage, read-only bundled models, readiness before traffic, and release scanning.
- The application log allowlist prohibits raw image, OCR, reference, filename, note, and exception content.
- The cleanup matrix covers success, validation, decode, OCR, rule, timeout, cancellation, and unhandled error exits.
- Batch remains a post-core Should gate. ZIP is excluded unless a separate archive decision and malicious-fixture proof are approved.
- Railway Serverless is disabled. Fly requires one running Machine. Azure requires at least one replica. These choices preserve the cold-start boundary at the architecture level.
- The package does not overclaim a production federal security architecture.

These passes reduce rework, but they do not neutralize the eight findings above.

## 8. Required re-review package

For RT3 re-review, provide one revision containing:

1. remediated ADR, security/data-flow, technical-source, traceability, engineering, and I2R handoff text;
2. an exact model artifact and redistribution register;
3. a selected host security/privacy profile with proxy and edge-log facts;
4. an immutable release provenance contract;
5. a source/ADR/BG/THR to FRD/test/owner matrix;
6. explicit stop conditions for every remediation above;
7. automated identifier and prohibited-Unicode-dash checks.

## 9. Final verdict

`REWORK_REQUIRED`

BAIRD may not advance to I2R on this revision. CLEAR requires closure of all eight findings on one unchanged reviewed revision. In particular, `BAIRD-RT3-F005` must be resolved before the selected offline OCR packaging architecture is treated as approved.
