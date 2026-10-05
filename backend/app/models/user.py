from app.schemas.user import Role as UserRole
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Enum as SQLEnum,
)
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    department: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.USER
    )

    disabled: Mapped[bool] = mapped_column(
        Boolean,
        default= False,
    )