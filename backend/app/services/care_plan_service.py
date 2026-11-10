from dataclasses import asdict

from app.algorithms.matcher import CompanionMatcher, HotelMatcher
from app.algorithms.planner import SeniorItineraryPlanner
from app.algorithms.wellness_matcher import WellnessProgramMatcher
from app.data.repository import LocalRepository
from app.domain.models import ElderProfile


class CarePlanService:
    def __init__(self, repository: LocalRepository | None = None):
        self.repository = repository or LocalRepository()
        self.planner = SeniorItineraryPlanner()
        self.hotel_matcher = HotelMatcher()
        self.companion_matcher = CompanionMatcher()
        self.wellness_matcher = WellnessProgramMatcher()

    @staticmethod
    def evening_slot(program: dict) -> str | None:
        for slot in program.get("time_slots", []):
            start = slot.split("-")[0]
            try:
                hour, minute = (int(value) for value in start.split(":"))
            except ValueError:
                continue
            if (hour, minute) >= (17, 0):
                return slot
        return None

    def build_plan(self, profile: ElderProfile) -> dict:
        itinerary = self.planner.create(profile, self.repository.attractions)
        hotels = self.hotel_matcher.recommend(profile, self.repository.hotels)[:3]
        selected_hotel = hotels[0] if hotels else None
        wellness_mode = "not_needed" if not profile.needs_wellness else profile.wellness_mode
        wellness_candidates = []
        scheduled_source = []
        if wellness_mode != "not_needed" and selected_hotel:
            wellness_candidates = self.wellness_matcher.recommend(profile, self.repository.wellness_programs, selected_hotel["id"])
        if wellness_mode == "selected" and selected_hotel:
            scheduled_source = self.wellness_matcher.recommend(
                profile, self.repository.wellness_programs, selected_hotel["id"], selected_only=True
            )

        guide_candidates = []
        if profile.needs_companion:
            guide_candidates = self.companion_matcher.match(profile, self.repository.companions)[:3]

        itinerary_data = [asdict(day) for day in itinerary]
        scheduled_wellness = []
        for index, day in enumerate(itinerary_data):
            if profile.needs_companion:
                day["student_guide_service"] = {
                    "requested": True,
                    "status": "demo_pending_manual_confirmation",
                    "suggested_scope": ["景区陪同", "文化讲解", "沟通协助", "基础应急求助协助"],
                    "notice": "仅在用户确认服务并完成排班后安排；不提供医疗、理疗、按摩、诊断或给药服务。",
                }
            if not scheduled_source:
                continue
            program = scheduled_source[index % len(scheduled_source)]
            slot = self.evening_slot(program)
            if slot is None:
                day["confirmations"].append(f"{program['name']}没有可衔接的晚间时段，本日不强行安排。")
                continue
            scheduled = {**program, "scheduled_time_slot": slot}
            scheduled_wellness.append(scheduled)
            day["wellness_program"] = scheduled
            day["evening"] = f"16:00 - 17:00 返回住处休息；{slot} {program['name']}（{program['duration_minutes']}分钟，演示项目，需确认）"
            day["confirmations"].append("康养项目为演示排程，须由酒店确认开放时间、资质、名额及老人适用性。")

        confirmations = [
            "当前合作酒店、康养项目及学生导游均为可替换的演示数据，不代表真实合作、实时房态或可预订服务。",
            "酒店房态、套餐价格、服务资质、开放时段与适老设施需由运营人员或酒店确认。",
            "本系统不提供医疗诊断、护理或紧急救援决策。",
        ]
        if profile.needs_companion:
            confirmations.insert(2, "学生导游推送后仍需确认排班、服务时段、集合点、本人/家属授权与服务协议。")

        guides = [asdict(person) for person in guide_candidates]
        return {
            "profile": asdict(profile),
            "itinerary": itinerary_data,
            "hotel_recommendations": hotels,
            "wellness_candidate_hotel": selected_hotel if wellness_mode != "not_needed" else None,
            "selected_wellness_hotel": selected_hotel if wellness_mode == "selected" and scheduled_wellness else None,
            "wellness_mode": wellness_mode,
            "wellness_program_recommendations": wellness_candidates,
            "selected_wellness_categories": profile.selected_wellness_categories,
            "scheduled_wellness_programs": scheduled_wellness,
            "platform_student_guide_recommendations": guides,
            "companion_recommendations": guides,
            "manual_confirmation": confirmations,
        }
