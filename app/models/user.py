# Users, Role 등
# 작성자 : 엄인섭
# app/models/user.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, SmallInteger, CHAR, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Role(Base):
    """
    [역할 테이블]
    RBAC 구조의 핵심. 유저의 등급(예: 회장, 부회장, 총무, 일반회원)을 정의합니다.
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    role_name: Mapped[str] = mapped_column(String(10), unique=True)

    # 1:N 양방향 관계 (하나의 역할은 여러 유저를 가질 수 있음)
    users: Mapped[List["User"]] = relationship(back_populates="role")
    permissions: Mapped[List["RolePermission"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class Permission(Base):
    """
    [권한 테이블]
    시스템 내의 세부적인 액션 권한을 정의합니다.
    """
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    action_name: Mapped[str] = mapped_column(String(20))

    roles: Mapped[List["RolePermission"]] = relationship(back_populates="permission", cascade="all, delete-orphan")


class RolePermission(Base):
    """
    [역할-권한 매핑 테이블 (N:M 해소)]
    Role과 Permission의 다대다 관계를 매핑하는 중간 테이블입니다.
    """
    __tablename__ = "role_permissions"

    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)

    role: Mapped["Role"] = relationship(back_populates="permissions")
    permission: Mapped["Permission"] = relationship(back_populates="roles")


class User(Base):
    """
    [유저 테이블]
    사용자의 핵심 정보를 저장합니다.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(String(15), unique=True, index=True) # 학번
    password_hash: Mapped[str] = mapped_column(String(255)) # 해싱된 비밀번호
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True) # 이메일
    name: Mapped[str] = mapped_column(String(10)) # 이름
    status: Mapped[str] = mapped_column(CHAR(2), default='재학') # 학적 상태
    phone: Mapped[str] = mapped_column(String(13)) # 휴대폰 번호
    admission_year: Mapped[int] = mapped_column(SmallInteger) # 입학 연도
    
    # 외래키 설정
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    # Null이 허용되는 필드는 Optional[]을 사용하여 타입 힌트를 명확히 줍니다.
    file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id", ondelete="SET NULL"), nullable=True) 

    # 양방향 관계 설정
    role: Mapped["Role"] = relationship(back_populates="users")
    email_verifications: Mapped[List["EmailVerification"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class EmailVerification(Base):
    """
    [이메일 인증 테이블]
    비밀번호 찾기 등 이미 가입된 유저의 이메일 소유를 검증하기 위한 난수 저장 테이블입니다.
    """
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    verification_code: Mapped[str] = mapped_column(CHAR(6))
    is_verified: Mapped[bool] = mapped_column(default=False)
    
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="email_verifications")