REWORK_REQUIRED

# BAIRD Red Team 3 Re-review

**Role:** Security, privacy, deployment, delivery, and traceability skeptic  
**Reviewed snapshot manifest SHA-256:** `02b68ffb8148f0880fa70b51135b062238a196eab8739894e141f66083381d71`  
**Review date:** 2026-08-31  
**Material findings:** 3 Medium  

## 1. Binary decision

The corrected architecture is substantially stronger and six of the eight original RT3 findings are closed at the architectural decision level. BAIRD is still not ready for I2R because three material proof and handoff gaps remain:

1. the trusted Fly client identity has no reserved public-edge spoof and duplicate-header acceptance test;
2. the selected no-store response policy has no explicit reserved acceptance test, and its remediation citation points to the CSRF test;
3. source and security-control ownership is not end-to-end, and several RT3 remediation citations point to unrelated requirements and tests.

These are not requests for implementation evidence before implementation exists. They are BAIRD requirements for an unambiguous, executable I2R handoff. Each can be corrected in the planning package without changing the selected product or architecture.

## 2. Snapshot verification

I verified the manifest before reviewing source and repeated the verification after the review:

| Check | Result |
|---|---|
| Manifest file SHA-256 | PASS, exact requested hash |
| Manifest entries | 45 |
| Missing listed files | 0 |
| Hash mismatches | 0 |
| `SOURCE_COVERAGE.csv` rows | 58, exactly `SRC-001` through `SRC-058`, no duplicates |
| Handoff control IDs | 12 ADR, 8 BG, and 18 THR, each present once |
| Reserved requirement/test IDs | 38 `R-NNN` and 38 `T-NNN`, no duplicate IDs |
| Prohibited Unicode dash scan | 0 matches |

Concurrent re-review outputs are intentionally outside the manifest. They did not change any of the 45 attested files.

## 3. Scope completed

I reviewed the complete Intake, all BAIRD documents, the full retained feasibility report and raw evidence, the research spike source and lockfile, the exact OCR model BOM, all three initial BAIRD RT reports, `SOURCE_COVERAGE.csv`, `BAIRD_CONTROL_HANDOFF_MATRIX.md`, `BAIRD_RT_REMEDIATION.md`, `README.md`, `AGENTS.md`, and `docs/PROCESS.md`.

The standard security scan covered ten surfaces: snapshot integrity, upload boundary, worker lifecycle, client identity and origin, runtime egress, model supply chain, privacy and caching, release provenance, control handoff, and scope or regulatory authority. It produced the same three Medium findings documented below.

## 4. Re-test of all eight original RT3 findings

| Original finding | Re-review result | Evidence and conclusion |
|---|---|---|
| `BAIRD-RT3-F001`, pre-parser limits | CLOSED | `SECURITY_DATA_FLOW.md:48-76` fixes actual received-byte enforcement before routing, malformed or missing length behavior, raw and file caps, part counts, field size, spool threshold and directory, pixel limits, sequential decode, and cleanup ownership. `THR-001` and `THR-002` map to `R-021/T-021` and `R-022/T-022`. |
| `BAIRD-RT3-F002`, killable work ownership | CLOSED at architecture, remediation citation correction required under RR3 | `ADR-007` and `ENGINEERING_BLUEPRINT.md:246-256` assign the slot, handles, request directory, and buffers to one child until result or confirmed exit. Timeout and shutdown terminate and join before cleanup or replacement. The authoritative rows are `R-007/T-007` and `R-028/T-028`, not the `R-023/T-023` MIME-spoof row cited by remediation. |
| `BAIRD-RT3-F003`, client identity and Origin/Host | OPEN | `SECURITY_DATA_FLOW.md:103-120` closes the topology and exact Host/Origin table. The remaining client-identity proof is not present in `THR-008`, `T-028`, or another reserved test. Remediation also cites `R-024/T-024`, which is the decoder-exploit row. See RR1 and RR3. |
| `BAIRD-RT3-F004`, Fly egress semantics | CLOSED | `ADR-012` accurately selects a directional allowlist policy with one deliberately unused TCP port, limits the claim to no external inference, model download, telemetry, DNS, HTTP, or HTTPS path, and explicitly rejects a claim of blocking every covert channel. Policy readback, DNS probes, direct-IP probes, and network capture map to `R-012/T-012`, `R-017/T-017`, and `R-033/T-033`. |
| `BAIRD-RT3-F005`, model rights and provenance | CLOSED at architecture, remediation citation correction required under RR3 | `MODEL_BOM.md:5-39` records the three exact files, ModelScope model-set version, byte counts, SHA-256 values, container paths, Baidu attribution, Apache notices, build-only fetch, runtime-download denial, offline readiness, and stop-on-rights-change rule. The supply-chain rows are `R-004/T-004` and `R-032/T-032`, not only `R-013/T-013` as remediation states. |
| `BAIRD-RT3-F006`, platform metadata and no-store | OPEN for test ownership | `SECURITY_DATA_FLOW.md:26-46` and `181-206` disclose Fly metadata and about-seven-day application-log search, prohibit content logs, and define browser cleanup. `SECURITY_DATA_FLOW.md:150-159` selects correct no-store headers. No reserved test explicitly owns no-store behavior across response classes and the deployed proxy path. See RR2 and RR3. |
| `BAIRD-RT3-F007`, immutable OCI promotion | CLOSED | `ADR-008`, `SECURITY_DATA_FLOW.md:163-177`, and the release checklist select one build, an immutable release tuple, exact image-digest promotion, Machine image-reference readback, safe `/api/v1/meta`, checksummed evidence, clean-browser smoke, and rollback digest. `R-008/T-008` blocks any tuple mismatch or mutable promotion. |
| `BAIRD-RT3-F008`, complete ownership and traceability | OPEN | Identifier presence is complete, but the required semantic ownership chain is not. `I2R_HANDOFF.md:86-88` requires every SRC, ADR, BG, and THR to have a requirement, component, test, stop gate, and owner in the control matrix. The matrix contains only ADR, BG, and THR rows. Many SRC rows terminate at prose artifacts, and remediation has multiple unrelated R/T citations. See RR3. |

