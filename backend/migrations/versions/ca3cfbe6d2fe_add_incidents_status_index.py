"""add incidents status index

Revision ID: ca3cfbe6d2fe
Revises: d4ae88116902
Create Date: 2026-09-07 12:38:23.228995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca3cfbe6d2fe'
down_revision: Union[str, Sequence[str], None] = 'd4ae88116902'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_incidents_status",
        "incidents",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_incidents_status",
        table_name="incidents",
    )