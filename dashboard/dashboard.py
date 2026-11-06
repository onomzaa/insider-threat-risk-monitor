"""Dashboard for baseline alerts, incident scoring, and analyst review."""
import streamlit as st
import pandas as pd
import time
from modules.data_loader import load_activity
from modules.baseline_detector import detect_baseline
from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident
from modules.alert_manager import build_alert, set_disposition, priority, filter_alerts
from modules.case_store import create_case, update_case, list_cases, get_case_history
from modules.audit_log import list_audit_events, verify_audit_chain
from modules.auth import authenticate, can, create_user, load_users, change_password
from modules.alert_review_store import get_review, save_review
from modules.report_generator import generate_alert_report
from modules.evidence_store import add_evidence, list_evidence
from modules.mitigation_recommendations import recommend_mitigations

st.set_page_config(page_title="Insider Threat Risk Monitor", layout="wide")

# Login gate: no dashboard data or review controls are shown before authentication.
if "analyst_account" not in st.session_state:
    st.session_state.analyst_account = None
if not st.session_state.analyst_account:
    st.title("Insider Threat Risk Monitor — Sign in")
    with st.form("analyst_login"):
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        login_submitted = st.form_submit_button("Sign in")
    if login_submitted:
        account = authenticate(login_username, login_password)
        if account:
            st.session_state.analyst_account = account
            st.rerun()
        st.error("Invalid username or password.")
    st.info("First-time setup: run python -m modules.setup_admin in your project terminal.")
    st.stop()

# Prototype session expiry: 15 minutes idle or 8 hours absolute.
now = time.time()
if "session_started_at" not in st.session_state:
    st.session_state.session_started_at = now
if "last_activity_at" not in st.session_state:
    st.session_state.last_activity_at = now
idle_expired = now - st.session_state.last_activity_at >= 15 * 60
absolute_expired = now - st.session_state.session_started_at >= 8 * 60 * 60
if idle_expired or absolute_expired:
    st.session_state.analyst_account = None
    st.session_state.pop("session_started_at", None)
    st.session_state.pop("last_activity_at", None)
    st.warning("Your session expired. Please sign in again.")
    st.rerun()
st.session_state.last_activity_at = now

analyst = st.session_state.analyst_account
st.title("Insider Threat Risk Monitor")
st.caption(f"Signed in: {analyst['username']} • Role: {analyst['role']} • Research prototype; alerts require human review")
if st.button("Sign out"):
    st.session_state.analyst_account = None
    st.session_state.pop("session_started_at", None)
    st.session_state.pop("last_activity_at", None)
    st.rerun()

with st.expander("My account • Change password"):
    with st.form("change_own_password"):
        current_pw = st.text_input("Current password", type="password")
        new_pw = st.text_input("New password (12+ characters)", type="password")
        confirm_pw = st.text_input("Confirm new password", type="password")
        password_submitted = st.form_submit_button("Update password")
    if password_submitted:
        if new_pw != confirm_pw:
            st.error("New passwords do not match.")
        else:
            try:
                change_password(analyst["username"], current_pw, new_pw)
                st.success("Password changed. Use the new password next time you sign in.")
            except ValueError as exc:
                st.error(str(exc))

# Account administration is restricted to administrators.
if can("manage_users", analyst["role"]):
    with st.expander("Admin • User management"):
        st.caption("Create local dashboard accounts. Passwords are hashed and stored in data/analysts.json.")
        with st.form("create_analyst_user"):
            new_username = st.text_input("New username")
            new_password = st.text_input("Temporary password (12+ characters)", type="password")
            confirm_password = st.text_input("Confirm password", type="password")
            new_role = st.selectbox("Account role", ["viewer", "analyst", "admin"])
            create_submitted = st.form_submit_button("Create account")
        if create_submitted:
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                try:
                    created_account = create_user(new_username, new_password, role=new_role)
                    st.success(f"Created account: {created_account['username']} ({created_account['role']}).")
                except (ValueError, OSError) as exc:
                    st.error(str(exc))
        users = load_users()
        if users:
            st.write("**Current accounts**")
            st.dataframe(pd.DataFrame([
                {"Username": name, "Role": record.get("role", "unknown")}
                for name, record in sorted(users.items())
            ]), width="stretch", hide_index=True)
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
for a in alerts:
 persisted_review = get_review(a["alert_id"])
 if persisted_review:
  a.update({"status": persisted_review["status"],
            "analyst_note": persisted_review["analyst_note"],
            "reviewed_at": persisted_review["reviewed_at"],
            "reviewed_by": persisted_review["reviewed_by"]})
