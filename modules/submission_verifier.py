"""Verify a generated ITRM submission ZIP without extracting its contents."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import zipfile
from pathlib import Path, PurePosixPath

FORBIDDEN_NAMES = {
    "analysts.json", "cases.db", "audit.log", "audit.jsonl",
    ".env", "secrets.json", "credentials.json",
}
FORBIDDEN_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "node_modules", "dist", "build",
}
MANIFEST_NAME = "SUBMISSION_MANIFEST.json"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _safe_archive_path(name: str) -> bool:
    """Reject absolute paths, traversal, Windows paths, and private runtime files."""
    if not name or "\\" in name or name.startswith("/"):
        return False
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        return False
    if path.parts and ":" in path.parts[0]:
        return False
    if any(part in FORBIDDEN_PARTS for part in path.parts):
        return False
    if any(part in FORBIDDEN_NAMES or part.startswith(".env") for part in path.parts):
        return False
    return True


def verify_submission_bundle(bundle_path: Path) -> dict:
    """Return an integrity and packaging-safety report; never extract archive files."""
    bundle_path = Path(bundle_path)
    issues: list[str] = []
    checked_files = 0

    if not bundle_path.is_file():
        return {
            "bundle": str(bundle_path),
            "status": "FAIL",
            "checked_files": 0,
            "issues": ["Submission ZIP does not exist."],
        }

    try:
        with zipfile.ZipFile(bundle_path, "r") as archive:
            infos = archive.infolist()
            names = [info.filename for info in infos]
            if len(names) != len(set(names)):
                issues.append("Archive contains duplicate member names.")

            for info in infos:
                name = info.filename
                if name != MANIFEST_NAME and not _safe_archive_path(name):
                    issues.append(f"Unsafe or prohibited archive path: {name}")
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    issues.append(f"Archive contains a symlink entry: {name}")

            bad_member = archive.testzip()
            if bad_member:
                issues.append(f"ZIP CRC check failed for: {bad_member}")

            if MANIFEST_NAME not in names:
                issues.append(f"{MANIFEST_NAME} is missing.")
                manifest = None
            else:
                try:
                    manifest = json.loads(archive.read(MANIFEST_NAME).decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    manifest = None
                    issues.append("Submission manifest is not valid UTF-8 JSON.")

            if manifest is not None:
                if not isinstance(manifest, dict):
                    issues.append("Submission manifest must contain a JSON object.")
                else:
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
                        if not isinstance(expected_hash, str) or not _SHA256_RE.fullmatch(expected_hash):
                            issues.append(f"Manifest has an invalid SHA-256 value: {name}")
                            continue
                        if isinstance(expected_size, bool) or not isinstance(expected_size, int) or expected_size < 0:
                            issues.append(f"Manifest has an invalid file size: {name}")
                            continue
                        if name not in names:
                            issues.append(f"Manifest file is missing from ZIP: {name}")
                            continue

                        payload = archive.read(name)
                        checked_files += 1
                        if hashlib.sha256(payload).hexdigest() != expected_hash:
                            issues.append(f"SHA-256 mismatch: {name}")
                        if len(payload) != expected_size:
                            issues.append(f"File size mismatch: {name}")

                    actual_files = set(names) - {MANIFEST_NAME}
                    unlisted = actual_files - declared
                    missing = declared - actual_files
                    if unlisted:
                        issues.append("ZIP contains files absent from manifest: " + ", ".join(sorted(unlisted)))
                    if missing:
                        issues.append("Manifest lists files absent from ZIP: " + ", ".join(sorted(missing)))
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
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
    lines.extend([
        "",
        "A PASS confirms package integrity and basic packaging safeguards only; it does not certify project security or research validity.",
        "",
    ])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")


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
