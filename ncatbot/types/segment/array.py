from __future__ import annotations

import re
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from .base import MessageSegment, parse_segment
from .forward import Forward
from .media import Image, Video
from .text import At, Face, PlainText, Reply

__all__ = [
    "MessageArray",
    "parse_cq_code_to_onebot11",
]

T = TypeVar("T", bound=MessageSegment)


def parse_cq_code_to_onebot11(
    cq_string: str,
) -> List[Dict[str, Union[str, Dict[str, str]]]]:
    """将 CQ 码字符串解析为 OB11 消息数组格式"""
    cq_pattern = re.compile(r"\[CQ:([^,\]]+)(?:,([^\]]+))?\]")
    segments: List[Dict[str, Union[str, Dict[str, str]]]] = []
    last_pos = 0
    html_unescape_map = {"&amp;": "&", "&#91;": "[", "&#93;": "]", "&#44;": ","}

    def unescape_cq(text: str) -> str:
        for escaped, unescaped in html_unescape_map.items():
            text = text.replace(escaped, unescaped)
        return text

    for match in cq_pattern.finditer(cq_string):
        text_before = cq_string[last_pos : match.start()]
        if text_before:
            segments.append({"type": "text", "data": {"text": unescape_cq(text_before)}})
        cq_type = match.group(1)
        cq_params_str = match.group(2) or ""
        params: Dict[str, str] = {}
        for param in cq_params_str.split(","):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = unescape_cq(value)
        segments.append({"type": cq_type, "data": params})
        last_pos = match.end()

    text_after = cq_string[last_pos:]
    if text_after:
        segments.append({"type": "text", "data": {"text": unescape_cq(text_after)}})
    return segments


def _parse_any(data: Any) -> List[MessageSegment]:
    """将各种输入格式统一解析为 MessageSegment 列表"""
    if isinstance(data, MessageSegment):
        return [data]
    if isinstance(data, dict):
        return [parse_segment(data)]
    if isinstance(data, str):
        return [parse_segment(seg) for seg in parse_cq_code_to_onebot11(data)]
    if isinstance(data, Iterable):
        result: List[MessageSegment] = []
        for item in data:
            result.extend(_parse_any(item))
        return result
    return []


class MessageArray:
    """消息段数组 — 容器 + 查询 + 链式构造"""

    __slots__ = ("_segments",)

    def __init__(self, segments: Optional[List[MessageSegment]] = None):
        self._segments: List[MessageSegment] = list(segments or [])

    # ---- Pydantic 自定义类型支持 ----

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._pydantic_validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._pydantic_serialize, info_arg=False
            ),
        )

    @classmethod
    def _pydantic_validate(cls, v: Any) -> MessageArray:
        if isinstance(v, MessageArray):
            return v
        if isinstance(v, list):
            return cls.from_list(v)
        if isinstance(v, str):
            return cls.from_any(v)
        raise ValueError(f"Cannot convert {type(v)} to MessageArray")

    def _pydantic_serialize(self) -> List[Dict[str, Any]]:
        return self.to_list()

    # ---- 反序列化 ----

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> MessageArray:
        return cls([parse_segment(seg) for seg in data])

    @classmethod
    def from_any(cls, data: Any) -> MessageArray:
        return cls(_parse_any(data))

    # ---- 序列化 ----

    def to_list(self) -> List[Dict[str, Any]]:
        return [seg.to_dict() for seg in self._segments]

    # ---- 查询 ----

    @overload
    def filter(self, cls: None = None) -> List[MessageSegment]: ...

    @overload
    def filter(self, cls: Type[T]) -> List[T]: ...

    def filter(
        self, cls: Union[Type[T], None] = None
    ) -> Union[List[MessageSegment], List[T]]:
        if cls is None:
            return list(self._segments)
        return [s for s in self._segments if isinstance(s, cls)]

    def filter_text(self) -> List[PlainText]:
        return self.filter(PlainText)

    def filter_at(self) -> List[At]:
        return self.filter(At)

    def filter_image(self) -> List[Image]:
        return self.filter(Image)

    def filter_video(self) -> List[Video]:
        return self.filter(Video)

    def filter_face(self) -> List[Face]:
        return self.filter(Face)

    @property
    def text(self) -> str:
        """拼接所有纯文本段"""
        return "".join(s.text for s in self.filter(PlainText))

    def is_at(self, user_id: Union[str, int], all_except: bool = False) -> bool:
        uid = str(user_id)
        all_at = False
        for at in self.filter(At):
            if at.qq == uid:
                return True
            if at.qq == "all":
                all_at = True
        return not all_except and all_at

    def is_forward_msg(self) -> bool:
        return len(self.filter(Forward)) > 0

    # ---- 链式构造 ----

    def add_text(self, text: str) -> MessageArray:
        self._segments.extend(_parse_any(text))
        return self

    def add_image(self, image: Union[str, Image]) -> MessageArray:
        if isinstance(image, Image):
            self._segments.append(image)
        elif isinstance(image, str):
            self._segments.append(Image(file=image))
        else:
            raise TypeError(f"image must be str or Image, got {type(image)}")
        return self

    def add_at(self, user_id: Union[str, int]) -> MessageArray:
        self._segments.append(At(qq=str(user_id)))
        return self

    def add_at_all(self) -> MessageArray:
        self._segments.append(At(qq="all"))
        return self

    def add_reply(self, message_id: Union[str, int]) -> MessageArray:
        self._segments.append(Reply(id=str(message_id)))
        return self

    def add_segment(self, segment: MessageSegment) -> MessageArray:
        self._segments.append(segment)
        return self

    def add_segments(self, data: Any) -> MessageArray:
        self._segments.extend(_parse_any(data))
        return self

    # ---- 容器协议 ----

    def __iter__(self):
        return iter(self._segments)

    def __len__(self):
        return len(self._segments)

    def __add__(self, other: Any) -> MessageArray:
        return MessageArray(self._segments + _parse_any(other))

    def __radd__(self, other: Any) -> MessageArray:
        return MessageArray(_parse_any(other) + self._segments)

    def __repr__(self) -> str:
        return f"MessageArray({self._segments!r})"
