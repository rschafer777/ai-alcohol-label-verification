# Regulatory Validation Record

Document ID: LV-REG-001  
Source review date: 2026-09-03  
Status: Every selected rule re-verified against the current primary source

The take-home instructions ask that the prototype check the label elements TTB requires and
that the government health warning be verified word for word, with "GOVERNMENT WARNING:" in
capital letters and bold type. This record lists every rule the application applies, the
primary source it was verified against on the review date, what the application implements,
and where the implementation lives. Sources are the Electronic Code of Federal Regulations
(eCFR, mirrored by Cornell LII on the review date) and TTB.gov guidance pages.

## Government health warning (all beverage types)

| Rule | Source (verified 2026-09-03) | Implementation | Status |
| --- | --- | --- | --- |
| Applies to every alcoholic beverage at or above 0.5 percent alcohol by volume | 27 CFR 16.10 and 16.20; TTB wine labeling health warning page | `warning_applicability`: an alcohol value at or above 0.5 percent requires the statement. Without a readable value, wine and distilled spirits are treated as required because both families are above the threshold by definition, and a malt beverage with a recognized class designation and no non-alcoholic statement is treated the same way | Implemented, `backend/labelverify/domain/warnings.py` |
| Exact text: "GOVERNMENT WARNING: (1) According to the Surgeon General, women should not drink alcoholic beverages during pregnancy because of the risk of birth defects. (2) Consumption of alcoholic beverages impairs your ability to drive a car or operate machinery, and may cause health problems." | 27 CFR 16.21 | `warning_wording`: the read is compared word for word with the statute. An exact read is a match; letter case and spacing are not differences because 16.22 fixes the case of the heading only and OCR invents spacing around the clause markers; a clause number fused to the next word ("1According") is an unresolved marker bracket, an OCR signature no label prints. Any other punctuation difference is a review item that names the marks in question, never cleared by the machine, because a photograph cannot settle it. A missing sentence, a statutory word dropped from the middle of a cleanly read statement ("women should drink"), replacement language, or clear word substitutions that outnumber the OCR slips in the read are differences; a read peppered with slips, or truncated at either end, goes to review | Implemented, `warnings.py`, `normalize.py` |
| "GOVERNMENT WARNING" in capital letters | 27 CFR 16.22(a)(2) | `warning_heading_uppercase`: exact uppercase heading is a match, title or mixed case is a difference | Implemented |
| "GOVERNMENT WARNING" in bold type | 27 CFR 16.22(a)(2) | `warning_heading_emphasis`: stroke width (area over half perimeter) divided by letter height (upper quartile of connected-component heights, which lands on capitals and ascenders and ignores parentheses, dots, and commas) is measured for the heading and each body line on the OCR view. A heading at least 1.3 times the body's weight ratio is bold; a heading at 1.05 or less is no heavier than its body, which means either it is not bold or the body is, and goes to review; a ratio between the two is inconclusive and goes to review. The ink-density heuristic decides only when the type is too small to measure. Type weight read from a photograph is never on its own a rejection | Implemented as a measured visual check |
| Remainder of the statement may not appear in bold type | 27 CFR 16.22(a)(2) | `warning_body_not_bold`: the same measurement from the body's side; a body clearly lighter than its heading is regular, a body as heavy as its heading is reported as bold for the reviewer, an inconclusive ratio goes to review | Implemented as a measured visual check |
| Readily legible under ordinary conditions, on a contrasting background | 27 CFR 16.22(a)(1) | `warning_contrast`: two independent measurements must agree, the WCAG 2.x relative-luminance ratio between ink and background (fail below 3.0, pass at 4.5 or more) and the raw gray-level range inside the boxes; both low over at least two lines of measurable type is a difference, both clear is a match, disagreement is review. When the measurements are unavailable (type too small, or boxes without a luminance reading) the older ink-density heuristic can support a pass or ask for review but never rejects. `warning_legibility` uses OCR signal strength | Implemented as measured visual checks |
| Separate and apart from all other information; continuous paragraph | 27 CFR 16.21 and 16.22(b); TTB guidance | `warning_separation` measures the box gap between the statement block and the nearest neighbouring text in units of the statement's line height: three quarters of a line height or more of clear space is separate (visibly more than the ordinary spacing between lines of one paragraph), a quarter line height or less is adjoining and goes to review, and the band between, which includes text set at ordinary line spacing directly above or below the statement, goes to review; `warning_continuity` detects unrelated text between the two numbered clauses and rejects only inside a cleanly read statement; a read that skipped or garbled lines (a curved surface) cannot show what was printed between the clauses and goes to review | Implemented; separation never rejects on its own because OCR box padding is not ink |
| Type size: at least 1 mm for containers of 237 mL or less, 2 mm above 237 mL up to 3 L, 3 mm above 3 L; at most 40, 25, and 12 characters per inch respectively | 27 CFR 16.22(b) and (c) | `warning_physical_size` states the applicable minimum for the read net contents. An unscaled photograph cannot yield millimeters, so the row is reported for the reviewer and does not count against the machine summary | Implemented as an informational row |

