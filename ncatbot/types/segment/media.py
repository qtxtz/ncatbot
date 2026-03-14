from __future__ import annotations

from typing import Any, ClassVar, Dict, Optional

from .base import MessageSegment

__all__ = [
    "DownloadableSegment",
    "Image",
    "Record",
    "Video",
    "File",
]


class DownloadableSegment(MessageSegment):
    """可下载资源的消息段基类"""

    file: str
    url: Optional[str] = None
    file_id: Optional[str] = None
    file_size: Optional[int] = None
    file_name: Optional[str] = None


class Image(DownloadableSegment):
    _type: ClassVar[str] = "image"
    sub_type: int = 0
    type: Optional[int] = None  # OB11 data.type: 0=normal, 1=flash

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Image:
        seg_data = dict(data.get("data", {}))
        # OB11: data.type 是 0/1，直接作为 type 字段
        return cls.model_validate(seg_data)

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        return result


class Record(DownloadableSegment):
    _type: ClassVar[str] = "record"
    magic: Optional[int] = None


class Video(DownloadableSegment):
    _type: ClassVar[str] = "video"


class File(DownloadableSegment):
    _type: ClassVar[str] = "file"
