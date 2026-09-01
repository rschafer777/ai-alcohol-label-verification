# BAIRD Control Handoff Matrix

I2R must preserve these reserved requirement and test IDs. Build Instructions must later add work-package IDs without replacing this chain.

## Architecture decisions

| Source control | I2R requirement | Component/integration | Acceptance test | Stop gate | Owner |
|---|---|---|---|---|---|
| `ADR-001` | `R-001` | `BC-001` through `BC-013` | `T-001` dependency-direction and single-origin contract | No cross-origin service split | Architecture owner |
| `ADR-002` | `R-002` | `BC-001`, `BC-002` | `T-002` strict compile, component, and browser flow | Frontend build or accessibility failure | Frontend owner |
| `ADR-003` | `R-003` | `BC-003` through `BC-013` | `T-003` API contract and event-loop responsiveness | Blocking OCR in HTTP process | Backend owner |
| `ADR-004` | `R-004` | `BC-006`, `BC-007` | `T-004` model BOM, adapter, fixture, hash, and latency | Wrong hash, rights change, false clean, field-family failure | Architecture owner |
| `ADR-005` | `R-005` | `BC-009` through `BC-011` | `T-005` policy mutation and aggregation branch coverage | Any non-deterministic clean result | Rules owner |
| `ADR-006` | `R-006` | `BC-004`, `BC-012` | `T-006` every-exit filesystem and log baseline | Any retained content | Security owner |
| `ADR-007` | `R-007` | `BC-003`, `BC-007`, `BC-013` | `T-007` 200 ms worker acquisition, 6.25/7.5-second ordering, result-free 503/504, supervisor ownership across three caller cancellations, abort storm, shutdown with active/waiting requests, readiness 503, PID/child count, async rewarm, empty request directories, zero final reservations, and complete recovery | Capacity or cleanup released before child exit, unbounded queue, partial result, blocking rewarm, or traffic while unready | Backend owner |
| `ADR-008` | `R-008` | Build pipeline, `/api/v1/meta` | `T-008` immutable tuple and platform digest readback | Any tuple mismatch or mutable promotion | Release owner |
| `ADR-009` | `R-009` | Fly Machine, health, and concurrency integration | `T-009` region/resource/cost/readiness/p95 plus soft-2/hard-4 readback | Over 15 USD, wrong class, sleep, concurrency mismatch, or failed p95 | Release owner |
| `ADR-010` | `R-010` | Optional batch coordinator | `T-010` core-first gate and absence test | Batch code before every core gate | Product owner |
| `ADR-011` | `R-011` | Result contract and browser session disposition | `T-011` evidence immutability test | Reviewer action mutates system evidence | Product owner |
| `ADR-012` | `R-012` | Build assets, dependency inventory, readiness, Fly network policy | `T-012` exact model, selected-check registry, and regulatory-rules registry hashes and versions; non-writable governed assets; representative warmup; wrong/missing/writable failure probes; inventory/code review; port-policy readback; 53/80/443 denial; and explicit 65535 disclosure | Any readiness fail-open, declared external runtime dependency, policy mismatch, probe success, or broader egress claim | Security owner |

## BAIRD gates

| Source control | I2R requirement | Component/integration | Acceptance test | Stop gate | Owner |
|---|---|---|---|---|---|
| `BG-001` | `R-013` | `BC-006` through `BC-010`, `BC-014` | `T-013` 30-fixture field-family and error taxonomy | Any false clean or systematic unsupported family | Validation owner |
| `BG-002` | `R-014` | Browser, API, Fly deployment | `T-014` fixed set of at least 30 valid attempts, 100 percent completion, timeout/error counts, and deployed browser p95 | Any incomplete valid attempt or p95 above 5.0 s | Performance owner |
| `BG-003` | `R-015` | Worker readiness and Fly health | `T-015` five forced restarts | p95 at or above 10 s or traffic before ready | Release owner |
| `BG-004` | `R-016` | `BC-014` fixture harness | `T-016` manifest independence, mutation, and sealed holdout | Oracle imports app constants or coverage gap | Validation owner |
| `BG-005` | `R-017` | Build inventory and Fly network policy | `T-017` startup/request capture, dependency/code inventory, exact 65535 allow readback, and 53/80/443 denial probes | Undeclared outbound dependency, common-port probe success, or claim exceeds port evidence | Security owner |
| `BG-006` | `R-018` | Application-owned multipart parser and OCR worker supervisor | `T-018` success/error/limit/partial-spool-timeout/repeated-cancel/shutdown cleanup matrix with explicit handle closure and exact byte/directory/counter baseline | Temp, handle, memory, reservation, or ownership leak | Security owner |
| `BG-007` | `R-019` | Selected Fly resource class | `T-019` peak RSS, CPU, quote, and owner acceptance | Outside 2 GiB or cost ceiling | Release owner |
| `BG-008` | `R-020` | Optional batch coordinator | `T-020` 250-row proof only after core | Core regression or archive control missing | Product owner |

