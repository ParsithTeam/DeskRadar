from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AlertSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(str, Enum):
    INCIDENT_CANDIDATE = "incident_candidate"
    URGENT_TICKET = "urgent_ticket"
    INCIDENT = "incident"
    TICKET = "ticket"
    ESCALATION = "escalation"
    # پشتیبانی از مقادیر قبلی برای سازگاری عقب‌رو
    SLA_RISK = "sla_risk"
    SAL_RISK = "sal_risk"


class AlertCreate(BaseModel):
    type: AlertType
    message: str
    severity: AlertSeverity = AlertSeverity.WARNING
    title: str | None = None
    ticket_id: int | None = None
    incident_id: int | None = None


class AlertResponse(AlertCreate):
    id: int = Field(default=0, description="شناسه اصلی هشدار")
    alert_id: int | None = Field(default=None, description="شناسه معادل جهت سازگاری با فرانت")
    is_read: bool = Field(default=False, description="وضعیت خوانده‌شده")
    read: bool = Field(default=False, description="فلگ معادل خوانده‌شده برای فرانت")
    assigned_admin_id: str | None = Field(default=None, description="شناسه ادمین مسئول")
    assigned_admin_name: str | None = Field(default=None, description="نام ادمین مسئول")
    created_at: datetime

    @model_validator(mode="after")
    def sync_id_and_read(self) -> "AlertResponse":
        # هماهنگ‌سازی id و alert_id برای جلوگیری از خطای ۵۰۰ در فرانت و تست‌ها
        if self.alert_id is None and self.id:
            self.alert_id = self.id
        elif self.id == 0 and self.alert_id is not None:
            self.id = self.alert_id

        # همگام‌سازی is_read و read
        if self.is_read:
            self.read = True
        elif self.read:
            self.is_read = True

        # در صورت نبود عنوان، بر اساس نوع پیام عنوانی پیش‌فرض تولید می‌شود
        if not self.title:
            if self.type in (AlertType.INCIDENT_CANDIDATE, AlertType.INCIDENT):
                self.title = "هشدار رخداد احتمالی"
            elif self.type in (AlertType.URGENT_TICKET, AlertType.TICKET):
                self.title = "هشدار تیکت با فوریت بالا"
            else:
                self.title = "اعلان سیستم"

        return self

    model_config = ConfigDict(from_attributes=True, extra="allow")