from enum import Enum


class PostCategory(str, Enum):
    NOTICE = "공지"
    FREE = "일반"
    QNA = "질문"
    ACTIVITY = "동아리활동"
