from typing import Tuple

from app.schemas.ticket import AnalysisStatus, TicketStatus
from app.repositories.ticket_repository import TicketRepository
from app.services.analysis_service import AnalysisService
from fastapi import BackgroundTasks, HTTPException, status as http_status

from app.services.incident_service import IncidentService


class TicketService:

    def __init__(self, ticket_repo: TicketRepository,
                 analysis_serv: AnalysisService,
                 incident_serv: IncidentService) -> None:

        self.ticket_repo = ticket_repo
        self.analysis_serv = analysis_serv
        self.incident_serv = incident_serv
    # ثبت تیکت جدید
    async def create_ticket(
        self, 
        title: str, 
        description: str, 
        requester: str | None, 
        department: str | None, 
        background_tasks: BackgroundTasks,
        auto_analyze: bool = True
    ) -> dict:
        
        already_exist = await self.ticket_repo.is_already_exist(title=title, description=description, requester=requester)
        
        if already_exist:
            raise HTTPException(
                status_code= http_status.HTTP_400_BAD_REQUEST,
                detail= "Ticket has already been submitted and it is in progress."
            )

        #ذخیره اولیه تیکت با وضعیت های:
        #ticket status: OPEN
        #analysis status: WAITING
        created_ticket = await self.ticket_repo.save_new_ticket(
            title=title,
            description=description,
            requester=requester,
            department=department,

            analysis_status= AnalysisStatus.PENDING if auto_analyze else AnalysisStatus.WAITING
        )

        #ایجاد تسک در پس زمنیه برای ثبت خودکار خروجی تحلیل بخش 
        #Ai Core
        if auto_analyze:
            background_tasks.add_task(
                self.process_ticket_analyze,
                ticket_id=created_ticket["ticket_id"],
            )

        return created_ticket

    # async def process_ticket(self, ticket_id: int):

    #تسک اجرای تحلیل هوش مصنوعی در پس زمنیه
    async def process_ticket_analyze(self, ticket_id: int) -> None:
        
        try:
            ticket, is_valid = await self._fetch_and_validate_ticket(ticket_id)
            if not is_valid: return

            #ااستخراج فیلد های لازم برای ارسال به ai core
            context = await self._gather_ai_context()

            ai_raw_response = await self.analysis_serv.analyze_ticket(ticket_id=ticket_id,
                                                                      title=ticket.get("title", ""),
                                                                      category= ticket.get("category", "unknown"),
                                                                      description=ticket.get("description", ""),
                                                                      old_tickets=context["old_tickets"],
                                                                      open_incidents=context["open_incidents"])
            if not ai_raw_response:
                raise Exception(f"AI Core returned an empty response for ticket {ticket_id}")

            analysis_data = ai_raw_response.get("analysis", {})
            intelligence_data = ai_raw_response.get("intelligence", {})
            category = analysis_data.get("category", "unknown")

            await self.ticket_repo.update_ticket_analysis(ticket_id=ticket_id,
                                                   new_analysis_status= AnalysisStatus.COMPLETED,
                                                   new_analysis_data= analysis_data )
            
            print(f"Updating analysis for ticket id: {ticket_id} completed.")

            if intelligence_data:
                await self.incident_serv.upsert_from_ai(
                    ticket_id=ticket_id,
                    category=category,
                    intelligence_data=intelligence_data
                )

        except Exception as e:
            await self.ticket_repo.update_ticket_analysis(
                ticket_id=ticket_id,
                new_analysis_status=AnalysisStatus.FAILED
            )
            print(f"Background analysis failed for ticket {ticket_id}: {str(e)}")

    #---------- helper methods for process_ticket_analyze ----------
    async def _fetch_and_validate_ticket(self, ticket_id: int) -> Tuple[dict|None, bool]:
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            print(f"No ticket found for ticket id: {ticket_id}")
            return None, False

        title = ticket.get("title", "").strip()
        description = ticket.get("description", "").strip()

        if not title or not description:
            raise Exception(f"Invalid text content for ticket id: {ticket_id}. Aborting.")

        return ticket, True

    async def _gather_ai_context(self) -> dict[str, list[dict]]:
        """تجمیع داده‌های جانبی برای دقیق‌تر شدن تصمیم‌گیری مدل هوش مصنوعی"""
        #TODO: پیاده سازی این متد ها در لایه ریپازیتوری
        old_tickets = (
            await self.ticket_repo.get_recent_tickets(days=2)
            if hasattr(self.ticket_repo, "get_recent_tickets")
            else []
        )
        open_incidents = (
            await self.incident_serv.get_open_incidents()
            if hasattr(self.incident_serv, "get_open_incidents")
            else []
        )
        return {
            "old_tickets": old_tickets,
            "open_incidents": open_incidents
        }
    #------------------------------------------------------------------

    async def manual_analyze_ticket(self, ticket_id:int, background_task:BackgroundTasks ) -> dict:
        # بررسی وجود تیکت
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Ticket {ticket_id} not found."
            )

        #بررسی وضعیت تحلیل فعلی تیکت برای جلوگیری از تحلیل همزمان
        if ticket.get("analysis_status") == AnalysisStatus.PENDING:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail=f"Ticket {ticket_id} already has been in progress."
            )

        await self.ticket_repo.update_ticket_analysis(ticket_id=ticket_id,
                                                      new_analysis_status=AnalysisStatus.PENDING)
        #اضافه کردن تسک پس زمینه
        background_task.add_task(self.process_ticket_analyze, ticket_id=ticket_id)
        #TODO: ین بخش بعدا یک شی از نوع آیتم نمایشی در لیست برگردونه
        return {"analysis_status":AnalysisStatus.PENDING, "ticket_status": TicketStatus.OPEN, ticket_id:ticket_id}



    async def get_ticket_by_id(self, ticket_id: int ) -> dict:
            
            target_ticket = await self.ticket_repo.get_by_id(target_ticket_id= ticket_id)

            if target_ticket is None:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Ticket Not found."
                )

            return target_ticket
            

