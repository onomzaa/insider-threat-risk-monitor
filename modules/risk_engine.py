"""Transparent rule-based risk score (0-100), suitable for a student prototype."""

def score_incident(events, context_results=None):
    context_results = context_results or []
    score = 0
    reasons = []
    actions = {str(e.get("action", "")).lower() for e in events}

    weights = {"download": 15, "export": 25, "delete": 20, "share": 20,
               "login_failed": 5, "permission_change": 25}
    for action in actions:
        if action in weights:
            score += weights[action]
            reasons.append(f"Observed action: {action} (+{weights[action]})")

    if len(events) >= 3:
        score += 10
        reasons.append("Three or more events correlated (+10)")
    if len(events) >= 5:
        score += 10
        reasons.append("Five or more events in incident (+10)")

    for context in context_results:
        if context.get("outside_role_scope"):
            score += 20
            reasons.extend(context.get("context_reasons", [])[:1])
        if context.get("after_hours"):
            score += 10
            reasons.append("After-hours activity (+10)")
        if context.get("sensitive"):
            score += 15
            reasons.append("Sensitive resource (+15)")

    score = min(100, score)
    level = "High" if score >= 70 else "Medium" if score >= 40 else "Low"
    return {"risk_score": score, "risk_level": level,
            "explanation": list(dict.fromkeys(reasons)) or ["No configured risk indicators"]}
