from datetime import timezone, datetime
import copy
from app.schemas.incident import IncidentStatus, IncidentCreate, IncidentUpdate

FAKE_INCIDENT_DB = []
INCIDENT_ID_COUNTER = 911

class IncidentRepository:
    #TODO: در نسخه ی نهایی اینجا باید وابستگی(سشن دیتابیس) تزریق بشه
    def __init__(self):
        pass

    async def get_all(self, status: IncidentStatus | None = None) -> list[dict]:
        if status:
            return [inc for inc in FAKE_INCIDENT_DB if inc.get("status") == status]
        return FAKE_INCIDENT_DB

    async def get_by_id(self, incident_id: int) -> dict | None:
        for inc in FAKE_INCIDENT_DB:
            if inc.get("id") == incident_id:
                return inc
        return None

    async def create(self, incident_in: IncidentCreate) -> dict:
        global INCIDENT_ID_COUNTER
        now = datetime.now(timezone.utc)

        new_incident = incident_in.model_dump()
        new_incident.update({
            "id": INCIDENT_ID_COUNTER,
            "ticket_count": len(incident_in.matched_ticket_ids),
            "created_at": now,
            "updated_at": now,
            "resolved_at": None
        })

        INCIDENT_ID_COUNTER += 1
        FAKE_INCIDENT_DB.append(new_incident)
        return new_incident

    async def update(self, incident_id: int, update_data: IncidentUpdate) -> dict | None:

        incident = await self.get_by_id(incident_id)
        if not incident:
            return None

        # استخراج داده‌های جدید
        update_dict = update_data.model_dump(exclude_unset=True)

        # مدیریت منطق اتصال تیکت‌های جدید به رخداد فعلی
        if "new_ticket_ids" in update_dict:
            new_ids = update_dict.pop("new_ticket_ids")
            if new_ids:
                current_ids = set(incident["matched_ticket_ids"])
                current_ids.update(new_ids)
                incident["matched_ticket_ids"] = list(current_ids)
                incident["ticket_count"] = len(incident["matched_ticket_ids"])

        # آپدیت سایر فیلدها (مثل تغییر وضعیت یا تغییر شدت)
        for key, value in update_dict.items():
            if key != "new_ticket_ids":
                incident[key] = value

        incident["updated_at"] = datetime.now(timezone.utc)
        return copy.deepcopy(incident)