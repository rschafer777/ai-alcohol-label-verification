REWORK_REQUIRED

# RT1 BAIRD Architecture and Requirements Fidelity Rereview

## Reviewed snapshot

- Snapshot manifest: `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT.sha256`
- Manifest SHA-256: `02b68ffb8148f0880fa70b51135b062238a196eab8739894e141f66083381d71`
- Manifest entries verified: 45 of 45
- Hash mismatches: 0
- Review rule: the manifest was verified before review and verified again before this report was written.

I reviewed the complete Intake package, every BAIRD artifact in the snapshot, the retained feasibility source and raw evidence, all three initial BAIRD review reports, and `docs/reviews/baird/BAIRD_RT_REMEDIATION.md`. I also spot-checked the material RapidOCR and Fly.io claims against the current primary sources listed in `docs/baird/TECHNICAL_SOURCE_REGISTER.md`. No additional platform-source mismatch changes the findings below.

## Binary verdict basis

The selected modular monolith, same-origin React and FastAPI boundary, local RapidOCR and ONNX path, deterministic comparison layer, one-job worker model, and always-ready Fly deployment remain credible directions. BAIRD cannot advance to I2R on this snapshot because three high-severity contradictions can create a false architecture pass or a false clean result. A fourth traceability defect would also make source-to-FRD derivation unreliable.

## Prior RT1 finding retest

| Prior finding | Rereview result | Reason |
|---|---|---|
| `RT1-B-F001` load-bearing assumptions | NOT CLOSED | The retained browser test does not render a complete field-level result, and the feasibility comparator omits multiple Active warning checks. The report therefore overstates the evidence used to close `ASM-007` and the zero-false-clean gate. See `RT1-B-RR-F002`. |
| `RT1-B-F002` warning capability and aggregation | NOT CLOSED | The written capability matrix now has the correct aggregation rule, but the retained feasibility implementation does not execute that rule and declares clean results without evaluating all applicable Active warning checks. See `RT1-B-RR-F002`. |
| `RT1-B-F003` resource envelope | CLOSED AT DESIGN LEVEL | The BAIRD documents now select byte, pixel, canvas, concurrency, worker, host, region, and cost boundaries with release stops. The retained 1.23 GB number is not independently preserved in raw metadata and the selected parent-child topology was not measured, so the full-path evidence correction in `RT1-B-RR-F002` must also retain topology-level memory evidence. |
| `RT1-B-F004` latency and timeout contract | NOT CLOSED | The p95 target is still implemented as an exact five-second browser cancellation, which Intake explicitly rejected. See `RT1-B-RR-F001`. |
| `RT1-B-F005` option and fallback evidence | CLOSED | The corrected assessment distinguishes measured, documented, and unknown evidence; removes unsupported weighted scores; rejects Tesseract.js only on measured required-field failures; and reopens BAIRD if the selected adapter fails instead of silently narrowing scope. |

## Findings

### RT1-B-RR-F001 - HIGH - The hard five-second cancellation contradicts the attested latency contract

**Evidence**

- `docs/intake/INTAKE_DOCUMENT.md:128-132` defines 5.0 seconds as a deployed warmed-path p95 for valid supported runs. Every measured success must end with the complete result rendered and announced.
- `docs/intake/success-definition.md:54-64` states that timeouts and actionable failures do not count as valid-result success. A p95 permits valid outliers above the target and exposes them in the run distribution.
- `docs/intake/INTAKE_DOCUMENT.md:162-171` explicitly lists "hard cancellation at five seconds" among the Grok and Gemini ideas that must not become requirements.
- `docs/baird/UX_PRODUCT_SPEC.md:47` correctly says an independent hard safety deadline may return an actionable non-clean timeout and that failures do not satisfy the p95 target.
- `docs/baird/SECURITY_DATA_FLOW.md:146-148` then sets the browser abort at exactly 5.0 seconds from Verify activation, with an app deadline at 4.75 seconds and a worker deadline at 4.4 seconds.

**Impact**

The exact five-second abort converts every slower valid result into a failure that is excluded from the valid-result p95. This makes the release metric self-fulfilling, prevents observation of valid performance outliers, and directly imports a rejected design-reference idea. It also makes the statement at `SECURITY_DATA_FLOW.md:148` that a valid p95 outlier can be returned misleading because the browser cannot receive a valid result after the same five-second boundary.

