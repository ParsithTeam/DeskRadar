from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)

from app.core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    type = Column(
        String(50),
        nullable=False,
    )

    message = Column(
        String,
        nullable=False,
    )

    severity = Column(
        String(50),
        nullable=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=True,
    )

    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=True,
    )

    urgent_ticket = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    incident_candidate = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    sla_risk = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )