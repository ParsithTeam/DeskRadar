# from datetime import datetime


# class Incident:

#     def __init__(
#         self,
#         title: str,
#         description: str,
#         severity: str,
#         status: str = "open"
#     ):

#         self.title = title
#         self.description = description
#         self.severity = severity
#         self.status = status

#         self.created_at = datetime.now()
#         self.updated_at = datetime.now()


from datetime import datetime


from app.core.database import Base
from app.core.data_enum import Incident_Status

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum as SQLEnum,
    Index,
)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    title = Column(String(200), nullable=False)

    description = Column(
        String,
        nullable=True,
    )

    severity = Column(
        String(50),
        nullable=True,
    )

    status = Column(
        SQLEnum(Incident_Status),
        default=Incident_Status.CANDIDATE,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
    Index("ix_incidents_status", "status"),
    )