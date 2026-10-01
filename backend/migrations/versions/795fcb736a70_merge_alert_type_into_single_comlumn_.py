"""merge alert type into single column and remove additional columns

Revision ID: 795fcb736a70
Revises: 089bf761b869
Create Date: 2026-10-02 00:28:36.969905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '795fcb736a70'
down_revision: Union[str, Sequence[str], None] = '089bf761b869'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""

    op.drop_column('alerts', 'urgent_ticket')
    op.drop_column('alerts', 'incident_candidate')
    op.drop_column('alerts', 'sla_risk')


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        'alerts',
        sa.Column(
            'urgent_ticket',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        'alerts',
        sa.Column(
            'incident_candidate',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        'alerts',
        sa.Column(
            'sla_risk',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )