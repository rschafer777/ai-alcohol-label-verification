# Change Control Register

Document ID: LV-CM-001  
Status: Active

## Purpose

This register preserves the evidence-based progression from initial requirements through corrective release. Canonical lifecycle documents describe the current approved baseline. This register explains material changes without rewriting earlier decisions to appear prescient.

## Change policy

Every material change must identify:

- the observed condition and objective evidence;
- the earlier assumption or decision affected;
- the approved requirement change;
- architecture, contract, code, test, and documentation impact;
- safety and regression risks;
- entry and exit gates;
- implementation and verification status.

Expected results are not changed merely to match current software. A source requirement or independent oracle may be corrected only when evidence demonstrates that it was wrong, and the correction must remain visible here.

## Change records

### CR-001: Initial integrated prototype

| Field | Record |
| --- | --- |
| Trigger | Assignment discovery and stakeholder interview notes |
| Decision | Build a local OCR-assisted evidence tool for malt beverage, wine, and distilled-spirit labels, with deterministic checks and human disposition |
| Scope | Single product, batch, evidence, warning detail, history, export, security boundary, documentation, and Azure demonstration |
| Verification | Automated source gates, governed fixtures, private-image technical processing, deployment smoke, and requester UAT instructions |
| Status | Superseded as the current release target by CR-002; retained as historical evidence |

### CR-002: UAT-driven corrective release

| Field | Record |
| --- | --- |
| Trigger | Representative-image testing and direct reviewer feedback |
| Observed condition | 214 of 221 analyses routed to Review; 27 of 30 oracle expected-Pass cases routed to Review; numeric brands were rejected by admission rules; image roles were inferred from position; observation correction reran OCR and used application-reference provenance; producer extraction was the weakest common field; representative Azure corpus timing was absent |
| Earlier assumptions revised | Conservative review routing alone was assumed to provide sufficient triage value; positional panel names were treated as harmless presentation; a manual reference rerun was treated as an adequate correction mechanism; broad language phrases were considered before the producer failure causes were classified |
| Approved direction | Attribute blocking causes, preserve exact compliance behavior, implement field-level provenance and atomically serialized observation corrections that retain verbatim printed form and derive normalized values server-side without OCR, use neutral image names, support numeric brands generically, improve measured recoverable producer and warning-wording fields, run cause-routed OCR evaluation before parser changes when recognition is responsible, then add only justified language support |
| Safety boundary | No uncertain evidence becomes Match merely to reduce Review volume; no machine result creates legal approval; no filename or expected value steers extraction; original OCR and evidence remain immutable; 500 product lineages and 10 revisions per lineage bound retained storage; protected fields retain exact value, check-state, and evidence integrity |
| Model boundary | No general-purpose language model, vision-language model, external inference, broad translation service, model ensemble, or fine-tuning enters the corrective release without a later governed change record |
| Entry gate | Updated Intake, BAIRD, I2R, FRD, Build Instructions, Validation Protocol, QA/QC plan, and traceability reviewed as one frozen snapshot by three independent reviewers |
| Exit gate | Corrective requirements, implementation, automated gates, an evidence-reviewed sealed-holdout utility result, zero new false clean, representative distinct-hash local and Azure tests, documentation, release manifest, and three final independent reviews pass |
| Status | Implementation, local source gates, and corrected-candidate corpus evidence complete; final frozen-candidate reviews, deployment, and requester UAT remain |

#### CR-002 final-review integrity closure

The first frozen corrective candidate did not pass all three final reviews. Requirements traceability was Clear, while architecture and delivery review identified concrete integrity gaps: invalid history identifiers did not traverse every mutation boundary; unresolved beverage type could be coerced during a revision; result copy used record-level rather than field-level reference provenance; correction replay depended on order-derived evidence IDs and did not persist every raw and derived form; add-panel telemetry could describe the prior run; file deletion preceded metadata commit; documented error names diverged from the registry; and validation source hashes described working-tree line endings rather than Git's canonical staged bytes.

The candidate was not published. The implementation now applies the same mutation controls before history-ID validation, preserves unresolved type until supported evidence resolves it, renders per-field provenance, binds correction replay to source image hash plus panel and polygon, stores verbatim and derived correction forms, carries fresh add-panel telemetry and limitations, commits metadata deletion before blob unlink with startup reconciliation, uses registry error names, and canonicalizes governed source hashes to LF. Dedicated regression tests and regenerated corpus evidence are required before the candidate can be frozen again. This is corrective closure within CR-002, not a change to the assignment scope or acceptance standard.

A second final architecture review then identified six narrower defects in the correction workflow: add-panel comparison could retain a stale label-derived baseline; repeated correction replay could pair the newest value with an older locator; class correction did not rerun family inference; typed sulfite absence could overstate chemistry; numeric audit omitted printed form details; and the browser lacked a closed type selector and a correction-region tool when OCR had no box. Publication remained held. The corrective implementation now refreshes label-derived fields from the fresh complete read while preserving independent and corrected fields, replays each field's latest event as a unit, reruns or safely stops class-driven type inference, accepts only a visible Contains Sulfites transcription, persists printed numeric structure, and requires a controlled type or bounded original-pixel region in the browser. Targeted regressions and full corrected-candidate corpus regeneration pass; the complete release gate and three identical-snapshot reviews remain required before publication.

