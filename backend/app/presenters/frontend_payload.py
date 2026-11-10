from app.data.repository import LocalRepository
import re


def _restaurant_candidates(repository: LocalRepository) -> list[dict]:
    return [{
        "id": item["id"],
        "name": item["name"],
        "address": item["address"],
        "area": item["area"],
        "category": item["category"],
        "elderly_dining_tip": item["elderly_dining_tip"],
        "source_level": item["source_level"],
        "source_url": item["source_url"],
        "realtime_confirmation_required": item["realtime_confirmation_required"],
        "note": item["note"],
    } for item in repository.restaurants]


def _pick_meal(day: dict, restaurants: list[dict]) -> dict | None:
    theme = day["theme"]
    for restaurant in restaurants:
        if restaurant["area"] in theme:
            return restaurant
    return None


def _day_copy(day: dict) -> str:
    if day["day"] == 1:
        return "第一天不用着急，把脚步放慢，先和都江堰的水声打个招呼。"
    if day["day"] == 2:
        return "今天以轻松陪伴为主，看到喜欢的风景就多停一会儿。"
    return "旅程的最后一天，留一点从容给山风，也留一点体力给返程。"


def _timeline_item(period: str, raw_text: str, kind: str, tone: str, icon: str) -> dict:
    """Split a backend time string so the client can render screenshot-like cards."""
    match = re.match(r"^(\d{2}:\d{2}\s*-\s*\d{2}:\d{2})\s*(.*)$", raw_text)
    return {
        "period": period,
        "time_range": match.group(1) if match else "时间待确认",
        "title": match.group(2) if match else raw_text,
        "kind": kind,
        "tone": tone,
        "icon": icon,
        "render_style": "timeline_card",
    }


def build_frontend_payload(plan: dict, repository: LocalRepository | None = None) -> dict:
    """A stable, front-end-ready contract. No UI should parse LLM prose."""
    repository = repository or LocalRepository()
    restaurants = _restaurant_candidates(repository)
    profile = plan["profile"]
    day_cards = []
    for day in plan["itinerary"]:
        timeline = [
            _timeline_item("上午", day["morning"], "scenic", "gentle", "🌿"),
            _timeline_item("中午", day["noon"], "rest", "warm", "🍲"),
            _timeline_item("下午", day["afternoon"], "slow_walk", "gentle", "🚶"),
            _timeline_item("晚间", day["evening"], "hotel", "calm", "🏨"),
        ]
        wellness = day.get("wellness_program")
        guide = day.get("student_guide_service")
        day_cards.append({
            "day": day["day"],
            "title": day["theme"],
            "emotion_copy": _day_copy(day),
            "render_style": "daily_timeline",
            "timeline": timeline,
            "meal_candidate": _pick_meal(day, restaurants),
            "wellness": None if not wellness else {
                "status": "scheduled_candidate",
                "time": wellness["scheduled_time_slot"],
                "name": wellness["name"],
                "warm_copy": "今天走得刚刚好，晚间项目可按身体状态灵活取消。",
                "confirmation": "请确认名额、费用、服务资质和老人身体适用性。",
            },
            "student_guide": None if not guide else {
                "status": guide["status"],
                "warm_copy": "有人陪着，问路、休息和沟通都会更从容。",
                "scope": guide["suggested_scope"],
                "notice": guide["notice"],
            },
            "safety_copy": "如果今天感觉疲劳、头晕或膝盖不适，跳过后续活动也完全没关系。",
            "confirmations": day["confirmations"],
        })

    wellness_state = plan["wellness_mode"]
    wellness_summary = {
        "mode": wellness_state,
        "headline": "酒店康养服务，按您的心意来安排。",
        "selected_categories": plan["selected_wellness_categories"],
        "candidate_programs": [{"name": x["name"], "category": x["category"], "time_slots": x["time_slots"], "safety_note": x["safety_note"]} for x in plan["wellness_program_recommendations"]],
        "notice": "默认仅展示候选服务；用户确认后才写入行程。所有项目均需由酒店再次确认。",
    }
    return {
        "version": "travel_frontend_payload_v1",
        "status": "demo_pending_confirmation",
        "summary": {
            "headline": f"{profile['name']}，今天我们慢一点，把风景留给舒服的节奏。",
            "subheadline": f"{profile['travelers']}位同行长者 · {profile['days']}天 · {profile['mobility']}",
            "care_copy": "我们已为您预留午休、返程缓冲和随时调整的空间。",
            "render_style": "warm_hero",
        },
        "days": day_cards,
        "restaurant_candidates": restaurants,
        "restaurant_section": {
            "headline": "今天吃得舒服，也是一段好旅程。",
            "subheadline": "餐饮候选均带有地址和适老点餐提醒，请在出发前确认。",
            "render_style": "restaurant_card_list",
        },
        "wellness": wellness_summary,
        "student_guide": {
            "requested": profile["needs_companion"],
            "headline": "有人陪着，旅程更从容。",
            "candidates": plan["platform_student_guide_recommendations"],
            "notice": "学生导游仅提供陪同、沟通、讲解和协助求助；确认排班、集合点、家属授权与协议后再服务。",
        },
        "global_safety_copy": "不追赶打卡；长者当天感觉不舒服时，休息永远优先于行程。",
        "render_hints": {
            "page_layout": "senior_travel_timeline",
            "palette": "warm_cream",
            "show_day_tabs": True,
            "show_confirmations_as": "bottom_sheet_or_notice_card",
            "do_not_render_raw_llm_answer": True,
        },
        "manual_confirmations": plan["manual_confirmation"],
    }
