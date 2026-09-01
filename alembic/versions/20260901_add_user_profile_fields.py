"""add user profile fields

Revision ID: add_user_profile_fields_20260901
Revises: add_req_activity_20260831
Create Date: 2026-09-01 00:00:00.000000
"""
from alembic import op  # type: ignore[attr-defined]


revision = "add_user_profile_fields_20260901"
down_revision = "add_req_activity_20260831"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio VARCHAR(255) NULL;")
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS hashtags JSONB NOT NULL DEFAULT '[]'::jsonb;"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS hashtags;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS bio;")
