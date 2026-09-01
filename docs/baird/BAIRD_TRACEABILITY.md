# BAIRD Traceability and Decision Coverage

## 1. Intake research questions

| Research ID | BAIRD disposition | Evidence/output | I2R gate |
|---|---|---|---|
| `RQ-001` OCR/vision approach | RapidOCR 3.4.2 with ONNX Runtime 1.22.1 and the exact model BOM is selected from measured evidence. Tesseract.js failed field coverage, full PaddleOCR was not measured, and neither is an automatic fallback. External inference is rejected for core. | `BAIRD_ASSESSMENT.md`, `evidence/BAIRD_FEASIBILITY_REPORT.md`, `evidence/MODEL_BOM.md` | `BG-001`, `BG-002` |
| `RQ-002` Preprocessing | Bounded deterministic orientation/downscale/contrast/deskew only; preserve original and coordinate mapping | `ENGINEERING_BLUEPRINT.md` | Fixture and latency tests |
| `RQ-003` Warning capability | Every row marked Active in `WARNING_CAPABILITY_MATRIX.md` aggregates. Insufficient evidence becomes Review or Not verified. Physical type size is explicitly human-only and outside the automated aggregate. | `WARNING_CAPABILITY_MATRIX.md` | FRD check-by-check acceptance |
| `RQ-004` Normalization | Field-specific policies; no generic fuzzy threshold; transformations visible | Engineering comparison policy | Policy test matrix |
| `RQ-005` Input schemas | Fixed spirits profile, typed reference, 1 to 6 panels, conditional import origin | Reference/API contracts, `UX_PRODUCT_SPEC.md` | Schema and usability acceptance |
| `RQ-006` Deployment | Fly.io `iad`, one always-running `shared-cpu-2x` Machine with 2 GiB RAM and immutable image promotion is selected. Azure Container Apps is the named reconsideration path. Railway and sleeping hosts are not selected. | `ADR-009`, deployment matrix, technical source register | `BG-002`, `BG-003`, `BG-007` |
| `RQ-007` No-external-inference | Selected as core architecture | `ADR-004`, `ADR-012` | `BG-001`, `BG-005` |
| `RQ-008` Fixture set | 30 allocated, exceeding the 24 minimum, with 6 holdouts, controlled rendering/degradation, and independent manifest | Engineering fixture contract | `BG-004` |
| `RQ-009` Evidence UX | Panel/region/crop, processed/original, status/reason/capability | `UX_PRODUCT_SPEC.md` | E2E/accessibility tests |
| `RQ-010` Regulatory versioning | eCFR plus TTB guidance, centralized executable rule metadata, exact source/value versions and hashes, read-only runtime assets, and pre-release recheck | `BTS-029`, `BTS-030`, Intake register, `evidence/regulatory-rules.json` | FRD rule registry and readiness tests |
| `RQ-011` Public threat model | Completed prototype threat/data flow and acceptance controls | `SECURITY_DATA_FLOW.md` | Security requirements/tests |
| `RQ-012` Batch feasibility | Should-level only after core; exact 250-row proof required for claim | `ADR-010`, `BG-008` | Post-core go/no-go |
| `RQ-013` Extraction fields | Stable adapter result includes text, regions, confidence provenance, timing, model, typed errors | Extraction contract | API/component acceptance |
| `RQ-014` Browser/deployment test envelope | Chrome/Edge desktop, viewports/zoom, selected host/region recorded | UX and performance contracts | Test matrix |

## 2. Source themes to architecture

`SOURCE_COVERAGE.csv` is the machine-readable 58-row authority for source disposition, BAIRD control, and verification direction. The theme table below is the human summary.

| Source theme | Source IDs | Decisions/components | Proof direction |
|---|---|---|---|
| AI verification prototype | `SRC-001`, `SRC-002` | `ADR-001` through `ADR-005`, `BC-003` through `BC-011` | End-to-end fixture result |
| Selected fields and warning | `SRC-003` through `SRC-006`, `SRC-025` through `SRC-033` | Capability matrix, regulatory registry, field policies | Per-check unit/fixture/evidence |
| Standalone/no COLA | `SRC-007`, `SRC-038` | `ADR-001`, `ADR-012` | No COLA config; no declared external runtime dependency; denied 53/80/443 probes with TCP 65535 disclosure |
| Structured reference contract | `SRC-008` | Typed reference schema and `/api/v1/verifications` contract in `ENGINEERING_BLUEPRINT.md` | Schema, length, conditional-origin, and API contract tests |
| Human judgment/evidence | `SRC-009`, `SRC-010`, `SRC-019` through `SRC-024` | `ADR-005`, `ADR-011`, candidate/evidence contracts | State/aggregation/E2E tests |
| Five-second result | `SRC-011`, `SRC-017`, `SRC-039` | Preload, synchronous API, always-ready host, stage metrics | `BG-002`, `BG-003` |
| Obvious/accessibility | `SRC-012` through `SRC-018` | React UX spec, Try sample, semantic controls | Playwright/axe/manual review |
| Image resilience | `SRC-034` through `SRC-037` | Upload guard, imaging, extraction adapter | Degradation/error fixtures |
| Batch | `SRC-040` through `SRC-044` | `ADR-010`, extension seam | `BG-008` or documented omission |
| Privacy/security/honesty | `SRC-045` through `SRC-049` | `ADR-006`, `ADR-012`, security/data flow | Cleanup/log/egress/header tests |
| Repository/deployment/docs | `SRC-050` through `SRC-057` | Docker, locks, host, CI/release gates | Clean checkout and deployed provenance |
| Writing rule | `SRC-058` | Automated scan | Zero Unicode dash characters |

## 3. Load-bearing hypothesis closure ownership

| Intake assumption | BAIRD decision | Closure point |
|---|---|---|
| `ASM-007` Latency feasibility | Warm architecture path PASS on the equivalent two-CPU envelope: 74 full architecture runs had p95 4,062.84 ms and 74 fixed real-browser attempts were 100 percent complete with p95 4,213.30 ms. Cold path NOT CLOSED LOCALLY: five true process-spawn trials had conservative p95 11,557.18 ms. | `evidence/BAIRD_FEASIBILITY_REPORT.md`; deployed Fly `BG-002` and `BG-003` remain hard release gates |
| `ASM-012` Fixture sufficiency | PASS for validation design: 30 fixtures, including 6 sealed holdouts, cover every selected field family, proof branch, warning applicability/capability, panel boundary, degradation, decoy, import, and result class. | `evidence/FIXTURE_ALLOCATION.md`; `BG-004` verifies construction and independent oracle before release |

BAIRD closes the warmed architecture path and fixture-design hypothesis with retained evidence. It does not mislabel the local cold result or equivalent envelope as deployed proof. The always-running topology and readiness gate address routine exposure, while `BG-002`, `BG-003`, and `BG-004` remain hard stop gates for the final artifact.

## 4. Drift checks

- No all-category or comprehensive legal scope was added.
- No generated design was promoted to source truth.
- No direct COLA integration or real-data persistence was added.
- No failure can count as a successful valid-input result.
- No AI confidence or reviewer action can bypass evidence/rules.
- No expected reference value, fixture identifier, filename, or image hash can influence OCR candidate generation or primary selection.
- No batch claim exists before its post-core proof.
- No selected hosting convenience overrides cold-start or privacy requirements.
- Required repository, README, documentation, and deployed URL remain release Musts.

The complete decision, gate, and threat handoff into reserved I2R requirement and test IDs is in `BAIRD_CONTROL_HANDOFF_MATRIX.md`. I2R must preserve every row in both that matrix and `SOURCE_COVERAGE.csv`.
