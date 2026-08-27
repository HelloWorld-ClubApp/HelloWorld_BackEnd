from enum import Enum


class RoleName(str, Enum):
    MEMBER = "일반회원"
    PRESIDENT = "회장"
    VICE_PRESIDENT = "부회장"
    TREASURER = "총무"


class JoinStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


JOIN_APPROVER_ROLE_NAMES = {
    RoleName.PRESIDENT.value,
    RoleName.VICE_PRESIDENT.value,
    RoleName.TREASURER.value,
}
