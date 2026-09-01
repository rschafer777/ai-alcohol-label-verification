# Batch and Federal Readiness Feature Requirements

Document control ID: LV-FRD-003  
Revision: 1.0  
Date: 2026-09-01  
Status: Active  
Authority: LV-BRD-002 and LV-I2R-010

This addendum supersedes the former batch NO-GO disposition in `FR-036`. The original 41 Must requirements remain active unless this document explicitly corrects them.

| ID | Priority | Requirement | Acceptance | Test |
|---|---|---|---|---|
| `FR-042` | Must | Provide separate, obvious One label and Batch entries without weakening the single flow. | A first-time user can identify both paths and the single path retains all prior behavior. | `T-042` |
| `FR-043` | Must | Import one UTF-8 `manifest.csv` and associated folder for 1 to 300 distilled-spirits applications. | Required and optional headers parse deterministically; quoted CSV values and Windows-selected folder paths work. | `T-043` |
| `FR-044` | Must | Reject absolute paths, traversal, duplicate or case-ambiguous paths, unknown or duplicate headers, unreferenced files, shared panel ownership, duplicate case IDs, more than 300 rows, and per-application limit violations. | Each hostile case returns a plain structural or row error before unsafe transport. | `T-044` |
| `FR-045` | Must | Retain one stable queue row for every nonblank manifest row. | Valid, invalid, failed, cancelled, and completed rows remain in manifest order and appear in exports. | `T-045` |
| `FR-046` | Must | Process valid rows sequentially through the existing endpoint with a 35-second browser deadline per row. | Measured peak browser request concurrency is one and a terminal row never executes twice without user retry. | `T-046` |
| `FR-047` | Must | Isolate row failures and provide progress, current case, elapsed time, rolling average, estimated remaining time, status filters, and detailed evidence. | One row error does not block later valid rows and every completed result opens the existing 19-check workspace. | `T-047` |
| `FR-048` | Must | Cancel safely and retry Error or Cancelled rows without repeating completed work. | Cancel aborts the active request, stops starts, preserves completed results, marks queued rows Cancelled, and selected retries succeed. | `T-048` |
| `FR-049` | Must | Export a formula-safe summary CSV and detailed JSON. | CSV neutralizes `=`, `+`, `-`, `@`, tab, and carriage-return prefixes; outputs include all rows; JSON contains inputs, 19 checks, reasons, evidence, timings, limitations, and errors. | `T-049` |
| `FR-050` | Must | Meet batch capacity and throughput gates. | Warm normal images target less than 5 seconds each, difficult recoverable images may take up to 9 seconds, and the complete batch targets a mean at or below 5 seconds per image. Warm 10 is at most 60 seconds, warm 20 is at most 110 seconds, warm 300 is at most 1,510 seconds, all valid normal-profile rows complete, no row is missing or duplicated, zero false clean results occur, and peak RSS is below 2 GiB. | `T-050` |
| `FR-051` | Must | Apply correct government warning physical-size and character-density tiers. | Boundary tests at 237 mL, 237.01 mL, 3 L, and 3.001 L select 1, 2, or 3 mm and 40, 25, or 12 characters per inch; unscaled images remain Not verified. | `T-051` |
| `FR-052` | Must | Preserve exact warning punctuation and reject title-case heading capitalization as a definite difference. | Word or punctuation mutation is Mismatch; `Government Warning:` is Mismatch; line joining cannot remove punctuation. | `T-052` |
| `FR-053` | Must | Attempt bounded recovery for low light, small-angle skew, and a clearly detected perspective trapezoid while preserving original evidence coordinates. | Controlled transform tests map evidence to original pixels. Angle, glare, curvature, low light, or partial framing is not itself a label defect. Recoverable visible evidence can clear its supported checks. Missing or unreadable mandatory evidence remains Review, Not verified, or requests another image. Only a visible deterministic defect becomes Mismatch, and degraded evidence never produces a false clean result. | `T-053` |
| `FR-054` | Must | Keep runtime inference local and independent of external ML endpoints. | Source and runtime tests show hash-verified local model loading and no required external inference call. Offline provisioning and network-level egress enforcement are reported separately. | `T-054` |
| `FR-055` | Must | Route case-only and punctuation-only brand variations to Review. | `STONE'S THROW`, `Stone's Throw`, and `STONES THROW` fixtures produce Review, not Mismatch or clean Match. | `T-055` |
| `FR-056` | Must | Provide a current federal authorization-start package. | Package contains path and scope intake, CPO and SDR human and JSON templates, secure configuration guidance, KSI evidence plan, assessment plan, risk register, continuous monitoring plan, shared responsibility matrix, and agency RMF handoff. | `T-056` |
| `FR-057` | Must | State technologies, assumptions, trade-offs, and limitations clearly in the root README. | Evaluator can understand the stack, local runtime, batch boundaries, warning confidence, image recovery limits, storage, COLA boundary, deployment evidence, and federal preparation without reading process documents. | `T-057` |

## Batch acceptance scenarios

| Tier | Required content | Time limit |
|---|---|---:|
| 10 | Clean, Review, Differences, Bad image, complete row accounting, detail opening, CSV, and JSON | 60 seconds |
| 20 | Row isolation, invalid row, import, six-panel row, cancellation, and retry | 110 seconds |
| 300 | Mixed deterministic states, stable ordering, no missing or duplicate rows, zero false clean, bounded memory | 1,510 seconds |

The performance test reports cold first-row readiness separately. It also verifies `(T20 - T10) / 10` and `(T300 - T20) / 280` are no more than five seconds per added row. Clean and difficult-image classes are reported separately so a slower recovery attempt is not hidden inside the batch mean.

## Definition of complete

The addendum is complete only when production code, focused tests, full regression, batch timing evidence, security checks, accessibility checks, UAT scripts, README claims, Validation Protocol, and three independent RTs agree on the same candidate.
