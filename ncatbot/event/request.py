from __future__ import annotations

from typing import Any

from ncatbot.types import (
    FriendRequestEventData,
    GroupRequestEventData,
    RequestEventData,
    RequestType,
)

from .base import BaseEvent

__all__ = [
    "RequestEvent",
    "FriendRequestEvent",
    "GroupRequestEvent",
]


class RequestEvent(BaseEvent):
    """请求事件实体"""

    _data: RequestEventData

    async def approve(self, remark: str = "", reason: str = "") -> Any:
        if self._data.request_type is RequestType.FRIEND:
            return await self._api.set_friend_add_request(
                flag=self._data.flag, approve=True, remark=remark
            )
        elif self._data.request_type is RequestType.GROUP:
            return await self._api.set_group_add_request(
                flag=self._data.flag,
                sub_type=self._data.sub_type,  # type: ignore[attr-defined]
                approve=True,
                reason="",
            )

    async def reject(self, reason: str = "") -> Any:
        if self._data.request_type is RequestType.FRIEND:
            return await self._api.set_friend_add_request(
                flag=self._data.flag, approve=False
            )
        elif self._data.request_type is RequestType.GROUP:
            return await self._api.set_group_add_request(
                flag=self._data.flag,
                sub_type=self._data.sub_type,  # type: ignore[attr-defined]
                approve=False,
                reason=reason,
            )


class FriendRequestEvent(RequestEvent):
    """好友请求事件"""

    _data: FriendRequestEventData


class GroupRequestEvent(RequestEvent):
    """群请求事件"""

    _data: GroupRequestEventData
