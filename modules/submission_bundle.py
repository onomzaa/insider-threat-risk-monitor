"""Build a safe, reproducible ZIP bundle for academic project submission.

Only explicitly approved project files are included. Local databases, credentials,
logs, virtual environments, caches, and generated runtime state are excluded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_OUTPUT = Path("dist/ITRM_Submission_Bundle.zip")
ALLOWED_FILES = {
    "README.md",
    "requirements.txt",
    "LICENSE",
    "docs/ARCHITECTURE.md",
    "docs/DEFENSE_GUIDE.md",
    "docs/PRESENTATION_SLIDE_SCRIPT.md",
    "docs/FINAL_RESEARCH_REPORT.md",
    "docs/VIVA_QUESTION_BANK.md",
    "results/final_validation.json",
    "results/final_validation.md",
    "results/research_evaluation_report.md",
    "results/evaluation_metrics.csv",
    "results/scenario_predictions.csv",
    "results/threshold_analysis.csv",
    "presentation/Insider_Threat_Risk_Monitor.pptx",
}
ALLOWED_DIRS = ("modules", "dashboard", "evaluation", "tests", "scripts")
EXCLUDED_PARTS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    "node_modules", "dist", "build",
}
EXCLUDED_NAMES = {
    "analysts.json", "cases.db", "audit.log", "audit.jsonl",
    ".env", "secrets.json", "credentials.json",
}


def is_safe_relative(path: Path) -> bool:
    """Reject traversal and local/private runtime files."""
    if path.is_absolute() or ".." in path.parts:
        return False
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    if path.name in EXCLUDED_NAMES or path.name.startswith(".env"):
        return False
    return True


def approved_paths(root: Path) -> list[Path]:
    """Return existing, safe files from the project's explicit allowlist."""
    root = root.resolve()
    candidates: set[Path] = set()
    for name in ALLOWED_FILES:
        p = root / name
        if p.is_file():
            candidates.add(p)
    for directory in ALLOWED_DIRS:
        base = root / directory
        if base.is_dir():
            candidates.update(p for p in base.rglob("*") if p.is_file())
    safe = []
    for p in candidates:
        # Do not package symlinks: a link inside the repository could point outside it.
        if p.is_symlink():
            continue
        try:
            p.resolve().relative_to(root)
        except ValueError:
            continue
        rel = p.relative_to(root)
        if is_safe_relative(rel) and not any(part.startswith(".") for part in rel.parts):
            safe.append(p)
    return sorted(safe, key=lambda p: p.relative_to(root).as_posix())


def build_manifest(root: Path, files: Iterable[Path]) -> dict:
    root = root.resolve()
    entries = []
    for p in files:
        rel = p.relative_to(root).as_posix()
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        entries.append({"path": rel, "size_bytes": p.stat().st_size, "sha256": digest})
    expected = sorted(ALLOWED_FILES)
    present = {entry["path"] for entry in entries}
    return {
        "project": "Insider Threat Risk Monitor",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "included_files": entries,
        "allowlisted_files_not_present": [p for p in expected if p not in present],
        "note": "Use synthetic/demo data only. Local analyst accounts, databases, audit logs, secrets, and environment files are excluded.",
    }


def create_submission_bundle(root: Path = Path("."), output: Path = DEFAULT_OUTPUT) -> Path:
    root = root.resolve()
    output = output if output.is_absolute() else root / output
    output = output.resolve()
    files = approved_paths(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(root, files)
    manifest_text = json.dumps(manifest, indent=2)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for p in files:
            archive.write(p, p.relative_to(root).as_posix())
        archive.writestr("SUBMISSION_MANIFEST.json", manifest_text)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a safe academic submission ZIP.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="ZIP destination")
    args = parser.parse_args()
    bundle = create_submission_bundle(args.root, args.output)
    print(f"Submission bundle created: {bundle}")
    print("Only allowlisted source/docs/results/presentation files were included.")
    print("Review SUBMISSION_MANIFEST.json before sharing.")


if __name__ == "__main__":
    main()