c1,c2,c3,c4=st.columns(4)
c1.metric("Activity records",len(df)); c2.metric("Baseline alerts",len(baseline))
c3.metric("Incidents",len(alerts)); c4.metric("High risk",sum(a["risk_level"]=="High" for a in alerts))
m1,m2,m3,m4=st.columns(4)
m1.metric("Open alerts",sum(a["status"]=="Open" for a in alerts))
m2.metric("High risk alerts",sum(a["risk_level"]=="High" for a in alerts))
m3.metric("Resolved",sum(a["status"]=="Resolved" for a in alerts))
m4.metric("False positives",sum(a["status"]=="False Positive" for a in alerts))
st.subheader("Risk analytics")
if alerts:
 analytics_col1,analytics_col2=st.columns(2)
 with analytics_col1:
  st.caption("Alerts by risk level")
  risk_counts=pd.DataFrame({"Risk level":["High","Medium","Low"],
   "Alerts":[sum(a["risk_level"]==level for a in alerts) for level in ["High","Medium","Low"]]})
  st.bar_chart(risk_counts.set_index("Risk level"),width="stretch")
 with analytics_col2:
  st.caption("Alerts by disposition")
  disposition_order=["Open","Under Review","Resolved","False Positive"]
  disposition_counts=pd.DataFrame({"Disposition":disposition_order,
   "Alerts":[sum(a["status"]==status for a in alerts) for status in disposition_order]})
  st.bar_chart(disposition_counts.set_index("Disposition"),width="stretch")
 st.caption("Risk score distribution (0–100)")
 score_values=[int(a["risk_score"]) for a in alerts]
 score_counts=pd.Series(score_values,name="Alert count").value_counts().sort_index()
 score_chart=pd.DataFrame({"Alert count":score_counts.values},index=score_counts.index)
 score_chart.index.name="Risk score"
 st.bar_chart(score_chart,width="stretch")
else:
 st.info("Analytics will appear when incidents are generated.")

st.subheader("Incident alert queue")
st.caption("Scores prioritize review; they do not prove malicious intent.")
if alerts:
 f1,f2,f3=st.columns([1,1,2])
 with f1: risk_filter=st.selectbox("Risk level",["All","High","Medium","Low"],key="alert_risk_filter")
 with f2: status_filter=st.selectbox("Disposition",["All","Open","Under Review","Resolved","False Positive"],key="alert_status_filter")
 with f3: alert_query=st.text_input("Search Alert ID or employee",key="alert_search")
 filtered_alerts=filter_alerts(alerts,risk_filter,status_filter,alert_query)
 st.caption(f"Showing {len(filtered_alerts)} of {len(alerts)} alerts")
 table=pd.DataFrame([{"Alert ID":a["alert_id"],"Employee":a["employee_id"],"Events":a["event_count"],
 "Score":a["risk_score"],"Level":a["risk_level"],"Status":a["status"],"Reasons":"; ".join(a["reasons"])} for a in filtered_alerts])
 st.dataframe(table,width="stretch",hide_index=True)
 st.download_button("Export filtered alerts (CSV)",table.to_csv(index=False).encode(),"alert_queue.csv","text/csv")
 if filtered_alerts:
  st.subheader("Analyst review"); selected=st.selectbox("Select alert",[a["alert_id"] for a in filtered_alerts])
  a=next(x for x in filtered_alerts if x["alert_id"]==selected)
  st.subheader("Incident timeline")
  employee_events=[event for event in records if event["employee_id"]==a["employee_id"]]
  timeline=pd.DataFrame([{"Timestamp":event["timestamp"],"Action":event["action"],
   "Resource":event["resource"],"After hours":event["after_hours"],
   "Sensitive resource":event["sensitive"],"Details":event["details"]}
   for event in sorted(employee_events,key=lambda e:e["timestamp"])])
  st.caption("Chronological activity for this employee (synthetic dataset); contextual indicators do not prove wrongdoing.")
  st.dataframe(timeline,width="stretch",hide_index=True)
  report_timeline=[event for event in records if event["employee_id"]==a["employee_id"]]
  report_case=next((item for item in list_cases() if item["alert_id"]==selected),None)
  report_pdf=generate_alert_report(a,report_timeline,report_case,analyst["username"])
  st.download_button("Download investigation report (PDF)",report_pdf,
   file_name=f"{selected}_investigation.pdf",mime="application/pdf")
  st.subheader("Incident evidence")
  st.caption("Record references to synthetic or authorized evidence. Do not upload sensitive raw files.")
  with st.form("evidence_form_"+selected):
   evidence_title=st.text_input("Evidence title",placeholder="Example: Synthetic access log excerpt")
   evidence_description=st.text_area("Description",placeholder="What this reference supports or shows")
   evidence_reference=st.text_input("Evidence reference",placeholder="Example: scenario_logs.csv row 12")
   evidence_submitted=st.form_submit_button("Add evidence reference",disabled=not can("review",analyst["role"]))
  if evidence_submitted:
   try:
    added=add_evidence(selected,evidence_title,evidence_description,evidence_reference,analyst["username"])
    st.success("Evidence reference added: E"+str(added["evidence_id"]))
    st.rerun()
   except ValueError as exc:
    st.error(str(exc))
  evidence_records=list_evidence(selected)
  if evidence_records:
   st.dataframe(pd.DataFrame(evidence_records),width="stretch",hide_index=True)
  else:
   st.info("No evidence references recorded for this alert yet.")
  st.write(f"**Employee:** {a['employee_id']} | **Risk:** {a['risk_score']}/100 ({a['risk_level']})")
  if a.get("reviewed_by"):
   st.caption(f"Last reviewed by {a['reviewed_by']} • {a.get('reviewed_at', 'timestamp unavailable')}")
  st.subheader("Risk mitigation recommendations")
  st.caption("Advisory checks only; validate context before taking action.")
  for recommendation in recommend_mitigations(a):
   st.markdown("**"+recommendation["priority"]+" priority — "+recommendation["title"]+"**")
   st.write(recommendation["rationale"])
   st.write(recommendation["steps"])
  st.write("**Why this score?**")
  if a.get("risk_factors"):
   st.dataframe(pd.DataFrame(a["risk_factors"]),width="stretch",hide_index=True)
  st.write("**Explanation:**"); [st.write("- "+reason) for reason in a["reasons"]]
  status=st.selectbox("Disposition",["Open","Under Review","Resolved","False Positive"],
   index=["Open","Under Review","Resolved","False Positive"].index(a["status"]),key="status_"+selected)
  note=st.text_area("Analyst note",value=a.get("analyst_note",""),key="note_"+selected)
  if st.button("Save review",key="save_"+selected,disabled=not can("review",analyst["role"])):
   revised=set_disposition(a,status,note)
   persisted=save_review(selected,revised["status"],revised["analyst_note"],actor=analyst["username"])
   a.update({"status":persisted["status"],"analyst_note":persisted["analyst_note"],
    "reviewed_at":persisted["reviewed_at"],"reviewed_by":persisted["reviewed_by"]})
   st.success(f"Review saved persistently by {persisted['reviewed_by']} at {persisted['reviewed_at']}.")
   st.rerun()
 else:
  st.info("No alerts match these filters. Adjust risk, disposition, or search.")
