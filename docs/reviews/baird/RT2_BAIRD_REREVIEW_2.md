REWORK_REQUIRED

# BAIRD Red Team 2 Re-review, Round 2

**Role:** Independent stakeholder UX, extraction feasibility, performance, and assignment-fit skeptic  
**Review date:** 2026-08-31  
**Reviewed snapshot manifest SHA-256:** `0d80c9ffa7bb2e7d23d550b1639d7e9dc2c520b8e8500e264c71ecf1c0e1e29d`  
**Material findings:** 2 High

## 1. Binary decision

The corrected architecture is close, but it is not ready for I2R. The product and stack direction remain appropriate. The new benchmark also fixes the prior producer, warning-presentation, cold-clock, timeout-denominator, and traceability defects. Two false-clean defects remain in the exact sealed evidence:

1. the benchmark defines its own reduced active-check set, omitting proof and warning applicability even though both are applicable under the authoritative BAIRD contract; and
2. the warning-heading comparator returns Match for readable headings that omit the required colon or add other heading text.

These defects invalidate the claims of zero omitted active checks, complete field-level results, and zero false clean on the retained architecture slice. They also leave the planned fixture allocation without independent negative coverage for the omitted branches. The likely runtime cost of correcting two deterministic checks is small, but this process cannot infer feasibility or correctness from likely cost. The corrected contract must execute and the evidence must be regenerated before BAIRD can be CLEAR.

## 2. Snapshot integrity

I verified the seal before substantive review and repeated the verification after all read-only checks.

| Check | Result |
|---|---|
| Manifest file | `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V2.sha256` |
| Expected manifest SHA-256 | `0d80c9ffa7bb2e7d23d550b1639d7e9dc2c520b8e8500e264c71ecf1c0e1e29d` |
| Actual manifest SHA-256 | Exact match |
| Listed entries | 95 |
| Missing files | 0 |
| Hash mismatches | 0 |
| Snapshotted files modified by this review | 0 |

This report is outside the manifest, as instructed.

## 3. Evidence reviewed

I reviewed the complete 95-entry snapshot, including:

- all CLEAR Intake artifacts, the Intake remediation, gate, and all Intake RT reports;
- every BAIRD product, UX, architecture, warning, security, source-coverage, control-handoff, and I2R-handoff artifact;
- all retained architecture, browser, cold-start, model, fixture, and validation evidence;
- the complete retained research source, dependency locks, server, browser harness, cold harness, fixture generator, and all 1, 3, and 6-panel fixture files;
- all three initial BAIRD RT reports, all three first BAIRD rereviews, the prior snapshot, and `BAIRD_RT_REMEDIATION.md`;
- every Grok and Gemini disposition in `docs/intake/design-reference-analysis.md`.

I also independently parsed the retained result JSON and compared its emitted check IDs with the authoritative field and warning contracts. This is how the reduced denominator was found.

## 4. Retest of every prior RT2 finding

| Finding | Round 2 result | Evidence and conclusion |
|---|---|---|
| `RT2-BAIRD-001`, load-bearing feasibility deferred | REOPENED IN PART | Warm architecture and real-browser evidence now exist, with 42 fixed attempts and an honest cold failure. The timed result is still not complete under the authoritative active-check contract because proof and warning applicability are omitted. See F001. |
| `RT2-BAIRD-002`, reference-conditioned candidate selection | CLOSED | `ENGINEERING_BLUEPRINT.md` and `spike.py` keep observation and primary candidate selection reference-blind. The ABV decoy case cannot select the expected value. |
| `RT2-BAIRD-003`, warning capability and aggregation unresolved | CLOSED AS DOCUMENTED POLICY, OPEN IN EXECUTION | The warning matrix is coherent, but one Active row is absent from the benchmark and the heading rule contradicts the matrix. See F001 and F002. |
| `RT2-BAIRD-004`, OCR fallback can silently weaken the core | CLOSED AS A GATE, OPEN FOR THE CLAIMED SLICE | The documents correctly reopen BAIRD after systematic family failure. The retained slice nevertheless excludes an applicable proof branch while claiming all committed field families. See F001. |
| `RT2-BAIRD-005`, Try sample has two behaviors | CLOSED | One activation loads a complete sample, starts verification, announces processing, and focuses the result heading. |

