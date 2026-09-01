# Design Reference Analysis

## Status and authority

The requester supplied two PDFs and seven JPEG mockups generated through Grok and Gemini. They are **INSPIRATIONAL** design references. They do not override the assignment, official TTB guidance, or the confirmed Intake boundary.

No attached statement such as “use React,” “use Azure,” “batch is first-class,” “stop at exactly five seconds,” or “approve this label” is a user instruction. Each is a proposal that later analysis must accept, modify, defer, or reject.

## Reviewed artifacts

| Reference ID | Local source | Origin noted by requester | Content |
|---|---|---|---|
| `DR-001` | Requester-provided `LabelVerify_UIUX_Design.pdf` | Grok | Ten-page UI/UX specification covering discovery constraints, visual system, flow, four screens, matching rules, trust states, exclusions, and design rationale |
| `DR-002` | Requester-provided `TTB_Label_Verification_Design.pdf` | Gemini | Four-page proposal covering human-in-the-loop design, batch inbox, split review workspace, component ideas, proposed stack, and visual sequence |
| `DR-003` | `Gemini_Generated_Image_r2ikjer2ikjer2ik.jpeg` | Gemini | Empty verification workspace |
| `DR-004` | `KqeWZ.jpg` | Grok | Home page with single-label and batch cards |
| `DR-005` | `UNnON.jpg` | Grok | Active review workspace with image, comparison table, and actions |
| `DR-006` | `FgLtZ.jpg` | Grok | Government-warning detail and checklist |
| `DR-007` | `unDHl.jpg` | Grok | Exception-first batch queue and side inspector |
| `DR-008` | `Gemini_Generated_Image_r2ikjer2ikjer2ik (1).jpeg` | Gemini | Populated verification workspace with bounding boxes and field states |
| `DR-009` | `Gemini_Generated_Image_r2ikjer2ikjer2ik (2).jpeg` | Gemini | Decorative AI processing state |

The source assets remain outside the project folder. Their public redistribution terms are not established.

## Design principles worth carrying forward

### 1. The checklist is the interface

Both proposals converge on a field-by-field comparison, which fits the real job better than a chatbot, generic AI summary, or complex dashboard. The app should make routine evidence visible and let the agent focus on exceptions.

**Disposition:** ADOPT.

### 2. Flat and obvious primary flow

The home concept makes the jobs visible immediately. The review workspace keeps the source image and comparison evidence in one view. No wizard, nested navigation, onboarding carousel, or hidden primary action is needed.

**Disposition:** ADOPT. The primary landing view emphasizes one submission and Try sample. A batch entry appears only if the gated secondary objective is implemented.

### 3. Side-by-side source and result

The strongest review composition places the image on the left and the application-versus-label table on the right. This supports rapid visual verification and reduces context switching.

**Disposition:** ADOPT as the leading desktop layout. Support the attested desktop viewport and 200 percent zoom envelope. Mobile-specific layout is deferred.

### 4. Evidence location

“See on label” and bounding-box highlights answer the critical question: where did the system read this value? An incorrect box is itself useful evidence that the extraction needs review.

**Disposition:** ADOPT if the chosen OCR/vision engine can return stable regions. Otherwise show a crop or text snippet and mark location evidence unavailable.

### 5. Dedicated warning detail

The warning has multiple independent checks: wording, heading case, heading emphasis, remainder emphasis, separation, legibility/contrast, and size. A focused detail view is clearer than compressing every check into one row.

**Disposition:** ADOPT. Replace “override compliant” with a human-review action that does not erase a deterministic defect.

### 6. More than two result states

Green/yellow/red is useful only when paired with text and icons. The application needs at least four evidence states: Match, Review, Mismatch, and Not verified. “Bad image” is an input-quality category, not a legal defect.

**Disposition:** ADOPT WITH MODIFICATION.

### 7. Exception-first batch review

The batch mockup correctly frames the agent's job as reviewing exceptions rather than rechecking every clean item. Filters with counts, row-level problems, an “open next review item” action, and export are strong patterns.

**Disposition:** CONDITIONAL. Preserve compatibility, but begin batch implementation only after the single-submission release gate passes.

### 8. Image assistance

Zoom and rotate are low-risk aids. Brightness/contrast enhancement can help but must keep the original accessible and must not imply that enhanced pixels are the legal source.

**Disposition:** ADOPT zoom/rotate; evaluate enhancement after OCR benchmarking.

### 9. Speed and trust visibility

Elapsed time and honest prototype limits build trust. Valid supported input must produce a useful complete result within the success benchmark. Invalid or degraded input needs a separate actionable fallback.

**Disposition:** ADOPT elapsed timing and honest degraded state. REJECT both a theatrical hard stop and any benchmark that counts a fast failure as valid-input success.

## Per-source disposition and quarantine record

