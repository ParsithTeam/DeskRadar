from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.data_enum import Incident_Status
from app.models.incident import Incident
from app.models.ticket import TicketModel
from app.schemas.incident import IncidentCreate, IncidentStatus, IncidentUpdate


class IncidentRepository:

    def __init__(self, session: AsyncSession | None = None):
        self.session = session

    async def commit(self):
        await self.session.commit()

    def _require_session(self) -> AsyncSession:
        if self.session is None:
            raise RuntimeError("Database session is not available.")
        return self.session

    def _db_datetime(self, value: datetime | None) -> datetime | None:

        if value is None:
            return None

        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)

        return value

    def _db_status(self, value: IncidentStatus | str | None) -> Incident_Status:
        if value is None:
            return Incident_Status.CANDIDATE

        normalized = IncidentStatus.normalize(value)

        return Incident_Status[normalized.name]

    def _status_value(self, value) -> str | None:
        if value is None:
            return None

        if hasattr(value, "value"):
            return value.value

        return str(value).lower()

    async def _get_matched_tickets(
        self,
        incident_id: int,
    ) -> list[dict]:
    
        session = self._require_session()

        result = await session.execute(
            text(
                """
                SELECT ticket_id
                FROM tickets_incident
                WHERE incident_id = :incident_id
                ORDER BY ticket_id
                """
            ),
            {"incident_id": incident_id},
        )

        ticket_ids = [row[0] for row in result.all()]

        if not ticket_ids:
            return []

        # جدول similarity فعلی را می‌خوانیم و در Python تطبیق می‌دهیم.
        result = await session.execute(
            text(
                """
                SELECT
                    source_ticket_id,
                    target_ticket_id,
                    similarity
                FROM similarities_ticket
                """
            )
        )

        similarity_rows = result.all()

        matched_tickets = []

        for ticket_id in ticket_ids:
            scores = []

            for source_id, target_id, similarity in similarity_rows:
                if source_id == ticket_id and target_id in ticket_ids:
                    scores.append(float(similarity))

                elif target_id == ticket_id and source_id in ticket_ids:
                    scores.append(float(similarity))

            similarity = max(scores) if scores else 0.0

            matched_tickets.append(
                {
                    "ticket_id": ticket_id,
                    "similarity": similarity,
                }
            )

        return matched_tickets

    async def _add_ticket_links(
        self,
        incident_id: int,
        matched_tickets: list[dict],
    ) -> None:


        session = self._require_session()

        ticket_ids = []

        for item in matched_tickets:
            if not isinstance(item, dict):
                continue

            ticket_id = item.get("ticket_id")

            if isinstance(ticket_id, int):
                ticket_ids.append(ticket_id)

        if not ticket_ids:
            return

        # فقط ticketهایی که واقعاً در DB وجود دارند.
        result = await session.execute(
            select(TicketModel.id).where(
                TicketModel.id.in_(ticket_ids)
            )
        )

        valid_ticket_ids = {row[0] for row in result.all()}

        for ticket_id in valid_ticket_ids:
            await session.execute(
                text(
                    """
                    INSERT INTO tickets_incident (ticket_id, incident_id)
                    VALUES (:ticket_id, :incident_id)
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "ticket_id": ticket_id,
                    "incident_id": incident_id,
                },
            )

    def _to_dict(
        self,
        incident: Incident,
        matched_tickets: list[dict] | None = None,
    ) -> dict:

        return {
            "id": incident.id,

            # schema names
            "title_fa": incident.title,
            "reason_fa": incident.description,

            # model names هم نگه داشته می‌شوند
            "title": incident.title,
            "description": incident.description,

            "severity": incident.severity,
            "status": self._status_value(incident.status),

            "matched_tickets": matched_tickets or [],
            "ticket_count": len(matched_tickets or []),

            "created_at": incident.created_at,
            "updated_at": incident.updated_at,
            "resolved_at": incident.resolved_at,

            "resolved": incident.resolved_at is not None,
        }

    # ---------- CRUD ----------

    async def get_all(
        self,
        offset: int,
        limit: int = 20,
        status: IncidentStatus | None = None,
    ) -> tuple[list[dict], int]:

        session = self._require_session()

        conditions = []

        if status is not None:
            conditions.append(
                Incident.status == self._db_status(status)
            )

        # total
        count_query = select(func.count(Incident.id))

        if conditions:
            count_query = count_query.where(*conditions)

        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        # items
        query = (
            select(Incident)
            .order_by(Incident.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        if conditions:
            query = query.where(*conditions)

        result = await session.execute(query)
        incidents = result.scalars().all()

        items = []

        for incident in incidents:
            matched_tickets = await self._get_matched_tickets(
                incident.id
            )

            items.append(
                self._to_dict(
                    incident,
                    matched_tickets=matched_tickets,
                )
            )

        return items, total

    async def get_by_id(
        self,
        incident_id: int,
    ) -> dict | None:

        session = self._require_session()

        result = await session.execute(
            select(Incident).where(
                Incident.id == incident_id
            )
        )

        incident = result.scalar_one_or_none()

        if incident is None:
            return None

        matched_tickets = await self._get_matched_tickets(
            incident_id
        )

        return self._to_dict(
            incident,
            matched_tickets=matched_tickets,
        )

    async def create(
        self,
        incident_in: IncidentCreate,
    ) -> dict:

        session = self._require_session()

        data = incident_in.model_dump()

        now = datetime.utcnow()

        new_incident = Incident(
            title=data["title_fa"],
            description=data.get("reason_fa"),
            severity=(
                data["severity"].value
                if hasattr(data["severity"], "value")
                else str(data["severity"])
            ),
            status=self._db_status(
                data.get("status")
            ),
            created_at=now,
            updated_at=now,
            resolved_at=None,
        )

        try:
            session.add(new_incident)

            # گرفتن ID قبل از ثبت relationshipها
            await session.flush()

            matched_tickets = data.get(
                "matched_tickets",
                [],
            )

            await self._add_ticket_links(
                incident_id=new_incident.id,
                matched_tickets=matched_tickets,
            )

            await session.flush()

            saved_matched_tickets = await self._get_matched_tickets(
                new_incident.id
            )

            return self._to_dict(
                new_incident,
                matched_tickets=saved_matched_tickets,
            )

        except IntegrityError:
            await session.rollback()
            raise

        except SQLAlchemyError:
            await session.rollback()
            raise

    async def update(
        self,
        incident_id: int,
        update_data: IncidentUpdate,
    ) -> dict | None:

        session = self._require_session()

        result = await session.execute(
            select(Incident).where(
                Incident.id == incident_id
            )
        )

        incident = result.scalar_one_or_none()

        if incident is None:
            return None

        data = update_data.model_dump(
            exclude_unset=True
        )

        new_tickets = data.pop(
            "new_tickets",
            None,
        )

        if new_tickets:
            await self._add_ticket_links(
                incident_id=incident_id,
                matched_tickets=new_tickets,
            )

        if "title_fa" in data:
            incident.title = data["title_fa"]

        if "reason_fa" in data:
            incident.description = data["reason_fa"]

        if "description" in data:
            incident.description = data["description"]

        if "severity" in data:
            severity = data["severity"]

            incident.severity = (
                severity.value
                if hasattr(severity, "value")
                else str(severity)
            )

        if "status" in data:
            incident.status = self._db_status(
                data["status"]
            )

        if "resolved_at" in data:
            incident.resolved_at = self._db_datetime(
                data["resolved_at"]
            )

        incident.updated_at = datetime.utcnow()

        await session.flush()

        matched_tickets = await self._get_matched_tickets(
            incident_id
        )

        return self._to_dict(
            incident,
            matched_tickets=matched_tickets,
        )









# from datetime import timezone, datetime
# import copy

# from sqlalchemy.ext.asyncio import AsyncSession

# from app.schemas.incident import IncidentStatus, IncidentCreate, IncidentUpdate

# FAKE_INCIDENT_DB = []
# INCIDENT_ID_COUNTER = 911

# class IncidentRepository:

#     def __init__(self, session: AsyncSession | None = None):
#         self.session = session

#     async def get_all(self, offset:int, limit=int, status: IncidentStatus | None = None ) -> tuple[list[dict], int]:

#         items = []
#         for inc in FAKE_INCIDENT_DB:
#             if status and inc.get("status") != status:
#                 continue
#             items.append(inc)

#         return items[offset:offset+limit], len(items)

#     async def get_by_id(self, incident_id: int) -> dict | None:
#         for inc in FAKE_INCIDENT_DB:
#             if inc.get("id") == incident_id:
#                 return inc
#         return None

#     async def create(self, incident_in: IncidentCreate) -> dict:
#         global INCIDENT_ID_COUNTER
#         now = datetime.now(timezone.utc)

#         new_incident = incident_in.model_dump()
#         new_incident.update({
#             "id": INCIDENT_ID_COUNTER,
#             "ticket_count": len(incident_in.matched_tickets),
#             "created_at": now,
#             "updated_at": now,
#             "resolved_at": None
#         })

#         INCIDENT_ID_COUNTER += 1
#         FAKE_INCIDENT_DB.append(new_incident)
#         return new_incident

#     async def update(self, incident_id: int, update_data: IncidentUpdate) -> dict | None:
#         incident = await self.get_by_id(incident_id)
#         if not incident:
#             return None

#         update_dict = update_data.model_dump(exclude_unset=True)

#         if "new_tickets" in update_dict:
#             new_tickets = update_dict.pop("new_tickets")
#             if new_tickets:
#                 # دیکشنری از ticket_id → similarity از تیکت‌های فعلی
#                 existing_map = {
#                     t["ticket_id"]: t["similarity"]
#                     for t in incident["matched_tickets"]
#                     if isinstance(t, dict) and "similarity" in t
#                 }

#                 # دیکشنری از ticket_id → similarity از تیکت‌های جدید
#                 new_map = {
#                     t["ticket_id"]: t["similarity"]
#                     for t in new_tickets
#                     if isinstance(t, dict) and "similarity" in t
#                 }

#                 # merge: تیکت‌های جدید تیکت‌های قبلی را بازنویسی می‌کنند
#                 merged = {**existing_map, **new_map}

#                 # اختیاری: مرتب‌سازی نزولی بر اساس similarity
#                 incident["matched_tickets"] = [
#                     {"ticket_id": tid, "similarity": sim}
#                     for tid, sim in sorted(merged.items(), key=lambda x: -x[1])
#                 ]
#                 incident["ticket_count"] = len(incident["matched_tickets"])

#         for key, value in update_dict.items():
#             if key != "matched_tickets":
#                 incident[key] = value

#         incident["updated_at"] = datetime.now(timezone.utc)
#         return copy.deepcopy(incident)