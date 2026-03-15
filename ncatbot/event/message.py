from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ncatbot.types import (
    BaseSender,
    GroupMessageEventData,
    GroupSender,
    MessageArray,
    MessageEventData,
    MessageType,
    Anonymous,
    PrivateMessageEventData,
)

from .base import BaseEvent

if TYPE_CHECKING:
    pass

__all__ = [
    "MessageEvent",
    "PrivateMessageEvent",
    "GroupMessageEvent",
]


class MessageEvent(BaseEvent):
    """消息事件实体"""

    _data: MessageEventData

    # ---- MessageEventData 字段 ----

    @property
    def message_type(self) -> MessageType:
        return self._data.message_type

    @property
    def sub_type(self) -> str:
        return self._data.sub_type

    @property
    def message_id(self) -> str:
        return self._data.message_id

    @property
    def user_id(self) -> str:
        return self._data.user_id

    @property
    def message(self) -> MessageArray:
        return self._data.message

    @property
    def raw_message(self) -> str:
        return self._data.raw_message

    @property
    def sender(self) -> BaseSender:
        return self._data.sender

    @property
    def font(self) -> int:
        return self._data.font

    # ---- 便捷方法 ----

    def is_group_msg(self) -> bool:
        return self._data.message_type is MessageType.GROUP

    async def reply(self, text: Any, **kwargs: Any) -> Any:
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

    # ---- GroupMessageEventData 字段 ----

    @property
    def group_id(self) -> str:
        return self._data.group_id

    @property
    def anonymous(self) -> Optional[Anonymous]:
        return self._data.anonymous

    @property
    def sender(self) -> GroupSender:  # type: ignore[override]
        return self._data.sender

    # ---- 行为方法 ----

    async def kick(self, reject_add_request: bool = False) -> Any:
        return await self._api.set_group_kick(
            self._data.group_id, self._data.user_id, reject_add_request
        )

    async def ban(self, duration: int = 30 * 60) -> Any:
        return await self._api.set_group_ban(
            self._data.group_id, self._data.user_id, duration
        )
