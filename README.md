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


## Incident evidence register

Analysts can attach evidence metadata to an alert from the Analyst Review panel: title, description, and a reference to a synthetic or authorized source (for example, a scenario log row). Entries persist in the shared local SQLite database and record analyst attribution and timestamps. Evidence additions are written to the hash-chained audit log.

The register stores references and descriptions only; it does not upload or collect raw files. Use approved, minimized evidence and follow applicable privacy and retention requirements.


## Risk mitigation recommendations

The Analyst Review panel maps explainable risk factors to prioritized, advisory review steps (such as validating data movement, checking access changes, confirming after-hours schedules, and reviewing sensitive-resource access). Recommendations do not automatically disable accounts, block activity, or make accusations; analysts must validate context and follow approved organizational procedures.


## Behavioral anomaly indicators

The analyst review panel includes explainable peer comparisons for repeated role-unusual actions/resources, elevated action shares, and concentrated after-hours activity. Comparisons require a configurable minimum number of same-role peers (default: two). Small synthetic datasets can produce unstable comparisons; findings are review indicators, not evidence of intent or misconduct.


## End-to-end pipeline checks

`tests/test_pipeline_integration.py` exercises the synthetic pipeline from event correlation through context analysis, risk scoring, alert creation, filtering, and analyst disposition. It also verifies that events belonging to different fictional employees remain separate incidents.

Run the complete suite after pulling the latest changes:
```powershell
python -m unittest discover -s tests -v
```

Integration tests use fixed fictional events only; they do not connect to an organization's systems or collect employee activity.


## System health and project readiness

The authenticated dashboard includes a **System health • Project readiness** panel. It checks the activity dataset, local configuration, case database availability, synthetic evaluation output, ReportLab dependency, core module files, and audit-chain verification. These are read-only availability/integrity checks—not a production security certification.

The panel is useful before a class demonstration. Generate evaluation metrics with `python -m evaluation.evaluate`; install PDF support with `python -m pip install reportlab` if the PDF dependency check reports Attention.


## Guided project demonstration

After signing in, expand **Project demonstration • Guided synthetic scenario** and click **Run guided demonstration**. The walkthrough displays a fixed fictional sequence, correlation, context checks, explainable risk score, and analyst validation step. The demonstration alert is illustrative and is not written to the persistent case register. No real employee activity is collected.

Tests: `python -m unittest discover -s tests -v` (includes `tests/test_demo_scenario.py`).


## Presentation and project defense

- [System architecture](docs/ARCHITECTURE.md) — module flow, trust boundaries, and prototype limitations.
- [Demonstration and defense guide](docs/DEMONSTRATION_AND_DEFENSE_GUIDE.md) — objectives, demo steps, evaluation interpretation, ethical safeguards, slide outline, and sample defense questions.

These documents describe the educational prototype and its synthetic-data scope; they do not claim real-world detection effectiveness.

- [Presentation slide script](docs/PRESENTATION_SLIDE_SCRIPT.md) — complete 12-slide draft, speaker cues, evaluation/ethics guidance, and defense Q&A.

## PowerPoint presentation generator

Generate an editable 12-slide project deck locally with speaker notes:
```powershell
python -m pip install python-pptx
python scripts/generate_presentation.py
```
Output: `presentation/Insider_Threat_Risk_Monitor.pptx`. See [presentation instructions](presentation/README.md).

## Project finalization checklist

After sign-in, open **Project finalization • Submission readiness**. It checks the core pipeline, dashboard, research documentation, generated deliverables, test files, submission builder, and submission integrity verifier, plus optional presentation/PDF dependencies. It is a read-only presence check—not a quality or test certification. Also run:
```powershell
python -m unittest discover -s tests -v
python -m evaluation.evaluate
python scripts/generate_presentation.py
python -m modules.project_finalization
```

## Research evaluation report generator

After running the synthetic evaluation and optional threshold analysis, generate a formal report:
```powershell
python -m evaluation.evaluate
python -m evaluation.threshold_analysis
python -m evaluation.research_report
```
This writes `results/research_evaluation_report.md` and, when ReportLab is installed, `results/research_evaluation_report.pdf`. The report documents synthetic-data scope and limitations; it does not claim real-world effectiveness.


