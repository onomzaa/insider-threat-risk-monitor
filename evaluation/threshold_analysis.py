"""Threshold sensitivity analysis for insider-threat risk triage.

Evaluates trade-offs across candidate review thresholds on labeled synthetic
scenarios. It does not select a production threshold automatically.
"""
from pathlib import Path
import pandas as pd
from evaluation.evaluate import confusion_metrics

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS = ROOT / "results" / "scenario_predictions.csv"
OUT = ROOT / "results" / "threshold_analysis.csv"
DEFAULT_THRESHOLDS = range(30, 101, 10)


def analyze_thresholds(predictions, thresholds=DEFAULT_THRESHOLDS):
    required = {"ground_truth", "improved_risk_score"}
    missing = required - set(predictions.columns)
    if missing:
        raise ValueError(f"Missing prediction columns: {sorted(missing)}")
    actual = predictions["ground_truth"].astype(int).tolist()
    scores = predictions["improved_risk_score"].astype(int).tolist()
    rows = []
    for threshold in thresholds:
        if not 0 <= threshold <= 100:
            raise ValueError("Thresholds must be between 0 and 100")
        predicted = [int(score >= threshold) for score in scores]
        rows.append({"threshold": threshold, **confusion_metrics(actual, predicted)})
    return pd.DataFrame(rows)


def main():
    if not PREDICTIONS.exists():
        raise FileNotFoundError(
            f"{PREDICTIONS} not found. Run python -m evaluation.evaluate first."
        )
    predictions = pd.read_csv(PREDICTIONS)
    table = analyze_thresholds(predictions)
    OUT.parent.mkdir(exist_ok=True)
    table.to_csv(OUT, index=False)
    print("\nRisk threshold sensitivity:")
    print(table.to_string(index=False))
    print(f"\nSaved: {OUT}")
    print("\nInterpretation: higher thresholds generally reduce alerts but may increase")
    print("missed cases. Review precision/recall and false-positive rate together.")
    print("Do not tune and report performance on the same scenarios as independent validation.")


if __name__ == "__main__":
    main()
