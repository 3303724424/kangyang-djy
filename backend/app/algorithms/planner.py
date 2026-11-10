from app.domain.models import ElderProfile, ItineraryDay


class SeniorItineraryPlanner:
    """Create a conservative, deterministic daily skeleton for older travellers."""

    def score_attraction(self, profile: ElderProfile, attraction: dict) -> int:
        tags = set(attraction.get("tags", []))
        preference_score = min(40, sum(20 for tag in profile.preferences if tag in tags))
        mobility_score = 25 if profile.mobility in attraction.get("mobility_support", []) else -30
        rest_score = 15 if attraction.get("rest_points") else -10
        daily_budget = profile.budget / max(profile.days, 1)
        budget_score = 10 if attraction.get("ticket", 0) <= daily_budget else 3
        return preference_score + mobility_score + rest_score + budget_score + attraction.get("base_score", 0)

    def select_daily_attractions(self, profile: ElderProfile, attractions: list[dict]) -> list[dict]:
        # Only choose attractions that explicitly support the traveller's mobility level.
        accessible = [item for item in attractions if profile.mobility in item.get("mobility_support", [])]
        candidates = accessible or attractions
        candidates = sorted(candidates, key=lambda item: self.score_attraction(profile, item), reverse=True)

        # One main area per day. Do not mix scenic areas simply to fill a day.
        selected, used_zones = [], set()
        for attraction in candidates:
            zone = attraction.get("zone", attraction["name"])
            if zone in used_zones:
                continue
            selected.append(attraction)
            used_zones.add(zone)
            if len(selected) >= profile.days:
                break
        return selected or candidates[:1]

    def create(self, profile: ElderProfile, attractions: list[dict]) -> list[ItineraryDay]:
        selected = self.select_daily_attractions(profile, attractions)
        days = []
        for index in range(profile.days):
            poi = selected[index] if index < len(selected) else selected[-1]
            repeat_note = "以休息与自由活动为主，不新增跨区域景点" if index >= len(selected) else "当日只安排一个主游览区域"
            days.append(ItineraryDay(
                day=index + 1,
                theme=f"{poi['zone']}｜{poi['name']}",
                morning=f"10:00 - 11:30 {poi['name']}慢游与休息点停留（{repeat_note}）",
                noon="12:00 - 14:30 午餐、午休与交通缓冲；不安排赶路或连续打卡",
                afternoon=f"15:00 - 16:00 {poi['low_intensity_activity']}；16:00 后返回住处休息",
                evening="17:30 - 19:00 酒店晚餐、静养与次日确认，不再安排远距离外出",
                confirmations=[
                    "出发前向景区核验当天开放状态、天气和无障碍/休息设施",
                    "如老人出现疲劳、疼痛或眩晕，当日取消后续活动并优先休息或求助",
                ],
            ))
        return days
