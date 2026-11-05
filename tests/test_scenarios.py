"""Basic tests for activity loading and baseline rules."""
from modules.data_loader import load_activity
from modules.baseline_detector import detect_baseline


def test_sample_data_loads():
    df = load_activity()
    assert len(df) > 0
    assert {"timestamp", "user", "event"}.issubset(df.columns)


def test_sensitive_events_trigger_baseline():
    alerts = detect_baseline(load_activity())
    assert not alerts.empty
    assert alerts["event"].isin(["usb_copy", "privilege_change"]).any()
