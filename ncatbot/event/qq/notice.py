"""QQ 通知事件实体"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from ncatbot.types.qq import (
    GroupIncreaseNoticeEventData,
    GroupMsgEmojiLikeNoticeEventData,
    NoticeEventData,
    NoticeType,
)
from ncatbot.types.qq.notice import EmojiLike

from ..common.base import BaseEvent
from ..common.mixins import GroupScoped, HasSender, Kickable

if TYPE_CHECKING:
    from ncatbot.api.qq import QQAPIClient

__all__ = [
    "NoticeEvent",
    "GroupIncreaseEvent",
    "GroupMsgEmojiLikeEvent",
]


class NoticeEvent(BaseEvent, HasSender, GroupScoped):
    """QQ 通知事件实体"""

    _data: NoticeEventData
    _api: QQAPIClient

    @property
    def api(self) -> QQAPIClient:
        return self._api

    @property
    def notice_type(self) -> NoticeType:
        return self._data.notice_type

    @property
    def group_id(self) -> Optional[str]:
        return self._data.group_id

    @property
    def user_id(self) -> Optional[str]:
        return self._data.user_id


class GroupIncreaseEvent(NoticeEvent, Kickable):
    """QQ 群成员增加事件"""

    _data: GroupIncreaseNoticeEventData

    @property
    def sub_type(self) -> str:
        return self._data.sub_type

    @property
    def operator_id(self) -> str:
        return self._data.operator_id

    async def kick(self, reject_add_request: bool = False) -> Any:
        return await self._api.set_group_kick(
            self._data.group_id, self._data.user_id, reject_add_request
        )


class GroupMsgEmojiLikeEvent(NoticeEvent):
    """QQ 群消息表情回应事件"""

    _data: GroupMsgEmojiLikeNoticeEventData

    @property
    def message_id(self) -> str:
        return self._data.message_id

    @property
    def likes(self) -> list[EmojiLike]:
        return self._data.likes

    @property
    def message_seq(self) -> int | None:
        return self._data.message_seq

    @property
    def is_add(self) -> bool | None:
        return self._data.is_add
