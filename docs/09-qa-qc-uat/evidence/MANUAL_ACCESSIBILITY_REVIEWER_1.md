# Manual Accessibility Reviewer 1 Evidence

Document control ID: LV-A11Y-R1-001  
Revision: 1.0  
Date: 2026-09-01  
Reviewer pseudonym: LV-UAT-R1  
Reviewer role: Independent non-implementer evaluator and RT3 reviewer  
Scope: Manual keyboard, focus, visual, zoom, media-mode, and cross-browser observations required by T-030, excluding NVDA  
Verdict: FAIL

## 1. Candidate and environment

- Local application: `http://127.0.0.1:8000`
- Release manifest SHA-256: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Operating system: Microsoft Windows NT 10.0.26200.0
- Manual browser: Google Chrome 151.0.7922.175
- Edge browser used by the governed automated smoke: Microsoft Edge 152.0.4191.53
- Default viewport: 1443 by 1559 CSS pixels
- Required zoom viewport: 1024 by 768 pixels before applying the 200 percent content scale
- Assistive technology: NVDA intentionally NOT_RUN in this reviewer package; root will execute it separately
- Facilitator help: None

No source or existing documentation was changed. Temporary browser-only media and zoom emulation was restored after inspection.

## 2. Manual checks

| Check | Expected | Observed | Result |
|---|---|---|---|
| Keyboard focus order | Logical order follows the visual workflow, with no hidden or duplicate focus stop | Focus moved through Try sample, reference controls, imported checkbox, Choose images, a second visually clipped file input, Verify, and Start over. The clipped input is a non-visible duplicate focus stop | FAIL |
| Visible focus | Every keyboard-focusable control has a perceivable indicator | Visible controls showed a 2.4 pixel solid blue outline. When `#field-panels` received focus, it remained clipped to a 1 pixel-wide absolute box and no perceivable focus indicator appeared in the page | FAIL |
| Keyboard sample journey | Sample, Verify, evidence, reset dialog, Cancel, and Confirm operate from the keyboard | Tab plus Enter loaded the sample. Enter on Verify produced the result and moved focus to its heading. Enter activated evidence. Start over focused Cancel; Enter canceled. Reopening and Tab reached Confirm and Enter cleared the session | PASS |
| Keyboard validation | Invalid submission reports errors and moves focus | Enter on an empty Verify produced six alert messages. After the scheduled focus update, focus moved to `#field-brandName`, which had `aria-invalid=true`, `aria-describedby=error-brandName`, and a visible outline | PASS |
| Non-color state | Status remains understandable without color | Difference used `!`, the text `Difference`, the compared values, and a reason. Review used `?`, the text `Review`, values, and a capitalization reason. Match used `OK` and `Match`. Not applicable used text and a reason. Color was supplementary | PASS |
| Result evidence and judgment | Evidence focus and final human authority remain clear | Evidence actions focused original label content. Result copy said the reviewer makes the final decision and confidence is not an approval score | PASS |
| 200 percent layout at 1024 by 768 | Core result remains readable and operable without horizontal scrolling | The browser connection did not expose native browser zoom. A temporary 2.0 document content scale was applied at a 1024 by 768 viewport as the closest practical visual inspection. Summary text wrapped, viewer controls wrapped to two lines, focus remained visible on controls, and document scroll width equaled client width at 1009 pixels, with no horizontal overflow | PARTIAL |
| Reduced motion | Motion is removed when the user requests it | With `prefers-reduced-motion: reduce` active, the processing spinner reported `animation-name: none` and `animation-duration: 0s`; processing status text remained present | PASS |
| Forced colors | Content and focus remain perceivable in forced-color mode | Chrome matched `forced-colors: active`; cards, text, controls, image, and summary remained visible. The focused Enhanced display control used a solid system-colored outline and border | PASS |
| Chrome behavior | Required core behavior works in Chrome | Both timed UAT journeys, keyboard sample flow, validation focus, evidence focus, status communication, reduced motion, forced colors, and responsive inspection ran against Chrome 151. The hidden upload focus defect remains | FAIL |
| Edge behavior | Current governed Edge journey succeeds | The repository Playwright Edge project ran the same current local application and passed its sample, axe, result, evidence, reversible view, no-persistence, and guarded reset test in 5.1 seconds; total run was 6.2 seconds. A manual Edge browser connection was unavailable in this reviewer environment | PARTIAL |
| NVDA | Manual NVDA smoke | Excluded by package instruction and assigned separately to root | NOT_RUN |

