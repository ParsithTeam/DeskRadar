"""add ticket created at index

Revision ID: 7876be2faa54
Revises: 2fd5bf28232c
Create Date: 2026-09-07 12:28:37.898367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7876be2faa54'
down_revision: Union[str, Sequence[str], None] = '2fd5bf28232c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_tickets_created_at",
        "tickets",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tickets_created_at",
        table_name="tickets",
    )