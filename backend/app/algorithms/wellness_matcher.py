from app.domain.models import ElderProfile


class WellnessProgramMatcher:
    """Retrieve eligible hotel wellness options and optionally filter user selections."""

    @staticmethod
    def matches_selection(program: dict, selections: list[str]) -> bool:
        if not selections:
            return False
        searchable = " ".join([
            program.get("name", ""),
            program.get("category", ""),
            *program.get("tags", []),
        ])
        return any(selection in searchable for selection in selections)

    def recommend(
        self,
        profile: ElderProfile,
        programs: list[dict],
        hotel_id: str | None,
        selected_only: bool = False,
    ) -> list[dict]:
        ranked = []
        for program in programs:
            if hotel_id and program.get("hotel_id") != hotel_id:
                continue
            if profile.mobility not in program.get("suitable_mobility", []):
                continue
            if selected_only and not self.matches_selection(program, profile.selected_wellness_categories):
                continue
            tags = set(program.get("tags", []))
            score = 50
            score += 25 if "低强度" in tags else 0
            score += 10 if "休息" in tags or "室内" in tags else 0
            score += 5 if program.get("requires_manual_confirmation") else 0
            ranked.append({**program, "match_score": score})
        return sorted(ranked, key=lambda item: item["match_score"], reverse=True)
