# OCR Model and Asset Bill of Materials

**Decision:** Approved for the take-home prototype with the notice and hash controls below. A missing notice, wrong hash, or unresolved redistribution change is a release stop.

## Selected OCR artifacts

| Role | Artifact | Upstream version and source | Bytes | SHA-256 | Expected image path |
|---|---|---|---:|---|---|
| Text detector | `en_PP-OCRv3_det_infer.onnx` | RapidOCR model set v3.4.0, ModelScope `RapidAI/RapidOCR`, converted from PaddleOCR | 2,421,707 | `ea07c15d38ac40cd69da3c493444ec75b44ff23840553ff8ba102c1219ed39c2` | `/app/models/en_PP-OCRv3_det_infer.onnx` |
| Text recognizer | `en_PP-OCRv4_rec_infer.onnx` | RapidOCR model set v3.4.0, ModelScope `RapidAI/RapidOCR`, converted from PaddleOCR | 7,653,044 | `e8770c967605983d1570cdf5352041dfb68fa0c21664f49f47b155abd3e0e318` | `/app/models/en_PP-OCRv4_rec_infer.onnx` |
| Orientation classifier | `ch_ppocr_mobile_v2.0_cls_infer.onnx` | RapidOCR model set v3.4.0, ModelScope `RapidAI/RapidOCR`, converted from PaddleOCR | 585,532 | `e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c` | `/app/models/ch_ppocr_mobile_v2.0_cls_infer.onnx` |
| OCR rendering font | `DejaVuSans.ttf` | DejaVu Fonts 2.37 official release archive | 757,076 | `7da195a74c55bef988d0d48f9508bd5d849425c1770dba5d7bfc6ce9ed848954` | `/app/models/DejaVuSans.ttf` |

Exact upstream URLs are recorded in `ops/model-manifest.json`. The three OCR model URLs are declared by RapidOCR 3.4.2 in `default_models.yaml`. The font is extracted from the official DejaVu Fonts 2.37 release archive. Controlled setup and image builds verify the source archive and extracted font hashes. Runtime download code is bypassed by the explicit local font path, and the runtime image has no package cache or downloader configuration.

## Rights and notices

- RapidOCR engineering code is Apache License 2.0.
- The RapidOCR project explicitly identifies Baidu as the OCR model copyright holder.
- PaddleOCR publishes the PP-OCR model family and project under Apache License 2.0.
- The release must include the Apache 2.0 text, RapidOCR notice, PaddleOCR notice, Baidu model attribution, model filenames, sources, versions, and hashes in `THIRD_PARTY_NOTICES.md`.
- Model binaries are not committed to Git. They are fetched from the pinned upstream URLs in the image build, hash-verified before use, and present only in the immutable OCI image and build cache.
- Any upstream license or notice change requires re-review before another image is built.
- DejaVu Sans 2.37 is distributed under the DejaVu Fonts license reproduced in `docs/10-release/third-party-licenses/DejaVu-fonts-2.37.txt`.

This is a repository compliance decision for a take-home prototype, not legal advice. If a later employer review requires counsel approval, the image must not be promoted until that approval exists.

## Other bundled visual asset

RapidOCR's downloadable `FZYTK.TTF` is not selected. The product supplies the separately registered DejaVu Sans 2.37 file for RapidOCR's warmup and visualization path. Product UI fonts continue to use web-safe system stacks.

## Build and runtime controls

1. Fetch each selected artifact over HTTPS only during controlled setup or image build.
2. Verify the exact source and output SHA-256 values before copying into the runtime stage.
3. Copy only the four registered output assets into the read-only runtime model directory.
4. Preserve upstream provenance and hashes in `ops/model-manifest.json`, and preserve the independent fail-closed runtime hash registry in `rapidocr_adapter.py`. A regression requires both registries to agree.
5. Start the application with explicit absolute model and font paths.
6. Fail readiness if any registered file is absent, writable by the runtime user, or has the wrong hash.
7. Complete one representative warmup inference before readiness succeeds.
8. Record the built image by immutable digest and generate its build SBOM attestation. The source manifest remains the authority for individual model and font hashes.
9. For a production authorization boundary, enforce and test the selected platform outbound policy. The current Azure Consumption demo does not claim a deny-by-default egress control.

## Alternative disposition

Tesseract.js and its trained data have a clearer Apache-licensed distribution path and were explored during early technical research. The exact historical comparison inputs and resolved runtime assets were not retained, so those runs do not provide a reproducible full result-contract qualification and no historical field-miss or timing claim controls selection. Tesseract.js is therefore not qualified as the primary adapter. Full PaddleOCR is not an untested automatic fallback.
