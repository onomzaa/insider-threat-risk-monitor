import tempfile
import unittest
from pathlib import Path
from modules.final_validation import run_validation, save_report

class FinalValidationTests(unittest.TestCase):
    def test_runs_test_suite_and_returns_status(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            (root/"tests").mkdir()
            (root/"tests"/"test_sample.py").write_text(
                "import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n",
                encoding="utf-8")
            result=run_validation(root,timeout=20)
            self.assertTrue(result["passed"])
            self.assertEqual(result["status"],"PASS")
            self.assertIn("test_ok",result["output"])

    def test_saves_json_and_markdown(self):
        with tempfile.TemporaryDirectory() as temp:
            report={"timestamp_utc":"now","command":"test","status":"FAIL",
                    "passed":False,"return_code":1,"error":None,"output":"sample failure"}
            json_path,md_path=save_report(report,temp)
            self.assertTrue(json_path.is_file())
            self.assertIn("sample failure",md_path.read_text(encoding="utf-8"))

if __name__=="__main__":
    unittest.main()
