import tempfile
import unittest
from pathlib import Path
from modules.quality_audit import audit_project

class QualityAuditTests(unittest.TestCase):
    def test_reports_missing_files_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            result = audit_project(Path(temp))
            self.assertFalse(result["ready"])
            self.assertGreater(result["attention"], 0)

    def test_detects_python_syntax_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "modules").mkdir()
            (root / "modules" / "broken.py").write_text("def nope(:\n", encoding="utf-8")
            result = audit_project(root)
            syntax = next(row for row in result["checks"] if row["category"] == "Python syntax scan")
            self.assertEqual(syntax["status"], "FAIL")
            self.assertEqual(len(syntax["missing"]), 1)

if __name__ == "__main__":
    unittest.main()
