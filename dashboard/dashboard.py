"""Dashboard for baseline alerts, incident scoring, and analyst review."""
import streamlit as st
import pandas as pd
from modules.data_loader import load_activity
from modules.baseline_detector import detect_baseline
from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident
from modules.alert_manager import build_alert, set_disposition, priority
from modules.case_store import create_case, update_case, list_cases, get_case_history
from modules.audit_log import list_audit_events, verify_audit_chain

st.set_page_config(page_title="Insider Threat Risk Monitor", layout="wide")
st.title("Insider Threat Risk Monitor")
st.caption("Research prototype • synthetic activity • alerts are leads for human review")
df=load_activity(); baseline=detect_baseline(df)
records=[]
for row in df.to_dict(orient="records"):
 ts=row["timestamp"]; resource=str(row["resource"])
 records.append({"timestamp":ts.isoformat(),"employee_id":str(row["user"]),"role":str(row["role"]),
 "action":str(row["event"]).lower(),"resource":resource,"details":str(row["details"]),
 "after_hours":ts.hour<7 or ts.hour>=19,
 "sensitive":any(x in resource.lower() for x in ["payroll","employee_records","admin"])})
profiles={"emp01":{"role":"analyst","allowed_resources":["workstation","report.csv"]},
 "emp02":{"role":"hr","allowed_resources":["workstation","employee_records"]},
 "emp03":{"role":"finance","allowed_resources":["workstation","payroll.csv"]},
 "emp04":{"role":"it","allowed_resources":["workstation","admin_access"]}}
incidents=correlate_events(records,window_minutes=60); alerts=[]
for inc in incidents:
 contexts=[analyze_context(e,profiles) for e in inc["events"]]
 alerts.append(build_alert(inc,score_incident(inc["events"],contexts),contexts))
alerts.sort(key=priority)
if "alert_reviews" not in st.session_state: st.session_state.alert_reviews={}
for a in alerts:
 if a["alert_id"] in st.session_state.alert_reviews: a.update(st.session_state.alert_reviews[a["alert_id"]])
c1,c2,c3,c4=st.columns(4)
c1.metric("Activity records",len(df)); c2.metric("Baseline alerts",len(baseline))
c3.metric("Incidents",len(alerts)); c4.metric("High risk",sum(a["risk_level"]=="High" for a in alerts))
st.subheader("Incident alert queue")
st.caption("Scores prioritize review; they do not prove malicious intent.")
if alerts:
 table=pd.DataFrame([{"Alert ID":a["alert_id"],"Employee":a["employee_id"],"Events":a["event_count"],
 "Score":a["risk_score"],"Level":a["risk_level"],"Status":a["status"],"Reasons":"; ".join(a["reasons"])} for a in alerts])
 st.dataframe(table,width="stretch",hide_index=True)
 st.download_button("Export alert queue (CSV)",table.to_csv(index=False).encode(),"alert_queue.csv","text/csv")
 st.subheader("Analyst review"); selected=st.selectbox("Select alert",[a["alert_id"] for a in alerts])
 a=next(x for x in alerts if x["alert_id"]==selected)
 st.write(f"**Employee:** {a['employee_id']} | **Risk:** {a['risk_score']}/100 ({a['risk_level']})")
 st.write("**Why this score?**")
 if a.get("risk_factors"):
  st.dataframe(pd.DataFrame(a["risk_factors"]),width="stretch",hide_index=True)
 st.write("**Explanation:**"); [st.write("- "+reason) for reason in a["reasons"]]
 status=st.selectbox("Disposition",["Open","Under Review","Resolved","False Positive"],
 index=["Open","Under Review","Resolved","False Positive"].index(a["status"]),key="status_"+selected)
 note=st.text_area("Analyst note",value=a.get("analyst_note",""),key="note_"+selected)
 if st.button("Save review",key="save_"+selected):
  revised=set_disposition(a,status,note)
  st.session_state.alert_reviews[selected]={"status":revised["status"],"analyst_note":revised["analyst_note"],"reviewed_at":revised["reviewed_at"]}
  st.success("Review saved for this active session.")
else: st.info("No incidents were generated.")
st.subheader("Persistent investigation cases")
st.caption("SQLite-backed cases persist after dashboard restarts. Prototype only; no authentication is implemented.")
if alerts:
    alert_id = st.selectbox("Alert to create a case from", [a["alert_id"] for a in alerts], key="case_alert")
    if st.button("Create or open case"):
        selected_alert = next(a for a in alerts if a["alert_id"] == alert_id)
        case, created = create_case(selected_alert)
        st.success(("Created" if created else "Opened existing") + f" case #{case['case_id']}")
cases = list_cases()
if cases:
    labels = {f"Case #{c['case_id']} — {c['alert_id']} ({c['status']})": c for c in cases}
    label = st.selectbox("Case to investigate", list(labels), key="case_pick")
    case = labels[label]
    st.write(f"**Alert:** {case['alert_id']} | **Risk:** {case['risk_score']}/100")
    with st.form("case_editor"):
        case_status = st.selectbox("Status", ["Open", "Under Review", "Resolved", "False Positive"],
            index=["Open", "Under Review", "Resolved", "False Positive"].index(case["status"]))
        assigned = st.text_input("Assigned analyst", case["assigned_to"])
        notes = st.text_area("Investigation notes", case["analyst_notes"])
        submitted = st.form_submit_button("Save case")
    if submitted:
        update_case(case["case_id"], case_status, assigned, notes)
        st.success("Case saved to database.")
        st.rerun()
    st.write("**Case history**")
    history = get_case_history(case["case_id"])
    st.dataframe(pd.DataFrame(history), width="stretch", hide_index=True)
    st.download_button("Export history CSV", pd.DataFrame(history).to_csv(index=False).encode(),
                       f"case_{case['case_id']}_history.csv", "text/csv")
else:
    st.info("No investigation cases yet. Create one from an alert.")
st.subheader("Case register")
if cases:
    st.dataframe(pd.DataFrame(cases), width="stretch", hide_index=True)
else:
    st.caption("The case register is empty.")

st.subheader("Security audit trail")
st.caption("Audit events record case creation and changes. Hash-chain verification detects record edits; it is not a substitute for access controls or external backups.")
audit_col1, audit_col2 = st.columns([1, 3])
with audit_col1:
    if st.button("Verify audit chain"):
        verification = verify_audit_chain()
        if verification["valid"]:
            st.success(f"Verified {verification['checked']} audit entries.")
        else:
            st.error(f"Integrity failure at audit ID {verification['failed_audit_id']}: {verification['reason']}")
audit_events = list_audit_events()
if audit_events:
    audit_table = pd.DataFrame(audit_events)
    st.dataframe(audit_table, width="stretch", hide_index=True)
    st.download_button("Export audit log (CSV)", audit_table.to_csv(index=False).encode(),
                       "security_audit_log.csv", "text/csv")
else:
    st.info("No audit events recorded yet. Creating or updating a case will add entries.")

st.subheader("Baseline alerts"); st.dataframe(baseline,width="stretch")
st.subheader("Activity log"); st.dataframe(df,width="stretch")
