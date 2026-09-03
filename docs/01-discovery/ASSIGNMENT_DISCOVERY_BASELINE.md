# Assignment Discovery Baseline

## Product problem

TTB compliance agents review approximately 150,000 label applications each year. Much of the work consists of locating label text and comparing or checking predictable fields. A useful prototype must reduce repetitive reading while preserving human judgment for ambiguity and legal disposition.

## Stakeholder findings

| Stakeholder | Need captured |
| --- | --- |
| Compliance leadership | Typical results in about 5 seconds, a low-training interface, and batch support for peak-season deliveries of 200 to 300 products |
| IT administration | Standalone proof of concept, no COLAs Online integration, Azure-compatible packaging, local inference, bounded data handling, and no runtime dependence on outbound ML APIs |
| Senior reviewer | Capitalization and punctuation differences must preserve judgment, including `STONE'S THROW` versus `Stone's Throw` |
| Junior reviewer | Exact government warning wording and presentation matter; imperfect angles, glare, and lighting should be recovered when possible |
| Evaluator | Source code, setup and run instructions, approach, tools, assumptions, trade-offs, limitations, and an accessible deployed application |

## Product decisions established from discovery

- The normal workflow is label-first. The reviewer supplies images, OCR drafts the readable values, the rule engine checks the evidence, and the reviewer decides.
- A product accepts one to three label images so front, back, side, or neck evidence can be evaluated together.
- Beer or malt beverage, wine, and distilled spirits profiles are supported.
- Batch intake accepts up to 300 products and 900 images. The application suggests conservative image groups and requires human confirmation before processing.
- Batch folder intake skips unsupported files without blocking supported images and reports selection, processing count, rate, and estimated time.
- Results retain evidence locations, machine findings, reviewer disposition, and images in a 500-record FIFO history.
- The prototype uses local OCR and deterministic rule code. No cloud LLM or remote inference endpoint is required at runtime.
- Image quality alone is not a compliance defect. Readable evidence is evaluated; uncertain or absent evidence is routed to review or another-image request.
- Input errors state the submitted value, supported value, and exact corrective action when that information is measurable.

## Regulatory source baseline

The selected prototype rules are grounded in current official guidance and regulations:

- 27 CFR Part 16: health warning applicability, exact text, heading treatment, paragraph, separation, size, density, contrast, and legibility
- 27 CFR Part 4: wine labeling
- 27 CFR Part 5: distilled spirits labeling
- 27 CFR Part 7: malt beverage labeling
- TTB mandatory-label and anatomy guidance for wine, malt beverages, and distilled spirits

The versioned URLs and review date are maintained in `contracts/regulatory-rules-v1.json`.

## Delivery boundary

The prototype assists review. It does not issue a legal approval, replace agency judgment, or connect to COLAs Online. A versioned `/api/v1/verifications` interface accepts an independent reference record when a trusted application source becomes available; the shipped user interface does not ask the reviewer to retype that source.
