import tempfile
import unittest
from pathlib import Path
import pandas as pd
from evaluation.research_report import build_report, generate_report

class ResearchReportTests(unittest.TestCase):
    def test_requires_evaluation_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                build_report(tmp)

    def test_builds_report_with_metrics_and_predictions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pd.DataFrame([{"method":"Baseline","TP":1,"FP":1,"TN":2,"FN":0,
                "precision":.5,"recall":1.0,"F1":.6667,"false_positive_rate":.3333}]).to_csv(root/"evaluation_metrics.csv",index=False)
            pd.DataFrame([{"employee_id":"synth1","ground_truth":1,"baseline_detected":1,
                "improved_risk_score":80,"improved_detected":1},
                {"employee_id":"synth2","ground_truth":0,"baseline_detected":0,
                "improved_risk_score":10,"improved_detected":0}]).to_csv(root/"scenario_predictions.csv",index=False)
            report = build_report(root)
            self.assertIn("synthetic", report.lower())
            self.assertIn("Precision", report)
            path = generate_report(root)
            self.assertTrue(path.exists())
            self.assertIn("Limitations", path.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
