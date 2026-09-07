"""change ticket source to enum

Revision ID: bfe894bdd919
Revises: 81039210f964
Create Date: 2026-09-07 12:51:46.082326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfe894bdd919'
down_revision: Union[str, Sequence[str], None] = '81039210f964'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TYPE source_status AS ENUM (
            'manual',
            'csv'
        )
    """)

    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN source TYPE source_status
        USING lower(source)::source_status
    """)

def downgrade() -> None:
    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN source TYPE VARCHAR(20)
        USING source::text
    """)

    op.execute("""
        DROP TYPE source_status
    """)