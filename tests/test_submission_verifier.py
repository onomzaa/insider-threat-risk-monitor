import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from modules.submission_verifier import verify_submission_bundle, write_verification_report


class SubmissionVerifierTests(unittest.TestCase):
    def _make_bundle(self, path: Path, payload: bytes = b"safe content") -> None:
        manifest = {
            "project": "Insider Threat Risk Monitor",
            "included_files": [{
                "path": "docs/example.md",
                "size_bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }],
        }
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("docs/example.md", payload)
            archive.writestr("SUBMISSION_MANIFEST.json", json.dumps(manifest))

    def test_valid_bundle_passes_hash_and_size_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle.zip"
            self._make_bundle(bundle)
            report = verify_submission_bundle(bundle)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["checked_files"], 1)
            self.assertEqual(report["issues"], [])

    def test_tampered_payload_fails_hash_check(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle.zip"
            self._make_bundle(bundle)
            with zipfile.ZipFile(bundle, "a") as archive:
                archive.writestr("docs/example.md", b"changed")
            report = verify_submission_bundle(bundle)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("duplicate" in issue.lower() or "hash" in issue.lower()
                                for issue in report["issues"]))

    def test_unlisted_sensitive_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle.zip"
            self._make_bundle(bundle)
            with zipfile.ZipFile(bundle, "a") as archive:
                archive.writestr("data/analysts.json", b"private")
            report = verify_submission_bundle(bundle)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("prohibited" in issue.lower() or "manifest" in issue.lower()
                                for issue in report["issues"]))

    def test_traversal_and_windows_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle.zip"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("../outside.txt", b"x")
                archive.writestr("C:/private.txt", b"x")
                archive.writestr("SUBMISSION_MANIFEST.json", json.dumps({"included_files": []}))
            report = verify_submission_bundle(bundle)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("unsafe" in issue.lower() for issue in report["issues"]))

    def test_malformed_manifest_entry_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / "bundle.zip"
            with zipfile.ZipFile(bundle, "w") as archive:
                archive.writestr("docs/example.md", b"x")
                archive.writestr("SUBMISSION_MANIFEST.json", json.dumps({
                    "included_files": [{
                        "path": "docs/example.md",
                        "size_bytes": "one",
                        "sha256": "not-a-hash",
                    }]
                }))
            report = verify_submission_bundle(bundle)
            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("invalid" in issue.lower() for issue in report["issues"]))

    def test_missing_bundle_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as temp:
            report = verify_submission_bundle(Path(temp) / "missing.zip")
            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(report["checked_files"], 0)

    def test_reports_are_written(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bundle = root / "bundle.zip"
            self._make_bundle(bundle)
            report = verify_submission_bundle(bundle)
            json_path, md_path = root / "out/report.json", root / "out/report.md"
            write_verification_report(report, json_path, md_path)
            self.assertEqual(json.loads(json_path.read_text())["status"], "PASS")
            self.assertIn("Submission Bundle Verification", md_path.read_text())


if __name__ == "__main__":
    unittest.main()
