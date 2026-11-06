"""Read-only project finalization checklist and submission readiness assessment."""
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    ("Core pipeline", ["modules/event_correlator.py", "modules/context_analyzer.py", "modules/risk_engine.py"]),
    ("Dashboard", ["dashboard/dashboard.py"]),
    ("Test suite", ["tests"]),
    ("Research evaluation", ["evaluation/evaluate.py", "data/labeled_evaluation_scenarios.csv"]),
    ("Architecture documentation", ["docs/ARCHITECTURE.md"]),
    ("Defense guide", ["docs/DEMONSTRATION_AND_DEFENSE_GUIDE.md"]),
    ("Presentation script", ["docs/PRESENTATION_SLIDE_SCRIPT.md"]),
    ("PowerPoint generator", ["scripts/generate_presentation.py"]),
    ("Synthetic demo", ["modules/demo_scenario.py", "tests/test_demo_scenario.py"]),
]

def assess_project(root=ROOT):
    results = []
    for label, paths in CHECKS:
        missing = [p for p in paths if not (root / p).exists()]
        results.append({"item": label, "ready": not missing, "missing": missing})
    deps = {
        "python-pptx": importlib.util.find_spec("pptx") is not None,
        "reportlab": importlib.util.find_spec("reportlab") is not None,
    }
    pptx_path = root / "presentation" / "Insider_Threat_Risk_Monitor.pptx"
    results.append({"item": "Generated PowerPoint", "ready": pptx_path.exists(),
                    "missing": [] if pptx_path.exists() else ["presentation/Insider_Threat_Risk_Monitor.pptx"]})
    return {"checks": results, "dependencies": deps,
            "ready_count": sum(r["ready"] for r in results),
            "total_count": len(results),
            "ready": all(r["ready"] for r in results)}

def main():
    report = assess_project()
    print("\nPROJECT FINALIZATION CHECK")
    print("=" * 32)
    for item in report["checks"]:
        status = "READY" if item["ready"] else "MISSING"
        print(f"[{status:7}] {item['item']}")
        for path in item["missing"]:
            print(f"         - {path}")
    print("\nOptional dependencies:")
    for name, ok in report["dependencies"].items():
        print(f"[{'OK' if ok else 'NOT INSTALLED'}] {name}")
    print(f"\nFiles present: {report['ready_count']}/{report['total_count']}")
    print("Assessment: " + ("FILE CHECKS COMPLETE" if report["ready"] else "ACTION REQUIRED"))
    print("Note: This checks file presence only; run tests and review outputs separately.")

if __name__ == "__main__":
    main()
