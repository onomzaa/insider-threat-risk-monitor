"""SQLite-backed case records and an append-only case activity history.

Use only synthetic or organization-authorized data. This prototype has no
authentication/authorization layer and is not suitable for production deployment.
"""
import sqlite3
from contextlib import closing
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "cases.db"


def _connect(db_path=DEFAULT_DB):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_db(db_path=DEFAULT_DB):
    with closing(_connect(db_path)) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL UNIQUE,
                employee_id TEXT NOT NULL,
                risk_score INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                event_count INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'Open',
                assigned_to TEXT NOT NULL DEFAULT '',
                analyst_notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS case_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                actor TEXT NOT NULL DEFAULT 'analyst',
                occurred_at TEXT NOT NULL,
                FOREIGN KEY(case_id) REFERENCES cases(case_id)
            )
        """)


def create_case(alert, assigned_to="", db_path=DEFAULT_DB):
    initialize_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    with closing(_connect(db_path)) as conn, conn:
        existing = conn.execute("SELECT * FROM cases WHERE alert_id=?",
                                (str(alert["alert_id"]),)).fetchone()
        if existing:
            return dict(existing), False
        cur = conn.execute("""
            INSERT INTO cases(alert_id,employee_id,risk_score,risk_level,event_count,
                              status,assigned_to,analyst_notes,created_at,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (str(alert["alert_id"]), str(alert.get("employee_id","UNKNOWN")),
              int(alert.get("risk_score",0)), str(alert.get("risk_level","Low")),
              int(alert.get("event_count",0)), "Open", str(assigned_to).strip(),
              "", now, now))
        case_id = cur.lastrowid
        conn.execute("INSERT INTO case_history(case_id,action,details,occurred_at) VALUES(?,?,?,?)",
                     (case_id, "Created", f"Case created from alert {alert['alert_id']}", now))
        row = conn.execute("SELECT * FROM cases WHERE case_id=?", (case_id,)).fetchone()
        return dict(row), True


def update_case(case_id, status, assigned_to="", analyst_notes="", actor="analyst",
                db_path=DEFAULT_DB):
    valid = {"Open", "Under Review", "Resolved", "False Positive"}
    if status not in valid:
        raise ValueError(f"Invalid case status: {status}")
    initialize_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    with closing(_connect(db_path)) as conn, conn:
        row = conn.execute("SELECT * FROM cases WHERE case_id=?", (int(case_id),)).fetchone()
        if not row:
            raise ValueError(f"Case {case_id} does not exist")
        old = dict(row)
        conn.execute("""UPDATE cases SET status=?,assigned_to=?,analyst_notes=?,updated_at=?
                       WHERE case_id=?""",
                     (status, str(assigned_to).strip(), str(analyst_notes).strip(), now, int(case_id)))
        changes = []
        if old["status"] != status: changes.append(f"Status: {old['status']} -> {status}")
        if old["assigned_to"] != str(assigned_to).strip(): changes.append("Assignment updated")
        if old["analyst_notes"] != str(analyst_notes).strip(): changes.append("Analyst notes updated")
        if changes:
            conn.execute("""INSERT INTO case_history(case_id,action,details,actor,occurred_at)
                           VALUES(?,?,?,?,?)""",
                         (int(case_id), "Updated", "; ".join(changes), str(actor), now))
        updated = conn.execute("SELECT * FROM cases WHERE case_id=?", (int(case_id),)).fetchone()
        return dict(updated)


def list_cases(db_path=DEFAULT_DB):
    initialize_db(db_path)
    with closing(_connect(db_path)) as conn, conn:
        return [dict(r) for r in conn.execute("SELECT * FROM cases ORDER BY updated_at DESC")]


def get_case_history(case_id, db_path=DEFAULT_DB):
    initialize_db(db_path)
    with closing(_connect(db_path)) as conn, conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM case_history WHERE case_id=? ORDER BY history_id DESC",
            (int(case_id),))]
