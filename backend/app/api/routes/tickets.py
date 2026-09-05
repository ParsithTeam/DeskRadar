from app.repositories.alert_repository import AlertRepository
from app.repositories.incident_repository import IncidentRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreateRequest, TicketResponse
from app.services.alert_service import AlertService
from app.services.analysis_service import AnalysisService
from app.services.incident_service import IncidentService
from app.services.ticket_service import TicketService
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

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
        return response;

    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Unknow internal error occurred: {str(e)}"
        )


@router.get("/", status_code=status.HTTP_200_OK) #//TODO: ریکوئست دریافت لیست تیکت ها با فیلتر
async def get_all_tickets():
    return ["t1", "t2", "t3"]


@router.get("/{ticket_id}",response_model=TicketResponse, status_code=status.HTTP_200_OK) # //TODO: ریکوئست دریافت پاسخ یک تیکت خاص
async def get_ticket_detail(ticket_id: int):

    try:
        response = await ticket_service.get_ticket_by_id(ticket_id=ticket_id)
        return response
    
    except HTTPException as http_ex:
        raise http_ex
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= f"Unknow internal error occurred: {str(e)}"
        )

    
    

@router.post("/import", status_code=status.HTTP_200_OK)
async def import_tickets_csv():
    return {"message": "tickets uploaded successfully"}

@router.post("/{ticket_id}/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze_ticket_by_id(ticket_id: int, background_tasks: BackgroundTasks):
    """اجرای دستی تحلیل روی تیکت"""
    return await ticket_service.manual_analyze_ticket(ticket_id=ticket_id,
                                                      background_task=background_tasks)