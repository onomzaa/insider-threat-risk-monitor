import tempfile
import unittest
from pathlib import Path
from modules.evidence_store import add_evidence, list_evidence
from modules.audit_log import list_audit_events, verify_audit_chain


class EvidenceStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "evidence_test.db"

    def tearDown(self):
        self.temp.cleanup()

    def test_add_and_list_evidence(self):
        item = add_evidence("ALT-101", "Synthetic log excerpt", "Shows unusual export",
                            "scenario_logs.csv row 12", "analyst1", db_path=self.db)
        records = list_evidence("ALT-101", self.db)
        self.assertEqual(len(records), 1)
        self.assertEqual(item["evidence_id"], records[0]["evidence_id"])
        self.assertEqual(records[0]["added_by"], "analyst1")
        self.assertEqual(records[0]["reference"], "scenario_logs.csv row 12")

    def test_required_fields(self):
        with self.assertRaises(ValueError):
            add_evidence("ALT-101", "", "", "ref", "analyst1", db_path=self.db)

    def test_evidence_addition_is_audited(self):
        add_evidence("ALT-101", "Evidence", "", "synthetic reference", "analyst1",
                     db_path=self.db)
        events = list_audit_events(self.db)
        self.assertEqual(events[0]["action"], "EVIDENCE_ADDED")
        self.assertTrue(verify_audit_chain(self.db)["valid"])


if __name__ == "__main__":
    unittest.main()
