"""add waiting analysis status

Revision ID: 9cd0016173d6
Revises: bfe894bdd919
Create Date: 2026-09-22 23:16:22.406148

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cd0016173d6'
down_revision: Union[str, Sequence[str], None] = 'bfe894bdd919'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        "ALTER TYPE analysis_status ADD VALUE IF NOT EXISTS 'waiting' BEFORE 'pending'"
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
