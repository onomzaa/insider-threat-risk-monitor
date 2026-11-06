import tempfile
import unittest
from pathlib import Path
import pandas as pd

from modules.final_research_document import build_report


class FinalResearchDocumentTests(unittest.TestCase):
    def test_missing_metrics_are_not_fabricated(self):
        with tempfile.TemporaryDirectory() as temp:
            report = build_report(Path(temp) / "missing.csv", Path(temp) / "pred.csv")
        self.assertIn("not available yet", report.lower())
        self.assertIn("Not evaluated", report)
        self.assertNotIn("99.9%", report)

    def test_actual_metrics_and_employee_count_are_included(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            metrics = root / "metrics.csv"
            predictions = root / "predictions.csv"
            pd.DataFrame([{"method": "Baseline rules", "TP": 2, "FP": 1, "TN": 3,
                           "FN": 0, "precision": 0.6667, "recall": 1.0, "F1": 0.8,
                           "false_positive_rate": 0.25}]).to_csv(metrics, index=False)
            pd.DataFrame({"employee_id": ["A", "B", "A"]}).to_csv(predictions, index=False)
            report = build_report(metrics, predictions)
        self.assertIn("0.6667", report)
        self.assertIn("**2**", report)


if __name__ == "__main__":
    unittest.main()
