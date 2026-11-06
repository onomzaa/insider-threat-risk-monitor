"""SQLite evidence register for incident investigations.

Stores evidence metadata and references only; it does not upload or inspect files.
Use synthetic or authorized evidence references.
"""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from contextlib import closing

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "cases.db"


def _connect(db_path=DEFAULT_DB):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_evidence_db(db_path=DEFAULT_DB):
    with closing(_connect(db_path)) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incident_evidence (
                evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                reference TEXT NOT NULL,
                captured_at TEXT NOT NULL,
                added_by TEXT NOT NULL,
                added_at TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_evidence_alert ON incident_evidence(alert_id)")


def add_evidence(alert_id, title, description, reference, actor, captured_at=None, db_path=DEFAULT_DB):
    """Add an evidence metadata record and audit its creation."""
    alert_id = str(alert_id).strip()
    title = str(title).strip()
    reference = str(reference).strip()
    actor = str(actor).strip()
    if not alert_id or not title or not reference or not actor:
        raise ValueError("Alert ID, title, reference, and analyst are required.")
    if len(title) > 160 or len(description) > 2000 or len(reference) > 500:
        raise ValueError("Evidence fields exceed the allowed length.")
    captured_at = str(captured_at or datetime.now(timezone.utc).isoformat()).strip()
    added_at = datetime.now(timezone.utc).isoformat()
    initialize_evidence_db(db_path)
    with closing(_connect(db_path)) as conn, conn:
        cur = conn.execute("""
            INSERT INTO incident_evidence
            (alert_id,title,description,reference,captured_at,added_by,added_at)
            VALUES(?,?,?,?,?,?,?)
        """, (alert_id,title,str(description),reference,captured_at,actor,added_at))
        evidence_id = cur.lastrowid
    from modules.audit_log import append_audit_event
    append_audit_event(actor, "EVIDENCE_ADDED", f"alert:{alert_id}",
                       f"evidence_id={evidence_id}; title={title}", db_path)
    return get_evidence(alert_id, db_path)[-1]


def list_evidence(alert_id, db_path=DEFAULT_DB):
    """Return evidence records for an alert, oldest first."""
    initialize_evidence_db(db_path)
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT * FROM incident_evidence WHERE alert_id=? ORDER BY evidence_id",
            (str(alert_id),)
        ).fetchall()
    return [dict(row) for row in rows]


def get_evidence(alert_id, db_path=DEFAULT_DB):
    return list_evidence(alert_id, db_path)
