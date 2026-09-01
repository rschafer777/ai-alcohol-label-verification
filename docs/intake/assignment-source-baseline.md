# Sanitized Assignment Source Baseline

## Purpose and authority

This file is the durable, sanitized source record for the take-home assignment and the requester's delivery instructions. It preserves every product statement, stakeholder constraint, deliverable, and evaluation criterion needed to reconstruct requirements. Personal anecdotes, family details, and unnecessary names were deliberately omitted because they do not affect the product contract.

This record is authoritative for assignment intent. It does not replace official regulatory sources. Regulatory statements must also cite the TTB or eCFR source recorded in `regulatory-source-register.md`.

## Assignment statements

### Background and operating context

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `ASG-001` | Project Background, opening | Build a take-home prototype for AI-powered alcohol label verification. |
| `ASG-002` | Compliance interview, workload paragraph | TTB reportedly reviews about 150,000 label applications annually with 47 agents. |
| `ASG-003` | Compliance interview, workflow paragraph | Agents compare label artwork with application data, including brand name, alcohol content, and the government warning. |
| `ASG-004` | Compliance interview, workflow paragraph | A simple manual review reportedly takes about 5 to 10 minutes and longer when issues exist. |
| `ASG-005` | Compliance interview, routine-work paragraph | Much of the workload is routine matching, which limits time for complex analysis. |
| `ASG-006` | Compliance interview, prior-pilot paragraph | A prior scanning pilot reportedly took 30 to 40 seconds per label and was abandoned. |
| `ASG-007` | Compliance interview, prior-pilot paragraph | Results need to return in about five seconds for user adoption. |
| `ASG-008` | Compliance interview, usability paragraph | Users have widely varying technical comfort, so the interface must be clean, obvious, and require no hunting for controls. |
| `ASG-009` | Compliance interview, peak-season paragraph | Peak importer submissions can contain 200 to 300 label applications, and batch handling would have high operational value. |

### Technology, integration, and security context

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `ASG-010` | IT interview, infrastructure paragraph | The current organization uses Azure and operates in a federal compliance context. |
| `ASG-011` | IT interview, COLA paragraph | The existing COLA system uses .NET, but direct COLA integration is not part of this prototype. |
| `ASG-012` | IT interview, prototype paragraph | Treat the solution as a standalone proof of concept that may inform future procurement. |
| `ASG-013` | IT interview, security paragraph | A production solution would require PII, retention, and federal controls, but this exercise should not store sensitive information. |
| `ASG-014` | IT interview, network paragraph | Stakeholder networks may block outbound traffic and cloud ML endpoints. |

### Human judgment and matching nuance

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `ASG-015` | Senior-agent interview, skepticism paragraph | Modernization must make the review faster without increasing user burden. |
| `ASG-016` | Senior-agent interview, nuance paragraph | Matching requires judgment and cannot be reduced to naive pattern matching. |
| `ASG-017` | Senior-agent interview, example | `STONE'S THROW` on a label and `Stone's Throw` in an application are obviously related even though capitalization differs. |
| `ASG-018` | Senior-agent interview, closing | The tool should help agents move through the queue faster without making the existing workflow harder. |

### Warning and image-quality details

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `ASG-019` | Junior-agent interview, checklist paragraph | Agents manually compare brand name, alcohol content, and the warning statement for each label. |
| `ASG-020` | Junior-agent interview, warning paragraph | The warning statement requires exact wording and the heading requires specific uppercase and emphasis presentation. |
| `ASG-021` | Junior-agent interview, warning example | A title-case `Government Warning` heading should be identified as a problem rather than treated as an exact presentation match. |
| `ASG-022` | Junior-agent interview, image paragraph | Real label images may be angled, poorly lit, glared, or otherwise difficult to read. |
| `ASG-023` | Junior-agent interview, image paragraph | If the evidence is unreadable, an agent currently requests a better image; improved handling would be valuable but was described as possibly outside prototype scope. |

