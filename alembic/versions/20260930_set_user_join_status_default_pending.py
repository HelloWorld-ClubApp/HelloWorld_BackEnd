"""set user join status default to pending

Revision ID: set_join_pending_20260930
Revises: add_user_background_20260902
Create Date: 2026-09-30 00:00:00.000000
"""
from alembic import op  # type: ignore[attr-defined]


revision = "set_join_pending_20260930"
down_revision = "add_user_background_20260902"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN join_status SET DEFAULT 'PENDING';"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE users ALTER COLUMN join_status SET DEFAULT 'APPROVED';"
    )
