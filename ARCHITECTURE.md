# Architecture

## Local prototype flow

```text
Browser UI → Python HTTP handler → deterministic record analysis → evidence-linked draft
                                                   ↓
                                         SQLite review audit log
```

`GET /api/learner` returns the synthetic record timeline and analysis. `POST /api/draft` prepares the evidence-linked teacher conversation. `POST /api/decision` accepts only `approved`, `edited`, or `rejected` and writes the reviewer's name, decision, draft text, timestamp, and evidence snapshot to SQLite. `GET /api/reviews` displays recent decisions.

The workflow keeps arithmetic in ordinary Python and requires a teacher decision before the draft is logged. A model cannot approve a profile, and the prototype does not diagnose or label a learner.

## Next engineering steps

For a challenge-ready version, replace the embedded fixture with a validated import format and authorization model; define a versioned MCP server for history retrieval, pattern analysis, and draft preparation; then add an open-weights model only for language drafting with strict evidence grounding. Any external MCP server should provide a concrete capability such as standards lookup, with source attribution and failure handling. Run privacy, security, accessibility, and teacher usability reviews before handling real data.
