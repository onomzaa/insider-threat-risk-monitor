"""Read-only readiness checks for the local research prototype."""
from pathlib import Path
from importlib.util import find_spec


def check_system_health(project_root):
    """Return component status rows; checks availability, not production security."""
    root = Path(project_root)
    checks = []

    def add(name, ok, detail):
        checks.append({"Component": name, "Status": "Ready" if ok else "Attention",
                       "Details": detail})

    activity = root / "data" / "activity_logs.csv"
    add("Activity dataset", activity.is_file(),
        "activity_logs.csv found" if activity.is_file() else "Missing data/activity_logs.csv")

    config = root / "data" / "system_config.json"
    add("Configuration", config.is_file(),
        "Saved settings found; defaults are used when absent" if config.is_file()
        else "Using validated built-in defaults")

    database = root / "data" / "cases.db"
    add("Local case database", True,
        "Database exists" if database.is_file()
        else "Database will be initialized when case/audit features are used")

    metrics = root / "results" / "evaluation_metrics.csv"
    add("Evaluation results", metrics.is_file(),
        "Synthetic metrics file found" if metrics.is_file()
        else "Not generated; run python -m evaluation.evaluate")

    add("PDF dependency", find_spec("reportlab") is not None,
        "ReportLab installed" if find_spec("reportlab") is not None
        else "Missing; install with python -m pip install reportlab")

    required = ["modules/auth.py", "modules/risk_engine.py",
                "modules/event_correlator.py", "modules/alert_manager.py",
                "modules/case_store.py", "modules/audit_log.py"]
    missing = [item for item in required if not (root / item).is_file()]
    add("Core modules", not missing,
        "Required files present" if not missing else "Missing: " + ", ".join(missing))

    return checks