## 5. Retest of every prior RT2 second-round finding

| Finding | Round 2 result | Evidence and conclusion |
|---|---|---|
| `RT2-BAIRD-RR-001`, active warning rows and producer missing from feasibility proof | PARTIALLY CLOSED | The producer is now extracted and compared, and heading emphasis, body weight, separation, continuity, and contrast or legibility execute. Warning applicability is still missing, proof is missing, and the heading-exact branch can falsely Match. |
| `RT2-BAIRD-RR-002`, cold measurement excludes construction | CLOSED BY HONEST DISPOSITION | Five trials start before Python imports and include process start, model construction, readiness warmup, and first complete browser result. Conservative p95 is 10,287.61 ms, so local cold is correctly marked NOT CLOSED. |
| `RT2-BAIRD-RR-003`, exact five-second cancellation | CLOSED | Five seconds is the warmed p95 objective. Independent bounds are 6.25 s child, 6.75 s app, 7.5 s browser, and 9.0 s proxy. The fixed 42-attempt denominator retains errors and timeouts. |

The second-round RT1 and RT3 findings were also read and their remediated handoff controls were checked where they affect UX or feasibility. The corrected package now preserves client-identity tests, no-store tests, complete source-to-control ownership, brand case and punctuation behavior, and an independently bounded timeout chain. I found no additional RT2 blocker in those intersections.

## 6. Scenario attacks

| Scenario | Expected behavior | Round 2 result |
|---|---|---|
| First-time evaluator opens public URL | Honest notice, one-click sample, result without reading setup instructions | PASS AT DESIGN |
| Low-tech agent checks one label | Two obvious entry choices, grouped fields, one Verify action, plain reasons and recovery | PASS AT DESIGN |
| Try sample | One activation loads and runs, then moves focus to result | PASS |
| One, three, and six panels | Every supplied panel is decoded, evidence keeps panel identity, missing coverage cannot be clean | PASS ON RETAINED SLICE |
| Expected ABV appears as a decoy | Reference cannot select confirming text from the wrong role | PASS |
| Producer name or address differs | Observed producer candidate is compared to reference before aggregation | PASS |
| Exact warning with uncertain presentation | Any insufficient Active presentation evidence becomes Review or Not verified | PASS ON RETAINED SLICE |
| Warning applicability is uncertain or not established | Active applicability row returns Review and aggregates | NOT EXECUTED |
| Reference and label contain `45%` and `90 Proof` | ABV and proof relationship are both checked | NOT EXECUTED |
| ABV matches at `45%`, but label says `80 Proof` | Proof branch detects the inconsistency and prevents clean | FALSE-CLEAN PATH EXISTS |
| Heading reads `GOVERNMENT WARNING` without a colon | Readable formatting difference is reported | FALSE MATCH |
| Heading contains `GOVERNMENT WARNING EXTRA:` | Altered heading cannot be exact Match | FALSE MATCH |
| Warm valid result | Fixed valid-run denominator, complete rendered and announced result, p95 at or below 5 s | TIMING PASSES FOR REDUCED CONTRACT ONLY |
| True process cold start | Honest p95 below 10 s or clearly open release stop | PASS AS HONEST OPEN RISK, local result is 10.28761 s |
| Keyboard, screen reader, 200 percent zoom | Full core path is operable and announced | PASS AT DESIGN GATE |
| Batch is not built | Core remains complete and batch claims remain absent | PASS |
| Homework-assignment fit | Working, bounded core with evidence, README path, public URL plan, and explicit limitations | PASS IN DIRECTION, BLOCKED BY FALSE-CLEAN PROOF |

## 7. Material findings

