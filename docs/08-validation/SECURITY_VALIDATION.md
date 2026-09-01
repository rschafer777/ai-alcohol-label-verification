# Security Validation Results

Document control ID: LV-VAL-SEC-001  
Revision: 1.0  
Date: 2026-09-01  
Status: Local source and runtime validation complete

## 1. Scope

The security review covered the complete local application snapshot, including the browser client, FastAPI boundary, custom multipart parser, request lifecycle, spawned OCR worker, image decoders, deterministic comparison rules, local model assets, build inputs, container source, deployment template, lockfiles, SBOMs, and documentation claims.

The standard independent scan identifier was `6cb6f418-1e87-4d19-b823-c528be710202`. Canonical pre-fix evidence is retained under `docs/08-validation/evidence/security-pre-fix/`.

| Evidence | SHA-256 |
|---|---|
| `scan-manifest.json` | `7f281f1d9c7101932f6c3b7e1a16c9cb6edfb70069062025d0d7151b2a80a678` |
| `findings.json` | `696f308bba10a893ba36aca5e7c285eb1919b6e0e076a304852594f7a5f8e403` |
| `coverage.json` | `e0346b9bb7e5604fe7079d43c7d281942c38bd7cb46c8cec0994da99f308d68f` |

## 2. Validated findings and disposition

| Finding | Original severity | Corrective control | Verification | Status |
|---|---|---|---|---|
| Decoded raster allocation before pixel limit | Medium | Read and validate declared dimensions before verify, orientation, raster load, and conversion; pass remaining cumulative pixels before each decode. | Focused boundary tests plus strict static checks | FIXED |
| Worker replacement and shutdown race | Medium | Terminal stopping state, tracked replacement threads, interruptible readiness polling, and joined shutdown. | Deterministic stop and warmup-interruption regressions | FIXED |
| Global start budget charged before structural validation | Medium | Validate request framing before limiter charge and track ownership explicitly. | Invalid-length and concurrent ownership regressions | FIXED |
| Framework multipart spill outside governed spool | Low | Custom parser supplies the explicit spool root for every `SpooledTemporaryFile`. | Real spill-location regression | FIXED |
| Partial multipart resources not closed on every exception | Low | Parser closes all owned temporary files on `BaseException`. | RuntimeError and CancelledError regressions | FIXED |

The post-fix read-only review found no remaining source-backed bypass for these five findings. One circular-import regression discovered during independent fix review was corrected with lazy API package import behavior and covered by direct import tests.

## 3. Additional release security corrections

- CSP-compatible zoom and rotation classes replaced inline transform styles.
- The local container command now explicitly selects direct loopback mode.
- The frontend SBOM was reconstructed from the exact production package-lock graph after npm produced an empty private-package graph.
- FastAPI, Starlette, Pillow, and python-multipart were upgraded after current advisory review.
- pytest was upgraded after the full synchronized-environment audit identified a development-only advisory.
- The Python SBOM was regenerated from the corrected lock.

## 4. Dependency audit result

On 2026-09-01:

- `pip-audit` reported no known vulnerabilities in the complete synchronized Python environment;
- `npm audit --omit=dev` reported zero production vulnerabilities;
- exact production dependency identities remain frozen in `uv.lock` and `frontend/package-lock.json`;
- current SBOM hashes are recorded in `docs/10-release/DEPENDENCY_AND_MODEL_INVENTORY.md`.

Dependency results are time-bound. Both audits are mandatory again immediately before public release.

## 5. Source-backed security conclusion

Local source and test evidence supports the following conclusions:

- no required runtime external inference or other outbound application call path;
- no database, durable queue, object store, account, or browser persistence;
- no application content logging and no Uvicorn access log in documented launches;
- exact production Host and same-origin mutation checks;
- no-store API and health responses plus CSP and standard browser security headers;
- bounded request bytes, parts, pixels, deadlines, concurrency, limiter tables, worker lifetime, and temporary-resource cleanup;
- hash-verified OCR models and frozen contract registries;
- child-process decode through aggregation with hard termination and readiness-gated replacement;
- no false legal or TTB approval claim.

## 6. External controls not proven locally

The security conclusion does not claim the following without OCI or deployment evidence:

- a read-only container root filesystem;
- filesystem-level temporary storage quota;
- network-level outbound denial;
- Fly proxy header provenance in a real deployment;
- deployed TLS, edge, platform-log, health-routing, or retention behavior;
- immutable OCI identity and rollback digest.

These remain explicit release gates and are not product defects in the local candidate.
