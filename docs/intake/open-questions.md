# Open Questions

## Closed Checkpoint A decisions

| Decision ID | Decision | Ownership | State | Evidence |
|---|---|---|---|---|
| `DEC-001` | Use a selected-check distilled-spirits demo profile. Do not claim comprehensive distilled-spirits or TTB verification. Accept 1 to 6 panel images per submission. | SCOPE | CLOSED | `USR-008`, `EVT-011`, `scope-boundary.md` |
| `DEC-002` | Treat batch as a gated Should-level secondary objective after the single-submission release gate. Preserve batch compatibility even if the submission omits it. | SCOPE | CLOSED | `USR-008`, `EVT-011`, `scope-boundary.md` |
| `DEC-003` | Use the corrected valid-result latency, fixture/holdout, aggregation, accessibility, privacy, and release contract. A quick failure cannot satisfy valid-input success. | VISION / SUCCESS | CLOSED | `USR-008`, `EVT-011`, `success-definition.md` |

## I2R A&E research questions

These questions require evidence-backed technical decisions. They are not requester blockers unless analysis exposes a material scope, cost, credential, or legal issue.

| Research ID | Question | Owner | Required output |
|---|---|---|---|
| `RQ-001` | Which OCR/vision approach best meets latency, image quality, deployment, license, blocked-egress, and reproducibility constraints? | I2R A&E | Compared candidates, benchmark, selection, adapter contract, fallback |
| `RQ-002` | What bounded preprocessing improves rotation, perspective, lighting, and glare tolerance while preserving the original? | I2R A&E | Pipeline, thresholds, evidence behavior, tests |
| `RQ-003` | Which selected warning checks are deterministic, heuristic, or not provable from supplied images? | I2R A&E and regulatory analysis | Capability matrix and permitted result wording |
| `RQ-004` | What normalization is safe for brand, class/type, ABV/proof, net units, names/addresses, and origin? | I2R A&E | Per-field comparison policy and Review boundaries |
| `RQ-005` | What exact reference-record and multi-panel upload schemas minimize user effort and ambiguity? | I2R/UX | Types, required/conditional fields, validation, sample data |
| `RQ-006` | Which deployment platform provides a public URL, stable latency, safe secret handling, observability, and rollback? | I2R A&E | Platform ADR, cost/limit evidence, deployment plan |
| `RQ-007` | Can a self-contained or no-external-inference core meet the fixture and latency contract? | I2R A&E | Feasibility benchmark and blocked-egress test |
| `RQ-008` | How should the 24-fixture corpus and 6-fixture holdout be composed without implying production representativeness? | I2R/validation | Fixture manifest, coverage matrix, expected outcomes, anti-hard-coding control |
| `RQ-009` | How will the UI expose regions, crops, snippets, confidence provenance, and unavailable evidence without clutter? | I2R/UX | Information architecture, interaction contract, accessibility proof |
| `RQ-010` | What current TTB guidance and eCFR authority belongs in the rule registry? | I2R A&E and regulatory analysis | Source/version register and release re-verification step |
| `RQ-011` | What public-upload threat model and resource envelope are compatible with the selected stack? | I2R A&E and security analysis | Data-flow diagram, abuse cases, limits, cleanup, logging contract |
| `RQ-012` | Can the secondary batch objective safely prove up to 250 synthetic rows without threatening the core? | I2R A&E | Go/no-go gate, manifest, performance model, security limits |
| `RQ-013` | Which exact extraction result fields are required across every adapter? | I2R A&E | Raw text, candidate, region, confidence provenance, duration, error, provider/model version |
| `RQ-014` | What supported browser and deployment-region envelope will be used for performance and accessibility evidence? | I2R | Test matrix and recorded environment |

## Closed or intentionally excluded questions

- Direct COLA integration is not required.
- Production federal authorization is not required.
- Wine and malt-beverage rule coverage is not part of the selected profile.
- The requester does not need to choose language, framework, OCR library, model, or host before I2R A&E.
- Mobile-specific layout is deferred.
