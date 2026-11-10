from app.domain.models import CompanionMatch, ElderProfile


class HotelMatcher:
    def recommend(self, profile: ElderProfile, hotels: list[dict]) -> list[dict]:
        ranked = []
        for hotel in hotels:
            score = 0
            tags = hotel.get("tags", [])
            score += 35 if hotel.get("accessible") else 0
            score += 25 if "康养" in tags else 0
            price = hotel.get("price_per_night")
            if isinstance(price, (int, float)) and price <= profile.budget / max(profile.days, 1):
                score += 15
            rating = hotel.get("rating")
            if isinstance(rating, (int, float)):
                score += min(rating * 5, 25)
            ranked.append({**hotel, "match_score": round(score)})
        return sorted(ranked, key=lambda item: item["match_score"], reverse=True)


class CompanionMatcher:
    """Recommend only eligible platform-exclusive student-guide candidates."""

    def match(self, profile: ElderProfile, companions: list[dict]) -> list[CompanionMatch]:
        matches = []
        for person in companions:
            if not person.get("trained"):
                continue
            if not person.get("platform_exclusive"):
                continue
            if person.get("availability_status") != "demo_available":
                continue
            score, reasons = 45, ["平台专属学生导游候选（演示，待服务确认）", "已完成适老沟通与基础应急培训"]
            tags = set(person.get("tags", []))
            for preference in profile.preferences:
                if preference in tags:
                    score += 15
                    reasons.append(f"擅长{preference}")
            if profile.mobility != "可轻松步行" and "无障碍协助" in tags:
                score += 20
                reasons.append("具备无障碍协助服务标签")
            matches.append(CompanionMatch(
                person["name"],
                min(score, 100),
                reasons,
                person.get("service_scope", []),
                person.get("service_boundary", ""),
                person.get("data_status", ""),
            ))
        return sorted(matches, key=lambda item: item.score, reverse=True)
