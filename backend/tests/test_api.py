import unittest

from fastapi.testclient import TestClient

from app.api import create_app
from app.domain.models import ElderProfile
from app.presenters.frontend_payload import build_frontend_payload
from app.services.care_plan_service import CarePlanService


class FakeAgent:
    """No GPU/model is needed to verify the HTTP contract."""

    def answer(self, question: str, profile: ElderProfile) -> dict:
        plan = CarePlanService().build_plan(profile)
        return {"frontend_payload": build_frontend_payload(plan)}


class ApiContractTest(unittest.TestCase):
    def setUp(self):
        self.client_context = TestClient(create_app(agent_factory=FakeAgent))
        self.client = self.client_context.__enter__()

    def tearDown(self):
        self.client_context.__exit__(None, None, None)

    def test_health_and_contract_are_available(self):
        self.assertEqual(200, self.client.get("/health").status_code)
        contract = self.client.get("/api/v1/frontend-contract").json()
        self.assertEqual("travel_frontend_payload_v1", contract["version"])

    def test_plan_returns_frontend_payload(self):
        response = self.client.post("/api/v1/travel/plan", json={
            "question": "两位七十多岁长者去都江堰三天，想轻松慢游并安排温泉。",
            "name": "张阿姨",
            "days": 3,
            "travelers": 2,
            "needs_student_guide": True,
            "wellness_mode": "selected",
            "wellness_categories": ["温泉", "营养餐"],
        })
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual("success", body["status"])
        self.assertEqual("travel_frontend_payload_v1", body["frontend_payload"]["version"])
        self.assertTrue(body["frontend_payload"]["student_guide"]["requested"])

    def test_invalid_days_returns_422(self):
        response = self.client.post("/api/v1/travel/plan", json={"question": "帮我规划", "days": 0})
        self.assertEqual(422, response.status_code)


if __name__ == "__main__":
    unittest.main()
