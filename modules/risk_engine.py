"""Transparent, explainable incident risk scoring (0-100).

Context indicators are applied once per incident, not once per event, to avoid
inflating a score when several events share the same after-hours/sensitive flag.
A score is a review priority, never proof of malicious intent.
"""
def score_incident(events, context_results=None):
    context_results = context_results or []
    score = 0
    reasons = []
    actions = {str(e.get("action", "")).lower() for e in events}
    weights = {"download":15,"export":25,"delete":20,"share":20,
               "login_failed":5,"permission_change":25}
    for action in sorted(actions):
        if action in weights:
            score += weights[action]
            reasons.append(f"Observed action: {action} (+{weights[action]})")

    if len(events) >= 3:
        score += 10; reasons.append("Three or more events correlated (+10)")
    if len(events) >= 5:
        score += 10; reasons.append("Five or more events in incident (+10)")

    # Apply each context factor once per incident.
    if any(c.get("outside_role_scope") for c in context_results):
        score += 20; reasons.append("At least one activity outside listed role scope (+20)")
    if any(c.get("after_hours") for c in context_results):
        score += 10; reasons.append("After-hours activity (+10)")
    if any(c.get("sensitive") for c in context_results):
        score += 15; reasons.append("Sensitive resource involved (+15)")

    score = min(100, score)
    level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    return {"risk_score":score,"risk_level":level,
            "explanation":reasons or ["No configured risk indicators"]}
