# Source Requirements Register

These are Intake-level source statements. They are not the implementation FRD. Each row has a durable source locator in `assignment-source-baseline.md` or `regulatory-source-register.md`. The FRD must translate the accepted rows into sequential requirements with binary acceptance, components, tests, and evidence.

## Product and workflow

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-001` | STATED | `ASG-001` | Build an AI-powered alcohol label verification prototype. | Must | A working end-to-end deployed application exists. |
| `SRC-002` | STATED | `ASG-003` | Compare label artwork with application/reference data. | Must | Each selected check displays expected and extracted evidence with a result. |
| `SRC-003` | STATED | `ASG-003`, `ASG-019` | Check brand name. | Must | Brand fixtures produce expected states. |
| `SRC-004` | STATED | `ASG-003`, `ASG-019` | Check alcohol content. | Must | ABV/proof fixtures compare under documented normalization. |
| `SRC-005` | STATED | `ASG-003`, `ASG-020`, `ASG-021` | Check government warning text and supported presentation properties. | Must | Text and presentation checks remain separate and evidence-backed. |
| `SRC-006` | STATED | `ASG-025`, `ASG-026`, `DEC-001` | In the selected spirits profile, check class/type, net contents, name/address, and import origin when applicable. | Must for selected profile | Each enumerated check has schema, rule, fixture, and capability state. |
| `SRC-007` | STATED | `ASG-011`, `ASG-012` | Operate as a standalone proof of concept without COLA integration. | Must | No COLA credential, endpoint, or parser is required. |
| `SRC-008` | RECONSTRUCTED | `ASG-003`, `ASG-011`, `DEC-001` | Receive one structured reference record through a documented prototype contract. | Must | Schema, validation, optionality, and examples are documented and tested. |
| `SRC-009` | RECONSTRUCTED | `ASG-016`, `ASG-018` | Keep final judgment with the human agent. | Must | No automatic legal approval or rejection; ambiguity routes to Review. |
| `SRC-010` | RECONSTRUCTED | `ASG-022`, `ASG-023`, `DEC-001` | Accept 1 to 6 panel images, preserve originals, and expose missing panel coverage. | Must | Absent evidence cannot yield a clean summary; evidence links to region/crop or unavailable state. |

## Speed, usability, and accessibility

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-011` | STATED | `ASG-006`, `ASG-007`, `DEC-003` | Valid supported submissions return complete useful results in about five seconds. | Must | User Verify activation through complete rendered result has deployed warmed p95 at or below 5.0 seconds; fast failures and server-only timing do not count. |
| `SRC-012` | STATED | `ASG-008`, `ASG-018` | Keep the interface clean, obvious, and usable by people with varied technical comfort. | Must | Try sample and manual core journeys pass E2E and usability review without external instructions. |
| `SRC-013` | RECONSTRUCTED | `ASG-008`, `ASG-041` | Avoid hidden primary actions and give evaluators a self-starting sample path. | Must | One clear path and Try sample are present; no required nested navigation. |
| `SRC-014` | RECONSTRUCTED | `ASG-008`, `ASG-018` | Use plain-language states, reasons, and next actions. | Must | Every non-match state explains the issue and recovery. |
| `SRC-015` | RECONSTRUCTED | `ASG-008`, `DEC-003` | Do not rely on color and meet the defined core accessibility envelope. | Must | Text/icon status, WCAG 2.2 AA contrast, axe, keyboard, NVDA, and zoom checks pass. |
| `SRC-016` | RECONSTRUCTED | `ASG-008`, `DEC-003` | Support complete keyboard use with visible focus and programmatic error association. | Must | Core path passes keyboard-only acceptance. |
| `SRC-017` | RECONSTRUCTED | `ASG-006`, `ASG-007` | Expose processing status and elapsed time honestly. | Should | No indefinite spinner; current step, elapsed time, timeout, and recovery are available. |
| `SRC-018` | RECONSTRUCTED | `ASG-022`, `ASG-023` | Keep original evidence accessible when preprocessing or enhancement is shown. | Should | Original and derived views are distinguishable and comparable. |

