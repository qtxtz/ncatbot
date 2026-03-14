from __future__ import annotations

from typing import Any, ClassVar, Dict, Type

from pydantic import BaseModel, ConfigDict

__all__ = [
    "MessageSegment",
    "parse_segment",
    "SEGMENT_MAP",
]

SEGMENT_MAP: Dict[str, Type[MessageSegment]] = {}


class MessageSegment(BaseModel):
    """消息段基类

    _type (ClassVar): 内部判别标识，对应 OB11 外层 type。
    子类的 type 实例字段（如 Music.type, Image.type）保留 OB11 data.type 原始语义。
    """

    model_config = ConfigDict(extra="allow")
    _type: ClassVar[str]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if isinstance(cls.__dict__.get("_type"), str):
            SEGMENT_MAP[cls._type] = cls

    def to_dict(self) -> Dict[str, Any]:
        """序列化为 OB11: {"type": "...", "data": {...}}"""
        return {"type": self._type, "data": self.model_dump(exclude_none=True)}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MessageSegment:
        """从 {"type": "...", "data": {...}} 解析为具体子类"""
        return parse_segment(data)


def parse_segment(raw: Dict[str, Any]) -> MessageSegment:
    """从 OB11 {"type": "...", "data": {...}} 解析为具体 MessageSegment"""
    seg_type = raw.get("type", "")
    target_cls = SEGMENT_MAP.get(seg_type)
    if not target_cls:
        raise ValueError(f"Unknown segment type: {seg_type}")
    return target_cls.model_validate(raw.get("data", {}))
