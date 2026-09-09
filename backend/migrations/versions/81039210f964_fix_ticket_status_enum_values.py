"""fix ticket status enum values

Revision ID: 81039210f964
Revises: ca3cfbe6d2fe
Create Date: 2026-09-07 12:46:45.672808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81039210f964'
down_revision: Union[str, Sequence[str], None] = 'ca3cfbe6d2fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE ticket_status RENAME TO ticket_status_old")

    op.execute("""
        CREATE TYPE ticket_status AS ENUM (
            'in_progress',
            'open',
            'resolved',
            'closed'
        )
    """)

    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN ticket_status TYPE ticket_status
        USING lower(ticket_status::text)::ticket_status
    """)

    op.execute("DROP TYPE ticket_status_old")


def downgrade() -> None:
    op.execute("ALTER TYPE ticket_status RENAME TO ticket_status_old")

    op.execute("""
        CREATE TYPE ticket_status AS ENUM (
            'IN_PROGRESS',
            'OPEN',
            'RESOLVED',
            'CLOSED'
        )
    """)

    op.execute("""
        ALTER TABLE tickets
        ALTER COLUMN ticket_status TYPE ticket_status
        USING upper(ticket_status::text)::ticket_status
    """)

    op.execute("DROP TYPE ticket_status_old")