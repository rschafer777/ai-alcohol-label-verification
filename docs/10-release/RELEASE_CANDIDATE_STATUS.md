# Local Release Candidate Status

Document control ID: LV-REL-002  
Revision: 2.6  
Date: 2026-09-01  
Status: Azure performance correction pending proof; composite INCOMPLETE

## 1. Current conclusion

The source, README, numbered lifecycle documentation, governed fixtures, validation evidence, lockfiles, SBOMs, model manifest, container source, and deployment template form a complete local review package. Single-label and client-managed batch workflows are implemented. Current local gates include 197 passing Python tests, 46 passing frontend tests, 30 of 30 product-corpus cases, 456 of 456 expected check rows, 8 of 8 mutations, zero false-clean results, and a successful 300-application sequential capacity run. The later user-supplied 50-image automatic-clear recognition gate remains failed at 0 of 14 selected-profile visual passes, despite containing all 17 known defects with zero false clearances and zero false deterministic rejections. Run `33577226574` proved the complete protected source, privacy, OCI, Azure, and one-attempt public smoke path. Independent UAT then reproduced a two-panel timeout on the 1 vCPU profile. The active correction assigns 2 vCPU and 4 GiB and requires three consecutive public sample passes with a mean below 5 seconds and no attempt at or above 9 seconds before final deployment evidence can pass.

The pre-Azure source candidate received three independent RT verdicts. Source publication and clean-checkout replay are complete. Initial deployment runs closed action-policy, Linux portability, Unicode-scan portability, OIDC-subject, container-build, and runtime-font failures without bypassing their controls. Run `33577226574` then completed the protected workflow and established the first live URL. Independent UAT did not rely on that single success. It exposed the Azure CPU mismatch and reopened the deployed-performance gate. The active workflow still adds only an immutable image to the private registry, proves that digest locally before resource mutation, receives omitted personal-detail terms from a non-public environment value, and repeats the exact-archive scan before Azure authentication. Requester UAT and final submission approval remain separate. The local official-source release recheck passed on 2026-09-01.

## 2. Required take-home deliverables

| Assignment deliverable | Local status | Location or closure path |
|---|---|---|
| All source code | COMPLETE | `backend/`, `frontend/`, `contracts/`, `ops/`, `scripts/` |
| README setup and run instructions | COMPLETE | `README.md` |
| Approach, tools, and assumptions | COMPLETE | README plus `docs/intake/`, `docs/04-i2r-ae/`, and `docs/10-release/DEPENDENCY_AND_MODEL_INVENTORY.md` |
| Test and validation evidence | INCOMPLETE | `docs/08-validation/` and `docs/09-qa-qc-uat/`; the 50-image automatic-clear recognition gate fails and external environment gates remain explicit |
| Source repository URL | AVAILABLE | `https://github.com/rschafer777/ai-alcohol-label-verification` |
| Deployed application URL | LIVE, PERFORMANCE CORRECTION PENDING | The URL is live, but the corrected 2 vCPU three-run public performance gate must pass before final submission evidence is complete |

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
- One immutable OCI and deployed-edge workflow completed, but repeated public two-panel performance remains unproven on the corrected Azure profile.

## 5. Remaining release sequence

1. Commit and dispatch the corrected 2 vCPU Azure candidate from `main`.
2. Require the effective-configuration readback and three consecutive public sample performance checks to pass.
3. Repeat independent browser and public API UAT.
4. Update the README and release evidence to the proven deployment revision, then rerun regression and three independent RTs.
5. Present the deployed candidate to the requester for code review and UAT.
6. Improve automatic-clear recognition without introducing false clearances or false deterministic rejections, or retain it as an explicit human-review limitation for the take-home submission.
