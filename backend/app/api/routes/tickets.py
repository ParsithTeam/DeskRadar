from app.repositories.alert_repository import AlertRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreateRequest, TicketResponse, AdminTicketListItem, TicketStatus, TicketListItem, \
    AdminTicketResponse
from app.services.alert_service import AlertService
from app.services.analysis_service import AnalysisService
from app.services.incident_service import IncidentService
from app.services.ticket_service import TicketService
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Query

router = APIRouter(prefix="/tickets", tags=["Tickets"])

#---------------وابستگی های اولیه برای صرفا تست------------
alert_repo = AlertRepository()
alert_serv = AlertService(alert_repo=alert_repo)

incident_repo = IncidentRepository()
incident_serv = IncidentService(incident_repo, alert_serv)

ticket_repo = TicketRepository()
analysis_serv = AnalysisService()

ticket_service = TicketService(
    ticket_repo=ticket_repo,
    analysis_serv=analysis_serv,
    incident_serv=incident_serv
)

@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED) #ریکوئست ایجاد تیکت جدید
async def create_ticket(ticket_in: TicketCreateRequest, api_background_tasks: BackgroundTasks, auto_analyze: bool=True):
    
    try:

        response = await ticket_service.create_ticket(
            **ticket_in.model_dump(),
            background_tasks = api_background_tasks,
            auto_analyze= auto_analyze
            )
        return response

    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Unknow internal error occurred: {str(e)}"
        )

@router.get("/", response_model=list[TicketListItem], status_code=status.HTTP_200_OK)
async def list_user_tickets(
        current_user:str,   # current_user = Depends(get_current_user),  # بعد از پیاده‌سازی Auth
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0)
):
    """لیست تیکت‌های کاربر لاگین‌شده با حداقل جزئیات"""
    return await ticket_service.get_user_tickets(
        requester=current_user,
        limit=limit,
        offset=offset
    )

# --- اندپوینت کنسول ادمین ---
@router.get("/admin", response_model=list[AdminTicketListItem], status_code=status.HTTP_200_OK)
async def list_admin_tickets(
    # current_admin = Depends(get_current_admin), # اعتبارسنجی توکن ادمین
    department: str|None = None,
    ticket_status: TicketStatus|None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """دریافت لیست آیتم از تیکت های ادمین"""
    return await ticket_service.get_admin_tickets(
        department=department,
        ticket_status=ticket_status,
        limit=limit,
        offset=offset
    )

@router.get("/{ticket_id}",response_model=TicketResponse, status_code=status.HTTP_200_OK) #
async def get_user_ticket(ticket_id: int, requester: str):

    try:
        response = await ticket_service.get_user_ticket_detail(ticket_id=ticket_id, requester=requester)
        return response
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Unknow internal error occurred: {str(e)}"
        )

@router.get("/admin/{ticket_id}",response_model=AdminTicketResponse, status_code=status.HTTP_200_OK)
async def get_admin_ticket(ticket_id: int):
    return await ticket_service.get_admin_ticket_detail(ticket_id=ticket_id)

    

@router.post("/import", status_code=status.HTTP_200_OK)
async def import_tickets_csv():
    return {"message": "tickets uploaded successfully"}

@router.post("/{ticket_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_ticket_by_id(ticket_id: int, background_tasks: BackgroundTasks):
    """اجرای دستی تحلیل روی تیکت"""
    return await ticket_service.manual_analyze_ticket(ticket_id=ticket_id,
                                                      background_task=background_tasks)