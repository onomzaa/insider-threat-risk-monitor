"""Verify a generated ITRM submission ZIP without extracting its contents."""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path, PurePosixPath

FORBIDDEN_NAMES = {
    "analysts.json", "cases.db", "audit.log", "audit.jsonl",
    ".env", "secrets.json", "credentials.json",
}
FORBIDDEN_PARTS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}


def _safe_archive_path(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name)
        and not path.is_absolute()
        and ".." not in path.parts
        and not any(part in FORBIDDEN_PARTS for part in path.parts)
        and path.name not in FORBIDDEN_NAMES
        and not path.name.startswith(".env")
    )


def verify_submission_bundle(bundle_path: Path) -> dict:
    """Return a machine-readable integrity and safety verification report."""
    bundle_path = Path(bundle_path)
    issues: list[str] = []
    checked_files = 0
    manifest = None

    if not bundle_path.is_file():
        return {
            "bundle": str(bundle_path),
            "status": "FAIL",
            "checked_files": 0,
            "issues": ["Submission ZIP does not exist."],
        }

    try:
        with zipfile.ZipFile(bundle_path, "r") as archive:
            bad_member = archive.testzip()
            if bad_member:
                issues.append(f"ZIP CRC check failed for: {bad_member}")

            names = archive.namelist()
            if len(names) != len(set(names)):
                issues.append("Archive contains duplicate member names.")

            for name in names:
                if not _safe_archive_path(name):
                    issues.append(f"Unsafe or prohibited archive path: {name}")

            if "SUBMISSION_MANIFEST.json" not in names:
                issues.append("SUBMISSION_MANIFEST.json is missing.")
            else:
                try:
                    manifest = json.loads(archive.read("SUBMISSION_MANIFEST.json"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    issues.append("Submission manifest is not valid JSON.")

            if isinstance(manifest, dict):
                entries = manifest.get("included_files")
                if not isinstance(entries, list):
                    issues.append("Manifest included_files must be a list.")
                    entries = []

                declared: set[str] = set()
                for entry in entries:
                    if not isinstance(entry, dict):
                        issues.append("Manifest contains a malformed file entry.")
                        continue
                    name = entry.get("path")
                    expected_hash = entry.get("sha256")
                    expected_size = entry.get("size_bytes")
                    if not isinstance(name, str) or not _safe_archive_path(name):
                        issues.append(f"Manifest contains an unsafe path: {name!r}")
                        continue
                    if name in declared:
                        issues.append(f"Manifest contains a duplicate path: {name}")
                        continue
                    declared.add(name)
                    if name not in names:
                        issues.append(f"Manifest file is missing from ZIP: {name}")
                        continue
                    payload = archive.read(name)
                    checked_files += 1
                    actual_hash = hashlib.sha256(payload).hexdigest()
                    if actual_hash != expected_hash:
                        issues.append(f"SHA-256 mismatch: {name}")
                    if len(payload) != expected_size:
                        issues.append(f"File size mismatch: {name}")

                actual_files = set(names) - {"SUBMISSION_MANIFEST.json"}
                unlisted = actual_files - declared
                missing = declared - actual_files
                if unlisted:
                    issues.append("ZIP contains files absent from manifest: " + ", ".join(sorted(unlisted)))
                if missing:
                    issues.append("Manifest lists files absent from ZIP: " + ", ".join(sorted(missing)))
            elif manifest is not None:
                issues.append("Submission manifest must contain a JSON object.")
    except (zipfile.BadZipFile, OSError) as exc:
        issues.append(f"Unable to read submission ZIP: {exc}")

    return {
        "bundle": str(bundle_path),
        "status": "PASS" if not issues else "FAIL",
        "checked_files": checked_files,
        "issues": issues,
    }


def write_verification_report(report: dict, json_path: Path, markdown_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Submission Bundle Verification",
        "",
        f"- **Status:** {report['status']}",
        f"- **Bundle:** {report['bundle']}",
        f"- **Files checked:** {report['checked_files']}",
        "",
        "## Findings",
    ]
    lines.extend([f"- {issue}" for issue in report["issues"]] or ["- No integrity or packaging issues found."])
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify an ITRM submission ZIP.")
    parser.add_argument("--bundle", type=Path, default=Path("dist/ITRM_Submission_Bundle.zip"))
    parser.add_argument("--json", dest="json_path", type=Path, default=Path("results/submission_verification.json"))
    parser.add_argument("--markdown", dest="markdown_path", type=Path, default=Path("results/submission_verification.md"))
    args = parser.parse_args()
    report = verify_submission_bundle(args.bundle)
    write_verification_report(report, args.json_path, args.markdown_path)
    print(f"Submission bundle verification: {report['status']}")
    print(f"Files checked: {report['checked_files']}")
    for issue in report["issues"]:
        print(f"- {issue}")
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
