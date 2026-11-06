import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from modules.submission_bundle import approved_paths, create_submission_bundle, is_safe_relative


class SubmissionBundleTests(unittest.TestCase):
    def test_rejects_traversal_and_private_runtime_files(self):
        self.assertFalse(is_safe_relative(Path("../outside.txt")))
        self.assertFalse(is_safe_relative(Path("data/analysts.json")))
        self.assertFalse(is_safe_relative(Path(".env")))
        self.assertTrue(is_safe_relative(Path("modules/example.py")))

    def test_bundle_includes_allowlisted_sources_and_excludes_runtime(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "modules").mkdir()
            (root / "data").mkdir()
            (root / "docs").mkdir()
            (root / "results").mkdir()
            (root / "modules" / "sample.py").write_text("print('safe')", encoding="utf-8")
            (root / "data" / "analysts.json").write_text("secret", encoding="utf-8")
            (root / "data" / "cases.db").write_bytes(b"database")
            (root / ".env").write_text("TOKEN=secret", encoding="utf-8")
            report = root / "docs" / "FINAL_RESEARCH_REPORT.md"
            report.write_text("# Final report", encoding="utf-8")
            validation = root / "results" / "final_validation.md"
            validation.write_text("PASS", encoding="utf-8")
            output = root / "bundle.zip"

            create_submission_bundle(root, output)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertIn("modules/sample.py", names)
                self.assertIn("SUBMISSION_MANIFEST.json", names)
                self.assertIn("docs/FINAL_RESEARCH_REPORT.md", names)
                self.assertIn("results/final_validation.md", names)
                manifest = json.loads(archive.read("SUBMISSION_MANIFEST.json"))
                report_entry = next(item for item in manifest["included_files"]
                                    if item["path"] == "docs/FINAL_RESEARCH_REPORT.md")
                self.assertEqual(report_entry["sha256"], hashlib.sha256(b"# Final report").hexdigest())
                self.assertNotIn("data/analysts.json", names)
                self.assertNotIn("data/cases.db", names)
                self.assertNotIn(".env", names)

    def test_symlinked_files_are_not_packaged(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            (root / "modules").mkdir()
            secret = Path(outside) / "outside.py"
            secret.write_text("private", encoding="utf-8")
            link = root / "modules" / "linked.py"
            try:
                link.symlink_to(secret)
            except (OSError, NotImplementedError):
                self.skipTest("File symlinks are not available in this environment")
            self.assertNotIn(link, approved_paths(root))

    def test_allowlisted_missing_files_do_not_crash(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(approved_paths(Path(temp)), [])


if __name__ == "__main__":
    unittest.main()
