# Assumptions

This register contains working hypotheses for later research. Closed scope decisions are recorded in the clarification log, not hidden as assumptions. Removing an assumption must not silently change WHAT, WHO, SUCCESS, BOUNDARY, or AUTHORITY.

| Assumption ID | Working hypothesis | Why needed now | Falsification / verification path | Reversible? | Load-bearing? | Current treatment |
|---|---|---|---|---|---|---|
| `ASM-001` | The evaluator will use a modern desktop browser with JavaScript enabled. | Frames the browser-based prototype concept. | Document supported browsers; test a clean current Chromium browser and one alternative. | Yes | No | Research/FRD validates. |
| `ASM-002` | Demo inputs contain no real PII or protected application data. | Supports ephemeral, low-risk prototype handling. | Use only generated or explicitly sanitized fixtures; inspect repository before release. | Yes | No | Enforced as fixture policy. |
| `ASM-003` | A manual structured form plus Try sample is acceptable for the reference input. | The assignment omits an application-data schema. | I2R usability test and evaluator-path review. | Yes | No | Scope decision closed; exact schema remains research. |
| `ASM-004` | The selected-check distilled-spirits profile is the most defensible core because the assignment supplies that sample. | Supports a bounded rule profile without a completeness claim. | BAIRD requirements validation and FRD acceptance review. | Yes | No | Confirmed by `DEC-001`. |
| `ASM-005` | Batch can be sequenced after the single-submission gate. | Protects the working-core preference. | I2R A&E estimate and post-core go/no-go gate. | Yes | No | Confirmed by `DEC-002`. |
| `ASM-006` | Test fixtures can stand in for unavailable real COLA data without misrepresenting production accuracy. | A reproducible test suite is required. | Clearly label fixtures synthetic; report limitations; never claim representative production accuracy. | Yes | No | Allowed with disclosure. |
| `ASM-007` | A suitable input and deployment envelope can meet valid-result warmed p95 at or below five seconds while avoiding the rejected 30 to 40 second experience. | The five-second stakeholder expectation requires an executable architecture and benchmark. | I2R A&E feasibility evidence plus deployed benchmark; change architecture if falsified. | Yes | Yes | Open technical hypothesis. I2R A&E must select the architecture and limits. Deployment and validation must prove the final result. |
| `ASM-008` | The app can operate without storing uploaded images or form data after the request completes. | Minimizes privacy/security scope. | Architecture review and storage/network inspection; tests verify no persistence path. | Yes | No | Preferred constraint. |
| `ASM-009` | Some label-format requirements will remain “Not verified” because arbitrary images lack physical scale or reliable typography evidence. | Prevents overclaiming. | I2R A&E and FRD feasibility analysis by check; fixture validation. | Yes | No | Safety constraint, not a defect. |
| `ASM-010` | A public demo can be hosted within a reasonable free/low-cost tier. | A deployed URL is mandatory but budget is unspecified. | Compare current platforms, limits, cold starts, and OCR/runtime needs in analysis. | Yes | No | Implementation decision. |
| `ASM-011` | Up to six panel images are enough to represent a bounded label submission for the demo profile. | Multi-panel evidence is required but production artwork packaging is unspecified. | Fixture coverage and I2R upload usability test. | Yes | No | Provisional input envelope. |
| `ASM-012` | A corpus of at least 24 submissions with a 6-submission holdout is sufficient to demonstrate prototype behavior without claiming production accuracy. | The assignment provides no labeled evaluation set. | I2R A&E validation design, mutation coverage, anti-hard-coding test, and Validation Protocol results. | Yes | Yes | Open technical hypothesis. I2R A&E must define the corpus and controls. Construction and holdout integrity remain release gates. |

## Assumption control summary

- Total assumptions: 12
- Load-bearing technical assumptions: 2 (`ASM-007`, `ASM-012`)
- Human scope decisions disguised as assumptions: 0
- Result: Intake identifies the hypotheses and success conditions. BAIRD validates that they faithfully represent discovery. I2R A&E must resolve the technical hypotheses before FRD and BI approval.