## Threat controls

| Source control | I2R requirement | Component/integration | Acceptance test | Stop gate | Owner |
|---|---|---|---|---|---|
| `THR-001` | `R-021` | `BC-004`, `BC-013` process-global admission, pre-route receive guard, and application-owned parser | `T-021` full application stack with 0, 6, 7, and many files; extra and oversized fields; malformed boundary; per-file/aggregate/raw limits; fixed/missing/understated length; pre-route and pre-decoder assertions; two near-limit flows; exact baseline restoration | Third body consumed, two-copy reservation exceeds quota, handler/decode invoked after limit, wrong status, actual peak exceeds reservation, or unbounded artifacts | Security owner |
| `THR-002` | `R-022` | `BC-004`, `BC-005` | `T-022` per-image/cumulative/working-pixel bombs | Any limit bypass or unsafe allocation | Imaging owner |
| `THR-003` | `R-023` | `BC-004`, `BC-005` | `T-023` spoofed MIME/extension/polyglot matrix | Spoof accepted or original served | Security owner |
| `THR-004` | `R-024` | Decoder dependencies and container | `T-024` malformed corpus, scan, and resource bounds | Crash, escape, or unbounded decode | Security owner |
| `THR-005` | `R-025` | `BC-004` generated paths | `T-025` traversal and hostile filename tests | User path reaches filesystem | Security owner |
| `THR-006` | `R-026` | API schema/routes | `T-026` URL/base64/archive rejection | Remote fetch path exists | Backend owner |
| `THR-007` | `R-027` | API JSON, `BC-001`, CSP | `T-027` OCR/reference XSS browser fixtures | Script execution or unsafe HTML | Frontend owner |
| `THR-008` | `R-028` | Fly client-identity resolver, bounded keyed limiter, process-global start bucket, admission gate, and killable worker | `T-028` public-edge supplied/duplicate/malformed `Fly-Client-IP`, arbitrary forwarding headers, 4,096-key cap/15-minute TTL, 20-per-client/30-global bursts, two-admission limit, abort storm, child count, and recovery | Ambiguous identity, unbounded key/start state, more than two admitted bodies, or more than one OCR job | Security owner |
| `THR-009` | `R-029` | Edge, process-global admission, spool quota, ASGI receive guard, and owned multipart parser | `T-029` two admitted multipart clients send chunks every 250 ms after crossing the 1 MiB disk-spool threshold; the 3.0 second clock never resets; third request receives 503 before receive; both slow clients receive result-free 408 `upload_timeout`; all parser handles close; bytes, directories, and counters return to baseline; next request succeeds | Activity extends the deadline, a third body is consumed, partial spool remains, wrong status is returned, or recovery fails | Security owner |
| `THR-010` | `R-030` | `BC-012` observability and response-header middleware | `T-030` captured logs on every exit plus no-store/private and no-cache assertions for public success, evidence, validation, decode, overload, timeout, and internal-error responses | Content/identity logged or any covered response cacheable at the Fly URL | Security owner |
| `THR-011` | `R-031` | Request directory and worker ownership | `T-031` filesystem baseline after all exits | Artifact remains after true job exit | Security owner |
| `THR-012` | `R-032` | Locks, model BOM, both registries, SBOM, OCI tuple | `T-032` clean rebuild, exact hash/version/read-only state, notice, and digest verification | Unpinned, writable, wrong-version, or unnotified shipped artifact | Release owner |
| `THR-013` | `R-033` | Dependency/code inventory, telemetry settings, and Fly port policy | `T-033` inventory, network capture, exact policy readback, 53/80/443 denial probes, and 65535 disclosure | External runtime service declared, common port succeeds, or broader network claim appears | Security owner |
| `THR-014` | `R-034` | Security headers | `T-034` clickjack and permissions header assertions | Framing or unused capability enabled | Frontend owner |
| `THR-015` | `R-035` | Host/Origin middleware | `T-035` wrong/missing/null Origin, Host, and preflight | Cross-origin request accepted | Security owner |
| `THR-016` | `R-036` | Same-origin multipart endpoint | `T-036` cross-site form/fetch POST | Cross-site mutation reaches handler | Security owner |
| `THR-017` | `R-037` | Public error mapper | `T-037` production fault injection | Stack, path, model internals, or content exposed | Backend owner |
| `THR-018` | `R-038` | Core schema and optional batch gate | `T-038` archive rejection and batch decision check | ZIP/archive accepted without new ADR | Product owner |

## Gate rule

An I2R requirement is incomplete if it omits its mapped component, test, stop condition, or owner. `SOURCE_COVERAGE.csv` reserves `R-039` through `R-096` and `T-039` through `T-096` for the 58 Intake source rows. A Build Instruction is incomplete if it cannot cite the resulting `R-NNN` and `T-NNN` IDs.
