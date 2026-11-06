import tempfile
import unittest
from pathlib import Path
from modules.project_finalization import assess_project

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
            for _, paths in __import__("modules.project_finalization", fromlist=["CHECKS"]).CHECKS:
                for relative in paths:
                    path = root / relative
                    if relative == "tests":
                        path.mkdir(parents=True, exist_ok=True)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("synthetic test fixture", encoding="utf-8")
            (root / "presentation").mkdir()
            (root / "presentation" / "Insider_Threat_Risk_Monitor.pptx").write_bytes(b"fixture")
            report = assess_project(root)
            self.assertTrue(report["ready"])
            self.assertEqual(report["ready_count"], report["total_count"])

if __name__ == "__main__":
    unittest.main()
