"""Fixed fictional scenario for a classroom detection walkthrough."""
from datetime import datetime
from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident
from modules.alert_manager import build_alert


def run_demo_scenario():
    """Run a reproducible synthetic case; never reads real activity data."""
    events = [
        {"employee_id":"demo_finance_user","timestamp":"2026-02-03T20:05:00",
         "action":"permission_change","resource":"payroll","details":"Synthetic demo event"},
        {"employee_id":"demo_finance_user","timestamp":"2026-02-03T20:12:00",
         "action":"download","resource":"payroll","details":"Synthetic demo event",
         "sensitive":True,"after_hours":True},
        {"employee_id":"demo_finance_user","timestamp":"2026-02-03T20:18:00",
         "action":"export","resource":"payroll","details":"Synthetic demo event",
         "sensitive":True,"after_hours":True},
        {"employee_id":"demo_finance_user","timestamp":"2026-02-03T20:23:00",
         "action":"share","resource":"payroll","details":"Synthetic demo event",
         "sensitive":True,"after_hours":True},
    ]
    profile = {"demo_finance_user":{"role":"finance",
                                    "allowed_resources":["workstation","finance_report"]}}
    incidents = correlate_events(events, window_minutes=30)
    results=[]
    for incident in incidents:
        contexts=[analyze_context(event,profile) for event in incident["events"]]
        risk=score_incident(incident["events"],contexts)
        alert=build_alert(incident,risk,contexts)
        results.append({"incident":incident,"contexts":contexts,
                        "risk":risk,"alert":alert})
    return {
        "title":"After-hours sensitive-data activity (fictional)",
        "events":events,
        "steps":[
            {"title":"1 • Activity events","detail":"Four fictional events occur for one demo account."},
            {"title":"2 • Event correlation","detail":"Events inside the configured 30-minute window form one incident."},
            {"title":"3 • Context analysis","detail":"Role scope, after-hours timing, and sensitive resource indicators are checked."},
            {"title":"4 • Explainable scoring","detail":"Action and context factors contribute to a transparent risk score."},
            {"title":"5 • Analyst decision","detail":"The alert is a review prompt; a human validates context before disposition."},
        ],
        "results":results,
    }
