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

from datetime import datetime
from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident
from modules.alert_manager import build_alert, set_disposition

def make_event(user, ts, action, resource="report.csv", after=False, sensitive=False):
    return {"employee_id":user,"timestamp":ts,"action":action,"resource":resource,
            "after_hours":after,"sensitive":sensitive}

def test_normal_activity_stays_low():
    events=[make_event("u1","2026-11-01T09:00:00","login","workstation"),
            make_event("u1","2026-11-01T09:05:00","view")]
    incident=correlate_events(events)[0]
    assert score_incident(incident["events"])["risk_level"]=="Low"

def test_suspicious_transfer_scores_high():
    events=[make_event("u2","2026-11-01T22:00:00","download","payroll.csv",True,True),
            make_event("u2","2026-11-01T22:05:00","export","payroll.csv",True,True),
            make_event("u2","2026-11-01T22:10:00","share","payroll.csv",True,True)]
    incident=correlate_events(events)[0]
    profile={"u2":{"role":"staff","allowed_resources":["workstation"]}}
    contexts=[analyze_context(e,profile) for e in incident["events"]]
    result=score_incident(incident["events"],contexts)
    assert result["risk_score"]>=70

def test_alert_disposition_preserves_original():
    incident={"employee_id":"u3","events":[{"action":"export"}],
              "first_seen":datetime.fromisoformat("2026-11-01T10:00:00")}
    alert=build_alert(incident,{"risk_score":55,"risk_level":"Medium","explanation":["Export"]})
    updated=set_disposition(alert,"Under Review","Check authorization")
    assert updated["status"]=="Under Review"
    assert alert["status"]=="Open"
