"""信息查询命名空间 — 所有 get_* 查询操作"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI


class InfoExtension:
    """低频查询操作（读操作）"""

    __slots__ = ("_api",)

    def __init__(self, api: IBotAPI) -> None:
        self._api = api

    async def get_login_info(self) -> dict:
        return await self._api.get_login_info()

    async def get_stranger_info(self, user_id: Union[str, int]) -> dict:
        return await self._api.get_stranger_info(user_id)

    async def get_friend_list(self) -> List[dict]:
        return await self._api.get_friend_list()

    async def get_group_info(self, group_id: Union[str, int]) -> dict:
        return await self._api.get_group_info(group_id)

    async def get_group_list(self) -> list:
        return await self._api.get_group_list()

    async def get_group_member_info(
        self, group_id: Union[str, int], user_id: Union[str, int],
    ) -> dict:
        return await self._api.get_group_member_info(group_id, user_id)

    async def get_group_member_list(self, group_id: Union[str, int]) -> list:
        return await self._api.get_group_member_list(group_id)

    async def get_msg(self, message_id: Union[str, int]) -> dict:
        return await self._api.get_msg(message_id)

    async def get_forward_msg(self, message_id: Union[str, int]) -> dict:
        return await self._api.get_forward_msg(message_id)

    async def get_group_root_files(self, group_id: Union[str, int]) -> dict:
        return await self._api.get_group_root_files(group_id)

    async def get_group_file_url(
        self, group_id: Union[str, int], file_id: str,
    ) -> str:
        return await self._api.get_group_file_url(group_id, file_id)
