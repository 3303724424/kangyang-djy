import argparse
import json

from app.domain.models import ElderProfile
from app.llm.local_qwen import LocalQwen
from app.services.agent_service import LocalTravelAgent


def positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("必须是大于等于 1 的整数")
    return number


def non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("不能小于 0")
    return number


def parse_preferences(value: str) -> list[str]:
    return [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="都江堰银龄康养旅居本地智能体 Demo")
    parser.add_argument("--question", required=True, help="用户想咨询的问题")
    parser.add_argument("--model_path", default=r"D:\project\travel1\2\models\Qwen3-8B")
    parser.add_argument("--adapter_path", default=r"D:\git\kangyang-djy\agent\training\outputs\qwen3-djy-lora-v2")
    parser.add_argument("--name", default="体验用户")
    parser.add_argument("--age_group", default="70-79岁")
    parser.add_argument("--days", type=positive_int, default=3)
    parser.add_argument("--travelers", type=positive_int, default=1)
    parser.add_argument("--budget", type=non_negative_int, default=1800)
    parser.add_argument("--mobility", default="需要减少步行", choices=["可轻松步行", "需要减少步行", "需轮椅协助"])
    parser.add_argument("--preferences", default="文化讲解,轻松慢游")
    parser.add_argument("--travel_date", default="")
    parser.add_argument("--needs_companion", "--needs_student_guide", dest="needs_companion", action="store_true", help="需要平台专属学生导游候选建议")
    parser.add_argument("--wellness_mode", choices=["not_needed", "recommend_only", "selected"], default="recommend_only", help="not_needed=不展示；recommend_only=只推荐；selected=用户确认后排程")
    parser.add_argument("--wellness_categories", default="", help="已选择项目，用逗号分隔，例如：温泉,营养餐")
    parser.add_argument("--no_wellness", action="store_true", help="兼容旧参数：等同于 --wellness_mode not_needed")
    parser.add_argument("--output_mode", choices=["frontend", "full"], default="frontend", help="frontend=仅输出前端渲染协议；full=输出全部调试信息")
    args = parser.parse_args()
    wellness_mode = "not_needed" if args.no_wellness else args.wellness_mode
    profile = ElderProfile(
        name=args.name, age_group=args.age_group, days=args.days, budget=args.budget,
        mobility=args.mobility, preferences=parse_preferences(args.preferences), travel_date=args.travel_date,
        travelers=args.travelers, needs_companion=args.needs_companion, needs_wellness=wellness_mode != "not_needed",
        wellness_mode=wellness_mode, selected_wellness_categories=parse_preferences(args.wellness_categories),
    )
    result = LocalTravelAgent(LocalQwen(args.model_path, args.adapter_path)).answer(args.question, profile)
    output = result["frontend_payload"] if args.output_mode == "frontend" else result
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
