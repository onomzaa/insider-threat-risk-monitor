"""Add simple role/access context to activity events; no event alone proves intent."""

def analyze_context(event, user_profiles=None):
    user_profiles = user_profiles or {}
    profile = user_profiles.get(str(event.get("employee_id", "")), {})
    role = str(profile.get("role", "unknown")).lower()
    resource = str(event.get("resource", "")).lower()
    action = str(event.get("action", "")).lower()

    expected_resources = [str(x).lower() for x in profile.get("allowed_resources", [])]
    outside_role_scope = bool(expected_resources and resource and resource not in expected_resources)
    after_hours = bool(event.get("after_hours", False))
    sensitive = bool(event.get("sensitive", False) or "sensitive" in resource)

    reasons = []
    if outside_role_scope:
        reasons.append("Resource is outside the user's listed role scope")
    if after_hours:
        reasons.append("Activity occurred outside normal working hours")
    if sensitive:
        reasons.append("Activity involved a sensitive resource")
    if action in {"download", "export", "delete", "share"}:
        reasons.append(f"Action '{action}' may require review")

    return {"role": role, "outside_role_scope": outside_role_scope,
            "after_hours": after_hours, "sensitive": sensitive,
            "context_reasons": reasons}
