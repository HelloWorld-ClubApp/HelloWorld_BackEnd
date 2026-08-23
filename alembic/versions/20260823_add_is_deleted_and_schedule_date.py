"""comprehensive update: add is_deleted to users, schedule_date, start_date, end_date to posts

Revision ID: sns_comprehensive_20260823
Revises: 178b3c33a716
Create Date: 2026-08-23 20:00:00.000000

- 아키텍트 노트 (Architecture Note): 
  1. Alembic의 alembic_version.version_num 컬럼 제한(VARCHAR(32))에 맞춰 
     리비전 ID를 32자 이내('sns_comprehensive_20260823', 26자)로 최적화함.
  2. PostgreSQL의 IF NOT EXISTS 구문을 사용하여 중복 에러(DuplicateColumn) 원천 방지.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, updated to fit within VARCHAR(32) limit.
revision = 'sns_comprehensive_20260823'
down_revision = '178b3c33a716'  # 직전 정상 마이그레이션 리비전 ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    [Migration Upgrade]
    - 데이터베이스 스키마 확장 시 발생할 수 있는 중복 에러를 방지하고,
      필수 컬럼들을 IF NOT EXISTS 구문으로 안전하게 일괄 반영합니다.
    """
    # 1. users 테이블 소프트 삭제(Soft Delete) 관리를 위한 is_deleted 컬럼 추가
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT false;"
    )
    
    # 2. posts 테이블 공지사항 일정 관리를 위한 schedule_date 컬럼 추가
    op.execute(
        "ALTER TABLE posts ADD COLUMN IF NOT EXISTS schedule_date TIMESTAMP WITH TIME ZONE NULL;"
    )

    # 3. posts 테이블 다중 일정 관리를 위한 start_date (시작일) 컬럼 추가
    op.execute(
        "ALTER TABLE posts ADD COLUMN IF NOT EXISTS start_date TIMESTAMP WITH TIME ZONE NULL;"
    )

    # 4. posts 테이블 다중 일정 관리를 위한 end_date (종료일) 컬럼 추가
    op.execute(
        "ALTER TABLE posts ADD COLUMN IF NOT EXISTS end_date TIMESTAMP WITH TIME ZONE NULL;"
    )


def downgrade() -> None:
    """
    [Migration Downgrade]
    - 마이그레이션 롤백 시 추가된 모든 컬럼들을 안전하게 역순으로 제거합니다.
    """
    op.execute("ALTER TABLE posts DROP COLUMN IF EXISTS end_date;")
    op.execute("ALTER TABLE posts DROP COLUMN IF EXISTS start_date;")
    op.execute("ALTER TABLE posts DROP COLUMN IF EXISTS schedule_date;")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS is_deleted;")