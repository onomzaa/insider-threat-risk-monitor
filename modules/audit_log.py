"""SQLite-backed hash-chained audit log for prototype accountability.

The chain detects accidental or selective record edits; it is not tamper-proof
against an administrator who can rewrite the database and recompute every hash.
"""
import hashlib
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parents[1] / "data" / "cases.db"
GENESIS_HASH = "0" * 64


def _connect(db_path=DEFAULT_DB):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _entry_hash(entry):
    payload = {
        "audit_id": entry["audit_id"],
        "actor": entry["actor"],
        "action": entry["action"],
        "resource": entry["resource"],
        "details": entry["details"],
        "occurred_at": entry["occurred_at"],
        "previous_hash": entry["previous_hash"],
    }
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


def initialize_audit_db(db_path=DEFAULT_DB):
    with closing(_connect(db_path)) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                details TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                entry_hash TEXT NOT NULL
            )
        """)


def append_audit_event(actor, action, resource, details="", db_path=DEFAULT_DB):
    """Append one audit event and return its stored record."""
    initialize_audit_db(db_path)
    occurred_at = datetime.now(timezone.utc).isoformat()
    with closing(_connect(db_path)) as conn, conn:
        last = conn.execute(
            "SELECT entry_hash FROM audit_log ORDER BY audit_id DESC LIMIT 1"
        ).fetchone()
        previous_hash = last["entry_hash"] if last else GENESIS_HASH
        values = {
            "actor": str(actor).strip() or "unknown",
            "action": str(action).strip(),
            "resource": str(resource).strip(),
            "details": str(details),
            "occurred_at": occurred_at,
            "previous_hash": previous_hash,
        }
        cursor = conn.execute("""
            INSERT INTO audit_log(actor,action,resource,details,occurred_at,previous_hash,entry_hash)
            VALUES(?,?,?,?,?,?,?)
        """, (*values.values(), ""))
        audit_id = cursor.lastrowid
        entry = {"audit_id": audit_id, **values}
        digest = _entry_hash(entry)
        conn.execute("UPDATE audit_log SET entry_hash=? WHERE audit_id=?", (digest, audit_id))
        entry["entry_hash"] = digest
        return entry


def list_audit_events(db_path=DEFAULT_DB, limit=500):
    initialize_audit_db(db_path)
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT * FROM audit_log ORDER BY audit_id DESC LIMIT ?", (int(limit),)
        ).fetchall()
        return [dict(row) for row in rows]


def verify_audit_chain(db_path=DEFAULT_DB):
    """Return verification status and the first failing audit ID, if any."""
    initialize_audit_db(db_path)
    expected_previous = GENESIS_HASH
    checked = 0
    with closing(_connect(db_path)) as conn:
        rows = conn.execute("SELECT * FROM audit_log ORDER BY audit_id ASC").fetchall()
        for row in rows:
            entry = dict(row)
            checked += 1
            if entry["previous_hash"] != expected_previous:
                return {"valid": False, "checked": checked, "failed_audit_id": entry["audit_id"],
                        "reason": "Previous hash does not match prior entry"}
            expected_hash = _entry_hash(entry)
            if entry["entry_hash"] != expected_hash:
                return {"valid": False, "checked": checked, "failed_audit_id": entry["audit_id"],
                        "reason": "Entry hash mismatch"}
            expected_previous = entry["entry_hash"]
    return {"valid": True, "checked": checked, "failed_audit_id": None, "reason": "Chain verified"}
