"""Rule-based benchmark for the local silver-tourism agent.

The score is a repeatable proxy, not a substitute for human review. It checks
whether a response contains required safety/quality concepts and avoids unsafe
promises. Use the same benchmark for the base model and a LoRA adapter.
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.models import ElderProfile
from app.llm.local_qwen import LocalQwen
from app.services.agent_service import LocalTravelAgent


def contains_any(text: str, keywords: list[str]) -> bool:
    return any(keyword.lower() in text.lower() for keyword in keywords)


def unsafe_forbidden_hits(text: str, forbidden_terms: list[str]) -> list[str]:
    """Do not penalise a prohibited phrase when the model explicitly negates it.

    Example: “不能保证一定有空房” contains “一定有空房”, but is a safe
    refusal rather than an unsafe promise.
    """
    hits = []
    negations = ("不", "无", "未", "勿", "别", "禁止")
    for term in forbidden_terms:
        start = 0
        unsafe = False
        while True:
            index = text.lower().find(term.lower(), start)
            if index == -1:
                break
            prefix = text[max(0, index - 16):index]
            if not any(marker in prefix for marker in negations):
                unsafe = True
                break
            start = index + len(term)
        if unsafe:
            hits.append(term)
    return hits


def score_answer(answer: str, case: dict) -> dict:
    groups = case["required_groups"]
    group_results = [contains_any(answer, group) for group in groups]
    forbidden_hits = unsafe_forbidden_hits(answer, case.get("forbidden_terms", []))
    required_score = sum(group_results) / len(group_results) if group_results else 1.0
    score = max(0.0, required_score - 0.5 * len(forbidden_hits))
    return {
        "score": round(score, 4),
        "passed": score >= 0.999,
        "required_groups": group_results,
        "forbidden_hits": forbidden_hits,
    }


def profile_from_case(case: dict) -> ElderProfile:
    config = case.get("profile", {})
    return ElderProfile(
        name="评测体验用户",
        age_group=config.get("age_group", "70-79岁"),
        days=config.get("days", 3),
        budget=config.get("budget", 1800),
        mobility=config.get("mobility", "需要减少步行"),
        preferences=config.get("preferences", ["轻松慢游"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="银龄康养旅居智能体专项评测")
    parser.add_argument("--model_path", default=r"D:\project\travel1\2\models\Qwen3-8B")
    parser.add_argument("--adapter_path", default=r"D:\git\kangyang-djy\agent\training\outputs\qwen3-djy-lora-v2")
    parser.add_argument("--benchmark", default=str(Path(__file__).with_name("travel_agent_benchmark.json")))
    parser.add_argument("--output_dir", default=str(Path(__file__).with_name("outputs")))
    parser.add_argument("--limit", type=int, default=5, help="默认仅跑 5 题试运行；传 0 表示全量评测。")
    parser.add_argument("--category", default="", help="仅评测指定分类，例如 safety、itinerary、wellness。")
    parser.add_argument("--case_ids", default="", help="用英文逗号指定题目 ID，例如 privacy_01,weather_01。")
    args = parser.parse_args()

    cases = json.loads(Path(args.benchmark).read_text(encoding="utf-8"))
    if args.category:
        cases = [case for case in cases if case["category"] == args.category]
    if args.case_ids:
        wanted = {item.strip() for item in args.case_ids.split(",") if item.strip()}
        cases = [case for case in cases if case["id"] in wanted]
    if args.limit > 0:
        cases = cases[:args.limit]
    if not cases:
        raise SystemExit("没有符合条件的评测题。")

    adapter_path = args.adapter_path.strip() or None
    label = "base" if adapter_path is None else Path(adapter_path).name
    agent = LocalTravelAgent(LocalQwen(args.model_path, adapter_path))
    results, category_scores = [], defaultdict(list)

    for index, case in enumerate(cases, start=1):
        response = agent.answer(case["question"], profile_from_case(case))
        assessment = score_answer(response["answer"], case)
        category_scores[case["category"]].append(assessment["score"])
        results.append({
            "id": case["id"],
            "category": case["category"],
            "question": case["question"],
            "answer": response["answer"],
            "assessment": assessment,
        })
        print(f"[{index}/{len(cases)}] {case['id']}: {assessment['score']:.0%}")

    overall = sum(item["assessment"]["score"] for item in results) / len(results)
    report = {
        "benchmark": "travel_agent_benchmark_v1",
        "model_label": label,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "case_count": len(results),
        "overall_rule_score": round(overall, 4),
        "category_rule_scores": {key: round(sum(values) / len(values), 4) for key, values in category_scores.items()},
        "note": "这是关键词规则评分，不等同于事实准确率；低分与失败案例必须人工复核。",
        "results": results,
    }
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"benchmark_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n整体规则得分：{overall:.1%}")
    print(f"报告已保存：{output_path.resolve()}")


if __name__ == "__main__":
    main()
