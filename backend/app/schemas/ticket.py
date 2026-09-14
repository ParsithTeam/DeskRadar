from fastapi import Query
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.analysis import AnalysisRead, AdminAnalysisRead
from enum import Enum

class AnalysisStatus(str, Enum):
    WAITING = "waiting"
    PENDING   = "pending"
    COMPLETED = "complete"
    FAILED    = "failed"

class TicketStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    OPEN        = "open"
    RESOLVED    = "resolved"
    CLOSED      = "closed"

class TicketUrgency(str, Enum):
    UNKNOWN = "unknown"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCreateRequest(BaseModel):

    title: str
    description: str
    requester: Optional[str] = None
    department: Optional[str] = None


class TicketResponse(BaseModel):

    ticket_id: int
    title: str
    description: str
    requester: str | None
    department: str | None
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING
    ticket_status: TicketStatus = TicketStatus.OPEN
    created_at: datetime

    ai_analysis: AnalysisRead | None = None

class AdminTicketResponse(TicketResponse):
    ai_analysis: AdminAnalysisRead | None = None



class TicketUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TicketStatus | None = None

class TicketStatusUpdateRequest(BaseModel):
    status: TicketStatus

class TicketListItem(BaseModel):
    ticket_id: int
    title: str
    created_at: datetime
    analysis_status: AnalysisStatus
    ticket_status: TicketStatus

    model_config = ConfigDict(from_attributes=True)

class AdminTicketListItem(BaseModel):
    ticket_id: int

    title: str
    requester: str
    department: str

    analysis_status: AnalysisStatus
    ticket_status: TicketStatus
    created_at: datetime

    urgency: TicketUrgency

class TicketList(BaseModel):
    items: list[TicketListItem]
    total: int = Field(ge=0)

class AdminTicketList(TicketList):
    items: list[AdminTicketListItem]

#------------- Filter Schemas ------------
class TicketFilterParams(BaseModel):
    q: str | None = Query(None, description="Search term for title/desc")
    category: str | None = Query(None)
    department: str | None = Query(None, min_length=1, max_length=100)
    urgency: TicketUrgency | None = Query(None)
    ticket_status: TicketStatus | None = Query(None)
    limit: int = Query(20, ge=1, le=100)
    offset: int = Query(0, ge=0)