"""Transparent single-event baseline rules."""
import pandas as pd

AFTER_HOURS_START, AFTER_HOURS_END = 20, 6


def detect_baseline(df):
    alerts = []
    for _, row in df.iterrows():
        reasons = []
        hour = row["timestamp"].hour
        if hour >= AFTER_HOURS_START or hour < AFTER_HOURS_END:
            reasons.append("Activity outside normal hours (20:00–06:00)")
        if str(row["event"]).lower() in {"usb_copy", "privilege_change"}:
            reasons.append(f"Sensitive event: {row['event']}")
        if reasons:
            alerts.append({"timestamp": row["timestamp"], "user": row["user"], "role": row["role"],
                           "event": row["event"], "resource": row["resource"],
                           "score": min(100, 30 * len(reasons)), "reasons": reasons,
                           "source": "baseline"})
    return pd.DataFrame(alerts)
