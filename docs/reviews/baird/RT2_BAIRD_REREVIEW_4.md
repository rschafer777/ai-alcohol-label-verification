REWORK_REQUIRED

# BAIRD Red Team 2 Rereview 4

Review date: 2026-08-31

Role: Independent stakeholder UX, product safety, extraction feasibility, performance, and assignment-fit skeptic

## Sealed snapshot

- Manifest: `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V4.sha256`
- Expected and observed manifest SHA-256: `8e2b88b12699f8192bc1b66637885ac9c8fbc1f72cd4158604775d0d2f80932b`
- Expected and observed hashed entries: 144
- Missing files: 0
- Hash mismatches: 0

I verified the manifest and all 144 file hashes before review. I repeated the complete verification after inspecting this report and immediately before finalization. This report is outside the manifest. No snapshotted file was modified.

## Gate basis

V4 materially improves the package and closes the warning-punctuation, false-clean country selection, worker ownership, multipart storage, governed-rule readiness, slow-upload deadline, and stale-assumption defects found in V3. The selected product remains appropriately narrow, honest, accessible by design, and aligned to the take-home assignment.

One material UX and contract defect remains. A conflicting country result safely returns Review and includes both values in `extracted_display`, but the selected result schema defines only one `evidence_ref`, and the retained browser renders only that one evidence location. The API's ad hoc `evidence_refs` array does not associate a value with its region, the independent oracle does not assert the alternatives, and the browser proof never checks them. This contradicts the explicit requirement that every plausible alternative be shown with its panel and region evidence. It must be resolved before I2R derives the FRD and API contract.

## Review scope and independent checks

I reviewed the complete sealed package, including:

- the sanitized original assignment, stakeholder requirements, requester instructions, and attested Intake;
- every Grok and Gemini source disposition;
- BAIRD product, UX, warning, architecture, security, performance, deployment, evidence, traceability, and I2R-handoff documents;
- all initial BAIRD reviews and V1 through V3 rereviews;
- the V4 remediation record, 17-check registry, regulatory-rules registry, 37-case oracle, 74 direct runs, 74 managed-Chrome runs, five cold trials, timeout evidence, storage/admission evidence, and actual ASGI worker-control evidence;
- the retained fixture generator, comparison code, server, browser harness, cold harness, security harness, runtime-control harness, model BOM, dependency locks, and research fixtures.

I independently merged the base oracle and case overrides for every direct result. The recomputation covered 37 cases, 74 runs, and 1,258 field rows. It found zero error in check membership, applicability, state, reason code, required primary evidence, or aggregate summary. Every result emitted the 17 registry rows exactly once.

I independently parsed the browser evidence. All 74 attempts completed with 17 DOM rows, no timeout or request error, no false clean, no false mismatch, and the required `no-store, private` success header. The user-visible p95 was 4213.30 ms and the maximum was 4480.40 ms.

I reran the traceability validator. It passed with 58 source rows, 12 ADRs, 8 BGs, 18 THRs, requirements `R-001` through `R-096`, tests `T-001` through `T-096`, 30 allocated fixtures, and zero prohibited Unicode dash characters.

I also rechecked the current official TTB distilled-spirits guidance. The current TTB health-warning page and label anatomy guidance continue to require the prescribed warning, exact punctuation, the uppercase bold heading, non-bold remainder, separation, continuity, and the 0.5 percent ABV applicability threshold. The V4 regulatory registry remains aligned with those current primary sources.

## Prior finding retest

