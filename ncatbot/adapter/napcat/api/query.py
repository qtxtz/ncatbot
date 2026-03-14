"""信息查询 API Mixin"""

from typing import List, Union


class QueryAPIMixin:

    async def get_login_info(self) -> dict:
        return await self._call_data("get_login_info") or {}

    async def get_stranger_info(self, user_id: Union[str, int]) -> dict:
        return await self._call_data("get_stranger_info", {"user_id": int(user_id)}) or {}

    async def get_friend_list(self) -> List[dict]:
        return await self._call_data("get_friend_list") or []

    async def get_group_info(self, group_id: Union[str, int]) -> dict:
        return await self._call_data("get_group_info", {"group_id": int(group_id)}) or {}

    async def get_group_list(self) -> list:
        return await self._call_data("get_group_list") or []

    async def get_group_member_info(
        self, group_id: Union[str, int], user_id: Union[str, int],
    ) -> dict:
        return await self._call_data("get_group_member_info", {
            "group_id": int(group_id), "user_id": int(user_id),
        }) or {}

    async def get_group_member_list(self, group_id: Union[str, int]) -> list:
        return await self._call_data("get_group_member_list", {"group_id": int(group_id)}) or []

    async def get_msg(self, message_id: Union[str, int]) -> dict:
        return await self._call_data("get_msg", {"message_id": int(message_id)}) or {}

    async def get_forward_msg(self, message_id: Union[str, int]) -> dict:
        return await self._call_data("get_forward_msg", {"message_id": int(message_id)}) or {}
