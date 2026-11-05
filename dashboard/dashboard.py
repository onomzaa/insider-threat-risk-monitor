"""Streamlit dashboard placeholder; wired in a later implementation step."""
import streamlit as st
from modules.data_loader import load_activity
from modules.baseline_detector import detect_baseline

st.set_page_config(page_title="Insider Threat Risk Monitor", layout="wide")
st.title("Insider Threat Risk Monitor")
st.caption("Research prototype • synthetic activity data • alerts require human review")
events = load_activity()
alerts = detect_baseline(events)
a, b, c = st.columns(3)
a.metric("Activity records", len(events))
b.metric("Baseline alerts", len(alerts))
c.metric("Users observed", events["user"].nunique())
st.subheader("Activity log")
st.dataframe(events, use_container_width=True)
st.subheader("Baseline alerts")
st.dataframe(alerts, use_container_width=True)
