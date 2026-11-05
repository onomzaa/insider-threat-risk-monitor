import unittest
from modules.risk_engine import score_incident

class RiskEngineTests(unittest.TestCase):
    def test_score_is_bounded(self):
        events = [{"action": "export"} for _ in range(10)]
        result = score_incident(events, [{"outside_role_scope": True,
                                         "after_hours": True, "sensitive": True}])
        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["risk_score"], 100)

    def test_low_activity_is_low(self):
        result = score_incident([{"action": "view"}], [])
        self.assertEqual(result["risk_level"], "Low")

if __name__ == "__main__":
    unittest.main()
