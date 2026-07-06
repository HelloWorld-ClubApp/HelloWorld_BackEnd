# 작업자 : 엄인섭
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.post import Post, Like

# ---------------------------------------------------------
# 함수명: toggle_like
# 역할: 특정 게시글에 대한 사용자의 좋아요 상태를 전환(추가/삭제)합니다.
# 흐름: 게시글 검증 -> 카테고리 검증 -> 기존 좋아요 확인 -> 분기 처리(동시성 예외 처리 포함) -> 총 개수 반환
# ---------------------------------------------------------
def toggle_like(db: Session, post_id: int, user_id: int) -> dict:
    # 1. 대상 게시글 조회
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    # 2. 카테고리 제약 조건 검사
    if post.category == "공지":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="공지사항에는 좋아요를 누를 수 없습니다.")

    # 3. 사용자의 기존 좋아요 내역 조회
    existing_like = db.query(Like).filter(
        Like.post_id == post_id, 
        Like.user_id == user_id
    ).first()

    # 4. 토글 로직 분기 및 동시성 방어
    if existing_like:
        # 4-1. 이미 좋아요를 누른 상태라면 삭제
        db.delete(existing_like)
        db.commit()
        liked_status = False
    else:
        # 4-2. 좋아요 추가 시 동시성 충돌(Race Condition) 방어
        new_like = Like(post_id=post_id, user_id=user_id)
        db.add(new_like)
        try:
            db.commit()
            liked_status = True
        except IntegrityError:
            # 💡 동시성 문제 발생: 
            # 거의 같은 0.001초 사이에 동일한 유저의 좋아요 요청이 2번 들어와서 
            # DB의 UniqueConstraint(복합키 제약조건)에 걸려 에러가 발생한 상황입니다.
            db.rollback() # 트랜잭션을 롤백하여 DB 세션을 정상 상태로 복구
            liked_status = True # 이미 다른 요청에 의해 DB에 삽입되었으므로 결과는 True로 반환

    # 5. 실시간 총 좋아요 개수 산출
    total_likes = db.query(Like).filter(Like.post_id == post_id).count()

    # 6. 결과 반환
    return {
        "liked": liked_status,
        "total_likes": total_likes
    }