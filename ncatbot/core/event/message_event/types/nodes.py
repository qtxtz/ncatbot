from typing import List, Union, Literal, Optional
from pydantic import field_validator
from .base import MessageArrayDTO, MessageSegment


class Node(MessageSegment):
    type: Literal["node"] = "node"
    user_id: str
    nickname: str
    content: Union[
        str, List[MessageArrayDTO]
    ]  # Any 指代其他 MessageSegment 序列化后的 dict

    @field_validator("user_id", mode="before")
    def ensure_str(cls, v):
        return str(v) if v is not None else v


class Forward(MessageSegment):
    type: Literal["forward"] = "forward"
    id: Optional[str] = None
    content: Optional[List[Node]] = None
