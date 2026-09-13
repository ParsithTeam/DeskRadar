import copy
from datetime import datetime, timezone
from app.schemas.alert import AlertCreate, AlertSeverity, AlertType

# دیتابیس موقت (تا زمان اتصال کامل دیتابیس)
FAKE_ALERTS_DB: list[dict] = []
ALERT_ID_COUNTER = 101


def _seed_initial_alerts() -> None:
    global ALERT_ID_COUNTER
    if FAKE_ALERTS_DB:
        return

    now = datetime.now(timezone.utc)
    sample_alerts = [
        {
            "id": 1,
            "alert_id": 1,
            "type": AlertType.INCIDENT_CANDIDATE.value,
            "title": "رخداد احتمالی در سرویس VPN",
            "message": "تعداد ۵ تیکت هم‌پوشان در دسته‌بندی VPN ثبت شده است.",
            "severity": AlertSeverity.CRITICAL.value,
            "ticket_id": 101,
            "incident_id": 911,
            "is_read": False,
            "read": False,
            "assigned_admin_id": None,
            "assigned_admin_name": None,
            "created_at": now,
        },
        {
            "id": 2,
            "alert_id": 2,
            "type": AlertType.URGENT_TICKET.value,
            "title": "تیکت با فوریت بحرانی",
            "message": "تیکت جدید با درخواست فوری جلسه آنلاین و قطعی دسترسی اینترنت ثبت شد.",
            "severity": AlertSeverity.HIGH.value,
            "ticket_id": 102,
            "incident_id": None,
            "is_read": False,
            "read": False,
            "assigned_admin_id": None,
            "assigned_admin_name": None,
            "created_at": now,
        },
    ]
    FAKE_ALERTS_DB.extend(sample_alerts)


_seed_initial_alerts()


class AlertRepository:
    """
    ریپازیتوری هشدارها:
    مسئول ذخیره، واکشی و تغییر وضعیت خوانده‌شدن هشدارها با رعایت لاجیک انتساب First-Read.
    """

    async def create_alert(self, alert_in: AlertCreate) -> dict:
        global ALERT_ID_COUNTER

        new_alert = alert_in.model_dump()
        alert_id = ALERT_ID_COUNTER
        ALERT_ID_COUNTER += 1

        new_alert.update({
            "id": alert_id,
            "alert_id": alert_id,
            "is_read": False,
            "read": False,
            "assigned_admin_id": None,
            "assigned_admin_name": None,
            "created_at": datetime.now(timezone.utc),
        })

        FAKE_ALERTS_DB.insert(0, new_alert)
        return copy.deepcopy(new_alert)

    async def get_all_alerts(self, unread_only: bool = False) -> list[dict]:
        if unread_only:
            return copy.deepcopy([alert for alert in FAKE_ALERTS_DB if not alert.get("is_read")])
        return copy.deepcopy(FAKE_ALERTS_DB)

    async def get_by_id(self, alert_id: int) -> dict | None:
        for alert in FAKE_ALERTS_DB:
            if alert.get("id") == alert_id or alert.get("alert_id") == alert_id:
                return copy.deepcopy(alert)
        return None

    async def mark_as_read(
        self,
        alert_id: int,
        admin_id: str | None = None,
        admin_name: str | None = None,
    ) -> dict | None:
        """
        پیاده‌سازی لاجیک First-Read:
        - هشدار به وضعیت خوانده‌شده (is_read=True) تغییر می‌کند.
        - اولین ادمینی که هشدار را بخواند، به عنوان مسئول (assigned_admin) ثبت می‌شود.
        - اگر قبلاً ادمینی منتسب شده باشد، با خواندن ادمین‌های بعدی بازنویسی نمی‌شود.
        """
        for alert in FAKE_ALERTS_DB:
            if alert.get("id") == alert_id or alert.get("alert_id") == alert_id:
                alert["is_read"] = True
                alert["read"] = True

                # اگر هشدار تاکنون ادمین مسئول نداشته، اولین ادمین به صورت اتمیک منتسب می‌شود
                if not alert.get("assigned_admin_id") and admin_id:
                    alert["assigned_admin_id"] = str(admin_id)
                    alert["assigned_admin_name"] = str(admin_name or f"ادمین {admin_id}")

                return copy.deepcopy(alert)
        return None