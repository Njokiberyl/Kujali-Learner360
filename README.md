# Kujali Learner360

Kujali Learner360 is a teacher-support prototype for reviewing a fictional learner's quiz, attendance, and observation records across school terms. It surfaces evidence-linked patterns and missing information, then prepares a teacher-only conversation draft. It does not diagnose, label, rank, or recommend a subject or career path.

**All records in this repository are synthetic. Never enter identifiable student information.** This is a prototype, not a school records system or a validated education product.

## Problem statement

When learners move between teachers or school terms, assessment, attendance, and observation records can be scattered. A single score or a remembered impression may not show a learner's history. Teachers need a way to review available evidence, see what is missing, and prepare a supportive conversation without turning a pattern into a fixed label.

## Solution overview

The demo brings one fictional learner's records into a term-by-term timeline. Ordinary Python calculates first-to-latest patterns and marks missing data; findings retain their source IDs. An optional AI agent prepares a plain-language draft and can consult a public education reference. A named teacher must review and approve, edit, or reject the draft. The tool supports teacher judgment; it does not make learner decisions.

## Target users

The intended users are upper-primary public-school teachers who need to review a learner's evidence across terms, especially when records come from different teachers. The prototype is designed for a teacher preparing a supportive conversation. It is not intended for autonomous use by learners, guardians, or school administrators.

## Architecture

The local Python web app displays synthetic learner records and teacher review controls. Deterministic Python analyses records, while SQLite stores MCP activity and teacher decisions. The optional AI flow uses Pydantic AI with a locally served Qwen3 model through Ollama and connects to two MCP servers. See [ARCHITECTURE.md](ARCHITECTURE.md) for the flow diagram and component details.

### Agent architecture

1. A teacher starts a review in the local web app.
2. Pydantic AI orchestrates the review using Qwen3 served by Ollama.
3. The agent calls the Kujali MCP tools to retrieve fictional records, calculate patterns, and prepare a sourced draft.
4. When useful, it can call the community MCP Fetch server for a general public education reference. Learner-specific information must not be sent to Fetch.
5. Tool activity is recorded in SQLite. The named teacher then edits, approves, or rejects the draft.

The agent drafts language only. Python calculates scores and trends; the agent cannot approve or save a teacher decision.

## MCP implementation and tools/servers

The project implements an MCP server in `mcp_server.py` with three tools, restricted to the synthetic sample learner:

- `get_learner_history` retrieves term records and evidence IDs.
- `analyse_learning_patterns` calculates trends deterministically and identifies missing values.
- `draft_teacher_review` produces a sourced, plain-language teacher conversation draft.

The optional community [MCP Fetch server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch) retrieves public webpages for general education context. It is not given learner-specific content. Pydantic AI connects to both servers over local standard input/output (stdio). Inputs, outputs, status, and timestamps for tool calls are written to a local SQLite audit log.

## Human-in-the-loop workflow

The agent returns a draft for a named teacher to review. The teacher must enter their name and choose **Approve draft**, **Save edited**, or **Reject**. The agent cannot approve, save, or share the decision. The tool calls and teacher decision are logged locally. No guardian-sharing feature is included.

## Technology stack

- Python 3.10 or later and its built-in HTTP server
- Pydantic AI for agent orchestration
- Qwen3 `1.7b` served locally by Ollama
- MCP Python SDK and the community MCP Fetch server
- SQLite for local tool and teacher-decision audit records
- HTML, CSS, and JavaScript for the interface

## Setup and installation

The full agent demo requires Python 3.10+, [Ollama](https://ollama.com/download), and an internet connection for installing dependencies and downloading the model. From the repository folder in PowerShell:

```powershell
.\run_demo.ps1
```

The script installs the optional agent dependencies, downloads `qwen3:1.7b`, and starts the local web app. If PowerShell blocks the script, inspect `run_demo.ps1` and run its commands individually. The app is local to your computer; keep the terminal open while using it.

## Usage instructions

1. Open <http://127.0.0.1:8000> after the setup script starts the server.
2. Use **Run full AI + MCP review** for the optional agent workflow. This requires Ollama to be installed and running; the first review may take a while.
3. Read the sources and draft in the Teacher review card.
4. Enter the teacher's name and choose **Approve draft**, **Save edited**, or **Reject**.

For a deterministic preview without installing Ollama or agent extras, run `py app.py` and choose **Create a deterministic draft**. This preview does not run the AI/MCP flow.

## Limitations

- The sample has one fictional learner and four terms; it is not a cohort and cannot show comparative ranking.
- Trends compare the first and latest available values and may miss an intervening change.
- The AI/MCP flow has not yet been verified end to end on every computer. See [EVALS.md](EVALS.md): agent checks are marked **Not run** until a real local run is inspected.
- The prototype has no authentication and is for local demonstration with synthetic data only. Do not expose it to the public internet or enter real student records.
- It does not diagnose, label, rank learners, recommend pathways, or contact guardians. The prototype has not established educational validity or outcomes in real schools.

## Future improvements

- Run and document the full Qwen3 and MCP workflow on a supported computer, including review of its SQLite audit log.
- Evaluate with educators using synthetic or properly de-identified examples, and improve trend analysis so intermediate changes are visible.
- Improve accessibility, setup guidance, and support for additional synthetic scenarios.
- Before any real-world pilot, complete privacy, security, safeguarding, and educational validation with the relevant schools and communities.

## Other: evaluation and licence

The deterministic prototype has eight recorded evaluation tasks; they do not validate the AI/MCP agent. See [EVALS.md](EVALS.md) for results and checks still to run. The code is released under the [MIT License](LICENSE).
