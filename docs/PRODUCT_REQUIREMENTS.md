# Insider Threat Risk Monitor (ITRM)
## Product Direction and Requirements

**Project type:** Research-backed cybersecurity product prototype  
**Primary users:** SOC analysts, incident responders, security administrators  
**Initial deployment target:** Small organization or isolated security lab  
**Current maturity:** Early prototype; not production-ready

## Product vision
ITRM helps organizations identify, prioritize, and investigate potentially risky activity by trusted users. It combines transparent behavioral rules, event correlation, contextual risk indicators, and human-led case review.

A risk score is a triage signal—not a finding of guilt or proof of malicious intent.

## Core product principles
1. **Explainability:** Every alert must show the events and factors that contributed to its score.
2. **Human review:** No employee sanction or automated accusation based only on an alert.
3. **Privacy by design:** Collect only necessary security telemetry; restrict access and retention.
4. **Authorized use:** Process only logs an organization is permitted to monitor.
5. **Evidence integrity:** Preserve source events, timestamps, and analyst actions with an audit trail.
6. **Evaluation before claims:** Publish measured precision, recall, false-positive rate, and test conditions; never claim detection effectiveness without evidence.
7. **Safe failure:** Missing or malformed data must be visible and must not silently produce reassuring scores.

## Product modules
- **Telemetry ingestion:** Import CSV initially; later add authenticated connectors to approved sources such as endpoint, identity, file-access, and SIEM logs.
- **Normalization:** Map source-specific records into a common event schema and validate timestamps/fields.
- **Detection:** Transparent baseline rules and behavior indicators.
- **Correlation:** Group related events into incidents using configurable time windows and entity context.
- **Context & risk:** Apply role/resource/time context and produce a bounded, explainable score.
- **Alert queue:** Prioritize incidents and support analyst dispositions.
- **Case management:** Persistent cases, notes, evidence references, assignment, status history, and review trail.
- **Reporting & evaluation:** Export reports and run reproducible labeled-scenario tests.
- **Administration:** Roles, permissions, configuration, retention, and audit settings.

## Initial event schema
Required: event_id, timestamp, user_id, event_type/action, resource, source  
Optional: department/role, device_id, source_ip, outcome, sensitivity label, metadata  
Data minimization: avoid collecting message contents, passwords, or unrelated personal information.

## Risk workflow
1. Receive an authorized event.
2. Validate and normalize it.
3. Apply baseline and context checks.
4. Correlate related events.
5. Generate an explainable review-priority score.
6. Analyst reviews source events and context.
7. Analyst records a disposition and rationale.
8. System retains an access-controlled audit history.

## MVP acceptance criteria
- [ ] Import a documented, validated event format.
- [ ] Reject or flag malformed records and timezone ambiguity.
- [ ] Explain every scored incident with traceable factors.
- [ ] Compare baseline and improved detection on labeled scenarios.
- [ ] Report confusion matrix, precision, recall, F1, and false-positive rate.
- [ ] Persist cases and analyst actions across restarts.
- [ ] Enforce analyst/admin access boundaries.
- [ ] Log administrative and case-review actions.
- [ ] Export a report with data source, time range, and limitations.
- [ ] Include privacy, retention, deployment, and incident-response guidance.

## Development stages
### Stage 1 — Research and reproducibility
Labeled synthetic scenarios, baseline-vs-improved evaluation, tests, and limitations.

### Stage 2 — Reliable data pipeline
Schema validation, normalization, timezone handling, duplicate detection, and import diagnostics.

### Stage 3 — Analyst workflow
Persistent case database, review notes, assignment, status history, and evidence references.

### Stage 4 — Security and deployment
Authentication, role-based access, secrets management, audit logging, secure configuration, backups, and deployment documentation.

### Stage 5 — Integration and pilot
Connect one authorized log source in a controlled lab; test with security staff and privacy stakeholders; measure alert quality and analyst workload.

## Deployment safeguards
- Do not deploy against employee data without organizational authorization and appropriate privacy/legal review.
- Keep access to sensitive logs restricted and auditable.
- Define retention and deletion schedules.
- Use least privilege and encryption in transit/at rest.
- Treat all alerts as hypotheses requiring investigation.
- Never use the score alone for disciplinary, employment, or other high-impact decisions.

## Product status
The existing Streamlit dashboard, event correlation, context analysis, risk scoring, alert review, and synthetic scenarios are demonstrator components. Persistent storage, robust ingestion, authentication, audit trail, deployment hardening, and real-source validation remain future work.