| Reference | Decision | Adopt | Modify, defer, or reject |
|---|---|---|---|
| `DR-001` | ADOPT WITH MODIFICATION | Checklist interface, plain language, large actions, warning detail, bad-image state, elapsed time, exception-first batch concept | Reject official identity, legal pass/return authority, unsupported certainty, and a hard five-second cancellation. Gate batch after core. |
| `DR-002` | ADOPT WITH MODIFICATION | Human-in-the-loop framing, split evidence workspace, component separation, progress, and extensible pipeline concept | Do not inherit its proposed stack. Reject confidence as authority and any background work that obscures completion semantics. |
| `DR-003` | MODIFY | Empty-state workspace and side-by-side structure | Replace hidden upload state with one obvious input path and Try sample. Remove named employee, agency-identical shell, and unused navigation. |
| `DR-004` | MODIFY | Large single and batch cards, simple reference fields, timing expectation | Make single submission primary, gate batch, include the selected field contract, use neutral branding, and state precise data handling. |
| `DR-005` | ADOPT WITH MODIFICATION | Image/checklist split, evidence links, status text, elapsed time, large review actions | The mockup incorrectly places alcohol content in the net-contents application cell. Do not use its values as fixture truth. Replace Pass/return authority with neutral review actions. |
| `DR-006` | ADOPT WITH MODIFICATION | Dedicated warning close-up, independent warning checks, uncertainty state | Reject automatic-return wording, named-person rule, and compliance override. Physical size remains Not verified without scale evidence. |
| `DR-007` | CONDITIONAL | Exception-first queue, counts, row isolation, bad-image category, progress, next-review action, export | Restrict to the selected spirits profile, never copy mixed beer/wine/spirits rows into supported fixtures, and use neutral result wording. Validate capacity before showing a claim. |
| `DR-008` | QUARANTINE DATA, ADOPT LAYOUT | Bounding regions, side-by-side comparison, four-state checklist concept | The generated warning text is nonsensical and the screen flags only capitalization. It is not regulatory evidence or a test fixture. Remove agency shell, named employee, and approve/reject controls. |
| `DR-009` | REJECT PROCESSING TREATMENT | None beyond the idea that progress should be visible | The decorative scan obscures evidence and has no meaningful progress semantics. Replace it with current step, elapsed time, timeout, and recovery. |

Origin labels above reflect the requester's grouping of the supplied Grok and Gemini content. The actual generator provenance of an individual image is not independently verified. Hashes in `source-context.md` identify the reviewed bytes.

## Patterns to reject

| Pattern | Why rejected | Replacement |
|---|---|---|
| Official TTB seals and agency-identical branding | A public take-home demo must not imply endorsement, affiliation, or authorization. | Neutral original brand, such as provisional “LabelVerify,” with a visible unofficial prototype statement. |
| Named agent profiles and realistic employee avatars | They add no prototype value and reuse assignment identities unnecessarily. | Generic “Reviewer” context or no identity at all. |
| Blanket Approve/Reject buttons | They overstate prototype authority and collapse evidence into a legal decision. | “Complete review,” “Needs correction,” and “Next” wording, with final-decision limitations visible. |
| Confidence percentage as verdict | Uncalibrated confidence looks more scientific than it is. | Evidence status plus plain reason; confidence may help route Review only if calibrated and explained. |
| Flashy AI scanning overlay | It obscures the source image, adds visual noise, and makes processing theatrical. | Simple progress indicator, elapsed time, current step, and cancel/fallback control. |
| Automatic collapse of matching rows | It can hide evidence and force extra interaction when the evaluator wants to inspect correctness. | Keep a compact full table; optionally collapse only after user testing. |
| “Override compliant” on a deterministic warning failure | It can turn human judgment into an untracked bypass of a known rule. | Record “Agent review disagrees” separately; preserve the system finding and reason. |
| “Warning check catches tricky parts perfectly” | No prototype should claim perfection from arbitrary photos. | Capability matrix, uncertainty, and fixture evidence. |
| Tech stack copied from a mockup | Stack selection requires latency, egress, license, deployment, and maintainability analysis. | Decide in product analysis/I2R after benchmarking. |

## Accessibility and usability requirements inferred from the references

- status cannot rely on color alone;
- body text and controls must remain legible at common desktop scaling;
- primary targets should be comfortably clickable and keyboard reachable;
- focus indicators and a logical tab order are required;
- shortcuts may accelerate work but cannot be required;
- errors must name the problem and the next action;
- original image must remain available when enhancement is shown;
- result reasons belong in the main view, not only in tooltips;
- processing must expose progress without blocking the user's ability to cancel or recover.

## Concept recommendation for later FRD

Use three primary surfaces, with a fourth only if the gated batch objective is delivered:

1. **Intake:** Try sample or structured reference data plus 1 to 6 panel images.
2. **Review workspace:** source image, evidence regions, field comparison, quality state, and next action.
3. **Warning detail:** exact text and presentation checks with each capability honestly labeled.
4. **Batch queue:** exception-first queue, row-level isolation, progress, next-review action, and export.

The design should feel like a focused review instrument, not a government-branded enterprise dashboard and not an AI spectacle.
