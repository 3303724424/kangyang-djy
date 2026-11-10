from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.knowledge.retriever import LocalKnowledgeRetriever


def test_water_release_festival_retrieval():
    result = LocalKnowledgeRetriever().search("都江堰放水节是什么")
    assert result and result[0]["id"] == "culture-water-release-festival"


def test_service_boundary_retrieval():
    assert "不能自行提供理疗" in LocalKnowledgeRetriever().context("学生可以给老人理疗吗")
