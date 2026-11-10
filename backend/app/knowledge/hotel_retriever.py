import json
from pathlib import Path


class PlatformHotelRetriever:
    """Retrieve platform-collected candidates without presenting them as verified partners."""

    def __init__(self, path: Path | None = None):
        data_dir = Path(__file__).resolve().parents[2] / "data"
        paths = [path] if path else [data_dir / "platform_hotel_candidates.json", data_dir / "meituan_hotel_candidates.json"]
        self.items = []
        for source_path in paths:
            if source_path and source_path.exists():
                self.items.extend(json.loads(source_path.read_text(encoding="utf-8")))

    def search(self, query: str, limit: int = 3) -> list[dict]:
        terms = set(query)
        ranked = []
        for item in self.items:
            location = item.get("address") or item.get("location") or item.get("displayed_location_relation", "")
            text = "".join([item["name"], location, "".join(item["tags"])])
            score = len(terms & set(text))
            if score:
                ranked.append((score, item))
        ranked.sort(key=lambda x: x[0], reverse=True)
        return [{**item, "match_score": score} for score, item in ranked[:limit]]

    def context(self, query: str) -> str:
        matches = self.search(query)
        if not matches:
            return "未检索到平台候选酒店。"
        return "\n".join(
            f"- {x['name']}：平台候选资料，标签为{'、'.join(x['tags'])}；实时房价、房态、服务与适老设施必须向酒店或预订平台再次确认。来源：{x.get('source_url') or '用户提供的美团截图证据'}"
            for x in matches
        )
