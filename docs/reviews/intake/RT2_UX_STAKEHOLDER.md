# Intake Red Team 2: UX and Stakeholder Fidelity

**Reviewer role:** Independent UX and stakeholder red team  
**Review date:** 2026-08-31  
**Stage reviewed:** Intake / Checkpoint A  
**Verdict:** **REWORK_REQUIRED**

## Executive verdict

The Intake identifies the right product thesis: a fast, simple, evidence-backed verification assistant that reduces routine comparison work while preserving human judgment. It also correctly treats the Grok and Gemini materials as design proposals rather than requirements. The recommended distilled-spirits core, exception-first batch extension, side-by-side evidence workspace, explicit uncertainty, and warning-detail concept are directionally right.

The package does not yet clear Intake. Two material contradictions remain:

1. the proposed five-second acceptance contract can pass when a valid supported request returns an actionable failure instead of a completed result, and it only binds the warmed application;
2. the scope calls the path fully supported distilled-spirits verification while the input contract accepts one image even though required information may appear across multiple label panels.

These gaps could let the project meet its own tests while missing the assignment's most important stakeholder outcomes. Several medium findings also need correction before the scope is stable enough for architecture and FRD work.

## Evidence reviewed

### Authoritative assignment evidence

The review used the complete take-home assignment supplied in the initiating conversation, including:

- the approximately five-second adoption expectation;
- the requirement for a clean and obvious experience for users with varied technical comfort;
- the need to preserve judgment for differences such as capitalization and punctuation;
- the exact government-warning wording and heading treatment concern;
- the desire to handle poor images where feasible;
- the 200 to 300 item peak batch problem;
- the standalone, no-COLA-integration boundary;
- the blocked-outbound-network constraint;
- the preference for a working core over ambitious incomplete features;
- the source repository, source code, README, documentation, and deployed URL deliverables.

### Project documents

Every file under the project root was read, including `AGENTS.md`, `README.md`, `docs/PROCESS.md`, the complete Intake package, all registers, and all decision records.

### Supplied design evidence

Both PDFs were read in full and every page was rendered and visually inspected:

- Requester-provided `LabelVerify_UIUX_Design.pdf`, 10 pages;
- Requester-provided `TTB_Label_Verification_Design.pdf`, 4 pages.

All seven supplied JPEG mockups were inspected at original resolution:

- `Gemini_Generated_Image_r2ikjer2ikjer2ik.jpeg`;
- `KqeWZ.jpg`;
- `UNnON.jpg`;
- `FgLtZ.jpg`;
- `unDHl.jpg`;
- `Gemini_Generated_Image_r2ikjer2ikjer2ik (1).jpeg`;
- `Gemini_Generated_Image_r2ikjer2ikjer2ik (2).jpeg`.

### Regulatory evidence checked for UX consequences

Current official TTB guidance confirms that the warning may appear on a front, back, or side label and that other mandatory distilled-spirits information may appear on any label. It also confirms the separate warning checks and physical-size limitations already recognized by the Intake:

- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning
- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label
- https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling

## Assignment fit assessment

| Evaluation area | Intake assessment | Result |
|---|---|---|
| Correctness and core completeness | The Intake correctly centers label-to-reference comparison, warning checks, uncertainty, human review, and failure handling. The single-image versus full-label scope conflict remains material. | PARTIAL |
| Code quality and organization | The proposed separation of extraction, normalization, rules, UI contracts, tests, and traceability is stronger than the assignment explicitly requests. | EXCEEDS AT PLAN LEVEL |
| Technical choices | The Intake correctly avoids selecting a stack before latency, egress, hosting, and OCR feasibility work. | MEETS |
| User experience and error handling | Plain status, image evidence, failure states, and low-tech simplicity are strong. The latency contract, sample journey, and accessibility proof need correction. | PARTIAL |
| Attention to requirements | Deliverables, network limits, warning nuance, batch value, and no-false-clean-pass behavior are all captured. | MEETS WITH GAPS |
| Creative problem solving | Exception-first batch handling, dedicated warning evidence, and evidence-location interaction are appropriate and restrained. | EXCEEDS |
| Time-constrained delivery judgment | A complete distilled-spirits core followed by a gated batch extension is the right sequencing. | MEETS |

