import unittest

from app.domain.models import ElderProfile
from app.services.care_plan_service import CarePlanService


class CarePlanTest(unittest.TestCase):
    def setUp(self):
        self.profile = ElderProfile("王阿姨", "70-79岁", 3, 1800, "需要减少步行", ["文化讲解"])
        self.plan = CarePlanService().build_plan(self.profile)

    def test_itinerary_has_rest_schedule(self):
        self.assertEqual(3, len(self.plan["itinerary"]))
        self.assertIn("午休", self.plan["itinerary"][0]["noon"])

    def test_only_trained_companions_are_recommended(self):
        names = [item["name"] for item in self.plan["companion_recommendations"]]
        self.assertNotIn("陈同学", names)

    def test_manual_confirmation_is_present(self):
        self.assertGreater(len(self.plan["manual_confirmation"]), 0)


if __name__ == "__main__":
    unittest.main()
