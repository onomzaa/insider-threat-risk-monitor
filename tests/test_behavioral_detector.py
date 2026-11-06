import unittest
from modules.behavioral_detector import detect_behavioral_anomalies


class BehavioralDetectorTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            {"employee_id":"a","role":"finance","action":"view","resource":"report","after_hours":False},
            {"employee_id":"a","role":"finance","action":"view","resource":"report","after_hours":False},
            {"employee_id":"a","role":"finance","action":"export","resource":"payroll","after_hours":True},
            {"employee_id":"a","role":"finance","action":"export","resource":"payroll","after_hours":True},
            {"employee_id":"b","role":"finance","action":"view","resource":"report","after_hours":False},
            {"employee_id":"c","role":"finance","action":"view","resource":"report","after_hours":False},
        ]

    def test_detects_role_unusual_patterns(self):
        results = detect_behavioral_anomalies(self.records, min_peer_count=2)
        kinds = {item["kind"] for item in results if item["employee_id"] == "a"}
        self.assertIn("Role-unusual action", kinds)
        self.assertIn("Role-unusual resource", kinds)
        self.assertIn("After-hours concentration", kinds)

    def test_insufficient_peers_skips_comparison(self):
        results = detect_behavioral_anomalies(self.records, min_peer_count=3)
        self.assertEqual(results, [])

    def test_invalid_peer_threshold(self):
        with self.assertRaises(ValueError):
            detect_behavioral_anomalies(self.records, min_peer_count=0)


if __name__ == "__main__":
    unittest.main()
