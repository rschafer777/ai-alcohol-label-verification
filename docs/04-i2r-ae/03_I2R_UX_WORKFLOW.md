# I2R User Experience and Workflow Specification

Document control ID: LV-I2R-003  
Revision: 1.0  
Date: 2026-08-31  
Status: Draft for combined I2R and FRD review

## 1. Experience objective

A first-time evaluator with low technical comfort can understand the product, try a complete example, enter a manual record, add label panels, correct errors, receive a complete result, inspect evidence, and start over without outside instructions.

## 2. Page model

Use one responsive application shell and two primary workspace states:

1. Intake state: prototype notice, Try sample, structured reference form, panel intake, Verify.
2. Result state: label viewer and evidence controls on the left, field comparison checklist on the right, summary and next actions at the top.

No login, dashboard, hidden navigation, search, notification center, or decorative AI animation is included.

## 3. Primary journeys

### Try sample

1. Activate Try sample.
2. App loads one synthetic record and the required synthetic panels.
3. User can inspect or directly verify.
4. Processing status is announced.
5. Complete result appears and focus moves to the summary.
6. User selects a check and the associated panel region receives visible focus.
7. Start over clears the session.

### Manual verification

1. Enter required reference values.
2. Mark imported status; origin appears only when required.
3. Add 1 to 6 images by file picker or drag/drop.
4. Review previews, reorder or remove panels, and see count and file validation.
5. Activate Verify.
6. Invalid fields receive inline messages and focus moves to the first error.
7. Correct errors and verify again.
8. Complete result appears with summary, field table, limitations, and evidence actions.
9. Start over clears current browser data.

### Failure and recovery

- Invalid file: identify the panel and allowed formats.
- Unreadable image: keep other evidence, mark affected checks Review or Not verified, request a clearer panel.
- Busy capacity: tell the user the verifier is busy and offer Retry.
- Upload timeout: explain that upload did not finish and offer smaller files or Retry.
- Inference timeout: state that no result was issued, offer Retry, and preserve form and selected browser files when safe.
- Internal error: no prior result remains visible as current; offer Retry and Start over.
- User cancellation: enter Cancelled within 1 second, preserve form values and selected browser file objects, and offer Verify again or Start over.

## 4. Result vocabulary

| Machine state | User label | Meaning |
|---|---|---|
| Match | Match | Sufficient evidence supports the expected value or a documented safe representation |
| Mismatch | Difference | Sufficient evidence shows a definite difference |
| Review | Review | Evidence exists but judgment or ambiguity remains |
| Not verified | Not verified | Required evidence is absent, unreadable, unsupported, or not measurable |

Submission summaries:

- No differences found in checked fields
- Review needed
- Differences detected

Forbidden result wording: Approved, TTB approved, compliant, rejected, failed application, or any equivalent legal disposition.

## 5. Evidence interaction

- Selecting a field chooses its source panel and outlines the evidence polygon.
- A field with material alternatives shows one action per observed value, such as Show CANADA and Show USA.
- Evidence-unavailable rows explain why and do not display a fake crop.
- Original and enhanced views are clearly labeled. Original is always recoverable.
- Zoom, rotate view, fit, and reset operate only on the display and do not change machine findings.
- Warning review expands independent wording, heading case, heading emphasis, remaining-text emphasis, continuity, separation, contrast, legibility, and physical-size limitation rows.

## 6. Accessibility contract

- semantic landmarks, headings, labels, tables/lists, buttons, and status regions;
- complete keyboard operation with logical focus order and visible focus;
- focus moves to the first invalid field after failed client validation;
- processing and result summaries use polite live-region announcements;
- text and icon convey status, never color alone;
- WCAG 2.2 AA contrast for text and interactive controls;
- core flow usable at 200 percent zoom at 1024 by 768 and larger supported desktop sizes;
- touch targets and spacing support older users and reduced precision;
- no unexpected context change on focus or field selection;
- automated axe checks plus manual keyboard and NVDA smoke.

## 7. Visual direction from Grok and Gemini

Retain:

- concise government-service visual restraint;
- navy, white, neutral gray, green, amber, and red with text labels;
- large obvious upload and Verify controls;
- side-by-side evidence and result workspace;
- compact comparison rows with evidence actions;
- focused warning detail;
- exception-first batch queue with progress, filters, row detail, retry, cancellation, and export.

Reject or correct:

- official seals or visual claims of TTB affiliation;
- Approve and Reject buttons;
- decorative AI scanning effects;
- incorrect or unreadable generated warning text;
- field/value mixups;
- hiding incomplete analysis behind a clean status;
- dense navigation that is not required for the take-home.

## 8. Responsive boundary

The committed evaluator envelope is desktop-first Chrome and Edge from 1024 by 768 through 1920 by 1080. At narrower widths, the result columns stack without data loss, but mobile-specific optimization is not a release claim.

## 9. Session behavior

- Current form, file objects, result, reviewer note, and display choices exist only in browser memory.
- Start over opens a confirmation dialog whenever any form value, selected file, result, evidence selection, or reviewer note exists. Cancel leaves all work unchanged. Confirm clears all current browser state.
- Refresh and close lose the session; the UI states this before verification and near reviewer notes.
- No browser local storage, IndexedDB, service worker content cache, or analytics stores user content.
