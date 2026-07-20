# 게시글 조회, 페이징 로직
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from sqlalchemy import case, desc
from app.models.post import Like, Post,PostFile
from app.models.user import User , Role
from sqlalchemy.orm import Session
from app.models.file import File
from app.schemas.post import PostCreate

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
        .filter(Post.category == '공지')
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )

#=============================
# Post_001 공지사항 및 자유게시판 작성, 수정, 삭제 기능
def create_post(db: Session, post_data: PostCreate, user_id: int):
    """
    [Post_001] 게시글(공지사항, 자유게시판) 추가
    - 앞서 스키마(PostCreate)에서 1차 검열(빈칸, 과거 날짜 방지)을 마친 꺠끗한 데이터를 DB에 적재.
    - 게시글 작성 후 get_notice_list를 호출하면 정상적으로 목록에 띄워집니다.
    """
    db_post = Post(
        category=post_data.post_type, # 프론트에서 받은 게시글 타입(공지사항 등)을 DB 카테고리에 매핑
        title=post_data.title,
        content=post_data.content,
        schedule_date=post_data.schedule_date,
        user_id=user_id # 글을 작성한 사람의 고유 ID의 기록
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def update_notice_post(db: Session, post_id: int, post_data: dict):
    """
    [Post_001] 공지사항 게시글 수정
    - 수정할 게시글 번호(post_id)를 찾아 새로운 데이터로 덮어씌웁니다.
    """
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        db_post.category = post_data.post_type
        db_post.title = post_data.title
        db_post.content = post_data.content
        db_post.schedule_date = post_data.schedule_date
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
    [Post_L_002] 자유게시판 최신 목록 조회
    - filter(): '자유게시판' 카테고리만 쏙 골라냄.
    - order_by(): 만든 날짜(created_at)를 기준으로 최신순(desc)으로 줄 세움.
    - 페이징: page 번호에 따라 필요한 만큼만(limit) 가져옴.
    """
    offset = (page - 1) * limit
    return (
        db.query(Post)
        .filter(Post.category == '일반')
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

#=============================
# Post_002 자유게시판 추가, 수정, 삭제 및 제한 확인
def get_user_post_count(db: Session, user_id: int, category: str = "일반"):
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
    [Post_L_003] 질문게시판 최신 목록 조회
    - filter(): '질문' 카테고리만 필터링.
    - order_by(): 최신등록순(created_at desc) 정렬.
    - 페이징: page 단위로 limit만큼 조회.
    """
    offset = (page - 1) * limit
    return (
        db.query(Post)
        .filter(Post.category == '질문')
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

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