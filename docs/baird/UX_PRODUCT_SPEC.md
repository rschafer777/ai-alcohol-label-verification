# BAIRD UX and Product Specification

**Design basis:** Attested Intake plus explicit Grok/Gemini dispositions  
**Primary envelope:** Desktop Chrome and Edge, 1024 by 768 through 1920 by 1080, 200 percent zoom

## 1. Experience principle

The tool should feel like a focused review instrument. It should not feel like a chatbot, a generic dashboard, a government system replica, or an AI demonstration. The user's attention belongs on the label and the exceptions.

## 2. Information architecture

### Surface A: Start and input

Top area:

- LabelVerify name;
- Unofficial prototype tag;
- one-sentence purpose;
- synthetic-data-only and no-sensitive-upload notice.

Primary actions:

1. **Try sample** loads the default complete synthetic case and immediately starts verification in one activation. Focus moves to the processing heading, then to the result heading when complete.
2. **Check another label** reveals the structured form and panel upload.

Manual input groups:

- Application values;
- Label panel images;
- concise supported-file/limit help;
- one **Verify label** action.

The batch entry is absent unless the gated feature is implemented and validated.

### Surface B: Processing

Keep the uploaded image visible. Do not add a scanning animation over it.

Show:

- current step: Validating, Reading label panels, Comparing fields, Preparing results;
- elapsed time;
- panel progress, such as 2 of 3;
- Cancel;
- accessible live-region status that does not announce every animation frame.

The five-second p95 target is not satisfied by hiding or replacing a result. If the independent hard safety deadline is reached, stop the worker and show an actionable non-clean timeout. A failure never counts as successful performance.

### Surface C: Review workspace

Desktop split:

- left: panel selector, original image, zoom, rotate, optional processed view, evidence highlight;
- right: summary, quality/coverage, field table, warning detail entry, limitations, start-over.

Header:

- neutral case label, not an employee or official review ID;
- summary chip with icon and text;
- elapsed duration;
- profile label `Selected distilled-spirits checks`.

### Surface D: Warning detail

Show independently:

- prescribed wording;
- extracted wording and diff;
- heading uppercase;
- heading emphasis state;
- remainder emphasis state;
- separation state;
- continuity state;
- contrast and legibility state;
- physical-size limitation labeled as not automatically assessed.

Every active row follows `WARNING_CAPABILITY_MATRIX.md` and aggregates. Insufficient applicable evidence is Review or Not verified, never an implied Match.

Actions return to all fields. No compliance override or automatic return-to-applicant action exists.

## 3. Field row anatomy

Each row contains:

- field/check name;
- reference value or canonical rule;
- extracted candidate or Not found;
- state word and icon;
- short reason;
- evidence action;
- capability/limitation when relevant.

The default table stays expanded. Exact extracted text is visible. Confidence, if shown at all, is labeled `OCR signal` with provenance and never presented as correctness probability.

When more than one distinct plausible candidate exists, the row is Review and lists every alternative from the typed `alternatives[]` contract. Each item pairs its displayed value with its own evidence reference and accessible `Show <value> on label` action. Activating an action opens the identified panel and highlights that item's polygon. The UI must not display only the first candidate or conceal conflicting country-of-origin text.

## 4. Status language

| Internal state | User label | Example reason | Next action |
|---|---|---|---|
| Match | Match | Exact text found on back panel | Inspect evidence if desired |
| Review | Review | Same letters with different capitalization | Confirm intended equivalence |
| Mismatch | Difference | Label shows 40 percent; application shows 45 percent | Inspect source and correct record/label |
| Not verified | Not verified | Required panel or readable text was not available | Add a clearer panel image |
| Input quality | Image needs attention | Glare covers the alcohol statement | Replace or add an image |

Submission summaries use only:

- No differences found in checked fields;
- Review needed;
- Differences detected.

## 5. Form contract

### Required reference values

- Brand name;
- Class/type;
- Alcohol by volume percentage;
- Net contents quantity and unit;
- Producer/bottler name and address;
- Imported: Yes/No;
- Country of origin when Imported is Yes.

