from app.core.data_enum import Analysis_Status, Ticket_Status
from app.repositories.ticket_repository import TicketRepository
from app.services.analysis_service import AnalysisService
from fastapi import BackgroundTasks, HTTPException, status


class TicketService:

    def __init__(self):

        self.ticket_repo = TicketRepository()
        self.analysis_serv = AnalysisService()
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
                title=ticket_data["title"],
                description=ticket_data["description"]
            )

        return ticket_data
    #تسک اجرای تحلیل هوش مصنوعی در پس زمنیه
    async def run_ai_analysis(self, ticket_id: int,
                              title: str,
                              description: str) -> None:
        
        try:
            ai_raw_response = await self.analysis_serv.analyze_ticket(ticket_id=ticket_id, title=title, description=description)
            analysis_payload = ai_raw_response.get("analysis")

            await self.ticket_repo.update_ticket_analysis(ticket_id=ticket_id,
                                                   new_analysis_status= Analysis_Status.COMPLETED,
                                                   new_analysis_data= analysis_payload )
            
            print(f"Updating analysis for ticket id: {ticket_id} completed.")

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
            

