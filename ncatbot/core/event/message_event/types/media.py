from typing import Literal, Optional
from .base import MessageSegment


class DownloadableMessageSegment(MessageSegment):
    file: Optional[str] = None
    url: Optional[str] = None
    file_id: Optional[str] = None
    file_size: Optional[int] = None
    file_name: Optional[str] = None
    base64: Optional[str] = None


class Image(DownloadableMessageSegment):
    type: Literal["image"] = "image"
    sub_type: int = 0
    type: Optional[Literal["flash"]] = None


class Record(DownloadableMessageSegment):
    type: Literal["record"] = "record"
    magic: Optional[int] = None


class Video(DownloadableMessageSegment):
    type: Literal["video"] = "video"


class File(DownloadableMessageSegment):
    type: Literal["file"] = "file"
