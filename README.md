# LabelVerify

LabelVerify is an AI-assisted alcohol label verification prototype for the job-application take-home assignment. It compares application values with text found across one to six distilled-spirits label images, applies deterministic review rules, presents evidence for a human reviewer, and supports client-managed batches of up to 300 applications.

This is an unofficial standalone prototype. It is not affiliated with TTB, is not connected to COLAs Online, and does not make legal approval decisions.

## What the prototype demonstrates

- A first-time reviewer can try a complete built-in synthetic sample or enter an application manually.
- One to six JPEG, PNG, or WebP label panels can be previewed, reordered, removed, and verified together.
- Local RapidOCR models extract text without a required cloud API or runtime outbound connection.
- Nineteen selected checks cover brand, class or type, alcohol content, proof, net contents, producer, country of origin when applicable, panel coverage, and ten government-warning properties.
- Deterministic rules distinguish exact matches, definite differences, items requiring judgment, and items the prototype cannot verify.
- Every reported observation is linked to its image, original-pixel polygon, and transform provenance.
- The UI supports cancellation, retry without re-entry, guarded Start over, keyboard use, zoom, and status communication beyond color.
- A batch workspace imports a folder manifest, processes up to 300 applications sequentially, isolates row failures, shows progress and exception filters, supports cancellation and retry, and exports summary CSV plus detailed JSON.
- Uploaded content and reviewer notes are session-only. The application has no database, account, analytics, or durable queue.

The batch path intentionally reuses the single-verification endpoint and local OCR worker. It does not introduce a database, server-side queue, ZIP extraction, or a second comparison pipeline.

## Quick start

### Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) 0.11.32 or a compatible current release
- Node.js 24 and npm 11 for building or changing the frontend

Docker is optional for normal local use. A Docker-compatible OCI builder is required only for the container proof described below.

### Install and run

From the repository root in PowerShell:

```powershell
uv sync --frozen
uv run python ops/fetch_models.py models

Push-Location frontend
npm ci
npm run build
Pop-Location

uv run uvicorn labelverify.api.app:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

If Windows reports that the `uv` cache cannot create compatible hardlinks, rerun the first command as `uv sync --frozen --link-mode copy`. This changes only the local installation method and preserves the locked dependency versions.

Open `http://127.0.0.1:8000`. Choose **Try the built-in sample** for the fastest single-label evaluation path, or choose **Batch** and **Try a 10-application batch** for the fastest batch path.

The first worker start loads and warms the local OCR models. Readiness is available at `http://127.0.0.1:8000/health/ready`.

### Run a folder batch

Choose **Batch**, then **Choose batch folder**. The selected folder must contain exactly one UTF-8 `manifest.csv` and only the label images referenced by that manifest. The app accepts 1 to 300 data rows and processes one application at a time.

Required columns:

```text
case_id,brand_name,class_type,abv_percent,net_contents_value,net_contents_unit,producer_name_address,is_imported,panel_paths
```

Optional columns are `proof` and `country_of_origin`. Separate multiple relative panel paths with `|` or `;`. Use the in-app **Download manifest template** action for a complete example. Absolute paths, traversal, duplicate IDs, ambiguous paths, unreferenced files, files shared by multiple applications, unsupported formats, and per-application limit violations are rejected or retained as visible row errors.

Completed rows can be opened in the same evidence workspace used by a single label. **Export results CSV** produces one formula-safe summary row per manifest application. **Export detailed JSON** includes the input, all 19 checks, reasons, evidence, timings, limitations, and errors.

### Frontend development mode

Run the API on port 8000, then use a second PowerShell window:

```powershell
Set-Location frontend
npm run dev
```

Open `http://127.0.0.1:5173`. Vite proxies `/api` and `/health` to the local FastAPI service.

## Run the quality gates

The project-wide local check is:

```powershell
./scripts/check.ps1
```

It runs Python linting, strict typing, backend and validation tests, frontend linting, strict typing, unit and component tests, the production frontend build, and the prohibited Unicode dash scan.

Useful focused commands:

