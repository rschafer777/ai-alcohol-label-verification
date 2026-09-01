REWORK_REQUIRED

# BAIRD Red Team 2 Rereview 3

Review date: 2026-08-31

Role: Independent stakeholder UX, extraction feasibility, performance, and assignment-fit skeptic

## Reviewed sealed snapshot

- Manifest: `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V3.sha256`
- Expected and observed manifest SHA-256: `97707b49f130d37b1fc5303abb3f3fa87502efe23000f8f73089f79aa01277bc`
- Expected and observed entries: 119
- Missing files: 0
- Hash mismatches: 0

I verified the manifest hash and every listed file before substantive review. I performed a second complete seal verification immediately before finalizing this report. This report is outside the manifest. No snapshotted file was modified.

## Gate basis

The V3 correction closes the prior proof, warning-applicability, active-check denominator, result vocabulary, timeout recovery, field-oracle, model-integrity, and global-admission defects. Its product direction remains strong for the take-home assignment.

One material false-clean path remains in the exact-warning implementation used as the retained feasibility proof. The code deletes observed punctuation before exact comparison. An uppercase heading with an added period and a warning body with an added period at a line boundary can therefore be reported as Match. This directly conflicts with the selected warning policy, the junior agent's warning-exactness requirement, and the Intake no-false-clean contract. BAIRD should not hand that behavior to I2R as validated evidence.

## Evidence and review method

I reviewed the complete sealed set, including:

- the sanitized original assignment and requester instructions;
- the attested Intake, source map, scope, success definition, regulatory register, decision log, and Intake gate;
- all BAIRD product, UX, architecture, warning, security, performance, deployment, source-coverage, control-handoff, and I2R-handoff documents;
- all three initial BAIRD reviews, all prior rereviews, and `BAIRD_RT_REMEDIATION.md`;
- the 17-check registry, independent field oracle, 27 research cases, 54 direct runs, 54 browser runs, five cold runs, timeout evidence, security-control evidence, model BOM, fixture allocation, and retained research source;
- all per-source Grok and Gemini dispositions in `docs/intake/design-reference-analysis.md`.

I independently joined the registry, case oracle, and every direct result. The recomputation covered 918 field rows and found zero error in registry membership, applicability, state, reason code, required evidence, aggregate, or summary for the 54 retained direct runs. I also independently checked all 54 browser attempts: every attempt completed, every result and DOM contained 17 rows, every response was `no-store, private`, and the sums of field errors, missing required evidence, false clean, false mismatch, DOM mismatch, and status mismatch were all zero for the retained cases.

The measured warmed browser p95 was 3730.50 ms and the maximum was 4147.20 ms. The five true process-start cold trials had a conservative p95 of 10845.35 ms and remain honestly open for deployed proof. The forced hang returned a result-free 504 in 6325.75 ms, exposed a 503 readiness interval, replaced the child asynchronously, and recovered with one child and a complete 17-row result.

## Retest of prior findings

