# Kujali Learner360

Kujali Learner360 helps a public-school teacher review a fictional learner's quiz, attendance, and observation records across terms. It surfaces evidence-linked patterns and missing data, then prepares a teacher-only conversation draft. It does not diagnose, label, rank, or recommend a subject or career path.

**Everything in this repository is synthetic. Never enter identifiable student information.** This is a prototype, not a school records system or validated education product.

## Run the local demo

Requires Python 3.10+ and [Ollama for Windows, macOS, or Linux](https://ollama.com/download). Ollama serves the open-weight Qwen3 model locally.

1. Install Ollama and open a new PowerShell window.
2. From this repository folder, run the setup script. It installs app dependencies, downloads the model, and starts the site:

```powershell
.\run_demo.ps1
```

If PowerShell reports that scripts are disabled, run the three commands shown in `run_demo.ps1` directly in PowerShell instead.

Open <http://127.0.0.1:8000>. Keep the terminal open. In the Teacher review card, select **Run full AI + MCP review**. A run can take a minute on a small computer.

The agent uses Pydantic AI to coordinate two MCP servers: the three tools in this repository and the community MCP Fetch server. The Fetch server is used only for a public, general-education reference; learner records are not sent to it. Set `LEARNER360_MODEL` to choose another Ollama model, or `OLLAMA_BASE_URL` to change the local endpoint.

## Teacher approval

The agent returns a draft for a teacher to review. It cannot approve, save, or share the draft. A teacher must enter their name and choose **Approve draft**, **Save edited**, or **Reject**. Tool calls and teacher decisions are stored in a local SQLite audit log with inputs, outputs, timestamps, and the named reviewer.

The MCP server exposes:

- `get_learner_history`: retrieve the fictional learner's term records and evidence IDs.
- `analyse_learning_patterns`: calculate trends deterministically and identify missing values.
- `draft_teacher_review`: produce a sourced, plain-language teacher conversation draft.

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md): agent flow, MCP servers, and human review gate.
- [EVALS.md](EVALS.md): eight deterministic evaluation tasks and an unresolved limitation.
- [SUBMISSION.md](SUBMISSION.md): competition description.

## Local deterministic demo

To view the sample timeline without the agent extras or Ollama, run `py app.py` and use **Create a deterministic draft**. The agent button needs Ollama running and the optional dependencies above.

## Known limits

- The sample dataset contains one fictional learner; it is not a cohort and does not show comparative ranking.
- The trend calculation compares first and latest available values; it can miss an intermediate change.
- The built-in HTTP server has no authentication. It is suitable only for local demonstration with synthetic data. Do not expose it to the public internet.
- Open-weight model quality, tool use, runtime, and device compatibility have not yet been verified on every computer. Teacher review is required.
- No real student records, guardian communications, diagnoses, or pathway recommendations are supported.

## License

MIT. See [LICENSE](LICENSE).
