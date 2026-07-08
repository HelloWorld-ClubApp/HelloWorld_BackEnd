"""add_content_column_to_schedules

Revision ID: 1b4b4c3c930d
Revises: 5760b58cb12c
Create Date: 2026-07-08 20:15:54.318507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b4b4c3c930d'
down_revision: Union[str, Sequence[str], None] = '5760b58cb12c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 딱 컬럼 추가만 수행
    op.add_column('schedules', sa.Column('content', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('schedules', 'content')