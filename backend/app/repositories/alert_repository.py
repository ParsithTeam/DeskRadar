# import copy
# from datetime import datetime, timezone

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.schemas.alert import AlertCreate, AlertSeverity, AlertType

# # دیتابیس موقت (تا زمان اتصال کامل دیتابیس)
# FAKE_ALERTS_DB: list[dict] = []
# ALERT_ID_COUNTER = 101


# def _seed_initial_alerts() -> None:
#     global ALERT_ID_COUNTER
#     if FAKE_ALERTS_DB:
#         return

#     now = datetime.now(timezone.utc)
#     sample_alerts = [
#         {
#             "id": 1,
#             "alert_id": 1,
#             "type": AlertType.INCIDENT_CANDIDATE.value,
#             "title": "رخداد احتمالی در سرویس VPN",
#             "message": "تعداد ۵ تیکت هم‌پوشان در دسته‌بندی VPN ثبت شده است.",
#             "severity": AlertSeverity.CRITICAL.value,
#             "ticket_id": 101,
#             "incident_id": 911,
#             "is_read": False,
#             "read": False,
#             "assigned_admin_id": None,
#             "assigned_admin_name": None,
#             "created_at": now,
#         },
#         {
#             "id": 2,
#             "alert_id": 2,
#             "type": AlertType.URGENT_TICKET.value,
#             "title": "تیکت با فوریت بحرانی",
#             "message": "تیکت جدید با درخواست فوری جلسه آنلاین و قطعی دسترسی اینترنت ثبت شد.",
#             "severity": AlertSeverity.HIGH.value,
#             "ticket_id": 102,
#             "incident_id": None,
#             "is_read": False,
#             "read": False,
#             "assigned_admin_id": None,
#             "assigned_admin_name": None,
#             "created_at": now,
#         },
#     ]
#     FAKE_ALERTS_DB.extend(sample_alerts)


# _seed_initial_alerts()


# class AlertRepository:
#     """
#     ریپازیتوری هشدارها:
#     مسئول ذخیره، واکشی و تغییر وضعیت خوانده‌شدن هشدارها با رعایت لاجیک انتساب First-Read.
#     """
#     def __init__(self, session: AsyncSession | None = None):
#         self.session = session

#     async def create_alert(self, alert_in: AlertCreate) -> dict:
#         global ALERT_ID_COUNTER

#         new_alert = alert_in.model_dump()
#         alert_id = ALERT_ID_COUNTER
#         ALERT_ID_COUNTER += 1

#         new_alert.update({
#             "id": alert_id,
#             "alert_id": alert_id,
#             "is_read": False,
#             "read": False,
#             "assigned_admin_id": None,
#             "assigned_admin_name": None,
#             "created_at": datetime.now(timezone.utc),
#         })

#         FAKE_ALERTS_DB.insert(0, new_alert)
#         return copy.deepcopy(new_alert)

#     async def get_all_alerts(self, unread_only: bool = False) -> list[dict]:
#         if unread_only:
#             return copy.deepcopy([alert for alert in FAKE_ALERTS_DB if not alert.get("is_read")])
#         return copy.deepcopy(FAKE_ALERTS_DB)

#     async def get_by_id(self, alert_id: int) -> dict | None:
#         for alert in FAKE_ALERTS_DB:
#             if alert.get("id") == alert_id or alert.get("alert_id") == alert_id:
#                 return copy.deepcopy(alert)
#         return None

#     async def mark_as_read(
#         self,
#         alert_id: int,
#         admin_id: str | None = None,
#         admin_name: str | None = None,
#     ) -> dict | None:
#         """
#         پیاده‌سازی لاجیک First-Read:
#         - هشدار به وضعیت خوانده‌شده (is_read=True) تغییر می‌کند.
#         - اولین ادمینی که هشدار را بخواند، به عنوان مسئول (assigned_admin) ثبت می‌شود.
#         - اگر قبلاً ادمینی منتسب شده باشد، با خواندن ادمین‌های بعدی بازنویسی نمی‌شود.
#         """
#         for alert in FAKE_ALERTS_DB:
#             if alert.get("id") == alert_id or alert.get("alert_id") == alert_id:
#                 alert["is_read"] = True
#                 alert["read"] = True