| Finding family | V4 result | Evidence |
|---|---|---|
| `RT2-BAIRD-001`, load-bearing extraction and latency proof | PASS FOR BAIRD DIRECTION | The retained 37-case slice covers 1, 2, 3, and 6 panels, 12 MP input, all 17 checks, warning, proof, producer, country, quality, ambiguity, and a complete browser result. Warm p95 is below five seconds. |
| `RT2-BAIRD-002`, reference-conditioned candidate selection | PASS | OCR, observed candidates, and primary selection remain reference-blind. Expected values first enter at comparison. Decoy ABV and country cases preserve that boundary. |
| `RT2-BAIRD-003`, warning capability and aggregation | PASS | The matrix, regulatory registry, comparator, and cases S28 through S31 agree. Exact punctuation mutations are Mismatch. Low-evidence punctuation is Review. No punctuation repair can create Match. |
| `RT2-BAIRD-004`, fallback silently weakens core | PASS AS A GATE | Systematic field-family failure reopens BAIRD or requires approved scope change. Uncertainty remains case-level Review or Not verified and cannot hide a non-working family. |
| `RT2-BAIRD-005`, ambiguous Try sample | PASS | One activation loads a complete synthetic sample, starts verification, announces processing, and focuses the result heading. |
| `RT2-BAIRD-RR-001`, incomplete active warning/producer execution | PASS | Every result has all 17 rows. Producer, warning applicability, exact wording, heading, presentation, panel coverage, and image quality all execute and aggregate. |
| `RT2-BAIRD-RR-002`, cold construction omitted | PASS BY HONEST DISPOSITION | Five clocks start before imports and include assets, OCR construction, readiness, and the first browser result. Local cold p95 is 11557.18 ms, so the target remains explicitly open for deployed proof. |
| `RT2-BAIRD-RR-003`, exact five-second cancellation | PASS | Five seconds is only the valid-result warmed p95 objective. The 7.5-second browser safety boundary and non-clean timeout remain separate. |
| `RT2-BAIRD-RR2-001`, proof and warning applicability omitted | PASS | Both are registry checks. S15 through S20 cover proof difference, absence, ambiguity, below-threshold, threshold, and unparseable applicability. |
| `RT2-BAIRD-RR2-002`, missing-colon or altered-heading false clean | PASS | S21, S22, and S28 produce Mismatch for missing, altered, and extra punctuation. |
| `RT2-BAIRD-RR3-001`, punctuation deletion manufactures Match | PASS | Lines 306 and 643 through 667 of the V4 spike preserve observed punctuation for exact comparison. S28 through S30 are Differences detected, while S31 is Review needed. |
| `RT1-B-RR3-F002`, conflicting country candidates hidden by first Match | PASS FOR STATE SAFETY, OPEN FOR UX EVIDENCE | S33 returns Review and `CANADA, USA`; both polygons exist in `evidence_refs`. The chosen UI and result contract do not expose each value-region pair. See `RT2-BAIRD-RR4-001`. |
| V3 runtime queue and ownership findings | PASS FOR BAIRD DIRECTION | The actual ASGI control proves a 200 ms waiter bound, pre-body third rejection, result-free active timeout, shielded cancellation ownership, replacement, cleanup, zero final reservations, and two complete recovery results. |
| V3 two-copy spool finding | PASS FOR BAIRD DIRECTION | Two admissions reserve 101,187,584 bytes within the 128 MiB quota. Two actual near-limit multipart flows peak at 100,651,008 bytes and return to zero. |
| V3 governed-rule readiness finding | PASS | Exact model, check-registry, and rule-registry hashes and versions plus non-writable assets are required. Six invalid states fail readiness. |
| V3 total-upload deadline finding | PASS | The application owns a three-second pre-body total deadline that does not reset with activity. Two slow clients receive 408, a third is rejected pre-body, and capacity returns to zero. |
| V3 stale Intake assumptions | PASS | `ASM-007` and `ASM-012` now name the current V4 evidence and preserve the local cold and implementation-corpus release stops. |

## Scenario review