## 3. Focus sequence evidence

The observed initial keyboard sequence was:

1. `Try the built-in sample`, visible button, 336 by 46 pixels
2. `#field-caseLabel`, visible input, 427 by 44 pixels
3. `#field-brandName`, visible input, 427 by 44 pixels
4. `#field-classType`, visible input, 427 by 44 pixels
5. `#field-abvPercent`, visible input, 427 by 44 pixels
6. `#field-proof`, visible input, 427 by 44 pixels
7. `#field-netContentsValue`, visible input, 329 by 45 pixels
8. `#field-netContentsUnit`, visible select, 90 by 45 pixels
9. `#field-producerNameAddress`, visible textarea, 874 by 86 pixels
10. `#field-isImported`, visible checkbox, 22 by 22 pixels
11. `#choose-panels`, visible button, 155 by 46 pixels
12. `#field-panels`, clipped file input, 1 by 44 pixels
13. `Verify label`, visible button, 128 by 46 pixels
14. `Start over`, visible button, 116 by 46 pixels

All listed controls computed a focus outline. The outline on step 12 was not perceivable because the element was absolutely positioned and clipped with `rect(0px, 0px, 0px, 0px)` at 1 pixel width.

## 4. Defect

### A11Y-R1-D001 - HIGH - Hidden file input creates a non-visible duplicate keyboard focus stop

Requirement affected: `FR-030`, visible focus and complete keyboard operation.

Reproduction:

1. Open a clean intake page in Chrome.
2. Use Tab to move through the reference controls and imported checkbox.
3. Tab to the visible `Choose images` button and observe its focus outline.
4. Press Tab once.
5. Observe that focus moves to `#field-panels`, but no usable focus indicator is visible.
6. Press Tab again and observe that focus moves to `Verify label`.

Expected:

- Every keyboard focus stop is visibly perceivable and corresponds to an operable control.
- If the visible Choose images button is the keyboard upload control, its hidden backing input does not create a second tab stop.

Observed:

- The backing file input has accessible name `Label panel images` and remains in sequential focus order.
- At focus it has `position: absolute`, `clip: rect(0px, 0px, 0px, 0px)`, a 1 by 44 pixel rectangle, and a computed outline that is not visibly perceivable.
- The preceding visible Choose images button already provides the upload action, making this an unexpected duplicate focus stop.

Impact:

- Keyboard and low-vision users temporarily lose visible focus and may believe focus was dropped or the interface stopped responding.
- The defect violates the approved visible-focus contract and blocks a T-030 manual PASS even though the next Tab returns to a visible control.

Recommended closure:

1. Keep one clearly visible keyboard upload control.
2. Remove the clipped backing input from sequential focus order when the visible button owns activation, or render a native file input with a visible focus treatment.
3. Re-run the full focus sequence, keyboard upload action, 200 percent browser zoom, forced colors, Chrome, Edge, and NVDA checks on the corrected snapshot.

## 5. Environment limitations and interpretation

- The Chrome extension file-path permission prevented its high-level upload harness from assigning local files. This did not create A11Y-R1-D001; the focus defect was observed on the untouched first-load DOM before any upload workaround.
- Native 200 percent browser zoom could not be changed through the browser-control connection. The reviewer applied and then removed a temporary 2.0 document content scale for visual layout stress at the required 1024 by 768 viewport. This is useful reviewer evidence but is not represented as exact native browser-zoom proof.
- A live manual Edge connection was unavailable. The current configured Edge Playwright test passed, but it does not replace a manual Edge visual observation if the governing checklist requires one.
- NVDA is deliberately excluded from this record.

## 6. Reviewer verdict

Manual accessibility reviewer 1 verdict: FAIL

