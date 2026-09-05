# Delivery Process Conformance

Document ID: LV-GOV-002  
Status: Active release control

This project applies PROC-009, PROC-010, PROC-011, and PROC-013 as delivery controls. It uses their verification substance without claiming authority over an external production environment or replacing the repository's LabelVerify-specific lifecycle documents.

## Gated state mapping

| Process state | LabelVerify evidence |
| --- | --- |
| INGESTED | `docs/01-discovery/`, Intake source inventory, known facts, assumptions, open questions, and risk notes |
| BAIRD_COMPLETE | `docs/03-baird/BAIRD.md`, codebase and integration fit, gaps, risks, and recommended scope |
| I2R_COMPLETE | `docs/04-i2r-ae/ARCHITECTURE_ENGINEERING.md`, FRD, traceability, API, database, security, runtime, test, and acceptance design |
| BUILD_INSTRUCTIONS_READY | `docs/06-build-instructions/BUILD_INSTRUCTIONS.md`, work packages, ownership, gates, regression plan, and rollback considerations |
| DEV_IN_PROGRESS / DEV_COMPLETE | Governed source changes plus `docs/07-development/IMPLEMENTATION_RECORD.md` and local test evidence |
| QA_QC_RUNNING / QA_QC_PASSED | Validation evidence, defect history, QA/QC report, regression results, and UAT script |
| VP_VERIFIED | One frozen candidate, release manifest, validation protocol closure, risk and exception review, and three unanimous independent RT decisions |
| MERGED_TO_MAIN | Clean staged review, commit record, local CI summary, and verified `main` SHA |
| RELEASE_ARTIFACT_CREATED | Immutable container digest, deployment record, production-state readback, and smoke evidence |
| DEPLOYED_TO_PRODUCTION / LIVE_CERTIFIED | Exact build identity at the public URL, health, metadata, UI, core-flow, and post-deploy smoke verification |
| DD_CERTIFIED | Release readiness, rollback, notes, artifact manifest, deployment plan, and independent delivery signoff |
| HYPERCARE_COMPLETE | Requester UAT outcome and any resulting corrective loop closed or explicitly accepted |

No later state is asserted merely because tests are green. The artifacts and evidence for the preceding state must agree first. Deployment and live certification remain separate from local QA/QC and VP.

## Decision controls

- Verify before acting: inspect source, contracts, evidence, Git status, and exact targets before mutation.
- Validate after acting: rerun focused regressions, the complete source gate, governed corpora, accuracy scores, manifest validation, and live checks appropriate to the change.
- Challenge before accepting: three independent RTs attempt to falsify requirements, architecture, and delivery claims against the same frozen candidate.
- Reconcile before proceeding: a Not Clear decision reopens the responsible lifecycle stage; expected outcomes are not changed to make implementation pass.
- Decide from engineering evidence: ordinary implementation choices use documented best practice; operator input is reserved for authority, intent, credentials, licensing, or risk acceptance only the operator can provide.
- Preserve foreign work: the pre-change worktree is captured, unrelated edits are retained, destructive reset, clean, stash, and overwrite operations are prohibited, and exact paths are used for release actions.

## Evidence language

Release decisions distinguish:

- Observed: directly returned by a command, runtime, image, or service.
- Verified: observed evidence checked against a declared requirement or independent source.
- Inferred: a reasoned conclusion supported by stated evidence.
- Assumed: an unverified premise carried visibly as a risk or prerequisite.
- Unknown: information not available and not safe to infer.

Confidence alone is never a release gate. Material changes require evidence and adversarial review.

## Completion questions

Before a release advances, the owner records whether the exact candidate is identified; requirements and exceptions are reconciled; source and generated contracts agree; tests and governed evidence pass; security and privacy boundaries hold; performance is measured without cache or oracle gaming; documentation matches the implementation; the staged manifest validates; three independent RTs are Clear; GitHub contains the exact commit; Azure serves that build and digest; rollback is available; and requester UAT can begin. Any unanswered item keeps the corresponding state open.
