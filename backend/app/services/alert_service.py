from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertCreate
from app.websocket.manager import ws_manager


class AlertService:
    def __init__(self, alert_repo: AlertRepository | None = None) -> None:
        self.alert_repo = alert_repo or AlertRepository()

    async def create_and_broadcast(self, alert_in: AlertCreate) -> dict:
        saved_alert = await self.alert_repo.create_alert(alert_in)
        await ws_manager.broadcast_alert(saved_alert)
        return saved_alert

    async def fetch_alerts(self, unread_only: bool = False) -> list[dict]:
        return await self.alert_repo.get_all_alerts(unread_only)

    async def get_alert_by_id(self, alert_id: int) -> dict | None:
        return await self.alert_repo.get_by_id(alert_id)

    async def mark_alert_read(
        self,
        alert_id: int,
        admin_id: str | None = None,
        admin_name: str | None = None,
    ) -> dict | None:
        """
        خوانده‌شدن هشدار و انتساب ادمین به عنوان مسئول (First-Read)
        سپس برودکست از طریق وب‌سوکت برای آپدیت فوری داشبورد همه ادمین‌ها.
        """
        updated_alert = await self.alert_repo.mark_as_read(
            alert_id=alert_id,
            admin_id=admin_id,
            admin_name=admin_name,
        )
        if updated_alert:
            await ws_manager.broadcast_alert(updated_alert)

        return updated_alert
