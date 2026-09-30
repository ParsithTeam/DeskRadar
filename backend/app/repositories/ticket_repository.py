import copy
import hashlib
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.querise.ticket_querise import TicketQuery
from app.schemas.ticket import AnalysisStatus, TicketStatus, TicketUrgency


from sqlalchemy import select, update, or_, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import selectinload

from app.models.ticket import TicketModel
from app.models.ticket_analysis import TicketAnalysis

from app.core.data_enum import (
    Analysis_Status,
    Ticket_Status,
    Urgency_Status,
    Source_Status,
)

from app.exceptions.ticket_exceptions import (
    DuplicateTicketError,
    TicketPersistenceError,
)

#-----------------------------------------
#from app.models.ticket import TicketModel   //TODO:بعد از اتصال دیتا بیس از این مدل واقعی استفاده میکنیم
#-----------------------------------------

FAKE_TICKETS_DB :list[dict] = []
_id_counter = 777

class TicketRepository:

    def __init__(self, session: AsyncSession | None = None):
        self.session = session
    # ساخت اثر انگشت مخصوص، بعدا بنظرم بهتهره زمان هم به متد هش اضافه کرد

    def _to_dict(
        self,
        ticket: TicketModel,
        include_ai_details: bool = False,
    ) -> dict:

        analysis = ticket.analysis

        ai_analysis = None

        if include_ai_details and analysis is not None:
            ai_analysis = {
                "category": analysis.category,
                "category_label_fa": analysis.category_label_fa,
                "confidence": analysis.confidence,
                "intent": analysis.intent,
                "intent_label_fa": analysis.intent_label_fa,
                "urgency": analysis.urgency.value if analysis.urgency else TicketUrgency.UNKNOWN.value,
                "summary_fa": analysis.summary_fa,
                "suggested_reply_fa": analysis.suggested_reply_fa,
                "reasons_fa": analysis.reasons_fa or [],
                "related_article": [],
            }

        return {
            "ticket_id": ticket.id,
            "title": ticket.title,
            "description": ticket.description,
            "requester": ticket.requester_name,
            "department": ticket.department,
            "analysis_status": ticket.analysis_status.value,
            "ticket_status": ticket.ticket_status.value,
            "source": ticket.source.value,
            "fingerprint": ticket.fingerprint,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,

            "urgency": (
                analysis.urgency.value
                if analysis and analysis.urgency
                else TicketUrgency.UNKNOWN.value
            ),

            "category": analysis.category if analysis else "unknown",
            "category_label_fa": (
            analysis.category_label_fa
                if analysis and analysis.category_label_fa
                else "نامشخص"
            ),

            "ai_analysis": ai_analysis,
        }

    def _generate_fingerprint(self, title: str,
                              description: str,
                              requester: str | None) -> str:
        req = requester or "nobody"
        raw_text = f"{title.lower()}{description.lower()}{req.lower()}"
        return hashlib.md5(raw_text.encode("utf-8")).hexdigest()
    
    # async def get_by_fingerprint(self, finger_print) -> Optional[str]:
    #     for T in FAKE_TICKETS_DB:
    #         if T.get("fingerprint") == finger_print:
    #             return T
            
    #     return None
    
    # async def is_already_exist(self, title: str,
    #                           description: str,
    #                           requester: str | None) -> dict | None:
    #     finger_print = self._generate_fingerprint(title=title, description=description, requester=requester)

    #     for T in FAKE_TICKETS_DB:
    #         if T.get("fingerprint")==finger_print:
    #             return T
    #     return None
    async def commit(self):
        await self.session.commit()

    async def is_already_exist(
        self,
        title: str,
        description: str,
        requester: str | None,
    ) -> dict | None:

        if self.session is None:
            return None

        fingerprint = self._generate_fingerprint(
            title=title,
            description=description,
            requester=requester,
        )

        stmt = (
            select(TicketModel)
            .options(selectinload(TicketModel.analysis))
            .where(TicketModel.fingerprint == fingerprint)
        )

        result = await self.session.execute(stmt)

        ticket = result.scalar_one_or_none()

        if ticket is None:
            return None

        return self._to_dict(ticket, include_ai_details=True)






    
    
    # async def get_ticket(self, query: TicketQuery)-> dict | None:

    #     for T in FAKE_TICKETS_DB:
    #         if query.ticket_id is not None and T.get("ticket_id") != query.ticket_id:
    #             continue
    #         if query.requester is not None and T.get("requester") != query.requester:
    #             continue
    #         return T
    #         #TODO: پیاده سازی فیلتر جزئیات خروجی ai
    #     return None

    # async def get_tickets(self, ticket_ids= list[int]) -> list[dict]:
    #     ticket_list = []
    #     for T in FAKE_TICKETS_DB:
    #         if T.get("ticket_id") in ticket_ids:
    #             ticket_list.append(T)

    #     return ticket_list

    async def get_ticket(self, query: TicketQuery) -> dict | None:

        if self.session is None:
            return None

        stmt = (
            select(TicketModel)
            .outerjoin(
                TicketAnalysis,
                TicketAnalysis.ticket_id == TicketModel.id
            )
            .options(selectinload(TicketModel.analysis))
        )

        if query.ticket_id is not None:
            stmt = stmt.where(TicketModel.id == query.ticket_id)

        if query.requester is not None:
            stmt = stmt.where(
                TicketModel.requester_name == query.requester
            )

        if query.department is not None:
            stmt = stmt.where(
                TicketModel.department == query.department
            )

        if query.ticket_status is not None:
            stmt = stmt.where(
                TicketModel.ticket_status ==
                Ticket_Status(query.ticket_status.value)
            )

        if query.category is not None:
            stmt = stmt.where(
                func.lower(TicketAnalysis.category) ==
                query.category.lower()
            )

        if query.urgency is not None:
            if query.urgency == TicketUrgency.UNKNOWN:
                stmt = stmt.where(TicketAnalysis.urgency.is_(None))
            else:
                stmt = stmt.where(
                    TicketAnalysis.urgency ==
                    Urgency_Status(query.urgency.value)
                )

        if query.q is not None:
            search = f"%{query.q.strip()}%"

            stmt = stmt.where(
                or_(
                    TicketModel.title.ilike(search),
                    TicketModel.description.ilike(search),
                )
            )

        result = await self.session.execute(stmt.limit(1))

        ticket = result.scalar_one_or_none()

        if ticket is None:
            return None

        # برای جزئیات یک تیکت، AI را هم برمی‌گردانیم
        include_ai = (
            query.include_ai_details
            or (
                query.ticket_id is not None
                and not query.exclude_ai_details
            )
        )

        return self._to_dict(
            ticket,
            include_ai_details=include_ai
        )


    async def get_tickets(self, ticket_ids=list[int]) -> list[dict]:

        if self.session is None:
            return []

        stmt = (
            select(TicketModel)
            .options(selectinload(TicketModel.analysis))
            .where(TicketModel.id.in_(ticket_ids))
        )

        result = await self.session.execute(stmt)

        tickets = result.scalars().all()

        return [
            self._to_dict(ticket, include_ai_details=True)
            for ticket in tickets
        ]









        
        # async def save_new_ticket(self, title: str, 
        #                     description: str, 
        #                     requester: str | None, 
        #                     department: str | None,
        #                     analysis_status: AnalysisStatus = AnalysisStatus.PENDING) -> dict:
            
        #     # در آینده دیتابیس واقعی اینجا تزریق می‌شود:
        #     # def __init__(self, db_session): self.db = db_session
        #     global _id_counter

        #     FINGER_PRINT = self._generate_fingerprint(title=title, description=description, requester=requester)

        #     new_ticket = {
        #         "ticket_id": _id_counter,
        #         "title": title,
        #         "description": description,
        #         "requester": requester or "None",
        #         "department": department or "None",
        #         "ticket_status": TicketStatus.OPEN,
        #         "analysis_status": analysis_status,
        #         "source": "manual", #TODO: پیاده سازی این منطق
        #         "fingerprint": FINGER_PRINT,
        #         "created_at": datetime.now(tz=timezone.utc),
        #         "updated_at": datetime.now(tz=timezone.utc),
        #         "urgency": TicketUrgency.UNKNOWN,
        #         "category": "unknown",
        #         "category_label_fa": "نامشخص",
        #         "ai_analysis" : None
        #     }

        #     _id_counter+= 1
        #     FAKE_TICKETS_DB.append(new_ticket)

        #     return new_ticket
        # #TODO: نسخه اصلی متد ذخیره سازی بعد از اتصال دیتابیس
        #------------------
        # async def save_new_ticket(self, ...):
        #     fingerprint = self._generate_fingerprint(title, description, requester)
        #     new_ticket = TicketModel(
        #         title=title,
        #         description=description,
        #         requester=requester,
        #         department=department,
        #         analysis_status=analysis_status,
        #         fingerprint=fingerprint,
        #     )
        #     self.session.add(new_ticket)
        #     try:
        #         await self.session.flush()
        #     except IntegrityError as e:
        #         await self.session.rollback()
        #         if self._is_unique_violation(e):
        #             raise DuplicateTicketError() from e
        #         raise TicketPersistenceError() from e
        #     except SQLAlchemyError as e:
        #         await self.session.rollback()
        #         raise TicketPersistenceError() from e
        #     return self._to_dict(new_ticket)
        #
        # def _is_unique_violation(self, exc: IntegrityError) -> bool:
        #     msg = str(exc.orig).lower()
        #     return "unique" in msg or "duplicate" in msg

    async def save_new_ticket(
        self,
        title: str,
        description: str,
        requester: str | None,
        department: str | None,
        analysis_status: AnalysisStatus = AnalysisStatus.PENDING,
    ) -> dict:

        if self.session is None:
            raise TicketPersistenceError(
                "Database session is not available."
            )

        fingerprint = self._generate_fingerprint(
            title=title,
            description=description,
            requester=requester,
        )

        new_ticket = TicketModel(
            title=title,
            description=description,
            requester_name=requester,
            department=department,
            ticket_status=Ticket_Status.OPEN,
            analysis_status=Analysis_Status(analysis_status.value),
            source=Source_Status.MANUAL,
            fingerprint=fingerprint,
        )

        self.session.add(new_ticket)

        try:
            await self.session.flush()

        except IntegrityError as exc:
            await self.session.rollback()

            error_message = str(exc.orig).lower()

            if "fingerprint" in error_message or "unique" in error_message:
                raise DuplicateTicketError() from exc

            raise TicketPersistenceError() from exc

        except SQLAlchemyError as exc:
            await self.session.rollback()
            raise TicketPersistenceError() from exc

        return {
            "ticket_id": new_ticket.id,
            "title": new_ticket.title,
            "description": new_ticket.description,
            "requester": new_ticket.requester_name,
            "department": new_ticket.department,
            "ticket_status": new_ticket.ticket_status.value,
            "analysis_status": new_ticket.analysis_status.value,
            "source": new_ticket.source.value,
            "fingerprint": new_ticket.fingerprint,
            "created_at": new_ticket.created_at,
            "updated_at": new_ticket.updated_at,
            "ai_analysis": None,
        }






        
        # async def update_ticket_analysis(self, 
        #                           ticket_id: int, 
        #                           new_analysis_status: AnalysisStatus,
        #                           new_analysis_data: dict | None = None)-> None:
            
        #     for T in FAKE_TICKETS_DB:
        #         if T.get("ticket_id")== ticket_id:
        #             T["ai_analysis"] = new_analysis_data
        #             if new_analysis_data:
        #                 T["urgency"] = new_analysis_data.get("urgency", TicketUrgency.UNKNOWN)
        #                 T["category"] = new_analysis_data.get("category")
        #                 T["category_label_fa"] = new_analysis_data.get("category_label_fa")
        #             T["analysis_status"] = new_analysis_status
        #             T["updated_at"] = datetime.now(tz=timezone.utc)
        #             break


    async def update_ticket_analysis(
        self,
        ticket_id: int,
        new_analysis_status: AnalysisStatus,
        new_analysis_data: dict | None = None,
    ) -> None:

        if self.session is None:
            return

        stmt = (
            select(TicketModel)
            .options(selectinload(TicketModel.analysis))
            .where(TicketModel.id == ticket_id)
        )

        result = await self.session.execute(stmt)

        ticket = result.scalar_one_or_none()

        if ticket is None:
            return

        ticket.analysis_status = Analysis_Status(
            new_analysis_status.value
        )

        ticket.updated_at = func.now()

        if new_analysis_data is not None:

            analysis = ticket.analysis

            if analysis is None:
                analysis = TicketAnalysis(
                    ticket_id=ticket.id
                )
                self.session.add(analysis)

            analysis.category = new_analysis_data.get("category")
            analysis.category_label_fa = new_analysis_data.get(
                "category_label_fa"
            )
            analysis.category_score = new_analysis_data.get(
                "category_score"
            )

            analysis.intent = new_analysis_data.get("intent")
            analysis.intent_label_fa = new_analysis_data.get(
                "intent_label_fa"
            )

            urgency_value = new_analysis_data.get("urgency")

            if urgency_value:
                try:
                    analysis.urgency = Urgency_Status(
                        urgency_value
                    )
                except ValueError:
                    analysis.urgency = None
            else:
                analysis.urgency = None

            analysis.urgency_score = new_analysis_data.get(
                "urgency_score"
            )

            analysis.sentiment = new_analysis_data.get(
                "sentiment"
            )

            analysis.summary_fa = new_analysis_data.get(
                "summary_fa"
            )

            analysis.suggested_reply_fa = new_analysis_data.get(
                "suggested_reply_fa"
            )

            analysis.confidence = new_analysis_data.get(
                "confidence"
            )

            analysis.reasons_fa = new_analysis_data.get(
                "reasons_fa"
            )

            analysis.model_version = new_analysis_data.get(
                "model_version"
            )

            analysis.latency_ms = new_analysis_data.get(
                "latency_ms"
            )

            # فعلاً خود analysis response را به عنوان raw JSON ذخیره می‌کنیم
            analysis.raw_ai_response = new_analysis_data

        await self.session.flush()


        # async def update_ticket_status(self, ticket_id: int, new_status: TicketStatus)-> dict | None:
        #     for T in FAKE_TICKETS_DB:
        #         if T.get("ticket_id") == ticket_id:
        #             T["ticket_status"] = new_status
        #             return T
        #     return None

        # async def get_all_tickets(self) -> list[dict]:
        #     return copy.deepcopy(FAKE_TICKETS_DB)

    async def update_ticket_status(
        self,
        ticket_id: int,
        new_status: TicketStatus,
    ) -> dict | None:

        if self.session is None:
            return None

        stmt = (
            select(TicketModel)
            .options(selectinload(TicketModel.analysis))
            .where(TicketModel.id == ticket_id)
        )

        result = await self.session.execute(stmt)

        ticket = result.scalar_one_or_none()

        if ticket is None:
            return None

        ticket.ticket_status = Ticket_Status(
            new_status.value
        )

        await self.session.flush()

        return self._to_dict(
            ticket,
            include_ai_details=True
        )

    async def get_all_tickets(self) -> list[dict]:

        if self.session is None:
            return []

        stmt = (
            select(TicketModel)
            .options(selectinload(TicketModel.analysis))
            .order_by(TicketModel.created_at.desc())
        )

        result = await self.session.execute(stmt)

        tickets = result.scalars().all()

        return [
            self._to_dict(ticket, include_ai_details=True)
            for ticket in tickets
        ]


        # async def get_all(self,query: TicketQuery)-> tuple[list[dict], int]:
        #     #Hint: تمام پارامتر های قابل فیلتر اینجا بررسی نشده
        #     requester= query.requester
        #     department= query.department
        #     ticket_status= query.ticket_status
        #     limit = query.limit or 20
        #     offset = query.offset or 0

        #     #TODO: باز نویسی مجدد این متد با کوئری های استاندارد دیتابیس
        #     results = []
        #     total = 0
        #     for ticket in FAKE_TICKETS_DB:
        #         if requester and ticket.get("requester") != requester:
        #             continue
        #         if department and ticket.get("department") != department:
        #             continue
        #         if ticket_status and ticket.get("ticket_status") != ticket_status:
        #             continue
        #         results.append(ticket)
        #         total += 1

        #     return results[offset: offset + limit], total

    async def get_all(
        self,
        query: TicketQuery
    ) -> tuple[list[dict], int]:

        if self.session is None:
            return [], 0

        stmt = (
            select(TicketModel)
            .outerjoin(
                TicketAnalysis,
                TicketAnalysis.ticket_id == TicketModel.id
            )
            .options(selectinload(TicketModel.analysis))
        )

        count_stmt = (
            select(func.count(TicketModel.id))
            .select_from(TicketModel)
            .outerjoin(
                TicketAnalysis,
                TicketAnalysis.ticket_id == TicketModel.id
            )
        )

        conditions = []

        if query.requester is not None:
            conditions.append(
                TicketModel.requester_name == query.requester
            )

        if query.department is not None:
            conditions.append(
                TicketModel.department == query.department
            )

        if query.ticket_status is not None:
            conditions.append(
                TicketModel.ticket_status ==
                Ticket_Status(query.ticket_status.value)
            )

        if query.category is not None:
            conditions.append(
                func.lower(TicketAnalysis.category) ==
                query.category.lower()
            )

        if query.urgency is not None:

            if query.urgency == TicketUrgency.UNKNOWN:
                conditions.append(
                    TicketAnalysis.urgency.is_(None)
                )

            else:
                conditions.append(
                    TicketAnalysis.urgency ==
                    Urgency_Status(query.urgency.value)
                )

        if query.q is not None:

            search = f"%{query.q.strip()}%"

            conditions.append(
                or_(
                    TicketModel.title.ilike(search),
                    TicketModel.description.ilike(search),
                )
            )

        for condition in conditions:
            stmt = stmt.where(condition)
            count_stmt = count_stmt.where(condition)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = (
            stmt
            .order_by(TicketModel.created_at.desc())
            .offset(query.offset)
            .limit(query.limit)
        )

        result = await self.session.execute(stmt)

        tickets = result.scalars().all()

        items = [
            self._to_dict(
                ticket,
                include_ai_details=query.include_ai_details
                and not query.exclude_ai_details
            )
            for ticket in tickets
        ]

        return items, total

    # async def mark_as_pending(self, ticket_id: int)-> bool:
    #         """به صورت اتمیک وضعیت را به PENDING تغییر می‌دهد.
    #         اگر وضعیت قبلاً PENDING بود، False برمی‌گرداند."""
    #         #TODO: بعد از پیاده سازی واقعی دیتابیس
    #         # stmt = (
    #         #     update(TicketModel)
    #         #     .where(TicketModel.id == ticket_id)
    #         #     .where(TicketModel.analysis_status != AnalysisStatus.PENDING)
    #         #     .values(
    #         #         analysis_status=AnalysisStatus.PENDING,
    #         #         updated_at=func.now(),
    #         #     )
    #         # )
    #         # result = await self.session.execute(stmt)
    #         # await self.session.commit()
    #         # return result.rowcount == 1
    #         for T in FAKE_TICKETS_DB:
    #             if T.get("ticket_id") == ticket_id and T.get("analysis_status") != AnalysisStatus.PENDING:
    #                 T["analysis_status"] = AnalysisStatus.PENDING
    #                 return True
    #         return False

    async def mark_as_pending(
        self,
        ticket_id: int
    ) -> bool:

        if self.session is None:
            return False

        stmt = (
            update(TicketModel)
            .where(TicketModel.id == ticket_id)
            .where(
                TicketModel.analysis_status
                != Analysis_Status.PENDING
            )
            .values(
                analysis_status=Analysis_Status.PENDING,
                updated_at=func.now(),
            )
        )

        result = await self.session.execute(stmt)

        return result.rowcount == 1