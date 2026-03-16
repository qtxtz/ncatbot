"""辅助功能命名空间 — 文件管理 + 杂项"""

from __future__ import annotations

from typing import TYPE_CHECKING, Union

from ncatbot.types.napcat import CreateFolderResult, DownloadResult

if TYPE_CHECKING:
    from ..interface import IBotAPI


class SupportExtension:
    """低频辅助操作（文件管理 + 杂项）"""

    __slots__ = ("_api",)

    def __init__(self, api: IBotAPI) -> None:
        self._api = api

    # ---- 文件管理 ----

    async def upload_group_file(
        self,
        group_id: Union[str, int],
        file: str,
        name: str,
        folder_id: str = "",
    ) -> None:
        await self._api.upload_group_file(group_id, file, name, folder_id)

    async def delete_group_file(
        self,
        group_id: Union[str, int],
        file_id: str,
    ) -> None:
        await self._api.delete_group_file(group_id, file_id)

    # ---- 辅助 ----

    async def send_like(self, user_id: Union[str, int], times: int = 1) -> None:
        await self._api.send_like(user_id, times)

    # ---- 文件系统扩展 ----

    async def create_group_file_folder(
        self,
        group_id: Union[str, int],
        name: str,
        parent_id: str = "",
    ) -> CreateFolderResult:
        return await self._api.create_group_file_folder(group_id, name, parent_id)

    async def delete_group_folder(
        self, group_id: Union[str, int], folder_id: str
    ) -> None:
        await self._api.delete_group_folder(group_id, folder_id)

    async def upload_private_file(
        self,
        user_id: Union[str, int],
        file: str,
        name: str,
    ) -> None:
        await self._api.upload_private_file(user_id, file, name)

    async def download_file(
        self, url: str = "", file: str = "", headers: str = ""
    ) -> DownloadResult:
        return await self._api.download_file(url, file, headers)
