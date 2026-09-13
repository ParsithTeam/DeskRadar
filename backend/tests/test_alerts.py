from fastapi.testclient import TestClient


def test_get_alerts_list(client: TestClient):
    response = client.get("/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert isinstance(alerts, list)
    assert len(alerts) >= 1

    # اطمینان از رفع باگ ۵۰۰ و وجود هر دو کلید id و alert_id
    for a in alerts:
        assert "id" in a
        assert "alert_id" in a
        assert a["id"] == a["alert_id"]
        assert "is_read" in a
        assert "read" in a


def test_create_alert_trigger(client: TestClient):
    payload = {
        "type": "incident_candidate",
        "message": "رخداد احتمالی ناشی از تکرار تیکت‌های قطعی شبکه",
        "severity": "critical",
        "incident_id": 990,
    }
    response = client.post("/alerts/test-trigger", json=payload)
    assert response.status_code == 201
    alert = response.json()
    assert alert["type"] == payload["type"]
    assert alert["severity"] == payload["severity"]
    assert alert["is_read"] is False
    assert alert["assigned_admin_id"] is None


def test_alert_first_read_atomic_assignment(client: TestClient):
    # 1. ساخت هشدار جدید
    trigger_resp = client.post(
        "/alerts/test-trigger",
        json={
            "type": "urgent_ticket",
            "message": "هشدار تست لاجیک First-Read",
            "severity": "high",
            "ticket_id": 303,
        },
    )
    assert trigger_resp.status_code == 201
    alert_id = trigger_resp.json()["id"]

    # 2. اولین ادمین هشدار را می‌خواند (Admin 10)
    read_resp_1 = client.post(
        f"/alerts/{alert_id}/read?admin_id=admin-10&admin_name=علی رضایی",
    )
    assert read_resp_1.status_code == 200
    alert_after_admin1 = read_resp_1.json()
    assert alert_after_admin1["is_read"] is True
    assert alert_after_admin1["read"] is True
    assert alert_after_admin1["assigned_admin_id"] == "admin-10"
    assert alert_after_admin1["assigned_admin_name"] == "علی رضایی"

    # 3. دومین ادمین همان هشدار را می‌خواند (Admin 20)
    # لاجیک First-Read: انتساب نباید بازنویسی شود!
    read_resp_2 = client.post(
        f"/alerts/{alert_id}/read?admin_id=admin-20&admin_name=مریم احمدی",
    )
    assert read_resp_2.status_code == 200
    alert_after_admin2 = read_resp_2.json()
    assert alert_after_admin2["is_read"] is True
    assert alert_after_admin2["assigned_admin_id"] == "admin-10"
    assert alert_after_admin2["assigned_admin_name"] == "علی رضایی"


def test_mark_read_backward_compatibility_endpoint(client: TestClient):
    # تست اندپوینت /mark-read
    trigger_resp = client.post(
        "/alerts/test-trigger",
        json={
            "type": "urgent_ticket",
            "message": "تست اندپوینت معادل mark-read",
            "severity": "medium",
        },
    )
    alert_id = trigger_resp.json()["id"]

    resp = client.post(f"/alerts/{alert_id}/mark-read")
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True


def test_mark_read_non_existent_alert(client: TestClient):
    resp = client.post("/alerts/999999/read")
    assert resp.status_code == 404
