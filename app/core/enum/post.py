from enum import Enum


class PostCategory(str, Enum):
    NOTICE = "공지"
    FREE = "일반"
    QUESTION = "질문"