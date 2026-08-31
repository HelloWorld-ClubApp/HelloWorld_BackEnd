"""add requested at and activity date

Revision ID: add_req_activity_20260831
Revises: add_post_thumb_20260830
Create Date: 2026-08-31 00:00:00.000000
"""
from alembic import op  # type: ignore[attr-defined]


revision = "add_req_activity_20260831"
down_revision = "add_post_thumb_20260830"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS requested_at TIMESTAMP WITH TIME ZONE NULL;"
    )
    op.execute(
        "UPDATE users SET requested_at = COALESCE(requested_at, created_at, now()) WHERE requested_at IS NULL;"
    )
    op.execute("ALTER TABLE users ALTER COLUMN requested_at SET DEFAULT now();")
    op.execute("ALTER TABLE users ALTER COLUMN requested_at SET NOT NULL;")

    op.execute(
        "ALTER TABLE posts ADD COLUMN IF NOT EXISTS activity_date TIMESTAMP WITH TIME ZONE NULL;"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE posts DROP COLUMN IF EXISTS activity_date;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS requested_at;")
