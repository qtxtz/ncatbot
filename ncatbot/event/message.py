from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ncatbot.types import (
    GroupMessageEventData,
    MessageEventData,
    MessageType,
    PrivateMessageEventData,
)

from .base import BaseEvent

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI

__all__ = [
    "MessageEvent",
    "PrivateMessageEvent",
    "GroupMessageEvent",
]


class MessageEvent(BaseEvent):
    """消息事件实体"""

    _data: MessageEventData

    async def reply(self, text: Any, **kwargs: Any) -> Any:
        # str(Enum) 使用 .value；MessageType 继承 str，is 比较安全
        if self._data.message_type is MessageType.GROUP:
            return await self._api.send_group_msg(
                group_id=self._data.group_id,  # type: ignore[attr-defined]
                message=text,
                **kwargs,
            )
        return await self._api.send_private_msg(
            user_id=self._data.user_id, message=text, **kwargs
        )

    async def delete(self) -> Any:
        return await self._api.delete_msg(message_id=self._data.message_id)


class PrivateMessageEvent(MessageEvent):
    """私聊消息事件"""

    _data: PrivateMessageEventData


class GroupMessageEvent(MessageEvent):
    """群消息事件"""

    _data: GroupMessageEventData

    async def kick(self, reject_add_request: bool = False) -> Any:
        return await self._api.set_group_kick(
            self._data.group_id, self._data.user_id, reject_add_request
        )

    async def ban(self, duration: int = 30 * 60) -> Any:
        return await self._api.set_group_ban(
            self._data.group_id, self._data.user_id, duration
        )