Overall, the Intake is more disciplined than the assignment requires, but it cannot yet be said to meet or exceed every requirement because its own acceptance language can mask a failed primary outcome and its scope wording overstates what one image can prove.

## Comparative disposition of every supplied design source

| ID | Source | Useful contribution | Risk or defect | RT2 disposition |
|---|---|---|---|---|
| `DR-001` | `LabelVerify_UIUX_Design.pdf` | Best articulation of the checklist-as-interface concept, large actions, plain voice, visible latency, dedicated warning review, bad-image state, and exception-first batch flow. | Treats batch as first-class before core proof, uses official-looking identity, proposes a five-second hard stop, uses legally loaded pass/return actions, and sometimes treats normalized variation inconsistently. | ADOPT structure and voice principles. MODIFY latency and result actions. REJECT official identity and hard-stop behavior. |
| `DR-002` | `TTB_Label_Verification_Design.pdf` | Strong split workspace, bounding-box evidence, fuzzy-match escalation, and image tools. | Starts from batch, proposes prefetching before the single path is proven, uses Approve/Reject, says decisions are saved despite an ephemeral prototype, claims the warning can be caught perfectly, auto-collapses matches, and prescribes cloud/LLM technology without evidence. | ADOPT split workspace and evidence interaction. REJECT legal actions, perfect-accuracy language, automatic collapse, persistence assumptions, and copied stack choices. |
| `DR-003` | Empty Gemini workspace | Shows a reusable desktop workspace shell and clear two-column region. | The empty screen contains a hamburger menu, global search, notifications, profile, unused navigation icons, disabled controls, and a batch queue before the primary task begins. This is too much chrome for the stated user. | REJECT the enterprise shell. Keep only the simple two-column workspace. |
| `DR-004` | Grok home image | Makes single and batch jobs immediately visible, uses large targets, and states the approximate result time. | Equal visual weight makes batch look committed before `DEC-002`. Official seal, named employee, and a categorical nothing-is-stored statement are unsafe unless implementation proves them. The form omits several fields in the proposed complete spirits path. | ADOPT the card clarity. Gate the batch card. Use neutral branding and precise retention copy. |
| `DR-005` | Grok review image | Strongest visual direction for side-by-side image, expected versus found values, evidence links, image quality, and large next actions. | The Net contents application cell incorrectly shows an alcohol-content value. Confidence percentages appear more prominent than reasons. Pass/return language can imply a legal decision. | ADOPT layout only. Correct data semantics, subordinate or omit uncalibrated confidence, and use verification-assistant actions. |
| `DR-006` | Grok warning detail image | Correctly separates wording, capitalization, emphasis, separation, contrast, legibility, and uncertain physical size. | The image presentation is ambiguous because an all-caps heading and a title-case heading both appear. The override-compliant action can erase a deterministic defect or imply legal authority. | ADOPT the detailed checklist. Preserve system findings and record human disagreement separately. |
| `DR-007` | Grok batch queue image | Excellent exception-first queue, counts, row isolation, bad-image category, progress, next-review action, and export concept. | It mixes spirits, wine, and beer rows even though category-specific rule coverage is unresolved. Passed and Failed labels overstate authority. | CONDITIONAL on `DEC-002`. Restrict rows to supported beverage rules and use neutral result language. |
| `DR-008` | Populated Gemini workspace | Bounding boxes and explicit expected-versus-extracted values directly support trust and review speed. | The label warning is visibly nonsensical, yet the UI reports only a capitalization failure. The image also duplicates 750 mL. An Approve action remains available with a failed warning. | ADOPT evidence highlighting only. Explicitly reject the mock result as correctness evidence. |
| `DR-009` | Gemini processing image | Communicates that work is underway. | The scanning overlay obscures the source, is visually noisy, has no useful progress semantics, and could distract or create accessibility problems. | REJECT. Use a simple status line, elapsed time, current step, and recovery action. |

