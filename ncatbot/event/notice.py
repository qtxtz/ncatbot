from __future__ import annotations

from typing import Any, Optional

from ncatbot.types import (
    GroupIncreaseNoticeEventData,
    NoticeEventData,
    NoticeType,
)

from .base import BaseEvent

__all__ = [
    "NoticeEvent",
    "GroupIncreaseEvent",
]


class NoticeEvent(BaseEvent):
    """通知事件实体"""

    _data: NoticeEventData

    # ---- NoticeEventData 字段 ----

    @property
    def notice_type(self) -> NoticeType:
        return self._data.notice_type

    @property
    def group_id(self) -> Optional[str]:
        return self._data.group_id

    @property
    def user_id(self) -> Optional[str]:
        return self._data.user_id


class GroupIncreaseEvent(NoticeEvent):
    """群成员增加事件"""

    _data: GroupIncreaseNoticeEventData

    # ---- GroupIncreaseNoticeEventData 字段 ----

    @property
    def sub_type(self) -> str:
        return self._data.sub_type

    @property
    def operator_id(self) -> str:
        return self._data.operator_id

    # ---- 行为方法 ----

    async def kick(self, reject_add_request: bool = False) -> Any:
        return await self._api.set_group_kick(
            self._data.group_id, self._data.user_id, reject_add_request
        )
