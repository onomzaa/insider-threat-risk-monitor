import unittest
from modules.mitigation_recommendations import recommend_mitigations


class MitigationRecommendationTests(unittest.TestCase):
    def test_export_and_sensitive_factors_recommend_reviews(self):
        alert={"reasons":["Action: export","Sensitive resource involved"],
               "risk_factors":[{"factor":"Sensitive resource involved"}]}
        items=recommend_mitigations(alert)
        titles=[item["title"] for item in items]
        self.assertIn("Validate data movement",titles)
        self.assertIn("Review sensitive-resource access",titles)
        self.assertEqual(items[0]["priority"],"High")

    def test_after_hours_recommendation_is_non_accusatory(self):
        items=recommend_mitigations({"reasons":["After-hours activity"],"risk_factors":[]})
        item=next(x for x in items if x["title"]=="Confirm after-hours activity")
        self.assertIn("approved schedules",item["steps"])
        self.assertIn("General", [x["priority"] for x in items])

    def test_no_factors_returns_routine_review(self):
        items=recommend_mitigations({})
        self.assertEqual(items[0]["title"],"Routine analyst validation")


if __name__ == "__main__":
    unittest.main()
