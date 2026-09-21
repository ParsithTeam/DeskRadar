from fastapi import APIRouter, HTTPException, status as http_status, Query, Depends
from pydantic import BaseModel

from app.schemas.incident import IncidentResponse, IncidentStatus, IncidentStatusUpdate, IncidentList, IncidentFilter
from app.core.dependencies import get_incident_service
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])

# (نکته: در نسخه نهایی و پس از اتصال دیتابیس، این موارد از طریق Depends و Dependency Injection در توابع تزریق می‌شوند)


class MockAIPayload(BaseModel):
    ticket_id: int
    category: str
    intelligence_data: dict

# @router.post("/test-trigger", response_model=IncidentResponse, status_code=http_status.HTTP_201_CREATED)
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


@router.get("/", response_model=IncidentList, status_code=http_status.HTTP_200_OK)
async def get_incidents(
        status: IncidentStatus | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        incident_service: IncidentService = Depends(get_incident_service),
):
    """
    دریافت لیست تمامی رخدادها
    با امکان فیلتر کردن بر اساس وضعیت (candidate, confirmed, resolved, dismissed)
    """
    filters = IncidentFilter(status=status, offset=offset, limit=limit)
    return await incident_service.get_all(filter=filters)


@router.get("/{incident_id}", response_model=IncidentResponse, status_code=http_status.HTTP_200_OK)
async def get_incident_detail(incident_id: int, incident_service: IncidentService = Depends(get_incident_service) ):
    """
    دریافت جزئیات یک رخداد خاص و تیکت‌های متصل به آن
    """
    return await incident_service.get_incident_by_id(incident_id)


@router.patch("/{incident_id}/status", response_model=IncidentResponse, status_code=http_status.HTTP_200_OK)
async def update_incident_status(
        incident_id: int,
        payload: IncidentStatusUpdate,
        incident_service: IncidentService = Depends(get_incident_service)
):
    return await incident_service.update_status(incident_id, payload)