# Warning Capability and Aggregation Matrix

Every row marked Active is a selected check. Every applicable Active row returns Match, Mismatch, Review, or Not verified and participates in the submission aggregate. No active warning check is advisory. The UI may display the internal Mismatch state as Difference, but the API, rules, fixtures, and traceability use Mismatch.

`evidence/regulatory-rules.json` owns the exact canonical heading, body, applicability threshold, source citations, and versions. Match is available only from exact observed characters after whitespace and line-wrap normalization. Punctuation is never deleted, inserted, or repaired to create Match. A secondary recognition pass may confirm a readable punctuation mutation as Mismatch or route unconfirmed OCR punctuation to Review, but it can never return Match.

| Check | Status | Evidence prerequisites | Match proof | Mismatch proof | Uncertainty | Aggregate |
|---|---|---|---|---|---|---|
| Applicability at or above 0.5 percent ABV | Active | Parsed label or reference ABV and selected spirits profile | At or above 0.5 percent: warning is required and present. Below 0.5 percent: warning detail rows are not applicable. | At or above 0.5 percent: warning is required and absent when panel coverage is sufficient. | Review when ABV or warning coverage is insufficient to decide applicability or presence. | Yes |
| Prescribed wording | Active | Warning block located; OCR confidence and ensemble agreement meet threshold | Exact canonical characters after whitespace and line-wrap normalization only | Readable observed mutation in words or punctuation | Review or Not verified | Yes |
| `GOVERNMENT WARNING:` uppercase | Active | Heading region located and readable | Exact uppercase heading and colon | Readable title case, lowercase, missing colon, or altered heading | Review or Not verified | Yes |
| Heading emphasized relative to remainder | Active with capability limit | Clear raster; heading and body glyph samples; minimum text height; stable stroke proxy | Calibrated relative-weight threshold met | Calibrated threshold clearly fails | Review or Not verified | Yes |
| Remaining warning text not bold | Active with capability limit | Clear raster and representative body glyph samples | Calibrated regular-weight evidence met | Body weight clearly matches prohibited emphasized treatment | Review or Not verified | Yes |
| Warning separate and apart | Active | Warning block and neighboring text boundaries visible | Required separation boundary is visible | Readable neighboring text intrudes into the warning block | Review or Not verified | Yes |
| Warning continuous | Active | Complete warning block visible across supplied panels | Canonical text forms one continuous block | Non-warning material interrupts the prescribed statement | Review or Not verified | Yes |
| Contrast and legibility | Active | Luminance range, local contrast, blur, occlusion, and OCR agreement available | Calibrated quality thresholds all pass | Clear evidence of inadequate contrast or legibility | Review or Not verified | Yes |
| Physical type size | Human-only limitation | Reliable physical scale and container-volume mapping, which ordinary photos do not provide | Never issued automatically in this prototype | Never issued automatically in this prototype | Display `Not assessed: physical scale unavailable` | No, outside automated selected checks |

## Canonical aggregation

1. Any applicable Active Mismatch produces `Differences detected`.
2. Otherwise, any applicable Active Review or Not verified produces `Review needed`.
3. `No differences found in checked fields` is permitted only when every applicable Active check is Match.
4. The physical-size limitation is shown separately and never as a passed check.
5. A human session disposition is separate and cannot rewrite system evidence.

## Sample outcomes

| Sample | Warning result | Submission result |
|---|---|---|
| Clear canonical warning with proven presentation checks | All Active rows Match | May be No differences found in checked fields if other fields Match |
| Title-case heading | Heading Mismatch | Differences detected |
| One altered warning word | Wording Mismatch | Differences detected |
| Glare over warning | Quality and affected rows Review or Not verified | Review needed |
| Exact words with insufficient boldness evidence | Emphasis rows Review or Not verified | Review needed |