| Scenario | Required outcome | V4 result |
|---|---|---|
| First-time evaluator opens the app | Unofficial and synthetic-only notice, Try sample as the obvious first action | PASS by the UX contract |
| Low-tech agent checks a custom label | Plain groups, one Verify action, retained inputs, actionable errors, no technical vocabulary requirement | PASS by the UX contract |
| Brand differs only by capitalization | Human judgment remains visible instead of naive Match or automatic failure | PASS, Review needed |
| One, three, or six panels contain required evidence | All checks remain present and evidence preserves panel context | PASS in retained direct and browser evidence |
| Proof differs, is absent, or is ambiguous | Mismatch or uncertainty controls the summary | PASS in S15 through S17 |
| Warning punctuation is readable and altered | Mismatch, never repaired Match | PASS in S28 through S30 |
| Warning punctuation is not reliable | Review, never Mismatch without evidence and never Match by repair | PASS in S31 |
| Warning is below or at 0.5 percent ABV | Applicability and non-applicable rows are explicit | PASS in S18 and S19 |
| Warning applicability cannot be determined | Review prevents clean result | PASS in S20 |
| Two identical country candidates exist | No false ambiguity from duplicate identical evidence | PASS for country state in S32 |
| Canada and USA are both plausible origin candidates | Review, both values visible, each linked to its own panel/region evidence | PARTIAL: state and values pass, per-alternative evidence UI fails |
| Origin is missing, unreadable, a decoy, or a true difference | Uncertainty, reference-blind Match, or Mismatch as evidence supports | PASS in S34 through S37 |
| Glare or blur makes evidence unreliable | Review or Not verified and an actionable image-quality path | PASS in the retained quality cases and UX error contract |
| Valid warm submission completes | Complete rendered and announced result under five-second p95 | PASS on the local equivalent envelope; deployment remains a hard gate |
| Cold server starts | No hidden pass from the local miss | PASS by honest limitation; local 11.55718-second p95 is not relabeled |
| OCR child hangs or requester disconnects | No partial result, no orphaned work, cleanup and recovery | PASS for the retained architecture control |
| Keyboard, assistive technology, and 200 percent zoom | Complete workflow, visible focus, live status, result focus, text/icon states, and responsive stacking | PASS as an explicit I2R acceptance contract, not yet as product evidence |
| Peak-season batch demand | Preserve future value without endangering the working core | PASS; batch remains absent unless the post-core 250-row gate passes |

## Material finding

### `RT2-BAIRD-RR4-001` - MEDIUM - Conflicting candidate evidence is not structurally paired or visibly rendered

The product requirement is explicit:

- `docs/baird/UX_PRODUCT_SPEC.md:95` requires a Review row to list every plausible alternative with its panel and region evidence and forbids concealing conflicting country text.
- `docs/baird/ENGINEERING_BLUEPRINT.md:151-164` requires ambiguity alternatives with evidence and says the UI shows all material alternatives.
- The evidence interaction at `UX_PRODUCT_SPEC.md:141-148` requires `Show on label`, the correct panel, an outline, and an equivalent labeled crop.

The V4 country logic safely detects the conflict:

- `research/baird-spike/spike.py:606-617` returns Review with reason `country_ambiguous`, observed text `CANADA, USA`, one primary `evidence_ref`, and an `evidence_refs` array.
- The S33 direct payload retains two different polygons on panel 2.

The selected contract and browser do not complete that behavior:

1. `docs/baird/ENGINEERING_BLUEPRINT.md:191-218` defines only `evidence_ref or null` in each result row. It does not define a typed alternative object that pairs each observed value with its own evidence reference.
2. The V4 API's `extracted_display` is alphabetically sorted while `evidence_refs` remain in candidate encounter order. The two arrays have no explicit association, so a consumer cannot safely infer which polygon belongs to which country.
3. `research/baird-spike/server.py:456-458` renders `extracted_display` and only `field.evidence_ref`. It never reads `evidence_refs`. For S33, the user sees both country names but only one generic `Panel 2` evidence cell and cannot inspect the second region.
4. `research/baird-spike/browser_benchmark.py:140-176` validates the field oracle, row count, summary, status, and limitations. It does not assert either alternative value, either region, or an evidence action for both.
5. `docs/baird/evidence/expected-field-manifest.json:170-174` requires only one evidence reference for S33. The oracle would still pass if the second alternative polygon disappeared.

