"""Streamlit view for project finalization status."""
import streamlit as st
from modules.project_finalization import assess_project

def render_finalization_panel():
    with st.expander("Project finalization • Submission readiness", expanded=False):
        report = assess_project()
        st.caption("Read-only file-presence assessment. It does not certify quality, security, or successful tests.")
        st.progress(report["ready_count"] / report["total_count"])
        st.write(f"Project files present: **{report['ready_count']} / {report['total_count']}**")
        for item in report["checks"]:
            if item["ready"]:
                st.success(f"✓ {item['item']}")
            else:
                st.warning(f"Needs attention: {item['item']}")
                for missing in item["missing"]:
                    st.caption(f"Missing: {missing}")
        st.markdown("**Optional local dependencies**")
        for name, ok in report["dependencies"].items():
            st.write(f"{'✓' if ok else '⚠'} {name}: {'installed' if ok else 'not installed'}")
        st.info("Before submission: run the full test suite, execute evaluation, generate the PowerPoint, inspect screenshots, and verify references.")
