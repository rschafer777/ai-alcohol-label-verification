# Scope Boundary

**Status:** ATTESTED through `DEC-001` and `DEC-002`  
**Decision authority:** Requester authorization recorded in `EVT-011`

## Committed release scope

### Product identity

- standalone browser-based proof of concept;
- human-in-the-loop comparison assistant, not a compliance decision authority;
- selected-check distilled-spirits demo profile;
- original neutral LabelVerify identity with no TTB seal or claim of official affiliation;
- public evaluator path plus local reproducibility from the repository.

### Submission and evidence contract

- one submission contains one structured reference/application record and 1 to 6 label-panel images;
- a single image is valid only when it visibly contains the evidence needed for the selected checks;
- the UI shows panel coverage and cannot infer that an absent panel is compliant;
- accepted prototype image types are JPEG, PNG, and WebP after content sniffing;
- the Intake establishes a bounded-input requirement, with exact encoded-byte, decoded-pixel, request, memory, and processing limits to be selected and justified in I2R A&E;
- the original image remains review evidence when a derived crop or enhancement is shown;
- invalid, corrupt, unsupported, oversize, or unreadable input receives an actionable non-clean state.

### Reference record and selected checks

The distilled-spirits demo profile evaluates only the following documented checks:

1. brand name comparison;
2. class/type comparison;
3. alcohol content comparison, including ABV/proof normalization where defensible;
4. net contents comparison with documented unit normalization;
5. producer/bottler name and address comparison;
6. country of origin comparison when the reference record marks the product imported;
7. government-warning prescribed text comparison;
8. government-warning heading capitalization;
9. warning heading emphasis, remaining-text emphasis, separation, contrast, continuity, and legibility only where image evidence supports the specific check;
10. image and panel coverage sufficient to report what was and was not evaluated.

Application-to-label equality, label-only presentation checks, and legal sufficiency are separate concepts. The app may report only the first two within the listed capability. It does not determine overall legal sufficiency.

### Result contract

- field states: Match, Review, Mismatch, and Not verified;
- submission summaries: No differences found in checked fields, Review needed, and Differences detected;
- any Mismatch produces Differences detected;
- otherwise, any Review or Not verified produces Review needed;
- No differences found in checked fields is allowed only when every applicable selected check has sufficient evidence and resolves to Match;
- reviewer disposition, if provided, is session-only and separate from immutable system findings;
- no result uses Approve, TTB approved, compliant, rejected, or equivalent legal-decision wording.

### User experience and accessibility

- one obvious single-submission path from input to result;
- an in-product Try sample action that loads synthetic reference data and all necessary panel images;
- side-by-side image evidence and field checklist on the result surface;
- plain-language reasons and next actions;
- desktop-first support for current Chrome and Edge at 1024 by 768 through 1920 by 1080;
- primary journey remains operable at 200 percent browser zoom;
- keyboard-only completion, visible focus, accessible names, associated validation errors, no color-only meaning, and WCAG 2.2 AA contrast targets;
- axe automated checks with no serious or critical findings in the core flow plus manual keyboard and NVDA review.

### Validation and delivery

- synthetic deterministic fixtures with independent expected outcomes and a holdout subset;
- automated unit, integration, security-boundary, accessibility, and primary-journey tests;
- source repository with all source code;
- README setup and run instructions;
- brief approach, tools, assumptions, trade-offs, and limitations documentation;
- deployed public URL;
- revision and deployment provenance plus post-deploy smoke evidence.

### Data handling

- public demo is explicitly limited to synthetic or sanitized, non-sensitive data;
- no intentional persistent storage of uploaded images, extracted text, or form data;
- no raw image or extracted-label content in application logs, analytics, or crash reports;
- temporary files, if I2R A&E determines they are necessary, are request-scoped, access-restricted, and deleted on success, timeout, cancellation, and error;
- any third-party inference transfer and retention behavior must be disclosed before release;
- the public UI must not promise more privacy than the implemented and tested data flow proves.

## Gated secondary objective

Batch is a Should-level secondary objective, not a core release blocker. Work begins only after every committed single-submission gate passes. If implemented, the FRD must define a manifest-plus-images contract, row-level failure isolation, progress, cancellation, retry, exception-first review, export, security controls, and a tested capacity claim. The intended proof target is up to 250 synthetic rows because the stakeholder described 200 to 300 item peaks. No batch UI or README claim may exceed the validated size.

Architecture should preserve a clean path to batch processing even if the submitted prototype omits the secondary objective.

## Explicitly out of scope

- direct COLAs Online or legacy COLA integration;
- parsing real COLA PDFs;
- autonomous approval, rejection, legal advice, or final compliance determination;
- comprehensive distilled-spirits compliance or validation of every rule in applicable law;
- wine and malt-beverage rule packs;
- age statement, standards-of-identity, formula, geographic claim, advertising, and marketing-truth review outside the selected checks;
- production federal authorization, FedRAMP certification, ATO, records schedules, e-discovery, or enterprise identity integration;
- user accounts, roles, administrative consoles, saved case history, or audit history;
- use of real PII, proprietary applications, or confidential labels;
- production throughput for 150,000 annual applications;
- guaranteed recovery of severe blur, glare, occlusion, perspective distortion, or missing panels;
- definitive physical type-size measurement without reliable scale and container evidence;
- native mobile or desktop applications;
- replacement or modernization of COLA;
- Argus code, runtime, branding, services, or infrastructure.

## Explicitly deferred

- saved review history and agency authentication;
- high-volume durable queue infrastructure;
- wine and malt-beverage rule packs;
- multilingual OCR and translation;
- continuous regulatory update service;
- agent-feedback learning loop;
- formal model calibration on representative production data;
- mobile-specific layout and testing.

## Boundary rationale

The assignment prefers a working core over ambitious incomplete features. This boundary implements the provided distilled-spirits example through a defensible selected-check profile, preserves uncertainty, accepts multiple panels, and still demonstrates extensibility. It avoids turning a take-home prototype into a false claim of comprehensive TTB review.

## Scope change rule

Any change to beverage categories, selected checks, batch release priority, decision authority, persistence, or external integration changes the build materially. It must update this document, the decision log, FRD traceability, tests, and release claims.

## Attestation record

| Decision | State | Actor | Selected outcome |
|---|---|---|---|
| `DEC-001` | CLOSED | Requester through bounded decision delegation in `USR-008` and `EVT-011` | Selected-check distilled-spirits demo profile with explicit exclusions and no completeness claim. |
| `DEC-002` | CLOSED | Requester through bounded decision delegation in `USR-008` and `EVT-011` | Batch is a gated Should-level secondary objective after the single-submission release gate. |
