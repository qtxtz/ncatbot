from __future__ import annotations

from typing import Any

from ncatbot.types import (
    GroupIncreaseNoticeEventData,
    NoticeEventData,
)

from .base import BaseEvent

__all__ = [
    "NoticeEvent",
    "GroupIncreaseEvent",
]


class NoticeEvent(BaseEvent):
    """通知事件实体"""

    _data: NoticeEventData


class GroupIncreaseEvent(NoticeEvent):
    """群成员增加事件"""

    _data: GroupIncreaseNoticeEventData

    async def kick(self, reject_add_request: bool = False) -> Any:
        return await self._api.set_group_kick(
            self._data.group_id, self._data.user_id, reject_add_request
        )
