"""Enforce tickets.requester -> users.user_id.

Revision ID: d728c34b91ae
Revises: c74e91b2f063

Before running, install the previous UTC migration c74e91b2f063.
Existing orphan/null requester values must be resolved manually before migration.
"""
from alembic import op
import sqlalchemy as sa

revision = "d728c34b91ae"
down_revision = "c74e91b2f063"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    invalid_count = conn.execute(sa.text("""
        SELECT count(*) FROM tickets AS t
        WHERE t.requester IS NULL
           OR NOT EXISTS (SELECT 1 FROM users AS u WHERE u.user_id = t.requester)
    """)).scalar_one()
    if invalid_count:
        raise RuntimeError(
            f"Cannot add requester foreign key: {invalid_count} existing tickets "
            "have NULL or nonexistent requester ids. Resolve these records first."
        )
    op.alter_column("tickets", "requester", existing_type=sa.Integer(), nullable=False)
    op.create_foreign_key(
        "fk_tickets_requester_users", "tickets", "users",
        ["requester"], ["user_id"], ondelete="RESTRICT",
    )
    op.create_index("ix_tickets_requester", "tickets", ["requester"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_tickets_requester", table_name="tickets")
    op.drop_constraint("fk_tickets_requester_users", "tickets", type_="foreignkey")
    op.alter_column("tickets", "requester", existing_type=sa.Integer(), nullable=True)
