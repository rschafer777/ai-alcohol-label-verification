# OCR Model and Asset Bill of Materials

**Decision:** Approved for the take-home prototype with the notice and hash controls below. A missing notice, wrong hash, or unresolved redistribution change is a release stop.

## Selected OCR artifacts

| Role | Artifact | Upstream version and source | Bytes | SHA-256 | Expected image path |
|---|---|---|---:|---|---|
| Text detector | `en_PP-OCRv3_det_infer.onnx` | RapidOCR model set v3.4.0, ModelScope `RapidAI/RapidOCR`, converted from PaddleOCR | 2,421,707 | `ea07c15d38ac40cd69da3c493444ec75b44ff23840553ff8ba102c1219ed39c2` | `/app/models/en_PP-OCRv3_det_infer.onnx` |
| Text recognizer | `en_PP-OCRv4_rec_infer.onnx` | RapidOCR model set v3.4.0, ModelScope `RapidAI/RapidOCR`, converted from PaddleOCR | 7,653,044 | `e8770c967605983d1570cdf5352041dfb68fa0c21664f49f47b155abd3e0e318` | `/app/models/en_PP-OCRv4_rec_infer.onnx` |
| Orientation classifier | `ch_ppocr_mobile_v2.0_cls_infer.onnx` | RapidOCR model set v3.4.0, ModelScope `RapidAI/RapidOCR`, converted from PaddleOCR | 585,532 | `e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c` | `/app/models/ch_ppocr_mobile_v2.0_cls_infer.onnx` |

Exact upstream URLs are declared by RapidOCR 3.4.2 in `default_models.yaml`. Builds may fetch them only during the controlled image-build stage. Runtime download code is disabled and the runtime image has no package cache or downloader configuration.

## Rights and notices

- RapidOCR engineering code is Apache License 2.0.
- The RapidOCR project explicitly identifies Baidu as the OCR model copyright holder.
- PaddleOCR publishes the PP-OCR model family and project under Apache License 2.0.
- The release must include the Apache 2.0 text, RapidOCR notice, PaddleOCR notice, Baidu model attribution, model filenames, sources, versions, and hashes in `THIRD_PARTY_NOTICES.md`.
- Model binaries are not committed to Git. They are fetched from the pinned upstream URLs in the image build, hash-verified before use, and present only in the immutable OCI image and build cache.
- Any upstream license or notice change requires re-review before another image is built.

This is a repository compliance decision for a take-home prototype, not legal advice. If a later employer review requires counsel approval, the image must not be promoted until that approval exists.

## Other bundled visual asset

RapidOCR's downloadable `FZYTK.TTF` is not selected. The product will supply a separately registered open-font file for any OCR visualization path, or disable library visualization entirely. Product UI fonts use web-safe/system stacks unless an OFL-licensed font is deliberately added to the application asset register.

## Build and runtime controls

1. Fetch each selected artifact over HTTPS only in the controlled build stage.
2. Verify the exact SHA-256 before copying into the runtime stage.
3. Delete unused default Chinese detector and recognizer files from the runtime stage.
4. Record model hashes in `/app/release-manifest.json` and the image SBOM.
5. Start the application with explicit absolute model paths.
6. Fail readiness if any file is absent, writable by the runtime user, or has the wrong hash.
7. Complete one representative warmup inference before readiness succeeds.
8. Run the final container with outbound TCP 65535 as the sole allowed port and verify conventional DNS 53, HTTP 80, and HTTPS 443 are denied. This port policy does not prove that arbitrary traffic over 65535 is impossible.

## Alternative disposition

Tesseract.js and its trained data have a clearer Apache-licensed distribution path and were explored during early technical research. The exact historical comparison inputs and resolved runtime assets were not retained, so those runs do not provide a reproducible full result-contract qualification and no historical field-miss or timing claim controls selection. Tesseract.js is therefore not qualified as the primary adapter. Full PaddleOCR is not an untested automatic fallback.