### Technical freedom and label context

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `ASG-024` | Technical Requirements | The implementer may choose any programming languages, frameworks, or libraries. |
| `ASG-025` | Additional Context, common elements | Common label elements include brand name, class/type, alcohol content with exceptions, net contents, producer/bottler name and address, country of origin for imports, and the government health warning. |
| `ASG-026` | Additional Context, category caveat | Exact label requirements differ for beer, wine, and distilled spirits. |
| `ASG-027` | Additional Context, research invitation | Review TTB guidance for additional regulatory context. |
| `ASG-028` | Sample Label | The sample distilled-spirits record uses brand `OLD TOM DISTILLERY`, class/type `Kentucky Straight Bourbon Whiskey`, alcohol content `45% Alc./Vol. (90 Proof)`, net contents `750 mL`, and the standard government warning. |
| `ASG-029` | Sample Label, testing invitation | Additional test labels may be sourced or created, including with AI image-generation tools. |

### Required deliverables

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `ASG-030` | Deliverables, repository | Submit a source code repository such as GitHub. |
| `ASG-031` | Deliverables, repository contents | Include all source code. |
| `ASG-032` | Deliverables, README | Include README setup and run instructions. |
| `ASG-033` | Deliverables, documentation | Briefly document the approach, tools used, and assumptions made. |
| `ASG-034` | Deliverables, deployment | Provide a deployed application URL that evaluators can access and test. |

### Evaluation criteria and delivery preference

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `ASG-035` | Evaluation Criteria, item 1 | Evaluation includes correctness and completeness of core requirements. |
| `ASG-036` | Evaluation Criteria, item 2 | Evaluation includes code quality and organization. |
| `ASG-037` | Evaluation Criteria, item 3 | Evaluation includes appropriate technical choices for the scope. |
| `ASG-038` | Evaluation Criteria, item 4 | Evaluation includes user experience and error handling. |
| `ASG-039` | Evaluation Criteria, item 5 | Evaluation includes attention to requirements. |
| `ASG-040` | Evaluation Criteria, item 6 | Evaluation includes creative problem-solving. |
| `ASG-041` | Closing guidance | A working core application with clean code is preferred over ambitious but incomplete features. |
| `ASG-042` | Closing guidance | Document trade-offs and limitations. |
| `ASG-043` | Closing guidance | The evaluator values reasonable independent gap-filling when clarification is unavailable. |

## Requester delivery instructions

| Statement ID | Source locator | Sanitized source statement |
|---|---|---|
| `USR-001` | Requester follow-up, submission list | The final submission must include the source repository, all source code, README setup/run instructions, and brief approach/tools/assumptions documentation. |
| `USR-002` | Requester writing rule | Do not use em dashes. |
| `USR-003` | Requester design-reference instruction | Consider the supplied Grok and Gemini documents and images as design inputs, while distinguishing their content from requester instructions. |
| `USR-004` | Requester process instruction | Run three independent red-team reviews across Intake decisions and design comparisons before moving to BAIRD. |
| `USR-005` | Requester process instruction | Advance only after all three reviewers agree that the current stage is clear. |
| `USR-006` | Requester process instruction | Apply the same red-team discipline to BAIRD, I2R, BI, and the FRD/build instructions. |
| `USR-007` | Requester objective | Produce a deployable, accurate, direct, user-friendly solution with documented requirements, decisions, verification, validation, and build instructions. |
| `USR-008` | Requester authorization | The requester authorized the project to proceed through the documented pre-development stages and delegated bounded solution decisions that preserve assignment intent. |
| `USR-009` | Earlier requester GitHub instruction | Keep the project local until the requester agrees the solution is ready to push and creates the GitHub setup. |

## Explicit omissions

The source interviews include personal schedules, family anecdotes, employee names, and historical color that do not change the product contract. Those details are intentionally not reproduced here. Role-based context and every requirement-bearing statement are preserved.

## Reconstruction rule

Every STATED row in `source-requirements.md` must identify one or more `ASG-NNN` or `USR-NNN` locators. Every VERIFIED regulatory row must identify one or more `REG-NNN` sources. Reconstructed or proposed rows must identify the source statements from which they were derived.
