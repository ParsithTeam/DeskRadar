"""add ticket analysis urgency index

Revision ID: d4ae88116902
Revises: 3104d4ae791f
Create Date: 2026-09-07 12:36:11.235285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4ae88116902'
down_revision: Union[str, Sequence[str], None] = '3104d4ae791f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index(
        "ix_ticket_analysis_urgency",
        "ticket_analysis",
        ["urgency"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ticket_analysis_urgency",
        table_name="ticket_analysis",
    )