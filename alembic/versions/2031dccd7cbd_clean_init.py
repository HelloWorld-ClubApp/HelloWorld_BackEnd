"""clean_init_add_is_deleted_and_schedule_date

Revision ID: 2031dccd7cbd
Revises: 
Create Date: 2026-07-21 14:31:00.354660
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2031dccd7cbd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    [Upgrade Schema]
    1. users 테이블에 소프트 삭제(Soft Delete) 관리를 위한 is_deleted 컬럼 추가 (기본값 False)
    2. posts 테이블에 일정 관리를 위한 schedule_date (TIMESTAMP WITH TIME ZONE) 컬럼 추가
    """
    # 1. users 테이블: is_deleted 컬럼 추가 (Boolean, Null 불가, 기본값 False)
    # 기존에 존재하는 회원 데이터들도 오류 없이 DEFAULT False 가 적용되도록 설정
    op.add_column(
        'users',
        sa.Column(
            'is_deleted',
            sa.Boolean(),
            nullable=False,
            server_default=sa.text('false')
        )
    )

    # 2. posts 테이블: schedule_date 컬럼 추가 (TIMESTAMP WITH TIME ZONE, Null 허용)
    # 일반 게시글 등 일정이 없는 경우도 있으므로 nullable=True 로 설정 (PostCreate 스키마 Optional과 일치)
    op.add_column(
        'posts',
        sa.Column(
            'schedule_date',
            sa.TIMESTAMP(timezone=True),
            nullable=True
        )
    )


def downgrade() -> None:
    """
    [Downgrade Schema]
    - upgrade()에서 추가한 컬럼들을 롤백(제거)할 때 실행되는 로직
    - 주의: 롤백 시 해당 컬럼에 저장된 데이터는 모두 소실됩니다.
    """
    # 1. posts 테이블에서 schedule_date 컬럼 제거
    op.drop_column('posts', 'schedule_date')

    # 2. users 테이블에서 is_deleted 컬럼 제거
    op.drop_column('users', 'is_deleted')