from typing import Literal, Union
from pydantic import field_validator
from .base import MessageSegment


class PlainText(MessageSegment):
    type: Literal["text"] = "text"
    text: str


class Face(MessageSegment):
    type: Literal["face"] = "face"
    id: str


class At(MessageSegment):
    type: Literal["at"] = "at"
    qq: Union[str, int]

    @field_validator("qq", mode="before")
    @classmethod
    def validate_qq(cls, v) -> str:
        str_v = str(v).strip()
        if str_v == "all":
            return str_v
        if str_v.isdigit():
            return str_v
        raise ValueError(f"At 消息的 qq 字段必须为纯数字或字符串 'all', 但读取到 {v}")


class Reply(MessageSegment):
    type: Literal["reply"] = "reply"
    id: str
