from app.core.utc import utc_now

from sqlalchemy import Column, Integer, String, DateTime, JSON

from app.core.database import Base


class KnowledgeArticle(Base):
    __tablename__ = "knowledge_articles"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    title = Column(
        String(200),
        nullable=False,
    )

    content = Column(
        String,
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    tags = Column(
        JSON,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )