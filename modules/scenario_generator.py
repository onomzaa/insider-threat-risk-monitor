"""Create deterministic synthetic activity rows for defensive dashboard testing."""
from datetime import datetime, timedelta
import random

ACTIONS = ("login", "view", "download", "export", "permission_change", "login_failed")
RESOURCES = ("workstation", "report.csv", "employee_records", "payroll.csv", "server")


def generate_activity(count=100, seed=42, start=None):
    """Generate fictional rows; count is capped and seed makes results repeatable."""
    if not isinstance(count, int) or not 1 <= count <= 10000:
        raise ValueError("count must be an integer between 1 and 10000")
    rng = random.Random(seed)
    start = start or datetime(2026, 1, 1, 9, 0)
    rows = []
    for index in range(count):
        timestamp = start + timedelta(minutes=index * 7)
        action = rng.choice(ACTIONS)
        resource = rng.choice(RESOURCES)
        rows.append({
            "timestamp": timestamp.isoformat(),
            "user": f"synthetic_user_{rng.randint(1, 20):02d}",
            "role": rng.choice(("Staff", "Analyst", "HR", "IT")),
            "event": action,
            "resource": resource,
            "details": "synthetic test event",
            "after_hours": timestamp.hour < 7 or timestamp.hour >= 19,
            "sensitive": resource in ("employee_records", "payroll.csv"),
        })
    return rows