The existing `design-reference-analysis.md` reaches most of these pattern-level conclusions, but it needs an explicit per-source disposition so the known mockup defects cannot later become accidental requirements or fixture truth.

## Stakeholder scenario tests

| Scenario | Expected stakeholder outcome | Intake result | Assessment |
|---|---|---|---|
| First-time low-tech user checks one complete fixture | One obvious path, no external instructions, plain errors, large controls. | The primary journey and low-friction intent are explicit, but no in-product sample path is committed and the full manual field contract is unresolved. | PARTIAL |
| Valid supported label on a warmed deployment | Completed field-level result in about five seconds. | The success contract permits either a complete result or an actionable failure in five seconds. | FAIL |
| Valid supported label on the evaluator's first cold request | A useful result fast enough not to recreate the prior vendor failure. | Cold-start behavior is only reported separately and has no pass threshold. | FAIL |
| Brand `STONE'S THROW` versus `Stone's Throw` | Human Review with an explanation, never silent exactness or automatic rejection. | Explicitly routes to Review and preserves exact versus normalized difference. | PASS |
| Warning has title-case heading | Deterministic wording/presentation finding with visible evidence. Human judgment does not delete the finding. | Dedicated checks and no unsupported blanket approval are specified. | PASS |
| Warning or address is on a back panel not present in the single uploaded image | Coverage limitation is explicit and the submission cannot be clean. | Not verified behavior is strong, but the product still calls the one-image path fully supported distilled-spirits verification. | FAIL |
| Glared or angled image | Preserve original, separate quality from a regulatory mismatch, offer bounded assistance, never invent text. | Correctly specified. | PASS |
| Network blocks inference endpoint | Actionable degraded state with no crash or false result. | Correctly specified, but the failure must not count as satisfying successful latency. | PARTIAL |
| Batch of 247 items contains one bad image and mixed results | Row failures are isolated, progress is visible, agent reviews exceptions. | Correctly designed as a gated extension, but category scope must constrain batch fixtures. | PASS IF GATED |
| Evaluator opens public demo with no test data | A safe example is immediately available and no private upload is encouraged. | Curated fixtures are planned, but no visible Try sample or downloadable example journey is required. | PARTIAL |
| Keyboard and low-vision user completes the core flow | Full keyboard operation, visible focus, announced status, associated errors, useful zoom/reflow, no color-only meaning. | Keyboard and no-color-only behavior are present, but the rest of the acceptance envelope is undefined. | PARTIAL |

## Findings

### RT2-001: Valid-request latency can pass by failing quickly

**Severity:** HIGH  
**References:** `docs/intake/success-definition.md:41`, `docs/intake/success-definition.md:64`, `docs/intake/INTAKE_DOCUMENT.md:150`, `docs/intake/assumptions.md:13`

The proposed performance requirement accepts a complete result or an actionable failure within five seconds. That allows an implementation to time out every valid supported image at five seconds and still pass the most important adoption gate. The warmed-only condition also excludes the evaluator's first experience on a public deployment.

This does not faithfully represent the stakeholder statement. The stakeholder wants results in about five seconds because a 30 to 40 second system was abandoned. Failure handling is necessary, but it is not a substitute for successful performance on supported inputs.

**Required change:** Separate successful latency from failure responsiveness.

- For a fixed supported fixture set, require a completed field-level result within five seconds under a documented environment and repeated-run measurement.
- Measure and publish cold and warm results separately.
- Give the deployed first-use path a pass threshold or require a hosting approach that avoids an uncontrolled cold start.
- Test service timeout and blocked-network behavior as resilience criteria, not as evidence that successful latency passed.
- Keep partial evidence after a timeout, but do not count the timeout as a successful verification result.

