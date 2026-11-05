import unittest
import pandas as pd
from evaluation.threshold_analysis import analyze_thresholds


class ThresholdAnalysisTests(unittest.TestCase):
    def test_threshold_analysis_reports_tradeoff(self):
        sample = pd.DataFrame({
            "ground_truth": [1, 1, 0, 0],
            "improved_risk_score": [85, 55, 65, 20],
        })
        result = analyze_thresholds(sample, thresholds=[50, 70])
        at_50 = result[result["threshold"] == 50].iloc[0]
        at_70 = result[result["threshold"] == 70].iloc[0]
        self.assertEqual(at_50["TP"], 2)
        self.assertEqual(at_50["FP"], 1)
        self.assertEqual(at_70["TP"], 1)
        self.assertEqual(at_70["FP"], 0)
        self.assertEqual(at_70["FN"], 1)

    def test_threshold_out_of_range_rejected(self):
        sample = pd.DataFrame({"ground_truth": [1], "improved_risk_score": [80]})
        with self.assertRaises(ValueError):
            analyze_thresholds(sample, thresholds=[101])


if __name__ == "__main__":
    unittest.main()
