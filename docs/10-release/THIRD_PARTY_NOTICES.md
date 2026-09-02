# Third-Party Notices

Document control ID: LV-REL-005  
Revision: 0.1  
Date: 2026-09-01

This notice applies only to third-party components and assets. It does not grant a license to the original LabelVerify source code. No project-level `LICENSE` file exists because the requester has not selected a license for that original source.

## RapidOCR and PaddleOCR model assets

LabelVerify uses RapidOCR 3.4.2 and three converted PP-OCR model assets identified by exact URL and SHA-256 in `ops/model-manifest.json`.

- RapidOCR engineering source: Apache License 2.0
- PaddleOCR engineering source: Apache License 2.0
- OCR model copyright attribution: Baidu
- Apache License 2.0 text: `third-party-licenses/Apache-2.0.txt`
- RapidOCR source and notice: https://github.com/RapidAI/RapidOCR
- PaddleOCR source and notice: https://github.com/PaddlePaddle/PaddleOCR

## DejaVu Sans 2.37

LabelVerify uses `DejaVuSans.ttf` from the official DejaVu Fonts 2.37 release archive solely as RapidOCR's local rendering font. The archive and extracted file hashes are pinned in `ops/model-manifest.json`.

- Project: DejaVu Fonts
- Release: 2.37
- Source: https://github.com/dejavu-fonts/dejavu-fonts/releases/tag/version_2_37
- License text: `third-party-licenses/DejaVu-fonts-2.37.txt`

## Other packages

The complete locked Python and frontend dependency inventories are in `sbom-python.cdx.json`, `sbom-frontend.cdx.json`, `uv.lock`, and `frontend/package-lock.json`. Each component remains subject to its own upstream license and notice terms.
