import tempfile
import unittest
from pathlib import Path
import pandas as pd

from modules.evaluation_dashboard import load_evaluation_metrics


class EvaluationDashboardTests(unittest.TestCase):
    def test_missing_file_returns_empty_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertTrue(load_evaluation_metrics(Path(directory) / "missing.csv").empty)

    def test_valid_metrics_load(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metrics.csv"
            pd.DataFrame([{
                "method": "baseline", "precision": .8, "recall": .7, "F1": .75,
                "false_positive_rate": .1, "TP": 7, "FP": 2,
                "TN": 18, "FN": 3,
            }]).to_csv(path, index=False)
            self.assertEqual(load_evaluation_metrics(path).iloc[0]["method"], "baseline")

    def test_missing_columns_raise_value_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.csv"
            pd.DataFrame([{"method": "baseline"}]).to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_evaluation_metrics(path)


if __name__ == "__main__":
    unittest.main()
