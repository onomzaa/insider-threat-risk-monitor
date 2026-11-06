"""Generate a final academic research report using actual evaluation artifacts.

Run: python -m modules.final_research_document
No performance values are invented: missing evaluation files are reported explicitly.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT = ROOT / "docs" / "FINAL_RESEARCH_REPORT.md"


def _metrics_section(path: Path) -> str:
    if not path.exists():
        return ("Evaluation metrics are not available yet. Run "
                "`python -m evaluation.evaluate` and regenerate this report.\n")
    frame = pd.read_csv(path)
    if frame.empty:
        return "The metrics file exists but contains no rows.\n"
    required = {"method", "TP", "FP", "TN", "FN", "precision", "recall", "F1",
                "false_positive_rate"}
    missing = required - set(frame.columns)
    if missing:
        return f"Metrics file has unexpected schema; missing columns: {', '.join(sorted(missing))}.\n"
    return frame[list(required)].to_markdown(index=False) + "\n"


def build_report(metrics_path: Path = RESULTS / "evaluation_metrics.csv",
                 predictions_path: Path = RESULTS / "scenario_predictions.csv") -> str:
    metrics = _metrics_section(metrics_path)
    n_employees = "Not evaluated"
    if predictions_path.exists():
        predictions = pd.read_csv(predictions_path)
        if "employee_id" in predictions.columns:
            n_employees = str(predictions["employee_id"].nunique())
    return f"""# Insider Threats in Organizations: Causes, Warning Signs, and Risk Management
## Insider Threat Risk Monitor (ITRM) — Final Research Report

**Author/group:** [Insert names and registration numbers]  
**Institution/department:** [Insert institution and department]  
**Course/supervisor:** [Insert course and supervisor]  
**Date:** [Insert submission date]

> Research integrity note: all reported performance figures below are read from the project's generated evaluation artifacts. Replace bracketed administrative fields before submission.

## Abstract
This project presents the Insider Threat Risk Monitor (ITRM), a defensive prototype for identifying potentially risky insider activity in organizational information systems. It combines rule-based indicators, event correlation, contextual analysis, risk scoring, alert review, case tracking, and audit-oriented records. Evaluation uses synthetic, hand-labeled employee activity scenarios. The prototype is intended to support analysts—not automatically accuse or discipline employees. Quantitative results are limited to the constructed test scenarios and should not be interpreted as evidence of operational effectiveness.

## Chapter One: Introduction
### 1.1 Background
Insider threats involve misuse of legitimate access by employees, contractors, or other trusted users. Risk may arise from malicious intent, negligence, compromised accounts, or policy violations. Traditional perimeter-focused controls may not fully address activity performed through authorized identities.

### 1.2 Problem statement
Organizations need a way to bring together activity indicators and contextual information while preserving analyst review. Isolated events can be ambiguous; excessive alerts can also burden security teams. This project explores a small, explainable monitoring workflow using synthetic data.

### 1.3 Aim and objectives
The aim is to develop a defensive prototype that demonstrates insider-risk monitoring and response support. Objectives are to:
- model synthetic employee activity and labeled scenarios;
- detect selected rule-based indicators;
- correlate events and analyze role/resource context;
- calculate interpretable risk scores and present alerts;
- support case review, audit records, and reproducible evaluation.

### 1.4 Research questions
1. How does event correlation and context change detection outcomes relative to baseline rules on the selected synthetic scenarios?
2. What trade-offs arise between detection coverage and false positives?
3. How can analyst review and auditability be incorporated into a prototype?

### 1.5 Scope and significance
The work is a local academic prototype using synthetic records. It does not connect to production employee systems, collect real personnel data, or automate disciplinary decisions. It demonstrates concepts that may inform further controlled research.

## Chapter Two: Conceptual Review
### 2.1 Insider threat
Insider-risk scenarios may involve misuse of privileges, inappropriate access, data handling violations, negligence, or compromised credentials. Intent cannot reliably be inferred from a single technical event.