```powershell
uv run pytest backend/tests tests
uv run ruff check backend tests scripts ops
uv run mypy
uv run python scripts/validate_fixture_corpus.py
uv run python scripts/validate_product_corpus.py
uv run python scripts/run_performance_validation.py
uv run python scripts/run_batch_performance_validation.py
uv run python scripts/generate_frontend_contract.py

Set-Location frontend
npm run test
npm run build
```

The deterministic test corpus contains 24 development cases, 6 sealed holdouts, and a separate two-panel built-in sample. It covers all 19 selected checks and includes ambiguity, warning, bad-image, input-limit, error, and anti-hard-coding controls. The decisive local run passed all 30 cases, all 456 expected result rows, and all 8 mutation controls with zero false-clean results. The current full regression contains 192 passing Python tests and 46 passing frontend tests.

Measured on the documented Windows development host, Warm p95 was 2.374 seconds across 30 two-panel verification runs. Cold readiness through first result was 7.532 seconds across 5 runs. A single warmed worker processed 10 applications in 18.665 seconds, 20 in 36.301 seconds, and all 300 in 521.963 seconds. Peak parent-plus-worker RSS was 1,578,123,264 bytes during the cold run and 847,986,688 bytes during the batch run, both below the selected 2 GiB limit. The machine-readable evidence is in `docs/08-validation/evidence/local-performance.json` and `docs/08-validation/evidence/local-batch-performance.json`. These are local measurements, not guarantees for different hardware or image complexity.

## Container build

The repository includes a multi-stage, non-root `Dockerfile`. It builds the React UI, creates the locked Python environment, downloads and hash-verifies the governed OCR models during the build, and produces one same-origin runtime image.

```powershell
docker build --build-arg LABELVERIFY_BUILD_ID=local-evaluation --tag labelverify:local .
docker run --rm --publish 127.0.0.1:8080:8080 --env LABELVERIFY_RUNTIME_MODE=direct --env LABELVERIFY_ALLOWED_HOST=127.0.0.1:8080 labelverify:local
```

Then open `http://127.0.0.1:8080`.

The current development host did not have an OCI builder installed. Container construction and runtime proof therefore remain explicitly blocked until a builder is available. They are not recorded as passed based on file inspection alone.

