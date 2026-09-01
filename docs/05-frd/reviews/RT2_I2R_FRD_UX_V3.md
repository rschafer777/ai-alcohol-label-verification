CLEAR

# RT2 I2R and FRD UX Review V3

Review role: stakeholder, user experience, and evaluator-fit red team  
Reviewed snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V3.sha256`  
Expected and observed manifest SHA-256: `d86756843c9414978ad2e7cf995be72e4abbbf7b1ba2e2d4a416810a52155722`  
Manifest entries: 50  
Hash verification: 50 matched, 0 missing, 0 mismatched  
Unicode U+2010 through U+2015 scan: 0 findings in the sealed snapshot

## V2 finding retest

### RT2-I2R-FRD-V2-F001 - CLOSED

The recovery contract is now consistent and binary:

- The UX contract preserves form values and selected browser files after inference timeout when safe and after user cancellation at `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:45-53`.
- Start over opens a confirmation whenever browser work exists. Cancel leaves all work unchanged, and Confirm clears all current browser state at `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:121-123`.
- `FR-025` requires retryable failures to preserve reference values and selected files and to recover without re-entry at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:47`.
- `FR-027` makes the full Start over confirmation, Cancel, Confirm, and already-clean behavior binary at line 49.
- `FR-041` makes cancellation preserve editable form and file work while retaining safe server ownership and cleanup at line 63.

These outcomes preserve low-tech recovery without creating persistence or weakening the result-free error invariant.

### RT2-I2R-FRD-V2-F002 - CLOSED

All active I2R and FRD contracts now use the same non-resetting 20 second request-body deadline:

- the selected limits and composed deadline appear at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:149-201`;
- the slow-body threat-control row now states 20 seconds at line 209;
- the required slow multipart test uses 20 seconds at line 277; and
- `FR-008`, `FR-031`, and `FR-041` use the same 20/30/35 second composition at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:30,53,63`.

References to the rejected 3 second value remain only in sealed historical review and remediation records. They are not current implementation authority.

## Earlier RT2 closure regression

- First-time usability remains binary through `FR-037` and `T-037`, with two independent no-instruction sessions covering Try sample and the complete manual workflow.
- The authoritative registry still contains 19 unique aggregating checks. Warning contrast, warning legibility, and warning physical size remain separate.
- `FR-019`, `FR-020`, and `FR-023` require independent warning rows, honest Not verified or human-confirmation behavior, evidence, and complete rendering.
- No old 17-check evidence file controls the product registry. The architecture identifies it as legacy research and requires new 19-check fixture proof.

## Focused regression and BI readiness

- Sarah's speed and simplicity objectives remain represented through the five-second normal profile, obvious sample and manual paths, plain processing and recovery states, and no batch release work.
- Dave's judgment boundary remains intact through Review handling for case, punctuation, ambiguity, and immutable machine evidence.
- Jenny's warning requirements remain explicit, independently testable, and honest about image-based physical-size limits.
- IT constraints remain represented through no COLA integration, no required inference egress, bounded public upload controls, no intentional persistence, content-free logs, and explicit cleanup.
- The evaluator path remains public, unofficial, synthetic-data-first, accessible, documented, and backed by binary setup, performance, evidence, privacy, and delivery acceptance.
- Evidence identity, error mapping, cancellation ownership, browser non-persistence, performance profiles, cold-start disclosure, accessibility, and Grok/Gemini adoption and rejection decisions show no material regression.
- The modular monolith remains proportional to the take-home. It adds no accounts, database, durable queue, batch interface, external inference dependency, or production federal claims.
- The FRD contains 41 contiguous `FR-NNN` requirements and 41 contiguous `T-NNN` identifiers. All 31 BAIRD requirements and all 16 I2R components remain covered.
- Known build and release work, including cold-start improvement, deployed performance, final 19-check fixtures, accessibility, security, clean checkout, configuration readback, and licenses, is explicit and test-owned. These are BI work items and release gates, not unresolved architecture or UX decisions.

## Material findings

None.

## Gate decision

The combined I2R and FRD V3 package is stakeholder-faithful, user-safe, internally consistent, binary enough for implementation planning, and free of material architecture overbuild. RT2 clears this exact sealed revision for BI after the other independent reviewers also return CLEAR on the same snapshot.
