import json

from app.domain.models import ElderProfile
from app.knowledge.retriever import LocalKnowledgeRetriever
from app.knowledge.hotel_retriever import PlatformHotelRetriever
from app.llm.local_qwen import LocalQwen
from app.presenters.frontend_payload import build_frontend_payload
from app.services.care_plan_service import CarePlanService


def render_structured_itinerary(plan: dict) -> str:
    """Render the deterministic plan first; the LLM must not rewrite route decisions."""
    profile = plan["profile"]
    lines = [
        "## 都江堰银龄旅居建议",
        f"对象：{profile['age_group']}｜{profile['travelers']}人｜{profile['days']}天｜行动能力：{profile['mobility']}",
        "安排原则：每天一个主游览区域；午间固定休息；16:00 后不再增加景点；身体不适可直接取消当日后续安排。",
        "",
        "## 每日安排",
    ]
    for day in plan["itinerary"]:
        lines.extend([
            f"### 第 {day['day']} 天：{day['theme']}",
            f"- 上午：{day['morning']}",
            f"- 中午：{day['noon']}",
            f"- 下午：{day['afternoon']}",
            f"- 晚间：{day['evening']}",
        ])
        if day.get("wellness_program"):
            program = day["wellness_program"]
            lines.append(
                f"- 住店康养候选：{program['scheduled_time_slot']} {program['name']}（仅演示排程；需确认名额、费用、资质及是否适合老人）"
            )
        if day.get("student_guide_service"):
            lines.append("- 平台专属学生导游：已提交陪伴需求；确认排班后提供景区陪同、讲解、沟通与求助协助。")

    lines.extend([
        "",
        "## 住宿与确认",
        "- 住宿仅从平台候选或演示合作酒店中筛选；不承诺房态、价格、无障碍设施或康养项目可用性。",
        "- 出发前依次确认：景区开放与天气、酒店房态与适老设施、康养项目适用性与预约规则。",
    ])
    if profile["wellness_mode"] == "recommend_only":
        candidates = plan["wellness_program_recommendations"][:3]
        if candidates:
            lines.append("- 可选酒店康养服务（尚未排入行程）：" + "、".join(item["name"] for item in candidates) + "。用户确认后再安排具体时段。")
    elif profile["wellness_mode"] == "selected" and not plan["scheduled_wellness_programs"]:
        lines.append("- 已收到康养意向，但没有匹配到可安排的晚间项目；请调整选择或与酒店确认其他时段。")
    if profile["needs_companion"]:
        lines.append("- 学生导游仅提供陪同、沟通、讲解和协助求助；需确认排班、集合点、家属授权与服务协议，不提供医疗、理疗、按摩、诊断或给药服务。")
    return "\n".join(lines)


class LocalTravelAgent:
    def __init__(self, llm: LocalQwen):
        self.llm = llm
        self.retriever = LocalKnowledgeRetriever()
        self.hotel_retriever = PlatformHotelRetriever()
        self.planner = CarePlanService()

    def answer(self, question: str, profile: ElderProfile) -> dict:
        facts = self.retriever.search(question)
        hotel_candidates = self.hotel_retriever.search(question)
        plan = self.planner.build_plan(profile)
        structured_itinerary = render_structured_itinerary(plan)
        frontend_payload = build_frontend_payload(plan)
        system = """你是都江堰银龄康养旅居助手。你不能改写、增加或调换用户已获得的结构化行程。
只输出“智能提醒”，最多 3 个简洁要点，不重复每日安排。必须提示：实时房态/价格/开放状态需要核验；医疗或理疗项目不得自动安排；如遇预警或身体不适应暂停活动并求助。"""
        user = (
            f"用户问题：{question}\n\n已审核知识：\n{self.retriever.context(question)}\n\n"
            f"平台候选酒店：\n{self.hotel_retriever.context(question)}\n\n"
            f"结构化行程（不可改写）：\n{structured_itinerary}"
        )
        ai_reminders = self.llm.generate(system, user, max_new_tokens=160)
        return {
            "answer": f"{structured_itinerary}\n\n## 智能提醒\n{ai_reminders}",
            "structured_itinerary": structured_itinerary,
            "ai_reminders": ai_reminders,
            "knowledge": facts,
            "platform_hotel_candidates": hotel_candidates,
            "plan": plan,
            "frontend_payload": frontend_payload,
        }
