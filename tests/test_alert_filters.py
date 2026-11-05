import unittest
from modules.alert_manager import filter_alerts

class AlertFilterTests(unittest.TestCase):
    def setUp(self):
        self.alerts = [
            {"alert_id":"AL-01", "employee_id":"emp01", "risk_level":"High", "status":"Open"},
            {"alert_id":"AL-02", "employee_id":"emp02", "risk_level":"Medium", "status":"Resolved"},
            {"alert_id":"AL-03", "employee_id":"emp01", "risk_level":"Low", "status":"False Positive"},
        ]

    def test_risk_filter(self):
        self.assertEqual(["AL-01"], [a["alert_id"] for a in filter_alerts(self.alerts, risk_level="High")])

    def test_status_filter(self):
        self.assertEqual(["AL-02"], [a["alert_id"] for a in filter_alerts(self.alerts, status="Resolved")])

    def test_search_matches_alert_and_employee_case_insensitive(self):
        self.assertEqual(["AL-03"], [a["alert_id"] for a in filter_alerts(self.alerts, query="emp01", risk_level="Low")])
        self.assertEqual(["AL-02"], [a["alert_id"] for a in filter_alerts(self.alerts, query="al-02")])

    def test_combined_filters_and_empty(self):
        self.assertEqual([], filter_alerts(self.alerts, risk_level="High", status="Resolved"))
        self.assertEqual(3, len(filter_alerts(self.alerts)))

if __name__ == "__main__":
    unittest.main()
