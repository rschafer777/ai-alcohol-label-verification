# Development Contract Baseline

Document control ID: LV-DEV-001  
Revision: 1.0  
Date: 2026-09-01  
Status: Accepted for `CG-001` through `CG-004`

The following root-controlled files implement the initial contract handoff:

| Contract | SHA-256 |
|---|---|
| `contracts/api-contract-v1.json` | `cc6e9463792efd50447fce6303fb8307bd6b462f5695cafd3e7880298a71e72a` |
| `contracts/error-registry-v1.json` | `41fa16e582d528e1fe9df7ad13feed557d788daa253bf7f2b628f87dde970fa7` |
| `contracts/selected-check-registry-v1.json` | `521d7a1dbdb3872086083e92a6f37e459c48ad5471a09f3f92c23472b7dc8b13` |
| `contracts/regulatory-rules-v1.json` | `6d1c9866738a1b863ff8572c29881195005861b2198c2e364c4b5ff0fbf2e6c2` |

They are derived from LV-I2R-002, LV-I2R-006, LV-I2R-007, LV-I2R-008, the FRD, and the cleared 19-check registry. Backend, frontend, and validation implementations consume these identifiers and limits. They do not edit these files directly.

Acceptance requires:

1. JSON parse success;
2. exactly 19 unique selected checks;
3. exactly 23 unique server errors and 4 unique browser-only errors;
4. request and runtime limits equal the cleared I2R values;
5. backend, frontend, and validation reviewers record the hashes before dependent integration begins.

Any later change follows LV-BI-001 `CG-001` and the contract-change ledger.

## Role acceptance

| Role | Status | Evidence |
|---|---|---|
| `ENG-BE` | ACCEPTED | All four hashes match; 19 unique checks including 10 warning checks; 23 server and 4 browser errors; all limits match |
| `ENG-FE` | ACCEPTED | All four hashes match; JSON parse/count/limit verification passed |
| `VV-LEAD` | ACCEPTED | Independent parse, hash, unique-count, and limit verification passed |

`CG-001` result: ACCEPTED by all consuming roles. Dependent implementation may proceed.

## CG-004 generated frontend types

- Generated artifact: `frontend/src/api/generated-contract.ts`
- SHA-256: `11d4b80a78f7bdc0a2b70b94fae32c55eea16bb4be5aba83602c7da2c8227755`
- Generator owner: `INT-LEAD`
- Feature ownership: `ENG-FE` consumes but does not hand-edit
- Acceptance: ACCEPTED by `ENG-FE`; hash verified and temporary duplicate types replaced with imports/re-exports from the governed file

## CG-002 synthetic sample

| Artifact | SHA-256 |
|---|---|
| `fixtures/sample/sample-manifest-v1.json` | `95bafa2f3b82b0751df668ef0d9dc8b78354688362dd195a4623c4e592133c64` |
| `fixtures/sample/panels/panel-1.png` | `4df695b8cfb09f436676eb11497e0be2dd4af971941cfa67aa5c04e8ac7da72f` |
| `fixtures/sample/panels/panel-2.png` | `4e6624bf8de4f6b40ea321f5a24fc7f91bbdf005a7fd3283f34cfa2a560dff9b` |

The accepted sample is `S001`, sample ID `old-tom-distillery-v1`, profile `distilled_spirits_demo_v1`, and is explicitly synthetic. It contains two 1200 by 1600 PNG panels and an independent expected result of `No differences found in checked fields`.

## CG-003 fixture and oracle baseline

The initial accepted hashes below are retained as historical evidence of the development handoff. They were superseded during `VAL-004` after the complete product corpus exposed oracle expectations that depended on generator-only information or rejected contract-permitted safe equivalence. The correction changed no public API, selected check, regulatory rule, input limit, or product requirement.

| Artifact | SHA-256 |
|---|---|
| `fixtures/schema/fixture-manifest.schema.json` | `b37e6fd8fd2550424a226aa14be11bffb114fa8ba753aba7178295030558a360` |
| `fixtures/schema/oracle.schema.json` | `88238edada4a61fa6d2be8b16ba2c90d6aab134e69c88be3a4cd93e99095ae8d` |
| `fixtures/corpus-manifest-v1.json` | `cf55ca7c637c2e86ca23f7da19034edaaa906fb438b27b579e718941d2f87bb3` |
| `fixtures/holdout/SEAL.sha256` | `7dc3c01e10ff2272da05229cdaba8ee0a81f61f94daf3842263858990f3d7bb0` |
| `fixtures/mutations/mutation-plan-v1.json` | `12bc5b89317a4d398cf336f682f4c1c71f0475c10abd7f5aa117a0d88d6f3e06` |

Independent validation passed with 24 development cases, 6 sealed holdouts, 19 checks per case, 8 mutation controls, and 50 scenario tags. The focused validation suite passed 8 of 8 tests.

### CG-003A final corrected fixture and oracle baseline

The corrected package was regenerated, independently validated, consumer-tested through the production API, and resealed before the decisive corpus run.

| Artifact | Final authoritative SHA-256 |
|---|---|
| `fixtures/schema/fixture-manifest.schema.json` | `b37e6fd8fd2550424a226aa14be11bffb114fa8ba753aba7178295030558a360` |
| `fixtures/schema/oracle.schema.json` | `88238edada4a61fa6d2be8b16ba2c90d6aab134e69c88be3a4cd93e99095ae8d` |
| `fixtures/corpus-manifest-v1.json` | `c7ba0668714867274de73cdf4828eaf2dbabc20f22e2339520783fdfae5810a6` |
| `fixtures/oracle/corpus-oracle-index-v1.json` | `e72628e586d0ae929c7f7019dc0a728933beb0fdd5f253472b9fed84a27a5b1d` |
| `fixtures/holdout/SEAL.sha256` | `fa43f21aeaca64ce955970c6e03fc06a2fa4ddec08a2d7fa963d6c6af3f32830` |
| `fixtures/mutations/mutation-plan-v1.json` | `7b35bf40cb411443a49893ddd4eb5847d4e67d3d0c78d35f7414afa4b606e314` |

Final consumer acceptance evidence:

- fixture validator: 30 cases, 8 mutations, 50 scenario tags, and all 19 checks covered;
- validation suite: 20 passing tests;
- production corpus: 30 of 30 cases, 456 of 456 expected result rows, and 8 of 8 mutation controls;
- false-clean count: zero; and
- product-corpus failures: zero.

`CG-003A` is the authoritative release-candidate fixture baseline. The earlier CG-003 hash table is historical and must not be used to identify the current corpus.

## CG-004 parity proof

The read-only command `uv run python scripts/generate_frontend_contract.py` verifies the generated TypeScript surface against the source JSON contracts. It passed contract version, resource limits, all 19 selected checks, and all 27 public error codes.

`CG-001`, `CG-002`, `CG-003A`, and `CG-004` are the accepted current baselines. Any later change to these artifacts requires the formal contract-change process and renewed consumer verification.
