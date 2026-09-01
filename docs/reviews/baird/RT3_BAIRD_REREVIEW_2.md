REWORK_REQUIRED

# BAIRD Red Team 3 Re-review 2

**Role:** Security, privacy, deployment, delivery, evidence, and traceability skeptic  
**Review date:** 2026-08-31  
**Reviewed snapshot manifest:** `docs/reviews/baird/BAIRD_REVIEW_SNAPSHOT_V2.sha256`  
**Reviewed manifest SHA-256:** `0d80c9ffa7bb2e7d23d550b1639d7e9dc2c520b8e8500e264c71ecf1c0e1e29d`  
**Material findings:** 1 High and 3 Medium

## 1. Binary decision

The second corrected BAIRD package is not ready to advance to I2R. The prior trusted-client, no-store, and traceability gaps are closed. Exact model provenance, immutable release ownership, regulatory authority, and the limited deployment direction are also substantially stronger.

Four material issues remain:

1. public upload admission has no global pre-body concurrency or aggregate spool quota, so many clients can exhaust temporary storage and request capacity before the one-job OCR control applies;
2. the retained feasibility oracle checks only submission summaries, omits the committed proof check, returns an import-origin Match without evidence location, and contains at least one demonstrably wrong field result while still reporting every expected outcome correct;
3. the cold/readiness report says model hash verification was inside the measured readiness path, but the retained server source performs no model or rule hash check before declaring ready;
4. the Fly network policy is port based and deliberately permits one TCP port, so it cannot prove the stated absence of every HTTP, HTTPS, telemetry, or external-inference path.

These are BAIRD-level problems. They affect the public resource boundary, the evidence used to approve the selected architecture, and the truth of the runtime-egress claim. They must be corrected before I2R consumes the package as authoritative.

## 2. Snapshot and validation verification

I verified the sealed snapshot before review.

| Check | Result |
|---|---|
| Manifest SHA-256 | PASS, exact requested value |
| Parsed manifest entries | 95 |
| Missing listed files | 0 |
| Hash mismatches | 0 |
| Traceability validator | PASS |
| Source rows | 58, exactly `SRC-001` through `SRC-058` |
| Control rows | 12 ADR, 8 BG, and 18 THR |
| Reserved requirements and tests | `R-001` through `R-096` and `T-001` through `T-096` |
| Fixture allocation IDs | `FX-001` through `FX-025` |
| Prohibited Unicode dash scan | 0 matches |

The executed documentation gate returned:

```text
BAIRD_TRACEABILITY_VALID=True
SOURCE_ROWS=58
CONTROL_IDS=ADR12,BG8,THR18
REQUIREMENT_IDS=R001-R096
TEST_IDS=T001-T096
FIXTURE_IDS=FX001-FX025
PROHIBITED_UNICODE_DASHES=0
```

I independently recomputed the retained evidence summaries. The files contain 42 architecture rows at p95 3813.48 ms, 42 complete browser attempts at p95 3580.50 ms, and 5 cold trials with conservative p95 10287.61 ms. Those arithmetic summaries match the reports. The findings below concern what the evidence proves, not whether those numbers were copied incorrectly.

## 3. Review scope

I reviewed:

- the complete CLEAR Intake package and Intake review history;
- every current BAIRD document and ADR;
- all retained feasibility source, dependency locks, fixtures, raw JSON/CSV evidence, and evidence-validation records;
- all initial and first-round BAIRD red-team reports and the current remediation record;
- `SOURCE_COVERAGE.csv`, `BAIRD_CONTROL_HANDOFF_MATRIX.md`, `CONTROL_EVIDENCE_CITATIONS.csv`, and the executable traceability validator;
- upload, temp-file, identity, Origin/Host, CORS, CSRF, worker, cache, log, and error boundaries;
- Fly deployment, egress, resource, price, health, image, and release claims;
- RapidOCR package/model filenames, sources, hashes, rights, and notice controls;
- batch gating, repository deliverables, deployment provenance, and regulatory authority.

