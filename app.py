"""Kujali Learner360: a synthetic-data learner support prototype."""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
DB_PATH = Path(os.environ.get("LEARNER360_DB", ROOT / "learner360.sqlite3"))

# Entirely synthetic sample records. Do not replace with identifiable learner data.
RECORDS = [
    {"term": "2024 · Term 1", "date": "2024-04-12", "reading": 48, "maths": 62, "absences": 4,
     "observation": "Enjoys reading aloud in a small group.", "sources": ["ASM-2401", "ATT-2401", "OBS-2401"]},
    {"term": "2024 · Term 2", "date": "2024-08-16", "reading": 52, "maths": 61, "absences": 5,
     "observation": "Often completes reading tasks with a partner.", "sources": ["ASM-2402", "ATT-2402", "OBS-2402"]},
    {"term": "2025 · Term 1", "date": "2025-04-11", "reading": None, "maths": 59, "absences": None,
     "observation": "Teacher A: contributes more in discussion. Teacher B: participation varies.", "sources": ["ASM-2501", "OBS-2501"]},
    {"term": "2025 · Term 2", "date": "2025-08-15", "reading": 68, "maths": 60, "absences": 3,
     "observation": "Selected a book independently and shared a short summary.", "sources": ["ASM-2502", "ATT-2502", "OBS-2502"]},
]


def analyse(records: list[dict] | None = None) -> dict:
    """Compare available values deterministically and preserve source references."""
    rows = records if records is not None else RECORDS
    patterns = []
    for field, label in (("reading", "Reading"), ("maths", "Mathematics")):
        present = [(r["term"], r.get(field), r["sources"][0]) for r in rows if r.get(field) is not None]
        missing = [r["term"] for r in rows if r.get(field) is None]
        if len(present) >= 2:
            change = present[-1][1] - present[0][1]
            direction = "increased" if change > 0 else "decreased" if change < 0 else "was unchanged"
            patterns.append({"area": label, "direction": direction, "change": change,
                             "first_term": present[0][0], "last_term": present[-1][0],
                             "sources": [x[2] for x in present], "missing_terms": missing,
                             "evidence_count": len(present)})
    return {"patterns": patterns, "missing_data": [
        {"term": r["term"], "field": field} for r in rows
        for field in ("reading", "maths", "absences") if r.get(field) is None
    ], "observations": [{"term": r["term"], "text": r["observation"], "sources": r["sources"][-1:]}
                       for r in rows if r.get("observation")],
       "records_reviewed": len(rows)}


def draft_review() -> dict:
    findings = analyse()
    lines = ["Learner support conversation · Draft", "", "What the records show:"]
    for p in findings["patterns"]:
        lines.append(f"• {p['area']} {p['direction']} by {p['change']} points from {p['first_term']} to {p['last_term']} (sources: {', '.join(p['sources'])}).")
    lines += ["", "Points to check with the learner:",
              "• Ask what has helped with reading and what support would feel useful.",
              "• Check the missing 2025 Term 1 assessment and attendance record before drawing a full-term conclusion.",
              "• Compare the differing participation observations with the learner and relevant teachers.",
              "", "This draft describes records; it is not a diagnosis or a decision about the learner."]
    return {"text": "\n".join(lines), "evidence": findings, "status": "draft"}


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS reviews (
          id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
          reviewer TEXT NOT NULL, decision TEXT NOT NULL, text TEXT NOT NULL,
          evidence_json TEXT NOT NULL)""")


def json_response(handler: BaseHTTPRequestHandler, status: int, value: object) -> None:
    payload = json.dumps(value, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(payload)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args: object) -> None:
        # Keep sample student details out of terminal logs.
        print(f"{self.log_date_time_string()} {self.command} {self.path.split('?')[0]}")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/learner":
            return json_response(self, 200, {"id": "SAMPLE-01", "name": "Amani N.", "class": "Class 6",
                                              "records": RECORDS, "analysis": analyse()})
        if path == "/api/reviews":
            with sqlite3.connect(DB_PATH) as db:
                db.row_factory = sqlite3.Row
                rows = db.execute("SELECT id,created_at,reviewer,decision,text FROM reviews ORDER BY id DESC LIMIT 20").fetchall()
            return json_response(self, 200, [dict(row) for row in rows])
        if path in ("/", "/index.html"):
            body = (ROOT / "static" / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return self.wfile.write(body)
        return json_response(self, 404, {"error": "Not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        if length > 50_000:
            return json_response(self, 413, {"error": "Request too large"})
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            return json_response(self, 400, {"error": "Invalid JSON"})
        if path == "/api/draft":
            return json_response(self, 200, draft_review())
        if path == "/api/decision":
            decision = payload.get("decision")
            if decision not in ("approved", "edited", "rejected"):
                return json_response(self, 400, {"error": "Choose approve, edit, or reject."})
            reviewer = str(payload.get("reviewer", "Teacher")).strip()[:80] or "Teacher"
            text = str(payload.get("text", ""))[:10_000]
            if not text.strip():
                return json_response(self, 400, {"error": "A review draft is required."})
            with sqlite3.connect(DB_PATH) as db:
                cursor = db.execute("INSERT INTO reviews(created_at,reviewer,decision,text,evidence_json) VALUES(?,?,?,?,?)",
                                    (datetime.now(timezone.utc).isoformat(), reviewer, decision, text,
                                     json.dumps(analyse(), ensure_ascii=False)))
                review_id = cursor.lastrowid
            return json_response(self, 201, {"id": review_id, "decision": decision, "saved": True})
        return json_response(self, 404, {"error": "Not found"})


if __name__ == "__main__":
    init_db()
    host, port = os.environ.get("HOST", "127.0.0.1"), int(os.environ.get("PORT", "8000"))
    print(f"Kujali Learner360 running at http://{host}:{port} (synthetic demo data)")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