| Finding family | V3 result | Concrete evidence |
|---|---|---|
| `RT2-BAIRD-001`, load-bearing extraction and latency proof | PASS FOR BAIRD DIRECTION | The 27-case, 54-direct, and 54-browser sets exercise 1, 3, and 6 panels, the 12 MP boundary, degraded images, decoys, import origin, all 17 checks, full rendering, and user-visible timing. Cold and deployed claims remain explicit release stops rather than inferred passes. |
| `RT2-BAIRD-002`, reference-conditioned candidate selection | PASS | `ENGINEERING_BLUEPRINT.md` keeps OCR, candidates, and primary selection reference-blind. Expected values first enter at comparison. The decoy cases and retained source preserve that ordering. |
| `RT2-BAIRD-003`, warning capability and aggregation | REOPENED IN EXECUTION | The written matrix is complete and safe, but `research/baird-spike/spike.py:279-280` and `:574-578` delete observed punctuation and can manufacture a warning Match. See `RT2-BAIRD-RR3-001`. |
| `RT2-BAIRD-004`, fallback silently weakens core | PASS AS A GATE | Systematic field-family failure reopens BAIRD or requires requester-approved scope change. Case-level uncertainty routes to Review or Not verified. No cloud fallback or hidden field removal was introduced. |
| `RT2-BAIRD-005`, ambiguous Try sample behavior | PASS | `UX_PRODUCT_SPEC.md:21-24` defines one activation that loads the complete synthetic sample, starts verification, announces processing, and moves focus to the result heading. |
| `RT2-BAIRD-RR-001`, complete active warning and producer execution | PASS FOR THE RETAINED DENOMINATOR, REOPENED FOR EXACTNESS | All 17 rows execute and the producer and warning subchecks aggregate. The new punctuation-repair branch is outside the retained negative denominator and contradicts the exactness policy. |
| `RT2-BAIRD-RR-002`, cold measurement excluded construction | PASS BY HONEST DISPOSITION | The cold clock starts before imports and includes model construction, hash checks, warmup, and the first browser result. The missed local target is disclosed rather than relabeled. |
| `RT2-BAIRD-RR-003`, five-second cancellation | PASS | Five seconds is the warmed p95 objective. Separate hard bounds at child, app, browser, and proxy layers remain visible and do not convert failure into successful latency. |
| `RT2-BAIRD-RR2-001`, proof and warning applicability omitted | PASS | `selected-check-registry.json` includes both checks. Cases S15 through S20 cover proof difference, missing and ambiguity, plus below-threshold, threshold, and unparseable warning applicability. Every run emits all 17 rows. |
| `RT2-BAIRD-RR2-002`, missing-colon and altered-heading false clean | PARTLY PASS, NEW EDGE REOPENED | S21 and S22 correctly return Mismatch for a missing colon and altered heading. An added terminal period still becomes Match because the comparator strips it. See `RT2-BAIRD-RR3-001`. |
| Cross-review V2 findings on vocabulary, timeout, traceability, admission, independent oracle, model hashes, country evidence, and narrowed egress | PASS | Internal states and summaries are consistent, forced-hang recovery is retained, I2R names the two correct mapping authorities, the global pre-body gate is bounded, the oracle is separate, startup fails on wrong hashes, country has region evidence, and the egress claim is limited to the measured port property. |

## Scenario attacks

| Scenario | Expected product behavior | V3 result |
|---|---|---|
| First-time evaluator selects Try sample | One activation reaches a complete synthetic result without data preparation | PASS by the explicit start, processing, and focus contract |
| Low-tech reviewer checks a custom label | Plain grouped fields, 1 to 6 panel upload, one Verify action, actionable errors | PASS in `UX_PRODUCT_SPEC.md` and the API/input contract |
| Public evaluator judges prototype scope | Unofficial, synthetic-only, no-sensitive-data disclosure and no legal approval claim | PASS; the selected-profile label and neutral result language remain visible |
| Complete one-panel result | Every applicable selected check exposes reference, observed evidence, state, reason, and location or unavailability | PASS for the retained case and 17-row browser rendering |
| Three-panel and six-panel evidence | Panel order and count do not omit fields or evidence actions | PASS for S07 and S08 in direct and browser evidence |
| Reference value appears only as a decoy | Extraction cannot choose a candidate because it matches the reference | PASS for the retained decoy attacks and reference-blind boundary |
| Brand differs only by capitalization | Preserve human judgment instead of naive exact failure or silent Match | PASS; the result is Review needed |
| Proof differs, is absent, or is ambiguous | Difference or uncertainty must aggregate | PASS for S15, S16, and S17 |
| Warning is below, at, or uncertain around 0.5 percent ABV | Applicability is explicit and no unknown branch becomes clean | PASS for S18, S19, and S20 |
| Warning colon is missing or heading text is altered | Readable defect returns Mismatch | PASS for S21 and S22 |
| Warning body is bold or heading is not emphasized | Independent evidence returns Mismatch without one metric proving both checks | PASS for S23 and S24 |
| Warning heading contains an added period | Exact uppercase heading and colon check must return Mismatch | FAIL; `GOVERNMENT WARNING:.` is reduced to the canonical heading and returned as Match |
| Prescribed body contains an added period at an OCR row boundary | Readable punctuation mutation must return Mismatch | FAIL; the period is removed when the next row begins with lowercase text, allowing canonical equality |
| Glare or blur makes evidence unreliable | Review or Not verified, never a clean result | PASS for the retained degraded case and written quality gate |
| Valid warm request exceeds five seconds | Remain observable until the independent safety deadline and stay in the benchmark denominator | PASS in the selected contract; no retained warm attempt exceeded five seconds |
| OCR child hangs | No partial result, actionable timeout, readiness loss, asynchronous recovery | PASS in forced-hang evidence |
| Keyboard, zoom, and assistive technology use | Native controls, visible focus, polite status, focused result, text plus icon, 200 percent reflow | PASS as a testable I2R contract; implementation and deployed proof remain release gates |
| Peak batch concept pressures core scope | Batch stays absent until every single-submission gate passes | PASS; batch remains a post-core Should objective with a 250-row proof gate |

