import tempfile
import unittest
from pathlib import Path
from modules.system_health import check_system_health


class SystemHealthTests(unittest.TestCase):
    def test_missing_files_are_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = check_system_health(Path(tmp))
            by_name = {row["Component"]: row for row in rows}
            self.assertEqual(by_name["Activity dataset"]["Status"], "Attention")
            self.assertEqual(by_name["Core modules"]["Status"], "Attention")
            self.assertIn("Evaluation results", by_name)
            self.assertIn("PDF dependency", by_name)

    def test_available_activity_file_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "data" / "activity_logs.csv").write_text("timestamp,user\n", encoding="utf-8")
            rows = check_system_health(root)
            activity = next(row for row in rows if row["Component"] == "Activity dataset")
            self.assertEqual(activity["Status"], "Ready")


if __name__ == "__main__":
    unittest.main()
