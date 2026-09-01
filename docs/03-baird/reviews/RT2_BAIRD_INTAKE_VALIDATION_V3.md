REWORK_REQUIRED

# RT2 BAIRD Intake Validation V3

Review role: stakeholder, user experience, and requirements fidelity red team  
Reviewed snapshot: `docs/03-baird/BAIRD_INTAKE_SNAPSHOT_V3.sha256`  
Expected and observed manifest SHA-256: `57f094518cbdf8c2680307623923464ec7ef4943189f5ff8ed020cb92019d8c8`  
Manifest entries: 34  
Hash verification: 34 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015 scan: 0 findings in the sealed snapshot

## Material findings

### RT2-BV3-F001 - HIGH - The low-tech usability gate tests only Try sample, not the primary manual workflow

`SRC-012` requires both Try sample and manual core journeys to pass usability review without external instructions at `docs/intake/source-requirements.md:24-25`. `SRC-013` separately supplies the self-starting sample path at `docs/intake/source-requirements.md:26`. The approved success definition also distinguishes Try sample from manual reference entry and 1 to 6 panel upload at `docs/intake/success-definition.md:14-20`.

BAIRD maps `SRC-012` through `SRC-014` to `BR-013`, but the only acceptance outcome for `BR-013` is that a first-time evaluator identifies the primary action, uses Try sample, and completes the flow at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:93`. The UX baseline describes fields and file selection at lines 117-125, but it does not require a first-time user to complete the manual journey without help. `BR-002` proves that manual inputs can be processed, not that the described low-tech agent can use them. The source disposition matrix therefore overstates `SRC-012` as fully carried at `docs/03-baird/02_BAIRD_SOURCE_DISPOSITION_MATRIX.md:27`.

This is material because Try sample bypasses the actual agent tasks of entering reference data, understanding applicability, supplying panels, correcting input errors, and initiating verification. A design could satisfy every current BAIRD acceptance outcome while remaining confusing for the primary user described in discovery.

Required remediation:

1. Amend `BR-013` acceptance so a first-time evaluator completes both Try sample and the supported manual reference, upload, verification, result-inspection, and correction journey without external instruction.
2. Preserve exact interaction design as an I2R A&E decision. This correction needs an observable usability outcome, not a selected layout.
3. Update the source disposition note so the carried acceptance is explicit.

### RT2-BV3-F002 - HIGH - BR-009 drops independently required warning-presentation checks that the matrix marks as carried

The Intake requires more than warning wording, heading capitalization, and emphasis:

- `SRC-026` requires prescribed wording at `docs/intake/source-requirements.md:49`.
- `SRC-027` and `SRC-028` require heading uppercase and evidence-bounded emphasis at lines 50-51.
- `SRC-029` requires continuity, separation, contrast, and legibility as independent checks where supported at line 52.
- `SRC-030` requires an explicit physical-size limitation at line 53.

`BR-009` names only prescribed text, heading capitalization, and heading emphasis. Its acceptance outcome refers only to exact text, heading checks, and unsupported physical-format checks at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:89`. It does not require continuity, separation, contrast, or legibility to be evaluated independently when the image evidence supports them. However, the disposition matrix marks all of `SRC-026` through `SRC-030` as carried by `BR-009` and `BR-022` at `docs/03-baird/02_BAIRD_SOURCE_DISPOSITION_MATRIX.md:41-45`. `BR-022` preserves provenance, not the omitted user-visible checks.

This is material because the government warning is the highest-nuance compliance area in the discovery. I2R A&E could omit four approved warning checks and still satisfy the current BR wording and acceptance outcome.

Required remediation:

1. Amend `BR-009` to enumerate prescribed wording, heading capitalization, emphasis, continuity, separation, contrast, and legibility as distinct evidence-backed capability outcomes.
2. Require each applicable property to return Match, Mismatch, Review, or Not verified according to documented capability and evidence.
3. Keep physical type size and any other unprovable property explicitly Not verified or assigned to human confirmation. Let `BQ-005` select the technical detection boundary.

## V2 CLEAR retest and unaffected areas

The V2 RT2 conclusions remain valid for human authority, false-clean prevention, evidence visibility, image and panel insufficiency, accessibility, privacy disclosure, blocked-egress behavior, performance honesty, batch deferral, evaluator deliverables, and Grok/Gemini disposition. The V3 additions also close the prior source-lineage, code-quality, limitation, public-artifact, cold-start, and process-ownership findings.

No architecture selection was found. The 31 contiguous `BR-NNN` entries state outcomes, while the 14 `BQ-NNN` entries retain technology and engineering selection for I2R A&E. The source disposition matrix contains all `SRC-001` through `SRC-058` and `DEC-001` through `DEC-003` without an unmapped identifier.

## Gate decision

V3 cannot advance on RT2 because two source obligations are not fully expressed as testable BAIRD acceptance outcomes. Correct `RT2-BV3-F001` and `RT2-BV3-F002`, reseal the complete package, and rerun the three independent BAIRD reviews on the same revision.
