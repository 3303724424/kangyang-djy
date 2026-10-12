import json
from app.domain.models import ElderProfile
from app.services.care_plan_service import CarePlanService


if __name__ == "__main__":
    profile = ElderProfile(
        name="王阿姨",
        age_group="70-79岁",
        days=3,
        budget=1800,
        mobility="需要减少步行",
        preferences=["文化讲解", "温泉疗愈"],
    )
    plan = CarePlanService().build_plan(profile)
    print(json.dumps(plan, ensure_ascii=False, indent=2))
