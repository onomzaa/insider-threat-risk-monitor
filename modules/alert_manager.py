"""Alert manager: create review-ready alerts and track analyst disposition."""
from datetime import datetime, timezone

VALID_STATUSES = {"Open", "Under Review", "Resolved", "False Positive"}

def build_alert(incident, risk_result, context_results=None):
    context_results = context_results or []
    events = incident.get("events", [])
    score = int(risk_result.get("risk_score", 0))
    return {
        "alert_id": f"AL-{incident.get('employee_id', 'UNKNOWN')}-{incident.get('first_seen').strftime('%Y%m%d%H%M')}",
        "employee_id": incident.get("employee_id", "UNKNOWN"),
        "event_count": len(events),
        "risk_score": score,
        "risk_level": risk_result.get("risk_level", "Low"),
        "reasons": list(risk_result.get("explanation", [])),
        "risk_factors": list(risk_result.get("factors", [])),
        "context": context_results,
        "status": "Open",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "analyst_note": "",
    }

def set_disposition(alert, status, note=""):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    updated = dict(alert)
    updated["status"] = status
    updated["analyst_note"] = str(note).strip()
    updated["reviewed_at"] = datetime.now(timezone.utc).isoformat()
    return updated

def priority(alert):
    """Sort key: high risk first, then medium, then low; open alerts before closed."""
    risk_order = {"High": 0, "Medium": 1, "Low": 2}
    status_order = {"Open": 0, "Under Review": 1, "Resolved": 2, "False Positive": 3}
    return (status_order.get(alert.get("status", "Open"), 0),
            risk_order.get(alert.get("risk_level", "Low"), 2),
            -int(alert.get("risk_score", 0)))


def filter_alerts(alerts, risk_level="All", status="All", query=""):
    """Return alerts matching queue filters; search Alert ID and employee ID."""
    needle = str(query).strip().lower()
    return [alert for alert in alerts
            if (risk_level == "All" or alert.get("risk_level", "Low") == risk_level)
            and (status == "All" or alert.get("status", "Open") == status)
            and (not needle or needle in str(alert.get("alert_id", "")).lower()
                 or needle in str(alert.get("employee_id", "")).lower())]
