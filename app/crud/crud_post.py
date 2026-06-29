# 게시글 조회, 페이징 로직
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from sqlalchemy import case
from app.models.post import Post,PostFile
from app.models.user import User , Role
from sqlalchemy.orm import Session
from app.models.file import File

def get_latest_posts(db: Session, limit: int = 3):
    return (
        db.query(Post, Role.role_name)
        .join(User, Post.user_id == User.id)
        .join(Role, User.role_id == Role.id)
        .order_by(
            case((Post.category == '공지', 0), else_=1), # 공지 우선순위
            Post.created_at.desc()                      # 최신순
        )
        .limit(limit)
        .all()
    )



def get_club_feed(db: Session, limit: int = 4):
    """
    이미지가 포함된 최신 게시글 4개를 가져옵니다.
    게시글에 이미지가 여러 개일 경우, 가장 먼저 등록된 이미지(대표 이미지) 1개만 추출합니다.
    """
    # 1. 파일이 존재하는 게시글을 최신순으로 모두 조인해서 가져옴
    query = (
        db.query(Post.id, Post.title, Post.created_at, File.file_url)
        .join(PostFile, Post.id == PostFile.post_id)
        .join(File, PostFile.file_id == File.id)
        # 만약 특정 카테고리(예: '앨범')만 피드에 띄우고 싶다면 아래 주석 해제
        # .filter(Post.category == '앨범')
        .order_by(
            Post.created_at.desc(),   # 1순위: 최신 게시글 순서
            File.id.asc()             # 2순위: File 테이블의 id를 기준으로 첫 번째 첨부파일 정렬
        )
    )
    
    records = query.all()
    
    # 2. 파이썬 단에서 게시글 중복 제거 (게시글 1개당 1장의 이미지만 노출되도록)
    result = []
    seen_post_ids = set()
    
    for row in records:
        # 아직 피드 리스트에 안 들어간 게시글이면 추가 (대표 이미지가 됨)
        if row.id not in seen_post_ids:
            result.append({
                "id": row.id,
                "title": row.title,
                "image_url": row.file_url,
                "created_at": row.created_at
            })
            seen_post_ids.add(row.id) # 확인된 게시글 ID 기록
            
        # 3. 원하는 개수(limit=4)가 다 채워졌으면 반복문 종료
        if len(result) >= limit:
            break
            
    return result