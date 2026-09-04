from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.analysis import Ai_Analysis
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING   = "pending"
    COMPLETED = "complete"
    FAILED    = "failed"

class TicketStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    OPEN        = "open"
    RESOLVED    = "resolved"
    CLOSED      = "closed"


class TicketCreateRequest(BaseModel):

    title: str
    description: str
    requester: Optional[str] = None
    department: Optional[str] = None


class TicketResponse(BaseModel):

    ticket_id: int
    title: str
    description: str
    requester: str
    department: str
    analysis_status: AnalysisStatus = AnalysisStatus.PENDING
    ticket_status: TicketStatus = TicketStatus.OPEN
    created_at: datetime

    ai_analysis: Optional[Ai_Analysis] = None


class TicketUpdateRequest(BaseModel):

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None