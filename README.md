# Insider Threat Risk Monitor

A student research prototype for insider-threat monitoring. It compares a simple activity-rule baseline with an improved event-correlation and context-aware alerting layer.

## Research basis
Motivated by published work on behavior detection, event-based detection, explainability, human context, and evaluation limits. It is not a production security product or proof that unusual activity is malicious.

## Implementation roadmap
- [x] Step 01 — Repository and project plan
- [ ] Step 02 — Activity data and loader
- [ ] Step 03 — Baseline detector
- [ ] Step 04 — Event correlation
- [ ] Step 05 — Context analysis
- [ ] Step 06 — Explainable risk scoring
- [ ] Step 07 — Alert manager
- [ ] Step 08 — Dashboard
- [ ] Step 09 — Scenario tests
- [ ] Step 10 — Evaluation and results
- [ ] Step 11 — Final documentation

## Run locally
Python 3.10+:
```bash
python -m pip install -r requirements.txt
python main.py
```
Use synthetic/sample records only. Alerts are investigation leads, not findings of wrongdoing.
