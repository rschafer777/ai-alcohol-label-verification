# Contract Change Ledger

Document control ID: LV-DEV-CCL-001  
Revision: 1.0  
Date: 2026-09-01  
Status: Accepted for the corrected Azure OCR candidate

## 1. Purpose

This ledger implements the LV-BI-001 `CG-001` change-control requirement. It records every accepted post-baseline change to a governed request, result, evidence, error, limit, selected-check, or regulatory contract. A change is not accepted until its consumers, regressions, and reviewers are identified.

## 2. Accepted changes

| Change ID | Artifact and field | Prior SHA-256 | New SHA-256 | Rationale | Affected requirements and tests | Affected work packages | Owner | Reviewers | Status |
|---|---|---|---|---|---|---|---|---|---|
| `CC-001` | `contracts/api-contract-v1.json`, `limits.workerDeadlineSeconds`, 6.25 to 9.0 seconds | `b7eb6b2e0c4082259f01fe5339dc2fe8ca3191a7831b11629c9fa202d852bb47` | `cc6e9463792efd50447fce6303fb8307bd6b462f5695cafd3e7880298a71e72a` | Independent Azure UAT reproduced a complete two-panel request reaching the 6.25-second child boundary on the constrained public CPU profile. The 9-second limit preserves the stakeholder's approximately 5-second normal target while admitting the explicitly governed 5-to-9-second difficult-image range. The 30-second server and 35-second browser deadlines remain unchanged. | `FR-009`, `FR-011`, `FR-025`, `FR-028`, `FR-029`, `FR-031`, `FR-041`, `FR-050`; `T-009`, `T-011`, `T-025`, `T-028`, `T-029`, `T-031`, `T-041`, `T-050` | `WP-003`, `WP-004`, `WP-006`, `WP-008`, `WP-009`, `WP-012`, `WP-017`, `WP-019`, `WP-020` | `INT-LEAD` | `ENG-BE`, `ENG-FE`, `VV-LEAD`, three independent release RT reviewers | ACCEPTED |

## 3. Consumer synchronization

`CC-001` synchronizes these consumers to the new contract hash and value:

- backend contract loading and supervisor defaults;
- generated frontend contract metadata;
- fixture and sample manifests;
- fixture, oracle, product-corpus, security, and total-phase validators;
- real-sample, six-panel, contract, and deployment tests;
- README, I2R, FRD, implementation, validation, defect, and release records; and
- the staged-tree release manifest and assertion-ledger artifact bindings.

The change does not alter request size limits, result fields, selected checks, deterministic rule states, error codes, the 20-second upload deadline, the 30-second server deadline, or the 35-second browser deadline.

## 4. Required regression and acceptance commands

The accepted correction ran these commands against the synchronized consumers:

```powershell
uv run python scripts/generate_frontend_contract.py
uv run pytest backend/tests/test_contracts.py backend/tests/test_rapidocr_adapter.py backend/tests/test_real_sample_integration.py tests/validation/test_fixture_corpus.py tests/validation/test_azure_deployment_contract.py
uv run python scripts/validate_fixture_corpus.py
uv run python scripts/validate_product_corpus.py
uv run python scripts/run_performance_validation.py
uv run python scripts/run_batch_performance_validation.py --count 300 --output docs/08-validation/evidence/local-batch-performance.json
uv run python scripts/run_security_post_fix_validation.py
uv run python scripts/run_total_phase_matrix.py
uv run python scripts/run_root_gate_evidence.py
```

Acceptance results are retained in `docs/08-validation/evidence/`. The full local gate passed 197 Python tests, 46 frontend tests, the production build, Chrome and Edge core journeys, Chrome privacy, and the prohibited Unicode dash scan. The 30-case product corpus, 300-application batch, local warm and cold performance gates, and focused contract and deployment tests also passed.

## 5. Deployment closure

Protected run `33583826159` closed the public technical proof for `CC-001`. It passed immutable OCI construction, local-digest readiness, Azure configuration readback, and three consecutive public sample verifications with mean duration 4,714.500 ms and maximum duration 5,027.237 ms. Independent browser and direct API UAT then passed. The final documentation-only publication commit must repeat the protected workflow so the public build ID matches the final source snapshot. Requester code review, requester UAT, and final submission approval remain separate gates.
