"""
信息查询 Mixin

包含用户信息、群信息、好友列表、群成员、消息获取等查询操作。
"""

from __future__ import annotations

from typing import List, Union

from ._base import NapCatBotAPIBase


class QueryMixin(NapCatBotAPIBase):
    """信息查询相关 API"""

    async def get_login_info(self) -> dict:
        return await self._call_data("get_login_info") or {}

    async def get_stranger_info(self, user_id: Union[str, int]) -> dict:
        return (
            await self._call_data("get_stranger_info", {"user_id": int(user_id)}) or {}
        )

    async def get_friend_list(self) -> List[dict]:
        return await self._call_data("get_friend_list") or []

    async def get_group_info(self, group_id: Union[str, int]) -> dict:
        return (
            await self._call_data("get_group_info", {"group_id": int(group_id)}) or {}
        )

    async def get_group_list(self, info: bool = False) -> list:
        data = await self._call_data("get_group_list") or []
        if info:
            return data
        return [str(g.get("group_id")) for g in data] if data else []

    async def get_group_member_info(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
    ) -> dict:
        return (
            await self._call_data(
                "get_group_member_info",
                {"group_id": int(group_id), "user_id": int(user_id)},
            )
            or {}
        )

    async def get_group_member_list(self, group_id: Union[str, int]) -> list:
        return (
            await self._call_data("get_group_member_list", {"group_id": int(group_id)})
            or []
        )

    async def get_msg(self, message_id: Union[str, int]) -> dict:
        return await self._call_data("get_msg", {"message_id": int(message_id)}) or {}

    async def get_forward_msg(self, message_id: Union[str, int]) -> dict:
        return (
            await self._call_data("get_forward_msg", {"message_id": int(message_id)})
            or {}
        )
