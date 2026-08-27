# 게시글 조회, 페이징 로직
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from sqlalchemy import case, desc, func
from app.models.post import Post, PostFile, Like, Comment
from app.models.user import User , Role
from app.models.file import File
from sqlalchemy.orm import Session

from app.schemas.post import PostCreate
from app.core.enum.post import PostCategory
from app.models.post import Comment

def normalize_file_url(file_url: str) -> str:
    normalized_url = file_url.replace("\\", "/")
    if normalized_url.startswith("uploads/"):
        return f"/{normalized_url}"
    return normalized_url

def get_latest_posts(db: Session, limit: int = 3):
    """
    메인 페이지 최신 게시글 조회 - 댓글 수 join 포함
    """
    return (
        db.query(
            Post,
            Role.role_name,
            func.count(Comment.id.distinct()).label("comment_count")
        )
        .join(User, Post.user_id == User.id)
        .join(Role, User.role_id == Role.id)
        .outerjoin(Comment, Post.id == Comment.post_id)
        .group_by(Post.id, Role.role_name)
        .order_by(
            case((Post.category == PostCategory.NOTICE.value, 0), else_=1),
            Post.created_at.desc()
        )
        .limit(limit)
        .all()
    )



"""
def get_club_feed(db: Session, limit: int = 4):
    
    이미지가 포함된 최신 게시글 4개를 가져옵니다.
    게시글에 이미지가 여러 개일 경우, 가장 먼저 등록된 이미지(대표 이미지) 1개만 추출합니다.
    
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
    """
    
#작성자 : 천석훈 , 김세연, 문호성
#=============================
def get_notice_list(db: Session, limit: int = 10):
    """
    [Post_L_001] 요구사항 정의서 연동 공지사항 최신 목록 조회
    - filter(): category가 '공지'인 행만 엄격하게 식별
    - order_by(): 최신등록순 정렬 오더 반영 (created_at desc)
    - limit(): 한 페이지당 최대 10개 출력 스펙 충족
    - 데이터가 존재하지 않을 경우 빈 리스트([])를 정상 반환하여 프론트엔드 예외 처리 유도
    """
    return (
        db.query(Post)
        .filter(Post.category == PostCategory.NOTICE.value)
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )

#=============================
# Post_001 공지사항 및 자유게시판 작성, 수정, 삭제 기능 --> 수정자 : 엄인섭
def create_post(db: Session, post_data: PostCreate, user_id: int):
    """
    [이슈 5, 8 해결] 게시글 생성 및 다중 파일 매핑, 일정 데이터 적재
    """
    # 1. 게시글 본문 데이터 생성 (시작일, 종료일 포함)
    db_post = Post(
        category=post_data.post_type,
        title=post_data.title,
        content=post_data.content,
        start_date=post_data.start_date,
        end_date=post_data.end_date,
        user_id=user_id
    )
    db.add(db_post)
    db.flush() # post.id를 즉시 추출하기 위해 flush 실행 (commit 아님)

    # 2. [이슈 5번 해결] 다중 파일 ID가 존재할 경우 post_files 매핑 테이블에 일괄 등록
    if post_data.file_ids:
        for file_id in post_data.file_ids:
            db_post_file = PostFile(
                post_id=db_post.id,
                file_id=file_id
            )
            db.add(db_post_file)

    db.commit()
    db.refresh(db_post)
    return db_post

def update_notice_post(db: Session, post_id: int, post_data: dict):
    """
    [Post_001] 공지사항 게시글 수정
    - 수정할 게시글 번호(post_id)를 찾아 새로운 데이터로 덮어씌웁니다.
    - schedule_date 대신 start_date/end_date를 사용합니다.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        db_post.category = post_data.get("post_type", db_post.category)
        db_post.title = post_data.get("title", db_post.title)
        db_post.content = post_data.get("content", db_post.content)
        db_post.start_date = post_data.get("start_date", db_post.start_date)
        db_post.end_date = post_data.get("end_date", db_post.end_date)
        db.commit()
        db.refresh(db_post)

    return db_post

def delete_notice_post(db: Session, post_id: int):
    """
    [Post_001] 공지사항 게시글 삭제
    - 게시글 번호(post_id)를 찾아 DB에서 완전히 삭제합니다.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        db.delete(db_post)
        db.commit()

    return db_post

