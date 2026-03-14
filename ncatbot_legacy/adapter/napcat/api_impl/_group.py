"""
群管理操作 Mixin

包含群成员管理、群设置、群文件夹、群相册、精华消息等。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import NapCatBotAPIBase


class GroupMixin(NapCatBotAPIBase):
    """群管理相关 API"""

    # ------ 基础群管理 ------

    async def set_group_kick(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        reject_add_request: bool = False,
    ) -> None:
        await self._call(
            "set_group_kick",
            {
                "group_id": int(group_id),
                "user_id": int(user_id),
                "reject_add_request": reject_add_request,
            },
        )

    async def set_group_ban(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        duration: int = 30 * 60,
    ) -> None:
        await self._call(
            "set_group_ban",
            {
                "group_id": int(group_id),
                "user_id": int(user_id),
                "duration": duration,
            },
        )

    async def set_group_whole_ban(
        self, group_id: Union[str, int], enable: bool = True
    ) -> None:
        await self._call(
            "set_group_whole_ban",
            {"group_id": int(group_id), "enable": enable},
        )

    async def set_group_admin(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        enable: bool = True,
    ) -> None:
        await self._call(
            "set_group_admin",
            {
                "group_id": int(group_id),
                "user_id": int(user_id),
                "enable": enable,
            },
        )

    async def set_group_card(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        card: str = "",
    ) -> None:
        await self._call(
            "set_group_card",
            {
                "group_id": int(group_id),
                "user_id": int(user_id),
                "card": card,
            },
        )

    async def set_group_name(self, group_id: Union[str, int], name: str) -> None:
        await self._call(
            "set_group_name",
            {"group_id": int(group_id), "group_name": name},
        )

    async def set_group_leave(
        self, group_id: Union[str, int], is_dismiss: bool = False
    ) -> None:
        await self._call(
            "set_group_leave",
            {"group_id": int(group_id), "is_dismiss": is_dismiss},
        )

    async def set_group_special_title(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        special_title: str = "",
        duration: int = -1,
    ) -> None:
        await self._call(
            "set_group_special_title",
            {
                "group_id": int(group_id),
                "user_id": int(user_id),
                "special_title": special_title,
            },
        )

    # ------ 群管理扩展 ------

    async def set_group_remark(self, group_id: Union[str, int], remark: str) -> None:
        await self._call(
            "set_group_remark",
            {"group_id": int(group_id), "remark": remark},
        )

    async def set_group_sign(self, group_id: Union[str, int]) -> None:
        await self._call("set_group_sign", {"group_id": int(group_id)})

    async def send_group_sign(self, group_id: Union[str, int]) -> None:
        await self._call("send_group_sign", {"group_id": int(group_id)})

    async def set_group_avatar(self, group_id: Union[str, int], file: str) -> None:
        file = await self._preupload_file(file, "image")
        await self._call(
            "set_group_avatar",
            {"group_id": int(group_id), "file": file},
        )

    async def get_group_album_list(self, group_id: Union[str, int]) -> List[dict]:
        return (
            await self._call_data("get_qun_album_list", {"group_id": int(group_id)})
            or []
        )

    async def upload_image_to_group_album(
        self,
        group_id: Union[str, int],
        file: str,
        album_id: str = "",
        album_name: str = "",
    ) -> None:
        file = await self._preupload_file(file, "image")
        await self._call(
            "upload_image_to_qun_album",
            {
                "group_id": int(group_id),
                "album_name": album_name,
                "album_id": album_id,
                "file": file,
            },
        )

    async def set_group_todo(
        self, group_id: Union[str, int], message_id: Union[str, int]
    ) -> dict:
        return (
            await self._call_data(
                "set_group_todo",
                {"group_id": int(group_id), "message_id": int(message_id)},
            )
            or {}
        )

    async def set_essence_msg(self, message_id: Union[str, int]) -> None:
        await self._call("set_essence_msg", {"message_id": int(message_id)})

    async def delete_essence_msg(self, message_id: Union[str, int]) -> None:
        await self._call("delete_essence_msg", {"message_id": int(message_id)})

    async def get_essence_msg_list(self, group_id: Union[str, int]) -> list:
        return (
            await self._call_data("get_essence_msg_list", {"group_id": int(group_id)})
            or []
        )

    async def get_group_honor_info(self, group_id: Union[str, int], type: str) -> dict:
        return (
            await self._call_data(
                "get_group_honor_info",
                {"group_id": int(group_id), "type": type},
            )
            or {}
        )

    async def get_group_info_ex(self, group_id: Union[str, int]) -> dict:
        return (
            await self._call_data("get_group_info_ex", {"group_id": int(group_id)})
            or {}
        )

    async def get_group_shut_list(self, group_id: Union[str, int]) -> list:
        return (
            await self._call_data("get_group_shut_list", {"group_id": int(group_id)})
            or []
        )