## 4. Attack cases

| Attack case | Expected BAIRD control | Result |
|---|---|---|
| Open many slow or full-size multipart uploads from different client identities | Global pre-body admission and bounded aggregate spool | FAIL, finding `RT3-V2-F001` |
| Fill `/tmp/labelverify` with many individually valid requests before OCR dispatch | Exact temporary-storage quota and aggregate byte ceiling | FAIL, finding `RT3-V2-F001` |
| Present matching ABV with inconsistent proof | Proof sub-check prevents a clean result | FAIL in retained slice, finding `RT3-V2-F002` |
| Ask whether each scenario reached the intended field states, not only the intended summary | Independent per-field expected manifest | FAIL, finding `RT3-V2-F002` |
| Inspect evidence for an imported country Match | Panel and region evidence or explicit defensible unavailability | FAIL in retained slice, finding `RT3-V2-F002` |
| Verify a title-case heading whose generated boldness remains correct | Heading case differs while emphasis rows remain correct or uncertain | FAIL in retained slice, finding `RT3-V2-F002` |
| Replace a selected model before cold readiness | Readiness rejects the wrong hash inside the measured path | NOT IMPLEMENTED in retained slice, finding `RT3-V2-F003` |
| Send HTTPS to an attacker endpoint on the deliberately allowed TCP port | Claim and test match actual port-policy semantics | FAIL, finding `RT3-V2-F004` |
| Supply, duplicate, join, or malform `Fly-Client-IP` at the public edge | Fail closed and preserve one normalized limiter key | PASS at design and reserved-test level |
| Return success or any public error through Fly | `no-store, private` and `no-cache` on every covered class | PASS at design and reserved-test level |
| Promote a mutable tag or mismatched release tuple | Release stops on digest/readback mismatch | PASS at design and reserved-test level |
| Accept ZIP or batch code before the core gate | Archive and batch paths remain absent | PASS |

## 5. Retest of the eight original RT3 findings

| Original finding | Result | Evidence and conclusion |
|---|---|---|
| `BAIRD-RT3-F001`, pre-parser upload limits | REOPENED | Per-request actual-byte, file, part, pixel, and spool controls are defined, but the original requested spool quota and a global pre-body admission bound are still absent. See `RT3-V2-F001`. |
| `BAIRD-RT3-F002`, killable work ownership | CLOSED | `ADR-007`, the worker blueprint, `R-007/T-007`, and `R-028/T-028` keep slot and artifact ownership with the child through actual exit or confirmed termination. |
| `BAIRD-RT3-F003`, client identity and Origin/Host | CLOSED | The Fly profile accepts exactly one valid `Fly-Client-IP`, ignores other forwarding headers, fails closed on ambiguous trusted values, and reserves the correct public-edge, Host, Origin, and CSRF cases in `T-028`, `T-035`, and `T-036`. |
| `BAIRD-RT3-F004`, Fly egress semantics | REOPENED | The directional allowlist semantics are documented correctly, but the remaining HTTP/HTTPS and telemetry claim is broader than a port-only policy with one allowed TCP port can prove. See `RT3-V2-F004`. |
| `BAIRD-RT3-F005`, model rights and provenance | CLOSED | The exact three files, versioned upstream paths, byte sizes, hashes, image paths, attribution, Apache notices, build-only fetch, runtime-download denial, and stop-on-change rule are recorded. Current primary sources match those identifiers. |
| `BAIRD-RT3-F006`, platform metadata and no-store | CLOSED | The data inventory separates proxy metadata from application-log retention. `THR-010` and `T-030` now cover content-free logs and public-Fly cache headers across success, evidence, validation, decode, overload, timeout, and internal-error responses. |
| `BAIRD-RT3-F007`, immutable OCI promotion | CLOSED | `ADR-008` and `T-008` bind source, locks, base image, OCI image, models, rules, fixtures, build, Fly deployment, Machine image readback, smoke result, and rollback digest. |
| `BAIRD-RT3-F008`, source/control ownership | CLOSED | Every SRC, ADR, BG, and THR has a requirement, component/integration, test, stop gate, and owner. The 96 reserved requirement/test pairs are complete, and the RT3 citation rows are now semantically aligned. |

