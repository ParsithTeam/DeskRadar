from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class AlertSeverity(str, Enum): # راهنمای ui در فرانت
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertType(str, Enum):
    INCIDENT_CANDIDATE = "incident_candidate"
    URGENT_TICKET = "urgent_ticket"
    SAL_RISK = "sal_risk"


class AlertCreate(BaseModel):
    type: AlertType
    message: str
    severity: AlertSeverity
    ticket_id: int | None = None
    incident_id: int | None = None


class AlertResponse(AlertCreate):
    id: int
    is_read: bool = False  # برای نمایش در صفحه نوتیفیکیشن‌ها
    created_at: datetime

    class Config:
        from_attributes = True