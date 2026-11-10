from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ElderProfile:
    name: str
    age_group: str
    days: int
    budget: int
    mobility: str
    preferences: list[str] = field(default_factory=list)
    travel_date: str = ""
    travelers: int = 1
    needs_companion: bool = False
    needs_wellness: bool = True
    wellness_mode: str = "recommend_only"  # not_needed | recommend_only | selected
    selected_wellness_categories: list[str] = field(default_factory=list)


@dataclass
class ItineraryDay:
    day: int
    theme: str
    morning: str
    noon: str
    afternoon: str
    evening: str
    confirmations: list[str] = field(default_factory=list)


@dataclass
class CompanionMatch:
    name: str
    score: int
    reasons: list[str]
    service_scope: list[str] = field(default_factory=list)
    service_boundary: str = ""
    data_status: str = ""


def serialise(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return value