## 6. Retest of prior re-review findings

| Finding | Result | Evidence |
|---|---|---|
| `RT3-RR1`, trusted client identity proof | CLOSED | `THR-008`, `R-028`, and `T-028` explicitly include supplied, duplicate, malformed, and comma-joined trusted-header values, arbitrary forwarding headers, limiter normalization, burst, abort storm, child count, and recovery. |
| `RT3-RR2`, no-store test ownership | CLOSED | `THR-010`, `R-030`, and `T-030` own no-store/private and no-cache proof through the deployed public URL for every listed response class. |
| `RT3-RR3`, semantic source and finding traceability | CLOSED | `SOURCE_COVERAGE.csv` gives each source a unique R/T pair and owner. The control matrix completes ADR/BG/THR ownership. `CONTROL_EVIDENCE_CITATIONS.csv` now cites the correct rows for all original RT3 and RR findings. The validator passes. |

## 7. Material findings

### `RT3-V2-F001`: Public upload admission and temporary storage remain globally unbounded

**Severity:** Medium  
**Reopens:** `BAIRD-RT3-F001`  
**Files:** `SECURITY_DATA_FLOW.md:54-76`, `SECURITY_DATA_FLOW.md:125-130`, `SECURITY_DATA_FLOW.md:169`, `ARCHITECTURE_DECISIONS.md:70-74`, `BAIRD_CONTROL_HANDOFF_MATRIX.md:39-47`

The package limits each request to 25,296,896 raw bytes and 24 MiB of encoded files. It spools each file after 1 MiB into a mode-0700 request directory. It also limits one client digest and one OCR job. Those controls do not bound how many requests can concurrently stream, parse, and spool before OCR admission.

An attacker can use many source addresses, or merely many first-seen identities, to open individually valid slow uploads. One Uvicorn process can accept many HTTP requests. The one-job OCR limit applies after the body and multipart work. The package does not select:

- a global in-flight POST admission count acquired before body consumption;
- a global request-start rate independent of client identity;
- a maximum aggregate number of spooled request directories or bytes;
- a filesystem or tmpfs quota for `/tmp/labelverify`;
- a bounded limiter-key table with TTL and maximum entries;
- an exact Fly `http_service.concurrency` hard limit or an application-level equivalent.

