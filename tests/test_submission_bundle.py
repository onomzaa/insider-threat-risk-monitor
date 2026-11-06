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
            (root / "modules" / "sample.py").write_text("print('safe')", encoding="utf-8")
            (root / "data" / "analysts.json").write_text("secret", encoding="utf-8")
            (root / "data" / "cases.db").write_bytes(b"database")
            (root / ".env").write_text("TOKEN=secret", encoding="utf-8")
            output = root / "bundle.zip"

            create_submission_bundle(root, output)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertIn("modules/sample.py", names)
                self.assertIn("SUBMISSION_MANIFEST.json", names)
                self.assertNotIn("data/analysts.json", names)
                self.assertNotIn("data/cases.db", names)
                self.assertNotIn(".env", names)

    def test_allowlisted_missing_files_do_not_crash(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(approved_paths(Path(temp)), [])


if __name__ == "__main__":
    unittest.main()
