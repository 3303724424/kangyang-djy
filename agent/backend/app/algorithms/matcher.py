from app.domain.models import CompanionMatch, ElderProfile


class HotelMatcher:
    def recommend(self, profile: ElderProfile, hotels: list[dict]) -> list[dict]:
        ranked = []
        for hotel in hotels:
            score = 0
            score += 35 if hotel.get("accessible") else 0
            score += 25 if "康养" in hotel.get("tags", []) else 0
            score += 15 if hotel.get("price_per_night", 9999) <= profile.budget / max(profile.days, 1) else 0
            score += min(hotel.get("rating", 0) * 5, 25)
            ranked.append({**hotel, "match_score": round(score)})
        return sorted(ranked, key=lambda item: item["match_score"], reverse=True)


class CompanionMatcher:
    def match(self, profile: ElderProfile, companions: list[dict]) -> list[CompanionMatch]:
        matches = []
        for person in companions:
            if not person.get("trained"):
                continue
            score, reasons = 45, ["已完成适老沟通与基础应急培训"]
            tags = set(person.get("tags", []))
            for preference in profile.preferences:
                if preference in tags:
                    score += 15
                    reasons.append(f"擅长{preference}")
            if profile.mobility != "可轻松步行" and "无障碍协助" in tags:
                score += 20
                reasons.append("具备无障碍协助服务标签")
            matches.append(CompanionMatch(person["name"], min(score, 100), reasons))
        return sorted(matches, key=lambda item: item.score, reverse=True)
