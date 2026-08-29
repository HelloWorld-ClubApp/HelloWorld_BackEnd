"""add post thumbnail file id

Revision ID: add_post_thumbnail_file_id_20260830
Revises: drop_post_schedule_date_20260827
Create Date: 2026-08-30 00:00:00.000000
"""
from alembic import op  # type: ignore[attr-defined]


revision = "add_post_thumbnail_file_id_20260830"
down_revision = "drop_post_schedule_date_20260827"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE posts ADD COLUMN IF NOT EXISTS thumbnail_file_id INTEGER NULL;"
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'fk_posts_thumbnail_file_id'
            ) THEN
                ALTER TABLE posts
                ADD CONSTRAINT fk_posts_thumbnail_file_id
                FOREIGN KEY (thumbnail_file_id)
                REFERENCES files(id)
                ON DELETE SET NULL;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("ALTER TABLE posts DROP CONSTRAINT IF EXISTS fk_posts_thumbnail_file_id;")
    op.execute("ALTER TABLE posts DROP COLUMN IF EXISTS thumbnail_file_id;")
