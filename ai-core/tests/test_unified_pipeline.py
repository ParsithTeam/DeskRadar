import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.infrastructure.embedding_model import set_model_for_testing
from app.main import app
from tests.test_analyzer_service import fake_classifier


class DeterministicMockEmbeddingModel:
    is_ready = True
    model_version = "mock-unified-test-v1"
    dimension = 4

    def encode(self, text: str) -> list[float]:
        t = text.lower()
        if "vpn" in t:
            return [1.0, 0.0, 0.0, 0.0]
        if "پرینتر" in t or "printer" in t:
            return [0.0, 1.0, 0.0, 0.0]
        if "ایمیل" in t or "email" in t:
            return [0.0, 0.0, 1.0, 0.0]
        return [0.0, 0.0, 0.0, 1.0]

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.encode(t) for t in texts]


@pytest.fixture(autouse=True)
def inject_mock_embedding():
    set_model_for_testing(DeterministicMockEmbeddingModel())


def test_unified_analyze_composite_vpn_scenario():
    with (
        patch(
            "app.analyzer.zero_shot_category.get_classifier",
            return_value=fake_classifier,
        ),
        TestClient(app) as client,
    ):
        payload = {
            "ticket_id": 101,
            "title": "VPN وصل نمی‌شود",
            "description": "خطای احراز هویت دارم و وی‌پی‌ان قطع است.",
            "old_tickets": [
                {
                    "ticket_id": 18,
                    "title": "VPN خطا می‌دهد",
                    "description": "وی‌پی‌ان قطع است",
                    "category": "vpn",
                    "status": "open",
                },
                {
                    "ticket_id": 22,
                    "title": "مشکل در اتصال به VPN",
                    "description": "وی‌پی‌ان کار نمیکنه",
                    "category": "vpn",
                    "status": "open",
                },
                {
                    "ticket_id": 35,
                    "title": "قطع شدن ارتباط راه دور",
                    "description": "vpn قطع است",
                    "category": "vpn",
                    "status": "open",
                },
                {
                    "ticket_id": 41,
                    "title": "عدم دسترسی به وی پی ان",
                    "description": "vpn ارور میده",
                    "category": "vpn",
                    "status": "open",
                },
            ],
            "open_incidents": [],
            "debug": False,
        }

        response = client.post("/analyze", json=payload)
        assert response.status_code == 200, response.text
        data = response.json()

        # 1. Check Root Fields
        assert data["ticket_id"] == 101
        assert data["status"] == "completed"
        assert "analysis" in data
        assert "intelligence" in data
        assert "meta" in data

        # 2. Check Analysis Block (Analyzer)
        analysis = data["analysis"]
        assert analysis["category"] == "vpn"
        assert analysis["analysis_status"] == "completed"
        assert "suggested_reply_fa" in analysis
        assert "summary_fa" in analysis
        assert "urgency" in analysis

        # 3. Check Intelligence Block (Infrastructure)
        intelligence = data["intelligence"]
        similar_tickets = intelligence["similar_tickets"]
        assert len(similar_tickets) == 4
        assert {t["ticket_id"] for t in similar_tickets} == {18, 22, 35, 41}

        incident = intelligence["incident"]
        assert incident["possible_incident"] is True
        assert incident["severity"] == "high"
        assert incident["is_duplicate"] is False
        assert incident["fa_title_incident"] is not None

        # 4. Check Meta Block
        meta = data["meta"]
        assert meta["status"] == "completed"
        assert "latency_ms" in meta
        assert meta["embedding_model_version"] == "mock-unified-test-v1"


def test_unified_analyze_with_empty_pool():
    with (
        patch(
            "app.analyzer.zero_shot_category.get_classifier",
            return_value=fake_classifier,
        ),
        TestClient(app) as client,
    ):
        payload = {
            "ticket_id": 202,
            "title": "پرینتر خراب است",
            "description": "کاغذ داخل پرینتر گیر کرده",
            "old_tickets": [],
        }

        response = client.post("/analyze", json=payload)
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "completed"
        assert data["analysis"]["category"] == "printer"
        assert data["intelligence"]["similar_tickets"] == []
        assert data["intelligence"]["incident"]["possible_incident"] is False


def test_unified_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("ok", "degraded")
        assert "model_loaded" in data
        assert "zero_shot_model_loaded" in data
        assert "rule_fallback_available" in data
