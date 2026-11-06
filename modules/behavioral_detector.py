"""Explainable behavioral anomaly checks over authorized/synthetic activity records.

These heuristics flag deviations for human review; they are not proof of misconduct.
"""
from collections import Counter, defaultdict


def detect_behavioral_anomalies(records, min_peer_count=2):
    """Compare each employee's event/resource patterns with same-role peers.

    Input records use employee_id, role, action, resource, timestamp and optional
    after_hours. Output is a list of explainable anomaly dictionaries.
    """
    if min_peer_count < 1:
        raise ValueError("min_peer_count must be at least 1")
    employees = defaultdict(list)
    role_users = defaultdict(set)
    for record in records:
        employee = str(record.get("employee_id", "UNKNOWN"))
        role = str(record.get("role", "unknown")).lower()
        employees[employee].append(record)
        role_users[role].add(employee)

    role_actions = defaultdict(Counter)
    role_resources = defaultdict(Counter)
    user_actions = defaultdict(Counter)
    user_resources = defaultdict(Counter)
    for employee, events in employees.items():
        role = str(events[0].get("role", "unknown")).lower()
        for event in events:
            action = str(event.get("action", "unknown")).lower()
            resource = str(event.get("resource", "unknown")).lower()
            user_actions[employee][action] += 1
            user_resources[employee][resource] += 1
            role_actions[role][action] += 1
            role_resources[role][resource] += 1

    output = []
    for employee, events in employees.items():
        role = str(events[0].get("role", "unknown")).lower()
        peers = role_users[role] - {employee}
        if len(peers) < min_peer_count:
            continue
        for action, count in user_actions[employee].items():
            peer_total = sum(user_actions[p][action] for p in peers)
            peer_event_total = sum(sum(user_actions[p].values()) for p in peers)
            peer_rate = peer_total / peer_event_total if peer_event_total else 0
            own_rate = count / max(1, len(events))
            if count >= 2 and peer_rate == 0:
                output.append({"employee_id": employee, "kind": "Role-unusual action",
                    "value": action, "observed": count, "peer_rate": peer_rate,
                    "explanation": f"{employee} recorded {count} '{action}' events; same-role peers recorded none."})
            elif count >= 2 and own_rate >= max(0.5, peer_rate * 3):
                output.append({"employee_id": employee, "kind": "Elevated action share",
                    "value": action, "observed": round(own_rate, 3), "peer_rate": round(peer_rate, 3),
                    "explanation": f"'{action}' represents {own_rate:.0%} of this employee's events versus {peer_rate:.0%} among same-role peers."})
        for resource, count in user_resources[employee].items():
            peer_count = sum(user_resources[p][resource] for p in peers)
            if count >= 2 and peer_count == 0:
                output.append({"employee_id": employee, "kind": "Role-unusual resource",
                    "value": resource, "observed": count, "peer_rate": 0,
                    "explanation": f"{employee} accessed '{resource}' {count} times; same-role peers recorded no access."})
        after_hours = sum(bool(e.get("after_hours")) for e in events)
        if after_hours >= 2:
            peer_events = [e for p in peers for e in employees[p]]
            peer_rate = sum(bool(e.get("after_hours")) for e in peer_events) / max(1, len(peer_events))
            own_rate = after_hours / max(1, len(events))
            if own_rate >= max(0.5, peer_rate * 3):
                output.append({"employee_id": employee, "kind": "After-hours concentration",
                    "value": "after_hours", "observed": round(own_rate, 3), "peer_rate": round(peer_rate, 3),
                    "explanation": f"{own_rate:.0%} of this employee's events are after-hours versus {peer_rate:.0%} among same-role peers."})
    return output