Impact: the aggregate is safe, but the evidence-backed human judgment workflow is incomplete. A reviewer cannot verify why two origins were considered plausible, which contradicts the app's central promise that the checklist exposes where each result came from. Leaving the plural payload outside the selected schema also forces I2R to invent a compatibility-sensitive contract.

Required remediation:

1. Add a typed `alternatives[]` result structure. Each item must contain the observed display or parsed value and its own evidence reference. Do not rely on parallel arrays or ordering.
2. Keep the singular candidate shape for unambiguous fields, or define one consistent candidate-list model, but make the selected API schema authoritative.
3. Render every S33 alternative as an accessible labeled item with its own `Show on label` action, panel switch, region outline, and equivalent crop description.
4. Extend the independent oracle to require the exact alternative values, count, and distinct evidence references for S33.
5. Extend the browser harness to assert that both `CANADA` and `USA` are visible, both evidence actions exist, and activating each targets the correct polygon.
6. Regenerate the direct and browser evidence, validation report, remediation record, and sealed manifest, then repeat the three independent BAIRD reviews.

## Grok and Gemini disposition recheck

| Reference | V4 disposition |
|---|---|
| Grok UI/UX PDF | Correctly informs checklist, plain language, warning detail, degraded-image handling, and elapsed time without becoming stack or legal authority. |
| Gemini design PDF | Correctly informs human-in-the-loop framing, split evidence workspace, progress, and modularity without making confidence authoritative. |
| Gemini empty workspace | Correctly contributes the split composition while hidden initiation, staff identity, official shell, and unused navigation remain rejected. |
| Grok home | Correctly contributes large, obvious entry actions while single submission remains primary and batch remains gated. |
| Grok review | Correctly contributes source/result comparison and evidence links while its incorrect sample cell and legal pass/return controls remain quarantined. |
| Grok warning detail | Correctly contributes independent warning checks and uncertainty while named-person rules, automatic return, and compliance override remain rejected. |
| Grok batch queue | Correctly remains a conditional exception-first pattern with no mixed-category or capacity overclaim. |
| Gemini populated workspace | Correctly contributes bounding-region and comparison ideas while its nonsensical warning text remains excluded from fixture truth. |
| Gemini processing view | Correctly remains rejected as decorative AI theater in favor of meaningful progress, timing, cancel, and recovery. |

The reference assets remain inspirational evidence, not instructions. No generated value, visual mistake, proposed technology, agency identity, named employee, or implied legal decision has been promoted into product truth.

## Assignment-fit conclusion

The selected direction otherwise meets or exceeds the original homework expectations without material scope drift:

- it concentrates on a working distilled-spirits core rather than pretending to cover all beverage categories;
- it automates routine comparison while preserving human judgment and exact warning nuance;
- it supports 1 to 6 panels, poor-image uncertainty, and a one-click sample without requiring COLA integration;
- it uses local packaged inference, fitting the blocked-outbound stakeholder environment;
- it makes the five-second metric user-visible and refuses to count failures as successful results;
- it keeps batch valuable but non-blocking;
- it preserves the repository, all-source, README, approach/tools/assumptions documentation, and public deployed URL deliverables;
- it explicitly avoids government identity, production-federal claims, persistence, and automatic legal approval.

## Strengths that should not regress

- Clear first-time and low-tech journey.
- Full 17-row deterministic result and safe aggregate state machine.
- Exact warning wording and punctuation with evidence-aware uncertainty.
- Reference-blind candidate selection and explicit human-review states.
- Original-image evidence, reversible view controls, and no AI theater.
- Honest warm, hard-timeout, cold, deployment, and synthetic-data limitations.
- Testable keyboard, focus, live-region, color-independent, and 200 percent zoom requirements.
- Core-first scope and explicit release deliverables.

## Advancement condition

Close `RT2-BAIRD-RR4-001`, regenerate the affected evidence, and reseal the package. The country state is already safe, so the correction is bounded, but the selected evidence contract must let a human inspect every conflicting candidate before I2R turns it into the FRD and implementation plan.
