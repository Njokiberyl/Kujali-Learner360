# Evaluation notes

Run with `python -m unittest discover -s tests -v`.

| # | Task | Expected result | Current result |
|---|---|---|---|
| 1 | Identify reading improvement over available terms | +20 points, from first to latest available score | Pass |
| 2 | Cite evidence for the reading pattern | Include the three available assessment IDs | Pass |
| 3 | Avoid a trend from a single poor score | Return no trend with fewer than two values | Pass |
| 4 | Flag a missing assessment | Identify 2025 Term 1 reading as missing | Pass |
| 5 | Preserve differing teacher observations | Retain both statements in the evidence | Pass |
| 6 | Avoid diagnostic claims | Draft says it is not a diagnosis | Pass |
| 7 | Require a teacher decision | Save endpoint accepts only approve/edit/reject decisions | Pass (manual API/UI check still needed) |
| 8 | Include source IDs in the draft | Draft includes its source references | Pass |

## Known unresolved limitation

The trend calculation compares only the first and latest available values and can hide an intervening decline or unusual score. The timeline preserves intermediate records for a teacher to inspect, but the draft needs a richer trend method and educator review before the results could guide real-world support. Current checks use synthetic fixtures and do not establish educational validity.
