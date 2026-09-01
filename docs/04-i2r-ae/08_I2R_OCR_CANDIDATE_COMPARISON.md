# I2R OCR Candidate Comparison

Document control ID: LV-I2R-008  
Revision: 1.0  
Date: 2026-08-31  
Status: Controlled I2R evidence summary

## Decision criteria

The primary adapter must provide offline runtime operation, text regions, sufficient selected-field recovery, bounded CPU latency, reproducible assets, acceptable licensing/notice obligations, and a stable adapter boundary.

## Candidate qualification comparison

The selection gate requires a reproducible full result-contract proof. Historical measurements that lack sealed inputs or runtime assets are exploratory only and cannot pass the gate.

| Criterion | RapidOCR 3.4.2 with ONNX Runtime | Tesseract.js 6.0.1 | External vision API |
|---|---|---|---|
| Runtime egress | PASS, no runtime egress after controlled build | POSSIBLE if worker/core/language assets are bundled, but not proven by a controlled full pipeline | FAIL for the restricted-network core unless an approved reachable endpoint and fallback are proven |
| Evidence regions | PASS, public adapter returns token polygons | NOT PROVEN in a sealed result-contract harness | Provider-dependent and not evaluated |
| Reproducible assets | PASS, exact model filenames, hashes, versions, and notices | PARTIAL, npm package lock exists but historical sheet inputs and language/runtime asset hashes were not retained | Not evaluated |
| Complete selected-check result | PASS on the legacy 17-check research registry | NOT PROVEN | Not evaluated |
| Repeated warm evidence | PASS, 74 direct and 74 browser attempts | Historical recognition-only runs exist but are non-decisional | None |
| Full browser timing | PASS, p95 3963.00 ms on the immutable current raw run set | NOT PROVEN | None |
| Correctness evidence | PASS on 1,258 legacy-registry field rows with zero research-oracle errors | NOT PROVEN | None |
| License and notices | Apache 2.0 code; model and Baidu/Paddle notices required | Apache-family package path; language asset notice still must be controlled | Provider contract dependent |
| Cold-start risk | OPEN, current local p95 10,949.98 ms misses BR-026 | Unknown full-pipeline cold behavior | Network/provider dependent |
| Qualification | QUALIFIED with open cold/deployed gates | NOT QUALIFIED due missing controlled full-contract evidence | DISQUALIFIED for the current restricted-network core |

Controlled decision evidence:

- `docs/baird/evidence/rapidocr-server-runs.csv`
- `docs/baird/evidence/browser-runs.json`
- `docs/baird/evidence/cold-start-runs.json`
- `docs/baird/evidence/MODEL_BOM.md`
- `research/baird-spike/requirements-research.lock`

Historical non-decisional evidence:

- `docs/baird/evidence/tesseract-runs.json` and `research/baird-spike/tesseract_benchmark.mjs` are preserved only to show that Tesseract.js was explored. The exact historical contact sheets and downloaded language/runtime assets were not retained, so the runs are not reproducible and no field-miss or timing claim from them controls this decision.
- `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md` is superseded for quantitative metrics because it describes an earlier raw run set. LV-I2R-001 and the immutable raw JSON/CSV files define the current metrics.

## Selection

RapidOCR remains selected because it is the only qualified candidate with controlled complete evidence-linked results, exact runtime assets, and a full browser benchmark. Tesseract.js is not rejected on an unsupported field-miss claim. It is not selected because it lacks a controlled, reproducible full result-contract proof. External APIs do not satisfy the restricted-network core requirement.

The selection remains behind the extraction port. Any final product false clean, systematic field-family failure, model-rights issue, deployed p95 failure, or unresolved cold-start failure reopens `ADR-004` before release.
