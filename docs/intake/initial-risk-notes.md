# Initial Risk Notes

| Risk ID | Risk | Likelihood | Impact | Why it matters | Initial mitigation / later proof |
|---|---|---|---|---|---|
| `RSK-001` | False clean pass from missing or low-confidence extraction | Medium | Critical | Misleads the agent and undermines the core compliance use case. | Fail closed to Review/Not verified; fixture invariant; explicit evidence; validation negative tests. |
| `RSK-002` | Scope expands into comprehensive legal label approval | High | Critical | Rules are beverage-specific, conditional, and larger than the take-home. | Selected-check attested scope; visible disclaimer; capability matrix; no approval language. |
| `RSK-003` | Five-second target missed, especially on cold start | Medium | High | Prior pilot adoption reportedly failed primarily on speed. | Benchmark candidate OCR paths early; measure cold/warm separately; strict input bounds; optimize primary path. |
| `RSK-004` | Cloud/API dependency blocked or unavailable | Medium | High | Stakeholder network may block outbound ML endpoints. | Prefer local-first or bounded fallback design; explicit timeout; degraded behavior; no hidden dependency. |
| `RSK-005` | Warning typography/size/contrast overclaimed | High | High | Image evidence may not prove physical or typographic facts. | Per-check evidence classes; Not verified when scale/visual confidence is absent; never collapse into blanket compliance. |
| `RSK-006` | Brand normalization creates false equivalence | Medium | High | Case/punctuation may be harmless, but aggressive normalization can hide a real difference. | Exact vs normalized status separation; transparent diff; human Review; field-specific normalization tests. |
| `RSK-007` | Batch consumes schedule and weakens core | Medium | High | Batch adds schemas, queue/progress, partial failure, output, and performance work. | Should-level objective only; gate after core; require an I2R A&E go/no-go and bounded proof. |
| `RSK-008` | Synthetic fixtures produce inflated accuracy claims | High | High | Generated labels are cleaner and less diverse than production data. | Label fixtures synthetic; include degradation variants; publish per-fixture results, not broad production accuracy. |
| `RSK-009` | Poor image quality creates unpredictable extraction | High | Medium | Glare, angle, blur, and missing panels are common enough to matter. | Input quality diagnostics; bounded preprocessing; actionable re-upload message; no hallucinated fields. |
| `RSK-010` | UI is too technical or visually dense | Medium | High | Intended users include infrequent/low-comfort technology users. | One primary action; progressive disclosure; plain reasons; keyboard/accessibility checks; user journey E2E. |
| `RSK-011` | Full all-category rules become inconsistent | Medium | High | Wine/malt requirements differ and may be conditional. | Explicit rule packs; dedicated fixtures; no generic requirement claim; narrow core if approved. |
| `RSK-012` | Deployed demo cold starts, exceeds memory, or leaks keys | Medium | High | Public URL is mandatory and often differs from local behavior. | Platform benchmark; secret scan; post-deploy smoke test; documented local fallback; no client-exposed secret. |
| `RSK-013` | Take-home reviewer cannot reproduce setup | Medium | High | Reproducibility is an explicit deliverable and code-quality signal. | Clean-checkout rehearsal; pinned versions; one-command start/test where practical; sample env and fixture. |
| `RSK-014` | Personal anecdotes from the assignment enter public artifacts | Low | Medium | They are unnecessary and weaken privacy/professionalism. | Data-minimized source brief; roles instead of personal details; repository review before publish. |
| `RSK-015` | Regulatory guidance changes after implementation | Low | Medium | Static rules can drift. | Source version/date metadata; centralized rules; limitations; no production legal claim. |
| `RSK-016` | The app presents AI confidence as truth | Medium | High | Numerical confidence can look authoritative without calibration. | Use confidence only to route Review/Not verified; explain evidence; no unsupported percent-accuracy claim. |
| `RSK-017` | Missing label panel is mistaken for a missing declaration or a clean label | Medium | Critical | Required evidence may be distributed across front, back, neck, or side panels. | Accept 1 to 6 panels; show coverage; absent evidence forces Review needed. |
| `RSK-018` | Fixture suite is cherry-picked or hard-coded | Medium | Critical | A take-home can appear correct without general rule behavior. | Independent manifest; 6 holdouts; extraction/comparison separation; mutation tests; per-fixture report. |
| `RSK-019` | Public uploads expose content through logs, temp files, analytics, or a provider | Medium | Critical | A public URL creates a real data boundary even for a prototype. | Threat model; synthetic-only notice; no raw-content logs; cleanup tests; provider disclosure; resource limits. |
| `RSK-020` | Malicious images or archives exhaust memory, CPU, or disk | Medium | High | Image decoders and optional batch inputs have decompression and resource-abuse risks. | Content sniffing; byte/pixel/time/concurrency limits; safe archive contract if batch ships; rate controls. |
| `RSK-021` | Accessibility promises are not testable | Medium | High | Mixed technical comfort and public evaluation require more than visual simplicity. | WCAG 2.2 AA targets; axe; keyboard; NVDA; 200 percent zoom; supported viewport matrix. |

## Cost-of-inaction note

The stakeholder cost of doing nothing is continued routine manual comparison and batch bottlenecks. That does not justify unsafe automation. The prototype succeeds by shifting routine evidence gathering left while preserving agent judgment.

## Risk acceptance boundary

Only the requester can expand scope into final compliance decisions, persistent data, production federal use, or mandatory all-category coverage. Engineering may mitigate risk inside the approved boundary but may not accept those risks by implementation choice.
