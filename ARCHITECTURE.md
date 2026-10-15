# Architecture

## Agent run

```text
Teacher starts review
        ↓
Pydantic AI orchestration + local Qwen3 open-weight model (Ollama)
        ├── Kujali MCP server: history → deterministic patterns → sourced teacher draft
        └── Borrowed MCP Fetch server: public general-education reference
        ↓
Tool inputs, outputs, status, and timestamps are written to SQLite
        ↓
Named teacher edits, approves, or rejects the draft; decision and evidence are logged
```

The web app uses a fictional learner and the built-in Python HTTP server. The agent sends no learner record to the borrowed Fetch server; it is asked to consult only a public, general-education page. The local Qwen model performs language drafting. Ordinary Python calculates all scores and trends.

## MCP servers

- **Built here:** `mcp_server.py` exposes `get_learner_history`, `analyse_learning_patterns`, and `draft_teacher_review`. The tools are limited to synthetic `SAMPLE-01`. The draft is a proposed teacher conversation, not a diagnosis or pathway decision.
- **Borrowed:** [`mcp-server-fetch`](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) retrieves and converts public webpages. Using this maintained server avoids writing and maintaining an HTML-fetching/parser tool. The agent is instructed to send it no learner-specific content.

Pydantic AI coordinates the multi-step task and connects to both servers over local stdio. Ollama serves Qwen3 locally through its OpenAI-compatible API. A run has a unique ID; every MCP call records the server, tool, input, output, status, and timestamps.

## Human review and limits

The model cannot approve or save a teacher decision. A teacher must enter their name and choose approve, edit, or reject before a review is recorded. The app has no guardian-sharing function, learner labels, class ranking, or subject/career recommendation. It contains no authentication and is only a synthetic-data prototype; never use real learner records or expose it publicly without a security review.
