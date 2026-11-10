import unittest

from app.domain.models import ElderProfile
from app.presenters.frontend_payload import build_frontend_payload
from app.services.care_plan_service import CarePlanService


class FrontendPayloadTest(unittest.TestCase):
    def test_payload_has_warm_copy_and_timeline(self):
        profile = ElderProfile("张阿姨", "70-79岁", 3, 2600, "需要减少步行", travelers=2)
        payload = build_frontend_payload(CarePlanService().build_plan(profile))
        self.assertEqual("travel_frontend_payload_v1", payload["version"])
        self.assertIn("慢一点", payload["summary"]["headline"])
        self.assertEqual(3, len(payload["days"]))
        self.assertEqual(4, len(payload["days"][0]["timeline"]))
        self.assertEqual("timeline_card", payload["days"][0]["timeline"][0]["render_style"])
        self.assertIn("time_range", payload["days"][0]["timeline"][0])

    def test_payload_exposes_restaurant_address_and_confirmation(self):
        profile = ElderProfile("张阿姨", "70-79岁", 3, 2600, "需要减少步行", travelers=2)
        payload = build_frontend_payload(CarePlanService().build_plan(profile))
        restaurant = payload["restaurant_candidates"][0]
        self.assertTrue(restaurant["address"])
        self.assertTrue(restaurant["realtime_confirmation_required"])

    def test_selected_wellness_is_presented_as_scheduled_candidate(self):
        profile = ElderProfile(
            "张阿姨", "70-79岁", 2, 2600, "需要减少步行", travelers=2,
            wellness_mode="selected", selected_wellness_categories=["温泉", "营养餐"],
        )
        payload = build_frontend_payload(CarePlanService().build_plan(profile))
        self.assertEqual("selected", payload["wellness"]["mode"])
        self.assertTrue(any(day["wellness"] for day in payload["days"]))


if __name__ == "__main__":
    unittest.main()
