REWORK_REQUIRED

# RT3 I2R and FRD Delivery and Traceability Review V1

## Reviewed seal

- Snapshot: `docs/05-frd/I2R_FRD_SNAPSHOT_V1.sha256`
- Expected and observed manifest SHA-256: `d2203fcfc94fd469d2855f50d9af291780014c751ce7dcaf8c51f1144b6f81c4`
- Manifest entries: 32
- Missing entries: 0
- Hash mismatches: 0
- Prohibited U+2010 through U+2015 characters in the sealed files: 0

The structural chain is complete: 31 of 31 BRs reach I2R and FRD, all 14 BQs have I2R dispositions, all 16 components reach the FRD, and the FRD contains 36 unique requirements with 36 unique tests. The following semantic gaps are material because BI would otherwise have to invent interface, timeout, or public-edge policy.

## Material findings

### RT3-I2R-F001: Verification evidence references cannot be resolved

Severity: HIGH

Evidence:

- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:62-92` defines `evidenceRef` values in checks and alternatives but defines no evidence collection or evidence object.
- `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:97-101` requires polygons from extraction and browser focus of each evidence region.
- `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:73` requires a selected field to choose its source panel and outline its evidence polygon.
- `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:45-46` requires every evidence action, including alternatives, to focus the exact region.

Impact:

The server and browser contracts cannot be implemented independently from the sealed specification. An engineer must invent how an `evidenceRef` resolves to a panel, polygon, coordinate space, source view, and alternative. T-023 and T-024 cannot have a deterministic contract oracle.

Required remediation:

Define the evidence object and reference rules in LV-I2R-002. At minimum, specify stable ID uniqueness, panel binding, polygon point type and order, original-image coordinate space and bounds, derived-to-original transform provenance, optional text/confidence exposure, alternative ownership, missing evidence behavior, and referential-integrity failure behavior. Update FR-023, FR-024, T-023, and T-024 to test schema validation, invalid references, coordinate mapping, and distinct ambiguity alternatives.

### RT3-I2R-F002: BQ-009 does not close the total timeout and cancellation contract

Severity: HIGH

Evidence:

- The BAIRD question at `docs/03-baird/01_BAIRD_INTAKE_VALIDATION.md:142` requires exact input, resource, concurrency, timeout, and cancellation limits.
- The claimed BQ-009 answer at `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:141` lists an upload deadline and worker deadline but no complete request safety deadline or client cancellation limit.
- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:133-135` specifies 3.0 seconds for request body receipt, 200 ms for worker acquisition, and 6.25 seconds for worker execution. It does not bound validation, decode, preprocessing, response transfer, or browser rendering as one failure path.
- `docs/04-i2r-ae/01_I2R_ARCHITECTURE_ENGINEERING.md:68` assigns cancellation to C-005 without defining its trigger, client abort time, UI behavior, or server race contract.
- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:150-154` correctly defines server ownership after disconnect, but does not close the client-visible cancellation contract or a maximum Verify-to-terminal-state failure duration.
- FR-007, FR-025, and FR-029 cover processing, error rendering, and cleanup, but none owns the missing total bound and cancellation behavior.

Impact:

The selected sub-deadlines can be implemented correctly while a decode or client request still waits without a specified terminal bound. Frontend, API, worker, recovery, and performance stories cannot share one testable timing budget. This also leaves BR-011 and the restricted-network bounded-failure outcome partially unproven.

Required remediation:

Define one exact Verify-activation-to-terminal-state safety contract, or an exact composed budget that bounds every sequential phase. State the client abort deadline, user cancellation availability, server behavior after disconnect, response-versus-abort race behavior, cleanup ownership, and the distinction between valid-result performance and failure timing. Add a dedicated FR and test with controlled stalls in upload, validation/decode, queue, inference, transfer, and render/announcement.

### RT3-I2R-F003: Selected ingress limits omit the normative raw request ceiling

Severity: HIGH

Evidence:

- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:10-17` specifies the 24 MiB aggregate encoded file payload but not the maximum complete multipart body including boundaries, headers, and the reference part.
- The selected control table at `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:129-141` also omits a raw body byte ceiling.
- FR-008 at `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:30` explicitly requires the selected raw-body limit, but no governing I2R value exists for the test to assert.
- The retained feasibility implementation at `research/baird-spike/server.py:29-32` distinguishes `RAW_REQUEST_LIMIT = 25_296_896` from the 24 MiB file-payload limit. That value was not promoted into the normative I2R contract.

