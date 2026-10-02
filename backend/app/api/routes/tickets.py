from app.schemas.ticket import (
    TicketCreateRequest, TicketResponse, TicketList,
    AdminTicketResponse, TicketStatusUpdateRequest, AdminTicketList,
    AdminTicketFilter, UserTicketFilter
)
from app.services.ticket_service import TicketService
from app.core.dependencies import get_ticket_service, get_current_user
from fastapi import APIRouter, BackgroundTasks, status, Depends


router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_ticket(
    ticket_in: TicketCreateRequest,
    api_background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    auto_analyze: bool = True,
    ticket_service: TicketService = Depends(get_ticket_service),
):
    
    ticket_data = ticket_in.model_dump()
    ticket_data.update({"requester": "nobody", "department": "hell"})

    return await ticket_service.create_ticket(
        **ticket_data,
        background_tasks=api_background_tasks,
        auto_analyze=auto_analyze,
        # requester= current_user,
    )



@router.get("/", response_model=TicketList, status_code=status.HTTP_200_OK)
async def list_user_tickets(
        current_user: dict = Depends(get_current_user),   # current_user = Depends(get_current_user),  # بعد از پیاده‌سازی Auth
        filters: UserTicketFilter = Depends(UserTicketFilter),
        ticket_service: TicketService = Depends(get_ticket_service)

):
    """لیست تیکت‌های کاربر لاگین‌شده با حداقل جزئیات"""
    return await ticket_service.get_user_tickets(
        requester=str(current_user["user_id"]),
        filters=filters
    )




# --- اندپوینت کنسول ادمین ---
@router.get("/admin", response_model=AdminTicketList, status_code=status.HTTP_200_OK)
async def list_admin_tickets(
    # current_admin = Depends(get_current_admin), # اعتبارسنجی توکن ادمین
    filters: AdminTicketFilter = Depends(AdminTicketFilter),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """دریافت لیست آیتم از تیکت های ادمین"""
    return await ticket_service.get_admin_tickets(filters=filters)




@router.get("/{ticket_id}",response_model=TicketResponse, status_code=status.HTTP_200_OK) #
# async def get_user_ticket(ticket_id: int, requester: str, ticket_service: TicketService = Depends(get_ticket_service)):

#     return await ticket_service.get_user_ticket_detail(ticket_id=ticket_id, requester=requester)
async def get_user_ticket(
    ticket_id: int,
    current_user: dict = Depends(get_current_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    return await ticket_service.get_user_ticket_detail(
        ticket_id=ticket_id,
        requester=str(current_user["user_id"])
    )

@router.get("/admin/{ticket_id}",response_model=AdminTicketResponse, status_code=status.HTTP_200_OK)
async def get_admin_ticket(ticket_id: int, ticket_service: TicketService = Depends(get_ticket_service)):

    return await ticket_service.get_admin_ticket_detail(ticket_id=ticket_id)

    

@router.post("/import", status_code=status.HTTP_200_OK)
async def import_tickets_csv():
    return {"message": "tickets uploaded successfully"}

@router.post("/{ticket_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_ticket(ticket_id: int, background_tasks: BackgroundTasks, ticket_service: TicketService = Depends(get_ticket_service)):
    """اجرای دستی تحلیل روی تیکت"""
    return await ticket_service.manual_analyze_ticket(ticket_id=ticket_id,
                                                      background_task=background_tasks)

@router.patch("/{ticket_id}/status", response_model=AdminTicketResponse, status_code=status.HTTP_200_OK)
async def update_ticket_status(
        ticket_id: int,
        payload: TicketStatusUpdateRequest,
        ticket_service: TicketService = Depends(get_ticket_service)
):
    return await ticket_service.update_ticket_status(ticket_id=ticket_id, status=payload.status)