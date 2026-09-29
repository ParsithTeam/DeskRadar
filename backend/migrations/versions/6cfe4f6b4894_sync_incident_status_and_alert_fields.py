"""sync incident status and alert fields

Revision ID: 6cfe4f6b4894
Revises: 9cd0016173d6
Create Date: 2026-09-22 23:36:05.062071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6cfe4f6b4894'
down_revision: Union[str, Sequence[str], None] = '9cd0016173d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        "ALTER TYPE incident_status ADD VALUE IF NOT EXISTS 'DISMISSED'"
    )

    op.add_column(
        "alerts",
        sa.Column(
            "assigned_admin_id",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "alerts",
        sa.Column(
            "assigned_admin_name",
            sa.String(length=100),
            nullable=True,
        ),
    )

def downgrade() -> None:
    op.drop_column("alerts", "assigned_admin_name")
    op.drop_column("alerts", "assigned_admin_id")
    pass