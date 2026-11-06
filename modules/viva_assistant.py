"""Generate project-specific viva questions and concise answer guidance.

This is a study aid, not a substitute for understanding or citing the project.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUESTION_BANK = [
("Research motivation", "Why did your group choose insider threats as the research topic?",
 "Insider activity can be difficult to distinguish from legitimate work. Our prototype explores explainable indicators and human review rather than assuming unusual activity is malicious."),
("Research objective", "What problem does the Insider Threat Risk Monitor address?",
 "It demonstrates a defensive workflow that correlates synthetic activity events, adds context, assigns an explainable risk score, and supports analyst review."),
("System architecture", "Explain the main processing pipeline.",
 "Synthetic or authorized activity is loaded, events are correlated, context is analyzed, risk is scored with reasons, alerts are created, and an analyst reviews them."),
("Detection logic", "Why combine event correlation with context?",
 "A single event may be normal in isolation. Grouping related events and checking role, time, and resource context can provide more useful review signals."),
("Explainability", "How does the system explain an alert?",
 "The score is accompanied by risk factors and reason text so an analyst can inspect which indicators contributed and validate them against legitimate context."),
("Evaluation", "How did you evaluate the prototype?",
 "We use labeled synthetic scenarios to compare a simple baseline with the improved approach, reporting confusion-matrix counts, precision, recall, F1, and false-positive rate."),
("Metrics", "What is the difference between precision and recall?",
 "Precision is the proportion of predicted alerts that are correct; recall is the proportion of labeled positive cases detected. They can trade off as thresholds change."),
("False positives", "Why are false positives important in insider-threat detection?",
 "Legitimate work can look unusual. Excessive false alerts waste analyst time and can unfairly affect people, so alerts require context and human validation"),
("Limitations", "Can this system prove that an employee is malicious?",
 "No. Risk scores and behavioral indicators are not proof of intent or misconduct. They only prioritize review and must be interpreted with verified context"),
("Ethics", "What safeguards should guide organizational deployment?",
 "Use authorized and minimized data, transparent policies, role-limited access, retention controls, human review, and an appeal or correction process. This prototype is not production-ready"),
("Data", "Why did you use synthetic activity data?",
 "Synthetic records support repeatable testing and demonstrations without collecting sensitive employee information. Their results do not establish real-world effectiveness"),
("Future work", "What would you improve next?",
 "Evaluate on appropriately governed, representative data; improve calibration and drift checks; conduct privacy and security reviews; and validate usefulness with qualified analysts"),
]

def load_project_context(root=ROOT):
    root=Path(root)
    snippets=[]
    for name in ("README.md","docs/ARCHITECTURE.md","docs/PRESENTATION_SLIDE_SCRIPT.md"):
        p=root/name
        if p.is_file():
            snippets.append(p.read_text(encoding="utf-8",errors="replace")[:12000])
    return "\n".join(snippets)

def generate_questions(root=ROOT, limit=None):
    context=load_project_context(root)
    # Include the context as a grounded reminder; question wording stays in reviewed bank.
    items=[]
    for category,question,answer in QUESTION_BANK:
        items.append({"category":category,"question":question,"answer":answer,
                      "project_context_available":bool(context)})
    return items[:limit] if limit else items

def render_markdown(items):
    out=["# ITRM Project Viva Preparation","",
         "> Study guide: explain in your own words and use your actual test results. Do not invent performance figures.",""]
    for i,item in enumerate(items,1):
        out += [f"## {i}. {item['category']}",f"**Question:** {item['question']}",
                f"**Answer guide:** {item['answer']}",""]
    return "\n".join(out)

def main():
    items=generate_questions()
    output=ROOT/"docs"/"VIVA_QUESTION_BANK.md"
    output.write_text(render_markdown(items),encoding="utf-8")
    print(f"Created {output.relative_to(ROOT)} with {len(items)} reviewed questions.")
    print("Personalize answers with your own contribution and actual evaluation outputs.")

if __name__=="__main__":
    main()
