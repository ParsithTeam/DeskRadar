from pydantic import BaseModel

from app.schemas.ticket import TicketStatus


class TicketQuery(BaseModel):
    ticket_id: int | None = None
    requester: str | None = None
    department: str | None = None
    ticket_status: TicketStatus | None = None

    # کنترل حجم دیتای واکشی‌شده
    include_ai_details: bool = False

    # صفحه‌بندی
    limit: int = 20
    offset: int = 0