# Project Delivery Process

## Purpose

This project adapts the proven Argus delivery sequence to a standalone job-application take-home. It preserves the useful controls: clear human intent, research before design, requirement traceability, executable build planning, and evidence-based validation. It does not import Argus-specific product architecture or governance.

## Stage map

| Stage | Question answered | Primary output | Entry/exit rule |
|---|---|---|---|
| 1. Intake | What outcome is wanted, for whom, and where does the ask stop? | Nine-artifact intake package | Exit only after success and scope are confirmed, no human-owned load-bearing assumption remains, and every load-bearing technical hypothesis is named for BAIRD requirements treatment with an I2R A&E falsification method and downstream stop gate. |
| 2. BAIRD requirements baseline | What did discovery define, what did it leave undefined, and which additional requirements and decision questions must be established before architecture begins? | Beginning Assessment Intake Requirements Document | Validate Intake fidelity, close requirements-level gaps needed for a seamless outcome, classify knowns and unknowns, and define the acceptance outcomes and technical questions I2R A&E must resolve. BAIRD defines what must be true. It does not select how to implement it. Three independent CLEAR reviews are required. |
| 3. I2R A&E | What architecture and engineering take the validated requirements from ideation to realization? | Architecture and engineering specification | Define UX, workflow, ingress, egress, data movement, storage, interfaces, frontend, middleware, backend, APIs, languages, runtime, security, operations, and expected results. |
| 4. FRD | Which exact features must the designed solution provide? | Feature Requirements Document | Every feature has binary acceptance, source traceability, component, interface, state behavior, failure behavior, and test. I2R A&E plus FRD require three independent CLEAR reviews. |
| 5. BI build instructions | Who builds each part, in what order, under which coding, documentation, review, QA/QC, UAT, DoD, and delivery standards? | Build instructions and work-package ledger | No coding from a loose summary. Every work package maps to requirements, assigned agent roles, tests, evidence, and integration gates and passes three independent readiness reviews. |
| 6. Development | Build and wire the approved scope. | Working implementation and engineering evidence | Implemented is not done until wired, tested, documented, and runnable. |
| 7. Validation Protocol | Does the deliverable match Intake, BAIRD, I2R A&E, FRD, and BI end to end? | Requirements traceability matrix and validation report | Test every acceptance criterion, failure path, UX behavior, and delivery obligation. Any gap loops back to development. |
| 8. QA/QC and UAT | Is the solution reliable, clear, maintainable, reviewable, and acceptable to the requester? | Regression results, QA/QC report, UAT plan and sign-off package | Repeat correction and regression until DoD passes. Requester review follows internal clearance. |
| 9. Release | Is the organized repository and deployed demo ready for the evaluator? | GitHub repository, README, deployed URL, release notes | Clean setup path, reproducible tests, known limitations, working public demo, and complete numbered documentation package. |

## Traceability convention

The intake uses `SRC-NNN` for source statements and `DEC-NNN` for human decisions. BAIRD uses `BR-NNN` for its validated and derived requirements and `BQ-NNN` for architecture questions. The FRD assigns feature requirement IDs (`FR-NNN`), test IDs (`T-NNN`), component IDs (`C-NNN`), and integration IDs (`IP-NNN`). Later stages must preserve the chain:

`source -> decision -> BAIRD requirement -> architecture decision -> feature requirement -> component -> test -> evidence`

## Two checkpoints

Checkpoint A occurs after Intake. It asks whether the project outcome, scope, and success definition are understood correctly. For this project, the requester delegated bounded decisions through `USR-008`, and all three independent Intake reviewers must return CLEAR before exit.

Checkpoint B occurs only after I2R A&E finds a consequential fork that research cannot settle. It must not be used for implementation details that the engineering process can decide.

## Project-specific interpretation

- The take-home assignment is authoritative for deliverables and stakeholder needs.
- Official TTB guidance is authoritative for regulatory facts used by the prototype.
- Stakeholder anecdotes are evidence of workflow needs, not automatically binding feature requirements.
- The prototype is a verification assistant. It does not issue legal approval, replace a compliance agent, or claim production authorization.
- A smaller complete product is preferred over a larger partially working one, consistent with the assignment's stated evaluation guidance.

## Stop conditions

Do not start implementation when any of these is true:

- supported beverage scope is unresolved;
- the comparison input workflow is unresolved;
- success can only be described with adjectives rather than observable evidence;
- a safety-critical result can silently pass when evidence is missing or low-confidence;
- an external service is assumed available despite the stated network constraint;
- the FRD cannot map every in-scope behavior to a test.

## Independent review rule

At each documented completion point for Intake, BAIRD, I2R/FRD, and BI:

1. three independent reviewers inspect the same complete revision;
2. each returns only CLEAR or REWORK_REQUIRED with evidence;
3. any material finding keeps the stage open;
4. remediation is recorded by finding ID;
5. all three reviewers re-review the corrected revision;
6. advancement requires three CLEAR verdicts on that same revision.
