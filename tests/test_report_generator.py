import unittest
from modules.report_generator import generate_alert_report

class ReportGeneratorTests(unittest.TestCase):
    def test_report_returns_pdf_bytes(self):
        alert={"alert_id":"AL-test","employee_id":"emp01","risk_score":75,"risk_level":"High",
               "status":"Under Review","reasons":["After-hours activity"],"analyst_note":"Reviewed"}
        result=generate_alert_report(alert,[{"timestamp":"2026-01-01T10:00:00","action":"download",
            "resource":"report.csv","after_hours":False,"sensitive":True}],analyst="analyst1")
        self.assertTrue(result.startswith(b"%PDF"))
        self.assertGreater(len(result),500)

if __name__ == "__main__": unittest.main()
