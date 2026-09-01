# Coding and Documentation Standards

Document control ID: LV-BI-004  
Revision: 1.0  
Date: 2026-09-01  
Status: Candidate for BI review

## 1. Governing principles

- Prefer readable, typed, deterministic code over clever abstraction.
- Keep business rules out of routes and UI components.
- Treat contracts, registries, errors, and limits as single governed sources.
- Comments explain intent, safety, or a non-obvious trade-off. They do not restate code.
- No production result depends on fixture names, expected outputs, or research artifacts.
- No unsupported accuracy, compliance, official-affiliation, or production-scale claim appears in code or documentation.

## 2. Naming

| Area | Standard |
|---|---|
| Python modules/packages/functions/variables | `snake_case` |
| Python classes, enums, Pydantic models | `PascalCase` |
| Python constants | `UPPER_SNAKE_CASE` |
| TypeScript variables/functions/hooks | `camelCase`, hooks begin with `use` |
| TypeScript components/types/interfaces | `PascalCase` |
| Frontend feature folders and non-component files | lowercase `kebab-case` |
| Tests | behavior name plus requirement ID where useful, such as `test_t022_mismatch_precedence` |
| Stable identifiers | Existing `SRC`, `DEC`, `BR`, `BQ`, `ADR`, `C`, `FR`, `T`, `WP`, `TASK`, `UAT`, and defect conventions |
| Public product name | `LabelVerify` |

Do not invent agency names, seals, case numbers, or official account identities for visual realism.

## 3. Python standards

- Python 3.12, full type annotations on public and domain boundaries.
- Pydantic models only at external/configuration boundaries. Pure domain code uses typed standard structures where practical.
- Ruff for format/lint and MyPy or Pyright for strict backend type checks.
- No blocking OCR or full image decode on the ASGI event loop.
- Use `Decimal` for alcohol and volume comparison values.
- Use explicit enums and reason codes, not magic strings.
- Catch exceptions only where they can be translated, cleaned up, or safely recovered.
- Never include user text, filenames, image content, paths, or IP addresses in logs.

## 4. TypeScript and React standards

- Strict TypeScript with no implicit `any` and no unsafe contract casts.
- Functional components and focused hooks.
- Server result state is immutable and never recomputed in the browser.
- Separate remote result, editable intake, viewer state, and session-only reviewer state.
- Every asynchronous path has explicit idle, validating, submitting, processing, complete, cancelled, and error handling.
- Use semantic HTML first. ARIA supplements semantics and does not replace them.
- Status never relies on color alone.
- No localStorage, sessionStorage, IndexedDB, service worker content cache, analytics, or crash SDK.

## 5. Contract and registry standards

- The API version is `/api/v1`.
- Result/error schema changes require backend and frontend contract tests in the same work package.
- The 19-check registry order and identifiers are stable.
- Every applicable check appears once, and non-applicable checks remain explicit when the contract requires them.
- Unknown error codes map to the safe result-free `internal_error` behavior.
- Evidence polygons use four clockwise original-image pixel points and a deterministic first point.
- Runtime limits are configuration-backed but cannot exceed cleared maximums without stage review.

## 6. Tests and code review

- A defect fix includes a failing regression test before closure.
- Test expected outcomes are not imported from production comparison code.
- Holdout content and expected outcomes are controlled by `VV-LEAD`.
- Deterministic tests do not use network services or current time without a controlled clock.
- Flaky tests are failures. Do not hide them with unbounded retries.
- Review checks requirement mapping, correctness, failure behavior, privacy, accessibility, dependency direction, test independence, and documentation.
- Generated lockfiles and SBOMs are reviewed as build outputs, not hand-edited.

## 7. Documentation and file control

- Markdown uses short sections, direct language, tables only when they clarify exact mappings, and ASCII punctuation.
- U+2010 through U+2015 characters are prohibited everywhere, including copied source text, UI copy, comments, snapshots, and release notes.
- Human-facing final artifacts belong inside the numbered project folders. Transient scripts, patches, and ad hoc reports do not belong in Documents.
- Documentation states observed evidence separately from future plans.
- Historical research must be labeled historical and cannot override current I2R/FRD authority.
- README commands are copied from passing automation and verified in a fresh environment.

## 8. Security and dependency control

- Exact Python and npm lockfiles are required.
- OCR models are fetched only during controlled image build, hash-verified, and never downloaded at runtime.
- Runtime executes as non-root with a read-only application filesystem and bounded private spool.
- Secrets are supplied only through deployment configuration and never committed.
- Dependency, license, container, secret, and known-vulnerability scans are release gates.
- No Git initialization, remote, publication, or deployment occurs until requester authorization.

## 9. Completion hygiene

Before a work package is marked complete:

1. format, lint, type, and focused tests pass;
2. requirement/test IDs are recorded;
3. no debug code, hidden bypass, dead branch, sample hard-coding, or stale result remains;
4. privacy and Unicode scans pass on changed files;
5. evidence and limitations are updated;
6. a non-owning role completes code review.
