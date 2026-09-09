"""add ticket analysis category index

Revision ID: 3104d4ae791f
Revises: 7876be2faa54
Create Date: 2026-09-07 12:34:07.235742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3104d4ae791f'
down_revision: Union[str, Sequence[str], None] = '7876be2faa54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index(
        "ix_ticket_analysis_category",
        "ticket_analysis",
        ["category"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_ticket_analysis_category",
        table_name="ticket_analysis",
    )