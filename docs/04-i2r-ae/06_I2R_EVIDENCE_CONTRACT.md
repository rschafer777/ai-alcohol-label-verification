# I2R Evidence Contract

Document control ID: LV-I2R-006  
Revision: 1.0  
Date: 2026-08-31  
Status: Draft for combined I2R and FRD review

## 1. Evidence object

Every non-null `evidenceRef` resolves to exactly one object in the response-level `evidence` collection:

```json
{
  "evidenceId": "ev_country_panel-2_01",
  "panelId": "panel-2",
  "polygonOriginalPixels": [
    {"x": 112, "y": 420},
    {"x": 382, "y": 418},
    {"x": 384, "y": 468},
    {"x": 110, "y": 470}
  ],
  "sourceView": "original",
  "transformId": "transform-panel-2-v1",
  "textSnippet": "PRODUCT OF CANADA",
  "confidenceProvenance": {
    "source": "rapidocr",
    "signal": 0.94,
    "calibratedProbability": false
  }
}
```

## 2. Identity and referential rules

- `evidenceId` is unique within one response and matches `ev_<check-or-role>_<panel-id>_<sequence>`.
- `panelId` resolves to exactly one response panel.
- Every field `evidenceRef` and every alternative `evidenceRef` resolves to an object.
- An evidence object may support multiple related checks only when the same observed region genuinely supplies them.
- Material ambiguity alternatives must have distinct evidence IDs and distinct polygons or panels. The expected value cannot choose or merge them.
- Missing, unreadable, unsupported, or non-measurable evidence uses `evidenceRef: null` and a reason code that explains the absence. No empty evidence object is created.

## 3. Coordinate contract

- Coordinate origin is the top-left pixel of the original decoded image after EXIF orientation normalization.
- `x` increases right and `y` increases down.
- Each point is an integer pixel coordinate with `0 <= x < originalWidth` and `0 <= y < originalHeight`.
- A polygon contains exactly four vertices.
- Vertices are clockwise. The first vertex is the vertex with the smallest `y`, breaking ties with the smallest `x`.
- The polygon must have non-zero area and remain within panel bounds.
- Derived OCR views carry a versioned `transformId`. The server maps their polygons back to original coordinates before building the public result.
- The browser renders only original-coordinate polygons. It applies a tested scale and translation for the current view without changing the stored object.

## 4. Text and confidence

- `textSnippet` contains only the observed label substring needed to explain the field. It is optional when the evidence is visual presentation rather than text.
- Confidence is raw adapter provenance, not an accuracy probability and not a legal score.
- The UI may display confidence only with an uncertainty explanation. It cannot use it as approval wording.

## 5. Schema failure behavior

- The server validates evidence uniqueness, references, panel existence, coordinate bounds, point order, and alternative ownership before returning a result.
- Any referential-integrity or coordinate failure converts the entire response to result-free `500 internal_error`; no partial result is sent.
- The browser validates the public result schema again. Any invalid or unresolved reference suppresses the entire result and shows a result-free recovery message.
- The browser never guesses a panel, reuses the last region, or silently drops an invalid alternative.

## 6. Test oracle

Required tests cover:

- valid single and multi-panel evidence;
- derived-to-original coordinate mapping;
- out-of-bounds and zero-area polygons;
- duplicate evidence IDs;
- missing panel and missing evidence references;
- wrong vertex count and deterministic point order;
- one field supported by one valid region;
- two conflicting country alternatives with exact values and distinct polygons;
- null evidence for Not verified;
- browser suppression of an invalid result contract.
