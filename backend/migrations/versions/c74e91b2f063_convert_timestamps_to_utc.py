"""Convert application timestamps to timezone-aware UTC instants.

Revision ID: c74e91b2f063
Revises: ef9066b27d7c

IMPORTANT: This assumes existing timestamp-without-time-zone values are UTC.
If historical values were written in local time, reconcile those rows first.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c74e91b2f063"
down_revision: Union[str, Sequence[str], None] = "ef9066b27d7c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UTC_COLUMNS = {
    "alerts": ("created_at",),
    "feedback_ai": ("created_at",),
    "incidents": ("created_at", "updated_at", "resolved_at"),
    "knowledge_articles": ("created_at", "updated_at"),
    "tickets": ("created_at", "updated_at"),
    "ticket_analysis": ("created_at",),
}


def upgrade() -> None:
    for table, columns in UTC_COLUMNS.items():
        for column in columns:
            op.alter_column(
                table,
                column,
                existing_type=sa.DateTime(timezone=False),
                type_=sa.DateTime(timezone=True),
                postgresql_using=f'"{column}" AT TIME ZONE \'UTC\'',
                existing_nullable=(table == "incidents" and column == "resolved_at"),
            )


def downgrade() -> None:
    for table, columns in reversed(list(UTC_COLUMNS.items())):
        for column in columns:
            op.alter_column(
                table,
                column,
                existing_type=sa.DateTime(timezone=True),
                type_=sa.DateTime(timezone=False),
                postgresql_using=f'"{column}" AT TIME ZONE \'UTC\'',
                existing_nullable=(table == "incidents" and column == "resolved_at"),
            )