The core keyboard journey, validation focus, non-color communication, reduced motion, forced colors, and practical high-zoom layout were otherwise usable. A11Y-R1-D001 prevents CLEAR because the required visible-focus contract fails at the hidden upload input. Exact native browser zoom, manual Edge visual inspection, and NVDA also remain to be completed by an environment that exposes those controls.

## 7. Remediation retest - 2026-09-01

Retest reviewer: LV-UAT-R1  
Retest environment: Windows NT 10.0.26200.0, Chrome 151.0.7922.175  
Defect under retest: `A11Y-R1-D001`  
Defect remediation verdict: PASS

### 7.1 Patched snapshot evidence

- `frontend/src/features/intake/IntakeForm.tsx` SHA-256: `8A6AE6ABD6A987D93C2CCE7A5E0340A673E44F36C68295E5C39EA41C8CBF58FD`
- `frontend/tests/app.test.tsx` SHA-256: `AB0CE62B7BAEBB30821C64A7B90A6C5519F9B0D8D0504DFF450264C1BFC7DC3C`
- Served production asset `frontend/dist/assets/index-B5BnStTm.js` SHA-256: `E3C0C061D7343A6DDC6270480CDD1EF8FA5A5B6C25FA5E367D119E780D2E3F9D`
- Source inspection found `tabIndex={-1}` on `#field-panels` at `frontend/src/features/intake/IntakeForm.tsx:225`.
- The regression assertion requires `Label panel images` to have `tabindex=-1` at `frontend/tests/app.test.tsx:38`.
- Focused component run: `npm run test -- tests/app.test.tsx` returned 1 of 1 file and 8 of 8 tests PASS in 4.61 seconds.

This is a post-manifest remediation snapshot. The earlier sealed release-manifest hash is not represented as covering these patched file hashes.

### 7.2 Live Chrome keyboard retest

The patched local application was started and loaded from `http://127.0.0.1:8000`. The served file input reported:

- `id`: `field-panels`
- `type`: `file`
- `aria-label`: `Label panel images`
- `tabindex`: `-1`

The complete initial sequential focus order was re-run. After `#field-isImported`, focus moved to the visible `#choose-panels` button. The next Tab moved directly to the visible `Verify label` button, then to `Start over`. `#field-panels` did not enter sequential focus order.

Expected: one visible keyboard upload control and no clipped duplicate focus stop.  
Observed: the visible Choose images button remained in order, the backing input was skipped, and every remaining focus stop was visible.  
Result: PASS.

`A11Y-R1-D001` is closed for this patched snapshot.

### 7.3 Edge supporting evidence

The current configured Edge Playwright project was run against the patched local application. Its sample, axe, result, evidence, reversible view, no-persistence, and guarded reset journey passed:

- Test: `frontend/e2e/labelverify.spec.ts:12`
- Browser project: Edge
- Result: 1 of 1 PASS
- Test duration: 6.1 seconds
- Total run duration: 7.2 seconds

A live manual Edge browser connection was not available in this reviewer environment, so this automated Edge result is not represented as a manual Edge visual inspection.

### 7.4 Exact native 200 percent zoom and NVDA boundaries

Exact native browser zoom was not locally runnable through the permitted Chrome browser connection. The connection did not expose a native zoom control, and Chrome policy blocked its settings surface. No workaround or browser-setting change was used. The earlier temporary 2.0 content-scale observation remains practical layout evidence only and is not relabeled as native browser-zoom proof.

NVDA was not run and no NVDA result is claimed.

### 7.5 Retest conclusion

- `A11Y-R1-D001` remediation: PASS
- Patched Chrome focus sequence: PASS
- Component regression assertion: PASS
- Current Edge automated smoke: PASS
- Manual Edge visual inspection: NOT_RUN because no live Edge browser connection was available
- Exact native 200 percent browser zoom: NOT_RUN because the permitted browser surface did not expose it
- NVDA: NOT_RUN by package instruction

The source-valid defect found by reviewer 1 is remediated. This append-only retest does not claim overall T-030 completion for the remaining environment-dependent manual checks.