## Safe submission bundle

Create a ZIP containing an explicit allowlist of project source, tests, documentation, evaluation outputs, and the generated presentation:
```powershell
python -m modules.submission_bundle
```
Output: `dist/ITRM_Submission_Bundle.zip`. The ZIP includes `SUBMISSION_MANIFEST.json` with SHA-256 hashes and a list of allowlisted files not present. The allowlist includes the final academic report, viva question bank, final validation summaries, evaluation artifacts, and generated presentation when available. The builder excludes local analyst credentials, SQLite case data, audit logs, environment secrets, virtual environments, caches, Git metadata, and symlinked files that could point outside the project. Review the manifest and contents before submitting; use synthetic/demo data only.

Test the bundle safeguards:
```powershell
python -m unittest tests.test_submission_bundle -v
```


## Final quality audit

Run the read-only project inventory and Python syntax scan from PowerShell:
```powershell
python -m modules.quality_audit
python -m unittest tests.test_quality_audit -v
python -m unittest discover -s tests -v
```

After signing in, the dashboard's **Final audit • Quality assurance** panel can run the same checks and export a JSON summary. It checks required files, parses Python source for syntax errors, and checks evaluation artifacts. It does not execute tests, inspect runtime behavior, or certify security; run the complete test suite separately.


## Viva / project defense preparation

After sign-in, open **Project defense • Viva preparation**, choose how many questions to display, and click **Prepare viva questions**. Review the questions and answer guides, then download the Markdown study guide. The reviewed question bank covers motivation, objectives, architecture, detection, explainability, evaluation metrics, false positives, limitations, ethics, synthetic data, and future work.

Generate the guide from PowerShell as well:
```powershell
python -m modules.viva_assistant
python -m unittest tests.test_viva_assistant -v
```
This writes `docs/VIVA_QUESTION_BANK.md`. Use the answer guides as prompts, add your actual contributions and evaluation results, and explain the material in your own words.


## Final system validation

Run the complete unittest suite and save timestamped output as JSON and Markdown:
```powershell
python -m modules.final_validation
python -m unittest tests.test_final_validation -v
```

The authenticated dashboard also has **Final system validation • Integration tests** → **Run full system validation**. This runs the same test suite locally and displays its output. Reports are saved to `results/final_validation.json` and `results/final_validation.md`. A PASS means the discovered automated tests passed—not that the prototype is production-secure or validated on real organizational data.


## Final academic research report

Generate a structured report draft from the actual evaluation files (without inventing metrics):
```powershell
python -m evaluation.evaluate
python -m evaluation.threshold_analysis
python -m modules.final_research_document
python -m unittest tests.test_final_research_document -v
```
Output: `docs/FINAL_RESEARCH_REPORT.md`. If evaluation metrics are missing, the report explicitly says so. Replace the administrative placeholders, verify reference editions/details, and critically discuss results before submission. The evaluation uses synthetic, hand-labeled scenarios only.

## Presentation evaluation integration
The PowerPoint generator now reads `results/evaluation_metrics.csv` when building slide 9. It inserts the actual precision, recall, F1, false-positive rate, and confusion-matrix counts for each available method. If the metrics file is missing or has an unexpected schema, the slide explicitly instructs the presenter to run the evaluation instead of showing invented figures.

Regenerate after evaluation:
```powershell
python -m evaluation.evaluate
python scripts/generate_presentation.py
python -m unittest tests.test_presentation_evaluation -v
```
Review the generated slide and speaker notes before presenting. Results remain limited to the hand-labeled synthetic scenarios.


## Submission bundle integrity verification

After creating the safe ZIP, verify its manifest, file hashes and sizes, ZIP CRC, archive paths, and that every packaged file is declared in the manifest:
```powershell
python -m modules.submission_bundle
python -m modules.submission_verifier
python -m unittest tests.test_submission_verifier -v
```
The verifier writes `results/submission_verification.json` and `results/submission_verification.md`. It exits with a non-zero status if verification fails. Review both the bundle and verification report before sharing; a PASS confirms package integrity and basic packaging safeguards, not project security or research validity.
