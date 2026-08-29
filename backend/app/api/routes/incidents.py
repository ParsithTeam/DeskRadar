from fastapi import APIRouter, HTTPException, status

from app.schemas.incident import IncidentResponse, IncidentStatus
from app.services.incident_service import IncidentService
from app.repositories.incident_repository import IncidentRepository
from app.services.alert_service import AlertService
from app.repositories.alert_repository import AlertRepository

router = APIRouter(prefix="/incidents", tags=["Incidents"])

# (نکته: در نسخه نهایی و پس از اتصال دیتابیس، این موارد از طریق Depends و Dependency Injection در توابع تزریق می‌شوند)
alert_repo = AlertRepository()
alert_service = AlertService(alert_repo)
incident_repo = IncidentRepository()
incident_service = IncidentService(incident_repo, alert_service)

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


@router.get("/", response_model=list[IncidentResponse], status_code=status.HTTP_200_OK)
async def get_incidents(status: IncidentStatus | None = None):
    """
    دریافت لیست تمامی رخدادها
    با امکان فیلتر کردن بر اساس وضعیت (candidate, confirmed, resolved, dismissed)
    """
    return await incident_service.get_all_incidents(status= status)


@router.get("/{incident_id}", response_model=IncidentResponse, status_code=status.HTTP_200_OK)
async def get_incident_detail(incident_id: int):
    """
    دریافت جزئیات یک رخداد خاص و تیکت‌های متصل به آن
    """
    incident = await incident_service.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.post("/{incident_id}/confirm", response_model=IncidentResponse, status_code=status.HTTP_200_OK)
async def confirm_incident(incident_id: int):
    """
    تأیید رخداد احتمالی توسط ادمین
    """
    incident = await incident_service.confirm_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.post("/{incident_id}/resolve", response_model=IncidentResponse, status_code=status.HTTP_200_OK)
async def resolve_incident(incident_id: int):
    """
    اعلام برطرف شدن رخداد توسط ادمین و ثبت زمان پایان
    """
    incident = await incident_service.resolve_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.post("/{incident_id}/dismiss", response_model=IncidentResponse, status_code=status.HTTP_200_OK)
async def dismiss_incident(incident_id: int):
    """
    رد کردن رخداد تشخیص داده شده توسط هوش مصنوعی (تشخیص نادرست)
    """
    incident = await incident_service.dismiss_incident(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident