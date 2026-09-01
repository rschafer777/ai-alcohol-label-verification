# BAIRD to I2R Handoff

**Status:** Draft pending three BAIRD CLEAR reviews

## 1. Selected baseline

I2R should write the FRD for:

- one single-origin React/TypeScript plus FastAPI/Python application;
- RapidOCR 3.4.2, ONNX Runtime 1.22.1 CPU, and exact `evidence/MODEL_BOM.md` artifacts behind an extraction port;
- typed multi-panel synchronous verification API;
- deterministic field/capability/aggregation logic;
- typed `alternatives[]` items that pair each conflicting value with its own evidence reference and browser action;
- one versioned 17-check registry containing brand, class/type, ABV, proof, net contents, producer, country, warning applicability, warning wording and presentation, panel coverage, and image quality;
- one separate versioned regulatory-rules registry containing exact authority metadata, warning text, and applicability threshold;
- no database, accounts, external inference, or runtime model download;
- one application-owned multipart parser and one worker supervisor with repeated-cancellation and shutdown-safe artifact ownership;
- desktop-first accessible evidence workspace;
- one Fly.io `iad` Machine, `shared-cpu-2x`, 2 GiB, always ready, deployed by immutable OCI digest, with conventional outbound ports 53, 80, and 443 denied and TCP 65535 explicitly allowed;
- batch as a separate post-core Should gate.

## 2. Required FRD identifier families

- `R-NNN`: functional and non-functional requirements;
- `C-NNN`: components;
- `IP-NNN`: integration points/contracts;
- `T-NNN`: test cases/evidence;
- `ADR-NNN`: inherited architecture decisions;
- `BG-NNN`: feasibility gates;
- `THR-NNN`: threat/control cases;
- `WP-NNN`: later Build Instruction work packages.

## 3. FRD mandatory sections

1. objective and non-goals;
2. actor and journey definitions;
3. exact reference and multi-panel schemas;
4. extraction/candidate/evidence contracts;
5. field-by-field comparison policies;
6. warning rule/capability matrix;
7. state and aggregation machine;
8. API and public error contracts;
9. UX/accessibility behavior;
10. performance envelope and benchmark method;
11. security/privacy/data flow and abuse controls;
12. observability and prohibited logs;
13. fixture/holdout/anti-hard-coding plan;
14. deployment, health, provenance, and rollback;
15. batch go/no-go and exact conditional requirements;
16. source-to-requirement-to-component-to-test matrix;
17. definition of done and release evidence.

## 4. Decisions I2R may refine without reopening Intake

- exact frontend and supporting package versions after compatibility check, except selected OCR/runtime versions and artifacts;
- OCR confidence routing thresholds from fixtures;
- image quality thresholds;
- fine-grained rate-limit refill implementation without changing the selected active/global caps;
- detailed component/file names;
- evidence-crop encoding and size;
- exact file/module names for the already selected separate proof check;

## 5. Decisions that require scope change control

- adding beverage categories or comprehensive claims;
- external inference in the release core;
- persistence, accounts, or case history;
- direct COLA integration or real COLA parsing;
- autonomous approval/rejection;
- making batch a core release blocker;
- accepting PDFs, archives, remote URLs, or additional image formats;
- mobile-specific support;
- changing the valid-result latency or no-false-clean invariant.
- demoting any Active warning row, changing its aggregation, or implying physical-size verification;
- changing the model BOM, either registry, worker ownership, 200 ms worker queue deadline, 3.0 second total upload deadline, two-copy 128 MiB spool envelope, selected resource class, or egress property without BAIRD reapproval.

## 6. I2R stop conditions

Do not approve the FRD if:

- any active check lacks explicit sufficient-evidence and uncertainty behavior;
- any active check is mislabeled as advisory or excluded from aggregation;
- OCR, candidate generation, or primary selection can see expected values;
- missing panels can yield a clean summary;
- the performance harness excludes upload/client/render time;
- fixture expected outcomes import application constants;
- raw-byte, total-body deadline, multipart, two-copy spool, pixel, worker queue, cancellation ownership, cleanup, proxy identity, Origin/Host, no-store, log, and egress controls lack tests;
- deployment can routinely sleep or accept traffic before model and registry hash/version/read-only readiness;
- batch requirements are partly committed without the exact go/no-go;
- README/repository/deployed deliverables disappear from traceability.
- any `SRC` lacks its requirement, component, acceptance test, stop gate, or owner in `SOURCE_COVERAGE.csv`;
- any `ADR`, `BG`, or `THR` lacks its requirement, component, acceptance test, stop gate, or owner in `BAIRD_CONTROL_HANDOFF_MATRIX.md`;
- the immutable release tuple or exact model notices disappear;

## 7. BAIRD exit evidence required

- three independent BAIRD reports with CLEAR verdicts on the same revision;
- all findings mapped to remediation if any;
- `evidence/BAIRD_FEASIBILITY_REPORT.md`, `evidence/EVIDENCE_VALIDATION.md`, `evidence/FIXTURE_ALLOCATION.md`, and `evidence/MODEL_BOM.md` accepted;
- `WARNING_CAPABILITY_MATRIX.md`, `evidence/selected-check-registry.json`, `evidence/regulatory-rules.json`, `evidence/FIXTURE_ALLOCATION.md`, `SOURCE_COVERAGE.csv`, and `BAIRD_CONTROL_HANDOFF_MATRIX.md` accepted as authoritative inputs;
- no prohibited Unicode dash characters or placeholder markers;
- all internal links and identifier sets valid;
- README updated to the next stage only after unanimous clearance.
