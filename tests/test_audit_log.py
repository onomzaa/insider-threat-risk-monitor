import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from modules.audit_log import append_audit_event, list_audit_events, verify_audit_chain


class AuditLogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "audit.db"

    def tearDown(self):
        self.temp.cleanup()

    def test_appends_and_verifies_chain(self):
        first = append_audit_event("analyst-a", "CASE_CREATED", "case:1", "created", self.db)
        second = append_audit_event("analyst-a", "CASE_UPDATED", "case:1", "status changed", self.db)
        self.assertEqual(second["previous_hash"], first["entry_hash"])
        result = verify_audit_chain(self.db)
        self.assertTrue(result["valid"])
        self.assertEqual(result["checked"], 2)
        self.assertEqual(len(list_audit_events(self.db)), 2)

    def test_detects_record_tampering(self):
        append_audit_event("analyst-a", "CASE_CREATED", "case:1", "created", self.db)
        append_audit_event("analyst-a", "CASE_UPDATED", "case:1", "status changed", self.db)
        import sqlite3
        with closing(sqlite3.connect(self.db)) as conn, conn:
            conn.execute("UPDATE audit_log SET details='altered' WHERE audit_id=1")
        result = verify_audit_chain(self.db)
        self.assertFalse(result["valid"])
        self.assertEqual(result["failed_audit_id"], 1)


if __name__ == "__main__":
    unittest.main()
