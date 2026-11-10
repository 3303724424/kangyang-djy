import unittest

from app.domain.models import ElderProfile
from app.services.care_plan_service import CarePlanService


class GuidePushTest(unittest.TestCase):
    def test_no_guide_is_pushed_without_request(self):
        profile = ElderProfile("测试", "70-79岁", 2, 1500, "需要减少步行", needs_companion=False)
        plan = CarePlanService().build_plan(profile)
        self.assertEqual([], plan["platform_student_guide_recommendations"])
        self.assertNotIn("student_guide_service", plan["itinerary"][0])

    def test_only_platform_exclusive_trained_guides_are_pushed(self):
        profile = ElderProfile("测试", "70-79岁", 2, 1500, "需要减少步行", needs_companion=True)
        plan = CarePlanService().build_plan(profile)
        names = [guide["name"] for guide in plan["platform_student_guide_recommendations"]]
        self.assertTrue(names)
        self.assertNotIn("陈同学（非可推送候选）", names)
        self.assertTrue(all(
            any("平台专属学生导游候选" in reason for reason in guide["reasons"])
            for guide in plan["platform_student_guide_recommendations"]
        ))
        self.assertTrue(all(day["student_guide_service"]["requested"] for day in plan["itinerary"]))


if __name__ == "__main__":
    unittest.main()
