from fastapi import APIRouter, HTTPException, status as http_status

from app.schemas.incident import IncidentResponse, IncidentStatus, IncidentStatusUpdate
from app.api.routes.tickets import incident_serv as incident_service

router = APIRouter(prefix="/incidents", tags=["Incidents"])

# (نکته: در نسخه نهایی و پس از اتصال دیتابیس، این موارد از طریق Depends و Dependency Injection در توابع تزریق می‌شوند)


# class MockAIPayload(BaseModel):
#     ticket_id: int
#     category: str
#     intelligence_data: dict
#
# @router.post("/test-trigger", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
# async def trigger_mock_incident(payload: MockAIPayload):
#     """
#     روت موقت برای شبیه‌سازی دریافت خروجی هوش مصنوعی و تست مستقل سرویس رخداد.
#     """
#     incident = await incident_service.upsert_from_ai(
#         ticket_id=payload.ticket_id,
#         category=payload.category,
#         intelligence_data=payload.intelligence_data
#     )
#     if not incident:
#         raise HTTPException(status_code=400, detail="Incident could not be created. Check your payload.")
#     return incident


@router.get("/", response_model=list[IncidentResponse], status_code=http_status.HTTP_200_OK)
async def get_incidents(status: IncidentStatus | None = None):
    """
    دریافت لیست تمامی رخدادها
    با امکان فیلتر کردن بر اساس وضعیت (candidate, confirmed, resolved, dismissed)
    """
    return await incident_service.get_all_incidents(status= status)


@router.get("/{incident_id}", response_model=IncidentResponse, status_code=http_status.HTTP_200_OK)
async def get_incident_detail(incident_id: int):
    """
    دریافت جزئیات یک رخداد خاص و تیکت‌های متصل به آن
    """
    incident = await incident_service.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident

@router.patch("/{incident_id}/satus", response_model=IncidentResponse, status_code=http_status.HTTP_200_OK)
async def update_incident_status(incident_id: int, payload: IncidentStatusUpdate):
    return await incident_service.update_incident_status(incident_id, payload.status)