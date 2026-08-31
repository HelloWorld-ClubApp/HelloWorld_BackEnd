# 게시판(공지, 자유, 질문), 좋아요 (Post_001~003)
# 작성자 : 엄인섭
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from app.core.database import get_db # 또는 세션 의존성 주입 경로
from app.schemas.post import PostPreviewResponse, NoticeListResponse, PostCreate, FreePostListResponse,QuestionPostListResponse, ActivityPostListResponse, PostDetailResponse, PaginatedPostResponse
from app.crud import crud_post
from app.api.dependencies import get_current_user
from app.schemas.post import PostCreate
from app.models.user import User
from app.core.enum.post import PostCategory

router = APIRouter()

# 임원진 및 관리자 권한 ID 목록 (2: 관리자, 3: 회장, 4: 부회장, 5: 총무)
NOTICE_ALLOWED_ROLE_IDS = crud_post.NOTICE_ALLOWED_ROLE_IDS

@router.get("/latest", response_model=List[PostPreviewResponse])
def get_latest_posts(db: Session = Depends(get_db)):
    posts_with_roles = crud_post.get_latest_posts(db)

    # 리스트 데이터 가공
    result = []
    for post, role_name, comment_count, thumbnail_image in posts_with_roles:
        result.append({
            "id": post.id,
            "title": post.title,
            "category": post.category,
            "author_role": role_name, # 회장/부회장 정보
            "created_at": post.created_at,
            "activity_date": post.activity_date,
            "comment_count": comment_count,
            "thumbnail_image": thumbnail_image,
            "thumbnail_file_id": thumbnail_image["id"] if thumbnail_image else None,
            "thumbnail_url": thumbnail_image["file_url"] if thumbnail_image else None,
        })
    return result

"""
@router.get("/feed", response_model=List[ClubFeedResponse], summary="메인 페이지 CLUB FEED (사진 앨범) 조회")
def get_club_feed(db: Session = Depends(get_db)):

    첨부파일(사진)이 포함된 최신 게시글 4개를 조회합니다.
    - 게시글에 이미지가 여러 개일 경우 가장 첫 번째 이미지를 썸네일로 사용합니다.
    - 결과가 빈 배열([])일 경우 프론트엔드에서 예외 처리 화면을 보여줍니다.

    return crud_post.get_club_feed(db=db, limit=4)
"""


