"""fix analysis status enum values

Revision ID: 3424b4b6348c
Revises: YOUR_REVISION_ID
Create Date: 2026-09-06 18:33:25.635606

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3424b4b6348c'
down_revision: Union[str, Sequence[str], None] = '9e3ffc287508'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE analysis_status RENAME TO analysis_status_old")

    op.execute("""
        CREATE TYPE analysis_status AS ENUM (
            'pending',
            'complete',
            'failed'
        )
    """)

    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN analysis_status TYPE analysis_status
        USING lower(analysis_status::text)::analysis_status
    """)

    op.execute("DROP TYPE analysis_status_old")

def downgrade() -> None:
    op.execute("ALTER TYPE analysis_status RENAME TO analysis_status_old")

    op.execute("""
        CREATE TYPE analysis_status AS ENUM (
            'PENDING',
            'COMPLETED',
            'FAILED'
        )
    """)

    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN analysis_status TYPE analysis_status
        USING upper(analysis_status::text)::analysis_status
    """)

    op.execute("DROP TYPE analysis_status_old")