"""群管理 API Mixin"""

from typing import Union


class GroupAPIMixin:

    async def set_group_kick(
        self, group_id: Union[str, int], user_id: Union[str, int],
        reject_add_request: bool = False,
    ) -> None:
        await self._call("set_group_kick", {
            "group_id": int(group_id),
            "user_id": int(user_id),
            "reject_add_request": reject_add_request,
        })

    async def set_group_ban(
        self, group_id: Union[str, int], user_id: Union[str, int],
        duration: int = 30 * 60,
    ) -> None:
        await self._call("set_group_ban", {
            "group_id": int(group_id),
            "user_id": int(user_id),
            "duration": duration,
        })

    async def set_group_whole_ban(
        self, group_id: Union[str, int], enable: bool = True,
    ) -> None:
        await self._call("set_group_whole_ban", {
            "group_id": int(group_id), "enable": enable,
        })

    async def set_group_admin(
        self, group_id: Union[str, int], user_id: Union[str, int],
        enable: bool = True,
    ) -> None:
        await self._call("set_group_admin", {
            "group_id": int(group_id),
            "user_id": int(user_id),
            "enable": enable,
        })

    async def set_group_card(
        self, group_id: Union[str, int], user_id: Union[str, int],
        card: str = "",
    ) -> None:
        await self._call("set_group_card", {
            "group_id": int(group_id),
            "user_id": int(user_id),
            "card": card,
        })

    async def set_group_name(
        self, group_id: Union[str, int], name: str,
    ) -> None:
        await self._call("set_group_name", {
            "group_id": int(group_id), "group_name": name,
        })

    async def set_group_leave(
        self, group_id: Union[str, int], is_dismiss: bool = False,
    ) -> None:
        await self._call("set_group_leave", {
            "group_id": int(group_id), "is_dismiss": is_dismiss,
        })

    async def set_group_special_title(
        self, group_id: Union[str, int], user_id: Union[str, int],
        special_title: str = "",
    ) -> None:
        await self._call("set_group_special_title", {
            "group_id": int(group_id),
            "user_id": int(user_id),
            "special_title": special_title,
        })