#=============================
# Post_L_002 자유게시판 목록 조회 기능
def get_free_posts(db: Session, page: int = 1, limit: int = 10):
    """
    [Post_L_002] 자유게시판 최신 목록 조회 - 좋아요/댓글 수 join 포함
    """
    offset = (page - 1) * limit
    rows = (
        db.query(
            Post,
            func.count(Like.id.distinct()).label("like_count"),
            func.count(Comment.id.distinct()).label("comment_count")
        )
        .filter(Post.category == PostCategory.FREE.value)
        .outerjoin(Like, Post.id == Like.post_id)
        .outerjoin(Comment, Post.id == Comment.post_id)
        .group_by(Post.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": post.id,
            "title": post.title,
            "created_at": post.created_at,
            "like_count": like_count,
            "comment_count": comment_count,
        }
        for post, like_count, comment_count in rows
    ]

#=============================
# Post_002 자유게시판 추가, 수정, 삭제 및 제한 확인
def get_user_post_count(db: Session, user_id: int, category: str = PostCategory.FREE.value):
    """[Post_002] 해당 유저의 특정 카테고리 게시글 작성 개수 조회"""
    return db.query(Post).filter(Post.user_id == user_id, Post.category == category).count()

def get_post_by_id(db: Session, post_id: int):
    """[Post_002] 게시글 상세 조회 (권한 체크용)"""
    return db.query(Post).filter(Post.id == post_id).first()

def update_free_post(db: Session, post_id: int, post_data: dict):
    """[Post_002] 자유게시판 게시글 수정"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db_post.title = post_data.get("title", db_post.title)
        db_post.content = post_data.get("content", db_post.content)
        # 이미지 URL 처리 로직 필요 시 추가
        db.commit()
        db.refresh(db_post)
    return db_post

def delete_free_post(db: Session, post_id: int):
    """[Post_002] 자유게시판 게시글 삭제"""
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False

#=============================
# Post_L_003 질문게시판 목록 조회 기능
def get_question_posts(db: Session, page: int = 1, limit: int = 10):
    """
    [Post_L_003] 질문게시판 최신 목록 조회 - 좋아요/댓글 수 join 포함
    """
    offset = (page - 1) * limit
    rows = (
        db.query(
            Post,
            func.count(Like.id.distinct()).label("like_count"),
            func.count(Comment.id.distinct()).label("comment_count")
        )
        .filter(Post.category == PostCategory.QNA.value)
        .outerjoin(Like, Post.id == Like.post_id)
        .outerjoin(Comment, Post.id == Comment.post_id)
        .group_by(Post.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": post.id,
            "title": post.title,
            "created_at": post.created_at,
            "like_count": like_count,
            "comment_count": comment_count,
        }
        for post, like_count, comment_count in rows
    ]

#=============================
# Post_003 질문게시판 수정, 삭제
def update_question_post(db: Session, post_id: int, post_data: dict):
    """
    [Post_003] 질문게시판 게시글 수정
    - 제목과 내용을 덮어씌웁니다.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db_post.title = post_data.get("title", db_post.title)
        db_post.content = post_data.get("content", db_post.content)
        # 파일 URL 등 추가 필드가 있다면 여기에 반영
        db.commit()
        db.refresh(db_post)
    return db_post

