# Clarification Log

This log is append-only in intent. Corrections add a superseding event rather than erase decision history.

| Event ID | Timestamp | Actor | Channel | Decision / artifact | Event | Answer type | State after event |
|---|---|---|---|---|---|---|---|
| `EVT-001` | 2026-08-31 | Requester | Codex conversation | Project creation authority | Requested a full local Intake package and deferred GitHub setup until agreement. | STATED | Local planning authorized; Git/GitHub not yet requested. |
| `EVT-002` | 2026-08-31 | Intake author | Local document | `DEC-001` | Proposed a narrow distilled-spirits path. | PROPOSED | OPEN |
| `EVT-003` | 2026-08-31 | Intake author | Local document | `DEC-002` | Proposed batch after the core. | PROPOSED | OPEN |
| `EVT-004` | 2026-08-31 | Intake author | Local document | `DEC-003` | Proposed a measurable fixture and latency contract. | PROPOSED | OPEN |
| `EVT-005` | 2026-08-31 | Requester | Codex conversation | Release deliverables | Reconfirmed repository, source, README, and brief documentation deliverables. | STATED | Added to release scope. |
| `EVT-006` | 2026-08-31 | Requester | Codex conversation | Writing convention | Prohibited em dashes. | STATED | Applies to all project content. |
| `EVT-007` | 2026-08-31 | Requester | Codex conversation | Design references | Supplied Grok and Gemini PDFs/images for design consideration. | STATED | Classified as inspirational evidence. |
| `EVT-008` | 2026-08-31 | Requester | Codex conversation | Stage review process | Required three independent red-team reviews at Intake and every later completion gate. | STATED | Unanimous CLEAR required before advancement. |
| `EVT-009` | 2026-08-31 | Intake RT1/RT2/RT3 | Local reports | Intake revision 1 | All three reviewers independently returned REWORK_REQUIRED. | VERIFIED REVIEW | Intake remained open. |
| `EVT-010` | 2026-08-31 | Intake author | Local remediation | Review findings | Corrected scope overclaim, panel contract, latency, fixtures, aggregation, accessibility, privacy, source durability, and design dispositions. | RECONSTRUCTED | Pending independent re-review. |
| `EVT-011` | 2026-08-31 | Requester | Codex conversation | `DEC-001`, `DEC-002`, `DEC-003` | Authorized the project to proceed through Intake, BAIRD, I2R, BI, and FRD using the right bounded decisions while maintaining close traceability to the assignment. The selected outcomes are the remediated narrow profile, gated batch objective, and corrected success contract. | STATED authorization plus documented bounded selection | CLOSED |
| `EVT-012` | 2026-08-31 | Intake RT1/RT2/RT3 | Local re-review reports | Intake gate | After two targeted correction cycles, RT1, RT2, and RT3 each returned CLEAR with no material finding remaining. | VERIFIED REVIEW | INTAKE CLEAR; BAIRD authorized |
| `EVT-013` | 2026-08-31 | BAIRD author under `EVT-011` bounded authority | Local remediation | `DEC-003` latency clarification | Proposed a 7.5 second hard safety deadline during technical analysis while retaining the five-second warmed valid-result p95 outcome. | RECONSTRUCTED technical proposal | SUPERSEDED by `EVT-014`; exact timeout belongs to I2R A&E |
| `EVT-014` | 2026-08-31 | Requester | Codex conversation | Process definition | Clarified that BAIRD validates the Intake against discovery only. Architecture, engineering, workflow, data, stack, hosting, limits, and feasibility decisions belong to I2R A&E. FRD defines features. BI defines work packages, standards, testing, UAT, and DoD. | STATED | Process corrected; downstream technical decisions removed from the Intake baseline |

## Decision record

| Decision | Final state | Selected outcome | Attesting event |
|---|---|---|---|
| `DEC-001` | CLOSED | Selected-check distilled-spirits demo profile, 1 to 6 panel images, explicit exclusions, no comprehensive compliance claim | `EVT-011` |
| `DEC-002` | CLOSED | Batch is a Should-level secondary objective gated after the single-submission release gate | `EVT-011` |
| `DEC-003` | CLOSED | Corrected fixture, five-second warmed valid-result latency outcome, all-attempt completion, aggregation, accessibility, security/privacy, and release contract. Exact technical timeout remains an I2R A&E decision. | `EVT-011`, process-corrected by `EVT-014` |

## Attestation state

| Artifact | Current state | Attesting event |
|---|---|---|
| `success-definition.md` | ATTESTED | `EVT-011` |
| `scope-boundary.md` | ATTESTED | `EVT-011` |

The Intake gate was completed under `EVT-012`. BAIRD now validates the corrected Intake-only baseline under `EVT-014` before I2R A&E begins.
