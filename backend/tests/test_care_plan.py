import unittest

from app.domain.models import ElderProfile
from app.services.care_plan_service import CarePlanService


class CarePlanTest(unittest.TestCase):
    def setUp(self):
        self.profile = ElderProfile(
            "王阿姨", "70-79岁", 3, 1800, "需要减少步行", ["文化讲解"], needs_companion=True
        )
        self.plan = CarePlanService().build_plan(self.profile)

    def test_itinerary_has_rest_schedule(self):
        self.assertEqual(3, len(self.plan["itinerary"]))
        self.assertIn("午休", self.plan["itinerary"][0]["noon"])

    def test_only_trained_companions_are_recommended(self):
        names = [item["name"] for item in self.plan["companion_recommendations"]]
        self.assertNotIn("陈同学", names)

    def test_companion_is_optional(self):
        profile = ElderProfile("李叔叔", "70-79岁", 2, 1200, "需要减少步行", needs_companion=False)
        self.assertEqual([], CarePlanService().build_plan(profile)["companion_recommendations"])

    def test_wellness_can_be_disabled(self):
        profile = ElderProfile("李叔叔", "70-79岁", 2, 1200, "需要减少步行", needs_wellness=False)
        plan = CarePlanService().build_plan(profile)
        self.assertEqual([], plan["wellness_program_recommendations"])
        self.assertIsNone(plan["selected_wellness_hotel"])

    def test_manual_confirmation_is_present(self):
        self.assertGreater(len(self.plan["manual_confirmation"]), 0)


if __name__ == "__main__":
    unittest.main()
