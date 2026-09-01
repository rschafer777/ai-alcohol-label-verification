REWORK_REQUIRED

# RT3 I2R and FRD Traceability Review V2

## Sealed snapshot verification

- Snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V2.sha256`
- Expected and observed SHA-256: `5d2fe2e62c5052bbb10f1e263946383c2674546e108dbdbb605586ba3c34c938`
- Entries: 44
- Missing entries: 0
- Hash mismatches: 0
- Prohibited U+2010 through U+2015 characters: 0

## Coverage and remediation verification

- BAIRD requirements: 31 of 31 reach I2R and FRD.
- BAIRD questions: 14 of 14 have selected I2R decisions.
- Architecture components: 16 of 16 reach the FRD.
- Feature and test pairs: 41 contiguous unique `FR-NNN` rows and 41 contiguous unique `T-NNN` references.
- Product check registry: 19 unique checks, including independent warning contrast, warning legibility, and warning physical-size rows.
- The first-time usability, release regulatory recheck, browser non-persistence, and OCR candidate-comparison remediations are present and test-owned.

Prior RT3 retest:

| Prior finding | V2 result | Evidence |
|---|---|---|
| Evidence contract | CLOSED | LV-I2R-006 defines resolvable evidence identity, panel binding, original-coordinate polygons, transform provenance, referential failure, and tests; FR-023 and FR-024 own it. |
| Total deadline and cancellation | NOT FULLY CLOSED | LV-I2R-002 Section 8 and FR-041 define the composed deadlines and races, but the governing threat table still asserts a contradictory 3 second upload deadline. See RT3-I2R-V2-F001. |
| Raw request ceiling | CLOSED | LV-I2R-002 Sections 1 and 6 define 8,650,752 complete request bytes separately from reference, per-file, and aggregate file limits; FR-008 and T-008 own the boundary cases. |
| Public edge, identity, security headers, and no-store | CLOSED | LV-I2R-002 Section 10 defines Fly identity trust, forwarded-header handling, Host and Origin behavior, response headers, and no-store; FR-040 and T-040 own the matrix. |
| Normative error model | CLOSED | LV-I2R-007 defines server and browser codes and mappings; FR-025 and T-025 require exhaustive contract coverage and the safe fallback. |

## Material findings

### RT3-I2R-V2-F001: The current security specification contains two different request-body deadlines

Severity: HIGH

Evidence:

- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:157` selects a non-resetting 20.0 second total request-body deadline.
- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:191-195` nests that 20 second deadline inside the 30 second server safety deadline.
- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:208` still defines the slow-body threat control as a non-resetting 3 second total body deadline.
- `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:30` and `:63` require the 20/30/35 second contract.
- `docs/05-frd/I2R_FRD_RT_REMEDIATION.md:10` claims the upload-envelope finding was resolved by replacing the old body deadline with 20 seconds.

Impact:

The same governing specification gives implementation and security-test authors incompatible values. A three-second control recreates the valid-upload feasibility failure that V2 claims to close. A 20-second control would contradict the threat table as sealed. BI cannot treat the deadline work package or its security acceptance as unambiguous.

Required remediation:

Replace the stale threat-table value with the selected 20 second value and explicitly point that row to Section 8. Scan all current authority documents for superseded 3 second implementation language, then reseal and rerun the gate.

### RT3-I2R-V2-F002: The FRD authority declaration excludes three contracts that its requirements depend on

Severity: HIGH

Evidence:

- `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:7` declares only LV-I2R-001 through LV-I2R-005 as architecture authority.
- FR-023 and FR-024 at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:45-46` depend on LV-I2R-006.
- FR-025 at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:47` depends on LV-I2R-007.
- The OCR selection and reopening gate are controlled by LV-I2R-008, while `docs/04-i2r-ae/05_I2R_REQUIREMENTS_TRACEABILITY.md:54-63` treats LV-I2R-006 through LV-I2R-008 as controlled resolutions.
- FR-019 and FR-020 at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:41-42` also depend on `selected-check-registry-v1.json`, which is not identified in the authority declaration.

Impact:

The FRD says its load-bearing evidence, error, OCR-selection, and check-registry sources are outside its declared architecture authority while using them for binary acceptance. A BI handoff that follows the declared authority can omit the exact contracts needed to size and implement FR-019, FR-020, FR-023, FR-024, FR-025, and related tests.

Required remediation:

Update the FRD authority declaration to include LV-I2R-001 through LV-I2R-008 and the versioned selected-check registry, or define an equally explicit controlled-authority list. Make the BI handoff require that full authority set and its hashes for every dependent Epic, Story, Task, and test package.

## Gate decision

The prior technical and UX remediations are otherwise detailed enough for BI decomposition, and the known cold-start miss is honestly preserved as a release-blocking FR-031 work item. Advancement remains blocked because one current safety value is contradictory and the FRD excludes its new load-bearing contracts from its own authority declaration.
