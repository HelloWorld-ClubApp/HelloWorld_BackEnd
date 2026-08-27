"""drop post schedule date

Revision ID: drop_post_schedule_date_20260827
Revises: add_user_join_status_20260827
Create Date: 2026-08-27 00:10:00.000000
"""
from alembic import op


revision = "drop_post_schedule_date_20260827"
down_revision = "add_user_join_status_20260827"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE posts DROP COLUMN IF EXISTS schedule_date;")


def downgrade() -> None:
    op.execute(
        "ALTER TABLE posts ADD COLUMN IF NOT EXISTS schedule_date TIMESTAMP WITH TIME ZONE NULL;"
    )
