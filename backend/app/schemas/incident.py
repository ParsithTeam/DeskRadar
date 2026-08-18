from pydantic import BaseModel
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

class IncidentBase(BaseModel):
    title_fa: str
    reason_fa: str
    severity: SeverityLevel
    status: IncidentStatus = IncidentStatus.CANDIDATE

#------Output/Input Incident Schema-----
class IncidentCreate(IncidentBase):
    matched_ticket_ids: list[int]

class IncidentResponse(IncidentBase):
    id: int
    matched_ticket_ids: list[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True