# Dependency and Model Inventory

Document control ID: LV-REL-001  
Revision: 0.1  
Date: 2026-09-01  
Status: Local release candidate preparation

## Machine-readable inventories

| Inventory | Scope | SHA-256 at generation |
|---|---|---|
| `sbom-python.cdx.json` | Locked production Python dependency graph in CycloneDX 1.5 format | `841a763a43be2123b4b4a3dd80b368883f40d9c2cf6a880f6c9b7c7e9d90af8a` |
| `sbom-frontend.cdx.json` | Locked production frontend dependency graph in CycloneDX 1.5 format | `db160ac9c3417df87cd66abedfb2b520dcdb34c00eaa14ffedd20aec4b86804a` |
| `../../ops/model-manifest.json` | Governed OCR model source, identity, license, filename, and SHA-256 values | `7714d5092c8458c8b2a94975ad6ab1f350b8ff087e5713102c94ea4d0aa6d8dc` |

The Python SBOM was regenerated from `uv.lock` with uv 0.11.32 after the security correction loop upgraded FastAPI to 0.141.1, Starlette to 1.6.0, Pillow to 12.3.0, and python-multipart to 0.0.32. The frontend SBOM was constructed deterministically from `frontend/package-lock.json` after npm 11.9.0 produced an empty graph for this private package. Its four production components and three direct root dependencies were verified against `npm ls --omit=dev --all --json`. The lockfiles remain the installation authority.

On 2026-09-01, `pip-audit` reported no known vulnerabilities in the complete synchronized Python environment after pytest was upgraded to 9.1.1. `npm audit --omit=dev` reported zero production vulnerabilities. These results are time-bound release evidence and must be repeated immediately before a public release.

## OCR model bill of materials

| Role | Artifact | SHA-256 |
|---|---|---|
| Detector | `en_PP-OCRv3_det_infer.onnx` | `ea07c15d38ac40cd69da3c493444ec75b44ff23840553ff8ba102c1219ed39c2` |
| Recognizer | `en_PP-OCRv4_rec_infer.onnx` | `e8770c967605983d1570cdf5352041dfb68fa0c21664f49f47b155abd3e0e318` |
| Orientation classifier | `ch_ppocr_mobile_v2.0_cls_infer.onnx` | `e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c` |

The models originate from PaddleOCR distributions published through RapidOCR. RapidOCR identifies the project as Apache-2.0 and notes that OCR model copyright belongs to Baidu. The exact source URLs and governed hashes are recorded in `ops/model-manifest.json`.

## License handling

- Third-party components remain subject to their own licenses and notices.
- The SBOM and package lockfiles identify the exact dependency versions used by this candidate.
- The requester has not selected a license for the take-home project's original source. No project-source license is asserted here.
- A final repository should include any license and notice files required by the selected distribution posture before public publication.
