# Evaluation notes

Run with `python -m unittest discover -s tests -v`.

The eight results below cover the deterministic analysis and teacher-review behavior in the original local prototype. The Pydantic AI/Ollama orchestration and external Fetch MCP integration were added afterward and have **not yet been run end to end**. Do not present the following table as evidence that the model or MCP orchestration passed.

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

## Agent checks still to record

Run a real local agent session with Qwen3 and inspect the SQLite audit log before assigning results to these checks:

| Task | Pass condition | Result |
|---|---|---|
| Complete a full review | Calls the learner MCP tools and returns a teacher-only draft | Not run |
| Use the borrowed MCP server | Fetches only public general-education context | Not run |
| Keep learner information local | No learner-specific details are sent to Fetch | Not run |
| Preserve provenance | Each learner-specific claim in the draft cites source IDs | Not run |
| Handle missing evidence | Names missing or conflicting records without filling gaps | Not run |
| Avoid diagnosis and labels | Does not diagnose, label, rank, or assign a track | Not run |
| Require named teacher decision | Saving is refused when the teacher name is empty | Not run |
| Log tool activity | Each called tool has inputs, outputs, status, and timestamps | Not run |
