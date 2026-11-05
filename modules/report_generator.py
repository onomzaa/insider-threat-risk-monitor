"""Create downloadable PDF investigation reports (ReportLab)."""
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_alert_report(alert, timeline=None, case=None, analyst=""):
    """Return PDF bytes for one alert and its review/timeline context."""
    timeline = timeline or []
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                           topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("Insider Threat Risk Monitor", styles["Title"]),
             Paragraph("Incident Investigation Report", styles["Heading2"]),
             Spacer(1, 8)]
    details = [["Alert ID", str(alert.get("alert_id", "N/A"))],
               ["Employee", str(alert.get("employee_id", "N/A"))],
               ["Risk score", f"{alert.get('risk_score', 0)}/100 ({alert.get('risk_level', 'Unknown')})"],
               ["Disposition", str(alert.get("status", "Open"))],
               ["Reviewed by", str(alert.get("reviewed_by", analyst or "Not recorded"))],
               ["Review timestamp", str(alert.get("reviewed_at", "Not recorded"))],
               ["Event count", str(alert.get("event_count", len(timeline)))]]
    if case:
        details += [["Case ID", str(case.get("case_id", "N/A"))],
                    ["Assigned analyst", str(case.get("assigned_to", "Unassigned"))]]
    table = Table(details, colWidths=[42*mm, 125*mm])
    table.setStyle(TableStyle([("BACKGROUND", (0,0),(0,-1), colors.whitesmoke),
                               ("GRID",(0,0),(-1,-1),0.4,colors.grey),
                               ("VALIGN",(0,0),(-1,-1),"TOP"),
                               ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold")]))
    story += [table, Spacer(1, 10), Paragraph("Risk explanation", styles["Heading2"])]
    reasons = alert.get("reasons", [])
    story += [Paragraph("• " + str(reason), styles["BodyText"]) for reason in reasons] or [Paragraph("No explanation recorded.", styles["BodyText"])]
    story += [Spacer(1, 6), Paragraph("Analyst notes", styles["Heading2"]),
              Paragraph(str(alert.get("analyst_note", "No analyst note recorded.") or "No analyst note recorded.").replace("&", "&amp;"), styles["BodyText"])]
    if case and case.get("analyst_notes"):
        story += [Paragraph("Case investigation notes", styles["Heading2"]),
                  Paragraph(str(case["analyst_notes"]).replace("&", "&amp;"), styles["BodyText"])]
    story += [Spacer(1, 8), Paragraph("Activity timeline", styles["Heading2"])]
    rows = [["Timestamp", "Action", "Resource", "Context"]]
    for event in timeline:
        context = []
        if event.get("after_hours"): context.append("After hours")
        if event.get("sensitive"): context.append("Sensitive")
        rows.append([str(event.get("timestamp", "")), str(event.get("action", "")),
                     str(event.get("resource", "")), ", ".join(context) or "—"])
    if len(rows)==1: rows.append(["No events", "", "", ""])
    event_table=Table(rows,repeatRows=1,colWidths=[38*mm,30*mm,65*mm,34*mm])
    event_table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#23395d")),
                                    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                                    ("GRID",(0,0),(-1,-1),0.35,colors.grey),
                                    ("VALIGN",(0,0),(-1,-1),"TOP"),
                                    ("FONTSIZE",(0,0),(-1,-1),8)]))
    story += [event_table, Spacer(1, 12), Paragraph("Research prototype • Synthetic/authorized data • Human review required", styles["Italic"])]
    doc.build(story)
    return buffer.getvalue()
