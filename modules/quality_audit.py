"""Read-only quality audit for the ITRM academic project."""
from pathlib import Path
import ast

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "Core detection": ["modules/event_correlator.py", "modules/context_analyzer.py", "modules/risk_engine.py"],
    "Dashboard": ["dashboard/dashboard.py"],
    "Evaluation": ["evaluation/evaluate.py", "evaluation/research_report.py"],
    "Documentation": ["README.md", "docs/ARCHITECTURE.md", "docs/DEMONSTRATION_AND_DEFENSE_GUIDE.md"],
    "Tests": ["tests/test_pipeline_integration.py", "tests/test_submission_bundle.py"],
    "Submission packaging": ["modules/submission_bundle.py"],
}

def audit_project(root=ROOT):
    root = Path(root).resolve()
    rows = []
    for group, paths in REQUIRED.items():
        missing = [p for p in paths if not (root / p).is_file()]
        rows.append({"category": group, "status": "PASS" if not missing else "CHECK",
                     "required": len(paths), "missing": missing})
    py_files = [p for folder in ("modules", "dashboard", "evaluation", "tests", "scripts")
                for p in (root / folder).rglob("*.py") if (root / folder).exists()]
    syntax_errors = []
    for path in py_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            syntax_errors.append({"file": str(path.relative_to(root)), "error": str(exc)})
    rows.append({"category": "Python syntax scan", "status": "PASS" if not syntax_errors else "FAIL",
                 "required": len(py_files), "missing": syntax_errors})
    metrics = root / "results" / "evaluation_metrics.csv"
    report = root / "results" / "research_evaluation_report.md"
    rows.append({"category": "Evaluation artifacts", "status": "PASS" if metrics.is_file() and report.is_file() else "CHECK",
                 "required": 2, "missing": [p for p in ("results/evaluation_metrics.csv",
                 "results/research_evaluation_report.md") if not (root / p).is_file()]})
    return {"checks": rows, "total": len(rows),
            "passed": sum(row["status"] == "PASS" for row in rows),
            "attention": sum(row["status"] == "CHECK" for row in rows),
            "failed": sum(row["status"] == "FAIL" for row in rows),
            "ready": all(row["status"] == "PASS" for row in rows)}

def main():
    report = audit_project()
    print("ITRM FINAL QUALITY AUDIT")
    for row in report["checks"]:
        print(f"[{row['status']}] {row['category']}")
        for item in row["missing"]:
            print("  -", item)
    print(f"Summary: {report['passed']}/{report['total']} passed; "
          f"{report['attention']} attention; {report['failed']} failed")
    print("Note: static file/syntax checks only; this does not execute tests or certify security.")

if __name__ == "__main__":
    main()