**Required remediation**

1. Preserve 5.0 seconds only as the valid-result p95 target.
2. Select a separate hard safety deadline above the p95 threshold and within the attested degraded/cold bounds, or define a justified security deadline that does not make valid-result measurement circular.
3. Reorder worker, app, browser, and proxy deadlines around that independent safety bound.
4. Add a benchmark assertion that valid results above five seconds remain observable, count in the run distribution, and fail the p95 gate when sufficiently frequent.

### RT1-B-RR-F002 - HIGH - The feasibility report claims a complete result and zero false cleans while its implementation omits required checks and UI output

**Evidence**

- `docs/baird/evidence/BAIRD_FEASIBILITY_REPORT.md:9-20` says the slice exercised deterministic comparison, safe aggregation, result rendering, and live-region update. Lines 45-56 report zero false cleans. Lines 62-74 claim 20 of 20 complete field-level browser results. Lines 96-106 use those results to support the selected architecture and zero-false-clean tolerance.
- `research/baird-spike/server.py:40-53` renders only one `h2` containing the submission summary and one status string. It does not render any field rows, field states, extracted/reference values, evidence links, panels, quality/coverage states, limitations, or warning presentation results required by `docs/baird/ENGINEERING_BLUEPRINT.md:191-219`.
- `research/baird-spike/browser_benchmark.py:12-48` benchmarks only four clean cases: `S01_clean_one`, `S07_three_panel`, `S08_six_panel`, and `S09_high_resolution`. It asserts only completion, summary, and status text. It does not exercise a browser-visible Difference, Review, Not verified, degraded-image, warning-format, decoy, or import path.
- `research/baird-spike/spike.py:238-303` evaluates brand, class/type, ABV, net contents, warning heading text, warning body text, a producer anchor, optional country, and blur. It does not evaluate heading emphasis, remaining warning text not bold, separation, continuity, contrast/legibility, or panel coverage.
- `docs/baird/WARNING_CAPABILITY_MATRIX.md:3-21` makes all of those applicable checks Active and permits `No differences found` only when every applicable Active check is Match.
- The clean raw runs in `docs/baird/evidence/rapidocr-server-runs.csv` therefore cannot establish zero false cleans under the corrected authoritative matrix. The spike simply has no state for several checks that must aggregate.
- `research/baird-spike/server.py:61-88` runs RapidOCR directly in the FastAPI process. It does not exercise the selected long-lived killable child, IPC, worker deadline, replacement warmup, upload guard, or full result response. The retained process RSS also does not prove the selected parent-plus-child peak.
- The snapshot retains no generated `metadata.json`, field-level detail output, fixture manifest, or Python dependency lock from the run. The 1.23 GB peak and exact full dependency environment therefore cannot be independently audited from the preserved raw evidence.

**Impact**

The measured OCR timing is useful, but it is not the complete architecture path or complete result contract described by the report. Adding omitted visual checks, evidence construction, full JSON, worker IPC, and field-level browser rendering consumes time and memory that are absent from the claimed p95 and peak. More importantly, the slice can issue `No differences found` without evaluating every Active check, so its zero-false-clean claim is invalid under the corrected BAIRD state machine. I2R would inherit an architecture marked feasible on evidence that does not represent the selected product behavior.

**Required remediation**

1. Re-run a retained architecture slice that produces the complete `VerificationResult` contract and executes every applicable Active warning and coverage check.
2. Render and announce all field-level results, states, evidence availability, coverage/quality, and limitations before stopping the browser clock.
3. Include representative clean, Difference, Review, Not verified, degraded, decoy, import, and multi-panel browser paths, not only clean summaries.
4. Exercise the selected parent-child worker boundary or explicitly measure and add its IPC, memory, cancellation, and replacement overhead.
5. Retain the fixture manifest, field-level result details, run metadata including peak RSS, and an exact Python dependency lock so the evidence is auditable and reproducible.
6. If any Active visual check cannot reach a tested Match/Difference/uncertainty state with defensible evidence, reopen its BAIRD capability decision. Do not label the architecture gate PASS by omitting the check.

### RT1-B-RR-F003 - HIGH - Fixture truth and retained comparison logic violate the capitalization and punctuation policy

**Evidence**

