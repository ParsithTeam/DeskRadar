from datetime import datetime, timezone

from fastapi import HTTPException, status as http_status

from app.repositories.incident_repository import IncidentRepository
from app.services.alert_service import AlertService
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentStatus,
    SeverityLevel
)
from app.schemas.alert import AlertCreate, AlertSeverity, AlertType


class IncidentService:
    def __init__(self, incident_repo: IncidentRepository, alert_serv: AlertService) -> None:
        self.incident_repo = incident_repo
        self.alert_serv = alert_serv

    async def upsert_from_ai(self, ticket_id: int, category: str, intelligence_data: dict) -> dict | None:
        """
        دریافت تحلیل هوش مصنوعی، ساخت رخداد جدید یا به‌روزرسانی رخداد قبلی
        و ارسال خودکار هشدار زنده در موارد بحرانی.
        """
        incident_info: dict | None =  intelligence_data.get("incident")
        if not incident_info or not incident_info.get("possible_incident"):
            return None

        is_duplicate = incident_info.get("is_duplicate", False)
        duplicate_id: int | None = incident_info.get("duplicate_incident_id")
        raw_severity = incident_info.get("severity", "medium").lower()
        send_alert = False
        incident_out: dict | None = None

        try:
            severity = SeverityLevel(raw_severity)
        except ValueError:
            severity = SeverityLevel.MEDIUM
            print(f"Unknown severity: {raw_severity}")

        matched_ticket_ids = list(incident_info.get("matched_ticket_ids", []))
        if ticket_id not in matched_ticket_ids:
            matched_ticket_ids.append(ticket_id)

        if is_duplicate and duplicate_id:
            existing_incident = await self.incident_repo.get_by_id(duplicate_id)
            if existing_incident:
                old_severity = existing_incident.get("severity")
                update_data = IncidentUpdate(
                    new_ticket_ids=matched_ticket_ids,
                    severity=severity,
                )

                incident_out = await self.incident_repo.update(incident_id=duplicate_id, update_data=update_data)

                if old_severity!=severity and severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                    send_alert = True
        else:
            new_incident_data = IncidentCreate(
                title_fa=incident_info.get("fa_title_incident", f"رخداد احتمالی در دسته {category}"),
                reason_fa=incident_info.get("fa_reason_incident", "تعداد قابل توجهی تیکت هم‌پوشان شناسایی شد."),
                severity=severity,
                status=IncidentStatus.CANDIDATE,
                matched_ticket_ids=matched_ticket_ids
            )

            incident_out = await self.incident_repo.create(new_incident_data)
            if severity in [SeverityLevel.HIGH, SeverityLevel.CRITICAL]:
                send_alert = True
        #بخش ارسال هشدار در صورت نیاز
        if send_alert and incident_out:
            new_alert = AlertCreate(
                type= AlertType.INCIDENT_CANDIDATE,
                message= "یک رخداد جدید شناسایی شد" if not is_duplicate else "یک رخداد به سطح هشدار رسید",
                severity= AlertSeverity.CRITICAL if severity == SeverityLevel.CRITICAL else AlertSeverity.WARNING,
                incident_id= incident_out.get("id")
            )
            await self.alert_serv.create_and_broadcast(new_alert)

        return incident_out

    async def get_all_incidents(self, status: IncidentStatus | None = None) -> list[dict]:
        return await self.incident_repo.get_all(status)


    async def get_incident_by_id(self, incident_id: int) -> dict | None:
        return await self.incident_repo.get_by_id(incident_id)


    async def update_status(self, incident_id: int, new_status: IncidentStatus):
        incident = await self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail= f"Incident {incident_id} not found")

        current_status= incident.get("status", IncidentStatus.CONFIRMED)
        if self._is_incident_terminated(current_status):
            raise HTTPException(status_code= http_status.Http_400, detail= f"Incident {incident_id} already terminated")

        if current_status == new_status:
            return incident

        update_data = IncidentUpdate(
            status=new_status,
            resolved_at= datetime.now(timezone.utc) if new_status == IncidentStatus.RESOLVED else None,
        )
        return await self.incident_repo.update(incident_id=incident_id, update_data=update_data)


    def _is_incident_terminated(self, status: IncidentStatus) -> bool:
        if status in [IncidentStatus.DISMISSED, IncidentStatus.RESOLVED]:
            return True
        return False