"""Generate a polished 12-slide research presentation for the ITRM prototype.

Run from repository root:
    python -m pip install python-pptx
    python scripts/generate_presentation.py
Output:
    presentation/Insider_Threat_Risk_Monitor.pptx
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "presentation" / "Insider_Threat_Risk_Monitor.pptx"
NAVY = RGBColor(15, 32, 58)
BLUE = RGBColor(35, 105, 190)
CYAN = RGBColor(45, 190, 205)
WHITE = RGBColor(245, 248, 252)
MUTED = RGBColor(175, 190, 210)

slides = [
("Insider Threats in Organizations", ["Causes, Warning Signs, and Risk Management", "A defensive monitoring and analyst-support simulation", "Group: [insert members]  |  Institution: [insert]"], "Introduce the topic and explain that this is an educational simulation using synthetic activity—not real employee surveillance."),
("Background", ["Organizations depend on trusted accounts and authorized access", "Access can be misused intentionally or accidentally", "Isolated events may look normal; patterns and context matter", "Security monitoring must respect privacy and accountability"], "An alert is a signal for review, not proof of misconduct."),
("Problem Statement", ["External-focused controls may overlook risky activity by authorized accounts", "Analysts need context to interpret unusual sequences", "Opaque alerts are difficult to validate consistently", "Excessive monitoring creates false-positive and privacy risks"], "Frame the problem as analyst support, not automated accusation."),
("Aim & Objectives", ["Aim: simulate a transparent insider-risk detection and review workflow", "Load synthetic activity and establish behavior baselines", "Correlate related events and add contextual indicators", "Produce explainable risk scores and review-ready alerts", "Support cases, evidence references, and audit records"], "Walk through the objectives and connect each to a system feature."),
("System Architecture", ["Synthetic activity → baseline detection → event correlation", "Context analysis → explainable scoring → alert queue", "Analyst review → case management and evidence register", "Audit trail, analytics, reports, configuration, evaluation"], "Show docs/ARCHITECTURE.md diagram or a dashboard screenshot here."),
("Methodology", ["Use fixed, repeatable synthetic activity records", "Apply baseline/rule checks and event time-window correlation", "Assess role, time, resource, and action context", "Score transparently with human-readable reasons", "Test components and end-to-end workflows"], "Explain why synthetic data protects privacy and makes demonstrations repeatable."),
("Implemented Modules", ["Activity loader & baseline detector", "Event correlator, context analyzer, risk engine", "Alert queue, filters, analytics, incident timeline", "Authentication, cases, evidence register, audit log", "PDF reports, scenario generator, guided demo", "Configuration, evaluation, and system-health panels"], "Use a real screenshot of the running dashboard if available."),
("Guided Demonstration", ["Open Project demonstration • Guided synthetic scenario", "Inspect the fictional event sequence", "Explain correlation and contextual checks", "Show score reasons and analyst validation", "Clarify the demo does not create a persistent case"], "Run the guided demo live. State explicitly that all events are fictional."),
("Evaluation", ["Unit tests validate individual module behavior", "Integration tests check the detection-to-review workflow", "Metrics use a small hand-labeled synthetic dataset", "Report precision, recall, F1, and false-positive rate", "Results are exploratory—not real-world accuracy claims"], "Insert actual test output and metrics from your own run; do not invent values."),
("Risk Management & Ethics", ["Use only authorized data and approved access", "Minimize personal data and restrict access by role", "Require human validation before consequential decisions", "Keep review records and accountable audit history", "Avoid protected-characteristic profiling; define retention"], "Discuss safeguards and why risk scores cannot establish intent."),
("Limitations & Future Work", ["Synthetic data may not reflect real organizations", "Rules and thresholds can produce false positives/negatives", "Prototype is not production-ready", "Future: approved anonymized datasets, calibration, drift checks", "Future: privacy assessment, secure deployment, analyst usability"], "Be candid about limitations and identify realistic next steps."),
("Conclusion", ["The prototype demonstrates a transparent insider-risk workflow", "Correlation and context can help analysts interpret activity", "Explainability, privacy, and human review are essential", "A score prioritizes review; it does not prove guilt"], "Close with the key contribution and invite questions."),
]

def add_notes(slide, notes):
    # python-pptx supports speaker notes in recent releases.
    try:
        slide.notes_slide.notes_text_frame.text = notes
    except Exception:
        pass

def add_text(slide, text, x, y, w, h, size, color, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.alignment = align
    p.font.name = "Aptos"
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.color.rgb = color
    return box

def main():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    for idx, (title, bullets, notes) in enumerate(slides, 1):
        s = prs.slides.add_slide(blank)
        bg = s.background.fill
        bg.solid()
        bg.fore_color.rgb = NAVY
        # top accent strip
        bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(.12))
        bar.fill.solid(); bar.fill.fore_color.rgb = CYAN; bar.line.fill.background()
        add_text(s, f"ITRM  /  RESEARCH PROJECT                                      {idx:02d}  •  12", .65, .32, 12, .35, 12, CYAN, True)
        add_text(s, title, .75, 1.05, 11.8, 1.0, 30 if idx != 1 else 34, WHITE, True)
        if idx == 1:
            add_text(s, bullets[0], .8, 2.45, 11.5, .7, 22, CYAN, True)
            for j, line in enumerate(bullets[1:]):
                add_text(s, line, .85, 3.5 + j*.55, 11.3, .45, 16, MUTED)
        else:
            # Accent panel and bullet text
            panel = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(.8), Inches(2.25), Inches(.18), Inches(4.25))
            panel.fill.solid(); panel.fill.fore_color.rgb = BLUE; panel.line.fill.background()
            for j, line in enumerate(bullets):
                yy = 2.35 + j*.68
                dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.25), Inches(yy+.12), Inches(.12), Inches(.12))
                dot.fill.solid(); dot.fill.fore_color.rgb = CYAN; dot.line.fill.background()
                add_text(s, line, 1.6, yy, 10.7, .55, 19, WHITE)
        add_text(s, "INSIDER THREAT RISK MONITOR  •  EDUCATIONAL PROTOTYPE", .75, 7.05, 11.8, .25, 10, MUTED)
        add_notes(s, notes)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Presentation created: {OUT}")

if __name__ == "__main__":
    main()
