"""Dashboard for baseline alerts, incident scoring, and analyst review."""
import streamlit as st
import pandas as pd
import time
from pathlib import Path
from modules.evaluation_dashboard import load_evaluation_metrics
from modules.scenario_generator import generate_activity
from modules.config_store import load_config, save_config
from modules.system_health import check_system_health
from modules.demo_scenario import run_demo_scenario
from modules.finalization_panel import render_finalization_panel
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
from modules.behavioral_detector import detect_behavioral_anomalies

st.set_page_config(page_title="ITRM • Security Operations", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
 /* Calm, low-glare slate canvas with subtle depth; avoid bright white wash. */
 .stApp{background:#111827!important;background-image:radial-gradient(ellipse at 12% 0%,rgba(45,78,105,.28),transparent 42%),radial-gradient(ellipse at 88% 18%,rgba(25,95,91,.16),transparent 38%)!important;color:#e5e7eb}
 [data-testid="stMain"]{background:transparent}
 .block-container{background:transparent}
 /* Panels use soft charcoal surfaces, not glaring white cards. */
 [data-testid="stMetric"]{background:#1f2937!important;border:1px solid #374151!important;box-shadow:0 8px 24px rgba(0,0,0,.16)!important}
 [data-testid="stMetricLabel"]{color:#cbd5e1!important}
 [data-testid="stMetricValue"]{color:#f8fafc!important}
 h1,h2,h3{color:#f1f5f9!important}
 p,li,label,[data-testid="stCaptionContainer"]{color:#d1d5db}
 .stMarkdown,.stText{color:#e5e7eb}
 [data-testid="stSidebar"]{background:#0b1220!important;border-right:1px solid #273449}
 [data-testid="stSidebar"] *{color:#e2e8f0}
 .stTextInput input,.stTextArea textarea,[role="combobox"],.stSelectbox div[data-baseweb="select"]{background:#111827!important;color:#f1f5f9!important;border-color:#4b5563!important}
 .stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{background:#263548!important;color:#f8fafc!important;border:1px solid #475569!important}
 .stButton>button:hover,.stDownloadButton>button:hover{background:#33465e!important;border-color:#64748b!important}
 .itrm-alert-card{background:#1f2937!important;border-color:#374151!important}
 .itrm-card-id,.itrm-card-score{color:#f8fafc!important}
 .itrm-card-meta{color:#cbd5e1!important}
 .itrm-card-kicker{color:#cbd5e1!important}
 .stDataFrame,[data-testid="stDataFrame"]{background:#1f2937}
 .stProgress>div>div{background:#14b8a6!important}

 .block-container{max-width:1500px;padding-top:1.4rem;padding-bottom:3rem}
 [data-testid="stMetric"]{background:#fff;border:1px solid #d7e2ee;padding:1rem;border-radius:16px;box-shadow:0 5px 18px rgba(23,45,74,.06)}
 [data-testid="stMetricLabel"]{color:#334155!important;font-weight:650!important}
 [data-testid="stMetricValue"]{color:#102a43!important}
 .stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"] button{border-radius:10px;min-height:44px;font-weight:650}
 input,textarea,[role="combobox"]{min-height:42px}
 :focus-visible{outline:3px solid #f59e0b!important;outline-offset:3px!important}
 h1,h2,h3{color:#102a43;letter-spacing:-.025em}
 div[role="alert"]{border-radius:12px}
 @media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
 @media(prefers-contrast:more){[data-testid="stMetric"]{border:2px solid #102a43}}
</style>
""",unsafe_allow_html=True)

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
st.markdown("""
<div style="background:linear-gradient(120deg,#102a43,#164e63 58%,#0f766e);padding:26px 30px;border-radius:22px;color:white;margin-bottom:18px;">
<div style="font-size:13px;font-weight:700;letter-spacing:.12em;">🛡️ SECURITY OPERATIONS • ITRM</div>
<div style="font-size:clamp(26px,3vw,38px);font-weight:800;line-height:1.15;margin:9px 0;">See the signal. Understand the story.</div>
<div style="font-size:15px;max-width:760px;line-height:1.55;">A human-led workspace to review unusual activity, connect context, and document decisions—not automate accusations.</div>
</div>
""",unsafe_allow_html=True)
st.caption(f"Signed in: {analyst['username']} • Role: {analyst['role']} • Research prototype; alerts require human review")

with st.sidebar:
 st.markdown("## ♿ Display & access")
 font_choice=st.radio("Text size",["Standard","Large","Extra large"],index=0,horizontal=False,key="itrm_font")
 contrast_choice=st.toggle("High contrast",value=False,key="itrm_contrast")
 st.caption("Keyboard: Tab to move • Enter/Space to activate • Esc to close menus")
 st.markdown("---")
 st.markdown("### 🧑‍💻 Analyst workspace")
 st.caption("Persona focus: triage quickly, inspect evidence, record a justified human decision.")
font_scale={"Standard":"16px","Large":"18px","Extra large":"20px"}[font_choice]
contrast_css="body{filter:contrast(1.12)} [data-testid=stMetric]{border:2px solid #102a43!important}" if contrast_choice else ""
st.markdown(f"<style>html,body,[class*='css']{{font-size:{font_scale}}}{contrast_css}</style>",unsafe_allow_html=True)
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
# System settings are persisted locally and applied to subsequent dashboard calculations.
try:
 config=load_config()
except ValueError as exc:
 st.error(str(exc))
 st.stop()
with st.expander("System configuration • Detection settings"):
 st.caption("Local prototype settings. Changes affect future dashboard calculations.")
 with st.form("system_config_form"):
  config_window=st.number_input("Event correlation window (minutes)",min_value=5,max_value=240,value=config["correlation_window_minutes"],step=5)
  config_medium=st.number_input("Medium-risk score threshold",min_value=10,max_value=99,value=config["medium_risk_threshold"],step=5)
  config_high=st.number_input("High-risk score threshold",min_value=50,max_value=100,value=config["high_risk_threshold"],step=5)
  config_submit=st.form_submit_button("Save system settings")
 if config_submit:
  proposed={"correlation_window_minutes":int(config_window),"medium_risk_threshold":int(config_medium),"high_risk_threshold":int(config_high)}
  try:
   save_config(proposed)
   st.success("Settings saved. Refreshing dashboard calculations.")
   st.rerun()
  except ValueError as exc:
   st.error(str(exc))
 st.write("Current configuration:",config)

# Read-only project readiness checks for demonstration preparation.
with st.expander("System health • Project readiness"):
 st.caption("Availability checks only—not a production security certification.")
 health_rows=check_system_health(Path(__file__).resolve().parent.parent)
 try:
  audit_health=verify_audit_chain()
  health_rows.append({"Component":"Audit hash chain",
   "Status":"Ready" if audit_health["valid"] else "Attention",
   "Details":f"{audit_health['checked']} entries checked — {audit_health['reason']}"})
 except Exception as exc:
  health_rows.append({"Component":"Audit hash chain","Status":"Attention",
   "Details":"Could not verify: "+str(exc)})
 health_frame=pd.DataFrame(health_rows)
 st.dataframe(health_frame,width="stretch",hide_index=True)
 ready_count=sum(row["Status"]=="Ready" for row in health_rows)
 st.metric("Readiness checks",f"{ready_count}/{len(health_rows)} ready")
 if any(row["Status"]=="Attention" for row in health_rows):
  st.warning("Review Attention items above before your project demonstration.")
 else:
  st.success("All current availability checks passed. This is not production approval.")

render_finalization_panel()

# Guided walkthrough runs only fixed fictional events and does not alter saved cases.
with st.expander("Project demonstration • Guided synthetic scenario"):
 st.caption("Safe classroom walkthrough using fictional activity only; no real employee data.")
 if st.button("Run guided demonstration",key="run_demo_scenario"):
  st.session_state["demo_scenario_result"]=run_demo_scenario()
 if "demo_scenario_result" in st.session_state:
  demo=st.session_state["demo_scenario_result"]
  st.markdown("### "+demo["title"])
  for step in demo["steps"]:
   st.markdown("**"+step["title"]+"**")
   st.write(step["detail"])
  st.write("**Synthetic events**")
  st.dataframe(pd.DataFrame(demo["events"]),width="stretch",hide_index=True)
  if demo["results"]:
   demo_result=demo["results"][0]
   demo_alert=demo_result["alert"]
   demo_col1,demo_col2,demo_col3=st.columns(3)
   demo_col1.metric("Correlated events",demo_alert["event_count"])
   demo_col2.metric("Risk score",str(demo_alert["risk_score"])+"/100")
   demo_col3.metric("Risk level",demo_alert["risk_level"])
   st.write("**Score explanation**")
   for reason in demo_alert["reasons"]:
    st.write("- "+reason)
   st.info("Demo alert is illustrative only. It is not saved to the case register and is not evidence of misconduct.")

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
behavioral_anomalies=detect_behavioral_anomalies(records,min_peer_count=2)
incidents=correlate_events(records,window_minutes=config["correlation_window_minutes"]); alerts=[]
for inc in incidents:
 contexts=[analyze_context(e,profiles) for e in inc["events"]]
 alerts.append(build_alert(inc,score_incident(inc["events"],contexts,high_threshold=config["high_risk_threshold"],medium_threshold=config["medium_risk_threshold"]),contexts))
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
st.subheader("📊 Risk analytics")
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

st.subheader("🚨 Incident alert queue")
st.caption("Scores prioritize review; they do not prove malicious intent.")
if alerts:
 f1,f2,f3=st.columns([1,1,2])
 with f1: risk_filter=st.selectbox("Risk level",["All","High","Medium","Low"],key="alert_risk_filter")
 with f2: status_filter=st.selectbox("Disposition",["All","Open","Under Review","Resolved","False Positive"],key="alert_status_filter")
 with f3: alert_query=st.text_input("Search Alert ID or employee",key="alert_search")
 filtered_alerts=filter_alerts(alerts,risk_filter,status_filter,alert_query)
 st.caption(f"Showing {len(filtered_alerts)} of {len(alerts)} alerts")

 # Visual triage cards: fast scanning, clear status, and an explicit human-review action.
 st.markdown("""
 <style>
 .itrm-alert-card{background:#fff;border:1px solid #d5e2ee;border-left:6px solid #64748b;
 border-radius:15px;padding:16px 18px;margin:8px 0;box-shadow:0 4px 14px rgba(16,42,67,.055)}
 .itrm-alert-card.high{border-left-color:#b91c1c}
 .itrm-alert-card.medium{border-left-color:#b45309}
 .itrm-alert-card.low{border-left-color:#0f766e}
 .itrm-card-kicker{font-size:12px;font-weight:750;letter-spacing:.08em;color:#475569;text-transform:uppercase}
 .itrm-card-id{font-size:19px;font-weight:800;color:#102a43;overflow-wrap:anywhere}
 .itrm-card-meta{color:#334155;font-size:14px;line-height:1.6}
 .itrm-card-score{font-size:27px;font-weight:850;color:#102a43}
 </style>
 """,unsafe_allow_html=True)
 st.markdown("### 🧭 Visual triage")
 st.caption("Scan severity and context, then open an alert for evidence-led review. A score is a prioritization signal—not a finding.")
 card_cols=st.columns(2)
 for card_index,card_alert in enumerate(filtered_alerts):
  with card_cols[card_index%2]:
   level=str(card_alert.get("risk_level","Low")).lower()
   score=max(0,min(100,int(card_alert.get("risk_score",0))))
   st.markdown(
    f'<div class="itrm-alert-card {level}">'
    f'<div class="itrm-card-kicker">{level.title()} priority • {card_alert.get("status","Open")}</div>'
    f'<div class="itrm-card-id">{card_alert["alert_id"]}</div>'
    f'<div class="itrm-card-meta">Employee: <strong>{card_alert["employee_id"]}</strong> &nbsp;•&nbsp; Events: {card_alert["event_count"]}</div>'
    f'<div class="itrm-card-score">{score}<span style="font-size:13px;font-weight:600"> / 100</span></div>'
    f'<div class="itrm-card-meta">{(" • ".join(card_alert.get("reasons",[])[:2])) or "No reason summary available"}</div>'
    f'</div>',unsafe_allow_html=True)
   st.progress(score/100,text=f"Risk score indicator: {score}/100")
   if st.button("Inspect alert →",key="inspect_"+str(card_alert["alert_id"]),use_container_width=True):
    st.session_state["visual_selected_alert"]=card_alert["alert_id"]
    st.rerun()
 table=pd.DataFrame([{"Alert ID":a["alert_id"],"Employee":a["employee_id"],"Events":a["event_count"],
 "Score":a["risk_score"],"Level":a["risk_level"],"Status":a["status"],"Reasons":"; ".join(a["reasons"])} for a in filtered_alerts])
 st.dataframe(table,width="stretch",hide_index=True)
 st.download_button("Export filtered alerts (CSV)",table.to_csv(index=False).encode(),"alert_queue.csv","text/csv")
 if filtered_alerts:
  st.subheader("🧑‍⚖️ Analyst review")
  alert_options=[a["alert_id"] for a in filtered_alerts]
  preferred_alert=st.session_state.get("visual_selected_alert")
  selected_index=alert_options.index(preferred_alert) if preferred_alert in alert_options else 0
  selected=st.selectbox("Select alert to investigate",alert_options,index=selected_index,key="analyst_alert_selector")
  st.session_state["visual_selected_alert"]=selected
  a=next(x for x in filtered_alerts if x["alert_id"]==selected)
  st.subheader("Behavioral anomaly indicators")
  employee_anomalies=[item for item in behavioral_anomalies if item["employee_id"]==a["employee_id"]]
  st.caption("Peer comparisons use the supplied dataset and same-role records; small samples can be misleading.")
  if employee_anomalies:
   st.dataframe(pd.DataFrame(employee_anomalies),width="stretch",hide_index=True)
  else:
   st.info("No configured behavioral deviations found for this employee.")
  st.subheader("🕒 Incident timeline")
  employee_events=[event for event in records if event["employee_id"]==a["employee_id"]]
  timeline=pd.DataFrame([{"Timestamp":event["timestamp"],"Action":event["action"],
   "Resource":event["resource"],"After hours":event["after_hours"],
   "Sensitive resource":event["sensitive"],"Details":event["details"]}
   for event in sorted(employee_events,key=lambda e:e["timestamp"])])
  st.caption("Chronological activity for this employee (synthetic dataset); contextual indicators do not prove wrongdoing.")
  # Compact investigation overview helps analysts orient before reading raw rows.
  tl1,tl2,tl3,tl4=st.columns(4)
  tl1.metric("Timeline events",len(employee_events))
  tl2.metric("After-hours",sum(bool(event.get("after_hours")) for event in employee_events))
  tl3.metric("Sensitive-resource flags",sum(bool(event.get("sensitive")) for event in employee_events))
  tl4.metric("Behavioral indicators",len(employee_anomalies))
  st.markdown("#### 🧾 Event sequence")
  st.dataframe(timeline,width="stretch",hide_index=True)
  report_timeline=[event for event in records if event["employee_id"]==a["employee_id"]]
  report_case=next((item for item in list_cases() if item["alert_id"]==selected),None)
  report_pdf=generate_alert_report(a,report_timeline,report_case,analyst["username"])
  st.download_button("Download investigation report (PDF)",report_pdf,
   file_name=f"{selected}_investigation.pdf",mime="application/pdf")
  st.subheader("📎 Incident evidence")
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
  st.subheader("🧩 Risk mitigation recommendations")
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
st.subheader("🗂️ Persistent investigation cases")
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

st.subheader("🔐 Security audit trail")
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

# Detection performance is evaluated against labeled synthetic scenarios only.
st.subheader("🎯 Detection performance evaluation")
st.caption("These metrics describe the supplied synthetic evaluation dataset, not validated real-world performance.")
metrics_path = Path(__file__).resolve().parent.parent / "results" / "evaluation_metrics.csv"
try:
    metrics = load_evaluation_metrics(metrics_path)
    if metrics.empty:
        st.info("No evaluation results yet. In the project terminal, run: python -m evaluation.evaluate")
    else:
        st.dataframe(metrics, width="stretch", hide_index=True)
        chart_metrics = [name for name in ["precision", "recall", "F1", "false_positive_rate"] if name in metrics.columns]
        if "method" in metrics.columns and chart_metrics:
            st.caption("Metric comparison by detector (0–1 scale)")
            st.bar_chart(metrics.set_index("method")[chart_metrics], width="stretch")
        st.download_button("Download evaluation metrics (CSV)", metrics.to_csv(index=False).encode(),
                           "evaluation_metrics.csv", "text/csv")
except (ValueError, OSError) as exc:
    st.error(f"Could not load evaluation metrics: {exc}")

# Synthetic activity generator: no real user or organization data is used.
st.subheader("Synthetic activity generator")
st.caption("Generate fictional activity rows for local testing. This does not monitor real people or systems.")
with st.expander("Configure and generate synthetic rows"):
    generated_count = st.number_input("Number of synthetic events", min_value=1, max_value=10000, value=100, step=25)
    generated_seed = st.number_input("Random seed (repeatable)", min_value=0, max_value=2147483647, value=42, step=1)
    if st.button("Generate synthetic activity"):
        try:
            generated_rows = generate_activity(int(generated_count), seed=int(generated_seed))
            generated_frame = pd.DataFrame(generated_rows)
            st.session_state["synthetic_activity_preview"] = generated_frame
            st.success(f"Generated {len(generated_frame)} fictional activity rows.")
        except ValueError as exc:
            st.error(str(exc))
    if "synthetic_activity_preview" in st.session_state:
        generated_frame = st.session_state["synthetic_activity_preview"]
        st.dataframe(generated_frame.head(100), width="stretch", hide_index=True)
        st.download_button("Download generated activity CSV",
            generated_frame.to_csv(index=False).encode("utf-8"),
            "synthetic_activity.csv", "text/csv")


# Read-only final quality audit; it scans project files but never executes project code.
st.subheader("Final audit • Quality assurance")
st.caption("Static readiness and Python syntax checks only. Run the full test suite separately; this is not a security certification.")
if st.button("Run final quality audit"):
    from modules.quality_audit import audit_project
    audit = audit_project()
    st.session_state["quality_audit_result"] = audit
if "quality_audit_result" in st.session_state:
    audit = st.session_state["quality_audit_result"]
    q1, q2, q3 = st.columns(3)
    q1.metric("Passed checks", f"{audit['passed']}/{audit['total']}")
    q2.metric("Needs attention", audit["attention"])
    q3.metric("Failures", audit["failed"])
    for item in audit["checks"]:
        with st.expander(f"{item['status']} — {item['category']}"):
            if item["missing"]:
                st.write(item["missing"])
            else:
                st.write(f"Verified {item['required']} item(s).")
    st.info("Audit result: " + ("All static checks passed." if audit["ready"] else "Review CHECK/FAIL items above."))
    st.download_button("Download audit results (JSON)",
        __import__("json").dumps(audit, indent=2).encode("utf-8"),
        "itrm_quality_audit.json", "application/json")


# Project viva preparation: reviewed question bank with concise answer guidance.
st.subheader("Project defense • Viva preparation")
st.caption("Use these as study prompts. Explain in your own words and insert actual project/test evidence; do not memorize unsupported claims.")
with st.expander("Generate and review viva questions"):
    viva_count = st.slider("Questions to display", min_value=4, max_value=12, value=12, key="viva_count")
    if st.button("Prepare viva questions", key="prepare_viva"):
        from modules.viva_assistant import generate_questions
        st.session_state["viva_questions"] = generate_questions(limit=viva_count)
    if "viva_questions" in st.session_state:
        viva_items = st.session_state["viva_questions"]
        for index, item in enumerate(viva_items, 1):
            with st.expander(f"{index}. {item['category']}"):
                st.markdown("**Question:** " + item["question"])
                st.markdown("**Answer guide:** " + item["answer"])
        from modules.viva_assistant import render_markdown
        st.download_button("Download viva study guide (Markdown)",
            render_markdown(viva_items).encode("utf-8"),
            "ITRM_Viva_Study_Guide.md", "text/markdown")


# Full integration validation runs the repository unittest suite locally on demand.
st.subheader("Final system validation • Integration tests")
st.caption("Runs the complete unittest suite in the project directory. This may take a little time; it does not connect to organizational systems.")
if st.button("Run full system validation", key="run_final_validation"):
    with st.spinner("Running all project tests..."):
        from modules.final_validation import run_validation, save_report
        validation = run_validation()
        save_report(validation)
        st.session_state["final_validation_result"] = validation
if "final_validation_result" in st.session_state:
    validation = st.session_state["final_validation_result"]
    if validation["passed"]:
        st.success("Validation passed: all discovered tests completed successfully.")
    elif validation["status"] == "TIMEOUT":
        st.warning(validation.get("error") or "Validation timed out.")
    else:
        st.error("Validation failed. Inspect the test output below.")
    st.code(validation["output"][-12000:] or "No test output captured.", language="text")
    st.download_button("Download validation report (JSON)",
        __import__("json").dumps(validation,indent=2).encode("utf-8"),
        "final_validation.json","application/json")
    st.caption("Saved reports: results/final_validation.json and results/final_validation.md")
