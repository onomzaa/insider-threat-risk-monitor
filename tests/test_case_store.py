import tempfile
import unittest
from pathlib import Path
from modules.case_store import create_case, update_case, list_cases, get_case_history

class CaseStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "cases.db"
        self.alert = {"alert_id":"AL-test-001","employee_id":"user-test",
                      "risk_score":75,"risk_level":"High","event_count":4}
    def tearDown(self):
        self.temp.cleanup()
    def test_create_is_idempotent(self):
        case, created = create_case(self.alert, db_path=self.db)
        again, duplicate = create_case(self.alert, db_path=self.db)
        self.assertTrue(created)
        self.assertFalse(duplicate)
        self.assertEqual(case["case_id"], again["case_id"])
        self.assertEqual(len(list_cases(self.db)), 1)
    def test_update_and_history(self):
        case, _ = create_case(self.alert, db_path=self.db)
        updated = update_case(case["case_id"], "Under Review", "Analyst B",
                              "Reviewed events", db_path=self.db)
        self.assertEqual(updated["status"], "Under Review")
        self.assertEqual(updated["assigned_to"], "Analyst B")
        self.assertGreaterEqual(len(get_case_history(case["case_id"], self.db)), 2)
    def test_invalid_status(self):
        case, _ = create_case(self.alert, db_path=self.db)
        with self.assertRaises(ValueError):
            update_case(case["case_id"], "Invalid", db_path=self.db)

if __name__ == "__main__":
    unittest.main()