else:
 st.info("No incidents were generated.")
st.subheader("Persistent investigation cases")
st.caption("SQLite-backed cases persist after dashboard restarts. Review permissions are role-controlled.")
if alerts:
    alert_id = st.selectbox("Alert to create a case from", [a["alert_id"] for a in alerts], key="case_alert")
    if st.button("Create or open case",disabled=not can("review",analyst["role"])):
        selected_alert = next(a for a in alerts if a["alert_id"] == alert_id)
        case, created = create_case(selected_alert, actor=analyst["username"])
        st.success(("Created" if created else "Opened existing") + f" case #{case['case_id']}")
cases = list_cases()
st.subheader("Case register")
if cases:
    filter_col, search_col = st.columns([1, 2])
    with filter_col:
        chosen_status = st.selectbox("Filter by status", ["All statuses", "Open", "Under Review", "Resolved", "False Positive"], key="case_status_filter")
    with search_col:
        case_query = st.text_input("Search case ID, alert ID, or analyst", key="case_search").strip().lower()
    filtered_cases = [
        item for item in cases
        if (chosen_status == "All statuses" or item["status"] == chosen_status)
        and (not case_query or case_query in str(item["case_id"]).lower()
             or case_query in str(item["alert_id"]).lower()
             or case_query in str(item["assigned_to"]).lower())
    ]
    st.caption(f"Showing {len(filtered_cases)} of {len(cases)} cases")
    if filtered_cases:
        st.dataframe(pd.DataFrame(filtered_cases), width="stretch", hide_index=True)
        labels = {f"Case #{item['case_id']} — {item['alert_id']} ({item['status']})": item for item in filtered_cases}
        label = st.selectbox("Case to investigate", list(labels), key="case_pick")
        case = labels[label]
        st.write(f"**Alert:** {case['alert_id']} | **Risk:** {case['risk_score']}/100")
        with st.form("case_editor"):
            case_status = st.selectbox("Status", ["Open", "Under Review", "Resolved", "False Positive"],
                index=["Open", "Under Review", "Resolved", "False Positive"].index(case["status"]))
            assigned = st.text_input("Assigned analyst", case["assigned_to"])
            notes = st.text_area("Investigation notes", case["analyst_notes"])
            submitted = st.form_submit_button("Save case", disabled=not can("review",analyst["role"]))
        if submitted:
            update_case(case["case_id"], case_status, assigned, notes, actor=analyst["username"])
            st.success("Case saved to database.")
            st.rerun()
        st.write("**Case history**")
        history = get_case_history(case["case_id"])
        st.dataframe(pd.DataFrame(history), width="stretch", hide_index=True)
        st.download_button("Export history CSV", pd.DataFrame(history).to_csv(index=False).encode(),
                           f"case_{case['case_id']}_history.csv", "text/csv")
    else:
        st.info("No cases match these filters. Change the status or search term.")
else:
    st.info("No investigation cases yet. Create one from an alert.")

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