The current Fly documentation states that the default soft concurrency limit is 20 and that no hard limit is enforced unless configured. This means the selected host does not supply the missing global bound by default. See [Fly app configuration](https://fly.io/docs/reference/configuration/) and [Fly concurrency guidance](https://fly.io/docs/apps/concurrency/).

**Impact:** A distributed or rotating-source upload storm can exhaust temporary disk, file descriptors, parser work, or the event loop while every request stays within its individual limits. OCR process count can remain one while the public service still fails.

**Required remediation:**

1. Select a global admission cap for verification POSTs before any body byte is consumed. Health and static GETs need a separately justified allowance.
2. Select a bounded aggregate spool budget and maximum request-directory count. State the backing filesystem capacity and failure behavior.
3. Bound the keyed limiter map by TTL and maximum entries.
4. Configure and read back an exact Fly request hard limit, or document why an application pre-body gate is the controlling boundary. Do not rely on the platform default.
5. Extend `THR-001`, `THR-008`, and `THR-009` ownership so multi-client slow and full-size upload storms prove that admission, disk bytes, open files, parser tasks, and recovery stay within the selected envelope.

**Closure proof:** A public-edge test opens more than the selected number of uploads from multiple identities. Excess requests fail before body consumption, aggregate temp use never exceeds the documented ceiling, limiter state remains bounded, and the service returns to baseline without restart.

### `RT3-V2-F002`: The retained architecture evidence does not prove field-level correctness or complete committed coverage

**Severity:** High  
**Files:** `BAIRD_ASSESSMENT.md:87-101`, `BAIRD_ASSESSMENT.md:171`, `BAIRD_FEASIBILITY_REPORT.md:16-22`, `BAIRD_FEASIBILITY_REPORT.md:45-77`, `BAIRD_FEASIBILITY_REPORT.md:146`, `EVIDENCE_VALIDATION.md:7-20`, `ENGINEERING_BLUEPRINT.md:96-103`, `ENGINEERING_BLUEPRINT.md:181-189`, `source-requirements.md:12`, `research/baird-spike/spike.py:35-39`, `spike.py:118-125`, `spike.py:386-469`, `spike.py:510-518`, `browser_benchmark.py:29-65`

The BAIRD report says the selected proof check is active when the reference or label presents proof. The Intake source register requires ABV/proof fixtures under a documented policy. Every retained reference record includes `proof: 90`, and the generated labels display proof. The spike's `ACTIVE_CHECKS` set has no proof check, and `compare()` never returns a proof field. A label with matching 45 percent ABV and inconsistent 80 proof can therefore remain clean in this evidence path.

The retained expected manifest also stores only a submission-level expectation: clean, review, or differences. Both `spike.py` and `browser_benchmark.py` define `expected_correct` solely as summary equality. There is no independent expected field state, reason code, candidate, evidence location, or active-check applicability oracle for the 14 cases. The statement that all expected outcomes were correct therefore means only that each submission landed in the expected broad summary class.

Independent readback of `architecture-details.json` found two concrete consequences:

- all three `S10_import_origin` runs return country Match with `evidence_ref: null`, even though the selected field was observed and the feasibility report claims complete evidence;
- all three `S02_title_case` runs return Difference for both heading emphasis and body-not-bold in addition to the intended heading-case Difference. The generated source keeps `heading_bold=True` and `body_bold=False`, so these are wrong presentation results hidden by the correct overall Differences summary.

The raw payloads are useful, but retaining payloads is not the same as validating them. `EVIDENCE_VALIDATION.md` repeats the 42 of 42 claim without identifying that the oracle is summary-only.

**Impact:** `BG-001` is marked PASS on evidence that can omit a committed sub-check, approve a field without its location evidence, and contain wrong field results without failing. This weakens the architecture selection and directly risks false-clean or false-difference behavior in the exact comparison logic the assignment evaluates.

**Required remediation:**

1. Give every architecture case an independent per-field expected manifest covering applicability, state, reason family, and required evidence presence.
2. Add the proof relationship check to the slice whenever proof is present, including matching ABV with wrong proof and wrong ABV with misleading proof.
3. Preserve country candidates as full observed records with panel and region evidence, or return an explicit non-Match state when the evidence cannot be located.
4. Correct or conservatively route the title-case emphasis observations. A known-correct generated boldness condition cannot produce Difference and still count as expected-correct evidence.
5. Rerun architecture and browser evidence against the per-field oracle. Report field-level expected counts, mismatches, missing evidence, false clean, and false difference separately.
6. Keep the final 25-fixture independent release oracle, but do not use that future gate to excuse an incorrect BAIRD feasibility claim.

**Closure proof:** Every applicable field and warning row in every retained run matches an independently authored expected state and evidence-presence rule. Proof is exercised independently of ABV. No scenario passes because an unrelated row happens to produce the expected submission summary.

### `RT3-V2-F003`: The recorded cold/readiness clock omits the hash verification it claims to include

**Severity:** Medium  
**Files:** `BAIRD_FEASIBILITY_REPORT.md:42`, `BAIRD_FEASIBILITY_REPORT.md:93-104`, `ENGINEERING_BLUEPRINT.md:80`, `ENGINEERING_BLUEPRINT.md:226`, `ENGINEERING_BLUEPRINT.md:352`, `MODEL_BOM.md:32-39`, `research/baird-spike/server.py:26-39`, `server.py:68-79`, `server.py:112-124`, `cold_start_benchmark.py:69-126`

The feasibility report says model hash verification occurred before readiness and inside each process-spawn cold trial. The architecture requires readiness to fail until model and rule hashes pass.

The retained `worker_main()` constructs `RapidOCR`, creates a contact sheet, performs one inference, and sends `type: ready`. It never hashes a model, compares a file to `MODEL_BOM.md`, checks model writability, or verifies a regulatory registry digest. The parent sets `app.state.ready = True` immediately after that message. `cold_start_benchmark.py` measures the process honestly, but it measures the source that omits the claimed checks.

`architecture-metadata.json` records model hashes from a separate `spike.py` run. That record identifies the environment but does not prove that each cold server process verified the selected artifacts before becoming ready.

**Impact:** The cold evidence is not measured against the selected readiness contract, and the report overstates its security and provenance boundary. The local cold result already misses the target by 287.61 ms, so even a small omitted step must not be hidden.

**Required remediation:** Add exact detector, recognizer, classifier, and registry hash checks to the retained readiness path, fail closed on absence/mismatch/writability, rerun the five process-spawn trials, and update the cold report without changing the honest PASS or NOT CLOSED interpretation.

**Closure proof:** A wrong model hash prevents readiness, the successful cold clock includes the checks, and raw cold evidence identifies the verified digests for each run.

### `RT3-V2-F004`: The Fly egress claim is broader than the selected port policy

**Severity:** Medium  
**Reopens:** `BAIRD-RT3-F004`  
**Files:** `ARCHITECTURE_DECISIONS.md:106-112`, `BAIRD_ASSESSMENT.md:16`, `BAIRD_ASSESSMENT.md:114`, `SECURITY_DATA_FLOW.md:89-91`, `SECURITY_DATA_FLOW.md:104`, `SECURITY_DATA_FLOW.md:173-176`, `BAIRD_CONTROL_HANDOFF_MATRIX.md:20`, `BAIRD_CONTROL_HANDOFF_MATRIX.md:51`, `TECHNICAL_SOURCE_REGISTER.md:73`

Fly network policies are transport protocol and destination-port allowlists. Once an egress rule exists, other egress is denied. The selected workaround deliberately permits one otherwise unused TCP port so that default-deny behavior is activated.

The package then claims that the deployed core has no HTTP, HTTPS, telemetry, model-download, or external-inference path. That does not follow from a port-only policy. HTTP and TLS can run on any permitted TCP port. An external endpoint controlled by an attacker or dependency can listen on the deliberately allowed port. This is ordinary permitted TCP traffic, not merely a theoretical covert channel.

The current [Fly Network Policies documentation](https://fly.io/docs/machines/guides-examples/network-policies/) describes allow rules by TCP/UDP port and states that unlisted traffic is denied. It does not perform application-protocol inspection. DNS and direct-IP probes to conventional ports can prove those ports are denied, but they cannot prove all HTTP/HTTPS or telemetry paths are absent while another TCP port is open.

**Impact:** The architecture, privacy statement, threat control, and release test can all pass while one declared external TCP channel remains available. This is a narrower risk than unrestricted egress, but it contradicts the stated protocol-level claim and the original compromised-process attack case.

**Required remediation:** Choose one truthful contract:

1. state that Fly policy denies all egress except exact TCP port `N`, and specifically denies conventional DNS 53, HTTP 80, and HTTPS 443 destinations; disclose that arbitrary application traffic can still use port `N`; or
2. select a platform or enforceable mechanism that actually provides the stronger no-egress property.

In either case, name the allowed port, explain why it is needed, probe that port, and make `T-012`, `T-017`, and `T-033` prove exactly the narrowed property. Do not use protocol names when the control sees only transport protocol and destination port.

**Closure proof:** The architecture wording, threat model, public privacy statement, network-policy readback, and probes state and prove the same exact port-level property. No broader egress claim remains.

## 8. Current primary-source verification

- [Fly Network Policies](https://fly.io/docs/machines/guides-examples/network-policies/) confirms directional allowlist behavior and default deny after a rule exists. It also confirms that rules are transport protocol and port based and do not affect Fly Proxy traffic.
- [Fly request headers](https://fly.io/docs/networking/request-headers/) confirms `Fly-Client-IP` is the address accepted by Fly Proxy and warns about forwarding-chain spoofing. The corrected exact-one-value test contract is appropriate.
- [Fly app configuration](https://fly.io/docs/reference/configuration/) confirms request concurrency can have a `hard_limit` and that no hard limit is enforced when it is unset. This supports finding `RT3-V2-F001`.
- [Fly Machine resources](https://fly.io/docs/machines/api/machines-resource/) exposes `image_ref.digest`, supporting immutable deployed-image readback.
- [Fly private registry deployment](https://fly.io/docs/blueprints/using-the-fly-docker-registry/) supports prebuilt-image promotion and post-deploy image reference inspection.
- [RapidOCR 3.4.2 default model registry](https://raw.githubusercontent.com/RapidAI/RapidOCR/v3.4.2/python/rapidocr/default_models.yaml) contains the exact selected detector, recognizer, and classifier hashes recorded in `MODEL_BOM.md`.
- [RapidOCR ModelScope model page](https://www.modelscope.cn/models/RapidAI/RapidOCR) currently identifies the model repository as Apache License 2.0. The package correctly retains RapidOCR, PaddleOCR, and Baidu attribution plus a stop-on-rights-change rule.
- [27 CFR 5.63](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-5/subpart-E/section-5.63), [27 CFR Part 16](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-16), and [TTB health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) continue to support the selected field inventory, same-field-of-vision limitation, warning text and presentation rules, and physical-scale limitation. The non-comprehensive authority wording remains correct.

## 9. Controls that are ready for I2R after remediation

The following decisions should be preserved:

- one same-origin modular monolith with no COLA integration;
- reference-blind observation and primary candidate selection;
- deterministic rules and fail-closed aggregation;
- one killable OCR child with true-exit ownership;
- exact RapidOCR package and model BOM with build-time hash verification;
- no database, external inference dependency, analytics, or intentional content persistence;
- exact Fly trusted-client and Host/Origin decision tables;
- response no-store ownership across public success and error classes;
- immutable OCI promotion and complete release tuple;
- selected-check distilled-spirits scope with current official authority and no legal-approval claim;
- batch held behind every core release gate;
- complete 58-source and 38-control handoff with 96 reserved requirement/test pairs;
- repository, all-source, README, brief-documentation, public-URL, clean-checkout, and deployed-provenance deliverables.

## 10. Re-review gate

RT3 can return CLEAR only after one new sealed snapshot proves all of the following:

1. global pre-body admission, aggregate spool quota, limiter-state bound, and multi-client upload-storm tests are explicit;
2. the retained architecture slice has an independent per-field oracle, includes proof, preserves country evidence, and has no known wrong field result counted as correct;
3. cold readiness performs the exact model and registry hash checks claimed by the report and the evidence is rerun;
4. Fly egress wording and tests describe only the exact port-level property the selected policy enforces, or a stronger enforceable host is selected;
5. all prior RT3 and RR closures remain intact;
6. the manifest, relation validator, evidence hashes, and Unicode scan pass again on the same revision;
7. all three BAIRD reviewers return CLEAR on that identical snapshot.

Until those conditions are met, BAIRD remains open and I2R must not begin.
