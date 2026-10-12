from dataclasses import asdict

from app.algorithms.matcher import CompanionMatcher, HotelMatcher
from app.algorithms.planner import SeniorItineraryPlanner
from app.data.repository import LocalRepository
from app.domain.models import ElderProfile


class CarePlanService:
    def __init__(self, repository: LocalRepository | None = None):
        self.repository = repository or LocalRepository()
        self.planner = SeniorItineraryPlanner()
        self.hotel_matcher = HotelMatcher()
        self.companion_matcher = CompanionMatcher()

    def build_plan(self, profile: ElderProfile) -> dict:
        itinerary = self.planner.create(profile, self.repository.attractions)
        hotels = self.hotel_matcher.recommend(profile, self.repository.hotels)[:3]
        companions = self.companion_matcher.match(profile, self.repository.companions)[:3]
        return {
            "profile": asdict(profile),
            "itinerary": [asdict(day) for day in itinerary],
            "hotel_recommendations": hotels,
            "companion_recommendations": [asdict(person) for person in companions],
            "manual_confirmation": [
                "酒店房态、套餐价格与服务资质需由运营人员确认。",
                "学生陪伴员服务时间、集合点与服务边界需由双方确认。",
                "本系统不提供医疗诊断、护理或紧急救援决策。",
            ],
        }
