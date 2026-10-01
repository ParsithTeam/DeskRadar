"""rename is_read to read, timeanddate defualt

Revision ID: 089bf761b869
Revises: 51178de9df31
Create Date: 2026-10-02 00:14:30.197346

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '089bf761b869'
down_revision: Union[str, Sequence[str], None] = '51178de9df31'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'alerts',
        'is_read',
        new_column_name='read',
    )


def downgrade() -> None:
    op.alter_column(
        'alerts',
        'read',
        new_column_name='is_read',
    )
