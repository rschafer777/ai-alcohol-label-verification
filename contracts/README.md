# Contract Registry

These machine-readable files govern the implemented LabelVerify interface, regulatory rule selection, check ordering, and public error behavior.

The filenames retain `v1` because they are the first published contract artifacts. Each document also carries its own semantic version. Backend startup verifies their SHA-256 values, and the frontend contract module is generated from the API and check registries.

## Presentation fields

`api-contract-v1.json` also allows display-only fields on each check (`group`, `shortLabel`, `ruleExpectation`, `reasonShort`, `wordingDiff`, `matchedWords`, `totalWords`). They are produced by `backend/labelverify/domain/presentation.py` from the check id, reason code, and observed warning text so the review interface never recomputes a rule. The `$defs` block adds `WordingToken`, `QualitySummary`, `BeverageInference`, and `WarningEvidence` for the same purpose.
