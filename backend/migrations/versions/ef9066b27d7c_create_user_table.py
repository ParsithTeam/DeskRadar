"""Create user table

Revision ID: ef9066b27d7c
Revises: 29192162ce32
Create Date: 2026-10-05 14:26:31.318173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ef9066b27d7c'
down_revision: Union[str, Sequence[str], None] = '29192162ce32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'users',

        sa.Column(
            'user_id',
            sa.Integer(),
            autoincrement=True,
            nullable=False
        ),

        sa.Column(
            'email',
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            'name',
            sa.String(length=100),
            nullable=False
        ),

        sa.Column(
            'hashed_password',
            sa.String(length=255),
            nullable=False
        ),

        sa.Column(
            'department',
            sa.String(length=100),
            nullable=True
        ),

        sa.Column(
            'role',
            sa.Enum(
                'admin',
                'user',
                name='user_role'
            ),
            nullable=False,
            server_default='user'
        ),

        sa.Column(
            'disabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false()
        ),

        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email'),
    )