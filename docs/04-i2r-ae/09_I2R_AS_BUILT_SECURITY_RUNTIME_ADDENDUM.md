# I2R As-Built Security and Runtime Addendum

Document control ID: LV-I2R-009  
Revision: 1.1  
Date: 2026-09-01  
Status: Active as-built authority

## 1. Purpose and precedence

This addendum records the implemented architecture after development, independent security review, and the first Validation Protocol correction loop. It does not change the frozen API, error, rule, or selected-check contracts. Where an earlier I2R design statement describes an implementation mechanism differently, this as-built record controls.

## 2. Corrected implementation statements

| Topic | As-built implementation | Evidence status |
|---|---|---|
| Multipart framework spool | A controlled Starlette parser creates every `SpooledTemporaryFile` under `LABELVERIFY_SPOOL_ROOT`. The parser closes all partially created files for every `BaseException`, including cancellation. | Source and regression PASS |
| Validated panel copies | The API route creates generated `request-*` directories and `panel-N.img` names under the same spool root. Client filenames are never filesystem paths. | Source and regression PASS |
| Cleanup ownership | The API route owns upload handles and request directories. The route shields and awaits the worker task before closing uploads and deleting the directory. The worker supervisor owns only worker process lifetime and worker capacity. | Source and regression PASS |
| Storage accounting | Admission reserves 17,301,504 logical bytes for each of at most two active requests, for 34,603,008 logical bytes. This is capacity accounting, not a filesystem quota. No 50,331,648 byte filesystem quota is claimed by source. | Source PASS; deployment quota NOT ESTABLISHED |
| Image limit | Pillow reads source dimensions and enforces the per-image and remaining cumulative pixel limits before orientation transforms or raster load. Full decode remains inside the supervised child. | Source and regression PASS |
| Start limiter | Host, Origin, client identity, and structural Content-Length checks occur before the shared valid-start budget is charged. A rejected concurrent begin cannot clear another request's active ownership. | Source and regression PASS |
| Worker shutdown | Shutdown sets a terminal stopping state, makes readiness polling interruptible, tracks replacement threads, prevents post-stop resurrection, and joins replacement activity before returning. | Source and regression PASS |
| Worker isolation | The spawned child provides lifetime, queue, memory-failure, and hard-timeout containment. It uses the same runtime OS identity, filesystem authority, and network authority as the parent. It is not claimed as a least-privilege sandbox. | Source PASS |
| Runtime filesystem | The OCI source declares UID and GID 10001 and makes governed model files non-writable. A read-only root filesystem and a single writable mount are not established until OCI runtime proof exists. | Source partial; OCI proof BLOCKED |
| Runtime egress | Production source has no required external inference, analytics, model download, or other outbound application path. Repository configuration does not itself enforce denied egress. | Source PASS for no required call path; network denial NOT ESTABLISHED |
| Logging | Application source emits no content-bearing structured logs and documented launches disable Uvicorn access logs. Platform and framework logging retention are deployment concerns. | Source PASS; platform readback PENDING |
| Direct local container mode | The documented local container command explicitly selects direct mode and binds to `127.0.0.1`. Production Host, Origin, and explicitly selected edge client-identity controls apply only in production mode. | Documentation and source PASS; OCI execution BLOCKED |
| Dependency posture | Frozen production dependencies use FastAPI 0.141.1, Starlette 1.6.0, Pillow 12.3.0, and python-multipart 0.0.32. The complete synchronized Python environment and npm production graph had zero known audit findings on 2026-09-01. | Local audit PASS; release recheck REQUIRED |

## 3. Effective request lifecycle

1. Boundary middleware validates production Host and Origin when applicable, resolves a non-reversible client key, validates request framing, and only then charges the valid-start limiter and admission counter.
2. The complete request remains subject to the 8,650,752 byte raw ceiling, 20 second body deadline, and 30 second server deadline.
3. The controlled multipart parser accepts one reference field and at most six files, keeps disk spills under the governed spool root, and closes partial resources on every exceptional path.
4. The route validates the reference, copies panels under generated names, enforces per-file and aggregate encoded limits, and checks media signatures.
5. One spawned worker performs source-dimension checks, decode, bounded transforms, local OCR, reference-blind candidate location, deterministic comparison, aggregation, and result validation under the 9 second worker deadline.
6. The parent validates the typed result and evidence geometry before returning a no-store response. Browser response parsing validates the same contract before rendering.
7. Cancellation suppresses delivery but does not release worker or file ownership early. Cleanup occurs only after worker completion or confirmed termination.

## 4. Total-phase verification interpretation

The 20 second upload, 30 second server, and 35 second browser deadlines remain unchanged. Controlled stalls cover every actual asynchronous wait boundary: upload, parent validation, worker queue, the single supervised child job containing decode through inference, response transfer, and the browser request deadline.

Client validation, React result rendering, focus placement, and live-region DOM output are synchronous browser commit paths. Their governed proof is immediate local rejection without transport or one complete result commit with all rows, managed focus, and the required live-region content. The application does not add dormant asynchronous phase adapters solely for tests.

## 5. Data handling statement

The implementation has no database, durable queue, object store, account, server session, browser storage API, analytics SDK, or runtime external inference service. Reference values, images, OCR text, evidence, notes, and disposition exist only in request-scoped server resources and current browser memory. This source-backed statement does not replace deployment proof for platform logs, egress policy, or filesystem mounts.

## 6. Remaining external assertions

The following are not converted to PASS by local source or test evidence:

- clean OCI build and rebuild;
- image digest and non-root runtime readback;
- runtime model and contract hash readback;
- read-only root or explicit writable-mount policy, if selected;
- deployed restricted-egress policy and probes;
- immutable source revision and clean-checkout replay;
- public deployment identity, URL, health, performance, and edge-header proof;
- final dated official-source regulatory recheck;
- requester code review, functional test, UAT, and release approval.

These remain environment, authorization, or external-verification gates. They do not block a local requester-review candidate, but they do block a final public-release claim.