### RT2-002: Fully supported distilled-spirits scope conflicts with a one-image evidence contract

**Severity:** HIGH  
**References:** `docs/intake/INTAKE_DOCUMENT.md:77-79`, `docs/intake/scope-boundary.md:11-16`, `docs/intake/regulatory-source-register.md:9-11`

The scope promises a fully supported distilled-spirits reference path covering brand, class/type, alcohol content, net contents, name/address, import origin, and the warning, while the core journey accepts one supported image. Official TTB guidance permits the warning and other mandatory information on different label panels. One photograph or one cropped front-label image cannot prove complete coverage.

The current Not verified state prevents a false clean pass, which is good, but it does not resolve the scope claim. A path that routinely cannot see the back or side label is not fully supported mandatory-information verification.

**Required change:** Choose and state one evidence contract before BAIRD.

Preferred narrow option:

- accept one label-artwork image only when it contains every in-scope panel for the fixture;
- call the capability a supported distilled-spirits comparison path, not complete container compliance;
- aggregate every absent required field to Review needed;
- show panel coverage explicitly.

Alternative option:

- accept a small ordered set of front, back, and side images for one application;
- associate evidence regions with their source image;
- require all expected panels or return Review needed.

Do not keep the current combination of fully supported language and a single unspecified image.

### RT2-003: The evaluator has no guaranteed self-starting demo path

**Severity:** MEDIUM  
**References:** `docs/intake/success-definition.md:16-22`, `docs/intake/scope-boundary.md:21`, `docs/intake/initial-risk-notes.md:12`, `docs/intake/initial-risk-notes.md:17`

The Intake requires curated fixtures and says the primary journey should work without external instructions, but it never commits an in-product example. A take-home evaluator may not have a label image and correctly paired application data ready. Manual entry of a complete spirits record also adds effort before the evaluator sees the product's value.

**Required change:** Add a Must requirement for a visible `Try a sample` path that loads a sanitized reference record and label artwork. Include at least one clear match, one Review case, one deterministic mismatch, and one poor-image example in the repository. The example path must exercise the same production code path as user uploads.

### RT2-004: Public-demo data handling is honest in principle but incomplete in user-facing policy

**Severity:** MEDIUM  
**References:** `docs/intake/source-requirements.md:83-87`, `docs/intake/scope-boundary.md:24`, `docs/intake/design-reference-analysis.md:84-94`

The Intake correctly avoids persistence and official affiliation, but a public upload control can still invite users to submit real labels or application data. Cloud hosts, request logs, crash telemetry, temporary files, and model providers may retain data even when the application does not have a database. A categorical `nothing is stored` message is unsafe until architecture verifies the complete path.

**Required change:** Require visible pre-upload copy limiting the prototype to provided samples or synthetic/sanitized data. Require the final UI and README to describe actual transport, temporary processing, third-party transmission, logs, and retention behavior based on the implemented architecture. Do not use categorical no-storage wording that the deployment cannot prove.

### RT2-005: Accessibility is named but not yet testable

**Severity:** MEDIUM  
**References:** `docs/intake/INTAKE_DOCUMENT.md:81`, `docs/intake/scope-boundary.md:20`, `docs/intake/source-requirements.md:28-30`, `docs/intake/design-reference-analysis.md:97-105`

Keyboard reachability, visible focus, and no-color-only status are good starts. They do not define how upload errors, progress, changed evidence, tables, image controls, zoom, or responsive layout work for assistive technology and low-vision users. The word accessible can otherwise survive into the FRD without a binary proof.

**Required change:** Carry a core-flow accessibility acceptance envelope into the FRD. At minimum, define:

