# LabelVerify

LabelVerify is a local-first, AI-assisted alcohol label evidence application built for the TTB take-home assignment. A reviewer supplies one to three images of a product. The application reads the images, infers beer or malt beverage, wine, or distilled spirits, extracts required label information, applies 24 deterministic common and beverage-specific checks, and shows what it found and where it found it. A human records the final disposition.

The application also groups and processes batches of up to 300 products and retains the latest 500 results with their source images and reopenable evidence.

## Live application and source

- Application: [LabelVerify on Azure](https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/)
- Repository: [rschafer777/ai-alcohol-label-verification](https://github.com/rschafer777/ai-alcohol-label-verification)

## What it does

- Starts from label images, not manually typed label fields.
- Accepts 1 to 3 JPEG, PNG, or WebP panels per product.
- Runs OCR locally with bundled ONNX models. Label processing requires no external ML API.
- Infers malt beverage, wine, or distilled spirits from whole-term evidence and exposes conflicts for review.
- Extracts brand, class/type, ABV, proof, net contents, producer/address, origin, warning, and selected family-specific evidence.
- Applies 24 ordered checks with Match, Mismatch, Review, and Not verified states.
- Evaluates the government warning through separate applicability, wording, capitalization, emphasis, separation, continuity, contrast, legibility, and size-capability checks.
- Maps every located field to an original-pixel polygon and provides Show on label.
- Preserves human judgment for case-only and punctuation-only variations such as `STONE'S THROW` and `Stone's Throw`.
- Attempts bounded orientation, deskew, perspective, and contrast recovery without inventing obscured text.
- Suggests product groups for folders containing up to 900 images, requires reviewer confirmation, and processes up to 300 products.
- Reports batch progress, remaining work, active time, average, ETA, attempts, exceptions, retry, cancel, CSV, and JSON.
- Stores the latest 500 results and images with filtering, paging, evidence reopening, disposition editing, deletion, and FIFO eviction. An opaque HttpOnly browser-scope cookie isolates history access in the public demo.
- Includes a complete built-in synthetic sample.

## Technology

- Frontend: React 19, strict TypeScript, Vite, Vitest, Testing Library, Playwright
- API: Python 3.12, FastAPI, Pydantic, Uvicorn
- OCR and imaging: RapidOCR, ONNX Runtime CPU, OpenCV, Pillow, NumPy
- Rules: deterministic Python modules plus versioned JSON registries
- Storage: SQLite plus a controlled local image directory
- Packaging and deployment: non-root OCI container, GitHub Actions OIDC, Azure Container Registry, Azure Container Apps

The agency context mentions .NET, but direct COLAs Online integration is excluded from this prototype. The typed HTTP boundary permits a later .NET adapter without coupling OCR or rules to the UI.

## Architecture

```text
React UI
  -> FastAPI security and validation boundary
    -> supervised child process
      -> image decode and bounded recovery views
        -> local RapidOCR
          -> candidates and original-pixel evidence
            -> beverage inference
              -> deterministic 24-check engine
                -> result and SQLite/file history
```

Single and batch flows use the same analysis endpoint. Batch coordination is sequential in the browser so one failed product is isolated and the local OCR worker stays resource-bounded.

## Quick start on Windows

Prerequisites:

- Python 3.12
- [uv](https://docs.astral.sh/uv/) 0.11.32 or compatible current release
- Node.js 24 and npm 11

From the repository root in PowerShell:

```powershell
uv sync --frozen --link-mode copy
uv run python ops/fetch_models.py models

Push-Location frontend
npm ci
npm run build
Pop-Location

uv run uvicorn labelverify.api.app:app --app-dir backend --host 127.0.0.1 --port 8000 --no-access-log
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Select **Use built-in sample** for the fastest complete path.

### Frontend development

Keep the API on port 8000, then run:

```powershell
Set-Location frontend
npm run dev
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173). Vite proxies `/api` and `/health` to the local API.

### Container

```powershell
docker build --build-arg LABELVERIFY_BUILD_ID=local-evaluation --tag labelverify:local .
docker run --rm --publish 127.0.0.1:8080:8080 --env LABELVERIFY_RUNTIME_MODE=direct --env LABELVERIFY_ALLOWED_HOST=127.0.0.1:8080 labelverify:local
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080).

## Run tests

The fast code-quality gate is:

```powershell
./scripts/check.ps1
```

The complete release-candidate gate adds the governed product corpus, warm and cold OCR timing, a 20-product sequential batch, dependency audits, release-manifest verification, and the 50-image diagnostic when its non-redistributable local images are installed:

```powershell
./scripts/release-check.ps1
```

Focused commands:

```powershell
uv run ruff check backend tests scripts ops
uv run mypy
uv run pytest
uv run python scripts/validate_product_corpus.py
uv run python scripts/run_performance_validation.py
uv run python scripts/run_batch_performance_validation.py --count 20
uv run python scripts/validate_test_images.py

Push-Location frontend
npm run lint
npm run typecheck
npm run test
npm run build
npm run test:e2e
Pop-Location
```

The user-supplied validation folder is expected at `tests/Test_Images/`. Its 50 governed images are identified by `test-oracle-v1.json`; additional local files are ignored and reported. Raw images remain excluded from the public repository because public redistribution rights were not established.

## API

| Method and path | Purpose |
| --- | --- |
| `GET /health/live` | Liveness |
| `GET /health/ready` | OCR readiness |
| `GET /api/v1/meta` | Build, contract, limits, and rule identity |
| `POST /api/v1/analyses` | Label-first OCR, checks, and persistence |
| `POST /api/v1/verifications` | Optional trusted-reference comparison |
| `GET /api/v1/history` | Filtered and paged history |
| `GET /api/v1/history/{id}` | Stored result |
| `GET /api/v1/history/{id}/panels/{panelId}` | Retained evidence image |
| `PATCH /api/v1/history/{id}/disposition` | Human disposition and note |
| `DELETE /api/v1/history/{id}` | Delete one record and images |
| `DELETE /api/v1/history` | Clear history |

## Image guidance

For UAT, use 2400 by 3200 pixels in portrait or 3200 by 2400 in landscape, 300 PPI metadata, JPEG quality 85 to 92, and approximately 1 to 4 MiB per file. Keep the label at least 60 percent of the frame and important characters at least 20 pixels high. A 736 by 532 image can work when sharp and tightly framed, but it is below the recommended evidence density.

PPI metadata does not prove physical type size. Reliable millimeter validation requires a trustworthy scale or known capture geometry.

## Regulatory approach

The selected rule registry is based on the current TTB and eCFR sources listed in `contracts/regulatory-rules-v1.json`.

- Malt beverages: recognized class/type, limitations on `IPA` alone, U.S. customary net quantity, alcohol-statement triggers, prohibited ranges, decimal precision, and formula or state-law dependencies. `ABV` is not accepted as an abbreviation.
- Wine: numeric alcohol rules, permitted range span and the 14 percent boundary, the table/light wine exception, conditional appellation, and sulfite declaration dependent on chemistry.
- Distilled spirits: required alcohol content, same-field-of-vision evaluation for brand, class/type, and ABV, plus optional proof comparison and distinction.
- All families at 0.5 percent ABV or more: exact government warning content and presentation checks.

The UI label `Approve` records a reviewer's prototype disposition. It does not alter machine evidence.

## Assumptions

- One to three submitted panels represent one product after user confirmation.
- Product grouping can use folder and filename cues, but ambiguity requires confirmation.
- The take-home prototype uses synthetic or sanitized data.
- No trusted COLA application record, formula, chemistry result, physical scale, state rule set, identity provider, or agency records schedule is supplied.
- The selected federal rules are evidence checks, not a replacement for the complete agency review process.

## Trade-offs

- Local CPU OCR avoids blocked cloud endpoints and data egress, but throughput depends on host hardware.
- Sequential batch processing prioritizes predictable resources and fault isolation over maximum parallel speed.
- A modular monolith is simpler to build, run, test, and deploy for this scope. Typed boundaries preserve a path to separate services later.
- SQLite plus local files makes the 500-record workflow easy to evaluate. A production Azure deployment should select durable managed storage.
- Anonymous browser-scope history avoids an account setup step for UAT. Production requires agency identity and role-based authorization.
- Typography and image heuristics can identify strong visual evidence, but uncertain emphasis, contrast, or physical size remains human review.
- Silent type inference reduces user work, but unresolved or conflicting signals are shown rather than guessed.

## Limitations

- Label-first OCR can test visible label evidence but cannot prove equality with an independent application record. The separate verification endpoint supports that comparison when a trusted source is later available.
- Formula-dependent malt rules, chemistry-dependent sulfite rules, wine below 7 percent jurisdiction, state requirements, permit truth, and production records cannot be decided from pixels alone.
- Ordinary images do not provide reliable physical type size.
- Glare removal, curved-bottle unwarping, and restoration of missing pixels are not guaranteed. Unreadable evidence requests review or another image.
- OCR engine confidence is not a calibrated compliance probability.
- Local history in the Azure demo can reset on container revision or instance lifecycle. Production needs durable storage, identity, audit, retention, backup, legal hold, and recovery controls.
- Clearing browser storage loses access to that browser scope's retained demo history. The cookie is intentionally unreadable to JavaScript, SameSite Strict, and Secure on the Azure deployment.
- The prototype supports one active OCR job and one Azure replica. It is designed for functional evaluation, not production multi-user scale.
- Initial dependency and model setup needs package and artifact access unless an approved offline bundle is prepared. Label processing itself has no runtime cloud inference dependency.

## Documentation

The governed development path is in [`docs/`](docs/README.md):

1. Discovery
2. Intake
3. BAIRD
4. I2R architecture and engineering
5. FRD and traceability
6. Build Instructions and Definition of Done
7. Implementation record
8. Validation Protocol and evidence
9. QA, QC, and UAT
10. Release and operations
11. Federal authorization starter package

Machine-enforced API limits and rules are in [`contracts/`](contracts/README.md).

## License

No LICENSE file is included. Third-party components retain their respective licenses, summarized in `docs/10-release/THIRD_PARTY_NOTICES.md` and the SBOM files.
