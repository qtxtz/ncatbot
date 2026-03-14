"""管理操作命名空间 — 群管理 + 账号设置 + 组合 sugar"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI


class ManageExtension:
    """低频管理操作（写操作）"""

    __slots__ = ("_api",)

    def __init__(self, api: IBotAPI) -> None:
        self._api = api

    # ---- 群管理（原子透传） ----

    async def set_group_kick(
        self, group_id: Union[str, int], user_id: Union[str, int],
        reject_add_request: bool = False,
    ) -> None:
        await self._api.set_group_kick(group_id, user_id, reject_add_request)

    async def set_group_ban(
        self, group_id: Union[str, int], user_id: Union[str, int],
        duration: int = 1800,
    ) -> None:
        await self._api.set_group_ban(group_id, user_id, duration)

    async def set_group_whole_ban(
        self, group_id: Union[str, int], enable: bool = True,
    ) -> None:
        await self._api.set_group_whole_ban(group_id, enable)

    async def set_group_admin(
        self, group_id: Union[str, int], user_id: Union[str, int],
        enable: bool = True,
    ) -> None:
        await self._api.set_group_admin(group_id, user_id, enable)

    async def set_group_card(
        self, group_id: Union[str, int], user_id: Union[str, int],
        card: str = "",
    ) -> None:
        await self._api.set_group_card(group_id, user_id, card)

    async def set_group_name(
        self, group_id: Union[str, int], name: str,
    ) -> None:
        await self._api.set_group_name(group_id, name)

    async def set_group_leave(
        self, group_id: Union[str, int], is_dismiss: bool = False,
    ) -> None:
        await self._api.set_group_leave(group_id, is_dismiss)

    async def set_group_special_title(
        self, group_id: Union[str, int], user_id: Union[str, int],
        special_title: str = "",
    ) -> None:
        await self._api.set_group_special_title(group_id, user_id, special_title)

    # ---- 账号操作（原子透传） ----

    async def set_friend_add_request(
        self, flag: str, approve: bool = True, remark: str = "",
    ) -> None:
        await self._api.set_friend_add_request(flag, approve, remark)

    async def set_group_add_request(
        self, flag: str, sub_type: str, approve: bool = True, reason: str = "",
    ) -> None:
        await self._api.set_group_add_request(flag, sub_type, approve, reason)

    # ---- 组合 sugar ----

    async def kick_and_block(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        message_id: Optional[Union[str, int]] = None,
    ) -> None:
        """撤回 + 踢出 + 拒绝再加群"""
        if message_id is not None:
            await self._api.delete_msg(message_id)
        await self._api.set_group_kick(group_id, user_id, reject_add_request=True)
