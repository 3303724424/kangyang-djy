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


def serialise(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return value
