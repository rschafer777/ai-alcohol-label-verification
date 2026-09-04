# Requirements Traceability Matrix

Document ID: LV-TRACE-001

| Intake | Design | Feature | Implementation | Verification |
| --- | --- | --- | --- | --- |
| INT-001 to INT-003 | Single product flow and optional application comparison | FR-001 to FR-003 | `frontend/src/app/App.tsx`, `frontend/src/features/intake/ApplicationDetails.tsx`, analysis and verification routes, `backend/labelverify/domain/reference_search.py` | Frontend component tests including the application comparison test, reference-search tests, API tests, browser UAT |
| INT-004 to INT-006 | Classification and rule activation | FR-007 to FR-013 | pipeline, domain engine, contract registries | Beverage-profile tests, contract tests |
| INT-007 | Warning engine | FR-014 to FR-016, FR-022 | warning and candidate modules | Domain warning tests, synthetic fixtures, governed visual oracle diagnostic |
| INT-008 | Human judgment | FR-018 | comparison engine | Case and punctuation tests including STONE'S THROW |
| INT-009 to INT-010 | Image and evidence design | FR-005, FR-006, FR-019 to FR-021 | imaging, OCR adapter, review workspace, evidence viewer | Imaging tests, evidence mapping tests, viewer zoom, pan, and view-switcher tests, browser UAT |
| INT-011 | Separate disposition | FR-023, FR-035 | review UI and history repository | UI and history tests |
| INT-012 to INT-014 | Batch architecture | FR-025 to FR-031 | batch filtering, per-image reads, grouping service, confirmation, queue, and exports | Mixed-folder tests, grouping tests, grouping-step guidance tests, private full-corpus API and grouped-product gate, capacity browser test, export review |
| INT-015 to INT-016 | FIFO history | FR-032 to FR-037 | history repository, routes, workspace | Repository, API, UI, and browser history tests |
| INT-017 | Sample | FR-038 | sample routes and adapter | Sample integration and browser UAT |
| INT-Q-001 to INT-Q-002 | Performance budgets | FR-041 to FR-043, FR-047 to FR-048 | bounded OCR recovery, exact-pixel bounded reuse, strict equivalent-panel deduplication, separate safety timeout, sequential queue | Local individual, grouped-product, equivalent cross-format multi-panel, warm, cold, and deployed timing protocols |
| INT-Q-003 | Local inference | FR-004 | local model manifest and runtime | Asset hash tests and network dependency review |
| INT-Q-004 | Accessibility | FR-024, FR-039 | semantic React components and CSS | Testing Library, Playwright, keyboard and visual review |
| INT-Q-005 | Fail-safe uncertainty | FR-017 | aggregation and warning rules | Negative, bad-image, ambiguity, and mutation tests |
| INT-Q-006 | Security | FR-040 to FR-041, FR-046 | boundary, supervisor, history repository, container, deployment | Security tests, isolation tests, dependency audit, security scan |
| INT-Q-007 | Traceability | FR-044 | metadata and documentation set | Contract tests, release review, RT gate |
| INT-Q-008 | Deployed performance parity | FR-049 | 4-vCPU and 8-GiB ARM template plus effective-configuration readback | Deployment contract tests and live uncached image timing |
