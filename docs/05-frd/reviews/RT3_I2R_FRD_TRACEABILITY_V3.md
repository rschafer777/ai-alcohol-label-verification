CLEAR

# RT3 I2R and FRD Traceability Review V3

## Sealed snapshot verification

- Snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V3.sha256`
- Expected and observed SHA-256: `d86756843c9414978ad2e7cf995be72e4abbbf7b1ba2e2d4a416810a52155722`
- Entries: 50
- Missing entries: 0
- Hash mismatches: 0
- Prohibited U+2010 through U+2015 characters: 0
- Nested BAIRD V4 source seal: 38 entries, 0 missing, 0 mismatched

## Targeted V2 finding retest

| Finding | Result | Concrete evidence |
|---|---|---|
| Conflicting request-body deadlines | CLOSED | LV-I2R-002 Sections 6, 8, 9, and 13 consistently use the non-resetting 20 second body deadline. FR-008, FR-031, and FR-041 use the same 20/30/35 second composition. No active I2R or FRD authority retains the superseded 3 second body limit. |
| FRD authority excluded load-bearing contracts | CLOSED | LV-FRD-001 line 7 declares LV-I2R-001 through LV-I2R-008 plus `selected-check-registry-v1.json` as authority. FR-019, FR-020, FR-023, FR-024, and FR-025 cite the appropriate controlled contracts. |

## Original RT3 contract retest

| Contract | Result | Evidence |
|---|---|---|
| Resolvable evidence | CLOSED | LV-I2R-006 defines evidence identity, panel binding, original-pixel polygons, transforms, alternative ownership, referential failure, and test oracles. FR-023 and FR-024 own binary acceptance. |
| Total deadline and cancellation | CLOSED | LV-I2R-002 defines the 20 second upload, 30 second server, and 35 second browser bounds, one-second cancellation transition, abort race, supervisor ownership, and controlled stalls. Full decode and downstream work now run inside the killable child. FR-009, FR-029, and FR-041 require real decoder-stall termination, recovery, and zero leaked ownership. |
| Complete raw request ceiling | CLOSED | LV-I2R-002 separates 8,650,752 raw multipart bytes from 32 KiB reference JSON, 4 MiB per file, and 8 MiB aggregate file bytes, and defines Content-Length and streaming behavior. FR-008 and T-008 own every boundary. |
| Public-edge identity and response privacy | CLOSED | LV-I2R-002 Section 10 defines Fly client identity trust, forwarding-header rejection, private digesting, Host and Origin rules, security headers, and no-store behavior. FR-040 and T-040 own the direct, proxied, spoofed, malformed, isolation, and response-header matrix. |
| Normative errors | CLOSED | LV-I2R-007 defines server and browser codes, statuses, retryability, locators, actions, logging classes, and the unknown-error fallback. FR-025 and T-025 require exhaustive typed mapping and recovery. |

## Traceability and BI readiness

- BAIRD requirements: 31 of 31 reach I2R and FRD.
- BAIRD questions: 14 of 14 have selected I2R decisions.
- Architecture components: 16 of 16 reach the FRD.
- Feature requirements: 41 contiguous, unique Must rows.
- Test identifiers: 41 contiguous, unique tests paired to the 41 FRs.
- Product check registry: 19 unique checks, including independent warning contrast, legibility, and physical-size limitation rows.
- Each FR has upstream authority, component ownership, binary pass/fail acceptance, failure behavior, and a test identifier.
- Test layers, evidence types, coverage thresholds, negative tests, mutation tests, holdouts, accessibility, performance, delivery, and operational controls are assigned.
- Delivery obligations cover source, README, clean-checkout setup, approach, tools, assumptions, trade-offs, limitations, validation results, deployed URL provenance, and cross-artifact claim consistency.
- Exclusions remain explicit: no COLA integration, persistence, accounts, wine or malt rule packs, legal disposition, required external AI, batch release, unscaled physical-size certification, or mobile release claim.
- Known cold-start, deployed performance/configuration, license/notice, accessibility, and security evidence gaps remain explicit release-stop work. They are sized implementation and validation obligations, not unresolved requirements or architecture choices.

The source-to-BR-to-BQ/I2R-to-component-to-FR-to-test chain is complete enough for BI to create Epics, Stories, Tasks, sequencing, agent ownership, integration gates, and evidence packages without inventing product, interface, security, or acceptance policy.

## Gate decision

No material traceability, contract, delivery, or BI-readiness finding remains in the sealed V3 package. RT3 returns CLEAR.
