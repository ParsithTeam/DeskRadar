from pydantic import BaseModel, Field

from app.schemas.ticket import TicketStatus, TicketUrgency

class TicketQuery(BaseModel):
    ticket_id: int | None = None
    requester: str | None = None
    category: str | None = None
    department: str | None = None
    ticket_status: TicketStatus | None = None
    urgency: TicketUrgency | None = None
    q: str | None = None

    # کنترل حجم دیتای واکشی‌شده
    include_ai_details: bool = False

    # صفحه‌بندی
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    exclude_ai_details: bool = False
