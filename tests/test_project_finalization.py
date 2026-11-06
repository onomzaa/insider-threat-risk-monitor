import tempfile
import unittest
from pathlib import Path

from modules.project_finalization import CHECKS, assess_project


class ProjectFinalizationTests(unittest.TestCase):
    def test_readiness_reports_missing_project_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = assess_project(Path(tmp))
            self.assertFalse(report["ready"])
            self.assertEqual(report["ready_count"], 0)
            self.assertEqual(report["total_count"], len(report["checks"]))

    def test_readiness_counts_present_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for _, paths in CHECKS:
                for relative in paths:
                    path = root / relative
                    if relative == "tests":
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("synthetic test fixture", encoding="utf-8")
            deck = root / "presentation" / "Insider_Threat_Risk_Monitor.pptx"
            deck.parent.mkdir(parents=True, exist_ok=True)
            deck.write_bytes(b"fixture")
            report = assess_project(root)
            self.assertTrue(report["ready"])
            self.assertEqual(report["ready_count"], report["total_count"])

    def test_final_submission_deliverables_are_in_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = assess_project(Path(tmp))
            by_name = {item["item"]: item for item in report["checks"]}
            expected = [
                "Final academic report",
                "Viva preparation",
                "Final system validation",
                "Submission bundle builder",
                "Submission integrity verifier",
            ]
            for label in expected:
                self.assertIn(label, by_name)
                self.assertFalse(by_name[label]["ready"])


if __name__ == "__main__":
    unittest.main()
