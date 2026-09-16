from datetime import timezone, datetime
import copy
from app.schemas.incident import IncidentStatus, IncidentCreate, IncidentUpdate

FAKE_INCIDENT_DB = []
INCIDENT_ID_COUNTER = 911

class IncidentRepository:
    #TODO: در نسخه ی نهایی اینجا باید وابستگی(سشن دیتابیس) تزریق بشه
    def __init__(self):
        pass

    async def get_all(self, offset:int, limit=int, status: IncidentStatus | None = None ) -> tuple[list[dict], int]:

        items = []
        for inc in FAKE_INCIDENT_DB:
            if status and inc.get("status") != status:
                continue
            items.append(inc)

        return items[offset:offset+limit], len(items)

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
            "ticket_count": len(incident_in.matched_tickets),
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

        update_dict = update_data.model_dump(exclude_unset=True)

        if "new_tickets" in update_dict:
            new_tickets = update_dict.pop("new_tickets")
            if new_tickets:
                # استخراج فقط ticket_id ها از دیکشنری‌ها
                current_ids = {
                    t["ticket_id"] if isinstance(t, dict) else t
                    for t in incident["matched_tickets"]
                }
                # new_tickets هم ممکنه دیکشنری یا int باشه
                new_ids = {
                    t["ticket_id"] if isinstance(t, dict) else t
                    for t in new_tickets
                }
                current_ids.update(new_ids)

                # اگه می‌خوای ساختار دیکشنری حفظ بشه، باید similarity رو هم مدیریت کنی
                incident["matched_tickets"] = [
                    {"ticket_id": tid} for tid in current_ids
                ]
                incident["ticket_count"] = len(incident["matched_tickets"])

        for key, value in update_dict.items():
            if key != "matched_tickets":
                incident[key] = value

        incident["updated_at"] = datetime.now(timezone.utc)
        return copy.deepcopy(incident)