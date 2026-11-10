"""FastAPI entry point for the Dujiangyan senior-travel assistant.

The model is loaded once during application startup.  Each request returns the
stable ``frontend_payload`` contract rather than asking the client to parse LLM
prose.
"""

from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.domain.models import ElderProfile
from app.llm.local_qwen import LocalQwen
from app.services.agent_service import LocalTravelAgent


DEFAULT_MODEL_PATH = r"D:\project\travel1\2\models\Qwen3-8B"
DEFAULT_ADAPTER_PATH = r"D:\git\kangyang-djy\agent\training\outputs\qwen3-djy-lora-v2"
MOBILITY_OPTIONS = ("可轻松步行", "需要减少步行", "需轮椅协助")
WELLNESS_MODES = ("not_needed", "recommend_only", "selected")


class TravelPlanRequest(BaseModel):
    """Parameters collected by the frontend before planning a trip."""

    question: str = Field(..., min_length=2, max_length=1000, description="用户的自然语言需求")
    name: str = Field("体验用户", min_length=1, max_length=40, description="称呼，仅用于温暖文案")
    age_group: str = Field("70-79岁", min_length=1, max_length=30, description="年龄段，例如：70-79岁")
    days: int = Field(3, ge=1, le=7, description="行程天数；Demo 目前支持 1-7 天")
    travelers: int = Field(1, ge=1, le=10, description="同行人数")
    budget: int = Field(1800, ge=0, le=100000, description="预算，仅用于候选筛选，不代表报价")
    mobility: Literal["可轻松步行", "需要减少步行", "需轮椅协助"] = Field(
        "需要减少步行", description="行动能力，用于控制强度"
    )
    preferences: list[str] = Field(
        default_factory=lambda: ["文化讲解", "轻松慢游"], description="偏好标签，如 [\"文化讲解\", \"温泉\"]"
    )
    travel_date: str = Field("", max_length=50, description="出行日期，当前仅展示给规划逻辑，不校验实时天气")
    needs_student_guide: bool = Field(False, description="是否需要平台学生导游陪伴候选")
    wellness_mode: Literal["not_needed", "recommend_only", "selected"] = Field(
        "recommend_only",
        description="not_needed=不展示；recommend_only=仅候选；selected=已选项目后才尝试排入行程",
    )
    wellness_categories: list[str] = Field(
        default_factory=list, description="用户已选的康养类别，如 [\"温泉\", \"营养餐\"]；仅 selected 时用于排程"
    )

    def to_profile(self) -> ElderProfile:
        return ElderProfile(
            name=self.name.strip(),
            age_group=self.age_group.strip(),
            days=self.days,
            budget=self.budget,
            mobility=self.mobility,
            preferences=[item.strip() for item in self.preferences if item.strip()],
            travel_date=self.travel_date.strip(),
            travelers=self.travelers,
            needs_companion=self.needs_student_guide,
            needs_wellness=self.wellness_mode != "not_needed",
            wellness_mode=self.wellness_mode,
            selected_wellness_categories=[item.strip() for item in self.wellness_categories if item.strip()],
        )


class TravelPlanResponse(BaseModel):
    request_id: str = Field(description="请求追踪 ID")
    status: Literal["success"] = "success"
    generated_at: str = Field(description="UTC 生成时间")
    frontend_payload: dict[str, Any] = Field(description="前端渲染专用数据；不要解析 LLM 原始文字")


AgentFactory = Callable[[], LocalTravelAgent]


def _default_agent_factory() -> LocalTravelAgent:
    model_path = os.getenv("TRAVEL_MODEL_PATH", DEFAULT_MODEL_PATH)
    adapter_path = os.getenv("TRAVEL_ADAPTER_PATH", DEFAULT_ADAPTER_PATH)
    return LocalTravelAgent(LocalQwen(model_path, adapter_path))


def _cors_origins() -> list[str]:
    raw = os.getenv("TRAVEL_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173")
    return [item.strip() for item in raw.split(",") if item.strip()]


def create_app(agent_factory: AgentFactory | None = None) -> FastAPI:
    """Create an app; ``agent_factory`` keeps API tests independent of the 8B model."""

    factory = agent_factory or _default_agent_factory

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.agent = factory()
        # GPU generation is deliberately serialised: the local model is not a request-per-GPU worker pool.
        app.state.generation_lock = asyncio.Lock()
        app.state.started_at = datetime.now(timezone.utc).isoformat()
        yield

    app = FastAPI(
        title="都江堰银龄康养旅居智能体 API",
        version="1.0.0",
        description="本地 Qwen + RAG + 规则规划接口。响应使用 frontend_payload，适合前端直接渲染时间线卡片。",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"message": "都江堰银龄康养旅居智能体 API", "docs": "/docs"}

    @app.get("/health", tags=["system"])
    async def health(request: Request) -> dict[str, Any]:
        return {
            "status": "ready" if hasattr(request.app.state, "agent") else "starting",
            "service": "dujiangyan-senior-travel-agent",
            "started_at": getattr(request.app.state, "started_at", None),
        }

    @app.get("/api/v1/frontend-contract", tags=["system"])
    async def frontend_contract() -> dict[str, Any]:
        return {
            "version": "travel_frontend_payload_v1",
            "plan_endpoint": "POST /api/v1/travel/plan",
            "render_rule": "仅渲染 frontend_payload；不要解析或展示模型内部的原始回答。",
            "availability_rule": "酒店、餐厅、康养服务与学生导游均可能需要人工确认，前端应展示 manual_confirmations。",
        }

    @app.post(
        "/api/v1/travel/plan",
        response_model=TravelPlanResponse,
        tags=["travel"],
        summary="生成银龄康养旅居行程",
        response_description="可由前端直接渲染的结构化行程 JSON",
    )
    async def create_travel_plan(payload: TravelPlanRequest, request: Request) -> TravelPlanResponse:
        agent = getattr(request.app.state, "agent", None)
        if agent is None:
            raise HTTPException(status_code=503, detail="模型正在启动，请稍后重试。")
        try:
            async with request.app.state.generation_lock:
                result = await run_in_threadpool(agent.answer, payload.question.strip(), payload.to_profile())
        except Exception as exc:  # keep model internals out of the client response
            raise HTTPException(status_code=500, detail="行程生成失败，请检查模型、适配器和本地知识库日志。") from exc
        return TravelPlanResponse(
            request_id=str(uuid.uuid4()),
            generated_at=datetime.now(timezone.utc).isoformat(),
            frontend_payload=result["frontend_payload"],
        )

    return app


app = create_app()
