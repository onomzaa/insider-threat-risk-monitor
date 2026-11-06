# Project Presentation Generator — Slide Content

This document is the ready-to-transfer slide script for the research presentation **Insider Threats in Organizations: Causes, Warning Signs, and Risk Management**. Replace placeholders with your institution's details and screenshots from your own local run.

## Slide 1 — Title
**Insider Threats in Organizations: Causes, Warning Signs, and Risk Management**  
A defensive monitoring and analyst-support simulation  
Group members: [insert names]  
Institution / Department: [insert]  
Supervisor: [insert]

Speaker cue: Introduce the research topic and explain that the project demonstrates how authorized security teams can identify suspicious activity patterns for human review.

## Slide 2 — Background
- Organizations rely on employees, contractors, and trusted accounts to access information systems.
- Legitimate access can be misused, accidentally or intentionally.
- Individual events may appear ordinary; patterns and context can make them concerning.
- Insider-risk monitoring must balance security, privacy, fairness, and accountability.

Speaker cue: Emphasize that an insider-risk alert is a signal for investigation, not proof of wrongdoing.

## Slide 3 — Problem Statement
- Traditional controls may focus heavily on external threats.
- Unusual activity by authorized accounts can be difficult to interpret.
- Analysts need context, explainable alerts, and consistent review records.
- Poorly designed monitoring can create false positives and privacy risks.

## Slide 4 — Aim and Objectives
**Aim:** Build a defensive simulation that illustrates insider-risk detection and risk-management workflows.

Objectives:
1. Load and inspect synthetic user activity.
2. Establish baseline behavior and flag deviations.
3. Correlate related events within a time window.
4. add contextual factors and explainable risk scores.
5. Present alerts for analyst review and case handling.
6. Record reviews, evidence references, and audit history.
7. Evaluate the pipeline using clearly labeled synthetic data.

## Slide 5 — System Architecture
Insert the Mermaid architecture diagram from `docs/ARCHITECTURE.md` or export a screenshot of it.

Explain the flow:
Synthetic activity → baseline detection → correlation → context analysis → risk scoring → alert queue → analyst review → case/evidence/audit records.

## Slide 6 — Methodology
- Use controlled, synthetic activity records rather than real employee monitoring data.
- Apply rule/baseline checks to identify deviations.
- Group related activity into event sequences.
- Apply context and transparent scoring rules.
- Display reasons with each alert for analyst interpretation.
- Test modules and end-to-end integration with repeatable cases.

## Slide 7 — Key System Modules
- Activity loader and baseline detection
- Event correlation and context analysis
- Explainable risk scoring
- Alert queue, filters, and analytics
- Incident timeline and case management
- Evidence register and security audit trail
- PDF report generator
- Synthetic scenario generator and guided demonstration
- Configuration, evaluation, and system-health panels

## Slide 8 — Demonstration
Use the dashboard's **Project demonstration • Guided synthetic scenario** panel.

1. Open the guided demonstration.
2. Review the synthetic event sequence.
3. Show how events are correlated.
4. Explain context and score reasons.
5. Review the generated alert.
6. Explain that analyst judgment is required.
7. Show review/case/audit features separately using test records.

Speaker cue: State clearly that the demonstration is synthetic and does not affect the persistent case database.

## Slide 9 — Evaluation
- Unit tests verify individual module behavior.
- Integration tests check the detection-to-review workflow.
- Evaluation metrics are calculated from a small labeled synthetic dataset.
- Explain precision, recall, and F1 only with the actual values shown by your run.
- Do not present synthetic results as proof of real-world accuracy.

Add a screenshot/table of your actual test output and evaluation dashboard here.

## Slide 10 — Risk Management and Ethics
- Use authorized data sources and approved access only.
- Minimize collected data and restrict access by role.
- Preserve review and audit accountability.
- Treat scores as prioritization aids, not disciplinary decisions.
- Validate alerts with human review and documented evidence.
- Avoid profiling protected or personal characteristics.
- Define retention, access, and appeal procedures before real deployment.

## Slide 11 — Limitations and Future Work
Limitations:
- Synthetic data does not represent every real organization.
- Baselines and thresholds may produce false positives or false negatives.
- Behavioral patterns can change over time.
- The prototype is not a production security platform.

Future work:
- Test on approved, anonymized datasets.
- Improve threshold calibration and drift monitoring.
- Add stronger deployment controls and secure storage.
- Conduct usability testing with authorized analysts.
- Document privacy impact and governance requirements.

## Slide 12 — Conclusion
- The simulation demonstrates a transparent insider-risk workflow.
- Correlation and context can help analysts interpret activity.
- Explainability, human review, privacy, and accountability are essential.
- The prototype supports research and learning; it does not automatically determine intent or guilt.

**Thank you — Questions?**

## Suggested defense questions
**Q: What is an insider threat?**  
A risk arising from a person with authorized access who may intentionally or unintentionally harm an organization or its information.

**Q: Does a high score prove malicious intent?**  
No. It indicates activity that may deserve review. Context and evidence must be assessed by an authorized human analyst.

**Q: Why synthetic data?**  
It enables repeatable demonstrations without exposing real employee records or monitoring people without authorization.

**Q: What is event correlation?**  
Connecting related events based on defined conditions, such as a time window and account identity, to analyze a sequence rather than isolated actions.

**Q: What are precision and recall?**  
Precision is the proportion of flagged cases that are positive in the labeled evaluation; recall is the proportion of labeled positive cases detected. Both depend on the evaluation labels and dataset.

**Q: Is this production-ready?**  
No. It is a research simulation. Real deployment would require validated data, security review, governance, privacy assessment, and operational testing.

## Presentation checklist
- [ ] Add group members, institution, supervisor, and date.
- [ ] Capture dashboard screenshots from your actual local run.
- [ ] Record actual test results and evaluation metrics.
- [ ] Rehearse the guided synthetic demonstration.
- [ ] Keep the distinction between alert, evidence, and conclusion clear.
- [ ] Cite research sources on the final slide or in speaker notes.
