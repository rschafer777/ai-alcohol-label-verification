# Independent UAT Reviewer 1 Evidence

Document control ID: LV-UAT-R1-001  
Revision: 1.0  
Date: 2026-09-01  
Reviewer pseudonym: LV-UAT-R1  
Reviewer role: Independent non-implementer evaluator and RT3 reviewer  
Facilitator help: None  
Critical application errors: None  
Verdict: PASS

## 1. Candidate and environment

- Local application: `http://127.0.0.1:8000`
- Release manifest: `docs/10-release/RELEASE_MANIFEST.sha256`
- Manifest SHA-256 observed before review: `078C78FC1625DA32381F5CF954B057AB6BA0B74100FD90AC73510B3EF79A1CA3`
- Operating system: Microsoft Windows NT 10.0.26200.0
- Primary browser: Google Chrome 151.0.7922.175
- Browser user agent: Chrome 151 on Windows 10, 64 bit
- Default visible viewport: 1443 by 1559 CSS pixels
- Display: 3072 by 1728 pixels
- Locale: en-US
- Time zone: America/Chicago, UTC-05:00
- Input data: repository-governed synthetic Old Tom Distillery reference and two synthetic sample panels

The reviewer did not implement the frontend. No source, existing documentation, oracle, time budget, or application configuration was changed during these journeys.

## 2. UAT-001 first-time Try sample

Threshold: complete from first load through evidence focus in at most 3 minutes, without help or a critical error.

- Start: `2026-09-01T08:54:10.435Z` (`2026-09-01T03:54:10.435-05:00`)
- End: `2026-09-01T08:54:56.570Z` (`2026-09-01T03:54:56.570-05:00`)
- Elapsed: 46.135 seconds
- Threshold margin: 133.865 seconds
- Result: PASS

| Step | Expected | Observed | Result |
|---|---|---|---|
| First load | Purpose, prototype limitations, primary action, reference fields, and panel step are understandable without outside instructions | The first page identified an unofficial evidence assistant, instructed use of synthetic or sanitized data, stated no legal decision or saved session, and presented `Try the built-in sample` next to the two-step manual form | PASS |
| Load sample | Complete synthetic values and panels appear | The button loaded the reference values and two named panel previews; the page announced `Sample loaded. Review it or choose Verify label.` | PASS |
| Verify | Processing is obvious and reaches a complete result | The UI showed elapsed processing and returned `No differences found in checked fields`; server work was 3.3 seconds | PASS |
| Result completeness | Complete selected-check result is visible and focus is managed | The result summary received focus and 19 check articles rendered | PASS |
| Inspect evidence | Reviewer can focus source evidence and understand its authority | `Show on label` for Brand name focused `OLD TOM DISTILLERY` on the original panel and stated that confidence is an extraction signal, not an approval score | PASS |
| Human judgment | Product does not imply legal approval | The result stated `You make the final decision` and kept machine findings separate from reviewer notes and disposition | PASS |

Reviewer observation: the sample path was obvious, concise, and comfortably within the time threshold. No facilitator help, hesitation-producing navigation, or application-critical error occurred.

## 3. UAT-002 first-time manual exact record

Threshold: manually enter the reference, add panels, induce and correct one input error, verify, inspect evidence, and Start over in at most 7 minutes, without help or a critical error.

- Start: `2026-09-01T08:55:12.490Z` (`2026-09-01T03:55:12.490-05:00`)
- End: `2026-09-01T08:58:18.306Z` (`2026-09-01T03:58:18.306-05:00`)
- Elapsed: 185.816 seconds
- Threshold margin: 234.184 seconds
- Result: PASS

| Step | Expected | Observed | Result |
|---|---|---|---|
| Enter reference | Labeled controls accept the complete record | Entered the synthetic case label, brand, class or type, ABV, proof, net contents, unit, and producer name and address without outside instructions | PASS |
| Add panels | One to six supported files can be attached and reviewed before submission | Two governed PNG panels were attached; the UI displayed `2 of 6 added`, two previews, filenames, sizes, order controls, and Remove controls | PASS |
| Induce error | Invalid input is rejected before verification with an actionable message | Entered ABV 101 and activated Verify. The UI displayed `Alcohol by volume must be 100 or less.` and moved focus to the ABV control | PASS |
| Correct error | Valid work and selected panels remain available | Corrected ABV to 45. All other reference values and both panel previews remained present | PASS |
| Verify corrected record | Complete result replaces the intake state | The corrected record returned `No differences found in checked fields`, focused the summary, and rendered 19 check articles; server work was 2.2 seconds | PASS |
| Inspect evidence | A material result can focus its exact evidence | `Show on label` for Warning wording focused the full warning snippet on the original panel and retained the extraction-signal limitation | PASS |
| Start over | Destructive reset is confirmed and clears the session | The dialog explained that form, images, result, evidence selection, and notes would be cleared. `Confirm and clear` returned to the intake heading with an empty Brand name and `0 of 6 added` | PASS |

### Upload harness note

The Chrome browser extension opened the file chooser, but its local-file permission blocked the automation harness from assigning repository paths. This was a browser-control environment limitation, not an application response. The reviewer completed the authorized upload step by attaching the same two governed synthetic sample panel byte streams to the real file input through the tab-scoped Chrome developer channel and dispatching its normal change event. The application then rendered the genuine file previews, names, sizes, ordering controls, and submitted the two `File` objects through the production UI and API path. The page was reset at journey completion, so no injected browser state remained.

This method validates the application upload boundary and manual workflow, but does not independently validate the operating system native file-picker dialog.

## 4. Defects and limitations

- UAT application defects: None.
- Critical errors: None.
- Facilitator interventions: None.
- Environment limitation: Native file-picker path assignment was blocked by the Chrome extension permission described above. It did not prevent completion inside the 7 minute threshold.
- Accessibility observations and defects are recorded separately in `docs/09-qa-qc-uat/evidence/MANUAL_ACCESSIBILITY_REVIEWER_1.md`.

## 5. Reviewer verdict

- `UAT-001`: PASS
- `UAT-002`: PASS
- Reviewer 1 FR-037 journey verdict: PASS

Both required first-time journeys completed within their exact time limits, without facilitator help or a critical application error. This record represents one independent non-implementer only. FR-037 still requires a second independent reviewer record.
