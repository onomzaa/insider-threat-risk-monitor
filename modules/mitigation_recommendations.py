"""Defensive recommendations mapped to explainable alert risk factors."""
def recommend_mitigations(alert):
    """Return prioritized review actions; recommendations never take automatic action."""
    reasons = [str(x).lower() for x in alert.get("reasons", [])]
    factors = [str(x.get("factor", "")).lower() for x in alert.get("risk_factors", [])]
    text = " ".join(reasons + factors)
    recommendations = []
    def add(priority, title, rationale, steps):
        recommendations.append({"priority": priority, "title": title,
                               "rationale": rationale, "steps": steps})
    if any(x in text for x in ["permission", "privilege", "role scope"]):
        add("High", "Review access and privilege changes",
            "The alert includes a permission or role-scope indicator.",
            "Verify the change against an approved request; have an authorized owner review current access.")
    if any(x in text for x in ["export", "download", "data transfer", "sharing", "share"]):
        add("High", "Validate data movement",
            "The alert includes a download, export, or sharing indicator.",
            "Check approved business purpose and destination using authorized logs; preserve relevant references.")
    if any(x in text for x in ["sensitive"]):
        add("High", "Review sensitive-resource access",
            "A sensitive resource indicator was recorded.",
            "Confirm need-to-know access with the resource owner and review applicable access policy.")
    if any(x in text for x in ["after-hours", "after hours"]):
        add("Medium", "Confirm after-hours activity",
            "The event occurred outside configured working hours.",
            "Compare with approved schedules, on-call duties, and change windows before drawing conclusions.")
    if any(x in text for x in ["delete"]):
        add("High", "Check data integrity and retention",
            "A deletion action was detected.",
            "Confirm authorization and retention requirements; consult approved recovery procedures if needed.")
    if not recommendations:
        add("Low", "Routine analyst validation",
            "No configured risk factor mapped to a specific recommendation.",
            "Review alert context, validate data quality, and document the disposition.")
    recommendations.append({"priority":"General","title":"Document and escalate appropriately",
        "rationale":"Recommendations are advisory and require human validation.",
        "steps":"Record evidence references and rationale; follow organizational incident-response policy and escalate to the designated security lead when warranted."})
    order={"High":0,"Medium":1,"Low":2,"General":3}
    return sorted(recommendations,key=lambda item:order.get(item["priority"],4))
