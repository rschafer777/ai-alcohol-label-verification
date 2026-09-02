# Local Release Candidate Status

Document control ID: LV-REL-002  
Revision: 2.5  
Date: 2026-09-01  
Status: Azure deployment candidate under renewed RT; composite INCOMPLETE

## 1. Current conclusion

The source, README, numbered lifecycle documentation, governed fixtures, validation evidence, lockfiles, SBOMs, model manifest, container source, and deployment template form a complete local review package. Single-label and client-managed batch workflows are implemented. Current local gates include 197 passing Python tests, 46 passing frontend tests, 30 of 30 product-corpus cases, 456 of 456 expected check rows, 8 of 8 mutations, zero false-clean results, and a successful 300-application sequential capacity run. The later user-supplied 50-image automatic-clear recognition gate remains failed at 0 of 14 selected-profile visual passes, despite containing all 17 known defects with zero false clearances and zero false deterministic rejections. Three independent final RTs returned APPROVED_WITH_KNOWN_GATE after the active release records, public index, and staged-byte manifest were corrected. The Azure runtime-font correction requires a new immutable RT snapshot and public workflow proof before final submission status can pass.

The pre-Azure source candidate received three independent RT verdicts. Source publication and clean-checkout replay are complete. Initial deployment run `33561343127` stopped before job startup because `astral-sh/setup-uv` was outside the repository's allowed-action policy, so it made no Azure changes. Run `33565168381` then reached the Linux quality gate and exposed writable POSIX model assets plus platform-dependent fixture raster hashes before any Azure authentication. Model acquisition now enforces read-only POSIX permissions. Fixture generation separately proves same-toolchain byte repeatability, complete generated-corpus hash and seal integrity, exact reference and oracle identity, and content-sensitive cross-platform visual equivalence with an adversarial blank-image control. Run `33568696374` passed every Python, frontend, build, and browser test, then exposed that the final Unicode scan depended on `rg`, which is not installed on the Ubuntu runner. The scan now uses checkout-provided Git against every tracked file. Run `33570716009` passed all source gates and exposed only the GitHub-to-Azure immutable-subject mismatch. The corrected credential allowed run `33572176211` to pass OIDC and registry authentication before the container build identified an omitted root contract in the frontend stage. Run `33573352505` built and deployed the corrected container, then exposed RapidOCR's attempted runtime font download during warmup. The application now supplies a governed local DejaVu Sans font. The workflow adds the immutable image to the private registry, runs that exact digest locally, and requires explicit readiness output before the serving Container App resource can change. The deployment workflow receives the omitted personal-detail terms from a non-public environment value and repeats the exact-archive scan against the committed public tree before any image build or Azure authentication. The corrected Azure change must receive a new three-reviewer RT decision, then the dispatch-only workflow must prove OCI construction, privacy, effective configuration, and public behavior. Requester UAT and final submission approval remain separate. The local official-source release recheck passed on 2026-09-01.

## 2. Required take-home deliverables

| Assignment deliverable | Local status | Location or closure path |
|---|---|---|
| All source code | COMPLETE | `backend/`, `frontend/`, `contracts/`, `ops/`, `scripts/` |
| README setup and run instructions | COMPLETE | `README.md` |
| Approach, tools, and assumptions | COMPLETE | README plus `docs/intake/`, `docs/04-i2r-ae/`, and `docs/10-release/DEPENDENCY_AND_MODEL_INVENTORY.md` |
| Test and validation evidence | INCOMPLETE | `docs/08-validation/` and `docs/09-qa-qc-uat/`; the 50-image automatic-clear recognition gate fails and external environment gates remain explicit |
| Source repository URL | AVAILABLE | `https://github.com/rschafer777/ai-alcohol-label-verification` |
| Deployed application URL | AUTHORIZED, EVIDENCE PENDING | The dispatch-only Azure workflow must complete before the URL is represented as live |

## 3. Candidate strengths

- Single-label and batch paths are implemented through one comparison contract and one local OCR worker.
- The workflow is optimized for exception review and low technical comfort.
- Local OCR avoids the stakeholder's blocked outbound endpoint risk.
- The evidence model distinguishes exact differences, safe equivalence, ambiguity, missing evidence, and unsupported physical measurement.
- The complete 19-check result prevents silent omission.
- Security, privacy, accessibility, performance, and failure behavior are tested as release properties.
- Documentation preserves the complete Discovery-to-delivery decision chain without presenting research artifacts as current authority.

## 4. Known limitations

- No direct COLAs Online integration.
- Batch is session-only and sequential. It has no ZIP ingestion, persistent queue, resume-after-refresh behavior, background scheduler, or multi-user coordination.
- No accounts, saved cases, durable audit record, or server-side reviewer decisions.
- OCR and image heuristics can require human review, especially with glare, blur, perspective, or small typography.
- The current user-supplied 50-image diagnostic automatically clears none of the 33 visually compliant images. It avoids false clearances and false deterministic rejections by routing them to review, so automatic clear recognition requires further work.
- Pixel evidence cannot always establish physical type size, character density, or font weight.
- Production OCI and deployed-edge behavior remain unproven until the authorized GitHub workflow completes.

## 5. Remaining release sequence

1. Freeze the Azure deployment candidate and obtain three independent RT verdicts.
2. Configure the GitHub `demo` environment and dispatch the workflow from `main`.
3. Validate the public URL, OCI identity, effective Azure configuration, and deployed behavior.
4. Update the README and release evidence to the proven deployment revision, then rerun regression and RT.
5. Present the deployed candidate to the requester for code review and UAT.
6. Improve automatic-clear recognition without introducing false clearances or false deterministic rejections, or obtain requester acceptance of the documented review-only limitation before final submission approval.