`ops/azure-container-app.json` and `.github/workflows/deploy-demo.yml` define the selected Azure demo deployment. The workflow uses GitHub OIDC, a private registry, an immutable image digest, a pull-only managed identity, application-aware health probes, effective-configuration readback, and public smoke tests. `ops/fly.toml.example` remains a non-active portability example. The source repository is [rschafer777/ai-alcohol-label-verification](https://github.com/rschafer777/ai-alcohol-label-verification). Live deployment evidence is not claimed until the authorized workflow completes.

## Architecture and engineering approach

LabelVerify is a same-origin modular monolith:

```text
React UI -> FastAPI boundary -> supervised child -> image transforms -> RapidOCR
                                              -> candidate location
                                              -> deterministic 19-check rules
                                              -> evidence-linked result

Batch folder -> browser manifest validator -> ordered in-memory queue
             -> same single-verification API, concurrency one
             -> progress, exceptions, detail, CSV and JSON
```

The API process owns ingress limits, Host and Origin controls, rate and capacity admission, public errors, cleanup, security headers, and static UI delivery. Full decode through result aggregation runs in one killable child process so cancellation, timeout, disconnect, and shutdown can be bounded and cleaned up.

Reference values are never supplied to OCR candidate location. The pipeline first extracts observations from label pixels, then compares those candidates with application values. This separation reduces confirmation bias and is protected by tests and mutation controls.

Core technology choices:

- React 19.2, strict TypeScript, Vite 8, Vitest, and Testing Library;
- Python 3.12, FastAPI, Pydantic, and Uvicorn;
- RapidOCR 3.4.2, ONNX Runtime 1.22.1 CPU, OpenCV, and Pillow;
- versioned JSON request, result, error, selected-check, and regulatory-rule contracts;
- deterministic synthetic fixtures, independent oracles, and sealed holdouts;
- one multi-stage OCI image with a non-root runtime identity.

## Assumptions, trade-offs, and limitations

These boundaries are part of the product contract and are not hidden future-work notes.

### Scope and workflow

- The implemented rule profile is distilled spirits. Beer and wine have different requirements and are not represented as supported batch or single-label profiles.
- Application values are entered manually or through the batch manifest because direct COLAs Online integration was explicitly excluded.
- Batch supports 1 to 300 manifest rows, but it is session-only and sequential. This keeps local CPU and memory predictable and reuses the validated single-request path, at the cost of total elapsed time increasing approximately with row count.
- Batch does not accept ZIP files, save a queue, resume after refresh, schedule background work, or provide multi-user coordination. Those behaviors would require a server queue, persistence, identity, retention, and operational controls that are outside this prototype.
- Reviewer notes and dispositions are browser-only working state. They are not an audit record and do not change immutable machine findings.

### AI, runtime, and network

- Runtime text extraction uses bundled, hash-verified RapidOCR ONNX models on the host CPU. The application has no required runtime cloud inference, analytics, model download, or external API call.
- Initial provisioning still requires dependency and model acquisition unless an organization prepares an approved offline bundle. The source does not itself prove a fully air-gapped installation process.
- Source behavior does not replace network policy. A production deployment must enforce and test its selected outbound allowlist or deny rule at the platform boundary.
- OCR confidence is an engine signal, not a calibrated probability or a compliance score.

### Correctness and compliance

- Exact warning wording and heading capitalization drive deterministic comparison. An exact OCR transcription can clear. Punctuation-only or minor OCR differences route to Review, while materially missing or replacement warning language becomes a Difference. Case-only or punctuation-only brand differences, including `STONE'S THROW` versus `Stone's Throw`, also route to Review so human judgment is preserved.
- Heading boldness, body emphasis, separation, continuity, contrast, and legibility use image heuristics and can require Review. They are not represented as exact typography measurement.
- Warning minimum type size and maximum characters per inch depend on container volume. An ordinary image has no trustworthy physical scale, so this check is Not verified unless separately reliable calibration is available. Printed text that says `2 mm` is not treated as calibration.
- `No differences found in checked fields` means only that the selected applicable checks did not expose a difference. It is not a legal approval and does not represent comprehensive alcohol-label compliance.
- Country of origin is evaluated only when the application marks the product as imported.
- The governed 50-image visual oracle contains 33 image-supported passes and 17 visible defects. The current partial local image harness sends all 33 visual-pass cases to review, detects 5 visible defects as deterministic differences, holds the other 12 defects for review, and produces zero false clearances or false deterministic rejections. This remains a failed automatic-clear recognition gate rather than corpus-UAT completion. Full evidence and every per-file reason are in [`docs/08-validation/TEST_IMAGES_VALIDATION_REPORT.md`](docs/08-validation/TEST_IMAGES_VALIDATION_REPORT.md).
- The 50 raw user-supplied validation images are intentionally excluded from the public repository because authorization covers local validation and retention but does not approve redistribution. The governed oracle, per-file report, and machine-readable results remain included. An authorized evaluator can place the original 50 files in `tests/Test_Images/` and run `uv run python scripts/validate_test_images.py` to reproduce the diagnostic.

### Images and performance

- The image pipeline handles EXIF orientation, bounded resizing, blur and exposure signals, conservative small-angle deskew or clear trapezoid correction, and one local contrast-recovery view. Derived evidence is mapped back to original pixels.
- It does not promise general glare removal, curved-bottle unwarping, restoration of missing pixels, or reliable recovery from every photograph. Angle, glare, curvature, low light, or partial framing is not a label defect by itself. Recoverable evidence is evaluated normally. Unreadable mandatory evidence remains Bad image, Review, Not verified, or requests another image. Only a visible deterministic defect becomes a Difference.
- Normal readable images target less than 5 seconds. Difficult recoverable images may take 5 to 9 seconds. Sequential batches target a mean near or below 5 seconds per image. Cold readiness, multiple panels, maximum inputs, and full batch elapsed time are measured and reported separately.
- Batch concurrency is deliberately one because the backend owns one governed OCR job. This favors stability, isolation, and predictable resources over maximum throughput.
- The application permits one active request per client and a bounded 360 verification starts per client per ten minutes so a 300-row sequential batch can complete. A separate global start limit, admission reservation, request deadlines, and the single governed OCR worker continue to bound aggregate demand.

### Data, deployment, and federal transition

- The prototype has no database, account system, durable queue, automatic browser persistence, analytics, or content logging. Server request files are temporary and browser state disappears on refresh or Start over. User-initiated CSV and detailed JSON exports are durable downloaded files under the user's browser and filesystem control; they can contain application values, panel paths, findings, evidence text, timings, and errors.
- Evaluation should use synthetic or sanitized inputs. Production data categories, PII analysis, records schedules, retention, legal hold, and audit requirements depend on the selected agency workflow.
- The legacy COLA system is .NET. This standalone prototype uses React, TypeScript, Python, FastAPI, RapidOCR, ONNX Runtime, OpenCV, and Pillow because that stack is implemented and measured here. The versioned API boundary permits a later .NET adapter or reimplementation after an actual integration and procurement decision.
- A container definition, governed Azure template, and OIDC deployment workflow are included. Local OCI proof remains blocked because this development host has no OCI builder. The GitHub workflow must build, deploy, read back, and smoke-test the exact public revision before deployed evidence can pass.
- [`docs/11-federal-authorization-readiness/`](docs/11-federal-authorization-readiness/) provides current starter materials for choosing and beginning an agency RMF/ATO or FedRAMP 20x path. Production boundary, impact, Azure services, identity, logging, retention, assessor, and operating evidence remain inputs to that process.

## Resource and privacy boundaries

- 1 to 6 images per verification;
- 4 MiB per image and 8 MiB aggregate image bytes;
- 12 megapixels per image and 36 megapixels cumulative;
- 32 KiB reference JSON;
- 20-second request-body deadline, 6.25-second child deadline, 30-second server deadline, and 35-second browser deadline;
- one active OCR job with bounded admission;
- no content logging, database, durable queue, browser persistence, or required runtime cloud inference.

## Documentation map

The numbered folders preserve the complete requirements-to-delivery path:

1. [`docs/01-discovery/`](docs/01-discovery/): sanitized assignment and stakeholder source material
2. [`docs/02-intake/`](docs/02-intake/): Intake baseline, scope, success, assumptions, risks, and source traceability
3. [`docs/03-baird/`](docs/03-baird/): Beginning Assessment Intake Requirements Document and independent validation
4. [`docs/04-i2r-ae/`](docs/04-i2r-ae/): Ideation-to-Realization architecture and engineering package
5. [`docs/05-frd/`](docs/05-frd/): 41 feature requirements, tests, and traceability
6. [`docs/06-build-instructions/`](docs/06-build-instructions/): epics, work packages, tasks, standards, QA/QC, UAT, and Definition of Done
7. [`docs/07-development/`](docs/07-development/): toolchain, contracts, implementation, and correction records
8. [`docs/08-validation/`](docs/08-validation/): Validation Protocol evidence
9. [`docs/09-qa-qc-uat/`](docs/09-qa-qc-uat/): defect loop, regression, accessibility, and UAT evidence
10. [`docs/10-release/`](docs/10-release/): local release candidate, provenance, limitations, and requester-controlled gates
11. [`docs/11-federal-authorization-readiness/`](docs/11-federal-authorization-readiness/): authorization path, package templates, secure configuration, evidence, assessment, risk, monitoring, and agency handoff

The root [`contracts/`](contracts/) directory is the versioned machine-readable source for API and rule identities. The root [`fixtures/`](fixtures/) directory contains the sample, development corpus, sealed holdouts, independent oracles, schemas, and mutation plan.

## Submission status

The source code and documentation package is published through [rschafer777/ai-alcohol-label-verification](https://github.com/rschafer777/ai-alcohol-label-verification). A public application deployment and deployed URL remain outstanding assignment deliverables.
