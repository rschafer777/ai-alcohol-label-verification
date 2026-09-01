# BAIRD Source Disposition Matrix

Document control ID: LV-BRD-002  
Revision: 1.0  
Date: 2026-08-31  
Status: Controlled with LV-BRD-001 Revision 2.2

## Purpose

This matrix proves that every Intake source requirement and requester decision has an explicit BAIRD disposition. CARRIED means the source is represented by an active `BR-NNN`. CONDITIONAL means it becomes active only after its named gate. BOUNDED QUESTION means BAIRD preserves the requirement while I2R A&E owns the technical decision. PROCESS means it governs the delivery method rather than product runtime behavior.

## Source requirement disposition

| Source | BAIRD mapping | Disposition | Notes |
|---|---|---|---|
| `SRC-001` | `BR-001`, `BR-003` | CARRIED | AI-powered working prototype |
| `SRC-002` | `BR-003`, `BR-007` | CARRIED | Compare expected and observed evidence |
| `SRC-003` | `BR-004` | CARRIED | Brand |
| `SRC-004` | `BR-004` | CARRIED | Alcohol content and proof |
| `SRC-005` | `BR-004`, `BR-009` | CARRIED | Warning text and supported presentation |
| `SRC-006` | `BR-004` | CARRIED | Selected spirits fields |
| `SRC-007` | `BR-001` | CARRIED | Standalone, no COLA integration |
| `SRC-008` | `BR-002`, `BQ-003` | CARRIED and BOUNDED QUESTION | Structured reference contract |
| `SRC-009` | `BR-008` | CARRIED | Human final judgment |
| `SRC-010` | `BR-002`, `BR-007`, `BR-018` | CARRIED | Multi-panel coverage and evidence |
| `SRC-011` | `BR-010` | CARRIED | Five-second warmed result |
| `SRC-012` | `BR-013` | CARRIED | Clean and obvious interface |
| `SRC-013` | `BR-013`, `BR-019` | CARRIED | Obvious primary action and Try sample |
| `SRC-014` | `BR-013`, `BR-017` | CARRIED | Plain language and recovery |
| `SRC-015` | `BR-014` | CARRIED | Non-color and accessibility envelope |
| `SRC-016` | `BR-014` | CARRIED | Keyboard and focus behavior |
| `SRC-017` | `BR-011`, `BR-017` | CARRIED | Honest processing status and timeout |
| `SRC-018` | `BR-007`, `BR-018` | CARRIED | Original evidence preservation |
| `SRC-019` | `BR-008` | CARRIED | Capitalization nuance |
| `SRC-020` | `BR-008`, `BQ-004` | CARRIED and BOUNDED QUESTION | Field-specific normalization policy |
| `SRC-021` | `BR-006`, `BR-021` | CARRIED | No false clean invariant |
| `SRC-022` | `BR-005` | CARRIED | Field states and aggregation |
| `SRC-023` | `BR-006`, `BR-017` | CARRIED | Image-quality failure distinction |
| `SRC-024` | `BR-003`, `BR-006`, `BR-007` | CARRIED | Confidence is evidence, not legal truth |
| `SRC-025` | `BR-004`, `BR-009`, `BR-022` | CARRIED | Warning applicability |
| `SRC-026` | `BR-009`, `BR-022` | CARRIED | Prescribed warning wording |
| `SRC-027` | `BR-009`, `BR-022` | CARRIED | Warning heading capitalization |
| `SRC-028` | `BR-009`, `BR-022` | CARRIED | Warning emphasis within evidence limits |
| `SRC-029` | `BR-009`, `BR-022` | CARRIED | Warning continuity, separation, contrast, legibility |
| `SRC-030` | `BR-009`, `BR-022`, `BQ-005` | CARRIED and BOUNDED QUESTION | Physical type-size limitation |
| `SRC-031` | `BR-004`, `BR-022` | CARRIED | Field-of-vision and panel coverage |
| `SRC-032` | `BR-004` | CARRIED AS BOUNDARY | Wine and malt beverages excluded from the profile |
| `SRC-033` | `BR-009`, `BR-022` | CARRIED | Regulatory source versioning |
| `SRC-034` | `BR-018`, `BQ-002` | CARRIED and BOUNDED QUESTION | Bounded image degradation support |
| `SRC-035` | `BR-015`, `BR-021`, `BQ-009` | CARRIED and BOUNDED QUESTION | Safe input and resource limits |
| `SRC-036` | `BR-003`, `BR-006`, `BR-021` | CARRIED | Never invent unreadable text |
| `SRC-037` | `BR-012`, `BR-017`, `BQ-001`, `BQ-008` | CONDITIONAL CARRIED | External inference failure behavior applies if used |
| `SRC-038` | `BR-012`, `BQ-001`, `BQ-008`, `BQ-011` | CARRIED and BOUNDED QUESTION | Restricted outbound environment |
| `SRC-039` | `BR-011`, `BR-017`, `BQ-009` | CARRIED and BOUNDED QUESTION | Timeout and recovery |
| `SRC-040` | `BR-020`, `BQ-013` | CONDITIONAL | Batch is post-core only |
| `SRC-041` | `BR-020`, `BQ-013` | CONDITIONAL | Manifest and safe filename rule if batch is GO |
| `SRC-042` | `BR-020`, `BQ-013` | CONDITIONAL | Row isolation, progress, cancellation, retry if batch is GO |
| `SRC-043` | `BR-020`, `BQ-013` | CONDITIONAL | Exception-first review if batch is GO |
| `SRC-044` | `BR-020`, `BQ-013` | CONDITIONAL | Machine-readable export if batch is GO |
| `SRC-045` | `BR-016`, `BR-027`, `BQ-008` | CARRIED and BOUNDED QUESTION | Synthetic-only handling and no intentional persistence |
| `SRC-046` | `BR-015`, `BQ-008`, `BQ-009` | CARRIED and BOUNDED QUESTION | Public upload and secret controls |
| `SRC-047` | `BR-027`, `BR-030` | CARRIED | Truthful scope, privacy, and limitation disclosure |
| `SRC-048` | `BR-024` | CARRIED | Neutral unofficial branding |
| `SRC-049` | `BR-029` | CARRIED | Public-artifact data minimization |
| `SRC-050` | `BR-001`, `BR-023` | CARRIED | Repository delivery |
| `SRC-051` | `BR-023` | CARRIED | All source code |
| `SRC-052` | `BR-023` | CARRIED | README setup and run instructions |
| `SRC-053` | `BR-023`, `BR-030` | CARRIED | Approach, tools, assumptions, trade-offs, limitations |
| `SRC-054` | `BR-001`, `BR-023` | CARRIED | Deployed URL |
| `SRC-055` | `BR-020`, `BR-021` | CARRIED | Working core before optional ambition |
| `SRC-056` | `BR-021`, `BR-028` | CARRIED | Code organization and separable tests |
| `SRC-057` | `BR-023`, `BR-030` | CARRIED | Limitation consistency |
| `SRC-058` | `BR-031` | PROCESS AND DELIVERY | No prohibited Unicode dash characters |

## Requester decision disposition

| Decision | BAIRD mapping | Disposition |
|---|---|---|
| `DEC-001` | `BR-002`, `BR-004` | Selected-check distilled-spirits scope and 1 to 6 panels carried |
| `DEC-002` | `BR-020`, `BQ-013` | Batch remains conditional and post-core |
| `DEC-003` | `BR-005`, `BR-006`, `BR-010`, `BR-011`, `BR-014` through `BR-016`, `BR-021`, `BR-025`, `BR-026` | Success, safety, accessibility, privacy, and validation outcomes carried; exact engineering limits remain I2R A&E decisions |

## Completeness result

- Source requirements dispositioned: 58 of 58
- Requester decisions dispositioned: 3 of 3
- Unmapped active source requirements: 0
- Proposed batch requirements promoted without gate: 0
- Architecture selections made by this matrix: 0