## Distilled spirits (27 CFR part 5)

| Rule | Source | Implementation | Status |
| --- | --- | --- | --- |
| Brand name, class or type designation, and alcohol content in the same field of vision | 27 CFR 5.63(a); TTB distilled spirits mandatory label information page | `spirits_field_of_vision`: the three fields must be located on the same submitted panel | Implemented |
| Alcohol content as percent alcohol by volume; only "alc" and "vol" abbreviations; "ABV" not authorized | 27 CFR 5.65(a); TTB distilled spirits alcohol content page | `abv`: statement parsed from the label; "ABV" as the abbreviation is a difference | Implemented |
| Proof optional, in the same field of vision as the percentage and in parentheses, brackets, or otherwise distinguished; proof equals twice the percentage | 27 CFR 5.65(a); TTB page | `proof`: compared with twice the alcohol by volume, must share the panel with it; a separate "80 PROOF" term beside the percentage is accepted as distinguished with a note to confirm by eye | Implemented |
| Name and address of the bottler, distiller, or importer; net contents; country of origin for imports | 27 CFR 5.63(b), 5.66 to 5.70, 5.67 | `producer`, `net_contents`, `country` | Implemented |

## Wine (27 CFR part 4)

| Rule | Source | Implementation | Status |
| --- | --- | --- | --- |
| Brand name and class or type on the brand label; name and address, net contents, and alcohol content on any label | 27 CFR 4.32(a) and (b) | `brand`, `class_type`, `producer`, `net_contents`, `abv` | Implemented |
| Alcohol content "Alcohol __% by volume" or a range; only "alc." and "vol." abbreviations; "ABV" not allowed; tolerance 1.5 points at or below 14 percent and 1 point above; ranges up to 3 points at or below 14 percent and 2 points above, not crossing 14 percent; table or light wine at 7 to 14 percent may omit the numeric statement | 27 CFR 4.36; TTB wine alcohol content page | `abv`: range span and 14 percent boundary checks, table or light wine exception, "ABV" as a difference; tolerances require a trusted actual value from the application | Implemented |
| Sulfite declaration at 10 ppm or more of sulfur dioxide | 27 CFR 4.32(e); TTB sulfite declaration page | `wine_sulfites`: a readable declaration is a match; none read is a review item because nearly every commercial wine reaches the threshold and only the application chemistry can waive it | Implemented |
| Appellation of origin required with a varietal, vintage, or estate bottled designation, on the brand label | 27 CFR 4.23, 4.25, 4.26, 4.27, 4.32(a); TTB brand label page | `wine_appellation`: triggered by a varietal name, a vintage year, or "estate bottled"; a state, county, recognized viticultural area, or origin statement read on the panel that carries the brand name satisfies the placement rule as far as a photograph can show; one read only on another panel, or none read, is a review item. A city and state inside the producer's name and address is not an appellation. The viticultural-area vocabulary covers the common areas, not all 270, so an unlisted area reads as "no appellation read" and goes to review rather than passing | Implemented |

## Malt beverages (27 CFR part 7)

