"""通用媒体类消息段"""

from __future__ import annotations

from typing import ClassVar, Optional

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


class Record(DownloadableSegment):
    _type: ClassVar[str] = "record"


class Video(DownloadableSegment):
    _type: ClassVar[str] = "video"


class File(DownloadableSegment):
    _type: ClassVar[str] = "file"
