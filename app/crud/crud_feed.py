from sqlalchemy.orm import Session

from app.models.feed import Feed
from app.schemas.feed import FeedCreate, FeedUpdate
from app.models.file import File
from app.crud.crud_chat import is_participant, add_message


def normalize_file_url(file_url: str) -> str:
    normalized_url = file_url.replace("\\", "/")
    if normalized_url.startswith("uploads/"):
        return f"/{normalized_url}"
    return normalized_url


def build_feed_response(feed: Feed, file_url: str):
    return {
        "id": feed.id,
        "title": feed.title,
        "file_id": feed.file_id,
        "file_url": normalize_file_url(file_url),
        "user_id": feed.user_id,
        "created_at": feed.created_at,
    }


# ==========================================
# FEED_001
# 메인페이지 피드 등록
# ==========================================
def create_feed(
    db: Session,
    feed_data: FeedCreate,
    user_id: int
):
    db_feed = Feed(
        title=feed_data.title,
        file_id=feed_data.file_id,
        user_id=user_id
    )

    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)

    file = db.query(File).filter(File.id == db_feed.file_id).first()
    return build_feed_response(db_feed, file.file_url if file else "")


# ==========================================
# FEED_002
# 메인페이지 피드 전체 조회
# ==========================================
def get_feed_list(
    db: Session
):
    rows = (
        db.query(Feed, File.file_url)
        .join(File, Feed.file_id == File.id)
        .order_by(Feed.created_at.desc())
        .all()
    )
    return [build_feed_response(feed, file_url) for feed, file_url in rows]

# ==========================================
# FEED_003
# 메인페이지 피드 수정
# ==========================================

def update_feed(
    db: Session,
    feed_id: int,
    feed_data: FeedUpdate
):
    feed = (
        db.query(Feed)
        .filter(Feed.id == feed_id)
        .first()
    )

    if not feed:
        return None
    
    feed.title = feed_data.title
    feed.file_id = feed_data.file_id

    db.commit()
    db.refresh(feed)

    file = db.query(File).filter(File.id == feed.file_id).first()
    return build_feed_response(feed, file.file_url if file else "")

# ==========================================
# FEED_004
# 메인페이지 피드 삭제
# ==========================================
def delete_feed(
    db: Session,
    feed_id: int
):
    feed = (
        db.query(Feed)
        .filter(Feed.id == feed_id)
        .first()
    )

    if not feed:
        return None

    file = (
        db.query(File)
        .filter(File.id == feed.file_id)
        .first()
    )

    # Feed 삭제
    db.delete(feed)

    # 연결된 File 삭제
    if file:
        db.delete(file)

    db.commit()

    return True

# ==========================================
# FEED_005
# 메인페이지 피드 상세 조회
# ==========================================

def get_feed_detail(
    db: Session,
    feed_id: int
):
    row = (
        db.query(
            Feed.id,
            Feed.title,
            Feed.created_at,
            File.file_url
        )
        .join(
            File,
            Feed.file_id == File.id
        )
        .filter(
            Feed.id == feed_id
        )
        .first()
    )

    if not row:
        return None

    return {
        "id": row.id,
        "title": row.title,
        "file_url": normalize_file_url(row.file_url),
        "created_at": row.created_at,
    }
    
# ==========================================
# [FEED_006] 피드 채팅방 공유
# ==========================================
def share_feed_to_chat(
    db: Session,
    feed_id: int,
    room_id: int,
    user_id: int
):
    # 1. 피드 조회
    feed = (
        db.query(Feed)
        .filter(Feed.id == feed_id)
        .first()
    )

    if not feed:
        return None, "FEED_NOT_FOUND"

    # 2. 채팅방 참여 여부 확인
    if not is_participant(
        db,
        room_id,
        user_id
    ):
        return None, "NOT_PARTICIPANT"

    # 3. 기존 메시지 생성 로직 재사용
    message = add_message(
        db=db,
        room_id=room_id,
        user_id=user_id,
        content=feed.title,
        file_id=feed.file_id
    )

    return message, None
