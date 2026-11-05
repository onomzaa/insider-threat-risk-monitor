# Synthetic Evaluation Scenario Design

## Purpose
This dataset tests whether the Insider Threat Risk Monitor can distinguish suspicious activity from legitimate activity using event correlation and context. All records and employee identifiers are fictional.

## Scenario coverage
The labeled dataset includes:
- Ordinary workstation/report activity.
- Unauthorized after-hours sensitive data transfer.
- Authorized HR access to sensitive employee/payroll records.
- Approved IT maintenance outside normal hours.
- Daytime activity outside role scope.
- Repeated failed login attempts.
- Privilege-change followed by download and sharing.
- Legitimate late-shift work.
- Low-volume suspicious export/sharing and single-event sensitive access.

## Ground truth
The `ground_truth` value is assigned by the scenario author:
- `1`: scenario is intended to represent insider-threat behavior requiring investigation.
- `0`: scenario is intended to represent legitimate/authorized behavior.

These labels are scenario assumptions, not forensic findings or proof of intent. A real organization would require authorized investigation and human review.

## Important evaluation limitation
The scenarios are synthetic and intentionally authored. They are useful for regression tests, demonstrations, and checking score behavior. They are **not an independent real-world test set**. Do not present their metrics as proof of operational accuracy.

## Reproducible commands
From the repository root:
```bash
python -m evaluation.evaluate
python -m evaluation.threshold_analysis
python -m unittest discover -s tests -v
```

Review precision, recall, F1, and false-positive rate together. A threshold should not be selected from this development dataset alone for production use.