Impact:

The production parser and T-008 must choose an unstated safety limit. Using 24 MiB as both limits would reject some otherwise valid 24 MiB file payloads due to multipart overhead. Omitting the raw limit would weaken the proven pre-parser memory and spool boundary.

Required remediation:

Promote an exact complete-request byte ceiling into LV-I2R-002, distinguish it from aggregate file bytes and reference bytes, and define behavior for missing, duplicate, invalid, understated, and oversized `Content-Length`. Make FR-008 and T-008 cite and test that value at the pre-body and streaming-overflow boundaries.

### RT3-I2R-F004: Public-edge identity and response privacy controls have no executable FR contract

Severity: HIGH

Evidence:

- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:136-138` defines per-client limits and a bounded key table but does not define the client identity source behind Fly.io or the Azure fallback, the trusted proxy boundary, spoof resistance, or missing/malformed identity behavior.
- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:170` says strict allowed Host/Origin policy and secure headers, but gives no allowed-value algorithm, method behavior, status/error contract, or required header set.
- No FR or test owns proxy identity, Host validation, Origin validation, or response security headers. FR-008 tests resource limits, while FR-029 tests logs and cleanup.
- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:122-125` treats verification results as request-scoped browser data, but the I2R and FRD define no `Cache-Control: no-store` contract for verification responses and errors.

Impact:

Per-client protection may collapse all public users into one proxy identity or trust a spoofable header. Cross-origin and Host handling can differ by engineer or deployment. Verification text and findings can be cached contrary to the stated request-scoped privacy posture. These are release controls, not optional implementation details.

Required remediation:

Define the canonical client identity derivation for each approved host, the exact trusted proxy configuration, normalization and digest rules, and fail-safe behavior for absent or malformed identity. Define allowed Host and Origin evaluation for the mutation route, explicit response status/code, the required security header set, and `Cache-Control: no-store` behavior for verification responses and errors. Add a dedicated FR/test matrix for direct and proxied requests, spoofed forwarding headers, invalid Host/Origin, missing Origin cases, identity isolation, rate-limit isolation, and response headers.

### RT3-I2R-F005: The typed error contract has no normative error taxonomy

Severity: HIGH

Evidence:

- `docs/04-i2r-ae/02_I2R_DATA_INTERFACE_SECURITY.md:45-58` provides a generic error shape but no allowed machine codes, HTTP statuses, field/panel locator rules, retryability values, or next-action mapping.
- `docs/05-frd/01_FEATURE_REQUIREMENTS_DOCUMENT.md:47` names error families and requires stable codes, retryability, and recovery, but does not define the values T-025 must assert.
- `docs/04-i2r-ae/03_I2R_UX_WORKFLOW.md:45-54` defines user-facing categories without binding them to API codes and statuses.

Impact:

The API and UI teams cannot implement or test a shared typed error model without making independent policy decisions. T-008, T-009, T-011, T-025, T-028, and T-029 can disagree while each appears locally correct.

Required remediation:

Add a normative error registry that maps every validation, admission, rate, upload, decode, queue, readiness, inference, cancellation/disconnect-delivery, and internal failure to HTTP status, stable code, locator applicability, retryability, public message/next-action class, result-free invariant, and logging class. Reference the registry from the affected FRs and tests and require unknown internal failures to use one safe fallback.

## Gate decision

The package is not ready for BI Epic, Story, and Task sizing. Counts, upstream source coverage, exclusions, delivery obligations, cold-start disclosure, and Unicode compliance are sound, but five load-bearing contracts remain undefined. Advance only after all five findings are closed in the I2R and FRD and the sealed review is rerun.