### `RT2-BAIRD-RR2-001`: The self-defined benchmark denominator omits two applicable Active checks

**Severity:** High  
**Status:** OPEN

#### Concrete evidence

- `docs/intake/scope-boundary.md:33` selects alcohol comparison including ABV and proof normalization where defensible.
- `docs/baird/BAIRD_ASSESSMENT.md:91` makes proof Active when the reference or label presents proof and requires comparison with the reference plus the two-times-ABV relationship.
- `docs/baird/ENGINEERING_BLUEPRINT.md:100` includes optional `proof` input, and line 187 requires label/reference comparison plus an ABV relationship check.
- `docs/baird/I2R_HANDOFF.md:57` permits I2R to choose a separate proof row or an ABV sub-check. It does not permit I2R to omit proof evaluation.
- Every one of the 14 retained case references in `architecture-fixture-manifest.json` contains `"proof": "90"`. The generated label base also contains `90 Proof`, with consistent 80-proof variants in the ABV-difference cases.
- `docs/baird/WARNING_CAPABILITY_MATRIX.md` states that every Active row returns a state and aggregates. Its first row makes warning applicability at or above 0.5 percent ABV Active.
- `research/baird-spike/spike.py:35-39` defines `ACTIVE_CHECKS` without `proof` and without warning applicability.
- `research/baird-spike/spike.py:396-404` compares only the percentage candidate. It neither extracts proof nor checks its relation to ABV.
- `research/baird-spike/spike.py:461-464` validates omitted rows only against that reduced in-code set.
- `research/baird-spike/browser_benchmark.py:45-53` imports the same reduced set to validate omissions and false clean. The harness therefore cannot discover a check missing from its own definition.
- Independent parsing of all 42 retained architecture results found emitted checks for ABV, producer, country when applicable, five warning-presentation rows, wording, heading case, coverage, and quality when applicable. It found 0 proof rows and 0 warning-applicability rows.
- The retained `active_check_count` is 13 for domestic cases and 14 for the import case. Under the documented contract, the corresponding counts are at least 15 and 16 because proof and warning applicability are applicable.
- `docs/baird/evidence/EVIDENCE_VALIDATION.md` and `BAIRD_FEASIBILITY_REPORT.md` still report zero omitted Active rows because they accept the reduced denominator.
- `FIXTURE_ALLOCATION.md:16` changes both ABV and proof together in `FX-008`. It tests that proof cannot override a wrong ABV, but it does not test a matching ABV with a wrong proof or a wrong proof-to-ABV relationship. No allocated case tests warning-applicability uncertainty.

#### Impact

A label can show the expected `45%` and an inconsistent `80 Proof` while every emitted check is Match. The current aggregator can then return `No differences found`. This directly contradicts the BAIRD field contract, the assignment sample, the zero-false-clean invariant, and the claim that the timed browser result is complete.

The omission also weakens stakeholder trust. An agent sees alcohol content Match even though the application and label proof are inconsistent. Because the UI does not expose the missing sub-check, the human has no cue that the value was not evaluated.

#### Required remediation

1. Extract proof candidates reference-blind with field-role evidence.
2. Compare observed proof with reference proof when supplied and check its relationship to observed ABV when proof appears on the label.
3. Return a visible proof row or an explicit ABV sub-check with its own state, reason, and evidence. Either shape is allowed by the current handoff.
4. Execute warning applicability as the Active warning contract requires, including uncertainty when applicable ABV evidence cannot be established.
5. Derive the benchmark's expected Active set from an independent versioned contract or fixture oracle, not only from `spike.ACTIVE_CHECKS`.
6. Add at least one matching-ABV and mismatching-proof case, one proof-relationship case, and one warning-applicability uncertainty case to the retained slice and 25-fixture allocation.
7. Regenerate architecture and browser evidence. Recompute completion, omitted-row, false-clean, field-count, response-size, memory, and p95 claims against the authoritative set.

#### Closure proof

