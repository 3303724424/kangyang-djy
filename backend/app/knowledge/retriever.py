import json
import re
from pathlib import Path


class LocalKnowledgeRetriever:
    """Dependency-free retrieval over reviewed local facts only."""

    def __init__(self, path: Path | None = None):
        self.path = path or Path(__file__).resolve().parents[2] / "data" / "knowledge_entries.json"
        self.entries = json.loads(self.path.read_text(encoding="utf-8"))

    @staticmethod
    def _terms(text: str) -> set[str]:
        cleaned = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", " ", text.lower())
        words = {word for word in cleaned.split() if len(word) > 1}
        words.update(cleaned[index:index + 2] for index in range(len(cleaned) - 1) if " " not in cleaned[index:index + 2])
        return words

    def search(self, query: str, limit: int = 3) -> list[dict]:
        terms = self._terms(query)
        scored = []
        for entry in self.entries:
            if entry["review_status"] != "verified":
                continue
            haystack = " ".join([entry["title"], entry["content"], " ".join(entry["tags"])])
            score = len(terms & self._terms(haystack))
            if score:
                scored.append((score, entry))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [{**entry, "match_score": score} for score, entry in scored[:limit]]

    def context(self, query: str, limit: int = 3) -> str:
        results = self.search(query, limit)
        if not results:
            return "未检索到可直接引用的已审核本地事实；请提示用户以官方最新信息为准。"
        return "\n".join(f"- {x['content']}（来源：{x['source_url']}）" for x in results)
