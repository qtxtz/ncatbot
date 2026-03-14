"""辅助功能命名空间 — 文件管理 + 杂项"""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI


class SupportExtension:
    """低频辅助操作（文件管理 + 杂项）"""

    __slots__ = ("_api",)

    def __init__(self, api: IBotAPI) -> None:
        self._api = api

    # ---- 文件管理 ----

    async def upload_group_file(
        self, group_id: Union[str, int], file: str, name: str, folder_id: str = "",
    ) -> None:
        await self._api.upload_group_file(group_id, file, name, folder_id)

    async def delete_group_file(
        self, group_id: Union[str, int], file_id: str,
    ) -> None:
        await self._api.delete_group_file(group_id, file_id)

    # ---- 辅助 ----

    async def send_like(self, user_id: Union[str, int], times: int = 1) -> None:
        await self._api.send_like(user_id, times)
