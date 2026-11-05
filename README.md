# Insider Threat Risk Monitor (ITRM)

A research-backed cybersecurity prototype being developed toward an organizational insider-threat monitoring and investigation platform. It compares a transparent activity-rule baseline with event correlation and context-aware, explainable alert triage. **Current status: early prototype—not production-ready.**

See [Product Requirements and Roadmap](docs/PRODUCT_REQUIREMENTS.md) for the intended organizational use, MVP acceptance criteria, privacy safeguards, and deployment stages.

## Research basis
Motivated by published work on behavior detection, event-based detection, explainability, human context, and evaluation limits. It is not a production security product or proof that unusual activity is malicious.

## Implemented modules
- `modules/event_correlator.py` — groups events for the same employee within a time window.
- `modules/context_analyzer.py` — checks role scope, after-hours activity, sensitive resources, and review-worthy actions.
- `modules/risk_engine.py` — transparent 0–100 score with human-readable reasons.
- `tests/test_risk_engine.py` — basic unit tests.

## Run tests
From the project root:
```powershell
python -m unittest discover -s tests -v
```

## Example integration
```python
from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident

incidents = correlate_events(events, window_minutes=60)
for incident in incidents:
    contexts = [analyze_context(e, user_profiles) for e in incident["events"]]
    result = score_incident(incident["events"], contexts)
    print(incident["employee_id"], result)
```

## Roadmap
- [x] Repository and project plan
- [x] Event correlation
- [x] Context analysis
- [x] Explainable risk scoring
- [ ] Connect modules to activity loader and dashboard
- [ ] Alert manager and scenario tests
- [ ] Baseline-vs-improved evaluation
- [ ] Final documentation and presentation

## Responsible use
Use synthetic or authorized activity logs only. Restrict access to logs, minimize personal data, and require a human analyst to validate alerts. A high score is not proof of malicious intent.

## Alert manager and scenario tests
- `modules/alert_manager.py` creates review-ready alerts, validates analyst dispositions, and sorts the queue.
- `tests/test_scenarios.py` includes normal activity, suspicious transfer, and analyst-review checks.
- `data/scenario_logs.csv` contains clearly synthetic scenario records for demonstration.

Run the tests:
```powershell
python -m unittest discover -s tests -v
```
If your repository uses pytest, also run:
```powershell
python -m pytest -q
```

The dashboard's review status is stored in Streamlit session state for demonstration; it resets when the app session restarts. It is not a persistent case-management database.


## Research-gap evaluation (Stage 1)
This evaluation directly tests the research gap: whether event correlation plus role/time/resource context can improve explainable insider-threat triage over simple event rules, while measuring false positives.

Run from the repository root:
```powershell
python -m evaluation.evaluate
```

It compares both methods against the labels in `data/labeled_evaluation_scenarios.csv` and writes:
- `results/scenario_predictions.csv` — per-employee ground truth, baseline alert, improved score, and prediction.
- `results/evaluation_metrics.csv` — TP, FP, TN, FN, precision, recall, F1, and false-positive rate.

**Research integrity:** These are hand-labeled synthetic scenarios. Metrics describe only this small test set and must not be presented as real-world organizational detection accuracy. The threshold (70) is a prototype setting, not a validated operational threshold.


## Risk threshold sensitivity (research-gap follow-up)
After generating employee predictions, run:
```powershell
python -m evaluation.threshold_analysis
```
This evaluates candidate risk thresholds from 30 to 100 in steps of 10 and writes `results/threshold_analysis.csv`. It reports precision, recall, F1, and false-positive rate at each threshold so the analyst can inspect trade-offs. Threshold analysis is exploratory: the same small synthetic set is not independent validation, and no threshold is approved for real organizational use.


## Persistent case management (Stage 3 prototype)
The dashboard can create investigation cases from alerts, assign an analyst, update status and notes, and inspect a case activity history. Records are stored in `data/cases.db` using SQLite and persist across dashboard restarts. Case creation is idempotent per alert ID, so the same alert does not create duplicate cases.

Run the dashboard:
```powershell
python -m streamlit run dashboard/dashboard.py
```

**Prototype limitation:** the database currently has no authentication, role-based access, or tamper-resistant audit controls. Do not use real employee records or deploy this feature operationally until access controls, privacy review, retention, and security hardening are implemented.


## Analyst authentication and session controls
- Local analyst login uses PBKDF2 password hashes; account creation is administrator-only in the dashboard.
- Analysts can change their own password after verifying the current password.
- Dashboard sessions expire after 15 minutes without a Streamlit rerun and after 8 hours absolute. Expiry is checked when the app reruns (this prototype does not run a background idle timer).
- These controls are prototype safeguards, not production-grade identity/session management. Use only on a trusted local machine and synthetic/authorized data.


## Persistent alert review workflow
- Analyst alert dispositions (status and review note) are stored in SQLite in the same local database file as case management.
- Each saved review records the analyst username and UTC review timestamp.
- Create/update review events are added to the hash-chained audit log.
- Reviews reload when the dashboard restarts, provided the same local database is used.
- This persistence is for the research prototype and does not establish production-grade audit integrity or secure multi-user deployment.


## Dashboard risk analytics

The dashboard includes charts for incident counts by risk level and disposition, plus a risk-score distribution. These charts summarize the currently generated synthetic incident alerts and are intended for analyst triage—not proof of malicious behavior.


## Incident activity timeline

The analyst review panel displays a chronological activity timeline for the selected employee, including timestamps, actions, resources, after-hours and sensitive-resource indicators, and event details. The view uses the project's synthetic activity records; indicators are contextual and are not proof of misconduct.


## PDF investigation reports

Analysts can download a PDF from the selected alert's review panel. Reports include alert identity and score, disposition/reviewer details, risk explanations, analyst and case notes, and a chronological activity table. Reports are generated locally from synthetic or authorized records and remain subject to human review.