## Matching and decision integrity

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-019` | STATED | `ASG-016`, `ASG-017` | Capitalization differences may require judgment rather than rejection. | Must | The supplied brand example routes to Review with a reason. |
| `SRC-020` | RECONSTRUCTED | `ASG-016`, `ASG-017` | Distinguish exact from field-specific normalized equivalence, including any proposed punctuation handling. | Must | The comparison policy exposes every transformation; unproven punctuation variation routes to Review rather than automatic Match. |
| `SRC-021` | RECONSTRUCTED | `ASG-023`, `DEC-003` | Missing, absent-panel, or low-confidence evidence must not become a clean result. | Must | The negative fixture invariant passes. |
| `SRC-022` | RECONSTRUCTED | `ASG-016`, `ASG-023`, `DEC-003` | Use Match, Review, Mismatch, and Not verified at field level with deterministic aggregation. | Must | Every field and submission resolves under the documented state machine. |
| `SRC-023` | RECONSTRUCTED | `ASG-022`, `ASG-023` | Separate image-quality failure from a detected label difference. | Must | Poor-image cases request better evidence and never invent a value. |
| `SRC-024` | RECONSTRUCTED | `ASG-016` | Confidence cannot be the legal decision or an unexplained truth score. | Must | Confidence provenance routes uncertainty; no threshold produces approval/rejection. |

## Regulatory grounding

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-025` | VERIFIED | `REG-003`, `REG-010` | Apply the health-warning rule to covered beverages at or above 0.5 percent ABV. | Scope dependent | Rule source/version is fixture-tested. |
| `SRC-026` | VERIFIED | `REG-003`, `REG-010` | Compare warning wording against the prescribed authority. | Must for selected profile | Mutations yield Mismatch or Review when unreadable. |
| `SRC-027` | VERIFIED | `ASG-020`, `ASG-021`, `REG-003`, `REG-010` | Check warning-heading uppercase presentation. | Must for selected profile | Title-case heading is not a Match. |
| `SRC-028` | VERIFIED | `ASG-020`, `REG-003`, `REG-010` | Check heading emphasis and remaining-text emphasis only where evidence permits. | Must with capability limit | State is Match, Review, Mismatch, or Not verified based on evidence. |
| `SRC-029` | VERIFIED | `REG-003`, `REG-010` | Evaluate continuity, separation, contrast, and legibility as independent checks where supported. | Should | Each check has its own evidence and state. |
| `SRC-030` | VERIFIED | `REG-003`, `REG-010` | Physical warning type size depends on container volume and reliable scale. | Must disclose limit | Unscaled photos cannot receive a definitive size Match. |
| `SRC-031` | VERIFIED | `REG-002`, `REG-009` | Relevant spirits fields may have field-of-vision requirements. | Should for profile | Panel coverage reports whether supplied evidence supports the check. |
| `SRC-032` | VERIFIED | `ASG-026`, `REG-004`, `REG-005`, `DEC-001` | Wine and malt requirements differ and are outside the selected profile. | Boundary | No cross-category completeness claim or mixed-category fixture result. |
| `SRC-033` | RECONSTRUCTED | `ASG-027`, `REG-001` through `REG-010` | Version every implemented rule by authority and verification date. | Must | Central registry identifies guidance, eCFR authority, retrieval date, and rule version. |

## Image handling and resilience

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-034` | STATED | `ASG-022`, `ASG-023` | Handle bounded angle, lighting, glare, blur, and perspective variation. | Should | Controlled degradation fixtures exercise each supported case. |
| `SRC-035` | RECONSTRUCTED | `ASG-022`, `DEC-003` | Validate type, bytes, decoded pixels, panel count, decode time, and usable content. | Must | Invalid, spoofed, corrupt, oversize, and resource-boundary tests are actionable and bounded. |
| `SRC-036` | RECONSTRUCTED | `ASG-023` | Never hallucinate unreadable text. | Must | Unreadable evidence yields Review or Not verified. |
| `SRC-037` | RECONSTRUCTED | `ASG-014`, `DEC-003` | External inference failure must degrade safely when such a service exists. | Conditional Must | Timeout/block test returns a bounded non-clean state without crash. |
| `SRC-038` | STATED | `ASG-014` | Stakeholder networks may block outbound ML endpoints. | Must consider | I2R A&E documents egress, fallback, and blocked-egress release behavior. |
| `SRC-039` | RECONSTRUCTED | `ASG-006`, `ASG-007`, `DEC-003` | Processing must have bounded timeout and recovery. | Must | No indefinite wait; valid success and failure timing are measured separately. |

## Batch

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-040` | STATED | `ASG-009`, `DEC-002` | Peak batches contain 200 to 300 applications and batch support is valuable. | Should, gated | Batch work starts only after the core gate. |
| `SRC-041` | PROPOSED | `ASG-009`, `DEC-002` | Pair rows and images through a documented manifest and safe filename rule. | Conditional | Schema and mapping tests exist if batch ships. |
| `SRC-042` | PROPOSED | `ASG-009`, `DEC-002` | Isolate failures by row and expose accurate progress, cancellation, and retry. | Conditional | One bad row cannot fail the batch. |
| `SRC-043` | PROPOSED | `ASG-005`, `ASG-009`, `DEC-002` | Default completed batch review to exceptions. | Conditional | Needs-review filter and next-review action work. |
| `SRC-044` | PROPOSED | `ASG-009`, `DEC-002` | Export batch results in a documented machine-readable format. | Conditional | Export schema and 250-row claim are tested if shipped. |

