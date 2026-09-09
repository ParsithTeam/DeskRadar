from datetime import datetime


from app.schemas.ticket import AnalysisStatus, TicketStatus

from sqlalchemy.orm import relationship
from app.core.data_enum import Source_Status
from app.core.database import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Index

class TicketModel(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(150), nullable=False)
    description = Column(String, nullable=False)
    department = Column(String(100), nullable=True)
    requester_name = Column(String(100), nullable=True)


    ticket_status = Column(
    SQLEnum(
        TicketStatus,
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
    ),
    default=TicketStatus.OPEN,
    nullable=False,
    )

    analysis_status = Column(
    SQLEnum(
        AnalysisStatus,
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
    ),
    default=AnalysisStatus.PENDING,
    nullable=False,
    )

    # source = Column(String(20), default="manual", nullable=False) # manual یا csv
    source = Column(
    SQLEnum(
        Source_Status,
        values_callable=lambda enum_cls: [member.value for member in enum_cls],
    ),
    default=Source_Status.MANUAL,
    nullable=False,
    )
    fingerprint = Column(String(255), nullable=True, unique=True) # برای چلوگیری از ثبت تیکت تکراری
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

     # هر تیکت یه انالیز داره 
    analysis = relationship(  
    "TicketAnalysis",  
    back_populates="ticket",
    uselist=False,
    cascade="all, delete-orphan",
    )

    __table_args__ = (
    Index("ix_tickets_created_at", "created_at"),
    )