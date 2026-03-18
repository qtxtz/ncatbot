"""跨平台通用类型

仅导出 common/ 中的平台无关类型。
QQ 平台类型请从 ncatbot.types.qq 导入。
NapCat 响应类型请从 ncatbot.types.napcat 导入。
"""

from .common import (
    SEGMENT_MAP,
    At,
    BaseEventData,
    BaseSender,
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
