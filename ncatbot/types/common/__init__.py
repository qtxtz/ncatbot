"""跨平台通用类型"""

from .base import BaseEventData
from .sender import BaseSender
from .segment import (
    SEGMENT_MAP,
    At,
    DownloadableSegment,
    File,
    Image,
    MessageArray,
    MessageSegment,
    PlainText,
    Record,
    Reply,
    Video,
    parse_segment,
)

__all__ = [
    "BaseEventData",
    "BaseSender",
    # segments
    "SEGMENT_MAP",
    "MessageSegment",
    "parse_segment",
    "PlainText",
    "At",
    "Reply",
    "DownloadableSegment",
    "Image",
    "Record",
    "Video",
    "File",
    "MessageArray",
]
