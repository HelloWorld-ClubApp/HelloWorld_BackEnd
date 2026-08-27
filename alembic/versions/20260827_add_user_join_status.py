"""add user join status

Revision ID: add_user_join_status_20260827
Revises: sns_comprehensive_20260823
Create Date: 2026-08-27 00:00:00.000000
"""
from alembic import op


revision = "add_user_join_status_20260827"
down_revision = "sns_comprehensive_20260823"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS join_status VARCHAR(10) NOT NULL DEFAULT 'APPROVED';"
    )
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now();"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS created_at;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS join_status;")
