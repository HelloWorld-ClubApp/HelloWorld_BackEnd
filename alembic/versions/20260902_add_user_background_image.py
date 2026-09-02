"""add user background image

Revision ID: add_user_background_20260902
Revises: add_user_profile_fields_20260901
Create Date: 2026-09-02 00:00:00.000000
"""
from alembic import op  # type: ignore[attr-defined]


revision = "add_user_background_20260902"
down_revision = "add_user_profile_fields_20260901"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS background_file_id INTEGER NULL;"
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'fk_users_background_file_id'
            ) THEN
                ALTER TABLE users
                ADD CONSTRAINT fk_users_background_file_id
                FOREIGN KEY (background_file_id)
                REFERENCES files(id)
                ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP CONSTRAINT IF EXISTS fk_users_background_file_id;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS background_file_id;")
