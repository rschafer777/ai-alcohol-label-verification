# LabelVerify

LabelVerify is a local-first, AI-assisted alcohol label evidence application built for the TTB take-home assignment. A reviewer supplies one to three images of a product. The application reads the images, infers beer or malt beverage, wine, or distilled spirits, extracts required label information, applies 24 deterministic common and beverage-specific checks, and shows what it found and where it found it. A human records the final disposition.

The application also groups and processes batches of up to 300 products and retains the latest 500 results with their source images and reopenable evidence.

## Live application and source

- Application: [LabelVerify on Azure](https://ca-labelverify-demo.agreeableplant-c5938eef.centralus.azurecontainerapps.io/)
- Repository: [rschafer777/ai-alcohol-label-verification](https://github.com/rschafer777/ai-alcohol-label-verification)

## What it does

- Starts from label images. Typing the application (COLA form) values is optional; when they are entered, the label is compared with them and every entered value is searched across all readable lines of the label.
- Accepts 1 to 3 JPEG, PNG, or WebP panels per product. Oversized browser-selected photos are proportionally resized and re-encoded locally before upload, with server limits still enforced as the authoritative boundary.
- Runs OCR locally with bundled ONNX models. Label processing requires no external ML API.
- Infers malt beverage, wine, or distilled spirits from whole-term evidence and exposes conflicts for review.
- Extracts brand, class/type, ABV, proof, net contents, producer/address, origin, warning, and selected family-specific evidence, reading each panel once at a bounded size and then re-reading the government warning and any missing field from an enlarged crop of the region it located.
- Applies 24 ordered checks with Match, Mismatch, Review, and Not verified states.
- Evaluates the government warning through separate applicability, wording, capitalization, emphasis, separation, continuity, contrast, legibility, and size checks. Each submitted panel carrying the warning is read independently so the clearest complete statement wins and complementary partial reads can confirm statutory words across images while punctuation remains for human review. Wording is compared word for word against 27 CFR 16.21, and a punctuation difference is a review item that names the marks in question, never cleared by the machine; heading and body weight are measured from stroke width against letter height; contrast is measured as a WCAG luminance ratio confirmed by the gray-level range; the millimeter type-size rule is reported for the reviewer because a photograph carries no scale.
- Maps every located field to an original-pixel polygon and provides Show on label.
- Preserves human judgment for case-only and punctuation-only variations such as `STONE'S THROW` and `Stone's Throw`.
- Attempts bounded orientation, deskew, perspective, and contrast recovery without inventing obscured text.
- Suggests product groups for folders containing up to 900 images, requires reviewer confirmation, and processes up to 300 products.
- Reports batch progress, remaining work, active time, average, ETA, attempts, exceptions, retry, cancel, CSV, and JSON.
- Reads the government warning on every submitted image of a product (up to three), keeps the best-read one, and confirms statutory words across images when a curved surface or glare hides part of the statement in any single photograph; a heading cut off at the image edge is a review item, not a defect, and punctuation stays with the reviewer.
- Recognizes common beer styles (bock, doppelbock, hefeweizen, saison, and others) as malt beverage class statements, and wine designations of geographic significance and varietal names (Chianti Classico, Barolo, Rioja, Bordeaux, and others) as wine class statements; a sentence of copy that mentions the class is never taken as the class statement.
- Brings phone photographs within the server's 12 megapixel and 4 MB per-image limits in the browser before upload, so a 24 or 48 megapixel photo needs no manual resizing.
- Lets the reviewer zoom the label with the mouse wheel, drag the enlarged image, use the keyboard for both, and switch between table, card, and image-first views from the head of the checks.
- Guides the grouping step: shows how many products are confirmed, filters to the cards that still need a decision, confirms the remaining suggestions in one step, and states why the run is locked until every product is confirmed.
- Stores the latest 500 results and images with filtering, paging, evidence reopening, disposition editing, deletion, and FIFO eviction. An opaque HttpOnly browser-scope cookie isolates history access in the public demo.
- Includes a complete built-in synthetic sample.
- Ships an evaluation harness (`scripts/score_ground_truth.py`) that processes every private test image, scores the 70 images with pixel-level field ground truth, and compares the 42 images covered by the disposition oracle; the runtime never reads either file.

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

The complete release-candidate gate adds the governed product corpus, warm and cold OCR timing, a 20-product sequential batch, dependency audits, release-manifest verification, and the private API and batch image corpus when at least 50 non-redistributable local images are installed:

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
uv run python scripts/normalize_test_images.py
uv run python scripts/validate_private_uat_corpus_e2e.py
uv run python scripts/score_ground_truth.py

Push-Location frontend
npm run lint
npm run typecheck
npm run test
npm run build
npm run test:e2e
Pop-Location
```

The user-supplied validation folder is expected at `tests/Test_Images/`. The current private corpus contains 76 accepted images plus 2 skipped JSON files (the disposition oracle and the pixel ground truth). The production multipart API processed all 76 images and all 48 server-suggested product groups. Individual-image mean latency was 3.573 seconds on the development workstation, p95 was 5.186 seconds, and the maximum was 6.206 seconds. Raw images remain excluded from the public repository because public redistribution rights were not established.

The disposition oracle covers 42 images and the pixel-level ground truth covers 70 current filenames; `scripts/score_ground_truth.py` scores the production path against both. The current result is 0 false rejects, 1 disputed false clean (an oracle row contradicted by the pixels), 65 of 65 alcohol contents, 64 of 64 net contents, 68 of 70 beverage types, and 61 of 70 brand names read exactly or within a longer line; the full table is in `docs/08-validation/VALIDATION_RESULTS.md`. The ground truth was read by people from the pixels and is not an independent COLA record.

## API

| Method and path | Purpose |
| --- | --- |
| `GET /health/live` | Liveness |
| `GET /health/ready` | OCR readiness |
| `GET /api/v1/meta` | Build, contract, limits, and rule identity |
| `POST /api/v1/analyses` | Label-first OCR, checks, and persistence (`?persist=false` reads without storing, used by batch grouping) |
| `POST /api/v1/verifications` | Optional trusted-reference comparison, also used for reviewer corrections |
| `POST /api/v1/grouping-suggestions` | Conservative product grouping from per-image label facts |
| `GET /api/v1/history` | Filtered and paged history |
| `GET /api/v1/history/{id}` | Stored result |
| `GET /api/v1/history/{id}/panels/{panelId}` | Retained evidence image |
| `POST /api/v1/history/{id}/panels` | Add one image to a stored record and re-read the enlarged panel set (new record, `supersedes` the old) |
| `PATCH /api/v1/history/{id}/disposition` | Human disposition and note |
| `DELETE /api/v1/history/{id}` | Delete one record and images |
| `DELETE /api/v1/history` | Clear history |

Every check row also carries display-only presentation fields (`group`, `shortLabel`, `ruleExpectation`, `reasonShort`, and for the warning wording check `wordingDiff`, `matchedWords`, `totalWords`), every panel carries `qualitySummary`, and every result carries `beverageInference`, `warningEvidence`, and `badImage`. They render governed states in plain language; they never change a state.

## Image guidance

For UAT, use 2400 by 3200 pixels in portrait or 3200 by 2400 in landscape, 300 PPI metadata, JPEG quality 85 to 92, and approximately 1 to 4 MiB per file. Keep the label at least 60 percent of the frame and important characters at least 20 pixels high. A 736 by 532 image can work when sharp and tightly framed, but it is below the recommended evidence density.

PPI metadata does not prove physical type size. Reliable millimeter validation requires a trustworthy scale or known capture geometry.

## Regulatory approach

The selected rule registry is based on the current TTB and eCFR sources listed in `contracts/regulatory-rules-v1.json`. Every applied rule was re-verified against its primary source on 2026-09-03; the rule-by-rule record, including what the application does with each rule and what a photograph cannot decide, is in [`docs/08-validation/REGULATORY_VALIDATION.md`](docs/08-validation/REGULATORY_VALIDATION.md).

- Malt beverages: recognized class/type, limitations on `IPA` alone, U.S. customary net quantity, alcohol-statement triggers, prohibited ranges, decimal precision, and formula or state-law dependencies. `ABV` is not accepted as an abbreviation.
- Wine: numeric alcohol rules, permitted range span and the 14 percent boundary, the table/light wine exception, conditional appellation, and sulfite declaration dependent on chemistry.
- Distilled spirits: required alcohol content, same-field-of-vision evaluation for brand, class/type, and ABV, plus optional proof comparison and distinction.
- All families at 0.5 percent ABV or more: exact government warning content and presentation checks. Wine and distilled spirits, and malt beverages with a recognized class designation, are above that threshold by definition, so the warning is required even when the alcohol statement could not be read.
- Wine: a missing sulfite declaration and a varietal or vintage designation without an appellation are review items, because only the application can waive the first and the second is a brand-label placement rule.

The UI label `Approve` records a reviewer's prototype disposition. It does not alter machine evidence.

## Assumptions

- One to three submitted panels represent one product after user confirmation.
- Product grouping can use folder and filename cues, but ambiguity requires confirmation.
- The take-home prototype uses synthetic or sanitized data.
- No trusted COLA application record, formula, chemistry result, physical scale, state rule set, identity provider, or agency records schedule is supplied.
- The selected federal rules are evidence checks, not a replacement for the complete agency review process.
- Type weight (bold heading, regular body) and contrast are measured on the OCR view; a measurement that is not clearly decisive is a review item, and type weight is never a rejection on its own.
- When application values are entered, the label-wide search can only rescue a field that extraction read wrongly or missed; a statement that breaks a format or placement rule stays a difference whatever the application says.

## Trade-offs

- Local CPU OCR avoids blocked cloud endpoints and data egress, but throughput depends on host hardware.
- Sequential batch processing prioritizes predictable resources and fault isolation over maximum parallel speed.
- A modular monolith is simpler to build, run, test, and deploy for this scope. Typed boundaries preserve a path to separate services later.
- SQLite plus local files makes the 500-record workflow easy to evaluate. A production Azure deployment should select durable managed storage.
- Anonymous browser-scope history avoids an account setup step for UAT. Production requires agency identity and role-based authorization.
- Typography and image heuristics can identify strong visual evidence, but uncertain emphasis, contrast, or physical size remains human review. Stroke width measured on OCR boxes is comparable within one statement (heading against body) but not against an absolute scale, so the weight checks only assert bold when the heading is clearly heavier than the body.
- Silent type inference reduces user work, but unresolved or conflicting signals are shown rather than guessed.
- Bounded exact-pixel OCR result reuse makes confirmed batch reruns fast without using filenames or product-specific expected values. Cache misses always execute the same local OCR and rules pipeline.

## Limitations

- Label-first OCR can test visible label evidence but cannot prove equality with an independent application record. The separate verification endpoint supports that comparison when a trusted source is later available.
- Formula-dependent malt rules, chemistry-dependent sulfite rules, wine below 7 percent jurisdiction, state requirements, permit truth, and production records cannot be decided from pixels alone.
- Ordinary images do not provide reliable physical type size.
- Glare removal, curved-bottle unwarping, and restoration of missing pixels are not guaranteed. Unreadable evidence requests review or another image.
- Highly stylized, curved, very small, or decorative text can be read partially. Generic layout and context ranking support the validated spirits, wine, vodka, and beer cases, but uncertain fields remain Review and require the reviewer to inspect the highlighted pixels.
- OCR engine confidence is not a calibrated compliance probability.
- The private corpus is scored against a pixel ground truth and a disposition oracle by an evaluation harness the runtime never reads. Most real labels are routed to review rather than reported clean, because warning punctuation, type weight, and contrast are measured from a photograph and left to the reviewer when not decisive; requester UAT still decides field-level and legal-label acceptance.
- Local history in the Azure demo can reset on container revision or instance lifecycle. Production needs durable storage, identity, audit, retention, backup, legal hold, and recovery controls.
- Clearing browser storage loses access to that browser scope's retained demo history. The cookie is intentionally unreadable to JavaScript, SameSite Strict, and Secure on the Azure deployment.
- The 500-record FIFO is global within the single-instance demo. A busy browser scope can therefore evict the oldest record created by another scope even though record access remains scope-isolated.
- Selecting the maximum 900-image batch keeps browser `File` objects and preview URLs in memory while the workspace is open. Server requests remain bounded, but practical browser memory depends on the operator workstation and image sizes.
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
