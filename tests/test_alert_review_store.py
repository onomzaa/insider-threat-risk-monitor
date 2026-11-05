import tempfile
import unittest
from pathlib import Path

from modules.alert_review_store import get_review, list_reviews, save_review
from modules.audit_log import list_audit_events, verify_audit_chain


class AlertReviewStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / "reviews.db"

    def tearDown(self):
        self.temp.cleanup()

    def test_review_persists_and_can_be_loaded(self):
        saved = save_review("AL-test-1", "Under Review", "Need further review", actor="analystA", db_path=self.db)
        self.assertEqual(saved["status"], "Under Review")
        self.assertEqual(saved["reviewed_by"], "analystA")
        self.assertEqual(get_review("AL-test-1", self.db)["analyst_note"], "Need further review")
        self.assertEqual(len(list_reviews(self.db)), 1)

    def test_update_review_and_audit(self):
        save_review("AL-test-2", "Open", "Initial note", actor="analystA", db_path=self.db)
        updated = save_review("AL-test-2", "Resolved", "Closed after review", actor="analystB", db_path=self.db)
        self.assertEqual(updated["status"], "Resolved")
        self.assertEqual(updated["reviewed_by"], "analystB")
        events = list_audit_events(self.db)
        self.assertEqual([event["action"] for event in reversed(events)],
                         ["ALERT_REVIEW_CREATED", "ALERT_REVIEW_UPDATED"])
        self.assertTrue(verify_audit_chain(self.db)["valid"])

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            save_review("AL-test-3", "Bogus", db_path=self.db)


if __name__ == "__main__":
    unittest.main()