- every applicable proof and warning-applicability state is present in raw field-level results;
- a 45-percent and 80-proof case cannot return clean;
- the expected Active set is independent of the implementation list;
- 42 fixed architecture and 42 fixed browser attempts are regenerated with zero authoritative omissions and zero false clean;
- the warm p95 remains within the selected envelope, or BAIRD revises the architecture.

### `RT2-BAIRD-RR2-002`: The warning-heading comparator does not enforce the exact heading and colon

**Severity:** High  
**Status:** OPEN

#### Concrete evidence

- `docs/baird/WARNING_CAPABILITY_MATRIX.md` requires exact uppercase `GOVERNMENT WARNING:` for Match and explicitly classifies a missing colon or altered heading as Difference when readable.
- `research/baird-spike/spike.py:418-424` returns Match whenever the observed heading contains the uppercase substring `GOVERNMENT WARNING`. The branch does not require a colon and does not require the heading to equal the prescribed heading.
- The Match reason states that the colon was observed even though the condition never tests it.
- `FIXTURE_ALLOCATION.md` includes title case and warning-body mutation, but no missing-colon or extra-heading-text case.
- The retained 42-run evidence therefore cannot detect this branch defect.

#### Impact

A clear label with `GOVERNMENT WARNING` and no colon can receive Match for the heading. If the body and other fields match, the submission can receive `No differences found`. An altered heading such as `GOVERNMENT WARNING EXTRA:` can follow the same false-Match path. This is precisely the warning exactness that the junior agent emphasized and that the assignment asks the prototype to demonstrate.

Current primary sources reinforce the internal BAIRD contract. [27 CFR 16.21](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-16/subpart-C/section-16.21) prints the required statement beginning with `GOVERNMENT WARNING:`. [TTB health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) likewise includes the colon and states that the warning must appear as prescribed.

#### Required remediation

1. Compare a readable normalized heading against the complete prescribed heading, including the colon. Do not use substring presence as exact Match.
2. Return Difference for readable missing colon, extra heading text, or changed heading characters. Preserve Review or Not verified when OCR evidence is insufficient.
3. Add independent missing-colon and extra-heading-text cases to the architecture slice and fixture allocation.
4. Regenerate the field-level, browser, false-clean, and timing evidence after the comparator changes.

#### Closure proof

- missing colon and altered heading cases produce a heading Difference;
- uncertainty remains Review or Not verified rather than a guessed Difference;
- no clean result contains a non-exact readable heading;
- regenerated raw evidence and report claims match the corrected branch.

## 8. Confirmed strengths that should not regress

### Stakeholder and low-tech usability

- The first view has only `Try sample` and `Check another label` as meaningful paths.
- Try sample is one activation, not an ambiguous prepare-or-run choice.
- Plain state names, reason text, large actions, error focus, start-over, and no AI jargon fit the mixed technical-comfort audience.
- No agency seal, named employee, fake production queue, or autonomous Approve or Reject authority remains.

### Evidence UX and multiple panels

- The desktop split keeps the original image next to the field table.
- `Show on label`, panel switching, crop fallback, explicit unavailability, original-versus-processed labeling, zoom, and rotate are coherent.
- One, three, and six panels execute within the retained warm envelope and preserve panel identity.
- Producer now uses an observed candidate before reference comparison, closing the prior false-Match defect.

### Reference blindness and human judgment

- Expected values do not enter OCR or primary candidate selection.
- Competing candidates cap the result below Match.
- Brand exact, capitalization, punctuation, and substantive difference paths are separate.
- A human disposition remains separate and cannot rewrite system evidence.

### Warning presentation

- Heading emphasis, body non-bold, separation, continuity, and contrast or legibility now execute as distinct aggregating rows.
- Insufficient presentation evidence produces Review or Not verified.
- Physical type size remains an explicit human-only limitation.
- The remaining defects are exact completeness defects, not a reason to abandon the warning-detail design.

### Performance and cold honesty

