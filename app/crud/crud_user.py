# 작성자 : 엄인섭 (2026-06-12)
# 학번/이메일 중복 검사 쿼리
import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, Role
from app.schemas.user import UserCreate
from app.core.security import get_password_hash # 보안 모듈에서 해시 함수를 가져옴
from app.models.file import File
from sqlalchemy import case
from app.core.enum.user import JoinStatus, RoleName


def get_user_by_student_id(db: Session, student_id: str):
    """학번으로 유저 조회 (중복 검사용)"""
    return db.query(User).filter(User.student_id == student_id).first()

def get_user_by_email(db: Session, email: str):
    """이메일로 유저 조회 (중복 검사용)"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """유저 ID로 유저 조회"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserCreate, default_role_id: int = 1):
    """새로운 유저 DB에 생성"""
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        student_id=user_in.student_id,
        email=user_in.email,
        password_hash=hashed_password,
        name=user_in.name,
        admission_year=user_in.admission_year,
        role_id=default_role_id, # 기본 역할 부여 (1 = 일반 회원 가정)
        status="재학",
        phone="010-0000-0000", # UI에 없으므로 기본값 세팅 (나중에 마이페이지에서 수정)
        join_status=JoinStatus.PENDING.value,
        requested_at=datetime.datetime.now(datetime.timezone.utc)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def normalize_file_url(file_url: Optional[str]) -> Optional[str]:
    if not file_url:
        return None

    normalized_url = file_url.replace("\\", "/")
    if normalized_url.startswith("uploads/"):
        return f"/{normalized_url}"
    return normalized_url


def get_my_profile(db: Session, user_id: int):
    row = (
        db.query(User, Role.role_name, File.file_url)
        .join(Role, User.role_id == Role.id)
        .outerjoin(File, User.file_id == File.id)
        .filter(User.id == user_id)
        .first()
    )

    if not row:
        return None

    user, role_name, profile_image_url = row
    current_year = datetime.date.today().year
    grade = max(1, current_year - user.admission_year + 1)

    return {
        "id": user.id,
        "student_id": user.student_id,
        "email": user.email,
        "name": user.display_name,
        "admission_year": user.admission_year,
        "grade": grade,
        "status": user.status,
        "phone": user.phone,
        "role_id": user.role_id,
        "role_name": role_name,
        "profile_image_url": normalize_file_url(profile_image_url),
        "join_status": user.join_status,
    }




def get_club_members_grouped(db: Session, see_all: bool = False):
    current_year = datetime.date.today().year

    # 1. 조인 쿼리 준비
    query = (
        db.query(User.id, User.name, Role.role_name, User.admission_year, File.file_url)
        .join(Role, User.role_id == Role.id)
        .outerjoin(File, User.file_id == File.id)
        .filter(User.is_deleted == False, User.join_status == JoinStatus.APPROVED.value)
    )

    # 2. 메인 페이지(see_all=False)일 경우 올해(1학년), 작년(2학년) 입학생만 필터링
    if not see_all:
        query = query.filter(User.admission_year.in_([current_year, current_year - 1]))

    # 3. 그룹 내 정렬 조건: 임원진 우선 -> 이름 가나다순
    role_priority = case(
        (Role.role_name == '회장', 1),
        (Role.role_name == '부회장', 2),
        (Role.role_name == '총무', 3),
        else_=4
    )

    members_query = query.order_by(
        User.admission_year.asc(),  # 고학년(입학년도가 빠른 사람)부터
        role_priority.asc(),        # 임원진 우선
        User.name.asc()             # 이름 가나다순
    ).all()

    # 4. 프론트엔드를 위해 학년별로 데이터 그룹화 (Dict 활용)
    grouped_data = {}
    for row in members_query:
        year = row.admission_year
        grade = current_year - year + 1 # 학년 계산
        
        if year not in grouped_data:
            grouped_data[year] = {
                "grade": grade,
                "admission_year": year,
                "members": []
            }
            
        grouped_data[year]["members"].append({
            "id": row.id,
            "name": row.name,
            "role_name": row.role_name,
            "profile_image_url": row.file_url
        })

    # 5. UI 순서에 맞게 고학년(2학년)이 먼저 나오도록 리스트 정렬
    result = list(grouped_data.values())
    result.sort(key=lambda x: x["grade"], reverse=True)

    return result


def count_pending_join_requests(db: Session) -> int:
    return db.query(User).filter(
        User.is_deleted == False,
        User.join_status == JoinStatus.PENDING.value,
    ).count()


def count_approved_members(db: Session) -> int:
    return db.query(User).filter(
        User.is_deleted == False,
        User.join_status == JoinStatus.APPROVED.value,
    ).count()


def get_pending_join_requests(db: Session, skip: int = 0, limit: int = 50):
    return db.query(User).filter(
        User.is_deleted == False,
        User.join_status == JoinStatus.PENDING.value,
    ).order_by(User.requested_at.asc()).offset(skip).limit(limit).all()


def approve_join_request(db: Session, user: User):
    member_role = db.query(Role).filter(Role.role_name == RoleName.MEMBER.value).first()
    if member_role:
        user.role_id = member_role.id
    user.join_status = JoinStatus.APPROVED.value
    db.commit()
    db.refresh(user)
    return user


def reject_join_request(db: Session, user: User):
    user.join_status = JoinStatus.REJECTED.value
    db.commit()
    db.refresh(user)
    return user



# ==========================================
# [MY_007] 회원 탈퇴 (Soft Delete)
# 작성자 : 엄인섭
# ==========================================
def soft_delete_user(db: Session, user_id: int):
    """
    물리적 삭제(Delete) 대신 is_deleted 플래그를 True로 업데이트합니다.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_deleted = True
        # 민감 정보 마스킹이 필요하다면 여기서 추가 처리 가능
        db.commit()
    return user

# ==========================================
# [MY_001] 프로필 수정 (학적 상태 및 이미지 업데이트)
# 작성자 : 천석훈, 김세연, 문호성, 강기민
# ==========================================
def update_user_profile(db: Session, user_id: int, status_in: str, file_id: Optional[int] = None):
    """
    사용자의 학적 상태(status)와 프로필 이미지(file_id)를 업데이트합니다.
    새로운 이미지가 업로드되어 file_id가 전달된 경우에만 프로필 이미지를 갱신합니다.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.status = status_in
        
        # 파일이 새로 업로드된 경우에만 file_id 업데이트
        if file_id is not None:
            user.file_id = file_id
            
        db.commit()
        db.refresh(user)
    return user
