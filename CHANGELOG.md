# Changelog

This file summarizes material product changes. Detailed reasons, evidence, affected requirements, and verification status are maintained in `docs/00-governance/CHANGE_CONTROL_REGISTER.md`.

## CR-002 corrective release candidate

### Implemented

- Separated machine findings, trusted application data, reviewer dispositions, and reviewer-corrected label observations.
- Added immutable correction and add-panel revision lineages with server-side re-evaluation. Corrections invoke OCR zero times and preserve the original pixels, OCR value, evidence, prior result, actor label, reason, and timestamp.
- Bound every correction replay to the immutable source image hash, panel, and polygon; retained the original snippet and persisted both the reviewer-visible transcription and the server-derived representation, including producer components.
- Made replay use the latest value and source locator for each corrected field, and made add-panel processing refresh label-derived comparison values from the fresh complete OCR read while preserving trusted and reviewer-corrected fields.
- Added controlled beverage-family correction, class-driven family re-inference, reviewer-drawn evidence regions when OCR has no box, and positive-only visible sulfite correction so typed text cannot assert chemical absence.
- Preserved printed ABV and proof wording, numeric precision, alcohol ranges, and net-content units in correction audit records.
- Preserved unresolved beverage type through correction and add-panel revisions until label evidence or an explicit cited reviewer correction resolves it; no default beverage profile is substituted.
- Preserved fresh OCR timing, limitations, and model identity on add-panel revisions, and made check presentation use each field's provenance instead of a record-wide shortcut.
- Preserved explicit provenance for every field during mixed-source add-panel merges, including the malt alcohol-source trigger; allowed fresh contradictory or insufficient label evidence to return a previously label-derived family to unresolved; and prevented a later class correction from overriding an explicitly reviewer-corrected family.
- Reconciled every returned add-panel draft with the merged reference persisted to history so trusted-application, fresh OCR, and reviewer-corrected values cannot be paired with the wrong source.
- Applied one authoritative original-pixel polygon rule to OCR and reviewer-selected evidence: coordinates remain inside the half-open image bounds and the polygon must have positive area.
- Hardened invalid-history-ID mutations at the same Origin, body-size, and rate boundaries as valid IDs; aligned documented public error names with the error registry.
- Changed history blob cleanup to commit metadata deletion before unlinking files and added startup orphan reconciliation for interrupted cleanup.
- Bound tracked validation evidence to Git's canonical LF source bytes so the release manifest, staged tree, and reported source hashes describe the same candidate.
- Assigned unique sequential identifiers to all 42 BAIRD derived requirements, reconciled the affected feature citations, and added a release regression that rejects duplicate or broken BAIRD numbering.
- Replaced inferred Front and Back result labels with neutral Image 1, Image 2, and Image 3 labels.
- Added constrained numeric-brand recovery based on pixels, geometry, prominence, class proximity, trademark context, and repetition, with quantity, year, age, postal, code, price, and deposit exclusions.
- Added blocking-check identifiers and normalized review-cause categories to every overall Review result.
- Improved producer role, wrapped-line, column, entity, and location assembly without normalizing OCR errors into trusted text.
- Compared the current PP-OCRv4 English recognizer with PP-OCRv5 English and Latin candidates. Neither candidate passed the protected-field promotion gate, so production retains PP-OCRv4.
- Added a sealed 24-product holdout, per-field scoring, OCR bakeoff evidence, and explicit oracle-conflict exclusions.
- Kept unsupported or uncertain language in Review. No translation, general-purpose language model, vision-language model, or external inference endpoint was added.

### Validation status

- The complete local source gate passes 412 Python and validation tests, strict typing, Python and frontend lint, 38 frontend tests, the 134-module production build, and applicable browser and accessibility workflows.
- The complete local release gate also passes the governed and private image corpora, batch timing, field ground truth, sealed product holdout, Python and production npm dependency audits, and the 375-entry release manifest.
- The final independent security diff review covered all 46 changed executable and contract surfaces with complete coverage, no deferred surface, and no reportable finding.
- The final local image and holdout evidence is recorded under `docs/08-validation/evidence/`.
- The exact candidate was committed as `0e9e79f37b074ba2f432ec7f6cf3e99495a4f007` and deployed through protected GitHub Actions run `33942995735`. Azure resource readback, immutable digest, HTTPS, health, exact build metadata, public sample, history, and engineering browser pre-UAT gates passed. Requester UAT remains open.

### Evidence prompting the corrective release

- The 221-image technical corpus completed successfully but routed most products to Review.
- The 42-case disposition oracle contained 30 expected-Pass cases, of which 27 were conservatively routed to Review.
- Producer extraction was exact in 31 of 65 applicable scored cases before the corrective work. Final results remain separately recorded rather than replacing that baseline.
- User acceptance testing exposed positional image-role labels, numeric-brand rejection, and a reviewer correction path that reran OCR and conflated observation corrections with independent application data.
- Representative corpus performance had been measured on the development workstation. Deployed performance evidence covered repeated governed samples rather than unique representative photographs.

## Initial release candidate

### Delivered

- Local ONNX OCR with deterministic beverage-specific TTB checks for malt beverages, wine, and distilled spirits.
- One-product and batch workflows with up to three images per product and up to 300 products per batch.
- Original-pixel evidence localization, warning detail, reviewer disposition, 500-record FIFO history, and export.
- Bounded image preparation, supervised OCR execution, browser-scope history isolation, and same-origin deployment.
- GitHub Actions deployment to the Azure demonstration environment.
