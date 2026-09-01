REWORK_REQUIRED

# BAIRD RT3 Intake Validation V2

## Snapshot verification

- Manifest: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V2.sha256`
- Observed manifest SHA-256: `480036814fe952f6111dc434311d4052c8cb318a0692eb07b62e2805165b90fa`
- Hashed entries: 29
- Missing entries: 0
- Hash mismatches: 0
- Files containing Unicode dash characters U+2010 through U+2015: 0

## Material findings

### RT3-BRD-V2-F001 - HIGH - BR-001 through BR-024 do not preserve source-to-requirement traceability or complete source disposition

`docs/PROCESS.md:26` requires the chain `source -> decision -> BAIRD requirement -> architecture decision -> feature requirement -> component -> test -> evidence`. The V2 BAIRD contains 24 unique `BR-NNN` rows, but it contains zero `SRC-NNN` locators. Each BR appears only in its definition row, and the rows provide only STATED, DECIDED, or DERIVED classification. They do not identify the source statements, requester decisions, regulatory records, or design dispositions that authorize each requirement.

This is not a formatting preference. The missing map hides material coverage gaps and authority ambiguity:

- `SRC-053` requires documentation of approach, tools, assumptions, trade-offs, and limitations. `BR-023` omits trade-offs and limitations from the requirement and does not test documentation completeness in its acceptance outcome.
- `SRC-056` requires clean code organization and separately testable extraction, normalization, rules, aggregation, and UI. No BR preserves this evaluator-facing engineering-quality outcome.
- `SRC-057` requires limitations to agree across README, UI, fixture report, and deployed behavior. No BR preserves that consistency outcome.
- `SRC-058` is the requester's project-wide prohibition on em dashes and Unicode dash characters. It has no BR or explicit process-only disposition.
- `SRC-049` requires excluding unnecessary personal anecdotes and identities from public artifacts. No BR or explicit process-only disposition preserves it.
- Conditional batch rows `SRC-041` through `SRC-044` have no explicit selected, deferred, conditional, or excluded mapping to `BR-020` and `BQ-013`.

Without a bidirectional map, I2R A&E and the FRD cannot prove that every selected source requirement is preserved and every omitted source row was intentionally dispositioned.

Required remediation:

1. Add durable source and decision locators to every `BR-NNN`, or add a bidirectional matrix mapping every `SRC-001` through `SRC-058` and `DEC-001` through `DEC-003` to one or more BRs, BQs, or an explicit excluded, deferred, conditional, or process-only disposition.
2. Add or amend BRs so trade-offs, limitations, engineering organization/test separation, limitation consistency, public-artifact data minimization, and the writing convention remain enforceable through later stages.
3. Give every derived BR a derivation rationale and upstream locator so later reviewers can distinguish required seamless-operation outcomes from design preference.

### RT3-BRD-V2-F002 - HIGH - The active process still assigns technical falsification to BAIRD

`docs/PROCESS.md:11` says Intake exits only when each load-bearing technical hypothesis has a named "BAIRD falsification method." This directly conflicts with:

- `docs/PROCESS.md:12`, which says BAIRD defines what must be true and does not select how to implement it;
- `docs/intake/clarification-log.md:20`, which assigns architecture, limits, hosting, and feasibility decisions to I2R A&E;
- `docs/intake/assumptions.md:13` and `docs/intake/assumptions.md:18`, which correctly leave both load-bearing technical hypotheses open for I2R A&E; and
- `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:11-15`, which routes bounded technical questions to I2R A&E.

The history notice correctly supersedes old review terminology, but it names `docs/PROCESS.md` as a current authority. The remaining active contradiction can therefore send feasibility proof back into BAIRD and recreate the stage contamination V2 is intended to remove.

Required remediation: change the Intake exit rule so BAIRD must identify and preserve the technical question and stop gate, while I2R A&E owns falsification and technical proof.

### RT3-BRD-V2-F003 - MEDIUM - The sealed baseline contains conflicting cold-start acceptance and omits it from the BR set

`docs/intake/INTAKE_DOCUMENT.md:132` requires cold-start submission p95 below 10 seconds. `docs/intake/success-definition.md:71` instead says I2R A&E selects the cold-start threshold and the FRD accepts it. `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:61-74` identifies cold start as undefined, but `BR-010` at line 90 covers only warmed result latency. The same Intake surfaces also retain a 3.0 second load-to-interactive target without a corresponding BR.

These are different acceptance baselines. I2R cannot tell whether 10 seconds and 3.0 seconds are requester-approved product requirements, BAIRD-derived outcomes, or superseded technical proposals.

Required remediation:

1. Reconcile the active Intake wording.
2. Give each retained initial-load and cold-start outcome a BR with source class, locator, and binary acceptance, or explicitly disposition it as an I2R A&E decision question.
3. Keep warmed valid-result success, cold behavior, initial load, and hard failure timeout separate.

### RT3-BRD-V2-F004 - MEDIUM - BR-012 overstates its source class and leaves blocked-egress success ambiguous

`BR-012` at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:92` is marked STATED and requires the product to remain usable in the restricted-network environment. Its acceptance says the core path must not fail solely because an "unapproved" external ML endpoint is blocked.

The discovery statement captured by `SRC-038` says stakeholder networks may block outbound ML endpoints and that this must be considered. `SRC-037` separately derives safe degradation when an external service exists. Discovery does not state that the prototype must produce a complete verification result with all inference egress blocked. The term "unapproved" is also undefined, so the acceptance could mean complete offline operation, approved-provider allowlisting, or merely bounded non-clean failure. Those outcomes impose materially different requirements on I2R A&E.

Required remediation: link BR-012 to `SRC-037` and `SRC-038`, classify the stated constraint separately from any derived continuity requirement, and define one testable blocked-egress outcome without selecting local, external, or hybrid architecture. If complete verification under zero inference egress is required, record it transparently as DERIVED or DECIDED rather than STATED.

## Gate decision

V2 removes the prior local-OCR, hosting, exact-resource-limit, and completed-benchmark contamination from the active requirements baseline. It does not yet establish a complete traceable BR baseline or a single unambiguous handoff contract for I2R A&E. The four material findings must be corrected and the package resealed before advancement.

REWORK_REQUIRED
