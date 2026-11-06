import unittest
from modules.demo_scenario import run_demo_scenario


class DemoScenarioTests(unittest.TestCase):
    def test_demo_is_synthetic_and_produces_one_explainable_alert(self):
        result = run_demo_scenario()
        self.assertEqual(len(result["events"]), 4)
        self.assertEqual(len(result["results"]), 1)
        alert = result["results"][0]["alert"]
        self.assertEqual(alert["event_count"], 4)
        self.assertEqual(alert["risk_level"], "High")
        self.assertTrue(alert["reasons"])
        self.assertEqual(len(result["steps"]), 5)

    def test_demo_is_repeatable(self):
        first = run_demo_scenario()["results"][0]["alert"]
        second = run_demo_scenario()["results"][0]["alert"]
        self.assertEqual(first["risk_score"], second["risk_score"])
        self.assertEqual(first["risk_level"], second["risk_level"])


if __name__ == "__main__":
    unittest.main()
