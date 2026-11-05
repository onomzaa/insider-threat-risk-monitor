import unittest
from modules.risk_engine import score_incident


class RiskEngineTests(unittest.TestCase):
    def test_score_is_bounded_and_explained(self):
        events = [{"action": "export"} for _ in range(10)]
        result = score_incident(events, [{"outside_role_scope": True,
                                          "after_hours": True, "sensitive": True}])
        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["risk_score"], 100)
        self.assertTrue(result["factors"])
        self.assertTrue(result["explanation"])

    def test_low_activity_is_low(self):
        result = score_incident([{"action": "view"}], [])
        self.assertEqual(result["risk_level"], "Low")
        self.assertEqual(result["risk_score"], 0)

    def test_privilege_data_share_sequence_adds_factor(self):
        events = [{"action": "permission_change"}, {"action": "download"},
                  {"action": "share"}]
        result = score_incident(events)
        self.assertIn(15, [factor["points"] for factor in result["factors"]])
        self.assertTrue(any("sequence" in factor["factor"].lower()
                            for factor in result["factors"]))

    def test_sequence_factor_requires_all_three_action_types(self):
        events = [{"action": "permission_change"}, {"action": "download"}]
        result = score_incident(events)
        self.assertFalse(any("sequence" in factor["factor"].lower()
                             for factor in result["factors"]))

    def test_raw_score_and_cap_are_reported(self):
        events = [{"action": action} for action in
                  ["permission_change", "download", "export", "delete", "share"]]
        result = score_incident(events, [{"outside_role_scope": True,
                                          "after_hours": True, "sensitive": True}])
        self.assertGreaterEqual(result["raw_score"], result["risk_score"])
        self.assertEqual(result["risk_score"], 100)


if __name__ == "__main__":
    unittest.main()
