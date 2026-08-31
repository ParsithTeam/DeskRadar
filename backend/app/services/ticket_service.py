from app.core.data_enum import Analysis_Status, Ticket_Status
from app.repositories.incident_repository import IncidentRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.analysis_service import AnalysisService
from fastapi import BackgroundTasks, HTTPException, status

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
                status_code= status.HTTP_400_BAD_REQUEST,
                detail= "Ticket has already been submitted and it is in progress."
            )
        
        ticket_data = await self.ticket_repo.save_new_ticket(
            title=title,
            description=description,
            requester=requester,
            department=department
        )

        #ایجاد تسک در پس زمنیه برای ثبت خودکار خروجی تحلیل بخش 
        #Ai Core
        if auto_analyze:
            background_tasks.add_task(
                self.run_ai_analysis,
                ticket_id=ticket_data["ticket_id"],
            )

        return ticket_data

    #تسک اجرای تحلیل هوش مصنوعی در پس زمنیه
    async def run_ai_analysis(self, ticket_id: int) -> None:
        
        try:
            ticket = await self.ticket_repo.get_by_id(ticket_id)
            if not ticket:
                print(f"No ticket found for ticket id: {ticket_id}")
                return

            #اعتبار سنجی فیلد های استخراج شده
            title: str = ticket.get("title", "")
            description: str = ticket.get("description", "")

            if not title.strip() or not description.strip():
                print(f"Invalid content for ticket id: {ticket_id}. Aborting analysis.")
                await self.ticket_repo.update_ticket_analysis(
                    ticket_id=ticket_id,
                    new_analysis_status=Analysis_Status.FAILED
                    )
                return

            #TODO: پیاده سازی این دو متد
            old_tickets = await self.ticket_repo.get_recent_tickets(days=2) if hasattr(self.ticket_repo,
                                                                                            "get_recent_tickets") else []
            open_incidents = await self.incident_serv.get_open_incidents() if hasattr(self.incident_serv,
                                                                                      "get_open_incidents") else []


            ai_raw_response = await self.analysis_serv.analyze_ticket(ticket_id=ticket_id,
                                                                      title=title,
                                                                      category= ticket.get("category", "unknown"),
                                                                      description=description,
                                                                      old_tickets=old_tickets,
                                                                      open_incident=open_incidents)
            if not ai_raw_response:
                await self.ticket_repo.update_ticket_analysis(ticket_id=ticket_id, new_analysis_status=Analysis_Status.FAILED)
                return

            analysis_data = ai_raw_response.get("analysis", {})
            intelligence_data = ai_raw_response.get("intelligence", {})
            category = analysis_data.get("category", "unknown")

            await self.ticket_repo.update_ticket_analysis(ticket_id=ticket_id,
                                                   new_analysis_status= Analysis_Status.COMPLETED,
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
                new_analysis_status=Analysis_Status.FAILED
            )
            print(f"Background analysis failed for ticket {ticket_id}: {str(e)}")


    async def get_ticket_by_id(self, ticket_id: int ) -> dict:
            
            target_ticket = await self.ticket_repo.get_by_id(target_ticket_id= ticket_id)

            if target_ticket is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ticket Not found."
                )

            return target_ticket
            