### 2.2 Detection and contextual analysis
Rule-based detection is understandable but may miss combinations of activity. Correlation groups related events; contextual analysis considers factors such as role, permitted resources, sensitivity, and time. Risk scores are prioritization aids, not proof of misconduct.

### 2.3 Human-centered response
Security alerts should be validated by authorized analysts, documented, and handled proportionately. Access controls, privacy safeguards, least privilege, and clear retention policies remain essential.

## Chapter Three: Methodology
### 3.1 Research design
A prototype implementation and scenario-based quantitative evaluation were used. The dataset is synthetic and hand-labeled; it is not a random sample of real organizations.

### 3.2 System workflow
1. Load synthetic activity records.
2. Apply baseline rule checks.
3. Correlate related activity within a configured time window.
4. analyze event context against role/resource profiles.
5. score incidents and generate alerts.
6. display results for analyst review and case management.
7. compare predictions with scenario labels using confusion-matrix metrics.

### 3.3 Evaluation measures
True positives (TP), false positives (FP), true negatives (TN), and false negatives (FN) are used to calculate precision, recall, F1, and false-positive rate. These measures describe agreement with scenario labels—not real-world truth.

### 3.4 Ethical considerations
The system uses synthetic data in this study. Any future deployment would require authorization, privacy impact assessment, access restrictions, secure retention, transparency, bias evaluation, and meaningful human review. Scores must not be treated as employee guilt.

## Chapter Four: Results
### 4.1 Evaluation sample
Number of distinct employees represented in prediction output: **{n_employees}**.

### 4.2 Recorded evaluation metrics
{metrics}
### 4.3 Interpretation
Interpret results only in relation to the synthetic scenarios and the assumptions used to label them. A higher metric on this dataset does not establish that the system will perform similarly in a real organization. Review false positives and false negatives at scenario level before drawing conclusions.

## Chapter Five: Discussion, Limitations, and Conclusion
### 5.1 Discussion
The prototype illustrates how combining related events and role/resource context can provide an explainable alerting workflow. Baseline and enhanced results should be compared using the generated metrics and scenario predictions. Operational usefulness also depends on alert quality, analyst workload, policy context, and investigation procedures.

### 5.2 Limitations
- Synthetic, hand-authored scenarios may not represent real behavior or adversarial adaptation.
- Scenario labels encode author assumptions and can contain bias.
- Dataset size and diversity limit generalization.
- Thresholds are design choices and require validation.
- Risk scores are simplified indicators, not intent classifiers.
- No production deployment or real employee monitoring was conducted.

### 5.3 Conclusion
ITRM provides an academic demonstration of defensive insider-risk monitoring, including detection, context, risk scoring, analyst review, case records, and evaluation. Its outputs should be treated as investigative leads. The project does not claim validated real-world detection accuracy.

### 5.4 Recommendations
Future work should expand independently reviewed synthetic scenarios, evaluate threshold trade-offs, conduct privacy and fairness assessments, document analyst procedures, and—only with formal authorization—study carefully controlled anonymized organizational data.

## Appendix A: Reproducibility
From the repository root, run:
```powershell
python -m evaluation.evaluate
python -m evaluation.threshold_analysis
python -m modules.final_research_document
```
Evaluation outputs are stored under `results/`; this report is generated at `docs/FINAL_RESEARCH_REPORT.md`.

## References
- National Institute of Standards and Technology (NIST). *Computer Security Incident Handling Guide*, SP 800-61 Rev. 2.
- National Institute of Standards and Technology (NIST). *Security and Privacy Controls for Information Systems and Organizations*, SP 800-53 Rev. 5.
- Center for Internet Security (CIS). *CIS Critical Security Controls* (consult the version applicable to the study).
- Add the exact editions, URLs, access dates, and any course-approved sources consulted; verify citation details before submission.
"""


def generate_report(output: Path = OUTPUT) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_report(), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(f"Generated: {generate_report()}")