## Grok and Gemini design-source disposition check

| Reference | V3 disposition check |
|---|---|
| `DR-001`, Grok UI/UX PDF | Correctly adopts the checklist, plain language, large actions, warning detail, degraded-image state, and elapsed time while rejecting official identity, unsupported certainty, legal authority, and hard five-second cancellation. |
| `DR-002`, Gemini design PDF | Correctly adopts human-in-the-loop framing, split evidence view, component separation, and progress without inheriting its proposed stack or confidence as decision authority. |
| `DR-003`, Gemini empty workspace | Correctly keeps the split structure but replaces hidden initiation, named staff, and agency-like chrome with Try sample and one obvious custom-input path. |
| `DR-004`, Grok home | Correctly makes one submission primary, gates batch, uses neutral branding, and requires truthful data handling. |
| `DR-005`, Grok review | Correctly adopts image plus checklist, evidence links, state text, and elapsed time while quarantining its wrong net-contents cell and rejecting pass or return authority. |
| `DR-006`, Grok warning detail | Correctly adopts independent warning checks and uncertainty while rejecting automatic return, named-person policy, and compliance override. Physical type size remains explicitly human-only. |
| `DR-007`, Grok batch queue | Correctly remains conditional and exception-first, with no mixed-category fixture claim or unproved capacity claim. |
| `DR-008`, Gemini populated workspace | Correctly adopts only the evidence layout and bounding-region idea. Its nonsensical generated warning text remains quarantined from requirements and fixtures. |
| `DR-009`, Gemini processing view | Correctly rejects decorative AI theater and retains meaningful step, elapsed time, cancel, timeout, and recovery status. |

The design references remain evidence, not instructions. No generated value, visual error, proposed stack, government identity, or implied legal decision was promoted into product truth.

## Material finding

### `RT2-BAIRD-RR3-001` - HIGH - Undocumented punctuation repair can turn a noncanonical warning into Match

The authoritative selected policy is explicit:

- `docs/baird/WARNING_CAPABILITY_MATRIX.md:8` permits warning-body Match only for exact canonical characters after whitespace and line-wrap normalization. A readable word or punctuation mutation is Mismatch.
- `docs/baird/WARNING_CAPABILITY_MATRIX.md:9` permits heading Match only for the exact uppercase heading and colon. Missing or altered punctuation is Mismatch.
- `docs/intake/success-definition.md:18-19` requires documented field-specific punctuation policy and forbids insufficient evidence from becoming clean.
- `docs/intake/source-requirements.md:49-50` requires warning-wording mutations and heading capitalization failures to be detected.

