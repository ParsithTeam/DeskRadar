import asyncio
from datetime import datetime, timezone

from fastapi import HTTPException, status as http_status

from app.repositories.incident_repository import IncidentRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.alert_service import AlertService
from app.schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentStatus,
    IncidentSeverity, IncidentFilter, IncidentStatusUpdate
)
from app.schemas.alert import AlertSeverity, AlertType, AlertCreate


class IncidentService:
    def __init__(self, incident_repo: IncidentRepository, alert_serv: AlertService, ticket_repo: TicketRepository) -> None:
        self.incident_repo = incident_repo
        self.alert_serv = alert_serv
        self.ticket_repo = ticket_repo

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
            severity = IncidentSeverity(raw_severity)
        except ValueError:
            severity = IncidentSeverity.MEDIUM
            print(f"Unknown severity: {raw_severity}")

        matched_tickets = list(incident_info.get("matched_tickets", []))
        if len(matched_tickets) == 0:
            print("Probably bad request format..!")
        try:
            matched_ticket_ids = self._matched_ticket_parser(matched_tickets)
        except Exception as e:
            print("Unable to parse incident matched tickets!")
            matched_ticket_ids = []

        if ticket_id not in matched_ticket_ids:
            matched_tickets.append({"ticket_id": ticket_id, "similarity": 0.2})
            print(f"Ticket {ticket_id} was not include in it's own incident!")

        if is_duplicate and duplicate_id:
            existing_incident = await self.incident_repo.get_by_id(duplicate_id)

            if existing_incident:
                old_severity = IncidentSeverity.normalize(existing_incident.get("severity"))
                update_data = IncidentUpdate(
                    new_tickets=matched_tickets,
                    severity=severity,
                )

                incident_out = await self.incident_repo.update(incident_id=duplicate_id, update_data=update_data)

                if old_severity!=severity and severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
                    send_alert = True
        else:
            new_incident_data = IncidentCreate(
                title_fa=incident_info.get("fa_title_incident", f"رخداد احتمالی در دسته {category}"),
                reason_fa=incident_info.get("fa_reason_incident", "تعداد قابل توجهی تیکت هم‌پوشان شناسایی شد."),
                severity=severity,
                status=IncidentStatus.CANDIDATE,
                matched_tickets= matched_tickets
            )

            incident_out = await self.incident_repo.create(new_incident_data)
            #TODO: کامیت بعد از اتصال دیتابیس
            #await self.incident_repo.commit()

            if severity in [IncidentSeverity.HIGH, IncidentSeverity.CRITICAL]:
                send_alert = True
        #بخش ارسال هشدار در صورت نیاز
        if send_alert and incident_out:
            await self._dispatch_alert(incident=incident_out, severity=severity, is_duplicate=is_duplicate)

        return incident_out

    async def _dispatch_alert(self, incident: dict, severity:IncidentSeverity, is_duplicate:bool):
        """ارسال alert بعد از commit؛ شکست آن incident را از بین نمی‌برد."""
        new_alert = AlertCreate(
            type=AlertType.INCIDENT_CANDIDATE,
            message="یک رخداد جدید شناسایی شد" if not is_duplicate else "یک رخداد به سطح هشدار رسید",
            severity=AlertSeverity.CRITICAL if severity == IncidentSeverity.CRITICAL else AlertSeverity.WARNING,
            incident_id=incident.get("id"),
            idempotency_key= f"incident-{incident['id']}-{severity.value}"
        )
        try:
            await asyncio.wait_for(
                self.alert_serv.create_and_broadcast(new_alert),
                timeout=5.0,
            )
        except Exception as e:
            print(f"fail to broadcast alert: {new_alert.model_dump()}. Error: {str(e)}")

    def _matched_ticket_parser(self, data: list[dict]) -> tuple[list[int], dict[int, float] ]:
        matched_ticket_ids = []
        matched_tickets: dict[int, float] = {}
        for t in data:
            if "ticket_id" in t and "similarity" in t:
                matched_ticket_ids.append(t["ticket_id"])
                matched_tickets[t["ticket_id"]] = t["similarity"]

        return matched_ticket_ids, matched_tickets


    async def get_all(self, filter: IncidentFilter) -> dict:
        items, total = await self.incident_repo.get_all(status=filter.status, offset=filter.offset, limit=filter.limit)
        for it in items:
            it.update({"resolved": True if it.get("resolved_at") else False})

        return {"items": items, "total": total}


    async def get_incident_by_id(self, incident_id: int) -> dict | None:
        incident = await self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail= f"Incident {incident_id} not found")

        matched_ticket_ids, matched_ticket_similarities = self._matched_ticket_parser(incident.get("matched_tickets", []))
        if len(matched_ticket_ids) == 0:
            print(f"Incident {incident_id} has no matching tickets!")
            #TODO: قرار دادن منطق حذف رخداد یا چیز دیگه ای
        tickets_data = await self.ticket_repo.get_tickets(ticket_ids=matched_ticket_ids)
        enriched_tickets = []
        for t in tickets_data:
            enriched_tickets.append({
                "ticket_id": t.get("ticket_id"),
                "title": t.get("title"),
                "category": t.get("category"),
                "category_label_fa": t.get("category_label_fa"),
                "similarity": matched_ticket_similarities[t.get("ticket_id")],
            })

        response_payload = {**incident, "tickets": enriched_tickets, "ticket_count": len(enriched_tickets)}
        return response_payload



    async def update_status(self, incident_id: int, payload: IncidentStatusUpdate):
        incident = await self.incident_repo.get_by_id(incident_id)
        if not incident:
            raise HTTPException(status_code=404, detail= f"Incident {incident_id} not found")

        current_status= IncidentStatus.normalize(incident.get("status", IncidentStatus.CONFIRMED))
        if self._is_incident_terminated(current_status):
            raise HTTPException(status_code= http_status.Http_400, detail= f"Incident {incident_id} already terminated")

        if current_status == payload.status:
            return incident

        update_data = IncidentUpdate(
            status=payload.status,
            resolved_at= datetime.now(timezone.utc) if payload.status == IncidentStatus.RESOLVED else None,
        )
        return await self.incident_repo.update(incident_id=incident_id, update_data=update_data)


    def _is_incident_terminated(self, status: IncidentStatus) -> bool:
        if status in [IncidentStatus.DISMISSED, IncidentStatus.RESOLVED]:
            return True
        return False