# [이슈 7 해결] 게시글 수정 API 단일화 (공지/일반/질문 통합)
# 기존에 있던 update_notice_api, update_free_post_api, update_question_post_api 삭제함.
# app/api/v1/posts.py 내 게시글 통합 수정 API 수정
@router.put("/{post_id}", summary="게시글 통합 수정 (공지/일반/질문)")
def update_integrated_post_api(
    post_id: int,
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    게시글 수정 API 통합 관리
    - [요구사항 반영]: 더 이상 사용되지 않는 schedule_date 참조를 완전히 제거하고,
      start_date 및 end_date 필드로 안전하게 업데이트되도록 수정합니다.
    """
    db_post = crud_post.get_post_by_id(db=db, post_id=post_id)
    if not db_post:
        raise HTTPException(status_code=404, detail="해당 게시글을 찾을 수 없습니다.")

    # 1. 권한 분기: 공지사항일 경우 임원진(role_id: 2~5) 검증
    if db_post.category == "공지":
        if getattr(current_user, "role_id", None) not in NOTICE_ALLOWED_ROLE_IDS:
            raise HTTPException(status_code=403, detail="공지를 수정할 권한이 없습니다.")
    # 2. 권한 분기: 일반/질문일 경우 본인 또는 최고관리자(role_id: 2) 검증
    else:
        if db_post.user_id != current_user.id and getattr(current_user, "role_id", None) != 2:
            raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 수정할 수 있습니다.")

    # 3. 통합 업데이트 수행 (schedule_date 제거 -> start_date, end_date 반영)
    db_post.title = post_in.title
    db_post.content = post_in.content
    file_ids_provided = "file_ids" in post_in.model_fields_set
    thumbnail_file_id_provided = "thumbnail_file_id" in post_in.model_fields_set

    if file_ids_provided:
        synced_file_ids = crud_post.sync_post_files(
            db=db,
            post_id=db_post.id,
            file_ids=post_in.file_ids,
        )
        db_post.thumbnail_file_id = crud_post.select_thumbnail_file_id(
            db=db,
            file_ids=synced_file_ids,
            thumbnail_file_id=post_in.thumbnail_file_id,
        )
    elif thumbnail_file_id_provided:
        if post_in.thumbnail_file_id is None:
            db_post.thumbnail_file_id = None
        else:
            existing_file_ids = crud_post.get_post_file_ids(db=db, post_id=db_post.id)
            db_post.thumbnail_file_id = crud_post.select_thumbnail_file_id(
                db=db,
                file_ids=existing_file_ids,
                thumbnail_file_id=post_in.thumbnail_file_id,
            )
    db_post.start_date = post_in.start_date
    db_post.end_date = post_in.end_date
    db_post.activity_date = post_in.activity_date

    db.commit()
    db.refresh(db_post)
    return {"data": db_post}


#작성자 : 천석훈 , 김세연, 문호성
#=============================
@router.get("/notices", response_model=NoticeListResponse, summary="공지 리스트 조회")
def get_notice_list_api(db: Session = Depends(get_db)):
    """
    [Post_L_001] 요구사항 정의서 연동 - 공지사항 게시판 목록 조회 API
    - DB에서 최신순으로 정렬된 10개의 공지사항 데이터를 호출합니다.
    - 만약 게시글이 없다면 빈 배열([])이 반환되며, 프론트엔드에서 "등록된 게시글이 없습니다"를 표시합니다.
    """
    # 1. 아까 2단계에서 만든 파이썬 엔진(crud_post)에게 DB에서 데이터 긁어오라고 명
    notices_data = crud_post.get_notice_list(db=db, limit=10)

    # 2. 1단계에서 만든 데이터 규격(NoticeListResponse)에 맞춰서 딕셔너리로 포장 후 배달!
    return {"notices": notices_data}

# =============================
# Post_001 공지사항 및 자유게시판 작성, 수정, 삭제 API
# =============================
@router.post("/", summary="게시글 작성 (공지/일반)")
def create_post_api(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)  # 현재 로그인한 사용자의 신분증(정보)
):
    """
    [Post_001] 게시글 작성 API
    - 스키마(PostCreate)를 통해 빈칸, 과거 날짜 여부는 이미 자동 필터링 되었습니다.
    - 공지사항일 경우, 직책이 [2: 관리자, 3: 회장, 4: 부회장, 5: 총무]인지 최종 권한 검사를 수행합니다.
    """
    # 1. 권한 검사: 작성하려는 글이 '공지'일 때 role_id(숫자) 기반으로 확인
    if post_in.post_type == "공지":
        # 주석: DB User 모델의 실제 속성명인 role_id 로 접근하여 검사
        if getattr(current_user, "role_id", None) not in NOTICE_ALLOWED_ROLE_IDS:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="공지를 작성할 권한이 없습니다. (임원진 또는 관리자만 작성 가능)"
            )

    # 2. 모든 검사를 통과했으니 CRUD 창고 지시서로 데이터 전달
    new_post = crud_post.create_post(db=db, post_data=post_in, user_id=current_user.id)
    return {"message": "게시글이 성공적으로 작성되었습니다.", "data": new_post}



@router.delete("/{post_id}", summary="게시글 삭제 (공지/일반)")
def delete_notice_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)  # 현재 로그인한 사용자의 신분증(정보)
):
    """
    [Post_001] 게시글 삭제 API
    - 공지사항 삭제 시 임원진/관리자 권한(role_id)을 검사합니다.
    - 일반 게시글 삭제 시 작성자 본인 또는 관리자인지 검사합니다.
    """
    # 1. 대상 게시글 존재 여부 사전 확인
    db_post = crud_post.get_post_by_id(db=db, post_id=post_id)
    if not db_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글을 찾을 수 없습니다."
        )

    if not crud_post.can_delete_post(
        post=db_post,
        user_id=current_user.id,
        role_id=getattr(current_user, "role_id", None),
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="게시글을 삭제할 권한이 없습니다."
        )

    # 4. 검증 완료 후 삭제 수행
    crud_post.delete_notice_post(db=db, post_id=post_id)
    return {"message": "게시글이 성공적으로 삭제되었습니다."}

#=============================
# Post_L_002 자유게시판 목록 조회 API
@router.get("/free", response_model=FreePostListResponse, summary="일반 목록 조회")
def get_free_post_list(page: int = 1, db: Session = Depends(get_db)):
    """
    [Post_L_002] 자유게시판 게시글 목록 조회 API
    - 최신순으로 정렬된 10개의 게시글을 가져옵니다.
    - 게시글이 없으면 "등록된 게시글이 없습니다"라는 메시지와 함께 빈 리스트를 반환합니다.
    - 좋아요 수와 댓글 수를 함께 응답합니다.
    """
    posts_data = crud_post.get_free_posts(db=db, page=page, limit=10)

    if not posts_data:
        return {"message": "등록된 게시글이 없습니다.", "posts": []}

    return {"posts": posts_data}

#=============================
# Post_002 자유게시판 작성/수정/삭제 API 추가
@router.post("/free", summary="일반 게시글 작성")
def create_free_post_api(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    # 1. 작성 제한 확인 (5개)
    if crud_post.get_user_post_count(db, current_user.id, "일반") >= 5:
        raise HTTPException(status_code=400, detail="일반은 최대 5개까지만 작성 가능합니다.")

    # 2. 작성 로직 수행
    new_post = crud_post.create_post(db=db, post_data=post_in, user_id=current_user.id)
    return {"message": "게시글이 작성되었습니다.", "data": new_post}


@router.delete("/free/{post_id}", summary="일반 게시글 삭제")
def delete_free_post_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    post = crud_post.get_post_by_id(db, post_id)
    if not post or post.category != "일반":
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")

    if not crud_post.can_delete_post(
        post=post,
        user_id=current_user.id,
        role_id=getattr(current_user, "role_id", None),
    ):
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    crud_post.delete_free_post(db=db, post_id=post_id)
    return {"message": "삭제되었습니다."}


#=============================
# Post_L_003 질문게시판 목록 조회 API
@router.get("/question", response_model=QuestionPostListResponse, summary="질문게시판 목록 조회")
def get_question_post_list(page: int = 1, db: Session = Depends(get_db)):
    """
    [Post_L_003] 질문게시판 게시글 목록 조회 API
    - 최신순 정렬, 페이지당 10개 출력.
    - 게시글이 없을 경우 안내 문구 반환.
    - 좋아요 수와 댓글 수를 함께 응답합니다.
    """
    posts_data = crud_post.get_question_posts(db=db, page=page, limit=10)

    if not posts_data:
        return {"message": "등록된 게시글이 없습니다.", "posts": []}

    # 제목 말줄임표 처리 (백엔드 처리 요청 시 적용)
    for post in posts_data:
        if len(post["title"]) > 20:
            post["title"] = post["title"][:20] + "..."

    return {"posts": posts_data}

# 질문게시판 작성, 수정, 삭제는 자유게시판 로직과 동일하게 진행 가능
# 필요 시 위와 같이 /question 경로로 CRUD API를 추가하여 사용


#=============================
# Post_003 질문게시판 작성/수정/삭제 API 추가
@router.get("/activity", response_model=ActivityPostListResponse, summary="동아리활동 목록 조회")
def get_activity_post_list(
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    posts_data = crud_post.get_activity_posts(
        db=db,
        page=page,
        limit=10,
        current_user_id=current_user.id,
        current_user_role_id=getattr(current_user, "role_id", None),
    )

    if not posts_data:
        return {"message": "등록된 게시글이 없습니다.", "posts": []}

    return {"posts": posts_data}


@router.post("/activity", summary="동아리활동 게시글 작성")
def create_activity_post_api(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    post_in.post_type = PostCategory.ACTIVITY.value
    new_post = crud_post.create_post(db=db, post_data=post_in, user_id=current_user.id)
    return {"message": "동아리활동 게시글이 작성되었습니다.", "data": new_post}


@router.post("/question", summary="질문게시판 게시글 작성")
def create_question_post_api(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    [Post_003] 질문게시판 작성
    - 5개 작성 제한 확인
    - 이미지/파일 확장자 및 용량 검증은 파일 업로드 공통 API(서비스)에서 처리됨
    """
    # 1. 작성 제한 확인 (5개)
    if crud_post.get_user_post_count(db, current_user.id, "질문") >= 5:
        raise HTTPException(status_code=400, detail="질문게시판은 최대 5개까지만 작성 가능합니다.")

    # 2. 작성 로직 수행 (프론트에서 post_in.post_type을 "질문"으로 보내야 함)
    new_post = crud_post.create_post(db=db, post_data=post_in, user_id=current_user.id)
    return {"message": "질문 게시글이 성공적으로 작성되었습니다.", "data": new_post}


@router.delete("/question/{post_id}", summary="질문게시판 게시글 삭제")
def delete_question_post_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """[Post_003] 질문게시판 삭제 (본인 또는 관리자만 가능)"""
    post = crud_post.get_post_by_id(db, post_id)
    if not post or post.category != "질문":
        raise HTTPException(status_code=404, detail="해당 질문 게시글을 찾을 수 없습니다.")

    if not crud_post.can_delete_post(
        post=post,
        user_id=current_user.id,
        role_id=getattr(current_user, "role_id", None),
    ):
        raise HTTPException(status_code=403, detail="질문 게시글을 삭제할 권한이 없습니다.")

    crud_post.delete_question_post(db=db, post_id=post_id)
    return {"message": "질문 게시글이 성공적으로 삭제되었습니다."}


# =============================
# [새 기능] 전체 게시판 목록 통합 조회 API (N+1 최적화 적용)
# =============================
@router.get("/all", summary="전체 게시글 통합 조회")
def get_all_post_list(
    page: int = 1,
    db: Session = Depends(get_db)
):
    """
    공지, 자유, 질문 등 모든 카테고리의 게시글을 한 번에 최신순으로 반환합니다.
    - 좋아요 수 및 댓글 수를 단일 쿼리로 집계합니다.
    - is_liked(좋아요 여부)는 게시글 상세 조회 API에서 확인하세요.
    """
    posts_data = crud_post.get_all_posts_optimized(
        db=db,
        page=page,
        limit=10
    )

    if not posts_data:
        return {"total_count": 0, "posts": []}

    return {"total_count": len(posts_data), "posts": posts_data}

# =============================
# [새 기능] 게시글 상세 조회 API (Join 포함)
# =============================
@router.get("/{post_id}/detail", response_model=PostDetailResponse, summary="게시글 상세 조회 (좋아요/댓글/파일 포함)")
def get_post_detail_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    게시글 본문, 좋아요 개수/여부, 작성자 여부, 첨부파일, 댓글 목록을 한 번의 통신으로 응답합니다.
    - is_liked: 현재 로그인 사용자가 좋아요를 눌렀는지 여부
    - is_author: 현재 로그인 사용자가 작성자인지 여부 (Frontend 편집 버튼 노출 판단용)
    - images: 이미지 첨부파일 목록 (image/* MIME 타입)
    - attachments: 일반 첨부파일 목록 (PDF, DOCX 등 이미지 외)
    - 댓글 작성자명이 함께 반환됩니다.
    """
    result = crud_post.get_post_detail_with_relations(
        db=db, post_id=post_id, current_user_id=current_user.id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글을 찾을 수 없습니다."
        )

    post = result["post"]
    return {
        "data": {
            "post_info": {
                "id": post.id,
                "user_id": post.user_id,
                "author_name": result["author_name"],
                "category": post.category,
                "title": post.title,
                "content": post.content,
                "thumbnail_file_id": post.thumbnail_file_id,
                "activity_date": post.activity_date,
                "start_date": post.start_date,
                "end_date": post.end_date,
                "created_at": post.created_at,
            },
            "total_likes": result["like_count"],
            "is_liked": result["is_liked"],
            "is_author": result["is_author"],
            "images": result["images"],
            "attachments": result["attachments"],
            "comments": result["comments"]
        }
    }
