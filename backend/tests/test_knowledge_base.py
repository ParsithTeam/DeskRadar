from fastapi.testclient import TestClient


def test_list_knowledge_articles(client: TestClient):
    response = client.get("/knowledge-articles")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert data["total"] >= 1


def test_list_knowledge_articles_category_filter(client: TestClient):
    response = client.get("/knowledge-articles?category=vpn")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["category"].lower() == "vpn"


def test_list_knowledge_articles_search_query(client: TestClient):
    response = client.get("/knowledge-articles?q=VPN")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_create_and_get_knowledge_article(client: TestClient):
    payload = {
        "title": "راهنمای تنظیم پروکسی تلگرام",
        "content": "برای تنظیم پروکسی داخلی، پورت 1080 و سرور محلی شرکت را در تنظیمات وارد نمایید.",
        "category": "network",
        "tags": ["proxy", "telegram", "پروکسی"],
        "summary": "نحوه تنظیم پروکسی داخلی جهت دسترسی پایدار",
    }
    create_resp = client.post("/knowledge-articles", json=payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    assert created_data["title"] == payload["title"]
    assert created_data["category"] == "network"
    assert created_data["category_label_fa"] == "شبکه و اینترنت"
    assert "id" in created_data
    article_id = created_data["id"]

    # بررسی دریافت جزئیات
    get_resp = client.get(f"/knowledge-articles/{article_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == article_id
    assert get_resp.json()["content"] == payload["content"]


def test_create_article_validation_error(client: TestClient):
    # تست ارسال فیلد ناقص (عدم ارسال content)
    invalid_payload = {
        "title": "عنوان تستی بدون محتوا"
    }
    response = client.post("/knowledge-articles", json=invalid_payload)
    assert response.status_code == 422


def test_get_non_existent_article_returns_404(client: TestClient):
    response = client.get("/knowledge-articles/999999")
    assert response.status_code == 404


def test_update_and_delete_article(client: TestClient):
    # 1. ساخت مقاله موقت
    create_resp = client.post(
        "/knowledge-articles",
        json={
            "title": "مقاله جهت ویرایش و حذف",
            "content": "این مقاله پس از تست ویرایش خواهد شد و سپس پاک می‌شود.",
            "category": "software",
        },
    )
    assert create_resp.status_code == 201
    art_id = create_resp.json()["id"]

    # 2. ویرایش
    update_resp = client.patch(
        f"/knowledge-articles/{art_id}",
        json={"title": "عنوان جدید به‌روزشده"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "عنوان جدید به‌روزشده"

    # 3. حذف
    delete_resp = client.delete(f"/knowledge-articles/{art_id}")
    assert delete_resp.status_code == 204

    # 4. اطمینان از عدم وجود پس از حذف
    get_again = client.get(f"/knowledge-articles/{art_id}")
    assert get_again.status_code == 404


def test_reindex_endpoint(client: TestClient):
    response = client.post("/knowledge-articles/reindex")
    assert response.status_code == 200
