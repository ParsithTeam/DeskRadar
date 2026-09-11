from pydantic import BaseModel
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
    ai_analysis: AdminAnalysisRead



class TicketUpdateRequest(BaseModel):

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class TicketListItem(BaseModel):
    ticket_id: int
    title: str
    created_at: datetime
    analysis_status: AnalysisStatus
    ticket_status: TicketStatus

class AdminTicketListItem(BaseModel):
    ticket_id: int

    title: str
    requester: str
    department: str

    analysis_status: AnalysisStatus
    ticket_status: TicketStatus
    created_at: datetime

    urgency: TicketUrgency