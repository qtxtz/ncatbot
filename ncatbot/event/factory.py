from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Type

from ncatbot.types import (
    BaseEventData,
    FriendRequestEventData,
    GroupIncreaseNoticeEventData,
    GroupMessageEventData,
    GroupRequestEventData,
    PrivateMessageEventData,
    PostType,
)

from .base import BaseEvent
from .message import GroupMessageEvent, MessageEvent, PrivateMessageEvent
from .notice import GroupIncreaseEvent, NoticeEvent
from .request import FriendRequestEvent, GroupRequestEvent, RequestEvent
from .meta import MetaEvent

if TYPE_CHECKING:
    from ncatbot.api import IBotAPI

__all__ = [
    "create_entity",
]

# 精确映射：数据模型类 → 实体类
_ENTITY_MAP: Dict[Type[BaseEventData], Type[BaseEvent]] = {
    PrivateMessageEventData: PrivateMessageEvent,
    GroupMessageEventData: GroupMessageEvent,
    FriendRequestEventData: FriendRequestEvent,
    GroupRequestEventData: GroupRequestEvent,
    GroupIncreaseNoticeEventData: GroupIncreaseEvent,
}

# post_type → 降级实体基类
_FALLBACK_MAP: Dict[str, Type[BaseEvent]] = {
    PostType.MESSAGE: MessageEvent,
    PostType.MESSAGE_SENT: MessageEvent,
    PostType.NOTICE: NoticeEvent,
    PostType.REQUEST: RequestEvent,
    PostType.META_EVENT: MetaEvent,
}


def create_entity(data: BaseEventData, api: "IBotAPI") -> BaseEvent:
    """数据模型 → 实体（精确映射优先，降级至 post_type 基类）"""
    entity_cls = _ENTITY_MAP.get(type(data))
    if entity_cls is None:
        entity_cls = _FALLBACK_MAP.get(data.post_type, BaseEvent)
    return entity_cls(data, api)