A third architecture challenge found four cross-revision integrity defects: fresh OCR fields did not all receive explicit provenance, the conditional malt alcohol-source field was omitted from merge coverage, a later class correction could replace an explicitly reviewer-corrected beverage family, newly conflicting add-panel evidence could leave a stale label-derived family resolved, and browser-drawn evidence could place a vertex exactly on the excluded right or bottom image boundary. Publication remained held. The merge now enumerates every reference field, label-derived family resolution follows the fresh complete read in both directions, reviewer-corrected family authority survives later class edits, and OCR and reviewer evidence use one positive-area half-open coordinate validator. Dedicated regressions pass, the 409-test source gate is clean, and governed/private/accuracy evidence was regenerated from the corrected source before refreeze.

A later requirements-traceability review rejected a frozen candidate because six distinct BAIRD derived requirements reused identifiers 37 through 39, making a downstream `BAIRD-38` citation ambiguous. Publication remained held. The requirements are now uniquely numbered 1 through 42, each affected feature cites its exact BAIRD source, and a release regression fails if that sequence is duplicated or broken.

## Decision chronology

| Date | Decision | Basis | Result |
| --- | --- | --- | --- |
| 2026-09-01 | Use local ONNX OCR and deterministic rules | Outbound network restrictions, latency target, and explainability | Retained |
| 2026-09-02 | Support single and batch workflows with retained evidence | Discovery requirement and peak-season volume | Retained |
| 2026-09-03 | Route uncertain warning and presentation evidence to Review | Avoid false deterministic differences or false clearance | Retained, with recovery and reason attribution to be improved |
| 2026-09-04 | Begin CR-002 corrective release | Representative-image evidence and reviewer UAT | Active |
| 2026-09-04 | Retain PP-OCRv4 English | PP-OCRv5 English and Latin were faster and improved some producer reads, but each regressed protected ABV or warning evidence on the sealed holdout | Candidate model not promoted; hashes and negative decision retained |
| 2026-09-04 | Accept measured producer utility below the provisional four-exact holdout target | The general parser raised full-corpus producer exact reads from 31 to 35 and sealed-holdout exact reads from 7 to 8 while reducing a miss or wrong result, but the remaining holdout errors were OCR transcription damage or disputed ground truth. A dual-recognizer runtime would add operational complexity and had protected-field regressions as a full replacement | Provisional target recorded as an accepted variance; no expected value, product name, or filename was added to runtime logic |
| 2026-09-04 | Reject the first CR-002 final candidate and harden release integrity | Final architecture and delivery review found mutation-boundary, unresolved-type, provenance, replay-locator, telemetry, deletion-order, error-contract, and source-hash gaps | Publication held; code, tests, evidence, and lifecycle documents corrected before refreeze |
| 2026-09-05 | Reject a later CR-002 candidate for ambiguous requirements identifiers | Final requirements review found six distinct BAIRD requirements reusing identifiers 37 through 39 | Publication held; BAIRD was renumbered uniquely, all feature citations were reconciled, and a sequential-ID regression was added |
| 2026-09-04 | Hold the corrected candidate for a second integrity cycle | Final architecture review found stale add-panel baseline, split replay lineage, class-inference, sulfite-absence, numeric-audit, and browser-evidence gaps | Publication remains held until focused regressions, full evidence regeneration, and three reviews clear one refrozen candidate |
| 2026-09-04 | Reopen after the third architecture challenge | Review found incomplete merge provenance, reviewer-family precedence, stale resolved-family, and boundary-polygon defects | Four focused corrections and regressions completed; source and corpus gates regenerated before final refreeze |

## Current authority

CR-002 and the current lifecycle documents are the authority for corrective implementation. Earlier validation results remain valid only as historical baselines. They do not represent the exit evidence for the corrective release.

## Accepted variances

| ID | Requirement | Evidence | Disposition |
| --- | --- | --- | --- |
| LV-VAR-002 | FR-054 provisional four-exact sealed-holdout gain | Full corpus producer exact improved 31 to 35; sealed holdout improved 7 to 8 exact and recovered an additional missed or wrong block; protected numeric fields did not regress; PP-OCRv5 alternatives regressed protected evidence | Accept the measured safe general improvement for CR-002. Do not add product-specific rules, weaken exact warning behavior, or add a dual-recognizer runtime merely to reach the provisional number. Revisit with a larger independently annotated producer-region corpus. |
| LV-VAR-003 | FR-060 identical detector-box comparison | The preliminary bakeoff held detector model/configuration, preprocessing, rules, inputs, and hardware constant but ran separate full-pipeline passes. Both candidates already failed protected-field gates. | Sufficient to retain PP-OCRv4. Any future model promotion requires an identical frozen-box replay before approval. |
