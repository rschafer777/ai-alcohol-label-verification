# Independent Fixture Allocation

**Decision:** The corpus is 30 end-to-end submissions: 24 development cases and 6 sealed holdouts. This exceeds the Intake minimum of 24 while preserving the required 6 sealed holdouts. The holdout expected outcomes are authored from the assignment and regulatory registry by a reviewer who does not inspect implementation constants.

Every active check appears in at least one positive and one negative or uncertain case. Overlap is intentional, but no single case is the only evidence for more than one field family.

| ID | Split | Panels | Principal coverage | Expected summary | Negative invariant |
|---|---|---:|---|---|---|
| `FX-001` | Dev | 1 | All domestic fields, exact warning, clear image | No differences found in checked fields | All active checks need evidence |
| `FX-002` | Dev | 3 | Fields split across front, side, and back panels | No differences found in checked fields | Panel order cannot drop evidence |
| `FX-003` | Dev | 6 | Maximum panel count with one field family per panel | No differences found in checked fields | Six panels cannot exceed working cap |
| `FX-004` | Dev | 1 | 12 MP source boundary and downscale with one safely uncertain OCR punctuation artifact | Review needed | Downscale cannot invent text or turn uncertainty into Match |
| `FX-005` | Dev | 1 | Brand capitalization variation | Review needed | Case difference cannot become automatic Match |
| `FX-006` | Dev | 1 | Brand semantically different by one word | Differences detected | Fuzzy similarity cannot create Match |
| `FX-007` | Dev | 1 | Class/type omission | Review needed | Missing class/type cannot be clean |
| `FX-008` | Dev | 1 | ABV matches reference while proof differs from reference and the two-times-ABV relationship | Differences detected | Matching ABV cannot hide wrong proof |
| `FX-009` | Dev | 2 | Expected ABV as promotional decoy, true field differs | Differences detected | Reference cannot select the decoy |
| `FX-010` | Dev | 1 | Net contents unit-equivalent representation | No differences found in checked fields | Unit conversion uses exact policy |
| `FX-011` | Dev | 2 | Competing net-content candidates | Review needed | Ambiguity cannot become Match |
| `FX-012` | Dev | 1 | Producer name/address mismatch | Differences detected | Address normalization cannot erase substance |
| `FX-013` | Dev | 2 | Imported spirits with matching origin | No differences found in checked fields | Conditional origin check is active |
| `FX-014` | Dev | 2 | Imported spirits with origin absent | Review needed | Missing conditional field cannot be clean |
| `FX-015` | Dev | 1 | Exact warning words and heading case | No differences found in checked fields | Canonical registry is versioned |
| `FX-016` | Dev | 1 | One warning word and punctuation mutated | Differences detected | Semantic closeness cannot create Match |
| `FX-017` | Dev | 1 | Title-case warning heading | Differences detected | Heading case is independently evaluated |
| `FX-018` | Dev | 1 | Glare plus blur over warning and producer | Review needed | Readable fragments cannot bypass quality |
| `FX-019` | Holdout | 4 | Unseen layout, all domestic fields | No differences found in checked fields | No layout-specific expected-value lookup |
| `FX-020` | Holdout | 2 | Expected brand appears only as a decoy in producer text while the true brand field differs | Differences detected | Brand candidate must use field role and cannot select the expected-value decoy |
| `FX-021` | Holdout | 3 | Small exact warning with uncertain emphasis evidence | Review needed | Unsupported emphasis cannot be implied Match |
| `FX-022` | Holdout | 1 | Clearly measurable warning body bold and heading not emphasized | Differences detected | Presentation checks aggregate when evidence is above the calibrated threshold |
| `FX-023` | Holdout | 6 | Maximum panels, one unreadable required panel | Review needed | Coverage gap cannot be clean |
| `FX-024` | Holdout | 2 | Imported origin differs, ABV and warning match | Differences detected | One Mismatch controls aggregate |
| `FX-025` | Dev | 1 | Brand punctuation-only variation | Review needed | Punctuation difference cannot become automatic Match |
| `FX-026` | Dev | 1 | Reference supplies proof but readable label omits proof | Review needed | Missing proof cannot be clean |
| `FX-027` | Dev | 1 | Two independently plausible proof candidates | Review needed | Ambiguous proof cannot be selected by reference value |
| `FX-028` | Dev | 1 | 0.4 percent ABV and no warning | No differences found in checked fields | Below-threshold warning detail is explicitly not applicable |
| `FX-029` | Dev | 1 | Exactly 0.5 percent ABV with exact warning | No differences found in checked fields | Threshold applicability is active |
| `FX-030` | Dev | 1 | Unparseable alcohol content and uncertain warning applicability | Review needed | Unknown applicability cannot be clean |

## Coverage counts

| Dimension | Allocated cases |
|---|---:|
| One panel | 19 |
| Two panels | 6 |
| Three or four panels | 3 |
| Six panels | 2 |
| Warning wording/case/presentation/applicability | 13 |
| Poor or insufficient evidence | 10 |
| Decoy or competing candidate | 3 |
| Import origin | 3 |
| Clean aggregate | 9 |
| Mismatch aggregate | 9 |
| Review aggregate | 12 |

## Oracle independence

- Fixture expected values are stored in a test-only manifest, not imported from application policy modules.
- Canonical warning truth is copied from the cited regulatory source into the fixture manifest and independently hash-reviewed.
- Holdout input images and expected outcomes are sealed before adapter or rule tuning begins.
- A mutation tool may derive negative images, but expected states are reviewed separately.
- No filename, fixture ID, image hash, or expected value may select an extraction result.
- The validation report separates decode, quality, OCR, location, parsing, comparison, and aggregation failures.

## Sufficiency decision

The allocation is sufficient for the selected take-home profile because every committed field family, proof branch, warning applicability boundary, warning state, panel boundary, quality boundary, and false-clean attack has independent evidence. If execution exposes a new error class or any holdout false clean, the corpus expands and the release gate remains closed.
