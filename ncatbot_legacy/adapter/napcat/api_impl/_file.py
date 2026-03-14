"""
文件操作 Mixin

包含群文件、私聊文件的上传/下载/删除/移动/重命名/文件夹管理等。
"""

from __future__ import annotations

from typing import Optional, Union

from ._base import NapCatBotAPIBase


class FileMixin(NapCatBotAPIBase):
    """文件操作相关 API"""

    # ------ 群文件 ------

    async def upload_group_file(
        self,
        group_id: Union[str, int],
        file: str,
        name: str,
        folder: Optional[str] = None,
    ) -> None:
        file = await self._preupload_file(file, "file")
        await self._call(
            "upload_group_file",
            {
                "group_id": int(group_id),
                "file": file,
                "name": name,
                "folder": folder,
            },
        )

    async def get_group_root_files(
        self, group_id: Union[str, int], file_count: int = 50
    ) -> dict:
        return (
            await self._call_data(
                "get_group_root_files",
                {"group_id": int(group_id), "file_count": file_count},
            )
            or {}
        )

    async def get_group_file_url(self, group_id: Union[str, int], file_id: str) -> str:
        data = await self._call_data(
            "get_group_file_url",
            {"group_id": int(group_id), "file_id": file_id},
        )
        return (data or {}).get("url", "")

    async def delete_group_file(self, group_id: Union[str, int], file_id: str) -> None:
        await self._call(
            "delete_group_file",
            {"group_id": int(group_id), "file_id": file_id},
        )

    async def move_group_file(
        self,
        group_id: Union[str, int],
        file_id: str,
        current_parent_directory: str,
        target_parent_directory: str,
    ) -> None:
        await self._call(
            "move_group_file",
            {
                "group_id": int(group_id),
                "file_id": file_id,
                "current_parent_directory": current_parent_directory,
                "target_parent_directory": target_parent_directory,
            },
        )

    async def trans_group_file(
        self, group_id: Union[str, int], file_id: str
    ) -> None:
        await self._call(
            "trans_group_file",
            {"group_id": int(group_id), "file_id": file_id},
        )

    async def rename_group_file(
        self, group_id: Union[str, int], file_id: str, new_name: str
    ) -> None:
        await self._call(
            "rename_group_file",
            {"group_id": int(group_id), "file_id": file_id, "new_name": new_name},
        )

    async def create_group_file_folder(
        self, group_id: Union[str, int], folder_name: str
    ) -> None:
        await self._call(
            "create_group_file_folder",
            {"group_id": int(group_id), "folder_name": folder_name},
        )

    async def delete_group_folder(
        self, group_id: Union[str, int], folder_id: str
    ) -> None:
        await self._call(
            "delete_group_folder",
            {"group_id": int(group_id), "folder_id": folder_id},
        )

    async def get_group_files_by_folder(
        self, group_id: Union[str, int], folder_id: str, file_count: int = 50
    ) -> dict:
        return (
            await self._call_data(
                "get_group_files_by_folder",
                {"group_id": int(group_id), "folder_id": folder_id, "file_count": file_count},
            )
            or {}
        )

    # ------ 私聊文件 ------

    async def upload_private_file(
        self, user_id: Union[str, int], file: str, name: str
    ) -> None:
        file = await self._preupload_file(file, "file")
        await self._call(
            "upload_private_file",
            {"user_id": int(user_id), "file": file, "name": name},
        )

    async def get_private_file_url(self, file_id: str) -> str:
        data = await self._call_data("get_private_file_url", {"file_id": file_id})
        return (data or {}).get("url", "")

    # ------ 通用文件 ------

    async def get_file(self, file_id: str, file: str) -> dict:
        return (
            await self._call_data("get_file", {"file_id": file_id, "file": file})
            or {}
        )