def delete_question_post(db: Session, post_id: int):
    """
    [Post_003] 질문게시판 게시글 삭제
    - DB에서 해당 레코드를 삭제합니다.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post:
        db.delete(db_post)
        db.commit()
        return True
    return False

class CRUDPost:
    def __init__(self, model):
        self.model = model
    def get_post(self, db, post_id):
        return db.query(self.model).filter(self.model.id == post_id).first()
    
from app.models.post import Post
post_crud = CRUDPost(Post)



# ==========================================
# [MY_005] 내가 쓴 게시물 조회 (무한 스크롤 페이징)
# 작성자 : 엄인섭
# ==========================================
def get_posts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    # 전체 개수 산출 (프론트 무한 스크롤 판단용)
    total_count = db.query(Post).filter(Post.user_id == user_id).count()
    
    # 최신순(created_at desc) 정렬 후 페이징 조회
    posts = (
        db.query(Post)
        .filter(Post.user_id == user_id)
        .order_by(desc(Post.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return total_count, posts

# ==========================================
# [MY_006] 좋아요 누른 게시물 조회 (좋아요 누른 시간 기준)
# ==========================================
def get_liked_posts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    query = (
        db.query(Post)
        .join(Like, Post.id == Like.post_id)
        .filter(Like.user_id == user_id)
    )
    
    total_count = query.count()
    
    # Post.created_at이 아닌 Like.created_at 최신순 정렬!
    posts = (
        query.order_by(desc(Like.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return total_count, posts


# ==========================================
# [Post_L_004] 전체 게시판 통합 목록 조회
# ==========================================
def get_all_posts(db: Session, page: int = 1, limit: int = 10):
    """
    공지, 자유, 질문 게시판을 통합하여 최신순으로 페이징 조회합니다.
    - 프론트엔드의 3중 호출 병목을 해결하기 위한 단일 쿼리입니다.
    """
    offset = (page - 1) * limit
    return (
        db.query(Post)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

# ==========================================
# [Post_D_001] 게시글 상세 조회 (좋아요/댓글 Join 최적화)
# ==========================================
def get_post_detail_with_relations(db: Session, post_id: int, current_user_id: int):
    """
    [Post_D_001] 단일 게시글과 해당 게시글에 달린 모든 데이터를 한 번에 반환합니다.
    - is_liked: 현재 로그인 사용자의 좋아요 여부 판별
    - is_author: 현재 로그인 사용자가 작성자인지 판별
    - author_name: 작성자 이름 (User.name 조인)
    - 댓글 목록: 댓글 작성자 이름도 함께 반환
    - images: 이미지 첨부파일 (image/* MIME)
    - attachments: 일반 첨부파일 (이미지 제외)
    """
    # 게시글 + 작성자 이름 join
    row = (
        db.query(Post, User.name.label("author_name"))
        .join(User, Post.user_id == User.id)
        .filter(Post.id == post_id)
        .first()
    )

    if not row:
        return None

    post, author_name = row

    # 좋아요 개수 집계
    like_count = db.query(func.count(Like.id)).filter(Like.post_id == post_id).scalar()

    # 현재 사용자 좋아요 여부
    is_liked = db.query(Like).filter(
        Like.post_id == post_id,
        Like.user_id == current_user_id
    ).first() is not None

    # 작성자 여부
    is_author = (post.user_id == current_user_id)

    # 댓글 목록 (작성자 이름 join)
    comment_rows = (
        db.query(Comment, User.name.label("commenter_name"))
        .join(User, Comment.user_id == User.id)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    comments = [
        {
            "id": c.id,
            "user_id": c.user_id,
            "author_name": commenter_name,
            "content": c.content,
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c, commenter_name in comment_rows
    ]

    # 첨부파일 조회 (post_files -> files join)
    file_rows = (
        db.query(File)
        .join(PostFile, File.id == PostFile.file_id)
        .filter(PostFile.post_id == post_id)
        .order_by(File.id.asc())
        .all()
    )

    # 이미지(image/*)와 일반 첨부파일 분리
    images = []
    attachments = []
    for f in file_rows:
        file_dict = {
            "id": f.id,
            "file_url": normalize_file_url(f.file_url),
            "file_type": f.file_type,
            "file_size": f.file_size,
            "original_name": f.original_name,
        }
        if f.file_type.startswith("image/"):
            images.append(file_dict)
        else:
            attachments.append(file_dict)

    return {
        "post": post,
        "author_name": author_name,
        "like_count": like_count,
        "is_liked": is_liked,
        "is_author": is_author,
        "images": images,
        "attachments": attachments,
        "comments": comments
    }


#============================================================
# 작성자 : 엄인섭
#============================================================

def get_all_posts_optimized(db: Session, page: int = 1, limit: int = 10):
    """
    [전체 게시판 통합 목록 조회 - 성능 최적화 버전]
    - Outer Join과 Group By를 사용하여 like_count, comment_count를 단일 쿼리로 추출.
    - is_liked는 상세 조회 API로 이동됨.
    """
    offset = (page - 1) * limit
    
    query = (
        db.query(
            Post,
            func.count(Like.id.distinct()).label("like_count"),
            func.count(Comment.id.distinct()).label("comment_count")
        )
        .outerjoin(Like, Post.id == Like.post_id)
        .outerjoin(Comment, Post.id == Comment.post_id)
        .group_by(Post.id)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    result = []
    for post, like_count, comment_count in query:
        result.append({
            "id": post.id,
            "category": post.category,
            "title": post.title,
            "created_at": post.created_at,
            "like_count": like_count,
            "comment_count": comment_count,
        })
        
    return result
