from datetime import datetime, timezone
from app.schemas.alert import AlertCreate

# دیتابیس موقت (تا زمان اتصال PostgreSQL)
FAKE_ALERTS_DB = []
ALERT_ID_COUNTER = 17


class AlertRepository:
    # در آینده اینجا db_session پاس داده می‌شود: def __init__(self, db: AsyncSession):
    def __init__(self):
        pass

    async def create_alert(self, alert_in: AlertCreate) -> dict:
        global ALERT_ID_COUNTER

        new_alert = alert_in.model_dump()
        new_alert.update({
            "id": ALERT_ID_COUNTER,
            "is_read": False,
            "created_at": datetime.now(timezone.utc)
        })

        FAKE_ALERTS_DB.append(new_alert)
        ALERT_ID_COUNTER += 1
        return new_alert

    async def get_all_alerts(self, unread_only: bool = False) -> list[dict]:
        if unread_only:
            return [alert for alert in FAKE_ALERTS_DB if not alert.get("is_read")]
        return FAKE_ALERTS_DB

    async def mark_as_read(self, alert_id: int) -> dict | None:
        for alert in FAKE_ALERTS_DB:
            if alert.get("id") == alert_id:
                alert["is_read"] = True
                return alert
        return None