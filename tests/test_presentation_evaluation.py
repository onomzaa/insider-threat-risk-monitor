import csv
import tempfile
import unittest
from pathlib import Path

from scripts.generate_presentation import evaluation_slide_content, load_evaluation_summary


class PresentationEvaluationTests(unittest.TestCase):
    def test_missing_metrics_are_not_invented(self):
        with tempfile.TemporaryDirectory() as tmp:
            bullets, notes = evaluation_slide_content(Path(tmp) / 'missing.csv')
        self.assertIn('Evaluation metrics not generated yet', bullets)
        self.assertIn('not available', notes)
        self.assertFalse(any('Precision 0.' in item for item in bullets))

    def test_actual_metrics_are_inserted_into_slide(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'metrics.csv'
            with path.open('w', newline='', encoding='utf-8') as handle:
                writer = csv.DictWriter(handle, fieldnames=['method','TP','FP','TN','FN','precision','recall','F1','false_positive_rate'])
                writer.writeheader()
                writer.writerow({'method':'Baseline','TP':3,'FP':1,'TN':4,'FN':2,'precision':'0.750','recall':'0.600','F1':'0.667','false_positive_rate':'0.200'})
            rows = load_evaluation_summary(path)
            bullets, notes = evaluation_slide_content(path)
        self.assertEqual(rows[0]['method'], 'Baseline')
        self.assertTrue(any('Precision 0.750' in item and 'F1 0.667' in item for item in bullets))
        self.assertIn('TP=3', notes)


if __name__ == '__main__':
    unittest.main()