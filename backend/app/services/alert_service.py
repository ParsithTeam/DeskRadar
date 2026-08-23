from app.repositories.alert_repository import AlertRepository
from app.websocket.manager import ws_manager
from app.schemas.alert import AlertCreate


class AlertService:
    def __init__(self, alert_repo: AlertRepository):
        self.alert_repo = alert_repo

    async def create_and_broadcast(self, alert_in: AlertCreate) -> dict:
        #TODO: ذخیره در دیتابیس - ارسال اعلان به ادمین ها

        saved_alert = await self.alert_repo.create_alert(alert_in)

        #TODO: بررسی بشه آیا نیاز به قالب بندی فراتر داریم یا نه
        # ws_payload = {
        #     "type": alert_in.type,
        #     "data": saved_alert
        # }

        await ws_manager.broadcast_alert(saved_alert)

        return saved_alert

    async def fetch_alerts(self, unread_only: bool = False) -> list:
        return await self.alert_repo.get_all_alerts(unread_only)

    async def mark_alert_read(self, alert_id: int) -> dict | None:
        return await self.alert_repo.mark_as_read(alert_id)
