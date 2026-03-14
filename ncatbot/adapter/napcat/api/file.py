"""文件操作 API Mixin"""

from typing import Union


class FileAPIMixin:

    async def upload_group_file(
        self, group_id: Union[str, int], file: str, name: str, folder_id: str = "",
    ) -> None:
        await self._call("upload_group_file", {
            "group_id": int(group_id),
            "file": file,
            "name": name,
            "folder_id": folder_id,
        })

    async def get_group_root_files(self, group_id: Union[str, int]) -> dict:
        return await self._call_data("get_group_root_files", {"group_id": int(group_id)}) or {}

    async def get_group_file_url(self, group_id: Union[str, int], file_id: str) -> str:
        data = await self._call_data("get_group_file_url", {
            "group_id": int(group_id), "file_id": file_id,
        })
        return (data or {}).get("url", "")

    async def delete_group_file(self, group_id: Union[str, int], file_id: str) -> None:
        await self._call("delete_group_file", {
            "group_id": int(group_id), "file_id": file_id,
        })
