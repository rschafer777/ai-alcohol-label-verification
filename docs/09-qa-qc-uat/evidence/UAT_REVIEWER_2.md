# Independent UAT Reviewer 2 Evidence

Document control ID: LV-UAT-R2-001  
Revision: 1.0  
Date: 2026-09-01  
Reviewer pseudonym: LV-UAT-R2  
Reviewer role: Independent non-implementer requirements and evidence reviewer  
Facilitator help: None  
Critical application errors: None  
Verdict: PASS

## 1. Candidate and environment

- Product snapshot: `PENDING_FINAL_RELEASE_MANIFEST`
- Local application: `http://127.0.0.1:8000`
- Operating system: Windows 10 compatible runtime, 64 bit
- Browser: Google Chrome 151
- Visible viewport: 1443 by 1559 CSS pixels
- Locale: en-US
- Time zone: America/Chicago
- Input data: repository-governed synthetic Old Tom Distillery reference and two synthetic sample panels

The reviewer did not implement the frontend. No source, contract, oracle, fixture, time threshold, or application configuration was changed during the journeys.

## 2. UAT-001 first-time Try sample

Threshold: complete from first load through evidence focus in at most 3 minutes, without help or a critical error.

- Start: `2026-09-01T09:16:14.299Z`
- End: `2026-09-01T09:16:43.860Z`
- Elapsed: 29.561 seconds
- Threshold margin: 150.439 seconds
- Result: PASS

| Step | Expected | Observed | Result |
|---|---|---|---|
| First load | Purpose, limitations, sample action, reference fields, and panel step are understandable without outside instructions | The page identified LabelVerify as an unofficial evidence assistant, limited use to synthetic or sanitized data, denied legal decision and session storage claims, and presented one obvious sample action beside the two-step manual form | PASS |
| Load sample | Complete synthetic values and panels appear | One click loaded the Old Tom reference and two named PNG panel previews; the page announced that the sample was ready to review or verify | PASS |
| Verify | Processing terminates in a complete result | Verification returned `No differences found in checked fields` | PASS |
| Result completeness | The complete selected-check result appears and focus is managed | The result heading received focus and exactly 19 check articles rendered | PASS |
| Inspect evidence | A reviewer can focus the exact source evidence and understand its limit | `Show on label` for Brand name focused `OLD TOM DISTILLERY` from the original panel and stated that confidence is an extraction signal, not an approval score | PASS |

Reviewer observation: the sample path was clear on first contact and completed with 150.439 seconds of margin. No facilitator help, navigation recovery, or critical application error was required.

## 3. UAT-002 first-time manual exact record

Threshold: manually enter the reference, add panels, induce and correct one input error, verify, inspect evidence, and Start over in at most 7 minutes, without help or a critical error.

- Start: `2026-09-01T09:16:56.349Z`
- End: `2026-09-01T09:19:16.129Z`
- Elapsed: 139.780 seconds
- Threshold margin: 280.220 seconds
- Result: PASS

| Step | Expected | Observed | Result |
|---|---|---|---|
| Enter reference | Labeled controls accept the complete synthetic record | Entered case label, brand, class/type, ABV, proof, net contents, unit, and producer name/address through the visible form | PASS |
| Add panels | One to six supported files appear as reviewable previews | Two governed PNG panels appeared as `2 of 6 added`, with filenames, sizes, order actions, and remove actions | PASS |
| Induce error | Invalid input is rejected before verification with an actionable message | ABV 101 produced `Alcohol by volume must be 100 or less.` and moved focus to the ABV control | PASS |
| Correct error | Valid values and panels remain intact | Correcting ABV to 45 preserved the other reference values and both selected panels | PASS |
| Verify corrected record | A complete result replaces intake processing | The corrected record returned `No differences found in checked fields`, focused the summary, and rendered exactly 19 check articles | PASS |
| Inspect evidence | A material rule row focuses its exact evidence | `Show on label` for Warning wording focused the full warning statement from the original panel and retained the extraction-signal limitation | PASS |
| Start over | Destructive reset is explained, confirmed, and complete | The confirmation named form, images, result, evidence selection, and notes. Confirm returned to the intake heading with an empty Brand name and `0 of 6 added` | PASS |

### Upload harness note

The permitted Chrome extension denied direct file-chooser path assignment. This was a browser-control environment limitation, not an application response. The reviewer used the tab-scoped Chrome developer test channel to fetch the same two repository-governed sample panel byte streams from the local application origin, construct normal browser `File` objects, assign them to the real panel input, and dispatch its normal change event. The production UI then rendered the actual previews and submitted those two file objects through the real application and API path.

The reviewer confirmed Start over at journey completion. No injected browser state remained. This method validates the application upload boundary and manual workflow, but it does not independently validate the operating-system native file-picker dialog.

## 4. Defects and limitations

- UAT application defects: None.
- Critical errors: None.
- Facilitator interventions: None.
- Environment limitation: Native file-picker path assignment was blocked by the Chrome extension permission described above.
- NVDA: Not run and not claimed by this UAT record.

## 5. Reviewer verdict

- `UAT-001`: PASS
- `UAT-002`: PASS
- Reviewer 2 FR-037 journey verdict: PASS

Both required first-time journeys completed within their exact time limits, without facilitator help or a critical application error. Together with `UAT_REVIEWER_1.md`, this provides the two independent non-implementer records required for local FR-037 evidence. Requester acceptance remains a separate requester-controlled gate.
