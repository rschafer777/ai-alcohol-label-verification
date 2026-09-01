# Ingest Summary

## Request record

| Field | Value |
|---|---|
| Requester | Project owner / job applicant |
| Received | 2026-08-31 through the current Codex conversation |
| Raw request | Build a full intake package for the supplied “Take-Home Project: AI-Powered Alcohol Label Verification App,” using the disciplined Argus Intake → analysis → I2R/FRD → Build Instructions process as the method, but keeping this project completely separate from Argus. Create a local project folder in Documents; do not create GitHub setup until the solution is agreed. |
| Source material | Full take-home assignment and stakeholder interview notes supplied in the initiating user message |
| Source location | `assignment-source-baseline.md`, a durable sanitized reconstruction of the initiating conversation |
| Source class | AUTHORITATIVE for the take-home deliverables, evaluator priorities, and stakeholder context |
| Trigger | Job-application homework assignment requiring a working prototype, source repository, documentation, and deployed URL |
| Authority | Requester owns scope approval for this local project; the evaluator ultimately judges the submitted deliverable |

## Plain-language thesis

Create a fast, obvious web tool that helps a compliance agent compare alcohol-label evidence with application/reference data. The tool should automate routine matching, explain discrepancies, and escalate ambiguity to the human instead of pretending that OCR or heuristics can make the final legal judgment.

## Why now

- The described team handles a high annual volume with limited staff.
- Much of the current review is repetitive field comparison.
- A prior scanning pilot was abandoned because 30 to 40 second processing was slower than manual review.
- The take-home is time-constrained and rewards a clean working core, good UX, error handling, and deliberate trade-offs.

## Cost of doing nothing for the stakeholder scenario

- agents continue spending substantial time on routine visual comparison;
- peak importer batches remain serialized and labor-intensive;
- experienced agents spend less time on nuanced compliance judgment;
- inconsistent manual attention may allow simple discrepancies to be missed;
- another slow or opaque prototype could reinforce resistance to modernization.

## Cost of building the wrong thing

- a false “pass” can mislead an agent about a legally important defect;
- broad but shallow rules can look complete while missing beverage-specific requirements;
- a cloud-only OCR path may fail on the stated network;
- a complex interface may be abandoned by the intended users;
- batch scope can consume the schedule before the single-label path is trustworthy;
- a prototype framed as an approval engine can create legal and ethical overclaiming.

## Intake recommendation

Proceed to BAIRD only after all three independent Intake re-reviews return CLEAR on the same remediated revision. BAIRD validates that the Intake faithfully, completely, and testably represents discovery. After BAIRD clears, I2R A&E must test latency, extraction, deployment, egress, licensing, regulatory capability, data flow, security, and batch feasibility before selecting stack, OCR/vision engine, rule architecture, or hosting platform.
