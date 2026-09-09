# from datetime import datetime


# class TicketAnalysis:

#     def __init__(
#         self,
#         category: str,
#         intent: str,
#         urgency: str,
#         summary: str,
#         reply: str,
#         confidence: float,
#         raw_ai_response: str
#     ):

#         self.category = category
#         self.intent = intent
#         self.urgency = urgency
#         self.summary = summary
#         self.reply = reply
#         self.confidence = confidence
#         self.raw_ai_response = raw_ai_response

#         self.created_at = datetime.now()


from datetime import datetime

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.data_enum import Urgency_Status

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey,
    Enum as SQLEnum,
    Index,
)

class TicketAnalysis(Base):
    __tablename__ = "ticket_analysis"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    category = Column(String(100), nullable=True)
    category_label_fa = Column(String(150), nullable=True)
    category_score = Column(Float, nullable=True)

    intent = Column(String(150), nullable=True)
    intent_label_fa = Column(String(150), nullable=True)

    urgency = Column(
        SQLEnum(Urgency_Status),
        nullable=True,
    )
    urgency_score = Column(Integer, nullable=True)

    sentiment = Column(String(100), nullable=True)

    summary_fa = Column(String, nullable=True)
    suggested_reply_fa = Column(String, nullable=True)

    confidence = Column(Float, nullable=True)

    reasons_fa = Column(JSONB, nullable=True)

    model_version = Column(String(100), nullable=True)
    latency_ms = Column(Integer, nullable=True)

    raw_ai_response = Column(JSONB, nullable=True)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    ticket = relationship(
        "TicketModel",
        back_populates="analysis",
    )

    __table_args__ = (
    Index("ix_ticket_analysis_category", "category"),
    Index("ix_ticket_analysis_urgency", "urgency"),
    )   