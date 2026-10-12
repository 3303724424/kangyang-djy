from app.algorithms.distance import haversine_km
from app.domain.models import ElderProfile, ItineraryDay


class SeniorItineraryPlanner:
    def score_attraction(self, profile: ElderProfile, attraction: dict) -> int:
        tags = set(attraction.get("tags", []))
        preference_score = min(40, sum(20 for tag in profile.preferences if tag in tags))
        mobility_score = 25 if profile.mobility in attraction.get("mobility_support", []) else 8
        rest_score = 15 if attraction.get("rest_points") else 0
        budget_score = 10 if attraction.get("ticket", 0) <= profile.budget / max(profile.days, 1) else 3
        return preference_score + mobility_score + rest_score + budget_score + attraction.get("base_score", 0)

    def create(self, profile: ElderProfile, attractions: list[dict]) -> list[ItineraryDay]:
        candidates = sorted(attractions, key=lambda item: self.score_attraction(profile, item), reverse=True)
        selected, days = [], []
        previous = None
        for attraction in candidates:
            if previous and haversine_km(previous, attraction) > 18 and len(selected) < profile.days:
                continue
            selected.append(attraction)
            previous = attraction
            if len(selected) >= profile.days:
                break
        if not selected:
            selected = candidates[:1]
        for index in range(profile.days):
            poi = selected[index % len(selected)]
            days.append(ItineraryDay(
                day=index + 1,
                theme=poi["name"],
                morning=f"09:30 - 11:30 {poi['name']}轻讲解与休息点停留",
                noon="12:00 - 14:30 营养午餐、午休与交通缓冲",
                afternoon=f"15:00 - 16:30 {poi['low_intensity_activity']}",
                evening="17:30 返回酒店，晚餐与次日确认",
                confirmations=["请在出发前人工确认景区开放状态与天气", "请根据长者当日身体状态调整活动强度"],
            ))
        return days
