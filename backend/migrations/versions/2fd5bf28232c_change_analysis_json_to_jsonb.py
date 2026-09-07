"""change analysis json to jsonb

Revision ID: 2fd5bf28232c
Revises: 3424b4b6348c
Create Date: 2026-09-07 12:23:06.045095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2fd5bf28232c'
down_revision: Union[str, Sequence[str], None] = '3424b4b6348c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.alter_column(
        "ticket_analysis",
        "reasons_fa",
        existing_type=sa.JSON(),
        type_=postgresql.JSONB(),
        existing_nullable=True,
        postgresql_using="reasons_fa::jsonb",
    )

    op.alter_column(
        "ticket_analysis",
        "raw_ai_response",
        existing_type=sa.JSON(),
        type_=postgresql.JSONB(),
        existing_nullable=True,
        postgresql_using="raw_ai_response::jsonb",
    )


def downgrade() -> None:
    op.alter_column(
        "ticket_analysis",
        "reasons_fa",
        existing_type=postgresql.JSONB(),
        type_=sa.JSON(),
        existing_nullable=True,
        postgresql_using="reasons_fa::json",
    )

    op.alter_column(
        "ticket_analysis",
        "raw_ai_response",
        existing_type=postgresql.JSONB(),
        type_=sa.JSON(),
        existing_nullable=True,
        postgresql_using="raw_ai_response::json",
    )