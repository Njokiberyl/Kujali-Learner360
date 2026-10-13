# Kujali Learner360

An early, local-first prototype for helping teachers review learner evidence across school terms. The demo demonstrates a learner timeline, deterministic trend calculations, evidence references, missing-data flags, draft support conversations, and a teacher approval/edit/reject audit trail.

## Run locally

Requires Python 3.10 or newer. No third-party packages are needed.

```powershell
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The app creates `learner360.sqlite3` in the project folder to record teacher review decisions. Set `PORT` or `LEARNER360_DB` to change the port or database path.

Run the documented checks:

```powershell
python -m unittest discover -s tests -v
```

## Prototype workflow

1. Retrieve the sample learner's term records and source IDs.
2. Compare assessment records with deterministic Python calculations; flag missing values.
3. Draft a plain-language support conversation with evidence references.
4. Let a named teacher edit, approve, or reject it; record the choice in SQLite.

Everything in the demo is synthetic. Do not use actual student records. This is a prototype, not a school records system, diagnostic tool, or validated education product. The sample recommendations are conversation prompts and require professional judgment.

## Optional MCP server

Install the MCP extra, then start the stdio server:

```powershell
python -m pip install -e ".[mcp]"
python mcp_server.py
```

It exposes `get_learner_history`, `analyse_learning_patterns`, and `draft_teacher_review`. Each tool is limited to the bundled synthetic learner; none can approve or save a learner profile.

## Current limits

- The sample dataset is embedded in `app.py` and contains one fictional learner.
- The built-in HTTP server is for local demonstration only; it has no authentication and must not be exposed to the public internet.
- Trend output compares first and latest available values. It does not claim causation or model a validated learning standard.
- No LLM is used in this first runnable prototype. Keeping calculations and review gates transparent makes the workflow inspectable; a later stage can add an open-weights model and MCP transport without letting a model calculate scores or approve records.

See [ARCHITECTURE.md](ARCHITECTURE.md) and [EVALS.md](EVALS.md) for design and evaluation notes.
