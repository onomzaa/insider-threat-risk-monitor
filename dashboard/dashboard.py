"""Dashboard for baseline alerts and explainable correlated incidents."""
import streamlit as st
import pandas as pd
from modules.data_loader import load_activity
from modules.baseline_detector import detect_baseline
from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident

st.set_page_config(page_title="Insider Threat Risk Monitor", layout="wide")
st.title("Insider Threat Risk Monitor")
st.caption("Research prototype • synthetic activity • alerts are leads for human review")

df = load_activity()
baseline = detect_baseline(df)

# Convert dataset fields to the common event format used by the new modules.
records = []
for row in df.to_dict(orient="records"):
    records.append({
        "timestamp": row["timestamp"].isoformat(),
        "employee_id": str(row["user"]),
        "role": str(row["role"]),
        "action": str(row["event"]).lower(),
        "resource": str(row["resource"]),
        "details": str(row["details"]),
        "after_hours": row["timestamp"].hour < 7 or row["timestamp"].hour >= 19,
        "sensitive": any(word in str(row["resource"]).lower()
                          for word in ["payroll", "employee_records", "admin"]),
    })

# Basic role/resource context. Replace with organization-approved policy data in a real deployment.
profiles = {
    "emp01": {"role": "analyst", "allowed_resources": ["workstation", "report.csv"]},
    "emp02": {"role": "hr", "allowed_resources": ["workstation", "employee_records"]},
    "emp03": {"role": "finance", "allowed_resources": ["workstation", "payroll.csv"]},
    "emp04": {"role": "it", "allowed_resources": ["workstation", "admin_access"]},
}

incidents = correlate_events(records, window_minutes=60)
incident_rows = []
for incident in incidents:
    contexts = [analyze_context(event, profiles) for event in incident["events"]]
    result = score_incident(incident["events"], contexts)
    incident_rows.append({
        "Employee": incident["employee_id"],
        "Events": len(incident["events"]),
        "First seen": incident["first_seen"].strftime("%Y-%m-%d %H:%M"),
        "Last seen": incident["last_seen"].strftime("%Y-%m-%d %H:%M"),
        "Risk score": result["risk_score"],
        "Risk level": result["risk_level"],
        "Explanation": "; ".join(result["explanation"]),
    })

high = sum(x["Risk level"] == "High" for x in incident_rows)
medium = sum(x["Risk level"] == "Medium" for x in incident_rows)
low = sum(x["Risk level"] == "Low" for x in incident_rows)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Activity records", len(df))
c2.metric("Baseline alerts", len(baseline))
c3.metric("Correlated incidents", len(incident_rows))
c4.metric("High-risk incidents", high)

st.subheader("Explainable incident review")
st.write("Scores are rule-based indicators, not proof of malicious intent.")
if incident_rows:
    st.dataframe(pd.DataFrame(incident_rows).sort_values("Risk score", ascending=False),
                 use_container_width=True, hide_index=True)
else:
    st.info("No incidents were produced for the current data.")

st.subheader("Baseline alerts")
st.dataframe(baseline, use_container_width=True)

st.subheader("Activity log")
st.dataframe(df, use_container_width=True)
