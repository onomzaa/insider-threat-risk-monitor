"""SQLite persistence for analyst alert dispositions."""
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from modules.audit_log import append_audit_event

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "cases.db"
VALID_STATUSES = {"Open", "Under Review", "Resolved", "False Positive"}


def _connect(db_path=DEFAULT_DB):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db(db_path=DEFAULT_DB):
    with closing(_connect(db_path)) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS alert_reviews (
                alert_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'Open',
                analyst_note TEXT NOT NULL DEFAULT '',
                reviewed_by TEXT NOT NULL,
                reviewed_at TEXT NOT NULL
            )
        """)


def get_review(alert_id, db_path=DEFAULT_DB):
    initialize_db(db_path)
    with closing(_connect(db_path)) as conn:
        row = conn.execute("SELECT * FROM alert_reviews WHERE alert_id=?",
                           (str(alert_id),)).fetchone()
        return dict(row) if row else None


def list_reviews(db_path=DEFAULT_DB):
    initialize_db(db_path)
    with closing(_connect(db_path)) as conn:
        rows = conn.execute("SELECT * FROM alert_reviews ORDER BY reviewed_at DESC").fetchall()
        return [dict(row) for row in rows]


def save_review(alert_id, status, analyst_note="", actor="analyst", db_path=DEFAULT_DB):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid alert status: {status}")
    alert_id = str(alert_id).strip()
    actor = str(actor).strip() or "unknown"
    if not alert_id:
        raise ValueError("Alert ID is required")
    initialize_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    note = str(analyst_note).strip()
    with closing(_connect(db_path)) as conn, conn:
        previous = conn.execute("SELECT * FROM alert_reviews WHERE alert_id=?",
                                (alert_id,)).fetchone()
        action = "ALERT_REVIEW_CREATED" if previous is None else "ALERT_REVIEW_UPDATED"
        conn.execute("""
            INSERT INTO alert_reviews(alert_id,status,analyst_note,reviewed_by,reviewed_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(alert_id) DO UPDATE SET
                status=excluded.status,
                analyst_note=excluded.analyst_note,
                reviewed_by=excluded.reviewed_by,
                reviewed_at=excluded.reviewed_at
        """, (alert_id, status, note, actor, now))
        result = dict(conn.execute("SELECT * FROM alert_reviews WHERE alert_id=?",
                                   (alert_id,)).fetchone())
    append_audit_event(actor, action, f"alert:{alert_id}",
                       f"status={status}; note={note}", db_path)
    return result