- WCAG 2.2 AA as the target for the supported core journey;
- logical keyboard order and no keyboard trap;
- visible focus and accessible names for upload and image tools;
- programmatic labels and error association for form fields;
- announced processing and result-state updates;
- non-color status communication;
- usable layout at 200 percent browser zoom;
- semantic comparison data that remains understandable outside a visual table;
- automated checks plus a manual keyboard and screen-reader smoke test.

### RT2-006: Design-source traceability is pattern-based and leaves known mockup defects implicit

**Severity:** MEDIUM  
**References:** `docs/intake/design-reference-analysis.md:11-21`, `docs/intake/source-context.md:13-15`, `docs/intake/source-context.md:33-39`

The current analysis lists every design artifact but records dispositions by pattern, not by source. Several images contain concrete semantic errors that should be explicitly quarantined: the review image places alcohol content in the Net contents application cell; the populated Gemini workspace shows nonsensical warning text while flagging only capitalization; the batch image mixes beverage categories before scope is decided; and the processing image obscures the label.

The requester said the materials came from Grok and Gemini but did not explicitly map every file to one generator. The current source register presents exact attribution as established fact.

**Required change:** Add a per-source disposition table to `design-reference-analysis.md`, including these defects. If generator mapping was inferred rather than stated, label it inferred or use `Grok/Gemini supplied reference` without unsupported precision.

### RT2-007: Responsive scope is ambiguous

**Severity:** LOW  
**References:** `docs/intake/INTAKE_DOCUMENT.md:81`, `docs/intake/scope-boundary.md:20`, `docs/intake/design-reference-analysis.md:43`

The stakeholders and all supplied concepts point to a desktop review workstation. `Responsive` can expand into a polished mobile product even though native mobile is excluded and mobile work is not part of the primary scenario.

**Recommended change:** State that the product is desktop-first, with a defined minimum supported viewport and functional reflow for browser zoom and narrower windows. Treat phone optimization as out of scope unless later justified.

## Decisions that are correct and should be preserved

The following Intake decisions are supported by the assignment and the comparative design evidence:

1. Keep the product a verification assistant, not a legal approval engine.
2. Use the checklist as the main interface rather than a chatbot or AI spectacle.
3. Use a side-by-side source and comparison workspace on desktop.
4. Preserve exact, normalized, ambiguous, mismatched, and not-verifiable distinctions.
5. Route `STONE'S THROW` versus `Stone's Throw` to human Review with a reason.
6. Split warning checks and preserve uncertainty for typography, scale, separation, contrast, and legibility.
7. Keep original imagery available and treat enhancement as a visual aid.
8. Separate bad-image status from regulatory mismatch.
9. Reject official seals, real employee profiles, and implied TTB affiliation in a public take-home.
10. Gate batch after a verified single-label core, while keeping the architecture compatible with an exception-first batch extension.
11. Keep wine and malt-beverage completeness out of the core unless dedicated rule packs and fixtures are funded by the timebox.
12. Reject copied technology choices until latency, egress, hosting, license, and deployment evidence exists.
13. Preserve the no-false-clean-pass invariant.

## Required rework before Intake can clear

1. Rewrite the latency success contract so valid supported requests must complete successfully within the target and failure responsiveness is measured separately.
2. Resolve the one-image versus complete-label evidence boundary.
3. Commit a self-starting sample journey for the evaluator.
4. Add a public-demo safe-data and actual-retention disclosure requirement.
5. Make core accessibility acceptance binary and testable.
6. Add per-source dispositions and explicit mockup defects to the design analysis.
7. Clarify desktop-first responsive scope.

After these changes, rerun the Intake red team against the updated files and decisions. BAIRD should not treat the current latency or image-coverage wording as an approved architecture input.

## Binary verdict

**REWORK_REQUIRED**

The Intake has the right product direction and most of the right controls, but the two HIGH findings change SUCCESS and BOUNDARY. They must be corrected before this independent reviewer can return CLEAR.
