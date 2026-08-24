import os
import unittest
import warnings
from unittest.mock import patch

os.environ["ANALYZER_PRELOAD_MODEL"] = "false"
warnings.filterwarnings(
    "ignore",
    message="Using `httpx` with `starlette.testclient` is deprecated.*",
)

try:
    from fastapi.testclient import TestClient

    from app.main import app
    from tests.test_analyzer_service import fake_classifier
except ImportError:
    TestClient = None


@unittest.skipIf(TestClient is None, "FastAPI test dependencies are not installed")
class AnalyzerApiTests(unittest.TestCase):
    def test_analyze_endpoint_and_schema(self):
        with (
            patch(
                "app.analyzer.zero_shot_category.get_classifier",
                return_value=fake_classifier,
            ),
            TestClient(app) as client,
        ):
            response = client.post(
                "/analyzer/analyze",
                json={
                    "ticket_id": "API-1",
                    "title": "مشکل VPN",
                    "description": "وی پی ان وصل نمی‌شود و احراز هویت خطا دارد",
                },
            )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertEqual(payload["category"], "vpn")
        self.assertEqual(payload["analysis_status"], "completed")
        self.assertNotIn("raw_ai_response", payload)

    def test_empty_payload_is_rejected(self):
        with TestClient(app) as client:
            response = client.post("/analyzer/analyze", json={})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
