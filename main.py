"""CLI entry point: load sample logs and print baseline alerts."""
from modules.data_loader import load_activity
from modules.baseline_detector import detect_baseline

if __name__ == "__main__":
    events = load_activity()
    alerts = detect_baseline(events)
    print(f"Loaded {len(events)} activity records; baseline produced {len(alerts)} alerts.")
    if not alerts.empty:
        print(alerts[["timestamp", "user", "event", "score", "reasons"]].to_string(index=False))
