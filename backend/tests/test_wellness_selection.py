import unittest

from app.domain.models import ElderProfile
from app.services.care_plan_service import CarePlanService


class WellnessSelectionTest(unittest.TestCase):
    def test_recommend_only_does_not_insert_wellness_into_itinerary(self):
        profile = ElderProfile("测试", "70-79岁", 2, 1800, "需要减少步行", wellness_mode="recommend_only")
        plan = CarePlanService().build_plan(profile)
        self.assertTrue(plan["wellness_program_recommendations"])
        self.assertEqual([], plan["scheduled_wellness_programs"])
        self.assertTrue(all("wellness_program" not in day for day in plan["itinerary"]))

    def test_selected_category_is_inserted_into_itinerary(self):
        profile = ElderProfile(
            "测试", "70-79岁", 2, 1800, "需要减少步行",
            wellness_mode="selected", selected_wellness_categories=["温泉", "营养餐"],
        )
        plan = CarePlanService().build_plan(profile)
        self.assertTrue(plan["scheduled_wellness_programs"])
        self.assertTrue(all(item["name"] in "温泉放松时段（演示） 清淡营养晚餐建议（演示）" for item in plan["scheduled_wellness_programs"]))

    def test_not_needed_hides_wellness_candidates(self):
        profile = ElderProfile("测试", "70-79岁", 2, 1800, "需要减少步行", wellness_mode="not_needed")
        plan = CarePlanService().build_plan(profile)
        self.assertEqual([], plan["wellness_program_recommendations"])
        self.assertIsNone(plan["wellness_candidate_hotel"])


if __name__ == "__main__":
    unittest.main()
