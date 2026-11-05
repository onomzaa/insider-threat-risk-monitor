# Insider Threat Risk Monitor

A student research prototype for insider-threat monitoring. It compares a simple activity-rule baseline with an improved event-correlation and context-aware alerting layer.

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
