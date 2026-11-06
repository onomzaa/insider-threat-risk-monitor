"""End-to-end checks for the synthetic detection pipeline."""
import unittest

from modules.event_correlator import correlate_events
from modules.context_analyzer import analyze_context
from modules.risk_engine import score_incident
from modules.alert_manager import build_alert, filter_alerts, set_disposition


class PipelineIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Fictional employee activity; test data is not collected from people.
        self.events = [
            {"employee_id": "demo-user", "timestamp": "2026-01-10T21:00:00",
             "action": "permission_change", "resource": "finance"},
            {"employee_id": "demo-user", "timestamp": "2026-01-10T21:10:00",
             "action": "download", "resource": "finance"},
            {"employee_id": "demo-user", "timestamp": "2026-01-10T21:15:00",
             "action": "share", "resource": "finance"},
        ]
        self.profiles = {"demo-user": {"role": "staff",
                                      "allowed_resources": ["general"]}}

    def test_events_flow_to_explainable_alert_and_review(self):
        incidents = correlate_events(self.events, window_minutes=30)
        self.assertEqual(len(incidents), 1)
        incident = incidents[0]
        contexts = [analyze_context(event, self.profiles)
                    for event in incident["events"]]
        risk = score_incident(incident["events"], contexts)
        alert = build_alert(incident, risk, contexts)

        self.assertEqual(alert["employee_id"], "demo-user")
        self.assertEqual(alert["event_count"], 3)
        self.assertGreaterEqual(alert["risk_score"], 70)
        self.assertEqual(alert["risk_level"], "High")
        self.assertTrue(alert["reasons"])
        self.assertTrue(any(item["outside_role_scope"] for item in contexts))

        queue = filter_alerts([alert], risk_level="High", status="Open",
                              query=alert["alert_id"])
        self.assertEqual(len(queue), 1)
        reviewed = set_disposition(queue[0], "Under Review",
                                   "Synthetic integration test review")
        self.assertEqual(reviewed["status"], "Under Review")
        self.assertEqual(reviewed["analyst_note"],
                         "Synthetic integration test review")

    def test_separate_employees_remain_separate(self):
        events = self.events + [
            {"employee_id": "demo-other", "timestamp": "2026-01-10T21:12:00",
             "action": "login_failed", "resource": "general"}
        ]
        incidents = correlate_events(events, window_minutes=30)
        self.assertEqual({item["employee_id"] for item in incidents},
                         {"demo-user", "demo-other"})


if __name__ == "__main__":
    unittest.main()
