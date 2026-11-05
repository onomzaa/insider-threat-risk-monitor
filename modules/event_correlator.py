"""Group suspicious events into employee incidents using a rolling time window."""
from datetime import datetime, timedelta

def correlate_events(events, window_minutes=60):
    """Return incident dictionaries. Each event must include employee_id and timestamp."""
    parsed = []
    for event in events:
        try:
            ts = datetime.fromisoformat(str(event["timestamp"]).replace("Z", "+00:00"))
        except (KeyError, ValueError):
            continue
        parsed.append((ts, event))
    parsed.sort(key=lambda item: item[0])

    incidents = []
    active = {}
    for ts, event in parsed:
        employee = str(event.get("employee_id", "UNKNOWN"))
        previous = active.get(employee)
        if previous and ts - previous["last_seen"] <= timedelta(minutes=window_minutes):
            previous["events"].append(event)
            previous["last_seen"] = ts
        else:
            incident = {"employee_id": employee, "events": [event],
                        "first_seen": ts, "last_seen": ts}
            incidents.append(incident)
            active[employee] = incident
    return incidents
