import copy
import hashlib
from datetime import datetime, timezone

from app.repositories.querise.ticket_querise import TicketQuery
from app.schemas.ticket import AnalysisStatus, TicketStatus, TicketUrgency

#-----------------------------------------
#from app.models.ticket import TicketModel   //TODO:بعد از اتصال دیتا بیس از این مدل واقعی استفاده میکنیم
#-----------------------------------------

FAKE_TICKETS_DB :list[dict] = []
_id_counter = 777

class TicketRepository:
    # ساخت اثر انگشت مخصوص، بعدا بنظرم بهتهره زمان هم به متد هش اضافه کرد
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
    
    async def is_already_exist(self, title: str,
                              description: str,
                              requester: str | None) -> dict | None:
        finger_print = self._generate_fingerprint(title=title, description=description, requester=requester)

        for T in FAKE_TICKETS_DB:
            if T.get("fingerprint")==finger_print:
                return T
        return None
    
    async def get_ticket(self, query: TicketQuery)-> dict | None:

        for T in FAKE_TICKETS_DB:
            if query.ticket_id is not None and T.get("ticket_id") != query.ticket_id:
                continue
            if query.requester is not None and T.get("requester") != query.requester:
                continue
            return T
            #TODO: پیاده سازی فیلتر جزئیات خروجی ai
        return None

    async def get_tickets(self, ticket_ids= list[int]) -> list[dict]:
        ticket_list = []
        for T in FAKE_TICKETS_DB:
            if T.get("ticket_id") in ticket_ids:
                ticket_list.append(T)

        return ticket_list

    
    async def save_new_ticket(self, title: str, 
                        description: str, 
                        requester: str | None, 
                        department: str | None,
                        analysis_status: AnalysisStatus = AnalysisStatus.PENDING) -> dict:
        
        # در آینده دیتابیس واقعی اینجا تزریق می‌شود:
        # def __init__(self, db_session): self.db = db_session
        global _id_counter

        FINGER_PRINT = self._generate_fingerprint(title=title, description=description, requester=requester)

        new_ticket = {
            "ticket_id": _id_counter,
            "title": title,
            "description": description,
            "requester": requester or "None",
            "department": department or "None",
            "ticket_status": TicketStatus.OPEN,
            "analysis_status": analysis_status,
            "source": "manual", #TODO: پیاده سازی این منطق
            "fingerprint": FINGER_PRINT,
            "created_at": datetime.now(tz=timezone.utc),
            "updated_at": datetime.now(tz=timezone.utc),
            "urgency": TicketUrgency.UNKNOWN,
            "category": "unknown",
            "category_label_fa": "نامشخص",
            "ai_analysis" : None
        }

        _id_counter+= 1
        FAKE_TICKETS_DB.append(new_ticket)

        return new_ticket
    #TODO: نسخه اصلی متد ذخیره سازی بعد از اتصال دیتابیس
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
    
    async def update_ticket_analysis(self, 
                              ticket_id: int, 
                              new_analysis_status: AnalysisStatus,
                              new_analysis_data: dict | None = None)-> None:
        
        for T in FAKE_TICKETS_DB:
            if T.get("ticket_id")== ticket_id:
                T["ai_analysis"] = new_analysis_data
                if new_analysis_data:
                    T["urgency"] = new_analysis_data.get("urgency", TicketUrgency.UNKNOWN)
                    T["category"] = new_analysis_data.get("category")
                    T["category_label_fa"] = new_analysis_data.get("category_label_fa")
                T["analysis_status"] = new_analysis_status
                T["updated_at"] = datetime.now(tz=timezone.utc)
                break

    async def update_ticket_status(self, ticket_id: int, new_status: TicketStatus)-> dict | None:
        for T in FAKE_TICKETS_DB:
            if T.get("ticket_id") == ticket_id:
                T["ticket_status"] = new_status
                return T
        return None

    async def get_all_tickets(self) -> list[dict]:
        return copy.deepcopy(FAKE_TICKETS_DB)

    async def get_all(self,query: TicketQuery)-> tuple[list[dict], int]:
        #Hint: تمام پارامتر های قابل فیلتر اینجا بررسی نشده
        requester= query.requester
        department= query.department
        ticket_status= query.ticket_status
        limit = query.limit or 20
        offset = query.offset or 0

        #TODO: باز نویسی مجدد این متد با کوئری های استاندارد دیتابیس
        results = []
        total = 0
        for ticket in FAKE_TICKETS_DB:
            if requester and ticket.get("requester") != requester:
                continue
            if department and ticket.get("department") != department:
                continue
            if ticket_status and ticket.get("ticket_status") != ticket_status:
                continue
            results.append(ticket)
            total += 1

        return results[offset: offset + limit], total

    async def mark_as_pending(self, ticket_id: int)-> bool:
        """به صورت اتمیک وضعیت را به PENDING تغییر می‌دهد.
        اگر وضعیت قبلاً PENDING بود، False برمی‌گرداند."""
        #TODO: بعد از پیاده سازی واقعی دیتابیس
        # stmt = (
        #     update(TicketModel)
        #     .where(TicketModel.id == ticket_id)
        #     .where(TicketModel.analysis_status != AnalysisStatus.PENDING)
        #     .values(
        #         analysis_status=AnalysisStatus.PENDING,
        #         updated_at=func.now(),
        #     )
        # )
        # result = await self.session.execute(stmt)
        # await self.session.commit()
        # return result.rowcount == 1
        for T in FAKE_TICKETS_DB:
            if T.get("ticket_id") == ticket_id and T.get("analysis_status") != AnalysisStatus.PENDING:
                T["analysis_status"] = AnalysisStatus.PENDING
                return True
        return False

