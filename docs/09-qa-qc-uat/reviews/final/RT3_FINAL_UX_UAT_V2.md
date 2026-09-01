# RT3 Final UX and UAT Review V2

Document control ID: LV-RT3-FINAL-V2  
Review date: 2026-09-01  
Reviewer role: Independent UX, accessibility, and UAT reviewer  
Verdict: **REWORK_REQUIRED**

## 1. Reviewed snapshot

This review is against `docs/10-release/RELEASE_MANIFEST.sha256` with SHA-256:

`9EBD7ABEF664A24680987C070EDEA5A5C2EF4861BE79344246516B890BDF16A3`

The manifest contains 528 parsed entries. Offline verification found 528 present files, zero missing files, and zero hash mismatches. Manifest-listed content was treated as immutable and was not changed. This review file is a post-seal review artifact and is not represented as one of the 528 sealed entries.

## 2. Verdict basis

The implemented workflow is locally usable, the two required first-time journeys have two independent timed records, the corrected keyboard focus path is supported by manual and automated evidence, and the package accurately leaves native 200 percent zoom with manual Edge, NVDA, and requester acceptance incomplete. No open actionable application UX defect was found in this review.

The verdict is nevertheless `REWORK_REQUIRED` because the sealed evaluator-facing README reports two stale exact performance figures that conflict with the sealed canonical validation evidence. Both measured results still pass their thresholds, but a release package cannot present two different exact results for the same final evidence run. This is a documentation and release-honesty defect, not a product performance failure.

## 3. Stakeholder and design alignment

The candidate implements the core needs reflected in the stakeholder record and the approved UX workflow:

- A low-friction `Try the built-in sample` route and a two-step manual route support evaluators with varying technical comfort.
- The result always presents the complete 19-check review surface instead of silently omitting checks.
- Match, Difference, Review, and Not verified use text and symbols as well as color.
- Original-image evidence, focused snippets, zoom, rotate, and reset make the machine result inspectable.
- Copy consistently describes LabelVerify as an unofficial evidence assistant, says confidence is an extraction signal rather than an approval score, and leaves the final decision to the human reviewer.
- Session-only notes and disposition do not change machine findings and are not represented as durable records.
- The UI and README clearly exclude completed batch processing, accounts, saved cases, and legal approval.

The Grok and Gemini materials are used as design-reference analysis rather than authority. The implemented dispositions adopt the useful review patterns, including an obvious sample, side-by-side evidence, explicit states, reversible image controls, and human judgment. They reject misleading official branding, legal pass or return language, confidence as authority, and decorative scan theater. Batch remains a documented later option rather than a falsely completed feature.

## 4. First-time usability and independent UAT

The sealed package contains two independent, pseudonymous, non-implementer records. Each record includes start and end timestamps, environment, no-help status, critical-error status, expected and observed steps, and an explicit verdict.

| Reviewer record | Role | Try sample | Manual entry, upload, error correction, verification, evidence, and Start over | Help | Critical errors | Verdict |
|---|---|---:|---:|---|---|---|
| `UAT_REVIEWER_1.md` | Independent non-implementer evaluator and RT3 reviewer | 46.135 seconds, under 3 minutes | 185.816 seconds, under 7 minutes | None | None | PASS |
| `UAT_REVIEWER_2.md` | Independent non-implementer requirements and evidence reviewer | 29.561 seconds, under 3 minutes | 139.780 seconds, under 7 minutes | None | None | PASS |

Both manual journeys entered the complete reference, attached two governed panels, induced ABV 101, observed the actionable maximum-value error and focus movement, corrected ABV to 45 without losing work, verified all 19 rows, inspected focused source evidence, and confirmed Start over. The sample journeys loaded the governed sample, completed verification, focused the result summary, and inspected brand evidence. This satisfies the local two-reviewer FR-037 evidence requirement.

Both reviewers used the permitted tab-scoped browser developer channel to supply the governed panel bytes because the browser-control extension could not assign local paths through the operating-system file chooser. The production file input, previews, ordering controls, form submission, API path, and reset behavior were exercised. The records correctly state that this does not independently validate the native file-picker dialog.

Reviewer 1 names an earlier seal because that journey preceded the narrow hidden-input focus remediation. The same record contains the append-only remediation retest, and Reviewer 2 ran after that remediation. The final 528-entry manifest seals both UAT records, the retest, the patched source, and its regression test. This provenance is sufficient for local FR-037, but future final-seal records should identify the final manifest directly instead of an earlier hash or `PENDING_FINAL_RELEASE_MANIFEST`.

## 5. Accessibility and browser evidence

No overall accessibility PASS is claimed by the sealed package. The evidence distinguishes corrected behavior from controls that could not be executed in the available environment.

| Area | Sealed evidence | Review conclusion |
|---|---|---|
| Hidden upload focus stop | `MANUAL_ACCESSIBILITY_REVIEWER_1.md` records the original failure, `tabIndex=-1` remediation, full Chrome focus-order retest, and 8 of 8 focused component tests passing | Remediated PASS; defect closed |
| Keyboard core and validation | Both UAT records plus the remediation retest show keyboard operation, validation focus, evidence focus, and guarded reset | PASS for tested paths |
| Non-color state and visible focus | Manual review confirms text or symbol state labels and visible focus on remaining sequential controls | PASS for tested paths |
| Reduced motion and forced colors | Manual inspection records spinner removal under reduced motion and perceivable content and focus in forced colors | PASS for tested paths |
| Automated accessibility | Chrome core and Edge core journeys passed with zero serious or critical axe violations | PASS for automated scope only |
| Exact native 200 percent zoom at 1024 by 768 | The permitted browser surface did not expose native zoom; a temporary content-scale observation is explicitly labeled only as practical evidence | BLOCKED by `ENV-A11Y-001`; not claimed PASS |
| Live manual Edge visual inspection | Edge automated core passed, but a live manual Edge connection was unavailable | BLOCKED by `ENV-A11Y-001`; not claimed PASS |
| NVDA | NVDA was not installed or executed in this review environment | BLOCKED by `ENV-NVDA-001`; not claimed PASS |

