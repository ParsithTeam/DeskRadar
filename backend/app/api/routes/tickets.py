from app.schemas.ticket import (
    TicketCreateRequest, TicketResponse, TicketList,
    AdminTicketResponse, TicketStatusUpdateRequest, AdminTicketList,
    AdminTicketFilter, UserTicketFilter
)
from app.services.ticket_service import TicketService
from fastapi import APIRouter, BackgroundTasks, status, Depends


router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED) #ریکوئست ایجاد تیکت جدید
async def create_ticket(
        ticket_in: TicketCreateRequest,
        api_background_tasks: BackgroundTasks,
        auto_analyze: bool=True,
        ticket_service: TicketService = Depends(TicketService),
):
    return await ticket_service.create_ticket(
            **ticket_in.model_dump(),
            background_tasks = api_background_tasks,
            auto_analyze= auto_analyze
    )



@router.get("/", response_model=TicketList, status_code=status.HTTP_200_OK)
async def list_user_tickets(
        current_user:str,   # current_user = Depends(get_current_user),  # بعد از پیاده‌سازی Auth
        filters: UserTicketFilter = Depends(UserTicketFilter),
        ticket_service: TicketService = Depends(TicketService)

):
    """لیست تیکت‌های کاربر لاگین‌شده با حداقل جزئیات"""
    return await ticket_service.get_user_tickets(
        requester=current_user,
        filters=filters
    )

# --- اندپوینت کنسول ادمین ---
@router.get("/admin", response_model=AdminTicketList, status_code=status.HTTP_200_OK)
async def list_admin_tickets(
    # current_admin = Depends(get_current_admin), # اعتبارسنجی توکن ادمین
    filters: AdminTicketFilter = Depends(AdminTicketFilter),
    ticket_service: TicketService = Depends(TicketService)
):
    """دریافت لیست آیتم از تیکت های ادمین"""
    return await ticket_service.get_admin_tickets(filters=filters)

@router.get("/{ticket_id}",response_model=TicketResponse, status_code=status.HTTP_200_OK) #
async def get_user_ticket(ticket_id: int, requester: str, ticket_service: TicketService = Depends(TicketService)):

    return await ticket_service.get_user_ticket_detail(ticket_id=ticket_id, requester=requester)


@router.get("/admin/{ticket_id}",response_model=AdminTicketResponse, status_code=status.HTTP_200_OK)
async def get_admin_ticket(ticket_id: int, ticket_service: TicketService = Depends(TicketService)):

    return await ticket_service.get_admin_ticket_detail(ticket_id=ticket_id)

    

@router.post("/import", status_code=status.HTTP_200_OK)
async def import_tickets_csv():
    return {"message": "tickets uploaded successfully"}

@router.post("/{ticket_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_ticket(ticket_id: int, background_tasks: BackgroundTasks, ticket_service: TicketService = Depends(TicketService)):
    """اجرای دستی تحلیل روی تیکت"""
    return await ticket_service.manual_analyze_ticket(ticket_id=ticket_id,
                                                      background_task=background_tasks)

@router.patch("/{ticket_id}/status", response_model=AdminTicketResponse, status_code=status.HTTP_200_OK)
async def update_ticket_status(
        ticket_id: int,
        payload: TicketStatusUpdateRequest,
        ticket_service: TicketService = Depends(TicketService)
):
    return await ticket_service.update_ticket_status(ticket_id=ticket_id, status=payload.status)