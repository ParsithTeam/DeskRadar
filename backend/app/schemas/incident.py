from pydantic import BaseModel, ConfigDict, Field
from enum import Enum
from  datetime import datetime

class IncidentStatus(str, Enum):
    CANDIDATE = "candidate"
    CONFIRMED = "confirmed"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentBase(BaseModel):
    title_fa: str
    reason_fa: str
    severity: SeverityLevel
    status: IncidentStatus = IncidentStatus.CANDIDATE

#------Output/Input Incident Schema-----
class IncidentCreate(IncidentBase):
    #Guide: اسکیمایی که توسط سرویس-رخداد استفاده میشه
    matched_ticket_ids: list[int] = Field(default_factory=list)
    #avg_similarity_score = float | None = None

class IncidentUpdate(BaseModel):
    """
    اسکیمایی که برای آپدیت وضعیت، شدت یا افزودن تیکت جدید به رخداد موجود استفاده می‌شود.
    تمام فیلدها اختیاری هستند تا فقط موارد لازم آپدیت شوند (Partial Update).
    """
    title_fa: str | None = None
    reason_fa: str | None = None
    severity: SeverityLevel | None = None
    status: IncidentStatus | None = None
    new_ticket_ids: list[int] | None = None
    resolved_at: datetime | None = None
    #avg_similarity_score: Optional[float] = None

class IncidentResponse(IncidentBase):
    #Guid: اسکیمای نهایی ارسال شده به فرانت
    id: int
    ticket_count: int
    matched_ticket_ids: list[int] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None = None

    # avg_similarity_score: Optional[float] = None

    # این تنظیم جایگزین class Config: orm_mode = True در Pydantic v2 است
    model_config = ConfigDict(from_attributes=True)