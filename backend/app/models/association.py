from sqlalchemy import (
    Table,
    Column,
    Integer,
    Float,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)

from app.core.database import Base


similarities_ticket = Table(
    "similarities_ticket",
    Base.metadata,

    Column(
        "source_ticket_id",
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    ),

    Column(
        "target_ticket_id",
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    ),

    Column(
        "similarity",
        Float,
        nullable=False,
    ),

    UniqueConstraint(
        "source_ticket_id",
        "target_ticket_id",
        name="uq_similarity_ticket_pair",
    ),

    CheckConstraint(
        "source_ticket_id <> target_ticket_id",
        name="ck_similarity_no_self_match",
    ),
)


tickets_incident = Table(
    "tickets_incident",
    Base.metadata,

    Column(
        "ticket_id",
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
    ),

    Column(
        "incident_id",
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    ),

    UniqueConstraint(
        "ticket_id",
        "incident_id",
        name="uq_ticket_incident_pair",
    ),
)