- Forty-two warm architecture runs report p95 3,813.48 ms.
- Forty-two fixed real-Chrome attempts are all complete and report p95 3,580.50 ms.
- Every attempted valid run stays in the denominator.
- The user-visible clock ends after the result and live status are rendered across two animation frames.
- Five true process-spawn trials report conservative cold p95 10,287.61 ms. The package correctly says NOT CLOSED LOCALLY.
- One always-running Machine plus readiness protection makes continued I2R work reasonable after the false-clean findings are fixed, but five deployed forced restarts remain a hard release stop.

### Accessibility and responsive boundary

- Semantic headings, native controls, error focus, polite status, result focus, keyboard-only operation, text plus icon states, visible focus, 200 percent stacking, reduced motion, axe, and NVDA proof are explicit.
- The supported desktop envelope is honest. A mobile-specific design is not falsely promised.

### Batch and assignment scope

- Batch remains a post-core Should objective and is absent unless every single-submission gate passes.
- The architecture remains a proportionate modular monolith with no database, account system, external inference, COLA integration, wine or beer promise, or production-federal claim.
- README, source repository, approach, tools, assumptions, public URL, clean-checkout rehearsal, and limitation consistency retain named release controls.

## 9. Grok and Gemini disposition recheck

| Source | Current disposition | Round 2 result |
|---|---|---|
| `DR-001` Grok PDF | Checklist, plain language, warning detail, elapsed time adopted; authority, hard cancel, and premature batch rejected | PASS |
| `DR-002` Gemini PDF | Human-in-the-loop and split workspace adopted; proposed stack and confidence authority not inherited | PASS |
| `DR-003` Gemini empty workspace | Split structure retained; hidden input, named employee, and agency shell removed | PASS |
| `DR-004` Grok landing page | Large simple actions retained; single submission and sample are primary; batch gated | PASS |
| `DR-005` Grok review workspace | Image-and-checklist composition and evidence links retained; fixture errors and legal actions quarantined | PASS |
| `DR-006` Grok warning detail | Independent warning detail retained; override and automatic return rejected | PASS AS DESIGN, execution blocked by F001 and F002 |
| `DR-007` Grok batch queue | Exception-first pattern preserved only for a future validated batch | PASS |
| `DR-008` Gemini populated workspace | Layout and regions retained; nonsensical generated text quarantined; authority controls rejected | PASS |
| `DR-009` Gemini AI overlay | Decorative scan rejected; step, elapsed time, status, cancel, and recovery selected | PASS |

The supplied concepts remain inspiration rather than requirements or fixture truth. No design source has displaced the original assignment or verified TTB sources.

## 10. Current source check

The two material findings are supported first by the project's own selected contract. I also rechecked the relevant current primary sources:

- [27 CFR 5.65](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-5/subpart-E/section-5.65) says proof may appear in addition to the required ABV statement. The BAIRD package has already selected comparison and relationship behavior when proof is present.
- [27 CFR 16.21](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-16/subpart-C/section-16.21) presents the mandatory warning with the colon.
- [TTB health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) confirms applicability at not less than 0.5 percent ABV and the prescribed warning format.

No current source check supports omitting an already selected Active row or treating substring presence as exact heading compliance.

## 11. Re-review gate

Do not advance this snapshot to I2R. Correct F001 and F002, allocate the missing negative cases, regenerate the architecture and browser evidence, seal a new unchanged manifest, and repeat all three independent BAIRD reviews.

RT2 can return CLEAR when the same corrected snapshot proves:

1. proof and warning applicability execute whenever applicable;
2. the authoritative expected-check set is independent from the implementation set;
3. readable missing-colon and altered-heading cases cannot Match;
4. all fixed attempts contain every applicable Active check and zero false clean;
5. the complete corrected browser result remains within the warmed performance envelope;
6. the honest local cold failure and deployed restart stop remain unchanged;
7. all stakeholder, accessibility, multi-panel, data-handling, batch, and assignment-scope controls above remain intact.
