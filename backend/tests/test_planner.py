import unittest

from app.algorithms.planner import SeniorItineraryPlanner
from app.data.repository import LocalRepository
from app.domain.models import ElderProfile


class PlannerTest(unittest.TestCase):
    def test_three_day_plan_uses_one_area_per_day(self):
        profile = ElderProfile("测试用户", "70-79岁", 3, 1800, "需要减少步行")
        days = SeniorItineraryPlanner().create(profile, LocalRepository().attractions)
        themes = [day.theme for day in days]
        self.assertEqual(3, len(themes))
        self.assertEqual(3, len(set(themes)))

    def test_wheelchair_profile_excludes_unsupported_attractions(self):
        profile = ElderProfile("测试用户", "70-79岁", 2, 1800, "需轮椅协助")
        days = SeniorItineraryPlanner().create(profile, LocalRepository().attractions)
        self.assertTrue(all("都江堰" in day.theme for day in days))

    def test_plan_has_fixed_rest_structure(self):
        profile = ElderProfile("测试用户", "70-79岁", 1, 1800, "需要减少步行")
        day = SeniorItineraryPlanner().create(profile, LocalRepository().attractions)[0]
        self.assertIn("午休", day.noon)
        self.assertIn("16:00", day.afternoon)


if __name__ == "__main__":
    unittest.main()