#                 # اگر هشدار تاکنون ادمین مسئول نداشته، اولین ادمین به صورت اتمیک منتسب می‌شود
#                 if not alert.get("assigned_admin_id") and admin_id:
#                     alert["assigned_admin_id"] = str(admin_id)
#                     alert["assigned_admin_name"] = str(admin_name or f"ادمین {admin_id}")

#                 return copy.deepcopy(alert)
#         return None

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate
from app.models.incident import Incident

class AlertRepository:

    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    def _to_dict(self, alert: Alert) -> dict:
        return {
            "id": alert.id,
            "alert_id": alert.id,

            "type": alert.type,
            "message": alert.message,
            "severity": alert.severity,

            "title": f"هشدار {alert.type}",

            "ticket_id": alert.ticket_id,
            "incident_id": alert.incident_id,

            "urgent_ticket": alert.urgent_ticket,
            "incident_candidate": alert.incident_candidate,
            "sla_risk": alert.sla_risk,

            "is_read": alert.is_read,
            "read": alert.is_read,

            "assigned_admin_id": alert.assigned_admin_id,
            "assigned_admin_name": alert.assigned_admin_name,

            "idempotency_key": alert.idempotency_key,
            "created_at": alert.created_at,
        }

    async def create_alert(self, alert_in: AlertCreate) -> dict:
        if self.session is None:
            raise RuntimeError("Database session is not available.")

        data = alert_in.model_dump()

        new_alert = Alert(
            type=data["type"].value if hasattr(data["type"], "value") else str(data["type"]),
            message=data["message"],
            severity=(
                data["severity"].value
                if hasattr(data["severity"], "value")
                else str(data["severity"])
            ),
            ticket_id=data.get("ticket_id"),
            incident_id=data.get("incident_id"),
            idempotency_key=data["idempotency_key"],
            urgent_ticket=False,
            incident_candidate=False,
            sla_risk=False,
            is_read=False,
            assigned_admin_id=None,
            assigned_admin_name=None,
            created_at=datetime.utcnow(),
        )

        try:
            self.session.add(new_alert)
            await self.session.flush()

            return self._to_dict(new_alert)

        except IntegrityError:
            await self.session.rollback()

            # اگر همین idempotency_key قبلاً ثبت شده،
            # همان Alert قبلی را برگردان.
            result = await self.session.execute(
                select(Alert).where(
                    Alert.idempotency_key == data["idempotency_key"]
                )
            )
            existing_alert = result.scalar_one_or_none()

            if existing_alert:
                return self._to_dict(existing_alert)

            raise

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    async def get_all_alerts(
        self,
        unread_only: bool = False,
    ) -> list[dict]:

        if self.session is None:
            raise RuntimeError("Database session is not available.")

        query = select(Alert).order_by(Alert.created_at.desc())

        if unread_only:
            query = query.where(Alert.is_read.is_(False))

        result = await self.session.execute(query)
        alerts = result.scalars().all()

        return [self._to_dict(alert) for alert in alerts]

    async def get_by_id(
        self,
        alert_id: int,
    ) -> dict | None:

        if self.session is None:
            raise RuntimeError("Database session is not available.")

        result = await self.session.execute(
            select(Alert).where(Alert.id == alert_id)
        )

        alert = result.scalar_one_or_none()

        if alert is None:
            return None

        return self._to_dict(alert)

    async def mark_as_read(
        self,
        alert_id: int,
        admin_id: str | None = None,
        admin_name: str | None = None,
    ) -> dict | None:

        if self.session is None:
            raise RuntimeError("Database session is not available.")

        # قفل کردن ردیف برای First-Read اتمیک
        result = await self.session.execute(
            select(Alert)
            .where(Alert.id == alert_id)
            .with_for_update()
        )

        alert = result.scalar_one_or_none()

        if alert is None:
            return None

        alert.is_read = True

        # فقط اولین ادمینی که Alert را می‌خواند assign شود
        if alert.assigned_admin_id is None and admin_id is not None:
            alert.assigned_admin_id = str(admin_id)
            alert.assigned_admin_name = (
                str(admin_name)
                if admin_name
                else f"ادمین {admin_id}"
            )

        await self.session.flush()

        return self._to_dict(alert)