`UAT_RESULTS.md`, `VALIDATION_PROTOCOL_RESULTS.md`, the assertion ledger, and `RELEASE_CANDIDATE_STATUS.md` all describe the accessibility and release composite as `INCOMPLETE`. The historic `FAIL` at the top of the append-only manual accessibility record is preserved, while the later section closes only the specific hidden-input defect and explicitly refuses to claim overall T-030 completion. This is honest and traceable rather than a false accessibility PASS.

The current local browser evidence also records Chrome core PASS, Chrome privacy PASS, Edge core PASS, and the duplicate Edge privacy journey intentionally skipped. The skip is not presented as manual Edge or native zoom proof.

## 6. Error handling, human boundaries, and privacy

The application provides typed, actionable errors, focuses invalid input, preserves safe retry inputs, exposes elapsed processing and cancellation, and does not turn an inference error into a clean result. Automated tests cover cancellation without loss of work and retry without re-entry.

The result surface keeps human judgment explicit. Reviewer notes and disposition are session-only and never overwrite check results. Evidence actions focus the original label, display enhancement is identified as display-only, and OCR confidence is not presented as regulatory approval.

The privacy matrix covers first load, success, Start over, refresh, close and reopen, error, and cancel. It records no content in local storage, session storage, IndexedDB, Cache Storage, service workers, or history state, and it verifies no-store API behavior. The UI and README consistently instruct use of synthetic or sanitized data and do not claim durable case storage. This is strong local evidence, while deployed-edge egress and infrastructure controls remain outside the authorized local proof.

## 7. Actionable release-honesty defect

### RT3V2-F001 - README exact performance figures conflict with sealed canonical evidence

Severity: Medium for evaluator readiness  
Type: Documentation and release-evidence consistency  
Status: Open

`README.md` states that warm p95 was 1.98 seconds across 30 runs and cold readiness was 9.54 seconds across 5 runs. The final sealed evidence records different exact values:

| Metric | README claim | Canonical sealed result | Threshold result |
|---|---:|---:|---|
| Warm performance p95, 30 runs | 1.98 seconds | 2,151.062 ms, or 2.151062 seconds | PASS under 5,000 ms |
| Cold readiness plus first result p95 and maximum, 5 runs | 9.54 seconds | 9,812.494 ms, or 9.812494 seconds | PASS under the exclusive 10,000 ms threshold |

Evidence: `README.md:87`, `docs/08-validation/evidence/local-performance.json`, `docs/08-validation/ASSERTION_EVIDENCE_LEDGER.md:96`, and `docs/08-validation/VALIDATION_PROTOCOL_RESULTS.md:34-35`.

Impact: An evaluator following the README sees exact results that cannot be reconciled with the canonical final evidence. The discrepancy does not change either PASS decision, but it weakens release honesty and reproducibility in a take-home package whose README is the first-run entry point.

Required closure:

1. Update the README to the canonical current figures, or rerun and regenerate the performance evidence so every artifact reports one result set.
2. Re-run the documentation consistency checks.
3. Generate a new immutable release manifest and have final reviewers identify that same seal.

## 8. Honest blockers and requester gates

The following items are incomplete but are not actionable UX defects discovered by RT3 V2:

- Exact native 200 percent browser zoom at 1024 by 768 and live manual Edge inspection are `BLOCKED` by the current browser-control environment.
- NVDA is `BLOCKED` because it was not available or run. No NVDA result is claimed.
- Requester UAT is `PENDING_REQUESTER_GATE`. Internal UAT does not infer requester acceptance.
- Git publication, OCI proof, public deployment, deployed restricted-egress proof, and final regulatory recheck remain accurately identified as later external or requester-controlled gates.

These gates may remain pending in a local take-home candidate if their status remains explicit. They do not justify relabeling the composite as PASS, and the sealed package does not do so.

## 9. Advisory observations

- A clean evaluator setup note could state more directly that initial local OCR model acquisition is a setup-time network action, while runtime inference is local. Existing dependency and model documentation provides the detail, but the README is the evaluator's first contact.
- A future environment with native browser zoom, a live manual Edge session, and NVDA should execute the remaining T-030 checks without converting automated substitutes into manual evidence.
- A future UAT record should exercise the native operating-system file picker where the control environment permits it.

## 10. Final decision

**REWORK_REQUIRED**

The candidate is locally usable, human-centered, privacy-conscious, explicit about batch and legal limitations, and honest about its unresolved accessibility and requester gates. The single actionable blocker to RT3 clearance is `RT3V2-F001`, the mismatch between the README's exact performance claims and the final sealed evidence. Correct that inconsistency, reseal the package, and rerun final traceability review. The honestly blocked native zoom/manual Edge, NVDA, and requester-controlled gates should remain visibly incomplete until their required environments or owners are available.
