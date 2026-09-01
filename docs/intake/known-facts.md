# Known Facts

Each fact has a provenance tag. `STATED` means it appears in the authoritative assignment. `VERIFIED` means it was confirmed from an official TTB source. `DERIVED` means it follows mechanically from stated quantities and is not used as authority.

## Assignment and workflow facts

| Fact ID | Provenance | Fact | Source / note |
|---|---|---|---|
| `FACT-001` | STATED | The take-home requires all source code in a GitHub-or-similar repository. | `S-001`, Deliverables |
| `FACT-002` | STATED | The repository must include setup/run instructions and brief documentation of approach, tools, assumptions, and trade-offs/limitations. | `S-001`, Deliverables and evaluation guidance |
| `FACT-003` | STATED | A deployed application URL is required. | `S-001`, Deliverables |
| `FACT-004` | STATED | Evaluation emphasizes core correctness/completeness, code organization, technical choices, UX/error handling, attention to requirements, and creative problem-solving. | `S-001`, Evaluation Criteria |
| `FACT-005` | STATED | The assignment explicitly prefers a working clean core over ambitious incomplete features. | `S-001`, Evaluation Criteria note |
| `FACT-006` | STATED | The described operation reviews about 150,000 applications annually with 47 agents. | `S-001`, Deputy Director interview; not independently verified |
| `FACT-007` | DERIVED | The stated volume is about 3,191 applications per agent per year before accounting for uneven assignment or non-review duties. | `150,000 / 47`; context only |
| `FACT-008` | STATED | Simple reviews take roughly 5 to 10 minutes in the described current workflow. | `S-001`, Deputy Director interview |
| `FACT-009` | STATED | A prior scanning pilot reportedly took 30 to 40 seconds and was abandoned; results need to return in about five seconds for adoption. | `S-001`, Deputy Director interview |
| `FACT-010` | STATED | User technical comfort varies widely and the interface must be clean and obvious. | `S-001`, Deputy Director and Senior Agent interviews |
| `FACT-011` | STATED | Peak submissions may arrive in batches of 200 to 300 applications, creating demand for batch handling. | `S-001`, Deputy Director interview |
| `FACT-012` | STATED | The prototype is standalone and does not need direct COLA integration. | `S-001`, IT Administrator interview |
| `FACT-013` | STATED | The stakeholder scenario uses Azure, but the prototype has no mandated deployment platform. | `S-001`, IT Administrator interview |
| `FACT-014` | STATED | The stakeholder network may block outbound domains, so cloud API dependencies can be unavailable. | `S-001`, IT Administrator interview |
| `FACT-015` | STATED | Production would raise PII, retention, and federal compliance concerns, but the exercise is not expected to store sensitive information. | `S-001`, IT Administrator interview |
| `FACT-016` | STATED | Brand-name capitalization differences may be semantically insignificant and require human judgment. | `S-001`, `ASG-016`, `ASG-017` |
| `FACT-017` | STATED | The government warning is expected to match prescribed wording and uses special capitalization/bold treatment for its heading. | `S-001`, Junior Agent interview; verified below |
| `FACT-018` | STATED | Poor lighting, glare, and perspective can make label images difficult to read; support for these conditions is desirable but may be beyond core scope. | `S-001`, Junior Agent interview |

## Verified regulatory facts

| Fact ID | Provenance | Fact | Official source |
|---|---|---|---|
| `FACT-019` | VERIFIED | The federal health warning applies to alcohol beverages for U.S. sale/distribution containing at least 0.5% alcohol by volume. | [TTB health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) |
| `FACT-020` | VERIFIED | The warning's wording is prescribed; the `GOVERNMENT WARNING` heading must be uppercase and bold, while the remainder may not be bold. | [TTB health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) |
| `FACT-021` | VERIFIED | The warning must be separate from other information, appear as one continuous paragraph, be readily legible on a contrasting background, and satisfy container-size-dependent type-size and character-density rules. | [TTB health-warning guidance](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) |
| `FACT-022` | VERIFIED | Distilled-spirits brand name, class/type, and alcohol content must appear in the same field of vision. | [TTB mandatory distilled-spirits information](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label) |
| `FACT-023` | VERIFIED | Distilled-spirits labels also include other mandatory or conditionally mandatory information such as name/address, net contents, warning, and country of origin for imports. | [TTB distilled-spirits labeling](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling) |
| `FACT-024` | VERIFIED | Distilled spirits must state alcohol content as a percentage of alcohol by volume; proof may be additional when properly presented. | [TTB distilled-spirits alcohol content](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-alcohol-content) |
| `FACT-025` | VERIFIED | Wine requirements differ: for some 7% to 14% wines a qualifying “table wine” or “light wine” designation may replace a numerical alcohol statement, while wine over 14% requires a numerical statement. | [TTB wine alcohol content](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/labeling-wine/wine-labeling-alcohol-content) |
| `FACT-026` | VERIFIED | Wine has additional conditional requirements including appellation, percentage of foreign wine, color disclosures, and sulfite declaration. | [TTB wine labeling](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/labeling) |
| `FACT-027` | VERIFIED | Malt-beverage alcohol-content requirements can be conditional, and other category-specific declarations may apply. | [TTB malt-beverage mandatory information](https://www.ttb.gov/regulated-commodities/beverage-alcohol/beer/labeling/malt-beverage-mandatory-label-information) |

## What is not a fact yet

- no accuracy percentage is established;
- no OCR/model/library is selected;
- no hosting platform is selected;
- no actual COLA application data format is supplied;
- no representative production dataset is supplied;
- no OCR extraction accuracy percentage is established;
- no evidence supports comprehensive distilled-spirits compliance;
- batch feasibility and validated capacity are not established;
- no claim has been established that physical font size, boldness, or contrast can always be proven from an uploaded image.
