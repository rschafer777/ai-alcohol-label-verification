# Regulatory Source Register

**Verified:** 2026-09-01

This register records official TTB guidance used to frame the prototype. It does not claim to replace the regulations, legal review, or a current TTB labeling checklist.

| Source ID | Official source | Facts used | Prototype implication |
|---|---|---|---|
| `REG-001` | [Distilled Spirits Labeling](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/labeling) | Mandatory and conditional distilled-spirits information, including brand, class/type, alcohol content, warning, name/address, net contents, and import origin | Grounds the selected profile inventory while showing that the profile is not comprehensive |
| `REG-002` | [Mandatory Distilled-Spirits Label Information](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-brand-label) | Brand, class/type, and alcohol content share one field of vision | A single uploaded panel may be insufficient to verify all mandatory information; the UI must expose coverage limits |
| `REG-003` | [Distilled-Spirits Health Warning](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-health-warning) | Warning applicability, prescribed text, heading case/emphasis, paragraph, separation, type-size bands, character density, contrast, and legibility | Split warning into independent checks; do not claim physical size from an unscaled photo |
| `REG-004` | [Distilled-Spirits Alcohol Content](https://www.ttb.gov/regulated-commodities/beverage-alcohol/distilled-spirits/ds-labeling-home/ds-alcohol-content) | Percent alcohol by volume is required; proof may be additional | Compare normalized percentage values; treat proof as a cross-check rather than a substitute |
| `REG-005` | [Wine Labeling](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/labeling) | Wine has category-specific and conditional statements | Full wine support needs a dedicated rule pack and fixtures |
| `REG-006` | [Wine Alcohol Content](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/labeling-wine/wine-labeling-alcohol-content) | Numerical alcohol statements are conditional in part of the 7% to 14% range and mandatory above 14% | A generic “ABV required for every label” rule is incorrect for full wine support |
| `REG-007` | [Wine Sulfite Declaration](https://www.ttb.gov/regulated-commodities/beverage-alcohol/wine/wine-labeling-declaration-of-sulfites) | Sulfite declaration depends on measured sulfur dioxide | The image alone cannot decide the underlying threshold; application/reference data is required |
| `REG-008` | [Malt-Beverage Mandatory Information](https://www.ttb.gov/regulated-commodities/beverage-alcohol/beer/labeling/malt-beverage-mandatory-label-information) | Malt-beverage alcohol and disclosure requirements can be conditional | Full malt support needs its own rule pack and reference fields |
| `REG-009` | [27 CFR 5.63, Mandatory label information](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-5/subpart-E/section-5.63) | Current eCFR authority lists same-field-of-vision and other mandatory spirits information plus additional conditional disclosures | Confirms that the selected profile covers only an enumerated subset and requires multi-panel evidence |
| `REG-010` | [27 CFR Part 16, especially 16.10, 16.21, and 16.22](https://www.ecfr.gov/current/title-27/chapter-I/subchapter-A/part-16) | Current eCFR authority defines covered beverages, prescribed warning text, placement, capitalization, emphasis, contrast, density, and size | Canonical warning rules must cite the regulation as well as TTB guidance and preserve physical-evidence limits |

## Rule implementation guardrails

- Store every implemented rule with a source ID and last-verified date.
- Keep canonical warning text in a centralized, test-covered rule source, not scattered UI strings.
- Separate application-versus-label matching from label-only regulatory checks.
- Separate deterministic failure from image-quality uncertainty.
- Do not infer facts that require formula, lab, container, or application evidence from pixels alone.
- Do not describe prototype coverage as complete TTB compliance.
- Re-verify official sources before final release.
- Record the eCFR displayed-current date separately from the project retrieval date because eCFR is continuously updated and authoritative but unofficial.

## Release source recheck

The release recheck was completed on 2026-09-01 against the official TTB health-warning guidance, the official TTB mandatory distilled-spirits checklist, and current 27 CFR Part 16. The TTB health-warning page reports a last-updated date of 2025-11-19. The TTB checklist reports a last-updated date of 2026-05-27. The eCFR page displayed Title 27 as current through 2026-08-28 and last amended on 2026-08-17. The recheck found no change that requires a modification to the prototype's selected distilled-spirits profile, prescribed warning text, heading capitalization and emphasis checks, non-bold body rule, paragraph rule, contrast rule, or size-band evidence limits.

This dated recheck closes the local regulatory-source release action. The official sources remain controlling, and any later production release requires another current-source review.

## Future FRD requirement

The FRD must produce a check-capability matrix with, at minimum:

| Check | Evidence required | Machine-verifiable | Human confirmation | Not verifiable from arbitrary image |
|---|---|---|---|---|
| Warning wording | OCR text plus canonical source | Yes, when readable | Review low-confidence text | No |
| Heading capitalization | OCR text and region | Usually | Review OCR ambiguity | No |
| Heading boldness | Region typography evidence | Heuristic | Yes | Sometimes |
| Remaining text not bold | Region typography evidence | Heuristic | Yes | Sometimes |
| Separation/paragraph | Layout regions | Heuristic | Yes | Sometimes |
| Contrast/legibility | Image quality and region | Heuristic | Yes | Sometimes |
| Physical type size | Container volume plus reliable image scale | Rarely | Yes | Usually |
