"""Reproducible employee-level evaluation on labeled synthetic scenarios.

Run from the repository root:
    python -m evaluation.evaluate

Ground truth is scenario authoring, not evidence about real-world accuracy.
"""
from pathlib import Path
import pandas as pd

from modules.baseline_detector import detect_baseline
from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "labeled_evaluation_scenarios.csv"
OUT = ROOT / "results"
HIGH_RISK_THRESHOLD = 70


def confusion_metrics(y_true, y_pred):
    tp = sum(a == 1 and b == 1 for a, b in zip(y_true, y_pred))
    fp = sum(a == 0 and b == 1 for a, b in zip(y_true, y_pred))
    tn = sum(a == 0 and b == 0 for a, b in zip(y_true, y_pred))
    fn = sum(a == 1 and b == 0 for a, b in zip(y_true, y_pred))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn,
            "precision": round(precision, 4), "recall": round(recall, 4),
            "F1": round(f1, 4), "false_positive_rate": round(fpr, 4)}


def evaluate():
    df = pd.read_csv(DATA)
    required = {"timestamp", "employee_id", "role", "action", "resource",
                "after_hours", "sensitive", "allowed_resources", "ground_truth"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="raise")
    for col in ("after_hours", "sensitive"):
        df[col] = df[col].astype(str).str.lower().map({"true": True, "false": False})
        if df[col].isna().any():
            raise ValueError(f"Invalid boolean values in {col}")
    if not set(df["ground_truth"].unique()).issubset({0, 1}):
        raise ValueError("ground_truth must contain only 0 or 1")

    truth = df.groupby("employee_id")["ground_truth"].nunique()
    if (truth > 1).any():
        raise ValueError("Each employee must have one consistent ground_truth label")
    labels = df.groupby("employee_id")["ground_truth"].first().astype(int).to_dict()

    # Adapt labeled records to the existing single-event baseline interface.
    baseline_input = df.rename(columns={"employee_id": "user", "action": "event"}).copy()
    baseline_alerts = detect_baseline(baseline_input)
    baseline_detected = set(baseline_alerts["user"].astype(str)) if not baseline_alerts.empty else set()

    # Build role/resource profiles and incidents for the improved method.
    profiles = {}
    events = []
    for _, row in df.iterrows():
        uid = str(row["employee_id"])
        profiles[uid] = {
            "role": str(row["role"]),
            "allowed_resources": [x.strip() for x in str(row["allowed_resources"]).split(";") if x.strip()],
        }
        events.append({
            "employee_id": uid,
            "timestamp": row["timestamp"].isoformat(),
            "action": str(row["action"]),
            "resource": str(row["resource"]),
            "after_hours": bool(row["after_hours"]),
            "sensitive": bool(row["sensitive"]),
        })

    incidents = correlate_events(events, window_minutes=60)
    improved_scores = {}
    for incident in incidents:
        uid = str(incident["employee_id"])
        contexts = [analyze_context(event, profiles) for event in incident["events"]]
        result = score_incident(incident["events"], contexts)
        improved_scores[uid] = max(improved_scores.get(uid, 0), result["risk_score"])

    rows = []
    for uid, actual in sorted(labels.items()):
        baseline_pred = int(uid in baseline_detected)
        score = int(improved_scores.get(uid, 0))
        improved_pred = int(score >= HIGH_RISK_THRESHOLD)
        rows.append({
            "employee_id": uid, "ground_truth": actual,
            "baseline_detected": baseline_pred,
            "improved_risk_score": score, "improved_detected": improved_pred,
            "threshold": HIGH_RISK_THRESHOLD,
        })

    results = pd.DataFrame(rows)
    baseline_metrics = confusion_metrics(results["ground_truth"], results["baseline_detected"])
    improved_metrics = confusion_metrics(results["ground_truth"], results["improved_detected"])
    metrics = pd.DataFrame([
        {"method": "Baseline rules", **baseline_metrics},
        {"method": f"Correlated + context (threshold {HIGH_RISK_THRESHOLD})", **improved_metrics},
    ])

    OUT.mkdir(exist_ok=True)
    results.to_csv(OUT / "scenario_predictions.csv", index=False)
    metrics.to_csv(OUT / "evaluation_metrics.csv", index=False)
    print("\nEmployee-level predictions:")
    print(results.to_string(index=False))
    print("\nMetrics:")
    print(metrics.to_string(index=False))
    print(f"\nSaved: {OUT / 'scenario_predictions.csv'}")
    print(f"Saved: {OUT / 'evaluation_metrics.csv'}")
    print("\nLIMITATION: These are synthetic, hand-labeled scenarios. Metrics demonstrate")
    print("behavior on this test set only; they do not establish real-world effectiveness.")


if __name__ == "__main__":
    evaluate()
