# Internal UAT Rehearsal and Requester UAT Package

Document control ID: LV-UAT-001  
Revision: 1.2  
Date: 2026-09-01  
Status: Timed internal UAT PASS; accessibility blockers and requester UAT pending

## 1. Purpose

Internal UAT rehearses the evaluator and compliance-agent journeys before asking the requester to test. It is not a substitute for requester acceptance. Two independent non-UI implementers completed both no-help timed journeys within the governed limits. The hidden-input keyboard defect was corrected and independently retested. Native 200 percent zoom with live manual Edge and the NVDA journey remain BLOCKED by the current environment, so the overall accessibility and release composite remains INCOMPLETE.

## 2. Rehearsed journeys

| Journey | Expected result | Result |
|---|---|---|
| Load governed sample | Reference and two label panels populate with plain privacy and prototype disclosures | PASS |
| Start verification | Processing state is obvious and completes without external service dependency | PASS |
| Review clean result | All 19 rows appear; 18 applicable rows Match; country is correctly Not verified for domestic product | PASS |
| Inspect evidence | Evidence control focuses the original image at the correct region; zoom, rotate, and reset remain reversible | PASS |
| Record human decision | Notes and disposition remain local to the current page session | PASS |
| Start over | Guarded reset clears reference, files, result, note, disposition, and object URLs | PASS |
| Refresh and reopen | User content is absent from browser storage, caches, and restored state | PASS |
| Keyboard path | Controls have accessible names and the full core journey is keyboard usable | PASS after independent `A11Y-001` regression |
| Native 200 percent zoom and live manual Edge | Core journey remains usable at the governed viewport and native zoom | BLOCKED pending `ENV-A11Y-001` closure |
| Screen-reader path | NVDA announces the full core journey and state changes | BLOCKED pending `ENV-NVDA-001` closure |
| Chrome and Edge | Same core outcome in both supported evaluator browsers | PASS |
| Error recovery | Typed error copy preserves safe retry inputs and never fabricates a clean result | PASS |

Automated browser evidence: three journeys passed, covering Chrome core, Chrome full privacy, and Edge core behavior, with zero serious or critical axe violations. The intentional duplicate Edge privacy run was skipped. Automated evidence does not replace the blocked native zoom/manual Edge and NVDA records.

## 3. Independent timed results

| Reviewer | Try sample limit/result | Manual journey limit/result | Help or critical error | Decision |
|---|---|---|---|---|
| Reviewer 1 | 3 minutes / 46.135 seconds | 7 minutes / 185.816 seconds | None | PASS |
| Reviewer 2 | 3 minutes / 29.561 seconds | 7 minutes / 139.780 seconds | None | PASS |

## 4. Requester UAT checklist

The requester should complete these checks after internal RT clearance:

1. Follow the README setup path from a clean local environment or the approved repository clone.
2. Load the sample and verify that the workflow is obvious without reading design documentation first.
3. Upload at least one requester-selected label and enter the corresponding application values.
4. Confirm every result row communicates what was compared, what was observed, the state, and the supporting evidence or limitation.
5. Exercise zoom, rotate, reset, retry, notes, disposition, and Start over.
6. Confirm wording does not imply legal approval, TTB affiliation, COLAs Online integration, server persistence, or a durable server-side batch queue.
7. Review code organization, comments, tests, numbered documentation, limitations, and deployment instructions.
8. Record ACCEPTED or RETURN_TO_DEVELOPMENT with defect IDs and evidence.

## 5. Acceptance record

| Role | Name | Decision | Date | Notes |
|---|---|---|---|---|
| Requester | Pending | PENDING | Pending | Internal clearance must finish first |

No requester signature or acceptance is inferred from automated evidence.