## Security, privacy, and honesty

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-045` | STATED | `ASG-013`, `DEC-003` | Do not store sensitive information for the exercise. | Must | Synthetic-only notice, no intentional persistence, cleanup, and no raw-content logs are proven. |
| `SRC-046` | RECONSTRUCTED | `ASG-013`, `DEC-003` | Bound public upload abuse and keep secrets/private sources out of the repository. | Must | Threat model, content sniffing, resource/rate limits, secret scan, and log review pass. |
| `SRC-047` | RECONSTRUCTED | `ASG-012`, `ASG-041`, `ASG-042` | State prototype scope, privacy, and limitations visibly and truthfully. | Must | UI and README agree with implemented data flow and validation evidence. |
| `SRC-048` | RECONSTRUCTED | `ASG-012`, `USR-003` | Do not imply official TTB affiliation through seals, branding, identities, or legal-action wording. | Must | Public UI uses original neutral branding and non-authoritative terms. |
| `SRC-049` | RECONSTRUCTED | `assignment-source-baseline.md`, Explicit omissions | Exclude unnecessary personal anecdotes and identities from public artifacts. | Must | Data-minimization review passes. |

## Submission and engineering quality

| Source ID | Provenance | Durable locator | Requirement or constraint | Priority | Acceptance direction |
|---|---|---|---|---|---|
| `SRC-050` | STATED | `ASG-030`, `USR-001` | Submit a source repository such as GitHub. | Must | Evaluator-accessible repository URL is delivered. |
| `SRC-051` | STATED | `ASG-031`, `USR-001` | Include all source code. | Must | Submitted revision contains the complete runnable implementation. |
| `SRC-052` | STATED | `ASG-032`, `USR-001` | Include README setup and run instructions. | Must | Clean-checkout rehearsal succeeds using only README. |
| `SRC-053` | STATED | `ASG-033`, `ASG-042`, `USR-001` | Briefly document approach, tools, assumptions, trade-offs, and limitations. | Must | Concise accurate documentation is linked from README. |
| `SRC-054` | STATED | `ASG-034` | Provide a deployed application URL. | Must | Clean-browser production smoke test passes on the submitted revision. |
| `SRC-055` | STATED | `ASG-041` | Favor a working core over ambitious incomplete features. | Must | No committed core behavior is a placeholder; batch cannot weaken the gate. |
| `SRC-056` | RECONSTRUCTED | `ASG-035`, `ASG-036`, `ASG-037` | Organize code cleanly and test extraction, normalization, rules, aggregation, and UI separately. | Must | Architecture and tests show separable contracts and anti-hard-coding controls. |
| `SRC-057` | RECONSTRUCTED | `ASG-042` | Document limitations without hiding them. | Must | README, UI, fixture report, and deployed behavior agree. |
| `SRC-058` | STATED | `USR-002` | Do not use em dashes or Unicode dash characters. | Must | Automated scan finds no Unicode dash characters in project files. |

## Counts and next transformation

- Total source statements: 58
- Stated: 21
- Verified regulatory: 8
- Reconstructed: 25
- Proposed design candidates: 4
- Open human decisions: 0

The FRD must preserve every source locator, explicitly exclude non-selected rows, and never promote a proposed row without its decision and evidence gate.
