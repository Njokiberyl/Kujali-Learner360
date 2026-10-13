"""Optional MCP adapter exposing Learner360's three review tools.

Install with `python -m pip install -e ".[mcp]"`, then run `python mcp_server.py`.
All tools operate on the bundled synthetic demo learner only.
"""
from mcp.server.fastmcp import FastMCP

from app import RECORDS, analyse, draft_review

mcp = FastMCP("Kujali Learner360")


@mcp.tool()
def get_learner_history(learner_id: str = "SAMPLE-01") -> dict:
    """Retrieve synthetic term records, source IDs, and missing-data indicators."""
    if learner_id != "SAMPLE-01":
        return {"error": "This prototype contains synthetic learner SAMPLE-01 only."}
    return {"learner_id": learner_id, "records": RECORDS, "analysis": analyse()}


@mcp.tool()
def analyse_learning_patterns(learner_id: str = "SAMPLE-01") -> dict:
    """Compare available synthetic assessment records and cite their source IDs."""
    if learner_id != "SAMPLE-01":
        return {"error": "This prototype contains synthetic learner SAMPLE-01 only."}
    return analyse()


@mcp.tool()
def draft_teacher_review(learner_id: str = "SAMPLE-01") -> dict:
    """Prepare an evidence-linked teacher draft; this tool cannot approve or save it."""
    if learner_id != "SAMPLE-01":
        return {"error": "This prototype contains synthetic learner SAMPLE-01 only."}
    return draft_review()


if __name__ == "__main__":
    mcp.run()