### Optional values

- Proof;
- evaluator-only case label;
- optional panel type label for each image: Front, Back, Side, Neck, Other.

The government warning is not manually pasted as application data. Its canonical rule comes from the versioned regulatory registry.

### Validation

- validate required and conditional fields before upload;
- preserve user entries after recoverable errors;
- focus the error summary and link each error to its field;
- do not autocorrect a legal/label value silently;
- accept common ABV and net-content entry formats, then show the canonical parsed value before verification.

## 6. Evidence interactions

- Selecting `Show on label` switches to the correct panel and outlines the OCR region.
- The outline is paired with a labeled crop so color is not the only cue.
- If the region is unavailable, the action is absent and the row says why.
- Original is the default. Processed view is explicitly labeled and never replaces original evidence.
- Rotation/zoom are reversible view controls and do not alter findings.
- Keyboard users can move between field rows and evidence without a trap.

## 7. Error and degraded states

| Scenario | User message structure |
|---|---|
| Unsupported file | Name accepted formats and retain other valid panels |
| Too large/pixel-heavy | State the exact limit and which image failed |
| Corrupt/spoofed image | Say the image could not be safely read, not that the label is wrong |
| Unreadable text | Identify panel/region, explain quality issue, request another image |
| Missing panel/evidence | State which selected check lacks evidence; do not call it missing from the legal label |
| OCR service/model error | State that verification could not finish; offer retry; no clean result |
| Overload/rate limit | State when to retry without blaming the label |
| Timeout | State that no complete result was produced; offer retry or smaller/clearer inputs |
| Network disconnect | Preserve local form/image selections when browser security permits and offer retry |

## 8. Accessibility interaction contract

- one `h1` and logical headings;
- native labels, buttons, table/list semantics, and file inputs;
- error summary receives focus after failed submit;
- processing uses `role=status` or an appropriate polite live region;
- result summary receives programmatic focus on completion;
- evidence outlines have equivalent text/crop descriptions;
- no focus movement on a field-row hover;
- all actions operate with keyboard alone;
- focus remains visible against every background;
- no content or action is available only on hover;
- status includes text and icon;
- touch/click targets are comfortably sized;
- 200 percent zoom reflows the two columns into stacked content without loss;
- animations honor reduced-motion preference.

## 9. Visual direction

- neutral deep navy for structure, warm amber for attention, green only for Match, red only for Difference, gray/blue for Not verified;
- off-white background and high-contrast body text;
- no official seal, agency wordmark, named employee, or federal-system imitation;
- restrained borders and spacing rather than dense enterprise chrome;
- no decorative AI beams, floating token text, or unnecessary loading spectacle;
- plain system fonts or a locally served open font only if it does not delay load.

## 10. Evaluator demo script

The README and in-product experience should make this five-minute path obvious:

1. Open the deployed URL.
2. Read the unofficial/synthetic-only notice.
3. Select Try sample.
4. Observe a complete result near the five-second target.
5. Open evidence for brand, ABV, net contents, and warning.
6. Inspect one Review or Difference case from a sample selector.
7. Start over and upload a supplied fixture manually.
8. Observe an invalid or poor-image recovery path.

Sample options may include Clean comparison, Heading capitalization difference, Warning wording difference, and Poor image review. Each maps to the same independent fixture manifest used by automated validation.

## 11. Batch UX gate

If delivered:

- batch is a separate secondary entry;
- accept a documented manifest and files without requiring a production COLA export;
- show processed/total, elapsed time, state counts, active/cancelled state, and row errors;
- default completed view to Review needed and Differences detected;
- one bad row never erases completed rows;
- open-next-review action is keyboard reachable;
- export contains system states/evidence references and any separate session disposition;
- do not mix unsupported beverage categories in examples.

## 12. UX non-goals

- no account/profile/settings shell;
- no global search;
- no notifications center;
- no official queue count in the core;
- no mobile-specific redesign;
- no legal approval action;
- no hidden confidence-driven auto-decision;
- no requirement to understand AI/OCR terminology.
