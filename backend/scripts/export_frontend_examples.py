"""Export versioned request/response examples and the OpenAPI contract for frontend work.

This script deliberately does not load the Qwen model; it uses the deterministic
planner to create a stable mock response that matches the live API shape.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# When this file is executed as ``python scripts\\export_frontend_examples.py``,
# Python otherwise only puts the scripts directory on sys.path.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.api import create_app
from app.domain.models import ElderProfile
from app.presenters.frontend_payload import build_frontend_payload
from app.services.care_plan_service import CarePlanService


EXAMPLES = ROOT / "docs" / "examples"


def write_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    request = {
        "question": "两位七十多岁长者去都江堰三天，想慢游、泡温泉，需要学生导游陪同。",
        "name": "张阿姨",
        "age_group": "70-79岁",
        "days": 3,
        "travelers": 2,
        "budget": 2600,
        "mobility": "需要减少步行",
        "preferences": ["文化讲解", "轻松慢游", "温泉"],
        "travel_date": "2026-11-15",
        "needs_student_guide": True,
        "wellness_mode": "selected",
        "wellness_categories": ["温泉", "营养餐"],
    }
    profile = ElderProfile(
        name=request["name"], age_group=request["age_group"], days=request["days"],
        budget=request["budget"], mobility=request["mobility"], preferences=request["preferences"],
        travel_date=request["travel_date"], travelers=request["travelers"],
        needs_companion=request["needs_student_guide"], needs_wellness=True,
        wellness_mode=request["wellness_mode"], selected_wellness_categories=request["wellness_categories"],
    )
    plan = CarePlanService().build_plan(profile)
    response = {
        "request_id": "example-request-id",
        "status": "success",
        "generated_at": "2026-11-08T00:00:00+00:00",
        "frontend_payload": build_frontend_payload(plan),
    }
    write_json(EXAMPLES / "travel-plan-request.json", request)
    write_json(EXAMPLES / "travel-plan-response.json", response)
    write_json(ROOT / "docs" / "openapi.json", create_app().openapi())
    print(f"已生成示例：{EXAMPLES}")


if __name__ == "__main__":
    main()
