"""Transparent, explainable incident risk scoring (0-100).

Scores prioritize analyst review; they are not proof of malicious intent.
Action and context factors are capped/combined to avoid double-counting.
"""
def score_incident(events, context_results=None):
    context_results = context_results or []
    factors = []
    actions = [str(e.get("action", "")).strip().lower() for e in events]
    unique_actions = set(actions)

    weights = {"download": 15, "export": 25, "delete": 20,
               "share": 20, "login_failed": 5, "permission_change": 25}
    for action in sorted(unique_actions):
        if action in weights:
            factors.append({"factor": f"Action: {action}", "points": weights[action]})

    if len(events) >= 3:
        factors.append({"factor": "Three or more correlated events", "points": 10})
    if len(events) >= 5:
        factors.append({"factor": "Five or more events in incident", "points": 10})

    # A privilege-change -> data-access -> sharing sequence is more concerning
    # than the individual actions; count it once per incident.
    if ("permission_change" in unique_actions and
            ({"download", "export"} & unique_actions) and "share" in unique_actions):
        factors.append({"factor": "Privilege change + data transfer + sharing sequence", "points": 15})

    if any(c.get("outside_role_scope") for c in context_results):
        factors.append({"factor": "Activity outside listed role scope", "points": 20})
    if any(c.get("after_hours") for c in context_results):
        factors.append({"factor": "After-hours activity", "points": 10})
    if any(c.get("sensitive") for c in context_results):
        factors.append({"factor": "Sensitive resource involved", "points": 15})

    raw_score = sum(item["points"] for item in factors)
    score = min(100, raw_score)
    level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    explanation = [f"{item['factor']} (+{item['points']})" for item in factors]
    if score != raw_score:
        explanation.append(f"Score capped at 100 (raw total: {raw_score})")
    return {"risk_score": score, "raw_score": raw_score, "risk_level": level,
            "factors": factors, "explanation": explanation or ["No configured risk indicators"]}
