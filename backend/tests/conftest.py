import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# تنظیم متغیرهای محیطی پایه برای تست‌ها
os.environ.setdefault("AI_CORE_URL", "http://localhost:8001")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/servicedesk_radar")

# اضافه کردن مسیر backend به sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)