The retained executable proof violates that policy in two places:

1. `research/baird-spike/spike.py:574` removes a final period whenever the OCR heading ends in `:.`. Lines 577-578 then return Match when the reduced value equals `GOVERNMENT WARNING:`. A readable label heading `GOVERNMENT WARNING:.` therefore becomes Match even though it has an added character.
2. `research/baird-spike/spike.py:277-280` removes a final period from any warning-body OCR row when the next row starts with a lowercase character. If the label visibly says `during pregnancy. because of the risk`, with the added period at the row boundary, reconstruction deletes that observed mutation. Lines 588-589 can then return Match against canonical `during pregnancy because of the risk`.

I reproduced both branches in memory without changing project files. The heading input `GOVERNMENT WARNING:.` reduced to `GOVERNMENT WARNING:` and selected Match. A two-row body containing the added period after `pregnancy.` reconstructed byte-for-byte to the canonical body after the period deletion.

The retained negative set does not protect these branches. S21 covers a missing colon. S22 covers added heading text. S02 happens to contain OCR text `Government Warning:.`, but title case controls its Mismatch, so it does not test the uppercase extra-period path. The planned `FX-016` says a word and punctuation are mutated but does not reserve the two deletion-boundary cases. The remediation claim that no readable negative can remain clean is therefore too broad.

Impact: a readable, noncanonical mandatory warning can receive a Match. If all other applicable checks match, the false Match can contribute to `No differences found in checked fields`. This is the exact class of error the original stakeholder warned was an automatic defect and the Intake explicitly prohibited.

Required remediation:

1. Remove both punctuation-deleting transformations from the exact comparator path. Exact warning normalization may change whitespace and line wrapping only.
2. When OCR punctuation is uncertain, return Review or Not verified using documented evidence thresholds. Do not repair observed punctuation into a Match.
3. Add independent oracle cases for uppercase `GOVERNMENT WARNING:.` and an added body period at an OCR line boundary. Both readable cases must be Mismatch and must prevent a clean aggregate.
4. Add a separate low-evidence OCR punctuation-artifact case that safely returns Review rather than proving exactness by repair.
5. Rerun the fixed direct and browser sets, independent field oracle, evidence validation, and all three BAIRD reviews against one new sealed manifest.

## Non-blocking precision cleanup

`docs/reviews/baird/BAIRD_RT_REMEDIATION.md:60` still says the complete browser result has 13 or 14 rows. V3 emits exactly 17 registry rows in every result, with 9 or 16 applicable rows for domestic cases and 17 for the retained import case. The later V3 closure rows are correct. Update the stale historical closure sentence when regenerating the remediation record.

## Confirmed strengths that should not regress

- The primary journey is smaller and clearer than the supplied enterprise-style mockups.
- The UI preserves original evidence, explicit uncertainty, human judgment, and accessible interaction instead of presenting AI confidence as authority.
- The one-click sample, expanded evidence table, warning detail, and actionable degraded states fit both a first-time evaluator and a low-tech compliance reviewer.
- Local packaged inference respects the blocked-outbound stakeholder context and avoids public-demo API keys or runtime model downloads.
- Warm performance is measured from Verify activation through rendered and announced complete results. Cold and deployed boundaries are reported honestly.
- Proof, warning applicability, producer nuance, import origin, 1 to 6 panels, and failure recovery now have explicit implementation and evidence contracts.
- Batch remains valuable but gated, which matches the assignment preference for a working clean core.
- Repository, all-source, README, brief approach/tools/assumptions documentation, public URL, and deployment provenance remain explicit release deliverables.

## Advancement condition

Correct `RT2-BAIRD-RR3-001`, regenerate all affected retained evidence and the sealed manifest, then repeat the three independent BAIRD reviews on the identical revision. The remaining change is narrow, but exact warning punctuation and zero false clean are core requirements, not optional I2R polish.
