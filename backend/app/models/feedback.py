from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)

from app.core.database import Base


class Feedback(Base):
    __tablename__ = "feedback_ai"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    )

    rating = Column(
        Integer,
        nullable=True,
    )

    comment = Column(
        String,
        nullable=True,
    )

    feedback_type = Column(
        String(50),
        nullable=True,
    )

    corrected_category = Column(
        String(100),
        nullable=True,
    )

    corrected_urgency = Column(
        String(50),
        nullable=True,
    )

    correction_reason = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )