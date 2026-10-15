"""Pydantic AI orchestration for the local, synthetic Learner360 demonstration."""
from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastmcp.client.transports import StdioTransport
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPToolset
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from app import DB_PATH, ROOT, init_db


MODEL_NAME = os.environ.get("LEARNER360_MODEL", "qwen3:1.7b")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
FETCH_GUIDANCE_URL = "https://www.unesco.org/en/education"


def _json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return json.dumps(str(value), ensure_ascii=False)


def _write_event(run_id: str, server: str, tool: str, inputs: dict[str, Any],
                 output: Any, status: str, started_at: str) -> None:
    finished_at = datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(DB_PATH) as db:
        db.execute(
            """INSERT INTO tool_events
               (run_id,server_name,tool_name,input_json,output_json,status,started_at,finished_at)
               VALUES(?,?,?,?,?,?,?,?)""",
            (run_id, server, tool, _json(inputs), _json(output), status, started_at, finished_at),
        )


def _logged_toolset(server_name: str, transport: StdioTransport, run_id: str) -> MCPToolset:
    async def record_call(ctx: Any, call_tool: Any, name: str, tool_args: dict[str, Any]) -> Any:
        del ctx
        started_at = datetime.now(timezone.utc).isoformat()
        safe_args = tool_args
        try:
            if server_name == "Official MCP Fetch server":
                if name != "fetch":
                    raise PermissionError("Only the public education reference fetch tool is allowed.")
                # Do not allow learner-derived text to enter an external request.
                safe_args = {"url": FETCH_GUIDANCE_URL, "max_length": 3000, "start_index": 0, "raw": False}
            result = await call_tool(name, safe_args)
            _write_event(run_id, server_name, name, safe_args, result, "succeeded", started_at)
            return result
        except Exception as exc:
            _write_event(run_id, server_name, name, safe_args,
                         {"error": str(exc)}, "failed", started_at)
            raise

    return MCPToolset(transport, process_tool_call=record_call)


async def _run(run_id: str) -> str:
    model = OpenAIChatModel(
        MODEL_NAME,
        provider=OpenAIProvider(base_url=OLLAMA_BASE_URL, api_key="ollama"),
    )
    env = {**os.environ, "LEARNER360_RUN_ID": run_id}
    kujali = _logged_toolset(
        "Kujali Learner360 MCP",
        StdioTransport(command=sys.executable, args=[str(ROOT / "mcp_server.py")], env=env),
        run_id,
    ).prefixed("learner")
    fetch = _logged_toolset(
        "Official MCP Fetch server",
        StdioTransport(command=sys.executable, args=["-m", "mcp_server_fetch"], env=env),
        run_id,
    ).prefixed("public_reference")

    agent = Agent(
        model=model,
        toolsets=[kujali, fetch],
        instructions=(
            "You are a teacher-support assistant. Work only with the bundled fictional learner SAMPLE-01. "
            "Use the learner MCP tools to retrieve the history, calculate evidence-linked patterns, and draft "
            "a short, plain-language teacher conversation. Use the public_reference_fetch tool to consult "
            f"the public general-education page at {FETCH_GUIDANCE_URL}; send no learner-specific information "
            "to that server. Never diagnose, assign a label, rank against peers, or recommend a subject/career "
            "path. Cite the source IDs for every learner-specific claim and name missing or conflicting data. "
            "Return a teacher-only draft. A named teacher must edit, approve, or reject it in the app before "
            "it is saved. Never contact a learner or guardian and never save or approve anything yourself."
        ),
    )
    task = (
        "Complete one full review task for the synthetic learner: retrieve the history, analyse patterns, "
        "draft a sourced teacher conversation, and consult the public education reference. Explain any data "
        "limits. Do not write to a learner profile or make a pathway recommendation."
    )
    result = await agent.run(task)
    return str(result.output)


def run_agent() -> dict[str, Any]:
    """Run the local open-weights agent and return its teacher-only draft plus audit ID."""
    init_db()
    run_id = str(uuid.uuid4())
    output = asyncio.run(_run(run_id))
    with sqlite3.connect(DB_PATH) as db:
        rows = db.execute(
            """SELECT server_name,tool_name,input_json,output_json,status,started_at,finished_at
               FROM tool_events WHERE run_id=? ORDER BY id""", (run_id,)
        ).fetchall()
    return {
        "run_id": run_id,
        "model": MODEL_NAME,
        "text": output,
        "status": "teacher_review_required",
        "tool_events": [
            {"server": row[0], "tool": row[1], "input": json.loads(row[2]),
             "output": json.loads(row[3]), "status": row[4],
             "started_at": row[5], "finished_at": row[6]}
            for row in rows
        ],
    }


if __name__ == "__main__":
    print(json.dumps(run_agent(), indent=2, ensure_ascii=False))