| Rule | Source | Implementation | Status |
| --- | --- | --- | --- |
| Brand name, class or type, name and address, net contents; alcohol content only when required | 27 CFR 7.63; TTB beer labeling page | `brand`, `class_type`, `producer`, `net_contents`; `malt_class_designation` requires a recognized class and treats "IPA" alone as insufficient | Implemented |
| Alcohol content, when stated, as percent by volume to the nearest tenth at or above 0.5 percent; only "alc" and "vol" abbreviations, "ABV" prohibited; no ranges; required when alcohol comes from added flavors or ingredients other than hops extract | 27 CFR 7.65; TTB malt beverage alcohol content page | `abv`: decimal precision, ranges, and "ABV" checks; a missing statement is reported as optional because the added-alcohol formula fact is not on the label | Implemented |
| Net contents in U.S. customary units, metric optional | 27 CFR 7.70 | `net_contents`: metric-only statement is a difference for malt beverages | Implemented |

## Common fields from the take-home instructions

| Field | Source | Implementation |
| --- | --- | --- |
| Brand name | 27 CFR 4.33, 5.64, 7.64 | Most prominent non-regulatory text on the brand label, excluding origin, class, address, warning, deposit, certification, and dated establishment copy and lines that are mostly digits; compared with the application value when one is entered |
| Class or type designation | 27 CFR parts 4, 5, and 7 subpart I | Recognized class words with glued-word repair. Readings of one family collapse to the most specific only when the shorter readings are contained in it ("Bourbon Whiskey" inside "Kentucky Straight Bourbon Whiskey"); two types of one family printed on one product ("Blended Whiskey" beside "Straight Bourbon Whiskey") stay a conflict for the reviewer, and marketing copy around class words ranks below a pure designation |
| Alcohol content | above | Percent statement with alcohol context; "vol" read as "vo", "ol", "vl", or "voi" after an "alc" prefix still names the statement |
| Net contents | above | Volume statement with unit; a zero read for the O of "OZ" is repaired, and two readings of one quantity ("12 FL. OZ" on the front, "12 FL. 0Z" on the side) are one value once parsed |
| Name and address of bottler or producer | above | Role phrase or organization name joined to the following address lines |
| Country of origin for imports | 27 CFR 4.32, 5.67, 7.67 | "Product of", "Produit de", "Wine of", "Made in", "Hecho en", and "Imported from" statements count only when what follows names a country (with or without "the"); "Made in small batches" and "Wine of the Month Club" are copy. "Product of USA" and a United States state after an origin phrase ("Wine of California") are domestic |
| Government health warning | 27 CFR part 16 | above |

## Application comparison

The instructions describe the review task as checking that what is on the label matches what
is in the application. When the reviewer enters application values, the label read is compared
with them: an entered value is searched across every readable line of the label, so a value
that OCR chose poorly for a field is still found if it is printed anywhere. Capitalization-only
and punctuation-only differences are routed to the reviewer, matching the "STONE'S THROW"
example in the instructions, and a value absent from every line is a difference.

The search only rescues a field whose failure means extraction chose the wrong text or found
none. A rule-format or placement failure (an unauthorized "ABV" abbreviation, a wine range
crossing 14 percent, a malt statement not to the nearest tenth, a metric-only malt net
contents, proof outside the alcohol content's field of vision) describes the label statement
itself and stands whatever the application says. A percentage counts as an alcohol
statement only in alcohol context ("alc", "vol", "abv", "proof"), so "contains 5% real
fruit juice" cannot satisfy a 5 percent application, and a label that states two
conflicting values for a field keeps its review status even when one of them matches.

## Not decidable from a label image

These facts need the application, formula, laboratory, or a physical sample and are reported
as review or informational rows rather than invented: actual alcohol content and tolerances,
sulfite chemistry, the added-alcohol trigger for malt beverage statements, state law
requirements, permit and production facts, physical type size in millimeters, and the
punctuation of the health warning, which OCR reads too unreliably to clear or to reject.

## Image quality

A panel the decoder classifies as blurred, dark, or blank stays a review item even when OCR
later reads text from it confidently: the read is used, but the image itself is a reviewer's
call and the result is never reported clean on that panel. A soft capture that OCR still
reads at length (eight lines or more at ordinary confidence) keeps its fields for the
reviewer; a capture that yields only a few weak lines is reported unreadable.
