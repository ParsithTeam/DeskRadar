"""align ticket fields with taskbook

Revision ID: 9e3ffc287508
Revises: 0b9a16f92d27
Create Date: 2026-09-06 18:23:54.026445

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "9e3ffc287508"
down_revision: Union[str, Sequence[str], None] = "0b9a16f92d27"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename departement column to department."""
    op.alter_column(
        "tickets",
        "departement",
        new_column_name="department",
    )


def downgrade() -> None:
    """Restore the old departement column name."""
    op.alter_column(
        "tickets",
        "department",
        new_column_name="departement",
    )