## 5. Material findings

### RR1: Trusted client identity proof is not owned

**Severity:** Medium  
**Reopens:** `BAIRD-RT3-F003`  
**Files:** `SECURITY_DATA_FLOW.md:89`, `SECURITY_DATA_FLOW.md:103-107`, `BAIRD_CONTROL_HANDOFF_MATRIX.md:46`, `BAIRD_RT_REMEDIATION.md:45`

The selected topology reasonably trusts `Fly-Client-IP`, ignores `X-Forwarded-For`, has no additional proxy, and does not expose the internal port. Fly's current official request-header documentation says the HTTP handler adds `Fly-Client-IP` as the address accepted by Fly Proxy. It does not define in the BAIRD package how duplicate or client-supplied values are normalized at the ASGI boundary.

The original closure proof required spoofed forwarding headers not to change the limiter key. The current `THR-008` proof lists burst, abort storm, child count, CPU, and recovery. `T-028` lists burst, concurrency, abort storm, and recovery. Neither requires:

- a client-supplied `Fly-Client-IP` through the public edge;
- duplicate `Fly-Client-IP` values;
- arbitrary `X-Forwarded-For` or `X-Real-IP` values;
- malformed or multiple address values;
- proof that one normalized proxy-derived address, and only that address, selects the keyed limiter digest.

This report does not claim Fly's header is spoofable. It finds that the package has not preserved the exact acceptance proof required to rely on the header for the public CPU-abuse boundary.

**Required remediation:** Extend `THR-008` and `R-028/T-028`, or create an equally explicit reserved row, with the public-edge cases above. Fail closed on ambiguous or multiple trusted-header values. Correct the RT3 remediation evidence for F003 to reference the client-identity test plus `R-035/T-035` and `R-036/T-036` for Origin and CSRF.

### RR2: No-store response behavior has no explicit test owner

**Severity:** Medium  
**Reopens:** `BAIRD-RT3-F006`  
**Files:** `SECURITY_DATA_FLOW.md:150-159`, `I2R_HANDOFF.md:73-88`, `BAIRD_CONTROL_HANDOFF_MATRIX.md:52-54`, `BAIRD_RT_REMEDIATION.md:48`

The policy decision is correct: verification responses, evidence, and errors require `Cache-Control: no-store, private` and `Pragma: no-cache`. The I2R handoff also says the FRD cannot pass if no-store lacks tests.

The authoritative matrix does not name this behavior. `T-034` covers clickjacking and permissions headers. `T-035` covers Host and Origin. `T-036`, which the remediation map cites for F006, covers cross-site form/fetch CSRF. None explicitly checks cache headers or intermediary behavior.

Without an assigned test, the policy can be omitted from one error class or changed by the deployed proxy while the handoff still appears complete.

**Required remediation:** Assign no-store to a reserved requirement, response or middleware component, acceptance test, stop gate, and owner. The test must cover verification success, safe evidence, validation errors, decode errors, overload, timeout, and internal errors through the public Fly URL. Correct the F006 remediation citation.

### RR3: The source and security-control evidence graph is incomplete and mis-cited

**Severity:** Medium  
**Reopens:** `BAIRD-RT3-F008` and the evidence chain for F002, F003, F005, and F006  
**Files:** `SOURCE_COVERAGE.csv:1-59`, `BAIRD_CONTROL_HANDOFF_MATRIX.md:5-60`, `I2R_HANDOFF.md:86-88`, `BAIRD_RT_REMEDIATION.md:43-50`

The identifier check passes only at the presence level:

- `SOURCE_COVERAGE.csv` has all 58 SRC rows;
- the control matrix has all 12 ADR, 8 BG, and 18 THR rows;
- each matrix row has a reserved R, component, T, stop gate, and owner.

The end-to-end relation does not pass. `I2R_HANDOFF.md:87` requires every SRC, ADR, BG, and THR to have those fields in the authoritative matrix. The matrix has no SRC section. Thirty-one SRC rows in `SOURCE_COVERAGE.csv` contain no ADR, BG, or THR identifier that can be joined mechanically to the matrix. They point only to prose artifacts such as the UX spec, warning matrix, engineering sections, or I2R handoff. This includes core source statements for brand, ABV, warning, selected fields, structured reference input, accessibility, no-store-adjacent privacy, repository delivery, and documentation.

The remediation record also contains semantic reference errors:

| RT3 closure row | Citation in remediation | What that row actually proves | Required ownership direction |
|---|---|---|---|
| F002 worker lifecycle | `R-023/T-023` | MIME/extension/polyglot handling | `R-007/T-007` and `R-028/T-028` |
| F003 client identity and Origin | `R-024/T-024` | Malformed decoder corpus and resource bounds | client-identity proof plus `R-035/T-035` and `R-036/T-036` |
| F005 model provenance | `R-013/T-013` | 24-case field-family corpus | `R-004/T-004` and `R-032/T-032` |
| F006 logs and no-store | `R-030/T-030`, `R-036/T-036` | logs, then CSRF | `R-030/T-030` plus an explicit no-store response test |

This is material because I2R is instructed to consume these files as authoritative. A semantic mismatch can make an omitted control appear proven by an unrelated test.

**Required remediation:** Choose one machine-checkable contract:

1. add requirement, component/integration, test, stop gate, and owner columns to every SRC row; or
2. add all SRC rows to the control matrix; or
3. create a complete, validated SRC-to-control relation where every source joins to one or more authoritative ADR, BG, or THR rows.

Then add an automated relation check that rejects missing joins, orphan IDs, duplicate ownership, and remediation citations whose target row does not prove the named finding.

## 6. Current primary-source verification

The architectural conclusions above were rechecked against current primary sources:

- [Fly Network Policies](https://fly.io/docs/machines/guides-examples/network-policies/) states that once a rule exists for a direction, the default for that direction is deny-all and only explicit allow rules pass. It also recommends direct-IP tests to avoid DNS masking. This supports F004 closure and the package's deliberately limited claim.
- [Fly request headers](https://fly.io/docs/networking/request-headers/) defines `Fly-Client-IP` as the address accepted by Fly Proxy and warns that forwarding chains require care. This supports the selected topology but does not replace the missing public-edge duplicate and spoof test.
- [Fly logging overview](https://fly.io/docs/monitoring/logging-overview/) states that Fly collects application stdout/stderr and its search retains application logs for seven days. The package's content-free application logging and about-seven-day disclosure are supported.
- [RapidOCR 3.4.2 default model registry](https://raw.githubusercontent.com/RapidAI/RapidOCR/v3.4.2/python/rapidocr/default_models.yaml) lists the exact three selected ModelScope URLs and the same SHA-256 values recorded in `MODEL_BOM.md`.
- [RapidOCR](https://github.com/RapidAI/RapidOCR/tree/v3.4.2), [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), and the [RapidOCR ModelScope model](https://www.modelscope.cn/models/RapidAI/RapidOCR) support the recorded Apache 2.0 engineering/model distribution path and Baidu attribution. The project's notice and stop-on-rights-change controls remain necessary.
- [Fly private registry deployment](https://fly.io/docs/blueprints/using-the-fly-docker-registry/) and [Fly Machine resources](https://fly.io/docs/machines/api/machines-resource/) support prebuilt-image promotion and Machine `image_ref.digest` readback. The package correctly blocks release on any digest mismatch.
- [27 CFR 5.63](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-5/subpart-E/section-5.63), [27 CFR Part 16](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-16), and [TTB health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) continue to support the selected fields, warning wording and presentation rules, multi-panel evidence need, physical-size limitation, and non-comprehensive scope.

## 7. Precision observations that do not change the verdict

- `TECHNICAL_SOURCE_REGISTER.md` uses older Fly paths for network policy and logging. Replace them with the current official URLs cited above so future re-verification does not depend on redirects.
- `SECURITY_DATA_FLOW.md:37` combines Fly Proxy metadata processing with seven-day application-log retention in one row. Line 204 correctly separates them. Split the inventory row so it does not imply that every IP, user-agent, and request-path value is stored in application-log search when the application explicitly excludes them.

## 8. Re-review gate

RT3 can return CLEAR after one unchanged corrected snapshot proves all of the following:

1. public-edge trusted-client spoof and duplicate-header behavior has an explicit reserved test and stop gate;
2. no-store behavior has an explicit reserved test across every response class and the deployed proxy path;
3. all 58 SRC rows join to requirement, component, test, stop gate, and owner;
4. every RT3 remediation citation points to the semantically correct reserved rows;
5. automated relation checks pass along with the existing identifier, hash, and Unicode checks;
6. the other five RT3 closures remain unchanged.

BAIRD must remain open until this rework is complete and all three reviewers return CLEAR on the same corrected revision.
