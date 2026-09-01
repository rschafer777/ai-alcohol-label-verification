# BAIRD Traceability Validation

`scripts/validate_baird_traceability.ps1` is the executable documentation gate. It fails on:

- missing, duplicate, or extra `SRC-001` through `SRC-058` rows;
- blank disposition, control, requirement, component/integration, test, stop-gate, or owner cells;
- missing, duplicate, or extra `ADR-001` through `ADR-012`, `BG-001` through `BG-008`, or `THR-001` through `THR-018` controls;
- missing, duplicate, or extra reserved `R-001` through `R-096` or `T-001` through `T-096` identifiers;
- control-evidence citations that point outside the reserved requirement or test set;
- missing, duplicate, or extra `FX-001` through `FX-030` fixture allocations;
- prohibited Unicode dash characters U+2010 through U+2015.

Run from the project root:

```powershell
powershell -NoProfile -File scripts/validate_baird_traceability.ps1
```

The machine check proves relation completeness and identifier integrity. The `proof_relation` column in `CONTROL_EVIDENCE_CITATIONS.csv` records the human semantic audit that the cited requirement and test actually address the named finding. Both checks are required. Identifier presence alone is not a BAIRD pass.

## Retained validation result

Run on 2026-08-31 from the project root after final BAIRD remediation:

```text
BAIRD_TRACEABILITY_VALID=True
SOURCE_ROWS=58
CONTROL_IDS=ADR12,BG8,THR18
REQUIREMENT_IDS=R001-R096
TEST_IDS=T001-T096
FIXTURE_IDS=FX001-FX030
PROHIBITED_UNICODE_DASHES=0
```