- `docs/intake/source-requirements.md:37-38` requires the supplied capitalization example to route to Review and requires unproven punctuation variation to route to Review rather than automatic Match.
- `docs/baird/ENGINEERING_BLUEPRINT.md:166-189` repeats the selected rule: brand exact Match, case-only Review, punctuation change Review, and no automatic semantic Match.
- `docs/baird/SOURCE_COVERAGE.csv:20-21` claims BAIRD selected those controls.
- `docs/baird/evidence/FIXTURE_ALLOCATION.md:13` assigns `FX-005`, "Brand capitalization and punctuation equivalence," the expected summary `No differences found`.
- `research/baird-spike/spike.py:243-250` uppercases values and removes all non-alphanumeric characters before comparing brand and class/type. That makes both case and punctuation differences automatic Match.

**Impact**

The test oracle and feasibility comparator contradict the authoritative policy and can produce a false clean for the exact judgment scenario highlighted in the assignment. This is source drift, not an I2R-level threshold choice. It also undermines the fixture allocation claim that expected outcomes are independent and source-derived.

**Required remediation**

1. Change `FX-005` to Review needed and split capitalization and punctuation into separate cases if both transformations are being tested.
2. Preserve exact, case-only, punctuation-only, and substantive differences as distinct comparison paths.
3. Correct the retained spike or retract any feasibility claim that depends on its generic uppercased alphanumeric comparator.
4. Audit every fixture expected outcome against `SRC-019`, `SRC-020`, the field policy, and the deterministic aggregate before I2R handoff.

### RT1-B-RR-F004 - MEDIUM - The machine-readable source coverage points to the wrong BAIRD sections

**Evidence**

- `docs/baird/SOURCE_COVERAGE.csv:16` maps accessibility source `SRC-015` to `UX_PRODUCT_SPEC section 11`, but accessibility is section 8 and section 11 is the batch gate.
- `docs/baird/SOURCE_COVERAGE.csv:17` maps keyboard and focus source `SRC-016` to sections 9 through 11, while the operative keyboard/focus contract is section 8.
- `docs/baird/SOURCE_COVERAGE.csv:18` maps progress source `SRC-017` to `UX_PRODUCT_SPEC section 4` and `ENGINEERING_BLUEPRINT section 12`; those sections are status language and quality metrics, not the complete processing and timeout contract.
- `docs/baird/SOURCE_COVERAGE.csv:19` maps evidence interaction source `SRC-018` to `UX_PRODUCT_SPEC section 5`, while evidence interactions are section 6.
- `docs/baird/SOURCE_COVERAGE.csv:21` maps normalization source `SRC-020` to `ENGINEERING_BLUEPRINT section 8`, while the comparison policy is section 7.
- `docs/reviews/baird/BAIRD_RT_REMEDIATION.md:50` presents this CSV as the explicit closure evidence for source-to-I2R handoff.

**Impact**

All source IDs are present, but presence is not durable traceability when the control locator resolves to unrelated content. I2R can miss the operative requirement or derive it from the wrong section. This fails the stated objective of producing binary requirements without invention.

**Required remediation**

1. Correct every section locator in `SOURCE_COVERAGE.csv` against the current document headings.
2. Add an automated traceability check that validates referenced file and section identifiers and detects stale numbering.
3. Rerun the full `SRC-001` through `SRC-058` semantic mapping review after the corrections, not only an identifier-presence check.

## Strengths retained

- The core scope remains faithful to the assignment: standalone proof of concept, no COLA integration, no autonomous approval/rejection, no persistence, and no external inference.
- The BAIRD package correctly separates authoritative assignment and Intake evidence from Grok and Gemini inspiration.
- The four-state field model and three-state aggregate are explicit and conservative in the written architecture.
- The selected upload, pixel, concurrency, data-lifetime, same-origin, logging, provenance, deployment-readiness, and rollback boundaries are specific enough for I2R once the findings above are corrected.
- Batch remains conditional and cannot displace the core single-submission release gates.
- The option analysis and fallback stop gates are substantially stronger than the initial BAIRD revision.

## Advancement decision

Do not advance this snapshot to I2R. Remediate `RT1-B-RR-F001` through `RT1-B-RR-F004`, generate a new checksummed BAIRD snapshot, and repeat all three independent BAIRD reviews against that exact revision. CLEAR requires no material finding to remain.
